// Numeric validation only. Apple is the producer of the output buffer.
use std::{env, fs};
fn main() {
    let args: Vec<_> = env::args().collect();
    assert_eq!(args.len(), 4);
    let a = fs::read(&args[1]).unwrap();
    let b = fs::read(&args[2]).unwrap();
    assert_eq!(a.len(), b.len());
    assert_eq!(a.len() % 16, 0);
    let mut finite = 0_u64;
    let mut nonfinite = 0_u64;
    let mut changed = 0_u64;
    let mut maximum = 0_f64;
    let mut total = 0_f64;
    for (i, (x, y)) in a.chunks_exact(4).zip(b.chunks_exact(4)).enumerate() {
        if i % 4 == 3 { continue; }
        let x = f32::from_le_bytes(x.try_into().unwrap());
        let y = f32::from_le_bytes(y.try_into().unwrap());
        if !x.is_finite() || !y.is_finite() { nonfinite += 1; continue; }
        finite += 1;
        let d = (f64::from(x) - f64::from(y)).abs();
        changed += u64::from(d > 0.0);
        total += d;
        maximum = maximum.max(d);
    }
    let mean = total / finite.max(1) as f64;
    let json = format!("{{\"finite_rgb_pairs\":{finite},\"nonfinite_rgb_pairs\":{nonfinite},\"changed_rgb_components\":{changed},\"max_abs\":{maximum},\"mean_abs\":{mean}}}\n");
    fs::write(&args[3], json).unwrap();
}
