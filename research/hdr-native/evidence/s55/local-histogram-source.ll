; ModuleID = '/Users/runner/work/_temp/air-only/0002.bc'
source_filename = "calculateLocalHistogramStats_all"
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v24:32:32-v32:32:32-v48:64:64-v64:64:64-v96:128:128-v128:128:128-v192:256:256-v256:256:256-v512:512:512-v1024:1024:1024-n8:16:32"
target triple = "air64_v29-apple-macosx27.0.0"

%union.counter_t = type { %"struct.metal::_atomic.186" }
%"struct.metal::_atomic.186" = type { i32 }
%union.histogram_t = type { [256 x %"struct.metal::_atomic.186"] }
%struct.SSRRenderROI = type { <2 x i16>, <2 x i16>, <2 x i16>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <2 x i16>, [12 x i8] }
%struct.SSRColorManagement.192 = type { %struct.SSRColorConversion.191, %struct.SSRColorConversion.191, %struct.SSRColorConversion.191, %struct.SSRColorConversion.191 }
%struct.SSRColorConversion.191 = type <{ i32, [12 x i8], %"struct.metal::matrix.17.190", i8, [15 x i8] }>
%"struct.metal::matrix.17.190" = type { [3 x <3 x float>] }
%struct.SSRParams = type { i32, float, float, float, float, float, float, float, i32, %struct.SSRCastAdjustments, %struct.SSRToneAdjustments, %struct.SSRColorAdjustments, %struct.SSRHazeAdjustments, %struct.SSRBGAdjustment, %struct.SSRFGAdjustment, %struct.SSRSemanticToneAdjustment, float, i32, float, float, float, float }
%struct.SSRCastAdjustments = type { float, float, float, float, float, float, [3 x float], [3 x float], [3 x float], float, float, float, [3 x float], [3 x float], [3 x float], float, float, float, float, float, float, float }
%struct.SSRToneAdjustments = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRColorAdjustments = type { float, float, float, float }
%struct.SSRHazeAdjustments = type { i8, float, float, float, float, float, float, float, float }
%struct.SSRBGAdjustment = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRFGAdjustment = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRSemanticToneAdjustment = type { float, float, float, float, float, float, float }
%struct.SSRStats = type { [10 x [256 x i32]], [10 x %struct.SSRGlobalStats], i32, i32, float, float, %struct.SSRBasicStats, %struct.SSRBasicStats }
%struct.SSRGlobalStats = type { float, float, float, float, float, float, float, float, float }
%struct.SSRBasicStats = type { float, float, float }
%struct.SSRIntermediateStats = type { [10 x [32 x [32 x [256 x i32]]]], [10 x [32 x [32 x %struct.SSRLocalStats]]], [32 x [32 x i32]], [32 x [32 x i32]] }
%struct.SSRLocalStats = type { float, float }

@__metal_implicit_fc_pred_0.41 = internal addrspace(2) global i8 0, align 1
@_ZL17useSrlBeforeStats = internal unnamed_addr addrspace(2) global i8 undef, align 1
@_Z17useSrlBeforeStats.MTL_FC_INIT_2_b = internal unnamed_addr addrspace(2) externally_initialized constant i8 undef, section "air.fc_initializer", align 1
@_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9skinCount = internal addrspace(3) global %union.counter_t undef, align 4
@_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E11personCount = internal addrspace(3) global %union.counter_t undef, align 4
@_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p50Idx = internal addrspace(3) global [10 x %union.counter_t] zeroinitializer, align 4
@_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p98Idx = internal addrspace(3) global [10 x %union.counter_t] zeroinitializer, align 4
@_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram = internal addrspace(3) global [10 x %union.histogram_t] zeroinitializer, align 4
@_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E11sampleCount = internal addrspace(3) global %union.counter_t undef, align 4
@__air_sampler_state = internal addrspace(2) constant [2 x i64] [i64 34901797601053257, i64 0], align 8
@__air_sampler_state.3 = internal addrspace(2) constant [2 x i64] [i64 34901797601020489, i64 0], align 8
@llvm.global_ctors = appending global [1 x { i32, ptr, ptr }] [{ i32, ptr, ptr } { i32 65535, ptr @_GLOBAL__sub_I_CMISmartStyleMetalRendererV1.metal, ptr null }]
@llvm.compiler.used = appending global [1 x ptr] [ptr addrspacecast (ptr addrspace(2) @__metal_implicit_fc_pred_0.41 to ptr)], section "llvm.metadata"

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i8 @air.normalize_function_constant_predicate.i8(i8) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define internal void @_GLOBAL__sub_I_CMISmartStyleMetalRendererV1.metal() #1 section "air.static_init" {
  %1 = load i8, ptr addrspace(2) @_Z17useSrlBeforeStats.MTL_FC_INIT_2_b, align 1, !tbaa !58, !range !62
  store i8 %1, ptr addrspace(2) @_ZL17useSrlBeforeStats, align 1, !tbaa !58
  %2 = tail call i8 @air.normalize_function_constant_predicate.i8(i8 %1) #11
  store i8 %2, ptr addrspace(2) @__metal_implicit_fc_pred_0.41, align 1
  ret void
}

; Function Attrs: convergent nounwind
define void @calculateLocalHistogramStats_all(ptr addrspace(1) %0, ptr addrspace(2) noundef readonly align 4 captures(none) dereferenceable(4) "air-buffer-no-alias" %1, ptr addrspace(1) %2, ptr addrspace(1) %3, ptr addrspace(1) %4, ptr addrspace(1) %5, ptr addrspace(1) %6, ptr addrspace(1) %7, ptr addrspace(2) noundef readonly align 16 captures(none) dereferenceable(320) "air-buffer-no-alias" %8, ptr addrspace(2) noundef readonly align 4 captures(none) dereferenceable(672) "air-buffer-no-alias" %9, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(10640) "air-buffer-no-alias" %10, ptr addrspace(1) noundef writeonly align 4 captures(none) dereferenceable(10575872) "air-buffer-no-alias" %11, ptr addrspace(2) noundef readonly align 16 captures(none) dereferenceable(176) "air-buffer-no-alias" %12, i16 noundef %13, i16 noundef %14, <2 x i16> noundef %15, i16 noundef %16, <2 x i16> noundef %17, <2 x i16> noundef %18, <2 x i16> noundef %19) local_unnamed_addr #2 {
  %21 = extractelement <2 x i16> %18, i64 0
  %22 = zext i16 %21 to i32
  %23 = extractelement <2 x i16> %18, i64 1
  %24 = zext i16 %23 to i32
  %25 = mul nuw nsw i32 %22, %24
  %26 = tail call fast half @air.convert.f.f16.u.i32(i32 %25) #11
  %27 = fdiv fast half 2.560000e+02, %26
  %28 = tail call fast half @air.ceil.f16(half %27) #11
  %29 = tail call i32 @air.convert.u.i32.f.f16(half %28) #11
  store i32 0, ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E11personCount, align 4, !tbaa !63
  store i32 0, ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9skinCount, align 4, !tbaa !63
  store i32 0, ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E11sampleCount, align 4, !tbaa !63
  %30 = zext i16 %16 to i32
  %31 = icmp eq i16 %16, 0
  %32 = icmp eq i32 %29, 0
  %33 = mul i32 %29, %30
  br label %67

34:                                               ; preds = %78
  tail call void @air.wg.barrier(i32 2, i32 5, i32 1) #12
  %35 = tail call i32 @air.get_width_texture_2d(ptr addrspace(1) readonly captures(none) %0, i32 0) #13, !alias.scope !64, !noalias !67
  %36 = tail call fast float @air.convert.f.f32.u.i32(i32 %35) #11
  %37 = insertelement <2 x float> undef, float %36, i64 0
  %38 = tail call i32 @air.get_height_texture_2d(ptr addrspace(1) readonly captures(none) %0, i32 0) #13, !alias.scope !64, !noalias !67
  %39 = tail call fast float @air.convert.f.f32.u.i32(i32 %38) #11
  %40 = insertelement <2 x float> %37, float %39, i64 1
  %41 = fmul fast <2 x float> %40, splat (float 3.125000e-02)
  %42 = tail call fast <2 x float> @air.convert.f.v2f32.u.v2i16(<2 x i16> %19) #11
  %43 = fmul fast <2 x float> %41, %42
  %44 = tail call fast <2 x float> @air.convert.f.v2f32.u.v2i16(<2 x i16> %17) #11
  %45 = fadd fast <2 x float> %44, splat (float 5.000000e-01)
  %46 = fadd fast <2 x float> %45, %43
  %47 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %12, i64 0, i32 3
  %48 = load <4 x float>, ptr addrspace(2) %47, align 16, !alias.scope !74, !noalias !75
  %49 = shufflevector <4 x float> %48, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %50 = fmul fast <2 x float> %46, %49
  %51 = shufflevector <4 x float> %48, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %52 = fadd fast <2 x float> %50, %51
  %53 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %0, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %52, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #14
  %54 = extractvalue { <4 x half>, i8 } %53, 0
  %55 = shufflevector <4 x half> %54, <4 x half> poison, <3 x i32> <i32 0, i32 1, i32 2>
  %56 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %12, i64 0, i32 9
  %57 = load <4 x float>, ptr addrspace(2) %56, align 16, !alias.scope !74, !noalias !75
  %58 = shufflevector <4 x float> %57, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %59 = fmul fast <2 x float> %58, %46
  %60 = shufflevector <4 x float> %57, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %61 = fadd fast <2 x float> %59, %60
  %62 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %61, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #14
  %63 = extractvalue { <4 x half>, i8 } %62, 0
  %64 = extractelement <4 x half> %63, i64 0
  %65 = load i8, ptr addrspace(2) @_ZL17useSrlBeforeStats, align 1, !tbaa !58, !range !62
  %66 = icmp eq i8 %65, 0
  br i1 %66, label %96, label %93

67:                                               ; preds = %78, %20
  %68 = phi i16 [ 0, %20 ], [ %79, %78 ]
  br i1 %31, label %69, label %73

