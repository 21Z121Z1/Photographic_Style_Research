source_filename = "updateBaseGainWithStats"
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v24:32:32-v32:32:32-v48:64:64-v64:64:64-v96:128:128-v128:128:128-v192:256:256-v256:256:256-v512:512:512-v1024:1024:1024-n8:16:32"
target triple = "air64_v29-apple-macosx27.0.0"

%struct.SSRStats = type { [10 x [256 x i32]], [10 x %struct.SSRGlobalStats], i32, i32, float, float, %struct.SSRBasicStats.0, %struct.SSRBasicStats.0 }
%struct.SSRGlobalStats = type { float, float, float, float, float, float, float, float, float }
%struct.SSRBasicStats.0 = type { float, float, float }
%struct.SSRParams = type { i32, float, float, float, float, float, float, float, i32, %struct.SSRCastAdjustments, %struct.SSRToneAdjustments, %struct.SSRColorAdjustments, %struct.SSRHazeAdjustments, %struct.SSRBGAdjustment, %struct.SSRFGAdjustment, %struct.SSRSemanticToneAdjustment, float, i32, float, float, float, float }
%struct.SSRCastAdjustments = type { float, float, float, float, float, float, [3 x float], [3 x float], [3 x float], float, float, float, [3 x float], [3 x float], [3 x float], float, float, float, float, float, float, float }
%struct.SSRToneAdjustments = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRColorAdjustments = type { float, float, float, float }
%struct.SSRHazeAdjustments = type { i8, float, float, float, float, float, float, float, float }
%struct.SSRBGAdjustment = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRFGAdjustment = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRSemanticToneAdjustment = type { float, float, float, float, float, float, float }

@llvm.global_ctors = appending global [0 x { i32, ptr, ptr }] zeroinitializer

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite)
define void @updateBaseGainWithStats(ptr addrspace(1) noundef align 4 captures(none) dereferenceable(672) "air-buffer-no-alias" %0, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(10640) "air-buffer-no-alias" %1) local_unnamed_addr #0 {
  %3 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %1, i64 0, i32 7, i32 2
  %4 = load float, ptr addrspace(1) %3, align 4, !tbaa !31, !alias.scope !38, !noalias !41
  %5 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %1, i64 0, i32 6, i32 2
  %6 = load float, ptr addrspace(1) %5, align 4, !tbaa !43, !alias.scope !38, !noalias !41
  %7 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %0, i64 0, i32 7
  %8 = load float, ptr addrspace(1) %7, align 4, !tbaa !44, !alias.scope !41, !noalias !38
  %9 = fmul fast float %8, %6
  %10 = fdiv fast float %4, %9
  %11 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %0, i64 0, i32 6
  store float %10, ptr addrspace(1) %11, align 4, !tbaa !57, !alias.scope !41, !noalias !38
  ret void
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="0" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }

