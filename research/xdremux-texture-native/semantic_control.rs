//! New diagnostic 2023 Styles context from CC0 analytical pixels only.
//! Not a 2026 Texture producer or original camera/RAW information.
use std::{env, fs, io::Write, path::Path};
use xdremux_engine::{
    apple_style_apply_global_tone_curve, apple_style_data_sha256, apple_style_distribution,
    apple_style_identity_data, apple_style_light_map, apple_style_monotonic_global_tone_curve,
    apple_style_property_list, AppleStyleLightMapRequest, AppleStylePropertyListRequest,
    AppleStyleStatistics,
};

fn luma(bytes: &[u8], count: usize) -> Result<Vec<f32>, Box<dyn std::error::Error>> {
    if bytes.len() != count.checked_mul(16).ok_or("dimensions overflow")? {
        return Err("analytical RGBA32f length mismatch".into());
    }
    bytes.chunks_exact(16).map(|p| {
        let r=f32::from_le_bytes(p[0..4].try_into()?);
        let g=f32::from_le_bytes(p[4..8].try_into()?);
        let b=f32::from_le_bytes(p[8..12].try_into()?);
        if ![r,g,b].iter().all(|v| v.is_finite() && *v>=0.0) { return Err("invalid analytical pixel".into()); }
        // Same linear Display P3 coefficients as the existing XDRemux runtime.
        Ok(0.228_974_56*r + 0.691_738_52*g + 0.079_286_91*b)
    }).collect()
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args=env::args().skip(1).collect::<Vec<_>>();
    if args.len()!=5 { return Err("HDR_RAW SDR_RAW WIDTH HEIGHT NEW_PLIST".into()); }
    let width:usize=args[2].parse()?;let height:usize=args[3].parse()?;
    let count=width.checked_mul(height).filter(|n| *n>0).ok_or("invalid dimensions")?;
    let hdr=fs::read(&args[0])?;let sdr=fs::read(&args[1])?;
    let linear=luma(&hdr,count)?;let tone=luma(&sdr,count)?;
    let curve=apple_style_monotonic_global_tone_curve(&linear,&tone)?;
    let mapped=apple_style_apply_global_tone_curve(&linear,&curve.linear_samples)?;
    let absent=apple_style_distribution(&[]);
    // No people exist in these analytical charts by construction. Empty
    // person/skin distributions are explicit diagnostic controls, not masks.
    let stats=AppleStyleStatistics {
        linear_gtc_image:apple_style_distribution(&mapped),linear_image:apple_style_distribution(&linear),
        linear_image_person_segment_based:absent,linear_image_skin_based:absent,
        tone_mapped_image:apple_style_distribution(&tone),tone_mapped_image_blue_channel_skin_based:absent,
        tone_mapped_image_green_channel_skin_based:absent,tone_mapped_image_person_segment_based:absent,
        tone_mapped_image_red_channel_skin_based:absent,tone_mapped_image_skin_based:absent,
    };
    // Explicit normalized diagnostic maps. This tests the missing semantic
    // argument contract; it is not a claim of camera LTM/Texture equivalence.
    let map=|luma:&[f32]| apple_style_light_map(&AppleStyleLightMapRequest {
        luma,width,height,value_scale:1.0,value_offset:0.0,output_minimum:0.0,output_maximum:1.0,storage_orientation:1,
    });
    let tone_map=map(&tone)?;let linear_map=map(&mapped)?;let identity=apple_style_identity_data();
    let lo=linear.iter().copied().fold(f32::INFINITY,f32::min);
    let hi=linear.iter().copied().fold(f32::NEG_INFINITY,f32::max);
    let plist=apple_style_property_list(&AppleStylePropertyListRequest {
        style_data:&identity,global_tone_curve:&curve.data,baseline_exposure:0.0,scene_type:0,statistics:&stats,
        people_ratio:0.0,person_masks_valid_hint:-1.0,skin_ratio:0.0,tone_light_map:&tone_map,linear_light_map:&linear_map,
        base_gain:1.0,linear_gain:1.0,original_range_min:f64::from(lo),original_range_max:f64::from(hi),face_exposure_boost:0.0,
    })?;
    fs::OpenOptions::new().write(true).create_new(true).open(Path::new(&args[4]))?.write_all(&plist)?;
    println!("diagnostic_semantic_plist_sha256={} input_hdr_sha256={} input_sdr_sha256={} original_camera_information=false texture_producer=false",
        apple_style_data_sha256(&plist),apple_style_data_sha256(&hdr),apple_style_data_sha256(&sdr));
    Ok(())
}