69:                                               ; preds = %67
  %70 = zext i16 %68 to i64
  %71 = getelementptr inbounds [10 x %union.counter_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p98Idx, i64 0, i64 %70, i32 0, i32 0
  %72 = getelementptr inbounds [10 x %union.counter_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p50Idx, i64 0, i64 %70, i32 0, i32 0
  store i32 256, ptr addrspace(3) %72, align 4, !tbaa !63
  store i32 256, ptr addrspace(3) %71, align 4, !tbaa !63
  br label %73

73:                                               ; preds = %69, %67
  br i1 %32, label %78, label %74

74:                                               ; preds = %73
  %75 = zext i16 %68 to i64
  %76 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 %75
  %77 = bitcast ptr addrspace(3) %76 to ptr addrspace(3)
  br label %81

78:                                               ; preds = %90, %73
  %79 = add nuw nsw i16 %68, 1
  %80 = icmp eq i16 %79, 10
  br i1 %80, label %34, label %67, !llvm.loop !76

81:                                               ; preds = %90, %74
  %82 = phi i32 [ 0, %74 ], [ %91, %90 ]
  %83 = add i32 %82, %33
  %84 = and i32 %83, 65280
  %85 = icmp eq i32 %84, 0
  br i1 %85, label %86, label %90

86:                                               ; preds = %81
  %87 = and i32 %83, 65535
  %88 = zext i32 %87 to i64
  %89 = getelementptr inbounds [256 x i32], ptr addrspace(3) %77, i64 0, i64 %88
  store i32 0, ptr addrspace(3) %89, align 4, !tbaa !63
  br label %90

90:                                               ; preds = %86, %81
  %91 = add nuw i32 %82, 1
  %92 = icmp eq i32 %91, %29
  br i1 %92, label %78, label %81, !llvm.loop !78

93:                                               ; preds = %34
  %94 = load float, ptr addrspace(2) %1, align 4, !tbaa !79, !alias.scope !81, !noalias !82
  %95 = tail call fast fastcc <3 x half> @_Z16applySemanticSRLDv3_DhfDh(<3 x half> noundef %55, float noundef %94, half noundef %64) #15
  br label %96

96:                                               ; preds = %93, %34
  %97 = phi <3 x half> [ %95, %93 ], [ %55, %34 ]
  %98 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %8, i64 0, i32 0, i32 0
  %99 = load i32, ptr addrspace(2) %98, align 16, !tbaa !83, !alias.scope !88, !noalias !89
  %100 = tail call fastcc <3 x half> @_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_(<3 x half> noundef %97, i32 noundef %99) #15
  %101 = icmp eq i32 %99, 6
  br i1 %101, label %102, label %138

102:                                              ; preds = %96
  %103 = tail call fast half @air.log2.f16(half 9.997550e-02) #11
  %104 = tail call fast half @air.pow.f16(half 1.111330e+00, half %103) #11
  %105 = fpext half %104 to float
  %106 = fmul fast float %105, 1.200000e+00
  %107 = fptrunc float %106 to half
  %108 = extractelement <3 x half> %100, i64 0
  %109 = fpext half %108 to float
  %110 = fmul fast float %109, 2.627000e-01
  %111 = extractelement <3 x half> %100, i64 1
  %112 = fpext half %111 to float
  %113 = fmul fast float %112, f0x3F2D9168
  %114 = fadd fast float %110, %113
  %115 = extractelement <3 x half> %100, i64 2
  %116 = fpext half %115 to float
  %117 = fmul fast float %116, 5.930000e-02
  %118 = fadd fast float %114, %117
  %119 = fpext half %107 to float
  %120 = fadd fast float %119, -1.000000e+00
  %121 = tail call fast float @air.fast_pow.f32(float %118, float %120) #11
  %122 = fptrunc float %121 to half
  %123 = fmul fast half %108, 2.130130e-01
  %124 = fmul fast half %111, 7.148430e-01
  %125 = fadd fast half %123, %124
  %126 = fmul fast half %115, 7.202140e-02
  %127 = fadd fast half %125, %126
  %128 = tail call fast half @air.fmax.f16(half %108, half %111) #11
  %129 = tail call fast half @air.fmax.f16(half %128, half %115) #11
  %130 = fadd fast half %127, %129
  %131 = fmul fast half %130, 5.000000e-01
  %132 = fadd fast half %107, -1.000000e+00
  %133 = tail call fast half @air.pow.f16(half %131, half %132) #11
  %134 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %8, i64 0, i32 0, i32 3
  %135 = load i8, ptr addrspace(2) %134, align 16, !tbaa !90, !range !62, !alias.scope !88, !noalias !89
  %136 = icmp eq i8 %135, 0
  %137 = select fast i1 %136, half %122, half %133
  br label %138

138:                                              ; preds = %102, %96
  %139 = phi half [ %137, %102 ], [ 1.000000e+00, %96 ]
  %140 = insertelement <3 x half> poison, half %139, i64 0
  %141 = shufflevector <3 x half> %140, <3 x half> poison, <3 x i32> zeroinitializer
  %142 = fmul fast <3 x half> %141, %100
  %143 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %8, i64 0, i32 0, i32 2, i32 0, i64 0
  %144 = load <3 x float>, ptr addrspace(2) %143, align 16, !tbaa !79, !alias.scope !88, !noalias !89
  %145 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %144) #11
  %146 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %8, i64 0, i32 0, i32 2, i32 0, i64 1
  %147 = load <3 x float>, ptr addrspace(2) %146, align 16, !tbaa !79, !alias.scope !88, !noalias !89
  %148 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %147) #11
  %149 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %8, i64 0, i32 0, i32 2, i32 0, i64 2
  %150 = load <3 x float>, ptr addrspace(2) %149, align 16, !tbaa !79, !alias.scope !88, !noalias !89
  %151 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %150) #11
  %152 = shufflevector <3 x half> %142, <3 x half> poison, <3 x i32> zeroinitializer
  %153 = fmul fast <3 x half> %152, %145
  %154 = shufflevector <3 x half> %142, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %155 = fmul fast <3 x half> %148, %154
  %156 = fadd fast <3 x half> %153, %155
  %157 = shufflevector <3 x half> %142, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %158 = fmul fast <3 x half> %151, %157
  %159 = fadd fast <3 x half> %156, %158
  %160 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %12, i64 0, i32 4
  %161 = load <4 x float>, ptr addrspace(2) %160, align 16, !alias.scope !74, !noalias !75
  %162 = shufflevector <4 x float> %161, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %163 = fmul fast <2 x float> %162, %46
  %164 = shufflevector <4 x float> %161, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %165 = fadd fast <2 x float> %163, %164
  %166 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %2, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %165, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #14
  %167 = extractvalue { <4 x half>, i8 } %166, 0
  %168 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %8, i64 0, i32 1, i32 2, i32 0, i64 0
  %169 = load <3 x float>, ptr addrspace(2) %168, align 16, !tbaa !79, !alias.scope !88, !noalias !89
  %170 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %169) #11
  %171 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %8, i64 0, i32 1, i32 2, i32 0, i64 1
  %172 = load <3 x float>, ptr addrspace(2) %171, align 16, !tbaa !79, !alias.scope !88, !noalias !89
  %173 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %172) #11
  %174 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %8, i64 0, i32 1, i32 2, i32 0, i64 2
  %175 = load <3 x float>, ptr addrspace(2) %174, align 16, !tbaa !79, !alias.scope !88, !noalias !89
  %176 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %175) #11
  %177 = shufflevector <4 x half> %167, <4 x half> undef, <3 x i32> zeroinitializer
  %178 = fmul fast <3 x half> %170, %177
  %179 = shufflevector <4 x half> %167, <4 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %180 = fmul fast <3 x half> %173, %179
  %181 = fadd fast <3 x half> %180, %178
  %182 = shufflevector <4 x half> %167, <4 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %183 = fmul fast <3 x half> %176, %182
  %184 = fadd fast <3 x half> %181, %183
  %185 = getelementptr inbounds %struct.SSRParams, ptr addrspace(2) %9, i64 0, i32 6
  %186 = load float, ptr addrspace(2) %185, align 4, !tbaa !91, !alias.scope !103, !noalias !104
  %187 = fptrunc float %186 to half
  %188 = insertelement <3 x half> poison, half %187, i64 0
  %189 = shufflevector <3 x half> %188, <3 x half> poison, <3 x i32> zeroinitializer
  %190 = fmul fast <3 x half> %189, %184
  %191 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %12, i64 0, i32 10
  %192 = load <4 x float>, ptr addrspace(2) %191, align 16, !alias.scope !74, !noalias !75
  %193 = shufflevector <4 x float> %192, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %194 = fmul fast <2 x float> %193, %46
  %195 = shufflevector <4 x float> %192, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %196 = fadd fast <2 x float> %194, %195
  %197 = fcmp fast oge half %64, 2.500000e-01
  %198 = tail call fast half @air.convert.f.f16.u.i1(i1 %197) #11
  %199 = tail call i16 @air.convert.u.i16.f.f16(half %198) #11
  %200 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %4, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %196, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #14
  %201 = extractvalue { <4 x half>, i8 } %200, 0
  %202 = extractelement <4 x half> %201, i64 0
  %203 = fcmp fast oge half %202, 2.500000e-01
  %204 = tail call fast half @air.convert.f.f16.u.i1(i1 %203) #11
  %205 = tail call i16 @air.convert.u.i16.f.f16(half %204) #11
  %206 = tail call i32 @air.get_width_texture_2d(ptr addrspace(1) readonly captures(none) %7, i32 0) #13, !alias.scope !64, !noalias !67
  %207 = tail call fast half @air.convert.f.f16.u.i32(i32 %206) #11
  %208 = getelementptr inbounds %struct.SSRParams, ptr addrspace(2) %9, i64 0, i32 7
  %209 = load float, ptr addrspace(2) %208, align 4, !tbaa !105, !alias.scope !103, !noalias !104
  %210 = fptrunc float %209 to half
  %211 = insertelement <3 x half> poison, half %210, i64 0
  %212 = shufflevector <3 x half> %211, <3 x half> poison, <3 x i32> zeroinitializer
  %213 = fmul fast <3 x half> %212, %190
  %214 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %213, <3 x half> splat (half 1.000000e+00)) #11
  %215 = extractelement <3 x half> %214, i64 0
  %216 = fadd fast half %207, -1.000000e+00
  %217 = fmul fast half %215, %216
  %218 = fpext half %217 to float
  %219 = fadd fast float %218, 5.000000e-01
  %220 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %219, i64 0
  %221 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %7, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %220, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #14
  %222 = extractvalue { <4 x half>, i8 } %221, 0
  %223 = extractelement <4 x half> %222, i64 0
  %224 = insertelement <3 x half> undef, half %223, i64 0
  %225 = extractelement <3 x half> %214, i64 1
  %226 = fmul fast half %225, %216
  %227 = fpext half %226 to float
  %228 = fadd fast float %227, 5.000000e-01
  %229 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %228, i64 0
  %230 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %7, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %229, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #14
  %231 = extractvalue { <4 x half>, i8 } %230, 0
  %232 = extractelement <4 x half> %231, i64 0
  %233 = insertelement <3 x half> %224, half %232, i64 1
  %234 = extractelement <3 x half> %214, i64 2
  %235 = fmul fast half %234, %216
  %236 = fpext half %235 to float
  %237 = fadd fast float %236, 5.000000e-01
  %238 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %237, i64 0
  %239 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %7, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %238, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #14
  %240 = extractvalue { <4 x half>, i8 } %239, 0
  %241 = extractelement <4 x half> %240, i64 0
  %242 = insertelement <3 x half> %233, half %241, i64 2
  %243 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %214, <3 x half> %242, <3 x half> splat (half 1.000000e+00)) #11
  %244 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %10, i64 0, i32 7, i32 1
  %245 = load float, ptr addrspace(1) %244, align 4, !tbaa !106, !alias.scope !110, !noalias !111
  %246 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %10, i64 0, i32 6, i32 1
  %247 = load float, ptr addrspace(1) %246, align 4, !tbaa !112, !alias.scope !110, !noalias !111
  %248 = fmul fast float %247, %186
  %249 = fptrunc float %248 to half
  %250 = insertelement <3 x half> poison, half %249, i64 0
  %251 = shufflevector <3 x half> %250, <3 x half> poison, <3 x i32> zeroinitializer
  %252 = fmul fast <3 x half> %251, %212
  %253 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %252, <3 x half> splat (half 1.000000e+00)) #11
  %254 = extractelement <3 x half> %253, i64 0
  %255 = fmul fast half %254, %216
  %256 = fpext half %255 to float
  %257 = fadd fast float %256, 5.000000e-01
  %258 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %257, i64 0
  %259 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %7, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %258, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #14
  %260 = extractvalue { <4 x half>, i8 } %259, 0
  %261 = extractelement <4 x half> %260, i64 0
  %262 = insertelement <3 x half> undef, half %261, i64 0
  %263 = extractelement <3 x half> %253, i64 1
  %264 = fmul fast half %263, %216
  %265 = fpext half %264 to float
  %266 = fadd fast float %265, 5.000000e-01
  %267 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %266, i64 0
  %268 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %7, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %267, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #14
  %269 = extractvalue { <4 x half>, i8 } %268, 0
  %270 = extractelement <4 x half> %269, i64 0
  %271 = insertelement <3 x half> %262, half %270, i64 1
  %272 = extractelement <3 x half> %253, i64 2
  %273 = fmul fast half %272, %216
  %274 = fpext half %273 to float
  %275 = fadd fast float %274, 5.000000e-01
  %276 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %275, i64 0
  %277 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %7, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %276, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #14
  %278 = extractvalue { <4 x half>, i8 } %277, 0
  %279 = extractelement <4 x half> %278, i64 0
  %280 = insertelement <3 x half> %271, half %279, i64 2
  %281 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %253, <3 x half> %280, <3 x half> splat (half 1.000000e+00)) #11
  %282 = extractelement <3 x half> %281, i64 0
  %283 = fptrunc float %245 to half
  %284 = insertelement <3 x half> poison, half %283, i64 0
  %285 = shufflevector <3 x half> %284, <3 x half> poison, <3 x i32> zeroinitializer
  %286 = fdiv fast <3 x half> %159, %285
  %287 = fdiv fast <3 x half> %190, %251
  %288 = shufflevector <3 x half> %281, <3 x half> poison, <3 x i32> zeroinitializer
  %289 = fdiv fast <3 x half> %243, %288
  %290 = tail call fast half @air.dot.v3f16(<3 x half> splat (half 3.332520e-01), <3 x half> %286) #11
  %291 = fmul fast half %290, 2.560000e+02
  %292 = tail call fast half @air.round.f16(half %291) #11
  %293 = tail call i32 @air.convert.s.i32.f.f16(half %292) #11
  %294 = tail call i32 @air.clamp.s.i32(i32 %293, i32 0, i32 255) #11
  %295 = tail call fast half @air.dot.v3f16(<3 x half> splat (half 3.332520e-01), <3 x half> %287) #11
  %296 = fmul fast half %295, 2.560000e+02
  %297 = tail call fast half @air.round.f16(half %296) #11
  %298 = tail call i32 @air.convert.s.i32.f.f16(half %297) #11
  %299 = tail call i32 @air.clamp.s.i32(i32 %298, i32 0, i32 255) #11
  %300 = tail call fast half @air.dot.v3f16(<3 x half> splat (half 3.332520e-01), <3 x half> %289) #11
  %301 = fmul fast half %300, 2.560000e+02
  %302 = tail call fast half @air.round.f16(half %301) #11
  %303 = tail call i32 @air.convert.s.i32.f.f16(half %302) #11
  %304 = tail call i32 @air.clamp.s.i32(i32 %303, i32 0, i32 255) #11
  %305 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %286) #11
  %306 = fmul fast <3 x half> %305, splat (half 2.550000e+02)
  %307 = tail call <3 x i16> @air.convert.u.v3i16.f.v3f16(<3 x half> %306) #11
  %308 = sext i32 %294 to i64
  %309 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 0, i32 0, i64 %308, i32 0
  %310 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) %309, i32 1, i32 0, i32 1, i32 0, i1 false) #16
  %311 = sext i32 %299 to i64
  %312 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 5, i32 0, i64 %311, i32 0
  %313 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) %312, i32 1, i32 0, i32 1, i32 0, i1 false) #16
  %314 = sext i32 %304 to i64
  %315 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 7, i32 0, i64 %314, i32 0
  %316 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) %315, i32 1, i32 0, i32 1, i32 0, i1 false) #16
  %317 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 1, i32 0, i64 %308, i32 0
  %318 = zext i16 %199 to i32
  %319 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) %317, i32 %318, i32 0, i32 1, i32 0, i1 false) #16
  %320 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 6, i32 0, i64 %311, i32 0
  %321 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) %320, i32 %318, i32 0, i32 1, i32 0, i1 false) #16
  %322 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E11personCount, i32 %318, i32 0, i32 1, i32 0, i1 false) #16
  %323 = extractelement <3 x i16> %307, i64 0
  %324 = zext i16 %323 to i64
  %325 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 2, i32 0, i64 %324, i32 0
  %326 = zext i16 %205 to i32
  %327 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) %325, i32 %326, i32 0, i32 1, i32 0, i1 false) #16
  %328 = extractelement <3 x i16> %307, i64 1
  %329 = zext i16 %328 to i64
  %330 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 3, i32 0, i64 %329, i32 0
  %331 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) %330, i32 %326, i32 0, i32 1, i32 0, i1 false) #16
  %332 = extractelement <3 x i16> %307, i64 2
  %333 = zext i16 %332 to i64
  %334 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 4, i32 0, i64 %333, i32 0
  %335 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) %334, i32 %326, i32 0, i32 1, i32 0, i1 false) #16
  %336 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 8, i32 0, i64 %308, i32 0
  %337 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) %336, i32 %326, i32 0, i32 1, i32 0, i1 false) #16
  %338 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 9, i32 0, i64 %311, i32 0
  %339 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) %338, i32 %326, i32 0, i32 1, i32 0, i1 false) #16
  %340 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9skinCount, i32 %326, i32 0, i32 1, i32 0, i1 false) #16
  %341 = tail call i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E11sampleCount, i32 1, i32 0, i32 1, i32 0, i1 false) #16
  tail call void @air.wg.barrier(i32 2, i32 5, i32 1) #12
  %342 = extractelement <2 x i16> %19, i64 1
  %343 = zext i16 %342 to i64
  %344 = extractelement <2 x i16> %19, i64 0
  %345 = zext i16 %344 to i64
  br label %354