!llvm.module.flags = !{!0, !1, !2, !3, !4, !5, !6, !7, !8}
!llvm.ident = !{!9}
!air.version = !{!10}
!air.language_version = !{!11}
!air.compile_options = !{!12, !13, !14}
!air.kernel = !{!15}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 27, i32 0]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 7, !"frame-pointer", i32 2}
!3 = !{i32 7, !"air.max_device_buffers", i32 31}
!4 = !{i32 7, !"air.max_constant_buffers", i32 31}
!5 = !{i32 7, !"air.max_threadgroup_buffers", i32 31}
!6 = !{i32 7, !"air.max_textures", i32 128}
!7 = !{i32 7, !"air.max_read_write_textures", i32 8}
!8 = !{i32 7, !"air.max_samplers", i32 16}
!9 = !{!"Apple metal version 32023.921 (metalfe-32023.921.4)"}
!10 = !{i32 2, i32 9, i32 0}
!11 = !{!"Metal", i32 4, i32 1, i32 0}
!12 = !{!"air.compile.denorms_disable"}
!13 = !{!"air.compile.fast_math_enable"}
!14 = !{!"air.compile.framebuffer_fetch_enable"}
!15 = !{ptr @updateBaseGainWithStats, !16, !17}
!16 = !{}
!17 = !{!18, !27}
!18 = !{i32 0, !"air.buffer", !"air.buffer_size", i32 672, !"air.location_index", i32 1, i32 1, !"air.read_write", !"air.address_space", i32 1, !"air.struct_type_info", !19, !"air.arg_type_size", i32 672, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"SSRParams", !"air.arg_name", !"params"}
!19 = !{i32 0, i32 4, i32 0, !"uint", !"castType", i32 4, i32 4, i32 0, !"float", !"castIntensity", i32 8, i32 4, i32 0, !"float", !"toneBias", i32 12, i32 4, i32 0, !"float", !"colorBias", i32 16, i32 4, i32 0, !"float", !"fgCastIntensity", i32 20, i32 4, i32 0, !"float", !"bgCastIntensity", i32 24, i32 4, i32 0, !"float", !"linearBaseGain", i32 28, i32 4, i32 0, !"float", !"baselineExposure", i32 32, i32 4, i32 0, !"uint", !"sceneType", !"air.struct_type_info", !20, i32 36, i32 136, i32 0, !"SSRCastAdjustments", !"castAdj", !"air.struct_type_info", !21, i32 172, i32 264, i32 0, !"SSRToneAdjustments", !"toneAdj", !"air.struct_type_info", !22, i32 436, i32 16, i32 0, !"SSRColorAdjustments", !"colorAdj", !"air.struct_type_info", !23, i32 452, i32 36, i32 0, !"SSRHazeAdjustments", !"hazeAdj", !"air.struct_type_info", !24, i32 488, i32 68, i32 0, !"SSRBGAdjustment", !"bgAdj", !"air.struct_type_info", !25, i32 556, i32 64, i32 0, !"SSRFGAdjustment", !"fgAdj", !"air.struct_type_info", !26, i32 620, i32 28, i32 0, !"SSRSemanticToneAdjustment", !"semanticToneAdj", i32 648, i32 4, i32 0, !"float", !"brightnessValue", i32 652, i32 4, i32 0, !"uint", !"tuningType", i32 656, i32 4, i32 0, !"float", !"peopleThresholdLo", i32 660, i32 4, i32 0, !"float", !"peopleThresholdHi", i32 664, i32 4, i32 0, !"float", !"faceBasedGlobalExposureBoostRatio", i32 668, i32 4, i32 0, !"float", !"personMasksValidHint"}
!20 = !{i32 0, i32 4, i32 0, !"float", !"bgWarmth", i32 4, i32 4, i32 0, !"float", !"fgWarmth", i32 8, i32 4, i32 0, !"float", !"bgRotate", i32 12, i32 4, i32 0, !"float", !"fgRotate", i32 16, i32 4, i32 0, !"float", !"personWarmth", i32 20, i32 4, i32 0, !"float", !"personRotate", i32 24, i32 4, i32 3, !"float", !"hue", i32 36, i32 4, i32 3, !"float", !"range", i32 48, i32 4, i32 3, !"float", !"strength", i32 60, i32 4, i32 0, !"float", !"shadow", i32 64, i32 4, i32 0, !"float", !"mids", i32 68, i32 4, i32 0, !"float", !"high", i32 72, i32 4, i32 3, !"float", !"shadowRGB", i32 84, i32 4, i32 3, !"float", !"midsRGB", i32 96, i32 4, i32 3, !"float", !"highRGB", i32 108, i32 4, i32 0, !"float", !"deRed", i32 112, i32 4, i32 0, !"float", !"deRedSatReduction", i32 116, i32 4, i32 0, !"float", !"deYellow", i32 120, i32 4, i32 0, !"float", !"skinWarmth", i32 124, i32 4, i32 0, !"float", !"skinProtectStrength", i32 128, i32 4, i32 0, !"float", !"skinProtectRange", i32 132, i32 4, i32 0, !"float", !"skinRatioThreshold"}
!21 = !{i32 0, i32 4, i32 0, !"float", !"toneMinusMids", i32 4, i32 4, i32 0, !"float", !"toneMinusExposure", i32 8, i32 4, i32 0, !"float", !"toneMinusPersonExposure", i32 12, i32 4, i32 0, !"float", !"toneMinusFGScale", i32 16, i32 4, i32 0, !"float", !"toneMinusPersonSatScale", i32 20, i32 4, i32 0, !"float", !"toneMinusPersonContrastMax", i32 24, i32 4, i32 0, !"float", !"toneMinusPersonContrastScale", i32 28, i32 4, i32 0, !"float", !"toneMinusBGContrastScale", i32 32, i32 4, i32 0, !"float", !"toneMinusBGContrastMax", i32 36, i32 4, i32 0, !"float", !"toneMinusLTMRatio", i32 40, i32 4, i32 0, !"float", !"toneMinusPersonSmartContrastScale", i32 44, i32 4, i32 0, !"float", !"tonePlusPersonSatScale", i32 48, i32 4, i32 0, !"float", !"tonePlusFGScale", i32 52, i32 4, i32 0, !"float", !"tonePlusExposure", i32 56, i32 4, i32 0, !"float", !"tonePlusBGContrast", i32 60, i32 4, i32 0, !"float", !"colorCubeToneBiasMinGamma", i32 64, i32 4, i32 0, !"float", !"colorCubeToneBiasMaxGamma", i32 68, i32 4, i32 0, !"float", !"starkBWBackgroundRed", i32 72, i32 4, i32 0, !"float", !"starkBWBackgroundGreen", i32 76, i32 4, i32 0, !"float", !"starkBWBackgroundBlue", i32 80, i32 4, i32 0, !"float", !"starkBWWhitesMax", i32 84, i32 4, i32 0, !"float", !"defaultContrastBump", i32 88, i32 4, i32 0, !"float", !"defaultSatBump", i32 92, i32 4, i32 0, !"float", !"defaultMidsBump", i32 96, i32 4, i32 0, !"float", !"defaultLightenBump", i32 100, i32 4, i32 0, !"float", !"dfContrastBump", i32 104, i32 4, i32 0, !"float", !"dfSatBump", i32 108, i32 4, i32 0, !"float", !"dfMidsBump", i32 112, i32 4, i32 0, !"float", !"dfLightenBump", i32 116, i32 4, i32 0, !"float", !"dfLowLightStarts", i32 120, i32 4, i32 0, !"float", !"dfLowLightMax", i32 124, i32 4, i32 0, !"float", !"dfLowLightContrastBump", i32 128, i32 4, i32 0, !"float", !"dfLowLightSatBump", i32 132, i32 4, i32 0, !"float", !"dfLowLightMidsBump", i32 136, i32 4, i32 0, !"float", !"dfLowLightLightenBump", i32 140, i32 4, i32 0, !"float", !"ubContrastBump", i32 144, i32 4, i32 0, !"float", !"ubSatBump", i32 148, i32 4, i32 0, !"float", !"ubMidsBump", i32 152, i32 4, i32 0, !"float", !"ubLightenBump", i32 156, i32 4, i32 0, !"float", !"digitalFlashContrastBump", i32 160, i32 4, i32 0, !"float", !"digitalFlashSatBump", i32 164, i32 4, i32 0, !"float", !"digitalFlashMidsBump", i32 168, i32 4, i32 0, !"float", !"digitalFlashLightenBump", i32 172, i32 4, i32 0, !"float", !"swfrContrastBump", i32 176, i32 4, i32 0, !"float", !"swfrSatBump", i32 180, i32 4, i32 0, !"float", !"swfrMidsBump", i32 184, i32 4, i32 0, !"float", !"swfrLightenBump", i32 188, i32 4, i32 0, !"float", !"wysContrastBump", i32 192, i32 4, i32 0, !"float", !"wysSatBump", i32 196, i32 4, i32 0, !"float", !"wysMidsBump", i32 200, i32 4, i32 0, !"float", !"wysLightenBump", i32 204, i32 4, i32 0, !"float", !"sfdContrastBump", i32 208, i32 4, i32 0, !"float", !"sfdSatBump", i32 212, i32 4, i32 0, !"float", !"sfdMidsBump", i32 216, i32 4, i32 0, !"float", !"sfdLightenBump", i32 220, i32 4, i32 0, !"float", !"videoContrastBump", i32 224, i32 4, i32 0, !"float", !"videoSatBump", i32 228, i32 4, i32 0, !"float", !"videoMidsBump", i32 232, i32 4, i32 0, !"float", !"videoLightenBump", i32 236, i32 4, i32 0, !"float", !"foodToneScale", i32 240, i32 4, i32 0, !"float", !"foodColorScale", i32 244, i32 4, i32 0, !"float", !"foodIntensityScale", i32 248, i32 4, i32 0, !"float", !"sunsetToneScale", i32 252, i32 4, i32 0, !"float", !"sunsetColorScale", i32 256, i32 4, i32 0, !"float", !"sunsetIntensityScale", i32 260, i32 4, i32 0, !"float", !"longGrayLiftMix"}
!22 = !{i32 0, i32 4, i32 0, !"float", !"bwBackgroundHue", i32 4, i32 4, i32 0, !"float", !"bwForegroundHue", i32 8, i32 4, i32 0, !"float", !"colorBoostScale", i32 12, i32 4, i32 0, !"float", !"shadMidHighPersonMix"}
!23 = !{i32 0, i32 1, i32 0, !"bool", !"doHazeTuning", i32 4, i32 4, i32 0, !"float", !"liftStrength", i32 8, i32 4, i32 0, !"float", !"bgLift", i32 12, i32 4, i32 0, !"float", !"personLift", i32 16, i32 4, i32 0, !"float", !"bgMids", i32 20, i32 4, i32 0, !"float", !"personMids", i32 24, i32 4, i32 0, !"float", !"satMix", i32 28, i32 4, i32 0, !"float", !"contrast", i32 32, i32 4, i32 0, !"float", !"localContrast"}
!24 = !{i32 0, i32 4, i32 0, !"float", !"whites", i32 4, i32 4, i32 0, !"float", !"contrast", i32 8, i32 4, i32 0, !"float", !"richSat", i32 12, i32 4, i32 0, !"float", !"shadows", i32 16, i32 4, i32 0, !"float", !"gammaContrast", i32 20, i32 4, i32 0, !"float", !"localContrast", i32 24, i32 4, i32 0, !"float", !"airy", i32 28, i32 4, i32 0, !"float", !"mids", i32 32, i32 4, i32 0, !"float", !"sat", i32 36, i32 4, i32 0, !"float", !"lighten", i32 40, i32 4, i32 0, !"float", !"underGrass", i32 44, i32 4, i32 0, !"float", !"airyGamma", i32 48, i32 4, i32 0, !"float", !"warmthMatchI", i32 52, i32 4, i32 0, !"float", !"warmthMatchQ", i32 56, i32 4, i32 0, !"float", !"warmthMatchSkyI", i32 60, i32 4, i32 0, !"float", !"warmthMatchSkyQ", i32 64, i32 4, i32 0, !"float", !"bgGlobalMix"}
!25 = !{i32 0, i32 4, i32 0, !"float", !"personMix", i32 4, i32 4, i32 0, !"float", !"airy", i32 8, i32 4, i32 0, !"float", !"mids", i32 12, i32 4, i32 0, !"float", !"lighten", i32 16, i32 4, i32 0, !"float", !"whites", i32 20, i32 4, i32 0, !"float", !"airyGamma", i32 24, i32 4, i32 0, !"float", !"shadows", i32 28, i32 4, i32 0, !"float", !"contrast", i32 32, i32 4, i32 0, !"float", !"smartContrast", i32 36, i32 4, i32 0, !"float", !"skinHighLights", i32 40, i32 4, i32 0, !"float", !"skinLocalContrast", i32 44, i32 4, i32 0, !"float", !"saturation", i32 48, i32 4, i32 0, !"float", !"faceI", i32 52, i32 4, i32 0, !"float", !"faceQ", i32 56, i32 4, i32 0, !"float", !"underTone", i32 60, i32 4, i32 0, !"float", !"neckShade"}
!26 = !{i32 0, i32 4, i32 0, !"float", !"bgLTM", i32 4, i32 4, i32 0, !"float", !"fgLTM", i32 8, i32 4, i32 0, !"float", !"bgExposureGain", i32 12, i32 4, i32 0, !"float", !"fgExposureGain", i32 16, i32 4, i32 0, !"float", !"GTC", i32 20, i32 4, i32 0, !"float", !"HR", i32 24, i32 4, i32 0, !"float", !"personHR"}
!27 = !{i32 1, !"air.buffer", !"air.buffer_size", i32 10640, !"air.location_index", i32 3, i32 1, !"air.read_write", !"air.address_space", i32 1, !"air.struct_type_info", !28, !"air.arg_type_size", i32 10640, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"SSRStats", !"air.arg_name", !"stats"}
!28 = !{i32 0, i32 4, i32 2560, !"uint", !"globalHistogram", !"air.struct_type_info", !29, i32 10240, i32 36, i32 10, !"SSRGlobalStats", !"globalStats", i32 10600, i32 4, i32 0, !"uint", !"globalPersonCount", i32 10604, i32 4, i32 0, !"uint", !"globalSkinCount", i32 10608, i32 4, i32 0, !"float", !"peopleRatio", i32 10612, i32 4, i32 0, !"float", !"skinRatio", !"air.struct_type_info", !30, i32 10616, i32 12, i32 0, !"SSRBasicStats", !"linBasicStats", !"air.struct_type_info", !30, i32 10628, i32 12, i32 0, !"SSRBasicStats", !"ltmBasicStats"}
!29 = !{i32 0, i32 4, i32 0, !"float", !"highKey", i32 4, i32 4, i32 0, !"float", !"p02", i32 8, i32 4, i32 0, !"float", !"p10", i32 12, i32 4, i32 0, !"float", !"p25", i32 16, i32 4, i32 0, !"float", !"p50", i32 20, i32 4, i32 0, !"float", !"p75", i32 24, i32 4, i32 0, !"float", !"p98", i32 28, i32 4, i32 0, !"float", !"blackPoint", i32 32, i32 4, i32 0, !"float", !"whitePoint"}
!30 = !{i32 0, i32 4, i32 0, !"float", !"min", i32 4, i32 4, i32 0, !"float", !"max", i32 8, i32 4, i32 0, !"float", !"avg"}
!31 = !{!32, !36, i64 10636}
!32 = !{!"_ZTS8SSRStats", !33, i64 0, !33, i64 10240, !35, i64 10600, !35, i64 10604, !36, i64 10608, !36, i64 10612, !37, i64 10616, !37, i64 10628}
!33 = !{!"omnipotent char", !34, i64 0}
!34 = !{!"Simple C++ TBAA"}
!35 = !{!"int", !33, i64 0}
!36 = !{!"float", !33, i64 0}
!37 = !{!"_ZTS13SSRBasicStats", !36, i64 0, !36, i64 4, !36, i64 8}
!38 = !{!39}
!39 = distinct !{!39, !40, !"air-alias-scope-arg(1)"}
!40 = distinct !{!40, !"air-alias-scopes(updateBaseGainWithStats)"}
!41 = !{!42}
!42 = distinct !{!42, !40, !"air-alias-scope-arg(0)"}
!43 = !{!32, !36, i64 10624}
!44 = !{!45, !36, i64 28}
!45 = !{!"_ZTS9SSRParams", !46, i64 0, !36, i64 4, !36, i64 8, !36, i64 12, !36, i64 16, !36, i64 20, !36, i64 24, !36, i64 28, !47, i64 32, !48, i64 36, !49, i64 172, !50, i64 436, !51, i64 452, !53, i64 488, !54, i64 556, !55, i64 620, !36, i64 648, !56, i64 652, !36, i64 656, !36, i64 660, !36, i64 664, !36, i64 668}
!46 = !{!"_ZTS11SSRCastType", !33, i64 0}
!47 = !{!"_ZTS12SSRSceneType", !33, i64 0}
!48 = !{!"_ZTS18SSRCastAdjustments", !36, i64 0, !36, i64 4, !36, i64 8, !36, i64 12, !36, i64 16, !36, i64 20, !33, i64 24, !33, i64 36, !33, i64 48, !36, i64 60, !36, i64 64, !36, i64 68, !33, i64 72, !33, i64 84, !33, i64 96, !36, i64 108, !36, i64 112, !36, i64 116, !36, i64 120, !36, i64 124, !36, i64 128, !36, i64 132}
!49 = !{!"_ZTS18SSRToneAdjustments", !36, i64 0, !36, i64 4, !36, i64 8, !36, i64 12, !36, i64 16, !36, i64 20, !36, i64 24, !36, i64 28, !36, i64 32, !36, i64 36, !36, i64 40, !36, i64 44, !36, i64 48, !36, i64 52, !36, i64 56, !36, i64 60, !36, i64 64, !36, i64 68, !36, i64 72, !36, i64 76, !36, i64 80, !36, i64 84, !36, i64 88, !36, i64 92, !36, i64 96, !36, i64 100, !36, i64 104, !36, i64 108, !36, i64 112, !36, i64 116, !36, i64 120, !36, i64 124, !36, i64 128, !36, i64 132, !36, i64 136, !36, i64 140, !36, i64 144, !36, i64 148, !36, i64 152, !36, i64 156, !36, i64 160, !36, i64 164, !36, i64 168, !36, i64 172, !36, i64 176, !36, i64 180, !36, i64 184, !36, i64 188, !36, i64 192, !36, i64 196, !36, i64 200, !36, i64 204, !36, i64 208, !36, i64 212, !36, i64 216, !36, i64 220, !36, i64 224, !36, i64 228, !36, i64 232, !36, i64 236, !36, i64 240, !36, i64 244, !36, i64 248, !36, i64 252, !36, i64 256, !36, i64 260}
!50 = !{!"_ZTS19SSRColorAdjustments", !36, i64 0, !36, i64 4, !36, i64 8, !36, i64 12}
!51 = !{!"_ZTS18SSRHazeAdjustments", !52, i64 0, !36, i64 4, !36, i64 8, !36, i64 12, !36, i64 16, !36, i64 20, !36, i64 24, !36, i64 28, !36, i64 32}
!52 = !{!"bool", !33, i64 0}
!53 = !{!"_ZTS15SSRBGAdjustment", !36, i64 0, !36, i64 4, !36, i64 8, !36, i64 12, !36, i64 16, !36, i64 20, !36, i64 24, !36, i64 28, !36, i64 32, !36, i64 36, !36, i64 40, !36, i64 44, !36, i64 48, !36, i64 52, !36, i64 56, !36, i64 60, !36, i64 64}
!54 = !{!"_ZTS15SSRFGAdjustment", !36, i64 0, !36, i64 4, !36, i64 8, !36, i64 12, !36, i64 16, !36, i64 20, !36, i64 24, !36, i64 28, !36, i64 32, !36, i64 36, !36, i64 40, !36, i64 44, !36, i64 48, !36, i64 52, !36, i64 56, !36, i64 60}
!55 = !{!"_ZTS25SSRSemanticToneAdjustment", !36, i64 0, !36, i64 4, !36, i64 8, !36, i64 12, !36, i64 16, !36, i64 20, !36, i64 24}
!56 = !{!"_ZTS13SSRTuningType", !33, i64 0}
!57 = !{!45, !36, i64 24}