346:                                              ; preds = %360
  %347 = fpext half %282 to float
  tail call void @air.wg.barrier(i32 2, i32 5, i32 1) #12
  %348 = icmp ult i16 %16, 256
  br i1 %348, label %349, label %406

349:                                              ; preds = %346
  %350 = icmp ult i32 %25, 256
  %351 = zext i16 %16 to i64
  %352 = zext i16 %14 to i32
  %353 = icmp ult i16 %16, %14
  br label %377

354:                                              ; preds = %360, %138
  %355 = phi i16 [ 0, %138 ], [ %361, %360 ]
  %356 = zext i16 %355 to i64
  br i1 %32, label %360, label %357

357:                                              ; preds = %354
  %358 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 %356
  %359 = bitcast ptr addrspace(3) %358 to ptr addrspace(3)
  br label %363

360:                                              ; preds = %374, %354
  %361 = add nuw nsw i16 %355, 1
  %362 = icmp eq i16 %361, 10
  br i1 %362, label %346, label %354, !llvm.loop !113

363:                                              ; preds = %374, %357
  %364 = phi i32 [ 0, %357 ], [ %375, %374 ]
  %365 = add i32 %364, %33
  %366 = and i32 %365, 65280
  %367 = icmp eq i32 %366, 0
  br i1 %367, label %368, label %374

368:                                              ; preds = %363
  %369 = and i32 %365, 65535
  %370 = zext i32 %369 to i64
  %371 = getelementptr inbounds %struct.SSRIntermediateStats, ptr addrspace(1) %11, i64 0, i32 0, i64 %356, i64 %343, i64 %345, i64 %370
  %372 = getelementptr inbounds [256 x i32], ptr addrspace(3) %359, i64 0, i64 %370
  %373 = load i32, ptr addrspace(3) %372, align 4, !tbaa !63
  store i32 %373, ptr addrspace(1) %371, align 4, !tbaa !114, !alias.scope !115, !noalias !116
  br label %374

374:                                              ; preds = %368, %363
  %375 = add nuw i32 %364, 1
  %376 = icmp eq i32 %375, %29
  br i1 %376, label %360, label %363, !llvm.loop !117

377:                                              ; preds = %403, %349
  %378 = phi i16 [ 0, %349 ], [ %404, %403 ]
  br i1 %350, label %379, label %396

379:                                              ; preds = %377
  br i1 %353, label %380, label %403

380:                                              ; preds = %379
  %381 = zext i16 %378 to i64
  %382 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 %381
  %383 = bitcast ptr addrspace(3) %382 to ptr addrspace(3)
  br label %384

384:                                              ; preds = %384, %380
  %385 = phi i32 [ 0, %380 ], [ %394, %384 ]
  %386 = phi i16 [ 0, %380 ], [ %392, %384 ]
  %387 = add nuw nsw i32 %385, %30
  %388 = zext i32 %387 to i64
  %389 = getelementptr inbounds [256 x i32], ptr addrspace(3) %383, i64 0, i64 %388
  %390 = load i32, ptr addrspace(3) %389, align 4, !tbaa !63
  %391 = tail call i32 @air.simd_prefix_inclusive_sum.u.i32(i32 %390) #12
  store i32 %391, ptr addrspace(3) %389, align 4, !tbaa !63
  %392 = add i16 %386, 1
  %393 = zext i16 %392 to i32
  %394 = mul nuw nsw i32 %393, %352
  %395 = icmp ult i32 %394, 256
  br i1 %395, label %384, label %403, !llvm.loop !118

396:                                              ; preds = %377
  %397 = zext i16 %378 to i64
  %398 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 %397
  %399 = bitcast ptr addrspace(3) %398 to ptr addrspace(3)
  %400 = getelementptr inbounds [256 x i32], ptr addrspace(3) %399, i64 0, i64 %351
  %401 = load i32, ptr addrspace(3) %400, align 4, !tbaa !63
  %402 = tail call i32 @air.simd_prefix_inclusive_sum.u.i32(i32 %401) #12
  store i32 %402, ptr addrspace(3) %400, align 4, !tbaa !63
  br label %403

403:                                              ; preds = %396, %384, %379
  %404 = add nuw nsw i16 %378, 1
  %405 = icmp eq i16 %404, 10
  br i1 %405, label %406, label %377, !llvm.loop !119

406:                                              ; preds = %403, %346
  %407 = icmp eq i16 %13, 0
  br i1 %407, label %408, label %409

408:                                              ; preds = %406
  tail call void @air.atomic.fence(i32 noundef 1, i32 noundef 3, i32 noundef 2) #17
  br label %409

409:                                              ; preds = %408, %406
  tail call void @air.wg.barrier(i32 2, i32 5, i32 1) #12
  %410 = zext i16 %14 to i32
  %411 = icmp uge i16 %16, %14
  %412 = icmp ugt i16 %14, 255
  %413 = or i1 %412, %411
  br label %426

414:                                              ; preds = %449
  tail call void @air.wg.barrier(i32 2, i32 5, i32 1) #12
  %415 = load i32, ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E11sampleCount, align 4, !tbaa !63
  %416 = tail call fast float @air.convert.f.f32.u.i32(i32 %415) #11
  %417 = fmul fast float %416, 5.000000e-01
  %418 = tail call i16 @air.convert.u.i16.f.f32(float %417) #11
  %419 = fmul fast float %416, 9.800000e-01
  %420 = tail call i16 @air.convert.u.i16.f.f32(float %419) #11
  %421 = icmp ult i32 %25, 256
  br i1 %421, label %422, label %482

422:                                              ; preds = %414
  %423 = icmp ult i16 %16, %14
  %424 = zext i16 %418 to i32
  %425 = zext i16 %420 to i32
  br label %452

426:                                              ; preds = %449, %409
  %427 = phi i16 [ 0, %409 ], [ %450, %449 ]
  br i1 %413, label %449, label %428

428:                                              ; preds = %426
  %429 = zext i16 %427 to i64
  %430 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 %429
  %431 = bitcast ptr addrspace(3) %430 to ptr addrspace(3)
  br label %432

432:                                              ; preds = %432, %428
  %433 = phi i32 [ %410, %428 ], [ %447, %432 ]
  %434 = phi i16 [ 1, %428 ], [ %445, %432 ]
  %435 = trunc i32 %433 to i16
  %436 = add i16 %435, %16
  %437 = add nsw i16 %435, -1
  %438 = zext i16 %437 to i64
  %439 = getelementptr inbounds [256 x i32], ptr addrspace(3) %431, i64 0, i64 %438
  %440 = load i32, ptr addrspace(3) %439, align 4, !tbaa !63
  %441 = zext i16 %436 to i64
  %442 = getelementptr inbounds [256 x i32], ptr addrspace(3) %431, i64 0, i64 %441
  %443 = load i32, ptr addrspace(3) %442, align 4, !tbaa !63
  %444 = add i32 %443, %440
  store i32 %444, ptr addrspace(3) %442, align 4, !tbaa !63
  %445 = add i16 %434, 1
  %446 = zext i16 %445 to i32
  %447 = mul nuw nsw i32 %446, %410
  %448 = icmp ult i32 %447, 256
  br i1 %448, label %432, label %449, !llvm.loop !120

449:                                              ; preds = %432, %426
  %450 = add nuw nsw i16 %427, 1
  %451 = icmp eq i16 %450, 10
  br i1 %451, label %414, label %426, !llvm.loop !122

452:                                              ; preds = %479, %422
  %453 = phi i16 [ 0, %422 ], [ %480, %479 ]
  br i1 %423, label %454, label %479

454:                                              ; preds = %452
  %455 = zext i16 %453 to i64
  %456 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 %455
  %457 = bitcast ptr addrspace(3) %456 to ptr addrspace(3)
  %458 = getelementptr inbounds [10 x %union.counter_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p50Idx, i64 0, i64 %455, i32 0, i32 0
  %459 = getelementptr inbounds [10 x %union.counter_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p98Idx, i64 0, i64 %455, i32 0, i32 0
  br label %460

460:                                              ; preds = %460, %454
  %461 = phi i32 [ 0, %454 ], [ %477, %460 ]
  %462 = phi i16 [ 0, %454 ], [ %475, %460 ]
  %463 = trunc i32 %461 to i16
  %464 = add i16 %463, %16
  %465 = zext i16 %464 to i64
  %466 = getelementptr inbounds [256 x i32], ptr addrspace(3) %457, i64 0, i64 %465
  %467 = load i32, ptr addrspace(3) %466, align 4, !tbaa !63
  %468 = icmp ugt i32 %467, %424
  %469 = icmp ugt i32 %467, %425
  %470 = zext i16 %464 to i32
  %471 = select i1 %468, i32 %470, i32 256
  %472 = tail call i32 @air.atomic.local.min.u.i32(ptr addrspace(3) captures(none) %458, i32 %471, i32 0, i32 1, i32 0, i1 false) #16
  %473 = select i1 %469, i32 %470, i32 256
  %474 = tail call i32 @air.atomic.local.min.u.i32(ptr addrspace(3) captures(none) %459, i32 %473, i32 0, i32 1, i32 0, i1 false) #16
  %475 = add i16 %462, 1
  %476 = zext i16 %475 to i32
  %477 = mul nuw nsw i32 %476, %410
  %478 = icmp ult i32 %477, 256
  br i1 %478, label %460, label %479, !llvm.loop !123

479:                                              ; preds = %460, %452
  %480 = add nuw nsw i16 %453, 1
  %481 = icmp eq i16 %480, 10
  br i1 %481, label %504, label %452, !llvm.loop !124

482:                                              ; preds = %414
  br i1 %348, label %483, label %504

483:                                              ; preds = %482
  %484 = zext i16 %16 to i64
  %485 = zext i16 %418 to i32
  %486 = zext i16 %420 to i32
  br label %487

487:                                              ; preds = %487, %483
  %488 = phi i16 [ 0, %483 ], [ %502, %487 ]
  %489 = zext i16 %488 to i64
  %490 = getelementptr inbounds [10 x %union.histogram_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9histogram, i64 0, i64 %489
  %491 = bitcast ptr addrspace(3) %490 to ptr addrspace(3)
  %492 = getelementptr inbounds [256 x i32], ptr addrspace(3) %491, i64 0, i64 %484
  %493 = load i32, ptr addrspace(3) %492, align 4, !tbaa !63
  %494 = icmp ugt i32 %493, %485
  %495 = icmp ugt i32 %493, %486
  %496 = getelementptr inbounds [10 x %union.counter_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p50Idx, i64 0, i64 %489, i32 0, i32 0
  %497 = select i1 %494, i32 %30, i32 256
  %498 = tail call i32 @air.atomic.local.min.u.i32(ptr addrspace(3) captures(none) %496, i32 %497, i32 0, i32 1, i32 0, i1 false) #16
  %499 = getelementptr inbounds [10 x %union.counter_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p98Idx, i64 0, i64 %489, i32 0, i32 0
  %500 = select i1 %495, i32 %30, i32 256
  %501 = tail call i32 @air.atomic.local.min.u.i32(ptr addrspace(3) captures(none) %499, i32 %500, i32 0, i32 1, i32 0, i1 false) #16
  %502 = add nuw nsw i16 %488, 1
  %503 = icmp eq i16 %502, 10
  br i1 %503, label %504, label %487, !llvm.loop !125

504:                                              ; preds = %487, %482, %479
  tail call void @air.wg.barrier(i32 2, i32 5, i32 1) #12
  br i1 %31, label %508, label %567

505:                                              ; preds = %525
  %506 = load i32, ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p50Idx, align 4, !tbaa !63
  %507 = icmp ugt i32 %506, 255
  br i1 %507, label %534, label %531

508:                                              ; preds = %525, %504
  %509 = phi i16 [ %529, %525 ], [ 0, %504 ]
  %510 = zext i16 %509 to i64
  %511 = getelementptr inbounds [10 x %union.counter_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p50Idx, i64 0, i64 %510, i32 0, i32 0
  %512 = load i32, ptr addrspace(3) %511, align 4, !tbaa !63
  %513 = icmp ugt i32 %512, 255
  br i1 %513, label %517, label %514

514:                                              ; preds = %508
  %515 = tail call fast float @air.convert.f.f32.u.i32(i32 %512) #11
  %516 = fmul fast float %515, f0x3B808081
  br label %517

517:                                              ; preds = %514, %508
  %518 = phi fast float [ %516, %514 ], [ -1.000000e+00, %508 ]
  %519 = getelementptr inbounds [10 x %union.counter_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p98Idx, i64 0, i64 %510, i32 0, i32 0
  %520 = load i32, ptr addrspace(3) %519, align 4, !tbaa !63
  %521 = icmp ugt i32 %520, 255
  br i1 %521, label %525, label %522

522:                                              ; preds = %517
  %523 = tail call fast float @air.convert.f.f32.u.i32(i32 %520) #11
  %524 = fmul fast float %523, f0x3B808081
  br label %525

525:                                              ; preds = %522, %517
  %526 = phi fast float [ %524, %522 ], [ -1.000000e+00, %517 ]
  %527 = getelementptr inbounds %struct.SSRIntermediateStats, ptr addrspace(1) %11, i64 0, i32 1, i64 %510, i64 %343, i64 %345, i32 0
  store float %518, ptr addrspace(1) %527, align 4, !tbaa !126, !alias.scope !115, !noalias !116
  %528 = getelementptr inbounds %struct.SSRIntermediateStats, ptr addrspace(1) %11, i64 0, i32 1, i64 %510, i64 %343, i64 %345, i32 1
  store float %526, ptr addrspace(1) %528, align 4, !tbaa !128, !alias.scope !115, !noalias !116
  %529 = add nuw nsw i16 %509, 1
  %530 = icmp eq i16 %529, 10
  br i1 %530, label %505, label %508, !llvm.loop !129

531:                                              ; preds = %505
  %532 = tail call fast float @air.convert.f.f32.u.i32(i32 %506) #11
  %533 = fmul fast float %532, f0x3B808081
  br label %534

534:                                              ; preds = %531, %505
  %535 = phi fast float [ %533, %531 ], [ -1.000000e+00, %505 ]
  %536 = load i32, ptr addrspace(3) getelementptr inbounds ([10 x %union.counter_t], ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E6p50Idx, i64 0, i64 7, i32 0, i32 0), align 4, !tbaa !63
  %537 = icmp ugt i32 %536, 255
  br i1 %537, label %541, label %538

538:                                              ; preds = %534
  %539 = tail call fast float @air.convert.f.f32.u.i32(i32 %536) #11
  %540 = fmul fast float %539, f0x3B808081
  br label %541

541:                                              ; preds = %538, %534
  %542 = phi fast float [ %540, %538 ], [ -1.000000e+00, %534 ]
  %543 = getelementptr inbounds %struct.SSRIntermediateStats, ptr addrspace(1) %11, i64 0, i32 2, i64 %343, i64 %345
  %544 = getelementptr inbounds %struct.SSRIntermediateStats, ptr addrspace(1) %11, i64 0, i32 3, i64 %343, i64 %345
  %545 = fmul fast float %245, f0x401C3D8F
  %546 = fmul fast float %545, %535
  %547 = fadd fast float %546, f0xBF87EDE0
  %548 = fptrunc float %547 to half
  %549 = fpext half %548 to float
  %550 = fadd fast float %549, 1.200000e+00
  %551 = fmul fast float %550, 2.941200e-01
  %552 = fptrunc float %551 to half
  %553 = fmul fast float %347, f0x401C3D8F
  %554 = fmul fast float %553, %542
  %555 = fadd fast float %554, f0xBF87EDE0
  %556 = fptrunc float %555 to half
  %557 = fpext half %556 to float
  %558 = fadd fast float %557, 1.200000e+00
  %559 = fmul fast float %558, 2.941200e-01
  %560 = fptrunc float %559 to half
  %561 = load i32, ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E11personCount, align 4, !tbaa !63
  store i32 %561, ptr addrspace(1) %543, align 4, !tbaa !114, !alias.scope !115, !noalias !116
  %562 = load i32, ptr addrspace(3) @_ZZ32calculateLocalHistogramStats_allN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEERU11MTLconstantKfS3_S3_S3_NS0_IDhLS1_2ELS2_0EvEES6_S3_RU11MTLconstantK18SSRColorManagementRU11MTLconstantK9SSRParamsRU9MTLdeviceK8SSRStatsRU9MTLdevice20SSRIntermediateStatsRU11MTLconstantK12SSRRenderROIttDv2_ttSM_SM_SM_E9skinCount, align 4, !tbaa !63
  store i32 %562, ptr addrspace(1) %544, align 4, !tbaa !114, !alias.scope !115, !noalias !116
  %563 = insertelement <4 x half> poison, half %552, i64 0
  %564 = shufflevector <4 x half> %563, <4 x half> poison, <4 x i32> zeroinitializer
  tail call void @air.write_texture_2d.i16.v4f16(ptr addrspace(1) captures(none) %5, <2 x i16> %19, <4 x half> %564, i16 0, i32 2) #18, !alias.scope !64, !noalias !67
  %565 = insertelement <4 x half> poison, half %560, i64 0
  %566 = shufflevector <4 x half> %565, <4 x half> poison, <4 x i32> zeroinitializer
  tail call void @air.write_texture_2d.i16.v4f16(ptr addrspace(1) captures(none) %6, <2 x i16> %19, <4 x half> %566, i16 0, i32 2) #18, !alias.scope !64, !noalias !67
  br label %567

567:                                              ; preds = %541, %504
  ret void
}

; Function Attrs: mustprogress nounwind willreturn memory(argmem: readwrite)
declare void @air.write_texture_2d.i16.v4f16(ptr addrspace(1) captures(none), <2 x i16>, <4 x half>, i16, i32) local_unnamed_addr #3

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.convert.f.f32.u.i32(i32) local_unnamed_addr #0

; Function Attrs: convergent mustprogress nounwind willreturn
declare void @air.wg.barrier(i32, i32, i32) local_unnamed_addr #4

; Function Attrs: mustprogress nounwind willreturn
declare i32 @air.atomic.local.min.u.i32(ptr addrspace(3) captures(none), i32, i32, i32, i32, i1) local_unnamed_addr #5

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i16 @air.convert.u.i16.f.f32(float) local_unnamed_addr #0

; Function Attrs: convergent
declare void @air.atomic.fence(i32 noundef, i32 noundef, i32 noundef) local_unnamed_addr #6

; Function Attrs: convergent mustprogress nounwind willreturn
declare i32 @air.simd_prefix_inclusive_sum.u.i32(i32) local_unnamed_addr #4

; Function Attrs: mustprogress nounwind willreturn
declare i32 @air.atomic.local.add.u.i32(ptr addrspace(3) captures(none), i32, i32, i32, i32, i1) local_unnamed_addr #5

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x i16> @air.convert.u.v3i16.f.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.saturate.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i32 @air.clamp.s.i32(i32, i32, i32) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i32 @air.convert.s.i32.f.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.round.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.dot.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.mix.v3f16(<3 x half>, <3 x half>, <3 x half>) local_unnamed_addr #0

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(argmem: read)
declare { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none), ptr addrspace(2) readonly captures(none), <2 x float>, i1, <2 x i32>, i1, float, float, i32) local_unnamed_addr #7

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.fmin.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.convert.f.f16.u.i32(i32) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i32 @air.get_width_texture_2d(ptr addrspace(1) readonly captures(none), i32) local_unnamed_addr #8

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i16 @air.convert.u.i16.f.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.convert.f.f16.u.i1(i1) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.pow.f16(half, half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmax.f16(half, half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_pow.f32(float, float) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.log2.f16(half) local_unnamed_addr #0

; Function Attrs: inlinehint mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_(<3 x half> noundef %0, i32 noundef %1) unnamed_addr #9 {
  switch i32 %1, label %75 [
    i32 0, label %3
    i32 1, label %3
    i32 2, label %4
    i32 3, label %9
    i32 4, label %19
    i32 5, label %29
    i32 6, label %39
    i32 7, label %52
    i32 8, label %66
  ]

3:                                                ; preds = %2, %2
  br label %75

4:                                                ; preds = %2
  %5 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #11
  %6 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #11
  %7 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %6, <3 x half> splat (half 1.000000e+00)) #11
  %8 = fmul fast <3 x half> %7, %5
  br label %75

9:                                                ; preds = %2
  %10 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #11
  %11 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #11
  %12 = fmul fast <3 x half> %11, splat (half 7.739250e-02)
  %13 = fadd fast <3 x half> %11, splat (half 5.499270e-02)
  %14 = fmul fast <3 x half> %13, splat (half 9.482420e-01)
  %15 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %14, <3 x half> splat (half 2.400390e+00)) #11
  %16 = fcmp fast ogt <3 x half> %11, splat (half 4.043580e-02)
  %17 = select fast <3 x i1> %16, <3 x half> %15, <3 x half> %12
  %18 = fmul fast <3 x half> %17, %10
  br label %75

19:                                               ; preds = %2
  %20 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #11
  %21 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #11
  %22 = fmul fast <3 x half> %21, splat (half 2.221680e-01)
  %23 = fadd fast <3 x half> %21, splat (half 9.899900e-02)
  %24 = fmul fast <3 x half> %23, splat (half 9.101560e-01)
  %25 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %24, <3 x half> splat (half 2.222660e+00)) #11
  %26 = fcmp fast ogt <3 x half> %21, splat (half 8.105460e-02)
  %27 = select fast <3 x i1> %26, <3 x half> %25, <3 x half> %22
  %28 = fmul fast <3 x half> %27, %20
  br label %75

29:                                               ; preds = %2
  %30 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #11
  %31 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #11
  %32 = fmul fast <3 x half> %31, splat (half 2.221680e-01)
  %33 = fadd fast <3 x half> %31, splat (half 9.930410e-02)
  %34 = fmul fast <3 x half> %33, splat (half 9.091790e-01)
  %35 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %34, <3 x half> splat (half 2.222660e+00)) #11
  %36 = fcmp fast ogt <3 x half> %31, splat (half 8.123780e-02)
  %37 = select fast <3 x i1> %36, <3 x half> %35, <3 x half> %32
  %38 = fmul fast <3 x half> %37, %30
  br label %75

39:                                               ; preds = %2
  %40 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #11
  %41 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #11
  %42 = fmul fast <3 x half> %41, %41
  %43 = fmul fast <3 x half> %42, splat (half 3.332520e-01)
  %44 = fadd fast <3 x half> %41, splat (half -5.600590e-01)
  %45 = fmul fast <3 x half> %44, splat (half 5.593750e+00)
  %46 = tail call fast <3 x half> @air.exp.v3f16(<3 x half> %45) #11
  %47 = fadd fast <3 x half> %46, splat (half 2.846680e-01)
  %48 = fmul fast <3 x half> %47, splat (half 8.331300e-02)
  %49 = fcmp fast ogt <3 x half> %41, splat (half 5.000000e-01)
  %50 = select fast <3 x i1> %49, <3 x half> %48, <3 x half> %43
  %51 = fmul fast <3 x half> %50, %40
  br label %75

52:                                               ; preds = %2
  %53 = fadd fast <3 x half> %0, splat (half -6.933590e-01)
  %54 = fmul fast <3 x half> %53, splat (half 1.169530e+01)
  %55 = tail call fast <3 x half> @air.powr.v3f16(<3 x half> splat (half 2.000000e+00), <3 x half> %54) #11
  %56 = fadd fast <3 x half> %55, splat (half -9.643550e-03)
  %57 = fcmp fast oge <3 x half> %0, splat (half 2.084960e-01)
  %58 = select fast <3 x i1> %57, <3 x half> %56, <3 x half> splat (half -5.639650e-02)
  %59 = fmul fast <3 x half> %0, splat (half 2.114870e-02)
  %60 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %59) #11
  %61 = fadd fast <3 x half> %60, splat (half -5.639650e-02)
  %62 = fcmp fast oge <3 x half> %0, zeroinitializer
  %63 = fcmp fast olt <3 x half> %0, splat (half 2.084960e-01)
  %64 = and <3 x i1> %62, %63
  %65 = select fast <3 x i1> %64, <3 x half> %61, <3 x half> %58
  br label %75

66:                                               ; preds = %2
  %67 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #11
  %68 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #11
  %69 = fadd fast <3 x half> %68, splat (half 6.250000e-01)
  %70 = fdiv fast <3 x half> %69, zeroinitializer
  %71 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %70, <3 x half> splat (half 1.799800e+00)) #11
  %72 = fcmp fast ogt <3 x half> %68, splat (half 1.953130e-03)
  %73 = select fast <3 x i1> %72, <3 x half> %71, <3 x half> %68
  %74 = fmul fast <3 x half> %73, %67
  br label %75

75:                                               ; preds = %66, %52, %39, %29, %19, %9, %4, %3, %2
  %76 = phi <3 x half> [ zeroinitializer, %2 ], [ %74, %66 ], [ %65, %52 ], [ %51, %39 ], [ %38, %29 ], [ %28, %19 ], [ %18, %9 ], [ %8, %4 ], [ %0, %3 ]
  ret <3 x half> %76
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.pow.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.fabs.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.sign.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.sqrt.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.powr.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.exp.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z16applySemanticSRLDv3_DhfDh(<3 x half> noundef %0, float noundef %1, half noundef %2) unnamed_addr #10 {
  %4 = fcmp fast olt float %1, 1.000000e+00
  br i1 %4, label %5, label %34

5:                                                ; preds = %3
  %6 = fcmp fast ogt float %1, 0.000000e+00
  br i1 %6, label %7, label %80

7:                                                ; preds = %5
  %8 = extractelement <3 x half> %0, i64 0
  %9 = fmul fast half %8, 2.990720e-01
  %10 = extractelement <3 x half> %0, i64 1
  %11 = fmul fast half %10, 5.869140e-01
  %12 = fadd fast half %9, %11
  %13 = extractelement <3 x half> %0, i64 2
  %14 = fmul fast half %13, 1.140140e-01
  %15 = fadd fast half %12, %14
  %16 = tail call fast half @air.fabs.f16(half %15) #11
  %17 = fcmp fast ult half %16, 1.531840e-05
  br i1 %17, label %80, label %18

18:                                               ; preds = %7
  %19 = fpext half %15 to float
  %20 = fmul fast float %19, %1
  %21 = fsub fast float 1.000000e+00, %1
  %22 = fsub fast half 1.000000e+00, %15
  %23 = fpext half %22 to float
  %24 = fmul fast float %21, %23
  %25 = fdiv fast float %20, %24
  %26 = fadd fast float %25, 1.000000e+00
  %27 = fdiv fast float 1.000000e+00, %26
  %28 = fsub fast float 1.000000e+00, %27
  %29 = fdiv fast float %28, %19
  %30 = fptrunc float %29 to half
  %31 = insertelement <3 x half> poison, half %30, i64 0
  %32 = shufflevector <3 x half> %31, <3 x half> poison, <3 x i32> zeroinitializer
  %33 = fmul fast <3 x half> %32, %0
  br label %80

34:                                               ; preds = %3
  %35 = fcmp fast olt float %1, 2.000000e+00
  br i1 %35, label %36, label %38

36:                                               ; preds = %34
  %37 = fadd fast float %1, -1.000000e+00
  br label %45

38:                                               ; preds = %34
  %39 = fcmp fast olt float %1, 3.000000e+00
  br i1 %39, label %40, label %45

40:                                               ; preds = %38
  %41 = fadd fast float %1, -2.500000e+00
  %42 = fmul fast float %41, 5.000000e-01
  %43 = fadd fast float %42, 5.000000e-01
  %44 = fadd fast float %1, -2.000000e+00
  br label %45

45:                                               ; preds = %40, %38, %36
  %46 = phi float [ %37, %36 ], [ %44, %40 ], [ -1.000000e+00, %38 ]
  %47 = phi float [ 5.000000e-01, %36 ], [ %43, %40 ], [ -1.000000e+00, %38 ]
  %48 = fpext half %2 to float
  %49 = tail call fast float @air.mix.f32(float %47, float %46, float %48) #11
  %50 = fcmp fast ogt float %49, 0.000000e+00
  %51 = fcmp fast olt float %49, 1.000000e+00
  %52 = select i1 %50, i1 %51, i1 false
  br i1 %52, label %53, label %80

53:                                               ; preds = %45
  %54 = extractelement <3 x half> %0, i64 0
  %55 = fmul fast half %54, 2.990720e-01
  %56 = extractelement <3 x half> %0, i64 1
  %57 = fmul fast half %56, 5.869140e-01
  %58 = fadd fast half %55, %57
  %59 = extractelement <3 x half> %0, i64 2
  %60 = fmul fast half %59, 1.140140e-01
  %61 = fadd fast half %58, %60
  %62 = tail call fast half @air.fabs.f16(half %61) #11
  %63 = fcmp fast ult half %62, 1.531840e-05
  br i1 %63, label %80, label %64

64:                                               ; preds = %53
  %65 = fpext half %61 to float
  %66 = fmul fast float %49, %65
  %67 = fsub fast float 1.000000e+00, %49
  %68 = fsub fast half 1.000000e+00, %61
  %69 = fpext half %68 to float
  %70 = fmul fast float %67, %69
  %71 = fdiv fast float %66, %70
  %72 = fadd fast float %71, 1.000000e+00
  %73 = fdiv fast float 1.000000e+00, %72
  %74 = fsub fast float 1.000000e+00, %73
  %75 = fdiv fast float %74, %65
  %76 = fptrunc float %75 to half
  %77 = insertelement <3 x half> poison, half %76, i64 0
  %78 = shufflevector <3 x half> %77, <3 x half> poison, <3 x i32> zeroinitializer
  %79 = fmul fast <3 x half> %78, %0
  br label %80

80:                                               ; preds = %64, %53, %45, %18, %7, %5
  %81 = phi <3 x half> [ %0, %5 ], [ %33, %18 ], [ %0, %7 ], [ %0, %45 ], [ %79, %64 ], [ %0, %53 ]
  ret <3 x half> %81
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fabs.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.mix.f32(float, float, float) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <2 x float> @air.convert.f.v2f32.u.v2i16(<2 x i16>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i32 @air.get_height_texture_2d(ptr addrspace(1) readonly captures(none), i32) local_unnamed_addr #8

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i32 @air.convert.u.i32.f.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.ceil.f16(half) local_unnamed_addr #0

attributes #0 = { mustprogress nofree nosync nounwind willreturn memory(none) }
attributes #1 = { mustprogress nofree nosync nounwind willreturn "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="0" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #2 = { convergent nounwind "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="64" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #3 = { mustprogress nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { convergent mustprogress nounwind willreturn }
attributes #5 = { mustprogress nounwind willreturn }
attributes #6 = { convergent "approx-func-fp-math"="true" "frame-pointer"="all" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #7 = { convergent mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #8 = { mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #9 = { inlinehint mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="48" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #10 = { mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="48" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #11 = { nounwind willreturn memory(none) }
attributes #12 = { convergent nounwind willreturn }
attributes #13 = { nounwind willreturn memory(argmem: read) }
attributes #14 = { convergent nounwind willreturn memory(argmem: read) }
attributes #15 = { nobuiltin "no-builtins" }
attributes #16 = { nounwind willreturn }
attributes #17 = { convergent nobuiltin nounwind "no-builtins" }
attributes #18 = { nounwind willreturn memory(argmem: readwrite) }

!llvm.module.flags = !{!0, !1, !2, !3, !4, !5, !6, !7, !8}
!llvm.ident = !{!9}
!air.version = !{!10}
!air.language_version = !{!11}
!air.compile_options = !{!12, !13, !14}
!air.kernel = !{!15}
!air.function_constants = !{!55}
!air.sampler_states = !{!56, !57}

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
!15 = !{ptr @calculateLocalHistogramStats_all, !16, !17}
!16 = !{}
!17 = !{!18, !19, !21, !22, !23, !24, !25, !26, !27, !30, !39, !43, !46, !48, !49, !50, !51, !52, !53, !54}
!18 = !{i32 0, !"air.texture", !"air.location_index", i32 0, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputImageTexture"}
!19 = !{i32 1, !"air.function_constant", !20, !"air.buffer", !"air.buffer_size", i32 4, !"air.location_index", i32 8, i32 1, !"air.read", !"air.address_space", i32 2, !"air.arg_type_size", i32 4, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"float", !"air.arg_name", !"srlPlaybackCurve"}
!20 = !{ptr addrspace(2) @__metal_implicit_fc_pred_0.41, !"bool", !"useSrlBeforeStats"}
!21 = !{i32 2, !"air.texture", !"air.location_index", i32 1, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputLinearImageTexture"}
!22 = !{i32 3, !"air.texture", !"air.location_index", i32 10, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"fgbgMatteTexture"}
!23 = !{i32 4, !"air.texture", !"air.location_index", i32 11, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"skinMatteTexture"}
!24 = !{i32 5, !"air.texture", !"air.location_index", i32 17, i32 1, !"air.write", !"air.arg_type_name", !"texture2d<half, write>", !"air.arg_name", !"lightMapTexture"}
!25 = !{i32 6, !"air.texture", !"air.location_index", i32 18, i32 1, !"air.write", !"air.arg_type_name", !"texture2d<half, write>", !"air.arg_name", !"linearLightMapTexture"}
!26 = !{i32 7, !"air.texture", !"air.location_index", i32 2, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputGlobalToneCurveTex"}
!27 = !{i32 8, !"air.buffer", !"air.buffer_size", i32 320, !"air.location_index", i32 0, i32 1, !"air.read", !"air.address_space", i32 2, !"air.struct_type_info", !28, !"air.arg_type_size", i32 320, !"air.arg_type_align_size", i32 16, !"air.arg_type_name", !"SSRColorManagement", !"air.arg_name", !"colorManagement"}
!28 = !{!"air.struct_type_info", !29, i32 0, i32 80, i32 0, !"SSRColorConversion", !"inputImage", !"air.struct_type_info", !29, i32 80, i32 80, i32 0, !"SSRColorConversion", !"inputLinearImage", !"air.struct_type_info", !29, i32 160, i32 80, i32 0, !"SSRColorConversion", !"inputMasks", !"air.struct_type_info", !29, i32 240, i32 80, i32 0, !"SSRColorConversion", !"outputImage"}
!29 = !{i32 0, i32 4, i32 0, !"uint", !"transferFunction", i32 16, i32 48, i32 0, !"float3x3", !"colorConversionMatrix", i32 64, i32 1, i32 0, !"bool", !"useVELuma"}
!30 = !{i32 9, !"air.buffer", !"air.buffer_size", i32 672, !"air.location_index", i32 1, i32 1, !"air.read", !"air.address_space", i32 2, !"air.struct_type_info", !31, !"air.arg_type_size", i32 672, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"SSRParams", !"air.arg_name", !"params"}
!31 = !{i32 0, i32 4, i32 0, !"uint", !"castType", i32 4, i32 4, i32 0, !"float", !"castIntensity", i32 8, i32 4, i32 0, !"float", !"toneBias", i32 12, i32 4, i32 0, !"float", !"colorBias", i32 16, i32 4, i32 0, !"float", !"fgCastIntensity", i32 20, i32 4, i32 0, !"float", !"bgCastIntensity", i32 24, i32 4, i32 0, !"float", !"linearBaseGain", i32 28, i32 4, i32 0, !"float", !"baselineExposure", i32 32, i32 4, i32 0, !"uint", !"sceneType", !"air.struct_type_info", !32, i32 36, i32 136, i32 0, !"SSRCastAdjustments", !"castAdj", !"air.struct_type_info", !33, i32 172, i32 264, i32 0, !"SSRToneAdjustments", !"toneAdj", !"air.struct_type_info", !34, i32 436, i32 16, i32 0, !"SSRColorAdjustments", !"colorAdj", !"air.struct_type_info", !35, i32 452, i32 36, i32 0, !"SSRHazeAdjustments", !"hazeAdj", !"air.struct_type_info", !36, i32 488, i32 68, i32 0, !"SSRBGAdjustment", !"bgAdj", !"air.struct_type_info", !37, i32 556, i32 64, i32 0, !"SSRFGAdjustment", !"fgAdj", !"air.struct_type_info", !38, i32 620, i32 28, i32 0, !"SSRSemanticToneAdjustment", !"semanticToneAdj", i32 648, i32 4, i32 0, !"float", !"brightnessValue", i32 652, i32 4, i32 0, !"uint", !"tuningType", i32 656, i32 4, i32 0, !"float", !"peopleThresholdLo", i32 660, i32 4, i32 0, !"float", !"peopleThresholdHi", i32 664, i32 4, i32 0, !"float", !"faceBasedGlobalExposureBoostRatio", i32 668, i32 4, i32 0, !"float", !"personMasksValidHint"}
!32 = !{i32 0, i32 4, i32 0, !"float", !"bgWarmth", i32 4, i32 4, i32 0, !"float", !"fgWarmth", i32 8, i32 4, i32 0, !"float", !"bgRotate", i32 12, i32 4, i32 0, !"float", !"fgRotate", i32 16, i32 4, i32 0, !"float", !"personWarmth", i32 20, i32 4, i32 0, !"float", !"personRotate", i32 24, i32 4, i32 3, !"float", !"hue", i32 36, i32 4, i32 3, !"float", !"range", i32 48, i32 4, i32 3, !"float", !"strength", i32 60, i32 4, i32 0, !"float", !"shadow", i32 64, i32 4, i32 0, !"float", !"mids", i32 68, i32 4, i32 0, !"float", !"high", i32 72, i32 4, i32 3, !"float", !"shadowRGB", i32 84, i32 4, i32 3, !"float", !"midsRGB", i32 96, i32 4, i32 3, !"float", !"highRGB", i32 108, i32 4, i32 0, !"float", !"deRed", i32 112, i32 4, i32 0, !"float", !"deRedSatReduction", i32 116, i32 4, i32 0, !"float", !"deYellow", i32 120, i32 4, i32 0, !"float", !"skinWarmth", i32 124, i32 4, i32 0, !"float", !"skinProtectStrength", i32 128, i32 4, i32 0, !"float", !"skinProtectRange", i32 132, i32 4, i32 0, !"float", !"skinRatioThreshold"}
!33 = !{i32 0, i32 4, i32 0, !"float", !"toneMinusMids", i32 4, i32 4, i32 0, !"float", !"toneMinusExposure", i32 8, i32 4, i32 0, !"float", !"toneMinusPersonExposure", i32 12, i32 4, i32 0, !"float", !"toneMinusFGScale", i32 16, i32 4, i32 0, !"float", !"toneMinusPersonSatScale", i32 20, i32 4, i32 0, !"float", !"toneMinusPersonContrastMax", i32 24, i32 4, i32 0, !"float", !"toneMinusPersonContrastScale", i32 28, i32 4, i32 0, !"float", !"toneMinusBGContrastScale", i32 32, i32 4, i32 0, !"float", !"toneMinusBGContrastMax", i32 36, i32 4, i32 0, !"float", !"toneMinusLTMRatio", i32 40, i32 4, i32 0, !"float", !"toneMinusPersonSmartContrastScale", i32 44, i32 4, i32 0, !"float", !"tonePlusPersonSatScale", i32 48, i32 4, i32 0, !"float", !"tonePlusFGScale", i32 52, i32 4, i32 0, !"float", !"tonePlusExposure", i32 56, i32 4, i32 0, !"float", !"tonePlusBGContrast", i32 60, i32 4, i32 0, !"float", !"colorCubeToneBiasMinGamma", i32 64, i32 4, i32 0, !"float", !"colorCubeToneBiasMaxGamma", i32 68, i32 4, i32 0, !"float", !"starkBWBackgroundRed", i32 72, i32 4, i32 0, !"float", !"starkBWBackgroundGreen", i32 76, i32 4, i32 0, !"float", !"starkBWBackgroundBlue", i32 80, i32 4, i32 0, !"float", !"starkBWWhitesMax", i32 84, i32 4, i32 0, !"float", !"defaultContrastBump", i32 88, i32 4, i32 0, !"float", !"defaultSatBump", i32 92, i32 4, i32 0, !"float", !"defaultMidsBump", i32 96, i32 4, i32 0, !"float", !"defaultLightenBump", i32 100, i32 4, i32 0, !"float", !"dfContrastBump", i32 104, i32 4, i32 0, !"float", !"dfSatBump", i32 108, i32 4, i32 0, !"float", !"dfMidsBump", i32 112, i32 4, i32 0, !"float", !"dfLightenBump", i32 116, i32 4, i32 0, !"float", !"dfLowLightStarts", i32 120, i32 4, i32 0, !"float", !"dfLowLightMax", i32 124, i32 4, i32 0, !"float", !"dfLowLightContrastBump", i32 128, i32 4, i32 0, !"float", !"dfLowLightSatBump", i32 132, i32 4, i32 0, !"float", !"dfLowLightMidsBump", i32 136, i32 4, i32 0, !"float", !"dfLowLightLightenBump", i32 140, i32 4, i32 0, !"float", !"ubContrastBump", i32 144, i32 4, i32 0, !"float", !"ubSatBump", i32 148, i32 4, i32 0, !"float", !"ubMidsBump", i32 152, i32 4, i32 0, !"float", !"ubLightenBump", i32 156, i32 4, i32 0, !"float", !"digitalFlashContrastBump", i32 160, i32 4, i32 0, !"float", !"digitalFlashSatBump", i32 164, i32 4, i32 0, !"float", !"digitalFlashMidsBump", i32 168, i32 4, i32 0, !"float", !"digitalFlashLightenBump", i32 172, i32 4, i32 0, !"float", !"swfrContrastBump", i32 176, i32 4, i32 0, !"float", !"swfrSatBump", i32 180, i32 4, i32 0, !"float", !"swfrMidsBump", i32 184, i32 4, i32 0, !"float", !"swfrLightenBump", i32 188, i32 4, i32 0, !"float", !"wysContrastBump", i32 192, i32 4, i32 0, !"float", !"wysSatBump", i32 196, i32 4, i32 0, !"float", !"wysMidsBump", i32 200, i32 4, i32 0, !"float", !"wysLightenBump", i32 204, i32 4, i32 0, !"float", !"sfdContrastBump", i32 208, i32 4, i32 0, !"float", !"sfdSatBump", i32 212, i32 4, i32 0, !"float", !"sfdMidsBump", i32 216, i32 4, i32 0, !"float", !"sfdLightenBump", i32 220, i32 4, i32 0, !"float", !"videoContrastBump", i32 224, i32 4, i32 0, !"float", !"videoSatBump", i32 228, i32 4, i32 0, !"float", !"videoMidsBump", i32 232, i32 4, i32 0, !"float", !"videoLightenBump", i32 236, i32 4, i32 0, !"float", !"foodToneScale", i32 240, i32 4, i32 0, !"float", !"foodColorScale", i32 244, i32 4, i32 0, !"float", !"foodIntensityScale", i32 248, i32 4, i32 0, !"float", !"sunsetToneScale", i32 252, i32 4, i32 0, !"float", !"sunsetColorScale", i32 256, i32 4, i32 0, !"float", !"sunsetIntensityScale", i32 260, i32 4, i32 0, !"float", !"longGrayLiftMix"}
!34 = !{i32 0, i32 4, i32 0, !"float", !"bwBackgroundHue", i32 4, i32 4, i32 0, !"float", !"bwForegroundHue", i32 8, i32 4, i32 0, !"float", !"colorBoostScale", i32 12, i32 4, i32 0, !"float", !"shadMidHighPersonMix"}
!35 = !{i32 0, i32 1, i32 0, !"bool", !"doHazeTuning", i32 4, i32 4, i32 0, !"float", !"liftStrength", i32 8, i32 4, i32 0, !"float", !"bgLift", i32 12, i32 4, i32 0, !"float", !"personLift", i32 16, i32 4, i32 0, !"float", !"bgMids", i32 20, i32 4, i32 0, !"float", !"personMids", i32 24, i32 4, i32 0, !"float", !"satMix", i32 28, i32 4, i32 0, !"float", !"contrast", i32 32, i32 4, i32 0, !"float", !"localContrast"}
!36 = !{i32 0, i32 4, i32 0, !"float", !"whites", i32 4, i32 4, i32 0, !"float", !"contrast", i32 8, i32 4, i32 0, !"float", !"richSat", i32 12, i32 4, i32 0, !"float", !"shadows", i32 16, i32 4, i32 0, !"float", !"gammaContrast", i32 20, i32 4, i32 0, !"float", !"localContrast", i32 24, i32 4, i32 0, !"float", !"airy", i32 28, i32 4, i32 0, !"float", !"mids", i32 32, i32 4, i32 0, !"float", !"sat", i32 36, i32 4, i32 0, !"float", !"lighten", i32 40, i32 4, i32 0, !"float", !"underGrass", i32 44, i32 4, i32 0, !"float", !"airyGamma", i32 48, i32 4, i32 0, !"float", !"warmthMatchI", i32 52, i32 4, i32 0, !"float", !"warmthMatchQ", i32 56, i32 4, i32 0, !"float", !"warmthMatchSkyI", i32 60, i32 4, i32 0, !"float", !"warmthMatchSkyQ", i32 64, i32 4, i32 0, !"float", !"bgGlobalMix"}
!37 = !{i32 0, i32 4, i32 0, !"float", !"personMix", i32 4, i32 4, i32 0, !"float", !"airy", i32 8, i32 4, i32 0, !"float", !"mids", i32 12, i32 4, i32 0, !"float", !"lighten", i32 16, i32 4, i32 0, !"float", !"whites", i32 20, i32 4, i32 0, !"float", !"airyGamma", i32 24, i32 4, i32 0, !"float", !"shadows", i32 28, i32 4, i32 0, !"float", !"contrast", i32 32, i32 4, i32 0, !"float", !"smartContrast", i32 36, i32 4, i32 0, !"float", !"skinHighLights", i32 40, i32 4, i32 0, !"float", !"skinLocalContrast", i32 44, i32 4, i32 0, !"float", !"saturation", i32 48, i32 4, i32 0, !"float", !"faceI", i32 52, i32 4, i32 0, !"float", !"faceQ", i32 56, i32 4, i32 0, !"float", !"underTone", i32 60, i32 4, i32 0, !"float", !"neckShade"}
!38 = !{i32 0, i32 4, i32 0, !"float", !"bgLTM", i32 4, i32 4, i32 0, !"float", !"fgLTM", i32 8, i32 4, i32 0, !"float", !"bgExposureGain", i32 12, i32 4, i32 0, !"float", !"fgExposureGain", i32 16, i32 4, i32 0, !"float", !"GTC", i32 20, i32 4, i32 0, !"float", !"HR", i32 24, i32 4, i32 0, !"float", !"personHR"}
!39 = !{i32 10, !"air.buffer", !"air.buffer_size", i32 10640, !"air.location_index", i32 3, i32 1, !"air.read", !"air.address_space", i32 1, !"air.struct_type_info", !40, !"air.arg_type_size", i32 10640, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"SSRStats", !"air.arg_name", !"stats"}
!40 = !{i32 0, i32 4, i32 2560, !"uint", !"globalHistogram", !"air.struct_type_info", !41, i32 10240, i32 36, i32 10, !"SSRGlobalStats", !"globalStats", i32 10600, i32 4, i32 0, !"uint", !"globalPersonCount", i32 10604, i32 4, i32 0, !"uint", !"globalSkinCount", i32 10608, i32 4, i32 0, !"float", !"peopleRatio", i32 10612, i32 4, i32 0, !"float", !"skinRatio", !"air.struct_type_info", !42, i32 10616, i32 12, i32 0, !"SSRBasicStats", !"linBasicStats", !"air.struct_type_info", !42, i32 10628, i32 12, i32 0, !"SSRBasicStats", !"ltmBasicStats"}
!41 = !{i32 0, i32 4, i32 0, !"float", !"highKey", i32 4, i32 4, i32 0, !"float", !"p02", i32 8, i32 4, i32 0, !"float", !"p10", i32 12, i32 4, i32 0, !"float", !"p25", i32 16, i32 4, i32 0, !"float", !"p50", i32 20, i32 4, i32 0, !"float", !"p75", i32 24, i32 4, i32 0, !"float", !"p98", i32 28, i32 4, i32 0, !"float", !"blackPoint", i32 32, i32 4, i32 0, !"float", !"whitePoint"}
!42 = !{i32 0, i32 4, i32 0, !"float", !"min", i32 4, i32 4, i32 0, !"float", !"max", i32 8, i32 4, i32 0, !"float", !"avg"}
!43 = !{i32 11, !"air.buffer", !"air.buffer_size", i32 10575872, !"air.location_index", i32 4, i32 1, !"air.read_write", !"air.address_space", i32 1, !"air.struct_type_info", !44, !"air.arg_type_size", i32 10575872, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"SSRIntermediateStats", !"air.arg_name", !"intermediateStats"}
!44 = !{i32 0, i32 4, i32 2621440, !"uint", !"localHistogram", !"air.struct_type_info", !45, i32 10485760, i32 8, i32 10240, !"SSRLocalStats", !"localStats", i32 10567680, i32 4, i32 1024, !"uint", !"localPersonCount", i32 10571776, i32 4, i32 1024, !"uint", !"localSkinCount"}
!45 = !{i32 0, i32 4, i32 0, !"float", !"p50", i32 4, i32 4, i32 0, !"float", !"p98"}
!46 = !{i32 12, !"air.buffer", !"air.buffer_size", i32 176, !"air.location_index", i32 5, i32 1, !"air.read", !"air.address_space", i32 2, !"air.struct_type_info", !47, !"air.arg_type_size", i32 176, !"air.arg_type_align_size", i32 16, !"air.arg_type_name", !"SSRRenderROI", !"air.arg_name", !"roi"}
!47 = !{i32 0, i32 4, i32 0, !"ushort2", !"logicalImageSize", i32 4, i32 4, i32 0, !"ushort2", !"renderRegionSize", i32 8, i32 4, i32 0, !"ushort2", !"renderEdge", i32 16, i32 16, i32 0, !"float4", !"logicalImageToInputImageGridScaleAndOffset", i32 32, i32 16, i32 0, !"float4", !"logicalImageToInputLinearImageGridScaleAndOffset", i32 48, i32 16, i32 0, !"float4", !"logicalImageToBgLTMGainMapGridScaleAndOffset", i32 64, i32 16, i32 0, !"float4", !"logicalImageToFgLTMGainMapGridScaleAndOffset", i32 80, i32 16, i32 0, !"float4", !"logicalImageToInputLightMapGridScaleAndOffset", i32 96, i32 16, i32 0, !"float4", !"logicalImageToInputLinearLightMapGridScaleAndOffset", i32 112, i32 16, i32 0, !"float4", !"logicalImageToInputPersonMaskGridScaleAndOffset", i32 128, i32 16, i32 0, !"float4", !"logicalImageToInputSkinMaskGridScaleAndOffset", i32 144, i32 16, i32 0, !"float4", !"logicalImageToInputSkyMaskGridScaleAndOffset", i32 160, i32 4, i32 0, !"ushort2", !"outputImageGridOffset"}
!48 = !{i32 13, !"air.simdgroup_index_in_threadgroup", !"air.arg_type_name", !"ushort", !"air.arg_name", !"simd_group_id"}
!49 = !{i32 14, !"air.threads_per_simdgroup", !"air.arg_type_name", !"ushort", !"air.arg_name", !"simd_size"}
!50 = !{i32 15, !"air.thread_position_in_grid", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"threadPosInGrid", !"air.arg_unused"}
!51 = !{i32 16, !"air.thread_index_in_threadgroup", !"air.arg_type_name", !"ushort", !"air.arg_name", !"threadIdxInGroup"}
!52 = !{i32 17, !"air.thread_position_in_threadgroup", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"threadPosInGroup"}
!53 = !{i32 18, !"air.threads_per_threadgroup", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"threadsPerGroup"}
!54 = !{i32 19, !"air.threadgroup_position_in_grid", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"groupPosInGrid"}
!55 = !{ptr addrspace(2) @_Z17useSrlBeforeStats.MTL_FC_INIT_2_b, !"bool", !"useSrlBeforeStats", i32 2, i1 true}
!56 = !{!"air.sampler_state", ptr addrspace(2) @__air_sampler_state}
!57 = !{!"air.sampler_state", ptr addrspace(2) @__air_sampler_state.3}
!58 = !{!59, !59, i64 0}
!59 = !{!"bool", !60, i64 0}
!60 = !{!"omnipotent char", !61, i64 0}
!61 = !{!"Simple C++ TBAA"}
!62 = !{i8 0, i8 2}
!63 = !{!60, !60, i64 0}
!64 = !{!65}
!65 = distinct !{!65, !66, !"air-alias-scope-textures"}
!66 = distinct !{!66, !"air-alias-scopes(calculateLocalHistogramStats_all)"}
!67 = !{!68, !69, !70, !71, !72, !73}
!68 = distinct !{!68, !66, !"air-alias-scope-arg(1)"}
!69 = distinct !{!69, !66, !"air-alias-scope-arg(8)"}
!70 = distinct !{!70, !66, !"air-alias-scope-arg(9)"}
!71 = distinct !{!71, !66, !"air-alias-scope-arg(10)"}
!72 = distinct !{!72, !66, !"air-alias-scope-arg(11)"}
!73 = distinct !{!73, !66, !"air-alias-scope-arg(12)"}
!74 = !{!73}
!75 = !{!65, !68, !69, !70, !71, !72}
!76 = distinct !{!76, !77}
!77 = !{!"llvm.loop.mustprogress"}
!78 = distinct !{!78, !77}
!79 = !{!80, !80, i64 0}
!80 = !{!"float", !60, i64 0}
!81 = !{!68}
!82 = !{!65, !69, !70, !71, !72, !73}
!83 = !{!84, !86, i64 0}
!84 = !{!"_ZTS18SSRColorManagement", !85, i64 0, !85, i64 80, !85, i64 160, !85, i64 240}
!85 = !{!"_ZTS18SSRColorConversion", !86, i64 0, !87, i64 16, !59, i64 64}
!86 = !{!"_ZTS19CMITransferFunction", !60, i64 0}
!87 = !{!"_ZTSN5metal6matrixIfLi3ELi3EvEE", !60, i64 0}
!88 = !{!69}
!89 = !{!65, !68, !70, !71, !72, !73}
!90 = !{!84, !59, i64 64}
!91 = !{!92, !80, i64 24}
!92 = !{!"_ZTS9SSRParams", !93, i64 0, !80, i64 4, !80, i64 8, !80, i64 12, !80, i64 16, !80, i64 20, !80, i64 24, !80, i64 28, !94, i64 32, !95, i64 36, !96, i64 172, !97, i64 436, !98, i64 452, !99, i64 488, !100, i64 556, !101, i64 620, !80, i64 648, !102, i64 652, !80, i64 656, !80, i64 660, !80, i64 664, !80, i64 668}
!93 = !{!"_ZTS11SSRCastType", !60, i64 0}
!94 = !{!"_ZTS12SSRSceneType", !60, i64 0}
!95 = !{!"_ZTS18SSRCastAdjustments", !80, i64 0, !80, i64 4, !80, i64 8, !80, i64 12, !80, i64 16, !80, i64 20, !60, i64 24, !60, i64 36, !60, i64 48, !80, i64 60, !80, i64 64, !80, i64 68, !60, i64 72, !60, i64 84, !60, i64 96, !80, i64 108, !80, i64 112, !80, i64 116, !80, i64 120, !80, i64 124, !80, i64 128, !80, i64 132}
!96 = !{!"_ZTS18SSRToneAdjustments", !80, i64 0, !80, i64 4, !80, i64 8, !80, i64 12, !80, i64 16, !80, i64 20, !80, i64 24, !80, i64 28, !80, i64 32, !80, i64 36, !80, i64 40, !80, i64 44, !80, i64 48, !80, i64 52, !80, i64 56, !80, i64 60, !80, i64 64, !80, i64 68, !80, i64 72, !80, i64 76, !80, i64 80, !80, i64 84, !80, i64 88, !80, i64 92, !80, i64 96, !80, i64 100, !80, i64 104, !80, i64 108, !80, i64 112, !80, i64 116, !80, i64 120, !80, i64 124, !80, i64 128, !80, i64 132, !80, i64 136, !80, i64 140, !80, i64 144, !80, i64 148, !80, i64 152, !80, i64 156, !80, i64 160, !80, i64 164, !80, i64 168, !80, i64 172, !80, i64 176, !80, i64 180, !80, i64 184, !80, i64 188, !80, i64 192, !80, i64 196, !80, i64 200, !80, i64 204, !80, i64 208, !80, i64 212, !80, i64 216, !80, i64 220, !80, i64 224, !80, i64 228, !80, i64 232, !80, i64 236, !80, i64 240, !80, i64 244, !80, i64 248, !80, i64 252, !80, i64 256, !80, i64 260}
!97 = !{!"_ZTS19SSRColorAdjustments", !80, i64 0, !80, i64 4, !80, i64 8, !80, i64 12}
!98 = !{!"_ZTS18SSRHazeAdjustments", !59, i64 0, !80, i64 4, !80, i64 8, !80, i64 12, !80, i64 16, !80, i64 20, !80, i64 24, !80, i64 28, !80, i64 32}
!99 = !{!"_ZTS15SSRBGAdjustment", !80, i64 0, !80, i64 4, !80, i64 8, !80, i64 12, !80, i64 16, !80, i64 20, !80, i64 24, !80, i64 28, !80, i64 32, !80, i64 36, !80, i64 40, !80, i64 44, !80, i64 48, !80, i64 52, !80, i64 56, !80, i64 60, !80, i64 64}
!100 = !{!"_ZTS15SSRFGAdjustment", !80, i64 0, !80, i64 4, !80, i64 8, !80, i64 12, !80, i64 16, !80, i64 20, !80, i64 24, !80, i64 28, !80, i64 32, !80, i64 36, !80, i64 40, !80, i64 44, !80, i64 48, !80, i64 52, !80, i64 56, !80, i64 60}
!101 = !{!"_ZTS25SSRSemanticToneAdjustment", !80, i64 0, !80, i64 4, !80, i64 8, !80, i64 12, !80, i64 16, !80, i64 20, !80, i64 24}
!102 = !{!"_ZTS13SSRTuningType", !60, i64 0}
!103 = !{!70}
!104 = !{!65, !68, !69, !71, !72, !73}
!105 = !{!92, !80, i64 28}
!106 = !{!107, !80, i64 10632}
!107 = !{!"_ZTS8SSRStats", !60, i64 0, !60, i64 10240, !108, i64 10600, !108, i64 10604, !80, i64 10608, !80, i64 10612, !109, i64 10616, !109, i64 10628}
!108 = !{!"int", !60, i64 0}
!109 = !{!"_ZTS13SSRBasicStats", !80, i64 0, !80, i64 4, !80, i64 8}
!110 = !{!71}
!111 = !{!65, !68, !69, !70, !72, !73}
!112 = !{!107, !80, i64 10620}
!113 = distinct !{!113, !77}
!114 = !{!108, !108, i64 0}
!115 = !{!72}
!116 = !{!65, !68, !69, !70, !71, !73}
!117 = distinct !{!117, !77}
!118 = distinct !{!118, !77}
!119 = distinct !{!119, !77}
!120 = distinct !{!120, !77, !121}
!121 = !{!"llvm.loop.unroll.enable"}
!122 = distinct !{!122, !77}
!123 = distinct !{!123, !77, !121}
!124 = distinct !{!124, !77}
!125 = distinct !{!125, !77}
!126 = !{!127, !80, i64 0}
!127 = !{!"_ZTS13SSRLocalStats", !80, i64 0, !80, i64 4}
!128 = !{!127, !80, i64 4}
!129 = distinct !{!129, !77}
