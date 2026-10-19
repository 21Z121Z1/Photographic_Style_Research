source_filename = "renderFinalAdjustments"
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v24:32:32-v32:32:32-v48:64:64-v64:64:64-v96:128:128-v128:128:128-v192:256:256-v256:256:256-v512:512:512-v1024:1024:1024-n8:16:32"
target triple = "air64_v29-apple-macosx27.0.0"

%"struct.metal::_imageblock_base.189.2404" = type { ptr addrspace(4) }
%struct.SSRRenderROI.2420 = type { <2 x i16>, <2 x i16>, <2 x i16>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <2 x i16>, [12 x i8] }
%struct.SSRParams.2416 = type { i32, float, float, float, float, float, float, float, i32, %struct.SSRCastAdjustments.2409, %struct.SSRToneAdjustments.2410, %struct.SSRColorAdjustments.2411, %struct.SSRHazeAdjustments.2412, %struct.SSRBGAdjustment.2413, %struct.SSRFGAdjustment.2414, %struct.SSRSemanticToneAdjustment.2415, float, i32, float, float, float, float }
%struct.SSRCastAdjustments.2409 = type { float, float, float, float, float, float, [3 x float], [3 x float], [3 x float], float, float, float, [3 x float], [3 x float], [3 x float], float, float, float, float, float, float, float }
%struct.SSRToneAdjustments.2410 = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRColorAdjustments.2411 = type { float, float, float, float }
%struct.SSRHazeAdjustments.2412 = type { i8, float, float, float, float, float, float, float, float }
%struct.SSRBGAdjustment.2413 = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRFGAdjustment.2414 = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRSemanticToneAdjustment.2415 = type { float, float, float, float, float, float, float }
%struct.SSRColorManagement.192.2408 = type { %struct.SSRColorConversion.191.2407, %struct.SSRColorConversion.191.2407, %struct.SSRColorConversion.191.2407, %struct.SSRColorConversion.191.2407 }
%struct.SSRColorConversion.191.2407 = type <{ i32, [12 x i8], %"struct.metal::matrix.17.190.2406", i8, [15 x i8] }>
%"struct.metal::matrix.17.190.2406" = type { [3 x <3 x float>] }
%struct.SSRStats.2419 = type { [10 x [256 x i32]], [10 x %struct.SSRGlobalStats.2417], i32, i32, float, float, %struct.SSRBasicStats.2418, %struct.SSRBasicStats.2418 }
%struct.SSRGlobalStats.2417 = type { float, float, float, float, float, float, float, float, float }
%struct.SSRBasicStats.2418 = type { float, float, float }
%"struct.metal::matrix.194" = type { [3 x <3 x half>] }

@__metal_implicit_fc_pred_1.42 = internal addrspace(2) global i8 0, align 1
@__metal_implicit_fc_pred_2.43 = internal addrspace(2) global i8 0, align 1
@_ZL13useSrlVersion = internal unnamed_addr addrspace(2) global i32 undef, align 4
@_Z13useSrlVersion.MTL_FC_INIT_1_i = internal unnamed_addr addrspace(2) externally_initialized constant i32 undef, section "air.fc_initializer", align 4
@_ZL13useImageBlock = internal unnamed_addr addrspace(2) global i8 undef, align 1
@_Z13useImageBlock.MTL_FC_INIT_0_b = internal unnamed_addr addrspace(2) externally_initialized constant i8 undef, section "air.fc_initializer", align 1
@__air_sampler_state = internal addrspace(2) constant [2 x i64] [i64 34901797601053257, i64 0], align 8
@__air_sampler_state.3 = internal addrspace(2) constant [2 x i64] [i64 34901797601020489, i64 0], align 8
@llvm.global_ctors = appending global [1 x { i32, ptr, ptr }] [{ i32, ptr, ptr } { i32 65535, ptr @_GLOBAL__sub_I_CMISmartStyleMetalRendererV1.metal, ptr null }]
@llvm.compiler.used = appending global [2 x ptr] [ptr addrspacecast (ptr addrspace(2) @__metal_implicit_fc_pred_1.42 to ptr), ptr addrspacecast (ptr addrspace(2) @__metal_implicit_fc_pred_2.43 to ptr)], section "llvm.metadata"

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i8 @air.normalize_function_constant_predicate.i8(i8) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define internal void @_GLOBAL__sub_I_CMISmartStyleMetalRendererV1.metal() #1 section "air.static_init" {
  %1 = load i8, ptr addrspace(2) @_Z13useImageBlock.MTL_FC_INIT_0_b, align 1, !tbaa !63, !range !67
  store i8 %1, ptr addrspace(2) @_ZL13useImageBlock, align 1, !tbaa !63
  %2 = load i32, ptr addrspace(2) @_Z13useSrlVersion.MTL_FC_INIT_1_i, align 4, !tbaa !68
  store i32 %2, ptr addrspace(2) @_ZL13useSrlVersion, align 4, !tbaa !68
  %3 = icmp sgt i32 %2, 0
  %4 = zext i1 %3 to i8
  %5 = tail call i8 @air.normalize_function_constant_predicate.i8(i8 %1) #25
  store i8 %5, ptr addrspace(2) @__metal_implicit_fc_pred_1.42, align 1
  %6 = tail call i8 @air.normalize_function_constant_predicate.i8(i8 %4) #25
  store i8 %6, ptr addrspace(2) @__metal_implicit_fc_pred_2.43, align 1
  ret void
}

; Function Attrs: convergent mustprogress nounwind willreturn
define void @renderFinalAdjustments(%"struct.metal::_imageblock_base.189.2404" %0, ptr addrspace(1) %1, ptr addrspace(1) %2, ptr addrspace(1) %3, ptr addrspace(1) %4, ptr addrspace(1) readnone captures(none) %5, ptr addrspace(1) %6, ptr addrspace(1) %7, ptr addrspace(1) %8, ptr addrspace(1) %9, ptr addrspace(1) %10, ptr addrspace(1) %11, ptr addrspace(1) %12, ptr addrspace(1) %13, ptr addrspace(1) %14, ptr addrspace(1) readnone captures(none) %15, ptr addrspace(2) noundef readonly align 16 captures(none) dereferenceable(320) "air-buffer-no-alias" %16, ptr addrspace(1) noundef align 4 captures(none) dereferenceable(672) "air-buffer-no-alias" %17, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(10640) "air-buffer-no-alias" %18, ptr addrspace(2) noundef readonly align 16 captures(none) dereferenceable(176) "air-buffer-no-alias" %19, ptr addrspace(2) noundef readonly align 4 captures(none) dereferenceable(4) "air-buffer-no-alias" %20, <2 x i16> noundef %21, <2 x i16> noundef %22, <2 x i16> noundef %23) local_unnamed_addr #2 {
  %25 = getelementptr inbounds %struct.SSRRenderROI.2420, ptr addrspace(2) %19, i64 0, i32 12
  %26 = load <2 x i16>, ptr addrspace(2) %25, align 16, !tbaa !70, !alias.scope !71, !noalias !74
  %27 = add <2 x i16> %26, %21
  %28 = tail call fast <2 x float> @air.convert.f.v2f32.u.v2i16(<2 x i16> %21) #25
  %29 = fadd fast <2 x float> %28, splat (float 5.000000e-01)
  %30 = getelementptr inbounds %struct.SSRRenderROI.2420, ptr addrspace(2) %19, i64 0, i32 3
  %31 = load <4 x float>, ptr addrspace(2) %30, align 16, !alias.scope !71, !noalias !74
  %32 = shufflevector <4 x float> %31, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %33 = fmul fast <2 x float> %32, %29
  %34 = shufflevector <4 x float> %31, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %35 = fadd fast <2 x float> %33, %34
  %36 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %1, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %35, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %37 = extractvalue { <4 x half>, i8 } %36, 0
  %38 = shufflevector <4 x half> %37, <4 x half> poison, <3 x i32> <i32 0, i32 1, i32 2>
  %39 = getelementptr inbounds %struct.SSRRenderROI.2420, ptr addrspace(2) %19, i64 0, i32 10
  %40 = load <4 x float>, ptr addrspace(2) %39, align 16, !alias.scope !71, !noalias !74
  %41 = shufflevector <4 x float> %40, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %42 = fmul fast <2 x float> %41, %29
  %43 = shufflevector <4 x float> %40, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %44 = fadd fast <2 x float> %42, %43
  %45 = getelementptr inbounds %struct.SSRRenderROI.2420, ptr addrspace(2) %19, i64 0, i32 11
  %46 = load <4 x float>, ptr addrspace(2) %45, align 16, !alias.scope !71, !noalias !74
  %47 = shufflevector <4 x float> %46, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %48 = fmul fast <2 x float> %47, %29
  %49 = shufflevector <4 x float> %46, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %50 = fadd fast <2 x float> %48, %49
  %51 = tail call i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none) %10) #27, !alias.scope !80, !noalias !81
  br i1 %51, label %62, label %52

52:                                               ; preds = %24
  %53 = getelementptr inbounds %struct.SSRRenderROI.2420, ptr addrspace(2) %19, i64 0, i32 9
  %54 = load <4 x float>, ptr addrspace(2) %53, align 16, !alias.scope !71, !noalias !74
  %55 = shufflevector <4 x float> %54, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %56 = fmul fast <2 x float> %55, %29
  %57 = shufflevector <4 x float> %54, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %58 = fadd fast <2 x float> %56, %57
  %59 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %10, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %58, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %60 = extractvalue { <4 x half>, i8 } %59, 0
  %61 = extractelement <4 x half> %60, i64 0
  br label %62

62:                                               ; preds = %52, %24
  %63 = phi fast half [ %61, %52 ], [ 0xH0000, %24 ]
  %64 = tail call i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none) %11) #27, !alias.scope !80, !noalias !81
  br i1 %64, label %69, label %65

65:                                               ; preds = %62
  %66 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %11, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %44, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %67 = extractvalue { <4 x half>, i8 } %66, 0
  %68 = extractelement <4 x half> %67, i64 0
  br label %69

69:                                               ; preds = %65, %62
  %70 = phi fast half [ %68, %65 ], [ 0xH0000, %62 ]
  %71 = tail call i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none) %12) #27, !alias.scope !80, !noalias !81
  br i1 %71, label %76, label %72

72:                                               ; preds = %69
  %73 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %12, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %50, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %74 = extractvalue { <4 x half>, i8 } %73, 0
  %75 = extractelement <4 x half> %74, i64 0
  br label %76

76:                                               ; preds = %72, %69
  %77 = phi fast half [ %75, %72 ], [ 0xH0000, %69 ]
  %78 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 21
  %79 = load float, ptr addrspace(1) %78, align 4, !tbaa !82, !alias.scope !95, !noalias !96
  %80 = fcmp fast ult float %79, 0.000000e+00
  br i1 %80, label %94, label %81

81:                                               ; preds = %76
  %82 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 9, i32 21
  %83 = load float, ptr addrspace(1) %82, align 4, !tbaa !97, !alias.scope !95, !noalias !96
  %84 = fdiv fast float %79, %83
  %85 = tail call fast float @air.fast_clamp.f32(float %84, float 0.000000e+00, float 1.000000e+00) #25
  %86 = fmul fast float %85, %85
  %87 = fmul fast float %85, 2.000000e+00
  %88 = fsub fast float 3.000000e+00, %87
  %89 = fmul fast float %86, %88
  %90 = tail call fast float @air.fast_fmax.f32(float %89, float 0x3FD3333340000000) #25
  %91 = fptrunc float %90 to half
  %92 = fmul fast half %63, %91
  %93 = fmul fast half %70, %91
  br label %94

94:                                               ; preds = %81, %76
  %95 = phi half [ %93, %81 ], [ %70, %76 ]
  %96 = phi half [ %92, %81 ], [ %63, %76 ]
  %97 = load i32, ptr addrspace(2) @_ZL13useSrlVersion, align 4, !tbaa !68
  switch i32 %97, label %133 [
    i32 1, label %98
    i32 2, label %130
  ]

98:                                               ; preds = %94
  %99 = load float, ptr addrspace(2) %20, align 4, !tbaa !98, !alias.scope !99, !noalias !100
  %100 = fcmp fast ogt float %99, 0.000000e+00
  %101 = fcmp fast olt float %99, 1.000000e+00
  %102 = select i1 %100, i1 %101, i1 false
  br i1 %102, label %103, label %133

103:                                              ; preds = %98
  %104 = extractelement <4 x half> %37, i64 0
  %105 = fmul fast half %104, 0xH34C9
  %106 = extractelement <4 x half> %37, i64 1
  %107 = fmul fast half %106, 0xH38B2
  %108 = fadd fast half %105, %107
  %109 = extractelement <4 x half> %37, i64 2
  %110 = fmul fast half %109, 0xH2F4C
  %111 = fadd fast half %108, %110
  %112 = tail call fast half @air.fabs.f16(half %111) #25
  %113 = fcmp fast ult half %112, 0xH0101
  br i1 %113, label %133, label %114

114:                                              ; preds = %103
  %115 = fpext half %111 to float
  %116 = fmul fast float %99, %115
  %117 = fsub fast float 1.000000e+00, %99
  %118 = fsub fast half 0xH3C00, %111
  %119 = fpext half %118 to float
  %120 = fmul fast float %117, %119
  %121 = fdiv fast float %116, %120
  %122 = fadd fast float %121, 1.000000e+00
  %123 = fdiv fast float 1.000000e+00, %122
  %124 = fsub fast float 1.000000e+00, %123
  %125 = fdiv fast float %124, %115
  %126 = fptrunc float %125 to half
  %127 = insertelement <3 x half> poison, half %126, i64 0
  %128 = shufflevector <3 x half> %127, <3 x half> poison, <3 x i32> zeroinitializer
  %129 = fmul fast <3 x half> %128, %38
  br label %133

130:                                              ; preds = %94
  %131 = load float, ptr addrspace(2) %20, align 4, !tbaa !98, !alias.scope !99, !noalias !100
  %132 = tail call fast fastcc <3 x half> @_Z16applySemanticSRLDv3_DhfDh(<3 x half> noundef %38, float noundef %131, half noundef %96) #28
  br label %133

133:                                              ; preds = %130, %114, %103, %98, %94
  %134 = phi <3 x half> [ %38, %94 ], [ %132, %130 ], [ %38, %98 ], [ %129, %114 ], [ %38, %103 ]
  %135 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 0, i32 0
  %136 = load i32, ptr addrspace(2) %135, align 16, !tbaa !101, !alias.scope !106, !noalias !107
  %137 = tail call fastcc <3 x half> @_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_(<3 x half> noundef %134, i32 noundef %136) #28
  %138 = icmp eq i32 %136, 6
  br i1 %138, label %139, label %175

139:                                              ; preds = %133
  %140 = tail call fast half @air.log2.f16(half 0xH2E66) #25
  %141 = tail call fast half @air.pow.f16(half 0xH3C72, half %140) #25
  %142 = fpext half %141 to float
  %143 = fmul fast float %142, 0x3FF3333340000000
  %144 = fptrunc float %143 to half
  %145 = extractelement <3 x half> %137, i64 0
  %146 = fpext half %145 to float
  %147 = fmul fast float %146, 0x3FD0D013A0000000
  %148 = extractelement <3 x half> %137, i64 1
  %149 = fpext half %148 to float
  %150 = fmul fast float %149, 0x3FE5B22D00000000
  %151 = fadd fast float %147, %150
  %152 = extractelement <3 x half> %137, i64 2
  %153 = fpext half %152 to float
  %154 = fmul fast float %153, 0x3FAE5C91E0000000
  %155 = fadd fast float %151, %154
  %156 = fpext half %144 to float
  %157 = fadd fast float %156, -1.000000e+00
  %158 = tail call fast float @air.fast_pow.f32(float %155, float %157) #25
  %159 = fptrunc float %158 to half
  %160 = fmul fast half %145, 0xH32D1
  %161 = fmul fast half %148, 0xH39B8
  %162 = fadd fast half %160, %161
  %163 = fmul fast half %152, 0xH2C9C
  %164 = fadd fast half %162, %163
  %165 = tail call fast half @air.fmax.f16(half %145, half %148) #25
  %166 = tail call fast half @air.fmax.f16(half %165, half %152) #25
  %167 = fadd fast half %164, %166
  %168 = fmul fast half %167, 0xH3800
  %169 = fadd fast half %144, 0xHBC00
  %170 = tail call fast half @air.pow.f16(half %168, half %169) #25
  %171 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 0, i32 3
  %172 = load i8, ptr addrspace(2) %171, align 16, !tbaa !108, !range !67, !alias.scope !106, !noalias !107
  %173 = icmp eq i8 %172, 0
  %174 = select fast i1 %173, half %159, half %170
  br label %175

175:                                              ; preds = %139, %133
  %176 = phi half [ %174, %139 ], [ 0xH3C00, %133 ]
  %177 = insertelement <3 x half> poison, half %176, i64 0
  %178 = shufflevector <3 x half> %177, <3 x half> poison, <3 x i32> zeroinitializer
  %179 = fmul fast <3 x half> %178, %137
  %180 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 0, i32 2, i32 0, i64 0
  %181 = load <3 x float>, ptr addrspace(2) %180, align 16, !tbaa !98, !alias.scope !106, !noalias !107
  %182 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %181) #25
  %183 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 0, i32 2, i32 0, i64 1
  %184 = load <3 x float>, ptr addrspace(2) %183, align 16, !tbaa !98, !alias.scope !106, !noalias !107
  %185 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %184) #25
  %186 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 0, i32 2, i32 0, i64 2
  %187 = load <3 x float>, ptr addrspace(2) %186, align 16, !tbaa !98, !alias.scope !106, !noalias !107
  %188 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %187) #25
  %189 = shufflevector <3 x half> %179, <3 x half> poison, <3 x i32> zeroinitializer
  %190 = fmul fast <3 x half> %189, %182
  %191 = shufflevector <3 x half> %179, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %192 = fmul fast <3 x half> %185, %191
  %193 = fadd fast <3 x half> %190, %192
  %194 = shufflevector <3 x half> %179, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %195 = fmul fast <3 x half> %188, %194
  %196 = fadd fast <3 x half> %193, %195
  %197 = getelementptr inbounds %struct.SSRRenderROI.2420, ptr addrspace(2) %19, i64 0, i32 7
  %198 = load <4 x float>, ptr addrspace(2) %197, align 16, !alias.scope !71, !noalias !74
  %199 = shufflevector <4 x float> %198, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %200 = fmul fast <2 x float> %199, %29
  %201 = shufflevector <4 x float> %198, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %202 = fadd fast <2 x float> %200, %201
  %203 = getelementptr inbounds %struct.SSRRenderROI.2420, ptr addrspace(2) %19, i64 0, i32 8
  %204 = load <4 x float>, ptr addrspace(2) %203, align 16, !alias.scope !71, !noalias !74
  %205 = shufflevector <4 x float> %204, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %206 = fmul fast <2 x float> %205, %29
  %207 = shufflevector <4 x float> %204, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %208 = fadd fast <2 x float> %206, %207
  %209 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %8, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %202, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %210 = extractvalue { <4 x half>, i8 } %209, 0
  %211 = extractelement <4 x half> %210, i64 0
  %212 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %9, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %208, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %213 = extractvalue { <4 x half>, i8 } %212, 0
  %214 = extractelement <4 x half> %213, i64 0
  %215 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 7
  %216 = load float, ptr addrspace(1) %215, align 4, !tbaa !109, !alias.scope !95, !noalias !96
  %217 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 2
  %218 = load float, ptr addrspace(1) %217, align 4, !tbaa !110, !alias.scope !95, !noalias !96
  %219 = fcmp fast ugt float %218, 0.000000e+00
  br i1 %219, label %220, label %227

220:                                              ; preds = %175
  %221 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 1
  %222 = load float, ptr addrspace(1) %221, align 4, !tbaa !111, !alias.scope !95, !noalias !96
  %223 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 0
  %224 = load i32, ptr addrspace(1) %223, align 4, !tbaa !112, !alias.scope !95, !noalias !96
  %225 = fmul fast float %222, 5.000000e-01
  %226 = fsub fast float 1.000000e+00, %225
  br label %243

227:                                              ; preds = %175
  %228 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 15, i32 2
  %229 = load float, ptr addrspace(1) %228, align 4, !tbaa !113, !alias.scope !95, !noalias !96
  %230 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 1
  %231 = load float, ptr addrspace(1) %230, align 4, !tbaa !111, !alias.scope !95, !noalias !96
  %232 = fmul fast float %231, 5.000000e-01
  %233 = fsub fast float 1.000000e+00, %232
  %234 = tail call fast float @air.mix.f32(float %229, float %216, float %233) #25
  %235 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 0
  %236 = load i32, ptr addrspace(1) %235, align 4, !tbaa !112, !alias.scope !95, !noalias !96
  %237 = icmp eq i32 %236, 2
  %238 = select reassoc nsz arcp contract afn i1 %237, float %234, float %229
  store float %238, ptr addrspace(1) %228, align 4, !tbaa !113, !alias.scope !95, !noalias !96
  %239 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 15, i32 3
  %240 = load float, ptr addrspace(1) %239, align 4, !tbaa !114, !alias.scope !95, !noalias !96
  %241 = tail call fast float @air.mix.f32(float %240, float %216, float %233) #25
  %242 = select reassoc nsz arcp contract afn i1 %237, float %241, float %240
  store float %242, ptr addrspace(1) %239, align 4, !tbaa !114, !alias.scope !95, !noalias !96
  br label %243

243:                                              ; preds = %227, %220
  %244 = phi float [ %226, %220 ], [ %233, %227 ]
  %245 = phi i32 [ %224, %220 ], [ %236, %227 ]
  %246 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 15
  %247 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 15, i32 5
  %248 = load float, ptr addrspace(1) %247, align 4, !tbaa !115, !alias.scope !95, !noalias !96
  %249 = tail call fast float @air.mix.f32(float %248, float 1.000000e+00, float %244) #25
  %250 = icmp eq i32 %245, 2
  %251 = select reassoc nsz arcp contract afn i1 %250, float %249, float %248
  store float %251, ptr addrspace(1) %247, align 4, !tbaa !115, !alias.scope !95, !noalias !96
  %252 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 15, i32 6
  %253 = load float, ptr addrspace(1) %252, align 4, !tbaa !116, !alias.scope !95, !noalias !96
  %254 = tail call fast float @air.mix.f32(float %253, float 1.000000e+00, float %244) #25
  %255 = select reassoc nsz arcp contract afn i1 %250, float %254, float %253
  store float %255, ptr addrspace(1) %252, align 4, !tbaa !116, !alias.scope !95, !noalias !96
  %256 = getelementptr inbounds %struct.SSRRenderROI.2420, ptr addrspace(2) %19, i64 0, i32 4
  %257 = load <4 x float>, ptr addrspace(2) %256, align 16, !alias.scope !71, !noalias !74
  %258 = shufflevector <4 x float> %257, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %259 = fmul fast <2 x float> %258, %29
  %260 = shufflevector <4 x float> %257, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %261 = fadd fast <2 x float> %259, %260
  %262 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %2, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %261, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %263 = extractvalue { <4 x half>, i8 } %262, 0
  %264 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 1, i32 2, i32 0, i64 0
  %265 = load <3 x float>, ptr addrspace(2) %264, align 16, !tbaa !98, !alias.scope !106, !noalias !107
  %266 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %265) #25
  %267 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 1, i32 2, i32 0, i64 1
  %268 = load <3 x float>, ptr addrspace(2) %267, align 16, !tbaa !98, !alias.scope !106, !noalias !107
  %269 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %268) #25
  %270 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 1, i32 2, i32 0, i64 2
  %271 = load <3 x float>, ptr addrspace(2) %270, align 16, !tbaa !98, !alias.scope !106, !noalias !107
  %272 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %271) #25
  %273 = shufflevector <4 x half> %263, <4 x half> undef, <3 x i32> zeroinitializer
  %274 = fmul fast <3 x half> %266, %273
  %275 = shufflevector <4 x half> %263, <4 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %276 = fmul fast <3 x half> %269, %275
  %277 = fadd fast <3 x half> %276, %274
  %278 = shufflevector <4 x half> %263, <4 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %279 = fmul fast <3 x half> %272, %278
  %280 = fadd fast <3 x half> %277, %279
  %281 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 6
  %282 = load float, ptr addrspace(1) %281, align 4, !tbaa !117, !alias.scope !95, !noalias !96
  %283 = fptrunc float %282 to half
  %284 = insertelement <3 x half> poison, half %283, i64 0
  %285 = shufflevector <3 x half> %284, <3 x half> poison, <3 x i32> zeroinitializer
  %286 = fmul fast <3 x half> %285, %280
  %287 = tail call i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none) %6) #27, !alias.scope !80, !noalias !81
  br i1 %287, label %336, label %288

288:                                              ; preds = %243
  %289 = tail call i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none) %7) #27, !alias.scope !80, !noalias !81
  br i1 %289, label %336, label %290

290:                                              ; preds = %288
  %291 = getelementptr inbounds %struct.SSRRenderROI.2420, ptr addrspace(2) %19, i64 0, i32 5
  %292 = load <4 x float>, ptr addrspace(2) %291, align 16, !alias.scope !71, !noalias !74
  %293 = shufflevector <4 x float> %292, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %294 = fmul fast <2 x float> %293, %29
  %295 = shufflevector <4 x float> %292, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %296 = fadd fast <2 x float> %294, %295
  %297 = getelementptr inbounds %struct.SSRRenderROI.2420, ptr addrspace(2) %19, i64 0, i32 6
  %298 = load <4 x float>, ptr addrspace(2) %297, align 16, !alias.scope !71, !noalias !74
  %299 = shufflevector <4 x float> %298, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %300 = fmul fast <2 x float> %299, %29
  %301 = shufflevector <4 x float> %298, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %302 = fadd fast <2 x float> %300, %301
  %303 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %6, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %296, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %304 = extractvalue { <4 x half>, i8 } %303, 0
  %305 = shufflevector <4 x half> %304, <4 x half> poison, <3 x i32> <i32 0, i32 1, i32 2>
  %306 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %7, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %302, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %307 = extractvalue { <4 x half>, i8 } %306, 0
  %308 = shufflevector <4 x half> %307, <4 x half> poison, <3 x i32> <i32 0, i32 1, i32 2>
  %309 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 15, i32 1
  %310 = load float, ptr addrspace(1) %309, align 4, !tbaa !118, !alias.scope !95, !noalias !96
  %311 = fptrunc float %310 to half
  %312 = fptrunc float %255 to half
  %313 = insertelement <3 x half> poison, half %311, i64 0
  %314 = shufflevector <3 x half> %313, <3 x half> poison, <3 x i32> zeroinitializer
  %315 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %308, <3 x half> splat (half 0xH3C00), <3 x half> %314) #25
  %316 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %315, <3 x half> splat (half 0xH3C00)) #25
  %317 = insertelement <3 x half> poison, half %312, i64 0
  %318 = shufflevector <3 x half> %317, <3 x half> poison, <3 x i32> zeroinitializer
  %319 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %315, <3 x half> %316, <3 x half> %318) #25
  %320 = fmul fast <3 x half> %319, %196
  %321 = getelementptr inbounds %struct.SSRSemanticToneAdjustment.2415, ptr addrspace(1) %246, i64 0, i32 0
  %322 = load float, ptr addrspace(1) %321, align 4, !tbaa !119, !alias.scope !95, !noalias !96
  %323 = fptrunc float %322 to half
  %324 = fptrunc float %251 to half
  %325 = insertelement <3 x half> poison, half %323, i64 0
  %326 = shufflevector <3 x half> %325, <3 x half> poison, <3 x i32> zeroinitializer
  %327 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %305, <3 x half> splat (half 0xH3C00), <3 x half> %326) #25
  %328 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %327, <3 x half> splat (half 0xH3C00)) #25
  %329 = insertelement <3 x half> poison, half %324, i64 0
  %330 = shufflevector <3 x half> %329, <3 x half> poison, <3 x i32> zeroinitializer
  %331 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %327, <3 x half> %328, <3 x half> %330) #25
  %332 = fmul fast <3 x half> %331, %196
  %333 = insertelement <3 x half> poison, half %96, i64 0
  %334 = shufflevector <3 x half> %333, <3 x half> poison, <3 x i32> zeroinitializer
  %335 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %332, <3 x half> %320, <3 x half> %334) #25
  br label %344

336:                                              ; preds = %288, %243
  %337 = tail call fast fastcc <3 x half> @_Z29renderSemanticToneAdjustmentsDv3_DhS_DhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEERU9MTLdevice25SSRSemanticToneAdjustment(<3 x half> noundef %286, <3 x half> noundef %196, half noundef %96, ptr addrspace(1) %3, ptr addrspace(1) noundef align 4 dereferenceable(28) %246) #29
  %338 = getelementptr inbounds %struct.SSRSemanticToneAdjustment.2415, ptr addrspace(1) %246, i64 0, i32 0
  %339 = load float, ptr addrspace(1) %338, align 4, !tbaa !119, !alias.scope !95, !noalias !96
  %340 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 15, i32 1
  %341 = load float, ptr addrspace(1) %340, align 4, !tbaa !118, !alias.scope !95, !noalias !96
  %342 = fptrunc float %339 to half
  %343 = fptrunc float %341 to half
  br label %344

344:                                              ; preds = %336, %290
  %345 = phi half [ %343, %336 ], [ %311, %290 ]
  %346 = phi half [ %342, %336 ], [ %323, %290 ]
  %347 = phi <3 x half> [ %337, %336 ], [ %335, %290 ]
  %348 = tail call fast half @air.mix.f16(half %214, half %211, half %346) #25
  %349 = tail call fast half @air.mix.f16(half %214, half %211, half %345) #25
  %350 = tail call fast half @air.mix.f16(half %348, half %349, half %96) #25
  %351 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 13
  %352 = tail call fast fastcc <3 x half> @_Z19renderBGAdjustmentsDv3_DhDhDhDhRU9MTLdevice15SSRBGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE(<3 x half> noundef %347, half noundef %350, half undef, half noundef %96, ptr addrspace(1) noundef align 4 dereferenceable(68) %351, ptr addrspace(1) %4) #29
  %353 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 14
  %354 = tail call fast fastcc <3 x half> @_Z19renderFGAdjustmentsDv3_DhS_DhDhDhDhRU9MTLdevice15SSRFGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE(<3 x half> noundef %352, <3 x half> noundef %347, half noundef %96, half undef, half noundef %95, half noundef %350, ptr addrspace(1) noundef align 4 dereferenceable(64) %353, ptr addrspace(1) %4) #29
  %355 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 3
  %356 = load float, ptr addrspace(1) %355, align 4, !tbaa !120, !alias.scope !95, !noalias !96
  %357 = fptrunc float %356 to half
  %358 = fpext half %357 to float
  %359 = fcmp fast olt half %357, 0xH0000
  %360 = fmul fast float %358, 0x3FE99999A0000000
  %361 = fmul fast half %357, %357
  %362 = fptrunc float %360 to half
  %363 = select fast i1 %359, half %362, half %361
  %364 = fadd fast half %363, 0xH3C00
  %365 = fcmp fast ogt half %357, 0xH0000
  br i1 %365, label %366, label %371

366:                                              ; preds = %344
  %367 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 11, i32 2
  %368 = load float, ptr addrspace(1) %367, align 4, !tbaa !121, !alias.scope !95, !noalias !96
  %369 = fptrunc float %368 to half
  %370 = tail call fast fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %354, half noundef %364, half undef, half noundef %369) #30
  br label %373

371:                                              ; preds = %344
  %372 = tail call fast fastcc <3 x half> @_Z15smoothSatFilterDv3_DhDh(<3 x half> noundef %354, half noundef %364) #30
  br label %373

373:                                              ; preds = %371, %366
  %374 = phi <3 x half> [ %370, %366 ], [ %372, %371 ]
  br i1 %365, label %375, label %378

375:                                              ; preds = %373
  %376 = fadd fast float %358, 0xBFE3333340000000
  %377 = tail call fast float @air.fast_fmax.f32(float %376, float 0x3FC99999A0000000) #25
  br label %382

378:                                              ; preds = %373
  %379 = fmul fast float %358, 0x3FE3333340000000
  %380 = fsub fast float 0x3FB99999A0000000, %379
  %381 = tail call fast float @air.fast_fmax.f32(float %380, float 0x3FC99999A0000000) #25
  br label %382

382:                                              ; preds = %378, %375
  %383 = phi fast float [ %377, %375 ], [ %381, %378 ]
  %384 = fptrunc float %383 to half
  %385 = fpext half %96 to float
  %386 = fpext half %384 to float
  %387 = fsub fast float 1.000000e+00, %386
  %388 = fmul fast float %387, %385
  %389 = fptrunc float %388 to half
  %390 = insertelement <3 x half> poison, half %389, i64 0
  %391 = shufflevector <3 x half> %390, <3 x half> poison, <3 x i32> zeroinitializer
  %392 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %374, <3 x half> %354, <3 x half> %391) #25
  %393 = tail call fast fastcc <3 x half> @_Z21renderSkinAdjustmentsDv3_DhRU9MTLdevice15SSRFGAdjustmentDhDh(<3 x half> noundef %392, ptr addrspace(1) noundef align 4 dereferenceable(64) %353, half noundef %95, half noundef %350) #28, !alias.scope !95, !noalias !96
  %394 = tail call fast fastcc <3 x half> @_Z16highlightRecoverDv3_DhDhDhDhDh(<3 x half> noundef %393, half noundef %350, half undef, half undef, half noundef 0xH4000) #28
  %395 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %393, <3 x half> %394, <3 x half> splat (half 0xH3800)) #25
  %396 = insertelement <3 x i1> poison, i1 %250, i64 0
  %397 = shufflevector <3 x i1> %396, <3 x i1> poison, <3 x i32> zeroinitializer
  %398 = select fast <3 x i1> %397, <3 x half> %395, <3 x half> %393
  %399 = fptrunc float %216 to half
  %400 = tail call fast fastcc <3 x half> @_Z23renderBrightAndContrastDv3_DhS_DhDhDhRU9MTLdevice8SSRStats(<3 x half> noundef %393, <3 x half> noundef %286, half noundef %96, half noundef %95, half noundef %399, ptr addrspace(1) noundef align 4 dereferenceable(10640) %18) #29, !alias.scope !122, !noalias !123
  %401 = icmp eq i32 %245, 16
  %402 = insertelement <3 x i1> poison, i1 %401, i64 0
  %403 = shufflevector <3 x i1> %402, <3 x i1> poison, <3 x i32> zeroinitializer
  %404 = select fast <3 x i1> %403, <3 x half> %400, <3 x half> %393
  %405 = xor i1 %51, true
  %406 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 9
  %407 = xor i1 %64, true
  %408 = tail call fast fastcc <3 x half> @_Z29renderNeutralizingAdjustmentsDv3_DhbRU9MTLdevice18SSRCastAdjustmentsDhDhbRU9MTLdevice8SSRStats(<3 x half> noundef %404, i1 noundef zeroext %405, ptr addrspace(1) noundef align 4 dereferenceable(136) %406, half noundef %95, half noundef %96, i1 noundef zeroext %407, ptr addrspace(1) noundef align 4 dereferenceable(10640) %18) #29, !alias.scope !124, !noalias !125
  %409 = tail call fast fastcc <3 x half> @_Z27renderWarmthCastAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsDh(<3 x half> noundef %408, ptr addrspace(1) noundef align 4 dereferenceable(136) %406, half noundef %96) #29, !alias.scope !95, !noalias !96
  %410 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 11, i32 3
  %411 = load float, ptr addrspace(1) %410, align 4, !tbaa !126, !alias.scope !95, !noalias !96
  %412 = fptrunc float %411 to half
  %413 = tail call fast fastcc <3 x half> @_Z31renderSelectiveColorAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEEDhDhDhDh(<3 x half> noundef %409, ptr addrspace(1) noundef align 4 dereferenceable(136) %406, ptr addrspace(1) %13, half noundef %96, half noundef %95, half noundef %77, half noundef %412) #29
  %414 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 17
  %415 = load i32, ptr addrspace(1) %414, align 4, !tbaa !127, !alias.scope !95, !noalias !96
  %416 = icmp eq i32 %415, 5
  %417 = select i1 %416, half 0xH399A, half 0xH3B33
  %418 = tail call fast float @air.fast_fmin.f32(float %218, float 0.000000e+00) #25
  %419 = fptrunc float %418 to half
  %420 = fneg fast half %419
  %421 = tail call fast half @air.mix.f16(half %417, half 0xHACCD, half %420) #25
  %422 = tail call fast half @air.mix.f16(half 0xH3C00, half 0xH38CD, half %420) #25
  %423 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 10, i32 65
  %424 = load float, ptr addrspace(1) %423, align 4, !tbaa !128, !alias.scope !95, !noalias !96
  %425 = fmul fast half %417, 0xH3800
  %426 = tail call fast fastcc <3 x half> @_Z10airyFilterDv3_DhDh(<3 x half> noundef %413, half noundef %425) #30
  %427 = fpext half %421 to float
  %428 = fmul fast float %427, 0x3FA99999A0000000
  %429 = fptrunc float %428 to half
  %430 = fmul fast half %429, 0xH4000
  %431 = fpext half %430 to float
  %432 = fsub fast float 1.000000e+00, %431
  %433 = fdiv fast float 1.000000e+00, %432
  %434 = fptrunc float %433 to half
  %435 = insertelement <3 x half> poison, half %434, i64 0
  %436 = shufflevector <3 x half> %435, <3 x half> poison, <3 x i32> zeroinitializer
  %437 = fmul fast <3 x half> %436, %426
  %438 = insertelement <3 x half> poison, half %429, i64 0
  %439 = shufflevector <3 x half> %438, <3 x half> poison, <3 x i32> zeroinitializer
  %440 = fadd fast <3 x half> %437, %439
  %441 = tail call fast half @air.dot.v3f16(<3 x half> %426, <3 x half> splat (half 0xH3555)) #25
  %442 = fpext half %441 to float
  %443 = fpext half %434 to float
  %444 = fmul fast float %443, %442
  %445 = fpext half %429 to float
  %446 = fadd fast float %444, %445
  %447 = fdiv fast float %446, %442
  %448 = fptrunc float %447 to half
  %449 = insertelement <3 x half> poison, half %448, i64 0
  %450 = shufflevector <3 x half> %449, <3 x half> poison, <3 x i32> zeroinitializer
  %451 = fmul fast <3 x half> %450, %426
  %452 = fcmp fast ogt half %441, 0xH0000
  %453 = insertelement <3 x i1> poison, i1 %452, i64 0
  %454 = shufflevector <3 x i1> %453, <3 x i1> poison, <3 x i32> zeroinitializer
  %455 = select fast <3 x i1> %454, <3 x half> %451, <3 x half> zeroinitializer
  %456 = insertelement <3 x half> poison, half %422, i64 0
  %457 = shufflevector <3 x half> %456, <3 x half> poison, <3 x i32> zeroinitializer
  %458 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %455, <3 x half> %440, <3 x half> %457) #25
  %459 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %458, <3 x half> zeroinitializer) #25
  %460 = fmul fast float %427, 0xBFC99999A0000000
  %461 = fptrunc float %460 to half
  %462 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %459, half noundef %461) #30
  %463 = fsub fast float 1.000000e+00, %424
  %464 = fmul fast float %463, %385
  %465 = fptrunc float %464 to half
  %466 = insertelement <3 x half> poison, half %465, i64 0
  %467 = shufflevector <3 x half> %466, <3 x half> poison, <3 x i32> zeroinitializer
  %468 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %462, <3 x half> %413, <3 x half> %467) #25
  %469 = icmp eq i32 %245, 3
  %470 = insertelement <3 x i1> poison, i1 %469, i64 0
  %471 = shufflevector <3 x i1> %470, <3 x i1> poison, <3 x i32> zeroinitializer
  %472 = select fast <3 x i1> %471, <3 x half> %468, <3 x half> %413
  %473 = icmp eq i32 %245, 4
  %474 = insertelement <3 x i1> poison, i1 %473, i64 0
  %475 = shufflevector <3 x i1> %474, <3 x i1> poison, <3 x i32> zeroinitializer
  %476 = select fast <3 x i1> %475, <3 x half> %472, <3 x half> %398
  %477 = tail call fast fastcc <3 x half> @_Z29renderBWAdjustmentsByCastTypeDhDhN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEEDv3_DhRU9MTLdevice9SSRParams(half noundef %350, half noundef %96, ptr addrspace(1) %4, <3 x half> noundef %472, ptr addrspace(1) noundef align 4 dereferenceable(672) %17) #29
  %478 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 4
  %479 = load float, ptr addrspace(1) %478, align 4, !tbaa !129, !alias.scope !95, !noalias !96
  %480 = fptrunc float %479 to half
  %481 = insertelement <3 x half> poison, half %480, i64 0
  %482 = shufflevector <3 x half> %481, <3 x half> poison, <3 x i32> zeroinitializer
  %483 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %476, <3 x half> %477, <3 x half> %482) #25
  %484 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 5
  %485 = load float, ptr addrspace(1) %484, align 4, !tbaa !130, !alias.scope !95, !noalias !96
  %486 = fptrunc float %485 to half
  %487 = insertelement <3 x half> poison, half %486, i64 0
  %488 = shufflevector <3 x half> %487, <3 x half> poison, <3 x i32> zeroinitializer
  %489 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %476, <3 x half> %477, <3 x half> %488) #25
  %490 = insertelement <3 x half> poison, half %96, i64 0
  %491 = shufflevector <3 x half> %490, <3 x half> poison, <3 x i32> zeroinitializer
  %492 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %489, <3 x half> %483, <3 x half> %491) #25
  %493 = tail call fast fastcc <3 x half> @_Z25renderVideoHazeCorrectionDv3_DhDhRU9MTLdevice9SSRParamsDh(<3 x half> noundef %492, half noundef %211, ptr addrspace(1) noundef align 4 dereferenceable(672) %17, half noundef %96) #29, !alias.scope !95, !noalias !96
  %494 = icmp eq i32 %415, 7
  %495 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 12, i32 0
  %496 = load i8, ptr addrspace(1) %495, align 4, !alias.scope !95, !noalias !96
  %497 = icmp ne i8 %496, 0
  %498 = select i1 %494, i1 %497, i1 false
  %499 = insertelement <3 x i1> poison, i1 %498, i64 0
  %500 = shufflevector <3 x i1> %499, <3 x i1> poison, <3 x i32> zeroinitializer
  %501 = select fast <3 x i1> %500, <3 x half> %493, <3 x half> %492
  %502 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 9, i32 19
  %503 = load float, ptr addrspace(1) %502, align 4, !tbaa !131, !alias.scope !95, !noalias !96
  %504 = fcmp fast olt float %503, 0x3F847AE140000000
  %505 = or i1 %51, %504
  br i1 %505, label %565, label %506

506:                                              ; preds = %382
  %507 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %18, i64 0, i32 1, i64 2, i32 4
  %508 = load float, ptr addrspace(1) %507, align 4, !tbaa !132, !alias.scope !122, !noalias !123
  %509 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %18, i64 0, i32 1, i64 3, i32 4
  %510 = load float, ptr addrspace(1) %509, align 4, !tbaa !132, !alias.scope !122, !noalias !123
  %511 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %18, i64 0, i32 1, i64 4, i32 4
  %512 = load float, ptr addrspace(1) %511, align 4, !tbaa !132, !alias.scope !122, !noalias !123
  %513 = fptrunc float %508 to half
  %514 = insertelement <3 x half> undef, half %513, i64 0
  %515 = fptrunc float %510 to half
  %516 = insertelement <3 x half> %514, half %515, i64 1
  %517 = fptrunc float %512 to half
  %518 = insertelement <3 x half> %516, half %517, i64 2
  %519 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %518) #25
  %520 = shufflevector <3 x float> %519, <3 x float> poison, <3 x i32> zeroinitializer
  %521 = fmul fast <3 x float> %520, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %522 = shufflevector <3 x float> %519, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %523 = fmul fast <3 x float> %522, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %524 = fadd fast <3 x float> %521, %523
  %525 = shufflevector <3 x float> %519, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %526 = fmul fast <3 x float> %525, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %527 = fadd fast <3 x float> %524, %526
  %528 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %527) #25
  %529 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %527) #25
  %530 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %529, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %531 = fmul fast <3 x float> %530, %528
  %532 = shufflevector <3 x float> %531, <3 x float> poison, <3 x i32> zeroinitializer
  %533 = fmul fast <3 x float> %532, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %534 = shufflevector <3 x float> %531, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %535 = fmul fast <3 x float> %534, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %536 = fadd fast <3 x float> %533, %535
  %537 = shufflevector <3 x float> %531, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %538 = fmul fast <3 x float> %537, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %539 = fadd fast <3 x float> %536, %538
  %540 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %539) #25
  %541 = extractelement <3 x half> %540, i64 2
  %542 = fcmp fast une half %541, 0xH0000
  %543 = extractelement <3 x half> %540, i64 1
  %544 = fcmp fast une half %543, 0xH0000
  %545 = select i1 %542, i1 true, i1 %544
  br i1 %545, label %546, label %548

546:                                              ; preds = %506
  %547 = tail call fast half @air.atan2.f16(half %541, half %543) #25
  br label %548

548:                                              ; preds = %546, %506
  %549 = phi fast half [ %547, %546 ], [ 0xH0000, %506 ]
  %550 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %17, i64 0, i32 9, i32 20
  %551 = load float, ptr addrspace(1) %550, align 4, !tbaa !134, !alias.scope !95, !noalias !96
  %552 = fmul fast float %551, %551
  %553 = fmul fast float %552, 0x3F19690E20000000
  %554 = fptrunc float %553 to half
  %555 = insertelement <3 x half> <half poison, half poison, half 0xH3C00>, half %549, i64 0
  %556 = insertelement <3 x half> %555, half %554, i64 1
  %557 = tail call fast fastcc <3 x half> @_Z17protectMaskFilterDv3_DhS_S_S_b(<3 x half> noundef %501, <3 x half> noundef %556, <3 x half> noundef %556, <3 x half> noundef %556, i1 noundef zeroext true) #30
  %558 = extractelement <3 x half> %557, i64 0
  %559 = fpext half %558 to float
  %560 = fmul fast float %503, %559
  %561 = fptrunc float %560 to half
  %562 = insertelement <3 x half> poison, half %561, i64 0
  %563 = shufflevector <3 x half> %562, <3 x half> poison, <3 x i32> zeroinitializer
  %564 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %501, <3 x half> %476, <3 x half> %563) #25
  br label %565

565:                                              ; preds = %548, %382
  %566 = phi <3 x half> [ %564, %548 ], [ %501, %382 ]
  %567 = tail call fast fastcc <3 x half> @_Z26renderChannelMixForBWCastsDhDv3_DhRU9MTLdevice9SSRParamsRU9MTLdevice8SSRStats(half noundef %96, <3 x half> noundef %566, ptr addrspace(1) noundef align 4 dereferenceable(672) %17, ptr addrspace(1) noundef align 4 dereferenceable(10640) %18) #29, !alias.scope !124, !noalias !125
  br i1 %138, label %568, label %575

568:                                              ; preds = %565
  %569 = fcmp fast ogt float %218, 0.000000e+00
  %570 = fmul fast float %218, 2.000000e+00
  %571 = tail call fast float @air.fast_fabs.f32(float %570) #25
  %572 = fptrunc float %571 to half
  %573 = tail call fast half @air.mix.f16(half 0xH3C00, half 0xH3C00, half %572) #25
  %574 = select i1 %569, half %573, half 0xH3C00
  br label %575

575:                                              ; preds = %568, %565
  %576 = phi half [ 0xH3C00, %565 ], [ %574, %568 ]
  %577 = fdiv fast half %576, %176
  %578 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 3, i32 2, i32 0, i64 0
  %579 = load <3 x float>, ptr addrspace(2) %578, align 16, !tbaa !98, !alias.scope !106, !noalias !107
  %580 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %579) #25
  %581 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 3, i32 2, i32 0, i64 1
  %582 = load <3 x float>, ptr addrspace(2) %581, align 16, !tbaa !98, !alias.scope !106, !noalias !107
  %583 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %582) #25
  %584 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 3, i32 2, i32 0, i64 2
  %585 = load <3 x float>, ptr addrspace(2) %584, align 16, !tbaa !98, !alias.scope !106, !noalias !107
  %586 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %585) #25
  %587 = shufflevector <3 x half> %567, <3 x half> poison, <3 x i32> zeroinitializer
  %588 = fmul fast <3 x half> %580, %587
  %589 = shufflevector <3 x half> %567, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %590 = fmul fast <3 x half> %583, %589
  %591 = fadd fast <3 x half> %590, %588
  %592 = shufflevector <3 x half> %567, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %593 = fmul fast <3 x half> %586, %592
  %594 = fadd fast <3 x half> %591, %593
  %595 = insertelement <3 x half> poison, half %577, i64 0
  %596 = shufflevector <3 x half> %595, <3 x half> poison, <3 x i32> zeroinitializer
  %597 = fmul fast <3 x half> %594, %596
  %598 = getelementptr inbounds %struct.SSRColorManagement.192.2408, ptr addrspace(2) %16, i64 0, i32 3, i32 0
  %599 = load i32, ptr addrspace(2) %598, align 16, !tbaa !135, !alias.scope !106, !noalias !107
  %600 = tail call fastcc <3 x half> @_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_(<3 x half> noundef %597, i32 noundef %599) #28
  %601 = load i8, ptr addrspace(2) @_ZL13useImageBlock, align 1, !tbaa !63, !range !67
  %602 = icmp eq i8 %601, 0
  br i1 %602, label %615, label %603

603:                                              ; preds = %575
  %604 = tail call ptr addrspace(4) @air.imageblock_data(<2 x i16> %22, i32 0, i16 0) #31
  %605 = shufflevector <3 x half> %600, <3 x half> poison, <4 x i32> <i32 0, i32 1, i32 2, i32 poison>
  %606 = insertelement <4 x half> %605, half 0xH3C00, i64 3
  %607 = bitcast ptr addrspace(4) %604 to ptr addrspace(4)
  store <4 x half> %606, ptr addrspace(4) %607, align 8, !tbaa !70
  tail call void @air.wg.barrier(i32 8, i32 5, i32 1) #32
  %608 = icmp eq <2 x i16> %22, zeroinitializer
  %609 = tail call i1 @air.all.v2i1(<2 x i1> %608) #25
  br i1 %609, label %610, label %618

610:                                              ; preds = %603
  %611 = getelementptr inbounds %struct.SSRRenderROI.2420, ptr addrspace(2) %19, i64 0, i32 2
  %612 = load <2 x i16>, ptr addrspace(2) %611, align 8, !tbaa !70, !alias.scope !71, !noalias !74
  %613 = sub <2 x i16> %612, %27
  %614 = tail call <2 x i16> @air.min.u.v2i16(<2 x i16> %23, <2 x i16> %613) #25
  tail call void @air.write_imageblock_slice_to_texture_2d.i16.v4f16(ptr addrspace(1) captures(none) %14, ptr addrspace(4) captures(none) %604, i1 true, <2 x i16> zeroinitializer, <2 x i16> %614, <2 x i16> %27, i16 0, i1 false, i32 2) #33
  br label %618

615:                                              ; preds = %575
  %616 = shufflevector <3 x half> %600, <3 x half> poison, <4 x i32> <i32 0, i32 1, i32 2, i32 poison>
  %617 = insertelement <4 x half> %616, half 0xH3C00, i64 3
  tail call void @air.write_texture_2d.i16.v4f16(ptr addrspace(1) captures(none) %14, <2 x i16> %27, <4 x half> %617, i16 0, i32 2) #33, !alias.scope !80, !noalias !81
  br label %618

618:                                              ; preds = %615, %610, %603
  ret void
}

; Function Attrs: mustprogress nounwind willreturn memory(argmem: readwrite)
declare void @air.write_texture_2d.i16.v4f16(ptr addrspace(1) captures(none), <2 x i16>, <4 x half>, i16, i32) local_unnamed_addr #3

; Function Attrs: mustprogress nounwind willreturn memory(argmem: readwrite)
declare void @air.write_imageblock_slice_to_texture_2d.i16.v4f16(ptr addrspace(1) captures(none), ptr addrspace(4) captures(none), i1, <2 x i16>, <2 x i16>, <2 x i16>, i16, i1, i32) local_unnamed_addr #3

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <2 x i16> @air.min.u.v2i16(<2 x i16>, <2 x i16>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i1 @air.all.v2i1(<2 x i1>) local_unnamed_addr #0

; Function Attrs: convergent mustprogress nounwind willreturn
declare void @air.wg.barrier(i32, i32, i32) local_unnamed_addr #4

; Function Attrs: mustprogress nofree nounwind willreturn memory(read)
declare ptr addrspace(4) @air.imageblock_data(<2 x i16>, i32, i16) local_unnamed_addr #5

; Function Attrs: inlinehint mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_(<3 x half> noundef %0, i32 noundef %1) unnamed_addr #6 {
  switch i32 %1, label %75 [
    i32 0, label %3
    i32 1, label %3
    i32 2, label %4
    i32 3, label %9
    i32 4, label %19
    i32 5, label %29
    i32 6, label %39
    i32 7, label %55
    i32 8, label %69
  ]

3:                                                ; preds = %2, %2
  br label %75

4:                                                ; preds = %2
  %5 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %6 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %7 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %6, <3 x half> splat (half 0xH3C00)) #25
  %8 = fmul fast <3 x half> %7, %5
  br label %75

9:                                                ; preds = %2
  %10 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %11 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %12 = fmul fast <3 x half> %11, splat (half 0xH4A76)
  %13 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %11, <3 x half> splat (half 0xH36AA)) #25
  %14 = fmul fast <3 x half> %13, splat (half 0xH3C38)
  %15 = fadd fast <3 x half> %14, splat (half 0xHAB0A)
  %16 = fcmp fast ogt <3 x half> %11, splat (half 0xH1A69)
  %17 = select fast <3 x i1> %16, <3 x half> %15, <3 x half> %12
  %18 = fmul fast <3 x half> %17, %10
  br label %75

19:                                               ; preds = %2
  %20 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %21 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %22 = fmul fast <3 x half> %21, splat (half 0xH4480)
  %23 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %21, <3 x half> splat (half 0xH3733)) #25
  %24 = fmul fast <3 x half> %23, splat (half 0xH3C65)
  %25 = fadd fast <3 x half> %24, splat (half 0xHAE56)
  %26 = fcmp fast ogt <3 x half> %21, splat (half 0xH249C)
  %27 = select fast <3 x i1> %26, <3 x half> %25, <3 x half> %22
  %28 = fmul fast <3 x half> %27, %20
  br label %75

29:                                               ; preds = %2
  %30 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %31 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %32 = fmul fast <3 x half> %31, splat (half 0xH4480)
  %33 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %31, <3 x half> splat (half 0xH3733)) #25
  %34 = fmul fast <3 x half> %33, splat (half 0xH3C66)
  %35 = fadd fast <3 x half> %34, splat (half 0xHAE5B)
  %36 = fcmp fast ogt <3 x half> %31, splat (half 0xH249F)
  %37 = select fast <3 x i1> %36, <3 x half> %35, <3 x half> %32
  %38 = fmul fast <3 x half> %37, %30
  br label %75

39:                                               ; preds = %2
  %40 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %41 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %42 = tail call fast <3 x half> @air.log.v3f16(<3 x half> splat (half 0xH39B9)) #25
  %43 = fmul fast <3 x half> %42, splat (half 0xHB1B9)
  %44 = fadd fast <3 x half> %43, splat (half 0xH3800)
  %45 = fmul fast <3 x half> %41, splat (half 0xH4200)
  %46 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %45) #25
  %47 = fmul fast <3 x half> %41, splat (half 0xH4A00)
  %48 = fadd fast <3 x half> %47, splat (half 0xHB48E)
  %49 = tail call fast <3 x half> @air.log.v3f16(<3 x half> %48) #25
  %50 = fmul fast <3 x half> %49, splat (half 0xH31B9)
  %51 = fadd fast <3 x half> %44, %50
  %52 = fcmp fast ogt <3 x half> %41, splat (half 0xH2D55)
  %53 = select fast <3 x i1> %52, <3 x half> %51, <3 x half> %46
  %54 = fmul fast <3 x half> %53, %40
  br label %75

55:                                               ; preds = %2
  %56 = fadd fast <3 x half> %0, splat (half 0xH20F0)
  %57 = tail call fast <3 x half> @air.log2.v3f16(<3 x half> %56) #25
  %58 = fmul fast <3 x half> %57, splat (half 0xH2D79)
  %59 = fadd fast <3 x half> %58, splat (half 0xH398C)
  %60 = fcmp fast oge <3 x half> %0, splat (half 0xH211F)
  %61 = select fast <3 x i1> %60, <3 x half> %59, <3 x half> zeroinitializer
  %62 = fadd fast <3 x half> %0, splat (half 0xH2B38)
  %63 = fmul fast <3 x half> %62, %62
  %64 = fmul fast <3 x half> %63, splat (half 0xH51E9)
  %65 = fcmp fast ogt <3 x half> %0, splat (half 0xHAB38)
  %66 = fcmp fast olt <3 x half> %0, splat (half 0xH211F)
  %67 = and <3 x i1> %65, %66
  %68 = select fast <3 x i1> %67, <3 x half> %64, <3 x half> %61
  br label %75

69:                                               ; preds = %2
  %70 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %71 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %72 = fcmp fast ogt <3 x half> %71, splat (half 0xH1800)
  %73 = select fast <3 x i1> %72, <3 x half> splat (half 0xHB900), <3 x half> %71
  %74 = fmul fast <3 x half> %73, %70
  br label %75

75:                                               ; preds = %69, %55, %39, %29, %19, %9, %4, %3, %2
  %76 = phi <3 x half> [ zeroinitializer, %2 ], [ %74, %69 ], [ %68, %55 ], [ %54, %39 ], [ %38, %29 ], [ %28, %19 ], [ %18, %9 ], [ %8, %4 ], [ %0, %3 ]
  ret <3 x half> %76
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.fabs.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.sign.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.log2.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.log.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.sqrt.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.pow.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.mix.f16(half, half, half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_fabs.f32(float) local_unnamed_addr #0

; Function Attrs: convergent mustprogress nofree nosync nounwind willreturn memory(argmem: read)
define internal fastcc <3 x half> @_Z26renderChannelMixForBWCastsDhDv3_DhRU9MTLdevice9SSRParamsRU9MTLdevice8SSRStats(half noundef %0, <3 x half> noundef %1, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(672) %2, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(10640) %3) unnamed_addr #7 {
  %5 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 0
  %6 = load i32, ptr addrspace(1) %5, align 4, !tbaa !112
  switch i32 %6, label %75 [
    i32 4, label %7
    i32 15, label %44
  ]

7:                                                ; preds = %4
  %8 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 10, i32 17
  %9 = load float, ptr addrspace(1) %8, align 4, !tbaa !136
  %10 = fptrunc float %9 to half
  %11 = insertelement <3 x half> undef, half %10, i64 0
  %12 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 10, i32 18
  %13 = load float, ptr addrspace(1) %12, align 4, !tbaa !137
  %14 = fptrunc float %13 to half
  %15 = insertelement <3 x half> %11, half %14, i64 1
  %16 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 10, i32 19
  %17 = load float, ptr addrspace(1) %16, align 4, !tbaa !138
  %18 = fptrunc float %17 to half
  %19 = insertelement <3 x half> %15, half %18, i64 2
  %20 = tail call fast fastcc <3 x half> @_Z24getBWChannelMixFromStatsRU9MTLdevice8SSRStatsRU9MTLdevice9SSRParams(ptr addrspace(1) noundef align 4 dereferenceable(10640) %3, ptr addrspace(1) noundef align 4 dereferenceable(672) %2) #28
  %21 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %1) #25
  %22 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %1) #25
  %23 = fmul fast <3 x half> %22, splat (half 0xH4A76)
  %24 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %22, <3 x half> splat (half 0xH36AA)) #25
  %25 = fmul fast <3 x half> %24, splat (half 0xH3C38)
  %26 = fadd fast <3 x half> %25, splat (half 0xHAB0A)
  %27 = fcmp fast ogt <3 x half> %22, splat (half 0xH1A69)
  %28 = select fast <3 x i1> %27, <3 x half> %26, <3 x half> %23
  %29 = fmul fast <3 x half> %28, %21
  %30 = tail call fast half @air.dot.v3f16(<3 x half> %29, <3 x half> %19) #25
  %31 = tail call fast half @air.dot.v3f16(<3 x half> %29, <3 x half> %20) #25
  %32 = tail call fast half @air.mix.f16(half %30, half %31, half %0) #25
  %33 = insertelement <3 x half> poison, half %32, i64 0
  %34 = shufflevector <3 x half> %33, <3 x half> poison, <3 x i32> zeroinitializer
  %35 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %34) #25
  %36 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %34) #25
  %37 = fmul fast <3 x half> %36, splat (half 0xH2CF4)
  %38 = fadd fast <3 x half> %36, splat (half 0xH2B0A)
  %39 = fmul fast <3 x half> %38, splat (half 0xH3B96)
  %40 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %39, <3 x half> splat (half 0xH40CD)) #25
  %41 = fcmp fast ogt <3 x half> %36, splat (half 0xH292D)
  %42 = select fast <3 x i1> %41, <3 x half> %40, <3 x half> %37
  %43 = fmul fast <3 x half> %42, %35
  br label %75

44:                                               ; preds = %4
  %45 = tail call fast fastcc <3 x half> @_Z24getBWChannelMixFromStatsRU9MTLdevice8SSRStatsRU9MTLdevice9SSRParams(ptr addrspace(1) noundef align 4 dereferenceable(10640) %3, ptr addrspace(1) noundef align 4 dereferenceable(672) %2) #28
  %46 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %1) #25
  %47 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %1) #25
  %48 = fmul fast <3 x half> %47, splat (half 0xH4A76)
  %49 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %47, <3 x half> splat (half 0xH36AA)) #25
  %50 = fmul fast <3 x half> %49, splat (half 0xH3C38)
  %51 = fadd fast <3 x half> %50, splat (half 0xHAB0A)
  %52 = fcmp fast ogt <3 x half> %47, splat (half 0xH1A69)
  %53 = select fast <3 x i1> %52, <3 x half> %51, <3 x half> %48
  %54 = fmul fast <3 x half> %53, %46
  %55 = tail call fast half @air.dot.v3f16(<3 x half> %54, <3 x half> %54) #25
  %56 = extractelement <3 x half> %54, i64 0
  %57 = extractelement <3 x half> %54, i64 1
  %58 = fadd fast half %56, %57
  %59 = extractelement <3 x half> %54, i64 2
  %60 = fadd fast half %58, %59
  %61 = fdiv fast half %55, %60
  %62 = tail call fast half @air.dot.v3f16(<3 x half> %54, <3 x half> %45) #25
  %63 = tail call fast half @air.mix.f16(half %61, half %62, half %0) #25
  %64 = insertelement <3 x half> poison, half %63, i64 0
  %65 = shufflevector <3 x half> %64, <3 x half> poison, <3 x i32> zeroinitializer
  %66 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %65) #25
  %67 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %65) #25
  %68 = fmul fast <3 x half> %67, splat (half 0xH2CF4)
  %69 = fadd fast <3 x half> %67, splat (half 0xH2B0A)
  %70 = fmul fast <3 x half> %69, splat (half 0xH3B96)
  %71 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %70, <3 x half> splat (half 0xH40CD)) #25
  %72 = fcmp fast ogt <3 x half> %67, splat (half 0xH292D)
  %73 = select fast <3 x i1> %72, <3 x half> %71, <3 x half> %68
  %74 = fmul fast <3 x half> %73, %66
  br label %75

75:                                               ; preds = %44, %7, %4
  %76 = phi <3 x half> [ %43, %7 ], [ %74, %44 ], [ %1, %4 ]
  ret <3 x half> %76
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.dot.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(argmem: read)
define internal fastcc <3 x half> @_Z24getBWChannelMixFromStatsRU9MTLdevice8SSRStatsRU9MTLdevice9SSRParams(ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(10640) %0, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(672) %1) unnamed_addr #8 {
  %3 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %0, i64 0, i32 1, i64 2, i32 4
  %4 = load float, ptr addrspace(1) %3, align 4, !tbaa !132
  %5 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %0, i64 0, i32 1, i64 3, i32 4
  %6 = load float, ptr addrspace(1) %5, align 4, !tbaa !132
  %7 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %0, i64 0, i32 1, i64 4, i32 4
  %8 = load float, ptr addrspace(1) %7, align 4, !tbaa !132
  %9 = fptrunc float %4 to half
  %10 = insertelement <3 x half> undef, half %9, i64 0
  %11 = fptrunc float %6 to half
  %12 = insertelement <3 x half> %10, half %11, i64 1
  %13 = fptrunc float %8 to half
  %14 = insertelement <3 x half> %12, half %13, i64 2
  %15 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %14) #25
  %16 = shufflevector <3 x float> %15, <3 x float> poison, <3 x i32> zeroinitializer
  %17 = fmul fast <3 x float> %16, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %18 = shufflevector <3 x float> %15, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %19 = fmul fast <3 x float> %18, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %20 = fadd fast <3 x float> %17, %19
  %21 = shufflevector <3 x float> %15, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %22 = fmul fast <3 x float> %21, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %23 = fadd fast <3 x float> %20, %22
  %24 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %23) #25
  %25 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %23) #25
  %26 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %25, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %27 = fmul fast <3 x float> %26, %24
  %28 = shufflevector <3 x float> %27, <3 x float> poison, <3 x i32> zeroinitializer
  %29 = fmul fast <3 x float> %28, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %30 = shufflevector <3 x float> %27, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %31 = fmul fast <3 x float> %30, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %32 = fadd fast <3 x float> %29, %31
  %33 = shufflevector <3 x float> %27, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %34 = fmul fast <3 x float> %33, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %35 = fadd fast <3 x float> %32, %34
  %36 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %35) #25
  %37 = extractelement <3 x half> %36, i64 2
  %38 = fcmp fast une half %37, 0xH0000
  %39 = extractelement <3 x half> %36, i64 1
  %40 = fcmp fast une half %39, 0xH0000
  %41 = select i1 %38, i1 true, i1 %40
  br i1 %41, label %42, label %44

42:                                               ; preds = %2
  %43 = tail call fast half @air.atan2.f16(half %37, half %39) #25
  br label %44

44:                                               ; preds = %42, %2
  %45 = phi fast half [ %43, %42 ], [ 0xH0000, %2 ]
  %46 = tail call fast half @air.fabs.f16(half %45) #25
  %47 = fmul fast half %46, 0xH3C72
  %48 = tail call fast half @air.clamp.f16(half %47, half 0xH0000, half 0xH3C00) #25
  %49 = fmul fast half %48, %48
  %50 = fmul fast half %48, 0xH4000
  %51 = fsub fast half 0xH4200, %50
  %52 = fmul fast half %49, %51
  %53 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %1, i64 0, i32 0
  %54 = load i32, ptr addrspace(1) %53, align 4, !tbaa !112
  switch i32 %54, label %63 [
    i32 4, label %55
    i32 15, label %59
  ]

55:                                               ; preds = %44
  %56 = insertelement <3 x half> poison, half %52, i64 0
  %57 = shufflevector <3 x half> %56, <3 x half> poison, <3 x i32> zeroinitializer
  %58 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> splat (half 0xH3555), <3 x half> <half 0xH3883, half 0xH3629, half 0xH2A87>, <3 x half> %57) #25
  br label %63

59:                                               ; preds = %44
  %60 = insertelement <3 x half> poison, half %52, i64 0
  %61 = shufflevector <3 x half> %60, <3 x half> poison, <3 x i32> zeroinitializer
  %62 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> splat (half 0xH3555), <3 x half> <half 0xH38F8, half 0xH3558, half 0xH2B0A>, <3 x half> %61) #25
  br label %63

63:                                               ; preds = %59, %55, %44
  %64 = phi <3 x half> [ %58, %55 ], [ %62, %59 ], [ undef, %44 ]
  %65 = extractelement <3 x half> %64, i64 0
  %66 = extractelement <3 x half> %64, i64 1
  %67 = fadd fast half %65, %66
  %68 = extractelement <3 x half> %64, i64 2
  %69 = fadd fast half %67, %68
  %70 = fdiv fast half %65, %69
  %71 = fdiv fast half %66, %69
  %72 = fdiv fast half %68, %69
  %73 = insertelement <3 x half> undef, half %70, i64 0
  %74 = insertelement <3 x half> %73, half %71, i64 1
  %75 = insertelement <3 x half> %74, half %72, i64 2
  ret <3 x half> %75
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.mix.v3f16(<3 x half>, <3 x half>, <3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.clamp.f16(half, half, half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fabs.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.atan2.f16(half, half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x float> @air.fast_pow.v3f32(<3 x float>, <3 x float>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x float> @air.fast_fabs.v3f32(<3 x float>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x float> @air.sign.v3f32(<3 x float>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z17protectMaskFilterDv3_DhS_S_S_b(<3 x half> noundef %0, <3 x half> noundef %1, <3 x half> noundef %2, <3 x half> noundef %3, i1 noundef zeroext %4) unnamed_addr #9 {
  %6 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %0) #25
  %7 = shufflevector <3 x float> %6, <3 x float> poison, <3 x i32> zeroinitializer
  %8 = fmul fast <3 x float> %7, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %9 = shufflevector <3 x float> %6, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %10 = fmul fast <3 x float> %9, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %11 = fadd fast <3 x float> %8, %10
  %12 = shufflevector <3 x float> %6, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %13 = fmul fast <3 x float> %12, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %14 = fadd fast <3 x float> %11, %13
  %15 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %14) #25
  %16 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %14) #25
  %17 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %16, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %18 = fmul fast <3 x float> %17, %15
  %19 = shufflevector <3 x float> %18, <3 x float> poison, <3 x i32> zeroinitializer
  %20 = fmul fast <3 x float> %19, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %21 = shufflevector <3 x float> %18, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %22 = fmul fast <3 x float> %21, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %23 = fadd fast <3 x float> %20, %22
  %24 = shufflevector <3 x float> %18, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %25 = fmul fast <3 x float> %24, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %26 = fadd fast <3 x float> %23, %25
  %27 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %26) #25
  %28 = extractelement <3 x half> %1, i64 1
  %29 = tail call fast half @air.fmax.f16(half %28, half 0xH0001) #25
  %30 = extractelement <3 x half> %2, i64 1
  %31 = tail call fast half @air.fmax.f16(half %30, half 0xH0001) #25
  %32 = extractelement <3 x half> %3, i64 1
  %33 = tail call fast half @air.fmax.f16(half %32, half 0xH0001) #25
  %34 = extractelement <3 x half> %27, i64 2
  %35 = fcmp fast une half %34, 0xH0000
  %36 = extractelement <3 x half> %27, i64 1
  %37 = fcmp fast une half %36, 0xH0000
  %38 = select i1 %35, i1 true, i1 %37
  br i1 %38, label %39, label %41

39:                                               ; preds = %5
  %40 = tail call fast half @air.atan2.f16(half %34, half %36) #25
  br label %41

41:                                               ; preds = %39, %5
  %42 = phi fast half [ %40, %39 ], [ 0xH0000, %5 ]
  %43 = extractelement <3 x half> %1, i64 0
  %44 = fsub fast half %42, %43
  %45 = fcmp fast ogt half %42, 0xH0000
  %46 = fpext half %44 to float
  br i1 %45, label %47, label %54

47:                                               ; preds = %41
  %48 = fadd fast float %46, -6.281250e+00
  %49 = fneg fast float %48
  %50 = fmul fast float %48, %49
  %51 = fpext half %29 to float
  %52 = fdiv fast float %50, %51
  %53 = tail call fast float @air.fast_exp.f32(float %52) #25
  br label %61

54:                                               ; preds = %41
  %55 = fadd fast float %46, 6.281250e+00
  %56 = fneg fast float %55
  %57 = fmul fast float %55, %56
  %58 = fpext half %29 to float
  %59 = fdiv fast float %57, %58
  %60 = tail call fast float @air.fast_exp.f32(float %59) #25
  br label %61

61:                                               ; preds = %54, %47
  %62 = phi float [ %53, %47 ], [ %60, %54 ]
  %63 = extractelement <3 x half> %2, i64 0
  %64 = fsub fast half %42, %63
  %65 = fpext half %64 to float
  br i1 %45, label %66, label %73

66:                                               ; preds = %61
  %67 = fadd fast float %65, -6.281250e+00
  %68 = fneg fast float %67
  %69 = fmul fast float %67, %68
  %70 = fpext half %31 to float
  %71 = fdiv fast float %69, %70
  %72 = tail call fast float @air.fast_exp.f32(float %71) #25
  br label %80

73:                                               ; preds = %61
  %74 = fadd fast float %65, 6.281250e+00
  %75 = fneg fast float %74
  %76 = fmul fast float %74, %75
  %77 = fpext half %31 to float
  %78 = fdiv fast float %76, %77
  %79 = tail call fast float @air.fast_exp.f32(float %78) #25
  br label %80

80:                                               ; preds = %73, %66
  %81 = phi float [ %72, %66 ], [ %79, %73 ]
  %82 = extractelement <3 x half> %3, i64 0
  %83 = fsub fast half %42, %82
  %84 = fpext half %83 to float
  br i1 %45, label %85, label %92

85:                                               ; preds = %80
  %86 = fadd fast float %84, -6.281250e+00
  %87 = fneg fast float %86
  %88 = fmul fast float %86, %87
  %89 = fpext half %33 to float
  %90 = fdiv fast float %88, %89
  %91 = tail call fast float @air.fast_exp.f32(float %90) #25
  br label %99

92:                                               ; preds = %80
  %93 = fadd fast float %84, 6.281250e+00
  %94 = fneg fast float %93
  %95 = fmul fast float %93, %94
  %96 = fpext half %33 to float
  %97 = fdiv fast float %95, %96
  %98 = tail call fast float @air.fast_exp.f32(float %97) #25
  br label %99

99:                                               ; preds = %92, %85
  %100 = phi float [ %91, %85 ], [ %98, %92 ]
  %101 = fneg fast half %83
  %102 = fmul fast half %83, %101
  %103 = fdiv fast half %102, %33
  %104 = tail call fast half @air.exp.f16(half %103) #25
  %105 = extractelement <3 x half> %3, i64 2
  %106 = fmul fast half %104, %105
  %107 = fpext half %106 to float
  %108 = fpext half %105 to float
  %109 = fmul fast float %100, %108
  %110 = fadd fast float %109, %107
  %111 = extractelement <3 x half> %2, i64 2
  %112 = fpext half %111 to float
  %113 = fmul fast float %81, %112
  %114 = fneg fast half %64
  %115 = fmul fast half %64, %114
  %116 = fdiv fast half %115, %31
  %117 = tail call fast half @air.exp.f16(half %116) #25
  %118 = fmul fast half %117, %111
  %119 = fpext half %118 to float
  %120 = fadd fast float %113, %119
  %121 = extractelement <3 x half> %1, i64 2
  %122 = fpext half %121 to float
  %123 = fmul fast float %62, %122
  %124 = fneg fast half %44
  %125 = fmul fast half %44, %124
  %126 = fdiv fast half %125, %29
  %127 = tail call fast half @air.exp.f16(half %126) #25
  %128 = fmul fast half %127, %121
  %129 = fpext half %128 to float
  %130 = fadd fast float %123, %129
  %131 = shufflevector <3 x half> %27, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %132 = tail call fast half @air.dot.v2f16(<2 x half> %131, <2 x half> %131) #25
  %133 = tail call fast half @air.sqrt.f16(half %132) #25
  %134 = fptrunc float %120 to half
  %135 = fptrunc float %130 to half
  %136 = fadd fast half %133, 0xHAA66
  %137 = fmul fast half %136, 0xH4E3E
  %138 = tail call fast half @air.clamp.f16(half %137, half 0xH0000, half 0xH3C00) #25
  %139 = fmul fast half %138, %138
  %140 = fmul fast half %138, 0xH4000
  %141 = fsub fast half 0xH4200, %140
  %142 = fmul fast half %139, %141
  %143 = select i1 %4, half 0xH3C00, half %142
  %144 = fptrunc float %110 to half
  %145 = fmul fast half %143, %135
  %146 = insertelement <3 x half> undef, half %145, i64 0
  %147 = fmul fast half %143, %134
  %148 = insertelement <3 x half> %146, half %147, i64 1
  %149 = fmul fast half %143, %144
  %150 = insertelement <3 x half> %148, half %149, i64 2
  ret <3 x half> %150
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.sqrt.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.dot.v2f16(<2 x half>, <2 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.exp.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_exp.f32(float) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmax.f16(half, half) local_unnamed_addr #0

; Function Attrs: convergent mustprogress nofree nosync nounwind willreturn memory(argmem: read)
define internal fastcc <3 x half> @_Z25renderVideoHazeCorrectionDv3_DhDhRU9MTLdevice9SSRParamsDh(<3 x half> noundef %0, half noundef %1, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(672) %2, half noundef %3) unnamed_addr #7 {
  %5 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 12, i32 1
  %6 = load float, ptr addrspace(1) %5, align 4, !tbaa.struct !139
  %7 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 12, i32 2
  %8 = load float, ptr addrspace(1) %7, align 4, !tbaa.struct !140
  %9 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 12, i32 3
  %10 = load float, ptr addrspace(1) %9, align 4, !tbaa.struct !141
  %11 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 12, i32 4
  %12 = load float, ptr addrspace(1) %11, align 4, !tbaa.struct !142
  %13 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 12, i32 5
  %14 = load float, ptr addrspace(1) %13, align 4, !tbaa.struct !143
  %15 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 12, i32 6
  %16 = load float, ptr addrspace(1) %15, align 4, !tbaa.struct !144
  %17 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 12, i32 7
  %18 = load float, ptr addrspace(1) %17, align 4, !tbaa.struct !145
  %19 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %2, i64 0, i32 12, i32 8
  %20 = load float, ptr addrspace(1) %19, align 4, !tbaa.struct !146
  %21 = fdiv fast float %6, %8
  %22 = fptrunc float %21 to half
  %23 = fpext half %22 to float
  %24 = fsub fast float 1.000000e+00, %23
  %25 = fdiv fast float 1.000000e+00, %24
  %26 = fptrunc float %25 to half
  %27 = fptrunc float %16 to half
  %28 = insertelement <3 x half> poison, half %26, i64 0
  %29 = shufflevector <3 x half> %28, <3 x half> poison, <3 x i32> zeroinitializer
  %30 = fmul fast <3 x half> %29, %0
  %31 = insertelement <3 x half> poison, half %22, i64 0
  %32 = shufflevector <3 x half> %31, <3 x half> poison, <3 x i32> zeroinitializer
  %33 = fadd fast <3 x half> %30, %32
  %34 = tail call fast half @air.dot.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3555)) #25
  %35 = fpext half %34 to float
  %36 = fpext half %26 to float
  %37 = fmul fast float %35, %36
  %38 = fadd fast float %37, %23
  %39 = fdiv fast float %38, %35
  %40 = fptrunc float %39 to half
  %41 = insertelement <3 x half> poison, half %40, i64 0
  %42 = shufflevector <3 x half> %41, <3 x half> poison, <3 x i32> zeroinitializer
  %43 = fmul fast <3 x half> %42, %0
  %44 = fcmp fast ogt half %34, 0xH0000
  %45 = insertelement <3 x i1> poison, i1 %44, i64 0
  %46 = shufflevector <3 x i1> %45, <3 x i1> poison, <3 x i32> zeroinitializer
  %47 = select fast <3 x i1> %46, <3 x half> %43, <3 x half> zeroinitializer
  %48 = insertelement <3 x half> poison, half %27, i64 0
  %49 = shufflevector <3 x half> %48, <3 x half> poison, <3 x i32> zeroinitializer
  %50 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %47, <3 x half> %33, <3 x half> %49) #25
  %51 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %50, <3 x half> zeroinitializer) #25
  %52 = fdiv fast float %6, %10
  %53 = fptrunc float %52 to half
  %54 = fpext half %53 to float
  %55 = fsub fast float 1.000000e+00, %54
  %56 = fdiv fast float 1.000000e+00, %55
  %57 = fptrunc float %56 to half
  %58 = insertelement <3 x half> poison, half %57, i64 0
  %59 = shufflevector <3 x half> %58, <3 x half> poison, <3 x i32> zeroinitializer
  %60 = fmul fast <3 x half> %59, %0
  %61 = insertelement <3 x half> poison, half %53, i64 0
  %62 = shufflevector <3 x half> %61, <3 x half> poison, <3 x i32> zeroinitializer
  %63 = fadd fast <3 x half> %60, %62
  %64 = fpext half %57 to float
  %65 = fmul fast float %35, %64
  %66 = fadd fast float %65, %54
  %67 = fdiv fast float %66, %35
  %68 = fptrunc float %67 to half
  %69 = insertelement <3 x half> poison, half %68, i64 0
  %70 = shufflevector <3 x half> %69, <3 x half> poison, <3 x i32> zeroinitializer
  %71 = fmul fast <3 x half> %70, %0
  %72 = select fast <3 x i1> %46, <3 x half> %71, <3 x half> zeroinitializer
  %73 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %72, <3 x half> %63, <3 x half> %49) #25
  %74 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %73, <3 x half> zeroinitializer) #25
  %75 = fptrunc float %12 to half
  %76 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %51, <3 x half> zeroinitializer) #25
  %77 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %51, <3 x half> splat (half 0xH3C00)) #25
  %78 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %51) #25
  %79 = extractelement <3 x half> %78, i64 0
  %80 = extractelement <3 x half> %78, i64 1
  %81 = extractelement <3 x half> %78, i64 2
  %82 = tail call fast half @air.fmax3.f16(half %79, half %80, half %81) #25
  %83 = tail call fast half @air.pow.f16(half %82, half 0xH3800) #25
  %84 = fsub fast half 0xH3C00, %83
  %85 = fmul fast half %84, %75
  %86 = fadd fast half %85, 0xH3C00
  %87 = insertelement <3 x half> poison, half %86, i64 0
  %88 = shufflevector <3 x half> %87, <3 x half> poison, <3 x i32> zeroinitializer
  %89 = fmul fast <3 x half> %88, %78
  %90 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %89) #25
  %91 = fadd fast <3 x half> %76, splat (half 0xHBC00)
  %92 = fadd fast <3 x half> %91, %77
  %93 = fadd fast <3 x half> %92, %90
  %94 = fptrunc float %14 to half
  %95 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %74, <3 x half> zeroinitializer) #25
  %96 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %74, <3 x half> splat (half 0xH3C00)) #25
  %97 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %74) #25
  %98 = extractelement <3 x half> %97, i64 0
  %99 = extractelement <3 x half> %97, i64 1
  %100 = extractelement <3 x half> %97, i64 2
  %101 = tail call fast half @air.fmax3.f16(half %98, half %99, half %100) #25
  %102 = tail call fast half @air.pow.f16(half %101, half 0xH3800) #25
  %103 = fsub fast half 0xH3C00, %102
  %104 = fmul fast half %103, %94
  %105 = fadd fast half %104, 0xH3C00
  %106 = insertelement <3 x half> poison, half %105, i64 0
  %107 = shufflevector <3 x half> %106, <3 x half> poison, <3 x i32> zeroinitializer
  %108 = fmul fast <3 x half> %107, %97
  %109 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %108) #25
  %110 = fadd fast <3 x half> %95, splat (half 0xHBC00)
  %111 = fadd fast <3 x half> %110, %96
  %112 = fadd fast <3 x half> %111, %109
  %113 = fptrunc float %18 to half
  %114 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %93, half noundef %113) #28
  %115 = fptrunc float %20 to half
  %116 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %114, <3 x half> zeroinitializer) #25
  %117 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %114, <3 x half> splat (half 0xH3C00)) #25
  %118 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %114) #25
  %119 = tail call fast half @air.dot.v3f16(<3 x half> %118, <3 x half> splat (half 0xH3555)) #25
  %120 = tail call fast half @air.sqrt.f16(half %119) #25
  %121 = fpext half %120 to float
  %122 = fsub fast float 1.000000e+00, %121
  %123 = fmul fast float %122, %121
  %124 = fptrunc float %123 to half
  %125 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %118) #25
  %126 = tail call fast half @air.sqrt.f16(half %1) #25
  %127 = fmul fast half %124, %115
  %128 = fmul fast half %127, 0xH4000
  %129 = fmul fast half %127, 0xHC000
  %130 = fmul fast half %129, %126
  %131 = fpext half %128 to float
  %132 = fmul fast float %131, 0x3FD322D0E0000000
  %133 = fptrunc float %132 to half
  %134 = insertelement <3 x half> poison, half %133, i64 0
  %135 = fmul fast <3 x half> %125, %134
  %136 = shufflevector <3 x half> %135, <3 x half> poison, <3 x i32> zeroinitializer
  %137 = shufflevector <3 x half> %125, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %138 = fmul fast float %131, 0x3FE2C8B440000000
  %139 = fptrunc float %138 to half
  %140 = insertelement <3 x half> poison, half %139, i64 0
  %141 = shufflevector <3 x half> %140, <3 x half> poison, <3 x i32> zeroinitializer
  %142 = fmul fast <3 x half> %137, %141
  %143 = shufflevector <3 x half> %125, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %144 = fmul fast float %131, 0x3FBD2F1AA0000000
  %145 = fptrunc float %144 to half
  %146 = insertelement <3 x half> poison, half %145, i64 0
  %147 = shufflevector <3 x half> %146, <3 x half> poison, <3 x i32> zeroinitializer
  %148 = fmul fast <3 x half> %143, %147
  %149 = insertelement <3 x half> poison, half %130, i64 0
  %150 = shufflevector <3 x half> %149, <3 x half> poison, <3 x i32> zeroinitializer
  %151 = fadd fast <3 x half> %142, %125
  %152 = fadd fast <3 x half> %151, %136
  %153 = fadd fast <3 x half> %152, %148
  %154 = fadd fast <3 x half> %153, %150
  %155 = insertelement <3 x half> poison, half %126, i64 0
  %156 = shufflevector <3 x half> %155, <3 x half> poison, <3 x i32> zeroinitializer
  %157 = fmul fast half %127, 0xHC000
  %158 = insertelement <3 x half> poison, half %157, i64 0
  %159 = shufflevector <3 x half> %158, <3 x half> poison, <3 x i32> zeroinitializer
  %160 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %125, <3 x half> %156, <3 x half> %159) #25
  %161 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %160, <3 x half> %154, <3 x half> splat (half 0xH3A66)) #25
  %162 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %161, <3 x half> zeroinitializer) #25
  %163 = fmul fast <3 x half> %162, %162
  %164 = fadd fast <3 x half> %116, splat (half 0xHBC00)
  %165 = fadd fast <3 x half> %164, %117
  %166 = fadd fast <3 x half> %165, %163
  %167 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %166, <3 x half> %114) #25
  %168 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %166, <3 x half> %167, <3 x half> zeroinitializer) #25
  %169 = insertelement <3 x half> poison, half %3, i64 0
  %170 = shufflevector <3 x half> %169, <3 x half> poison, <3 x i32> zeroinitializer
  %171 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %168, <3 x half> %112, <3 x half> %170) #25
  ret <3 x half> %171
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.fmax.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.saturate.v3f16(<3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.fmin.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %0, half noundef %1) unnamed_addr #10 {
  %3 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %4 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %5 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %6 = tail call fast half @air.dot.v3f16(<3 x half> %5, <3 x half> splat (half 0xH3555)) #25
  %7 = tail call fast half @air.sqrt.f16(half %6) #25
  %8 = extractelement <3 x half> %5, i64 0
  %9 = fsub fast half %8, %7
  %10 = fmul fast half %9, %9
  %11 = extractelement <3 x half> %5, i64 1
  %12 = fsub fast half %11, %7
  %13 = fmul fast half %12, %12
  %14 = fadd fast half %10, %13
  %15 = extractelement <3 x half> %5, i64 2
  %16 = fsub fast half %15, %7
  %17 = fmul fast half %16, %16
  %18 = fadd fast half %14, %17
  %19 = fpext half %7 to float
  %20 = fsub fast float 1.000000e+00, %19
  %21 = fmul fast float %20, %19
  %22 = fptrunc float %21 to half
  %23 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %5) #25
  %24 = fpext half %1 to float
  %25 = fmul fast float %24, 0x400B333340000000
  %26 = fptrunc float %25 to half
  %27 = fmul fast half %22, %26
  %28 = fpext half %27 to float
  %29 = fmul fast half %27, 0xHB800
  %30 = fmul fast float %28, 0x3FD322D0E0000000
  %31 = fptrunc float %30 to half
  %32 = insertelement <3 x half> poison, half %31, i64 0
  %33 = fmul fast <3 x half> %32, %23
  %34 = shufflevector <3 x half> %33, <3 x half> poison, <3 x i32> zeroinitializer
  %35 = shufflevector <3 x half> %23, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %36 = fmul fast float %28, 0x3FE2C8B440000000
  %37 = fptrunc float %36 to half
  %38 = insertelement <3 x half> poison, half %37, i64 0
  %39 = shufflevector <3 x half> %38, <3 x half> poison, <3 x i32> zeroinitializer
  %40 = fmul fast <3 x half> %39, %35
  %41 = shufflevector <3 x half> %23, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %42 = fmul fast float %28, 0x3FBD2F1AA0000000
  %43 = fptrunc float %42 to half
  %44 = insertelement <3 x half> poison, half %43, i64 0
  %45 = shufflevector <3 x half> %44, <3 x half> poison, <3 x i32> zeroinitializer
  %46 = fmul fast <3 x half> %45, %41
  %47 = insertelement <3 x half> poison, half %29, i64 0
  %48 = shufflevector <3 x half> %47, <3 x half> poison, <3 x i32> zeroinitializer
  %49 = fadd fast <3 x half> %48, %23
  %50 = fadd fast <3 x half> %49, %40
  %51 = fadd fast <3 x half> %50, %34
  %52 = fadd fast <3 x half> %51, %46
  %53 = fneg fast half %26
  %54 = fmul fast half %53, %22
  %55 = insertelement <3 x half> poison, half %54, i64 0
  %56 = shufflevector <3 x half> %55, <3 x half> poison, <3 x i32> zeroinitializer
  %57 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %23, <3 x half> splat (half 0xH3800), <3 x half> %56) #25
  %58 = fpext half %18 to float
  %59 = fadd fast float %58, 0x3FE99999A0000000
  %60 = fptrunc float %59 to half
  %61 = insertelement <3 x half> poison, half %60, i64 0
  %62 = shufflevector <3 x half> %61, <3 x half> poison, <3 x i32> zeroinitializer
  %63 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %57, <3 x half> %52, <3 x half> %62) #25
  %64 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %63, <3 x half> zeroinitializer) #25
  %65 = fmul fast <3 x half> %64, %64
  %66 = fadd fast <3 x half> %3, splat (half 0xHBC00)
  %67 = fadd fast <3 x half> %66, %4
  %68 = fadd fast <3 x half> %67, %65
  %69 = extractelement <3 x half> %0, i64 0
  %70 = extractelement <3 x half> %0, i64 1
  %71 = extractelement <3 x half> %0, i64 2
  %72 = tail call fast half @air.fmin3.f16(half %69, half %70, half %71) #25
  %73 = tail call fast half @air.fmax3.f16(half %69, half %70, half %71) #25
  %74 = fsub fast half %73, %72
  %75 = fpext half %74 to float
  %76 = fcmp fast ogt float %75, 0x3EE4F8B580000000
  br i1 %76, label %77, label %94

77:                                               ; preds = %2
  %78 = extractelement <3 x half> %68, i64 0
  %79 = extractelement <3 x half> %68, i64 1
  %80 = extractelement <3 x half> %68, i64 2
  %81 = tail call fast half @air.fmax3.f16(half %78, half %79, half %80) #25
  %82 = tail call fast half @air.fmin3.f16(half %78, half %79, half %80) #25
  %83 = fsub fast half %81, %82
  %84 = insertelement <3 x half> poison, half %82, i64 0
  %85 = shufflevector <3 x half> %84, <3 x half> poison, <3 x i32> zeroinitializer
  %86 = insertelement <3 x half> poison, half %72, i64 0
  %87 = shufflevector <3 x half> %86, <3 x half> poison, <3 x i32> zeroinitializer
  %88 = fsub fast <3 x half> %0, %87
  %89 = fdiv fast half %83, %74
  %90 = insertelement <3 x half> poison, half %89, i64 0
  %91 = shufflevector <3 x half> %90, <3 x half> poison, <3 x i32> zeroinitializer
  %92 = fmul fast <3 x half> %91, %88
  %93 = fadd fast <3 x half> %92, %85
  br label %94

94:                                               ; preds = %77, %2
  %95 = phi fast <3 x half> [ %93, %77 ], [ %68, %2 ]
  ret <3 x half> %95
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmin3.f16(half, half, half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmax3.f16(half, half, half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.pow.f16(half, half) local_unnamed_addr #0

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(read)
define internal fastcc <3 x half> @_Z29renderBWAdjustmentsByCastTypeDhDhN5metal9texture2dIDhLNS_6accessE0ELNS_16memory_coherenceE0EvEEDv3_DhRU9MTLdevice9SSRParams(half noundef %0, half noundef %1, ptr addrspace(1) %2, <3 x half> noundef %3, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(672) %4) unnamed_addr #11 {
  %6 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %4, i64 0, i32 2
  %7 = load float, ptr addrspace(1) %6, align 4, !tbaa !110
  %8 = fptrunc float %7 to half
  %9 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %4, i64 0, i32 10, i32 20
  %10 = load float, ptr addrspace(1) %9, align 4, !tbaa !147
  %11 = fptrunc float %10 to half
  %12 = tail call fast fastcc <3 x half> @_Z17starkBWAdjustmentDv3_DhDhDhDhDhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEE(<3 x half> noundef %3, half noundef %0, half noundef %1, half noundef %8, half noundef %11, ptr addrspace(1) %2) #29
  %13 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %4, i64 0, i32 0
  %14 = load i32, ptr addrspace(1) %13, align 4, !tbaa !112
  %15 = icmp eq i32 %14, 4
  %16 = insertelement <3 x i1> poison, i1 %15, i64 0
  %17 = shufflevector <3 x i1> %16, <3 x i1> poison, <3 x i32> zeroinitializer
  %18 = select fast <3 x i1> %17, <3 x half> %12, <3 x half> %3
  %19 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %4, i64 0, i32 17
  %20 = load i32, ptr addrspace(1) %19, align 4, !tbaa !127
  %21 = icmp eq i32 %20, 5
  %22 = select i1 %21, half 0xH399A, half 0xH3C00
  %23 = getelementptr inbounds %struct.SSRParams.2416, ptr addrspace(1) %4, i64 0, i32 10, i32 65
  %24 = load float, ptr addrspace(1) %23, align 4, !tbaa !128
  %25 = fmul fast half %22, 0xH3800
  %26 = tail call fast fastcc <3 x half> @_Z10airyFilterDv3_DhDh(<3 x half> noundef %18, half noundef %25) #30
  %27 = fpext half %22 to float
  %28 = fmul fast float %27, 0x3FA99999A0000000
  %29 = fptrunc float %28 to half
  %30 = fmul fast half %29, 0xH4000
  %31 = fpext half %30 to float
  %32 = fsub fast float 1.000000e+00, %31
  %33 = fdiv fast float 1.000000e+00, %32
  %34 = fptrunc float %33 to half
  %35 = insertelement <3 x half> poison, half %34, i64 0
  %36 = shufflevector <3 x half> %35, <3 x half> poison, <3 x i32> zeroinitializer
  %37 = fmul fast <3 x half> %36, %26
  %38 = insertelement <3 x half> poison, half %29, i64 0
  %39 = shufflevector <3 x half> %38, <3 x half> poison, <3 x i32> zeroinitializer
  %40 = fadd fast <3 x half> %37, %39
  %41 = tail call fast half @air.dot.v3f16(<3 x half> %26, <3 x half> splat (half 0xH3555)) #25
  %42 = fpext half %41 to float
  %43 = fpext half %34 to float
  %44 = fmul fast float %43, %42
  %45 = fpext half %29 to float
  %46 = fadd fast float %44, %45
  %47 = fdiv fast float %46, %42
  %48 = fptrunc float %47 to half
  %49 = insertelement <3 x half> poison, half %48, i64 0
  %50 = shufflevector <3 x half> %49, <3 x half> poison, <3 x i32> zeroinitializer
  %51 = fmul fast <3 x half> %50, %26
  %52 = fcmp fast ogt half %41, 0xH0000
  %53 = insertelement <3 x i1> poison, i1 %52, i64 0
  %54 = shufflevector <3 x i1> %53, <3 x i1> poison, <3 x i32> zeroinitializer
  %55 = select fast <3 x i1> %54, <3 x half> %51, <3 x half> zeroinitializer
  %56 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %55, <3 x half> %40, <3 x half> splat (half 0xH3C00)) #25
  %57 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %56, <3 x half> zeroinitializer) #25
  %58 = fmul fast float %27, 0xBFC99999A0000000
  %59 = fptrunc float %58 to half
  %60 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %57, half noundef %59) #30
  %61 = fpext half %1 to float
  %62 = fsub fast float 1.000000e+00, %24
  %63 = fmul fast float %62, %61
  %64 = fptrunc float %63 to half
  %65 = insertelement <3 x half> poison, half %64, i64 0
  %66 = shufflevector <3 x half> %65, <3 x half> poison, <3 x i32> zeroinitializer
  %67 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %60, <3 x half> %18, <3 x half> %66) #25
  %68 = icmp eq i32 %14, 15
  %69 = insertelement <3 x i1> poison, i1 %68, i64 0
  %70 = shufflevector <3 x i1> %69, <3 x i1> poison, <3 x i32> zeroinitializer
  %71 = select fast <3 x i1> %70, <3 x half> %67, <3 x half> %18
  ret <3 x half> %71
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z10airyFilterDv3_DhDh(<3 x half> noundef %0, half noundef %1) unnamed_addr #10 {
  %3 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %4 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %5 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %6 = extractelement <3 x half> %5, i64 0
  %7 = extractelement <3 x half> %5, i64 1
  %8 = fadd fast half %6, %7
  %9 = extractelement <3 x half> %5, i64 2
  %10 = fadd fast half %8, %9
  %11 = fdiv fast half 0xH3C00, %10
  %12 = fmul fast half %11, %6
  %13 = fmul fast half %11, %7
  %14 = fmul fast half %11, %9
  %15 = tail call fast half @air.fmax.f16(half %12, half %13) #25
  %16 = tail call fast half @air.fmax.f16(half %13, half %14) #25
  %17 = fadd fast half %15, 0xHB555
  %18 = fadd fast half %17, %16
  %19 = fmul fast half %18, 0xH3DFF
  %20 = tail call fast half @air.clamp.f16(half %19, half 0xH0000, half 0xH3C00) #25
  %21 = fmul fast half %20, %20
  %22 = fmul fast half %20, 0xH4000
  %23 = fsub fast half 0xH4200, %22
  %24 = fmul fast half %21, %23
  %25 = tail call fast half @air.dot.v3f16(<3 x half> %5, <3 x half> splat (half 0xH3555)) #25
  %26 = tail call fast half @air.sqrt.f16(half %25) #25
  %27 = insertelement <3 x half> poison, half %1, i64 0
  %28 = shufflevector <3 x half> %27, <3 x half> poison, <3 x i32> zeroinitializer
  %29 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %5, <3 x half> %28) #25
  %30 = fmul fast half %24, %26
  %31 = insertelement <3 x half> poison, half %30, i64 0
  %32 = shufflevector <3 x half> %31, <3 x half> poison, <3 x i32> zeroinitializer
  %33 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %5, <3 x half> %29, <3 x half> %32) #25
  %34 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %33) #25
  %35 = fadd fast <3 x half> %3, splat (half 0xHBC00)
  %36 = fadd fast <3 x half> %35, %4
  %37 = fadd fast <3 x half> %36, %34
  ret <3 x half> %37
}

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(read)
define internal fastcc <3 x half> @_Z17starkBWAdjustmentDv3_DhDhDhDhDhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEE(<3 x half> noundef %0, half noundef %1, half noundef %2, half noundef %3, half noundef %4, ptr addrspace(1) %5) unnamed_addr #12 {
  %7 = fcmp fast ogt half %3, 0xH0000
  %8 = fpext half %3 to float
  %9 = fmul fast float %8, 0x3FD99999A0000000
  %10 = fneg fast half %3
  %11 = fptrunc float %9 to half
  %12 = select fast i1 %7, half %11, half %10
  %13 = fmul fast half %12, %4
  %14 = tail call fast fastcc <3 x half> @_Z11whitesCurveDv3_DhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEEDhDh(<3 x half> noundef %0, ptr addrspace(1) %5, half noundef %13, half noundef 0xH3C00) #29
  %15 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %14, <3 x half> zeroinitializer) #25
  %16 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %14, <3 x half> splat (half 0xH3C00)) #25
  %17 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %14) #25
  %18 = tail call fast half @air.dot.v3f16(<3 x half> %17, <3 x half> splat (half 0xH3555)) #25
  %19 = tail call fast half @air.sqrt.f16(half %18) #25
  %20 = fpext half %19 to float
  %21 = fsub fast float 1.000000e+00, %20
  %22 = fmul fast float %21, %20
  %23 = fptrunc float %22 to half
  %24 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %17) #25
  %25 = tail call fast half @air.sqrt.f16(half %1) #25
  %26 = fneg fast half %25
  %27 = fmul fast half %26, %23
  %28 = fpext half %23 to float
  %29 = fmul fast float %28, 0x3FD322D0E0000000
  %30 = fptrunc float %29 to half
  %31 = insertelement <3 x half> poison, half %30, i64 0
  %32 = fmul fast <3 x half> %31, %24
  %33 = shufflevector <3 x half> %32, <3 x half> poison, <3 x i32> zeroinitializer
  %34 = shufflevector <3 x half> %24, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %35 = fmul fast float %28, 0x3FE2C8B440000000
  %36 = fptrunc float %35 to half
  %37 = insertelement <3 x half> poison, half %36, i64 0
  %38 = shufflevector <3 x half> %37, <3 x half> poison, <3 x i32> zeroinitializer
  %39 = fmul fast <3 x half> %38, %34
  %40 = shufflevector <3 x half> %24, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %41 = fmul fast float %28, 0x3FBD2F1AA0000000
  %42 = fptrunc float %41 to half
  %43 = insertelement <3 x half> poison, half %42, i64 0
  %44 = shufflevector <3 x half> %43, <3 x half> poison, <3 x i32> zeroinitializer
  %45 = fmul fast <3 x half> %44, %40
  %46 = insertelement <3 x half> poison, half %27, i64 0
  %47 = shufflevector <3 x half> %46, <3 x half> poison, <3 x i32> zeroinitializer
  %48 = fadd fast <3 x half> %47, %24
  %49 = fadd fast <3 x half> %48, %39
  %50 = fadd fast <3 x half> %49, %33
  %51 = fadd fast <3 x half> %50, %45
  %52 = insertelement <3 x half> poison, half %25, i64 0
  %53 = shufflevector <3 x half> %52, <3 x half> poison, <3 x i32> zeroinitializer
  %54 = fneg fast half %23
  %55 = insertelement <3 x half> poison, half %54, i64 0
  %56 = shufflevector <3 x half> %55, <3 x half> poison, <3 x i32> zeroinitializer
  %57 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %24, <3 x half> %53, <3 x half> %56) #25
  %58 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %57, <3 x half> %51, <3 x half> splat (half 0xH3A66)) #25
  %59 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %58, <3 x half> zeroinitializer) #25
  %60 = fmul fast <3 x half> %59, %59
  %61 = fadd fast <3 x half> %15, splat (half 0xHBC00)
  %62 = fadd fast <3 x half> %61, %16
  %63 = fadd fast <3 x half> %62, %60
  %64 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %63, <3 x half> %14) #25
  %65 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %63, <3 x half> %64, <3 x half> zeroinitializer) #25
  %66 = fpext half %2 to float
  %67 = fmul fast float %66, 0x3FE99999A0000000
  %68 = fptrunc float %67 to half
  %69 = insertelement <3 x half> poison, half %68, i64 0
  %70 = shufflevector <3 x half> %69, <3 x half> poison, <3 x i32> zeroinitializer
  %71 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %65, <3 x half> %0, <3 x half> %70) #25
  ret <3 x half> %71
}

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(read)
define internal fastcc <3 x half> @_Z11whitesCurveDv3_DhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEEDhDh(<3 x half> noundef %0, ptr addrspace(1) %1, half noundef %2, half noundef %3) unnamed_addr #13 {
  %5 = shufflevector <3 x half> %0, <3 x half> poison, <3 x i32> zeroinitializer
  %6 = fmul fast <3 x half> %5, <half 0xH383C, half 0xH2E4C, half 0xH2452>
  %7 = shufflevector <3 x half> %0, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %8 = fmul fast <3 x half> %7, <half 0xH3548, half 0xH3AFD, half 0xH2F88>
  %9 = fadd fast <3 x half> %6, %8
  %10 = shufflevector <3 x half> %0, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %11 = fmul fast <3 x half> %10, <half 0xH307F, half 0xH2734, half 0xH3AEC>
  %12 = fadd fast <3 x half> %9, %11
  %13 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %12) #25
  %14 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %13, <3 x half> splat (half 0xH3872)) #25
  %15 = extractelement <3 x half> %14, i64 0
  %16 = extractelement <3 x half> %14, i64 1
  %17 = extractelement <3 x half> %14, i64 2
  %18 = tail call fast half @air.fmin3.f16(half %15, half %16, half %17) #25
  %19 = tail call i32 @air.get_width_texture_2d(ptr addrspace(1) readonly captures(none) %1, i32 0) #27
  %20 = add nsw i32 %19, -1
  %21 = tail call fast half @air.convert.f.f16.s.i32(i32 %20) #25
  %22 = fmul fast half %21, %18
  %23 = fpext half %22 to float
  %24 = fadd fast float %23, 5.000000e-01
  %25 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %24, i64 0
  %26 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %1, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %25, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %27 = extractvalue { <4 x half>, i8 } %26, 0
  %28 = extractelement <4 x half> %27, i64 0
  %29 = tail call fast half @air.clamp.f16(half %28, half 0xH0000, half 0xH3C00) #25
  %30 = fcmp fast ogt half %18, 0xH3A00
  %31 = select i1 %30, half 0xH3C00, half %29
  %32 = tail call fast half @air.mix.f16(half %18, half %31, half %2) #25
  %33 = fcmp fast ogt half %18, 0xH0000
  br i1 %33, label %39, label %34

34:                                               ; preds = %4
  %35 = insertelement <3 x half> poison, half %18, i64 0
  %36 = shufflevector <3 x half> %35, <3 x half> poison, <3 x i32> zeroinitializer
  %37 = insertelement <3 x half> poison, half %32, i64 0
  %38 = shufflevector <3 x half> %37, <3 x half> poison, <3 x i32> zeroinitializer
  br label %47

39:                                               ; preds = %4
  %40 = insertelement <3 x half> poison, half %32, i64 0
  %41 = shufflevector <3 x half> %40, <3 x half> poison, <3 x i32> zeroinitializer
  %42 = fmul fast <3 x half> %41, %14
  %43 = insertelement <3 x half> poison, half %18, i64 0
  %44 = shufflevector <3 x half> %43, <3 x half> poison, <3 x i32> zeroinitializer
  %45 = fdiv fast <3 x half> %42, %44
  %46 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %14, <3 x half> %45, <3 x half> %44) #25
  br label %47

47:                                               ; preds = %39, %34
  %48 = phi <3 x half> [ %38, %34 ], [ %41, %39 ]
  %49 = phi <3 x half> [ %36, %34 ], [ %44, %39 ]
  %50 = phi fast <3 x half> [ %14, %34 ], [ %46, %39 ]
  %51 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %12, <3 x half> splat (half 0xH3C00)) #25
  %52 = fadd fast <3 x half> %51, splat (half 0xHBC00)
  %53 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %12, <3 x half> zeroinitializer) #25
  %54 = tail call fast half @air.mix.f16(half %18, half %32, half %3) #25
  %55 = fsub fast <3 x half> %14, %49
  %56 = fadd fast <3 x half> %55, %48
  %57 = insertelement <3 x half> poison, half %54, i64 0
  %58 = shufflevector <3 x half> %57, <3 x half> poison, <3 x i32> zeroinitializer
  %59 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %14, <3 x half> %56, <3 x half> %58) #25
  %60 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %50, <3 x half> %59, <3 x half> %49) #25
  %61 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %60, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #25
  %62 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %61, <3 x half> splat (half 0xH3F33)) #25
  %63 = fadd fast <3 x half> %52, %53
  %64 = fadd fast <3 x half> %63, %62
  %65 = shufflevector <3 x half> %64, <3 x half> poison, <3 x i32> zeroinitializer
  %66 = fmul fast <3 x half> %65, <half 0xH4011, half 0xHB353, half 0xHA060>
  %67 = shufflevector <3 x half> %64, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %68 = fmul fast <3 x half> %67, <half 0xHB9D2, half 0xH3CED, half 0xHB0E8>
  %69 = fadd fast <3 x half> %66, %68
  %70 = shufflevector <3 x half> %64, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %71 = fmul fast <3 x half> %70, <half 0xHB4E9, half 0xH99DE, half 0xH3CA6>
  %72 = fadd fast <3 x half> %69, %71
  %73 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %72, <3 x half> zeroinitializer) #25
  ret <3 x half> %73
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.clamp.v3f16(<3 x half>, <3 x half>, <3 x half>) local_unnamed_addr #0

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(argmem: read)
declare { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none), ptr addrspace(2) readonly captures(none), <2 x float>, i1, <2 x i32>, i1, float, float, i32) local_unnamed_addr #14

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.convert.f.f16.s.i32(i32) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i32 @air.get_width_texture_2d(ptr addrspace(1) readonly captures(none), i32) local_unnamed_addr #15

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_fmin.f32(float, float) local_unnamed_addr #0

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(read)
define internal fastcc <3 x half> @_Z31renderSelectiveColorAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEEDhDhDhDh(<3 x half> noundef %0, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(136) %1, ptr addrspace(1) readonly %2, half noundef %3, half noundef %4, half noundef %5, half noundef %6) unnamed_addr #16 {
  %8 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 9
  %9 = load float, ptr addrspace(1) %8, align 4, !tbaa !148
  %10 = tail call i1 @air.convert.u.i1.f.f32(float %9) #25
  br i1 %10, label %11, label %58

11:                                               ; preds = %7
  %12 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 12, i64 0
  %13 = load float, ptr addrspace(1) %12, align 4, !tbaa !98
  %14 = fptrunc float %13 to half
  %15 = insertelement <3 x half> undef, half %14, i64 0
  %16 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 12, i64 1
  %17 = load float, ptr addrspace(1) %16, align 4, !tbaa !98
  %18 = fptrunc float %17 to half
  %19 = insertelement <3 x half> %15, half %18, i64 1
  %20 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 12, i64 2
  %21 = load float, ptr addrspace(1) %20, align 4, !tbaa !98
  %22 = fptrunc float %21 to half
  %23 = insertelement <3 x half> %19, half %22, i64 2
  %24 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %23) #25
  %25 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %23) #25
  %26 = fmul fast <3 x half> %25, splat (half 0xH2CF4)
  %27 = fadd fast <3 x half> %25, splat (half 0xH2B0A)
  %28 = fmul fast <3 x half> %27, splat (half 0xH3B96)
  %29 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %28, <3 x half> splat (half 0xH40CD)) #25
  %30 = fcmp fast ogt <3 x half> %25, splat (half 0xH292D)
  %31 = select fast <3 x i1> %30, <3 x half> %29, <3 x half> %26
  %32 = fmul fast <3 x half> %31, %24
  %33 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %32) #25
  %34 = shufflevector <3 x float> %33, <3 x float> poison, <3 x i32> zeroinitializer
  %35 = fmul fast <3 x float> %34, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %36 = shufflevector <3 x float> %33, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %37 = fmul fast <3 x float> %36, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %38 = fadd fast <3 x float> %35, %37
  %39 = shufflevector <3 x float> %33, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %40 = fmul fast <3 x float> %39, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %41 = fadd fast <3 x float> %38, %40
  %42 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %41) #25
  %43 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %41) #25
  %44 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %43, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %45 = fmul fast <3 x float> %44, %42
  %46 = shufflevector <3 x float> %45, <3 x float> poison, <3 x i32> zeroinitializer
  %47 = fmul fast <3 x float> %46, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %48 = shufflevector <3 x float> %45, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %49 = fmul fast <3 x float> %48, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %50 = fadd fast <3 x float> %47, %49
  %51 = shufflevector <3 x float> %45, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %52 = fmul fast <3 x float> %51, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %53 = fadd fast <3 x float> %50, %52
  %54 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %53) #25
  %55 = shufflevector <3 x half> %54, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %56 = fptrunc float %9 to half
  %57 = insertelement <3 x half> <half poison, half 0xH0000, half 0xH0000>, half %56, i64 0
  br label %58

58:                                               ; preds = %11, %7
  %59 = phi <3 x half> [ %57, %11 ], [ zeroinitializer, %7 ]
  %60 = phi <2 x half> [ %55, %11 ], [ zeroinitializer, %7 ]
  %61 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 10
  %62 = load float, ptr addrspace(1) %61, align 4, !tbaa !149
  %63 = tail call i1 @air.convert.u.i1.f.f32(float %62) #25
  br i1 %63, label %64, label %111

64:                                               ; preds = %58
  %65 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 13, i64 0
  %66 = load float, ptr addrspace(1) %65, align 4, !tbaa !98
  %67 = fptrunc float %66 to half
  %68 = insertelement <3 x half> undef, half %67, i64 0
  %69 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 13, i64 1
  %70 = load float, ptr addrspace(1) %69, align 4, !tbaa !98
  %71 = fptrunc float %70 to half
  %72 = insertelement <3 x half> %68, half %71, i64 1
  %73 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 13, i64 2
  %74 = load float, ptr addrspace(1) %73, align 4, !tbaa !98
  %75 = fptrunc float %74 to half
  %76 = insertelement <3 x half> %72, half %75, i64 2
  %77 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %76) #25
  %78 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %76) #25
  %79 = fmul fast <3 x half> %78, splat (half 0xH2CF4)
  %80 = fadd fast <3 x half> %78, splat (half 0xH2B0A)
  %81 = fmul fast <3 x half> %80, splat (half 0xH3B96)
  %82 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %81, <3 x half> splat (half 0xH40CD)) #25
  %83 = fcmp fast ogt <3 x half> %78, splat (half 0xH292D)
  %84 = select fast <3 x i1> %83, <3 x half> %82, <3 x half> %79
  %85 = fmul fast <3 x half> %84, %77
  %86 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %85) #25
  %87 = shufflevector <3 x float> %86, <3 x float> poison, <3 x i32> zeroinitializer
  %88 = fmul fast <3 x float> %87, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %89 = shufflevector <3 x float> %86, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %90 = fmul fast <3 x float> %89, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %91 = fadd fast <3 x float> %88, %90
  %92 = shufflevector <3 x float> %86, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %93 = fmul fast <3 x float> %92, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %94 = fadd fast <3 x float> %91, %93
  %95 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %94) #25
  %96 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %94) #25
  %97 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %96, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %98 = fmul fast <3 x float> %97, %95
  %99 = shufflevector <3 x float> %98, <3 x float> poison, <3 x i32> zeroinitializer
  %100 = fmul fast <3 x float> %99, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %101 = shufflevector <3 x float> %98, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %102 = fmul fast <3 x float> %101, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %103 = fadd fast <3 x float> %100, %102
  %104 = shufflevector <3 x float> %98, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %105 = fmul fast <3 x float> %104, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %106 = fadd fast <3 x float> %103, %105
  %107 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %106) #25
  %108 = shufflevector <3 x half> %107, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %109 = fptrunc float %62 to half
  %110 = insertelement <3 x half> %59, half %109, i64 1
  br label %111

111:                                              ; preds = %64, %58
  %112 = phi <3 x half> [ %110, %64 ], [ %59, %58 ]
  %113 = phi <2 x half> [ %108, %64 ], [ zeroinitializer, %58 ]
  %114 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 11
  %115 = load float, ptr addrspace(1) %114, align 4, !tbaa !150
  %116 = tail call i1 @air.convert.u.i1.f.f32(float %115) #25
  br i1 %116, label %117, label %164

117:                                              ; preds = %111
  %118 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 14, i64 0
  %119 = load float, ptr addrspace(1) %118, align 4, !tbaa !98
  %120 = fptrunc float %119 to half
  %121 = insertelement <3 x half> undef, half %120, i64 0
  %122 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 14, i64 1
  %123 = load float, ptr addrspace(1) %122, align 4, !tbaa !98
  %124 = fptrunc float %123 to half
  %125 = insertelement <3 x half> %121, half %124, i64 1
  %126 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 14, i64 2
  %127 = load float, ptr addrspace(1) %126, align 4, !tbaa !98
  %128 = fptrunc float %127 to half
  %129 = insertelement <3 x half> %125, half %128, i64 2
  %130 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %129) #25
  %131 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %129) #25
  %132 = fmul fast <3 x half> %131, splat (half 0xH2CF4)
  %133 = fadd fast <3 x half> %131, splat (half 0xH2B0A)
  %134 = fmul fast <3 x half> %133, splat (half 0xH3B96)
  %135 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %134, <3 x half> splat (half 0xH40CD)) #25
  %136 = fcmp fast ogt <3 x half> %131, splat (half 0xH292D)
  %137 = select fast <3 x i1> %136, <3 x half> %135, <3 x half> %132
  %138 = fmul fast <3 x half> %137, %130
  %139 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %138) #25
  %140 = shufflevector <3 x float> %139, <3 x float> poison, <3 x i32> zeroinitializer
  %141 = fmul fast <3 x float> %140, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %142 = shufflevector <3 x float> %139, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %143 = fmul fast <3 x float> %142, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %144 = fadd fast <3 x float> %141, %143
  %145 = shufflevector <3 x float> %139, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %146 = fmul fast <3 x float> %145, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %147 = fadd fast <3 x float> %144, %146
  %148 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %147) #25
  %149 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %147) #25
  %150 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %149, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %151 = fmul fast <3 x float> %150, %148
  %152 = shufflevector <3 x float> %151, <3 x float> poison, <3 x i32> zeroinitializer
  %153 = fmul fast <3 x float> %152, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %154 = shufflevector <3 x float> %151, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %155 = fmul fast <3 x float> %154, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %156 = fadd fast <3 x float> %153, %155
  %157 = shufflevector <3 x float> %151, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %158 = fmul fast <3 x float> %157, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %159 = fadd fast <3 x float> %156, %158
  %160 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %159) #25
  %161 = shufflevector <3 x half> %160, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %162 = fptrunc float %115 to half
  %163 = insertelement <3 x half> %112, half %162, i64 2
  br label %164

164:                                              ; preds = %117, %111
  %165 = phi <3 x half> [ %163, %117 ], [ %112, %111 ]
  %166 = phi <2 x half> [ %161, %117 ], [ zeroinitializer, %111 ]
  %167 = tail call fast fastcc <3 x half> @_Z20selectiveColorFilterDv3_DhDhDhDhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEEDv2_DhS5_S5_S_Dh(<3 x half> noundef %0, half noundef %3, half noundef %4, half noundef %5, ptr addrspace(1) %2, <2 x half> noundef %60, <2 x half> noundef %113, <2 x half> noundef %166, <3 x half> noundef %165, half noundef %6) #29
  ret <3 x half> %167
}

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(read)
define internal fastcc <3 x half> @_Z20selectiveColorFilterDv3_DhDhDhDhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEEDv2_DhS5_S5_S_Dh(<3 x half> noundef %0, half noundef %1, half noundef %2, half noundef %3, ptr addrspace(1) %4, <2 x half> noundef %5, <2 x half> noundef %6, <2 x half> noundef %7, <3 x half> noundef %8, half noundef %9) unnamed_addr #16 {
  %11 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %12 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %11) #25
  %13 = shufflevector <3 x float> %12, <3 x float> poison, <3 x i32> zeroinitializer
  %14 = fmul fast <3 x float> %13, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %15 = shufflevector <3 x float> %12, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %16 = fmul fast <3 x float> %15, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %17 = fadd fast <3 x float> %14, %16
  %18 = shufflevector <3 x float> %12, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %19 = fmul fast <3 x float> %18, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %20 = fadd fast <3 x float> %17, %19
  %21 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %20) #25
  %22 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %20) #25
  %23 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %22, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %24 = fmul fast <3 x float> %23, %21
  %25 = shufflevector <3 x float> %24, <3 x float> poison, <3 x i32> zeroinitializer
  %26 = fmul fast <3 x float> %25, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %27 = shufflevector <3 x float> %24, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %28 = fmul fast <3 x float> %27, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %29 = fadd fast <3 x float> %26, %28
  %30 = shufflevector <3 x float> %24, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %31 = fmul fast <3 x float> %30, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %32 = fadd fast <3 x float> %29, %31
  %33 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %32) #25
  %34 = extractelement <3 x half> %33, i64 2
  %35 = fcmp fast une half %34, 0xH0000
  %36 = extractelement <3 x half> %33, i64 1
  %37 = fcmp fast une half %36, 0xH0000
  %38 = select i1 %35, i1 true, i1 %37
  br i1 %38, label %39, label %41

39:                                               ; preds = %10
  %40 = tail call fast half @air.atan2.f16(half %34, half %36) #25
  br label %41

41:                                               ; preds = %39, %10
  %42 = phi fast half [ %40, %39 ], [ 0xH0000, %10 ]
  %43 = shufflevector <3 x half> %33, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %44 = tail call fast half @air.dot.v2f16(<2 x half> %43, <2 x half> %43) #25
  %45 = tail call fast half @air.sqrt.f16(half %44) #25
  %46 = fpext half %42 to float
  %47 = fmul fast float %46, 0x404C9178A0000000
  %48 = fadd fast float %47, 1.795000e+02
  %49 = fptrunc float %48 to half
  %50 = tail call fast half @air.clamp.f16(half %49, half 0xH0000, half 0xH5D9C) #25
  %51 = fadd fast half %50, 0xH3800
  %52 = fpext half %51 to float
  %53 = insertelement <2 x float> undef, float %52, i64 0
  %54 = insertelement <2 x float> %53, float 5.000000e-01, i64 1
  %55 = fmul fast <2 x float> %54, <float 0x3F66C16C20000000, float 2.500000e-01>
  %56 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %4, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %55, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %57 = extractvalue { <4 x half>, i8 } %56, 0
  %58 = insertelement <2 x float> %53, float 1.500000e+00, i64 1
  %59 = fmul fast <2 x float> %58, <float 0x3F66C16C20000000, float 2.500000e-01>
  %60 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %4, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %59, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %61 = extractvalue { <4 x half>, i8 } %60, 0
  %62 = insertelement <2 x float> %53, float 2.500000e+00, i64 1
  %63 = fmul fast <2 x float> %62, <float 0x3F66C16C20000000, float 2.500000e-01>
  %64 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %4, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %63, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %65 = extractvalue { <4 x half>, i8 } %64, 0
  %66 = insertelement <2 x float> %53, float 3.500000e+00, i64 1
  %67 = fmul fast <2 x float> %66, <float 0x3F66C16C20000000, float 2.500000e-01>
  %68 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %4, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %67, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %69 = extractvalue { <4 x half>, i8 } %68, 0
  %70 = extractelement <4 x half> %57, i64 1
  %71 = fadd fast half %70, 0xH3C00
  %72 = extractelement <4 x half> %61, i64 1
  %73 = fadd fast half %72, 0xH3C00
  %74 = extractelement <4 x half> %65, i64 1
  %75 = fadd fast half %74, 0xH3C00
  %76 = extractelement <4 x half> %69, i64 1
  %77 = fadd fast half %76, 0xH3C00
  %78 = tail call fast half @air.mix.f16(half %71, half %77, half %3) #25
  %79 = tail call fast half @air.mix.f16(half %73, half %75, half %2) #25
  %80 = tail call fast half @air.mix.f16(half %78, half %79, half %1) #25
  %81 = fcmp fast ogt half %80, 0xH3C00
  br i1 %81, label %84, label %82

82:                                               ; preds = %41
  %83 = extractelement <3 x half> %33, i64 0
  br label %96

84:                                               ; preds = %41
  %85 = fmul fast half %45, 0xH4900
  %86 = tail call fast half @air.clamp.f16(half %85, half 0xH0000, half 0xH3C00) #25
  %87 = fmul fast half %86, 0xH4000
  %88 = fsub fast half 0xH4200, %87
  %89 = extractelement <3 x half> %33, i64 0
  %90 = fmul fast half %89, %89
  %91 = fsub fast half 0xH3C00, %90
  %92 = fmul fast half %86, %86
  %93 = fmul fast half %92, %91
  %94 = fmul fast half %93, %88
  %95 = tail call fast half @air.mix.f16(half %80, half 0xH3C00, half %94) #25
  br label %96

96:                                               ; preds = %84, %82
  %97 = phi half [ %83, %82 ], [ %89, %84 ]
  %98 = phi fast half [ %80, %82 ], [ %95, %84 ]
  %99 = extractelement <4 x half> %57, i64 2
  %100 = fadd fast half %99, 0xH3C00
  %101 = extractelement <4 x half> %69, i64 2
  %102 = fadd fast half %101, 0xH3C00
  %103 = tail call fast half @air.mix.f16(half %100, half %102, half %3) #25
  %104 = extractelement <4 x half> %61, i64 2
  %105 = fadd fast half %104, 0xH3C00
  %106 = extractelement <4 x half> %65, i64 2
  %107 = fadd fast half %106, 0xH3C00
  %108 = tail call fast half @air.mix.f16(half %105, half %107, half %2) #25
  %109 = tail call fast half @air.mix.f16(half %103, half %108, half %1) #25
  %110 = extractelement <4 x half> %57, i64 0
  %111 = extractelement <4 x half> %69, i64 0
  %112 = tail call fast half @air.mix.f16(half %110, half %111, half %3) #25
  %113 = extractelement <4 x half> %61, i64 0
  %114 = extractelement <4 x half> %65, i64 0
  %115 = tail call fast half @air.mix.f16(half %113, half %114, half %2) #25
  %116 = tail call fast half @air.mix.f16(half %112, half %115, half %1) #25
  %117 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %118 = fadd fast <3 x half> %117, splat (half 0xHBC00)
  %119 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %120 = fmul fast half %98, %45
  %121 = fadd fast half %116, %42
  %122 = tail call fast half @air.clamp.f16(half %120, half 0xHB99A, half 0xH399A) #25
  %123 = tail call fast half @air.mix.f16(half 0xH3C00, half %109, half %122) #25
  %124 = fmul fast half %123, %97
  %125 = insertelement <3 x half> poison, half %124, i64 0
  %126 = tail call fast half @air.cos.f16(half %121) #25
  %127 = fmul fast half %126, %120
  %128 = insertelement <3 x half> %125, half %127, i64 1
  %129 = tail call fast half @air.sin.f16(half %121) #25
  %130 = fmul fast half %129, %120
  %131 = insertelement <3 x half> %128, half %130, i64 2
  %132 = extractelement <3 x half> %8, i64 2
  %133 = fpext half %132 to float
  %134 = fpext half %97 to float
  %135 = fadd fast float %134, -1.000000e+00
  %136 = fmul fast float %135, %135
  %137 = fmul fast float %136, -1.600000e+01
  %138 = tail call fast float @air.fast_exp.f32(float %137) #25
  %139 = fmul fast float %138, %133
  %140 = fptrunc float %139 to half
  %141 = extractelement <3 x half> %8, i64 1
  %142 = fpext half %141 to float
  %143 = fadd fast float %134, -5.000000e-01
  %144 = fmul fast float %143, %143
  %145 = fmul fast float %144, -1.600000e+01
  %146 = tail call fast float @air.fast_exp.f32(float %145) #25
  %147 = fmul fast float %146, %142
  %148 = fptrunc float %147 to half
  %149 = extractelement <3 x half> %8, i64 0
  %150 = fpext half %149 to float
  %151 = fneg fast half %97
  %152 = fmul fast half %97, %151
  %153 = fpext half %152 to float
  %154 = fmul fast float %153, 1.600000e+01
  %155 = tail call fast float @air.fast_exp.f32(float %154) #25
  %156 = fmul fast float %155, %150
  %157 = fptrunc float %156 to half
  %158 = shufflevector <3 x half> %131, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %159 = fadd fast <2 x half> %158, %5
  %160 = insertelement <2 x half> poison, half %157, i64 0
  %161 = shufflevector <2 x half> %160, <2 x half> poison, <2 x i32> zeroinitializer
  %162 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %158, <2 x half> %159, <2 x half> %161) #25
  %163 = fadd fast <2 x half> %162, %6
  %164 = insertelement <2 x half> poison, half %148, i64 0
  %165 = shufflevector <2 x half> %164, <2 x half> poison, <2 x i32> zeroinitializer
  %166 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %162, <2 x half> %163, <2 x half> %165) #25
  %167 = fadd fast <2 x half> %166, %7
  %168 = insertelement <2 x half> poison, half %140, i64 0
  %169 = shufflevector <2 x half> %168, <2 x half> poison, <2 x i32> zeroinitializer
  %170 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %166, <2 x half> %167, <2 x half> %169) #25
  %171 = shufflevector <2 x half> %170, <2 x half> poison, <3 x i32> <i32 0, i32 1, i32 poison>
  %172 = shufflevector <3 x half> %125, <3 x half> %171, <3 x i32> <i32 0, i32 3, i32 4>
  %173 = insertelement <3 x half> poison, half %9, i64 0
  %174 = shufflevector <3 x half> %173, <3 x half> poison, <3 x i32> zeroinitializer
  %175 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %131, <3 x half> %172, <3 x half> %174) #25
  %176 = insertelement <3 x half> poison, half %1, i64 0
  %177 = shufflevector <3 x half> %176, <3 x half> poison, <3 x i32> zeroinitializer
  %178 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %172, <3 x half> %175, <3 x half> %177) #25
  %179 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %178) #25
  %180 = shufflevector <3 x float> %179, <3 x float> poison, <3 x i32> zeroinitializer
  %181 = shufflevector <3 x float> %179, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %182 = fmul fast <3 x float> %181, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %183 = fadd fast <3 x float> %182, %180
  %184 = shufflevector <3 x float> %179, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %185 = fmul fast <3 x float> %184, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %186 = fadd fast <3 x float> %183, %185
  %187 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %186) #25
  %188 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %186) #25
  %189 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %188, <3 x float> splat (float 0x40029ACA60000000)) #25
  %190 = fmul fast <3 x float> %189, %187
  %191 = shufflevector <3 x float> %190, <3 x float> poison, <3 x i32> zeroinitializer
  %192 = fmul fast <3 x float> %191, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %193 = shufflevector <3 x float> %190, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %194 = fmul fast <3 x float> %193, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %195 = fadd fast <3 x float> %192, %194
  %196 = shufflevector <3 x float> %190, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %197 = fmul fast <3 x float> %196, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %198 = fadd fast <3 x float> %195, %197
  %199 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %198) #25
  %200 = extractelement <4 x half> %57, i64 3
  %201 = fadd fast half %200, 0xH3C00
  %202 = extractelement <4 x half> %61, i64 3
  %203 = fadd fast half %202, 0xH3C00
  %204 = extractelement <4 x half> %65, i64 3
  %205 = fadd fast half %204, 0xH3C00
  %206 = extractelement <4 x half> %69, i64 3
  %207 = fadd fast half %206, 0xH3C00
  %208 = tail call fast half @air.mix.f16(half %201, half %207, half %3) #25
  %209 = tail call fast half @air.mix.f16(half %203, half %205, half %2) #25
  %210 = tail call fast half @air.mix.f16(half %208, half %209, half %1) #25
  %211 = insertelement <3 x half> poison, half %210, i64 0
  %212 = shufflevector <3 x half> %211, <3 x half> poison, <3 x i32> zeroinitializer
  %213 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %199, <3 x half> %212) #25
  %214 = tail call fast half @air.sqrt.f16(half %120) #25
  %215 = fsub fast half 0xH2E66, %214
  %216 = fneg fast half %214
  %217 = fdiv fast half %215, %216
  %218 = tail call fast half @air.clamp.f16(half %217, half 0xH0000, half 0xH3C00) #25
  %219 = fmul fast half %218, %218
  %220 = fmul fast half %218, 0xH4000
  %221 = fsub fast half 0xH4200, %220
  %222 = tail call fast half @air.sqrt.f16(half %97) #25
  %223 = fmul fast half %219, %222
  %224 = fmul fast half %223, %221
  %225 = insertelement <3 x half> poison, half %224, i64 0
  %226 = shufflevector <3 x half> %225, <3 x half> poison, <3 x i32> zeroinitializer
  %227 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %199, <3 x half> %213, <3 x half> %226) #25
  %228 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %227) #25
  %229 = fadd fast <3 x half> %118, %119
  %230 = fadd fast <3 x half> %229, %228
  ret <3 x half> %230
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <2 x half> @air.mix.v2f16(<2 x half>, <2 x half>, <2 x half>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.sin.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.cos.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i1 @air.convert.u.i1.f.f32(float) local_unnamed_addr #0

; Function Attrs: convergent mustprogress nofree nosync nounwind willreturn memory(argmem: read)
define internal fastcc <3 x half> @_Z27renderWarmthCastAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsDh(<3 x half> noundef %0, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(136) %1, half noundef %2) unnamed_addr #17 {
  %4 = alloca %"struct.metal::matrix.194", align 8
  %5 = bitcast ptr %4 to ptr
  call void @llvm.lifetime.start.p0(ptr %4)
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 8 dereferenceable(24) %5, i8 0, i64 24, i1 false)
  br label %16

6:                                                ; preds = %16
  %7 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 0
  %8 = load float, ptr addrspace(1) %7, align 4, !tbaa !151
  %9 = fmul fast float %8, 5.000000e-01
  %10 = fadd fast float %9, 5.000000e-01
  %11 = fptrunc float %10 to half
  %12 = fpext half %11 to float
  %13 = fadd fast float %12, -5.000000e-01
  %14 = tail call fast float @air.fast_fabs.f32(float %13) #25
  %15 = fcmp fast olt float %14, 0x3EE4F8B580000000
  br i1 %15, label %85, label %36

16:                                               ; preds = %16, %3
  %17 = phi i32 [ 0, %3 ], [ %34, %16 ]
  %18 = zext i32 %17 to i64
  %19 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 6, i64 %18
  %20 = load float, ptr addrspace(1) %19, align 4, !tbaa !98
  %21 = fptrunc float %20 to half
  %22 = insertelement <3 x half> undef, half %21, i64 0
  %23 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 7, i64 %18
  %24 = load float, ptr addrspace(1) %23, align 4, !tbaa !98
  %25 = fmul fast float %24, %24
  %26 = fmul fast float %25, 0x3EF02E85C0000000
  %27 = fptrunc float %26 to half
  %28 = insertelement <3 x half> %22, half %27, i64 1
  %29 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 8, i64 %18
  %30 = load float, ptr addrspace(1) %29, align 4, !tbaa !98
  %31 = fptrunc float %30 to half
  %32 = insertelement <3 x half> %28, half %31, i64 2
  %33 = getelementptr inbounds %"struct.metal::matrix.194", ptr %4, i64 0, i32 0, i64 %18
  store <3 x half> %32, ptr %33, align 8, !tbaa !152
  %34 = add nuw nsw i32 %17, 1
  %35 = icmp eq i32 %34, 3
  br i1 %35, label %6, label %16, !llvm.loop !154

36:                                               ; preds = %6
  %37 = getelementptr inbounds %"struct.metal::matrix.194", ptr %4, i64 0, i32 0, i64 0
  %38 = load <3 x half>, ptr %37, align 8, !tbaa.struct !156
  %39 = getelementptr inbounds %"struct.metal::matrix.194", ptr %4, i64 0, i32 0, i64 1
  %40 = load <3 x half>, ptr %39, align 8, !tbaa.struct !157
  %41 = getelementptr inbounds %"struct.metal::matrix.194", ptr %4, i64 0, i32 0, i64 2
  %42 = load <3 x half>, ptr %41, align 8, !tbaa.struct !158
  %43 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 2
  %44 = load float, ptr addrspace(1) %43, align 4, !tbaa !159
  %45 = fptrunc float %44 to half
  %46 = fsub fast half 0xH3C00, %11
  %47 = fpext half %46 to float
  %48 = fsub fast float %12, %47
  %49 = fmul fast float %48, 0x3FC99999A0000000
  %50 = fptrunc float %49 to half
  %51 = fmul fast float %12, 0x3F8EB851E0000000
  %52 = fmul fast float %47, 0x3FA99999A0000000
  %53 = fsub fast float %52, %51
  %54 = fptrunc float %53 to half
  %55 = fmul fast float %12, 0x3FA1EB8520000000
  %56 = fadd fast float %52, %55
  %57 = fptrunc float %56 to half
  %58 = tail call fast half @air.fabs.f16(half %45) #25
  %59 = fpext half %58 to float
  %60 = fcmp fast olt float %59, 0x3EE4F8B580000000
  br i1 %60, label %73, label %61

61:                                               ; preds = %36
  %62 = fmul fast half %45, 0xH4248
  %63 = tail call fast half @air.cos.f16(half %62) #25
  %64 = fmul fast half %63, %50
  %65 = tail call fast half @air.sin.f16(half %62) #25
  %66 = fmul fast half %65, %54
  %67 = fsub fast half %64, %66
  %68 = fmul fast half %67, %65
  %69 = fmul fast half %63, %54
  %70 = fadd fast half %68, %69
  %71 = fmul fast half %63, %57
  %72 = fadd fast half %68, %71
  br label %73

73:                                               ; preds = %61, %36
  %74 = phi half [ %57, %36 ], [ %72, %61 ]
  %75 = phi half [ %54, %36 ], [ %70, %61 ]
  %76 = phi half [ %50, %36 ], [ %67, %61 ]
  %77 = fcmp fast ogt half %11, 0xH3800
  %78 = select i1 %77, half 0xH3548, half 0xH3800
  %79 = insertelement <4 x half> undef, half %76, i64 0
  %80 = insertelement <4 x half> %79, half %75, i64 1
  %81 = insertelement <4 x half> %80, half %74, i64 2
  %82 = insertelement <4 x half> %81, half %78, i64 3
  %83 = tail call fast fastcc <3 x half> @_Z17protectMaskFilterDv3_DhS_S_S_b(<3 x half> noundef %0, <3 x half> noundef %38, <3 x half> noundef %40, <3 x half> noundef %42, i1 noundef zeroext false) #30
  %84 = tail call fast fastcc <3 x half> @_Z12warmthFilterDv3_DhS_Dv4_Dh(<3 x half> noundef %0, <3 x half> noundef %83, <4 x half> noundef %82) #30
  br label %85

85:                                               ; preds = %73, %6
  %86 = phi <3 x half> [ %0, %6 ], [ %84, %73 ]
  %87 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 1
  %88 = load float, ptr addrspace(1) %87, align 4, !tbaa !160
  %89 = fmul fast float %88, 5.000000e-01
  %90 = fadd fast float %89, 5.000000e-01
  %91 = fptrunc float %90 to half
  %92 = fpext half %91 to float
  %93 = fadd fast float %92, -5.000000e-01
  %94 = tail call fast float @air.fast_fabs.f32(float %93) #25
  %95 = fcmp fast olt float %94, 0x3EE4F8B580000000
  br i1 %95, label %110, label %96

96:                                               ; preds = %85
  %97 = getelementptr inbounds %"struct.metal::matrix.194", ptr %4, i64 0, i32 0, i64 0
  %98 = load <3 x half>, ptr %97, align 8, !tbaa.struct !156
  %99 = getelementptr inbounds %"struct.metal::matrix.194", ptr %4, i64 0, i32 0, i64 1
  %100 = load <3 x half>, ptr %99, align 8, !tbaa.struct !157
  %101 = getelementptr inbounds %"struct.metal::matrix.194", ptr %4, i64 0, i32 0, i64 2
  %102 = load <3 x half>, ptr %101, align 8, !tbaa.struct !158
  %103 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 3
  %104 = load float, ptr addrspace(1) %103, align 4, !tbaa !161
  %105 = fptrunc float %104 to half
  %106 = insertvalue [3 x <3 x half>] poison, <3 x half> %98, 0
  %107 = insertvalue [3 x <3 x half>] %106, <3 x half> %100, 1
  %108 = insertvalue [3 x <3 x half>] %107, <3 x half> %102, 2
  %109 = tail call fast fastcc <3 x half> @_Z29whiteBalanceFilterAdjustmentsDv3_DhN5metal6matrixIDhLi3ELi3EvEERU9MTLdevice18SSRCastAdjustmentsDhDh(<3 x half> noundef %0, [3 x <3 x half>] %108, ptr addrspace(1) align 4 undef, half noundef %91, half noundef %105) #29
  br label %110

110:                                              ; preds = %96, %85
  %111 = phi <3 x half> [ %0, %85 ], [ %109, %96 ]
  %112 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 4
  %113 = load float, ptr addrspace(1) %112, align 4, !tbaa !162
  %114 = fmul fast float %113, 5.000000e-01
  %115 = fadd fast float %114, 5.000000e-01
  %116 = fptrunc float %115 to half
  %117 = fpext half %116 to float
  %118 = fadd fast float %117, -5.000000e-01
  %119 = tail call fast float @air.fast_fabs.f32(float %118) #25
  %120 = fcmp fast olt float %119, 0x3EE4F8B580000000
  br i1 %120, label %170, label %121

121:                                              ; preds = %110
  %122 = getelementptr inbounds %"struct.metal::matrix.194", ptr %4, i64 0, i32 0, i64 0
  %123 = load <3 x half>, ptr %122, align 8, !tbaa.struct !156
  %124 = getelementptr inbounds %"struct.metal::matrix.194", ptr %4, i64 0, i32 0, i64 1
  %125 = load <3 x half>, ptr %124, align 8, !tbaa.struct !157
  %126 = getelementptr inbounds %"struct.metal::matrix.194", ptr %4, i64 0, i32 0, i64 2
  %127 = load <3 x half>, ptr %126, align 8, !tbaa.struct !158
  %128 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %1, i64 0, i32 5
  %129 = load float, ptr addrspace(1) %128, align 4, !tbaa !163
  %130 = fptrunc float %129 to half
  %131 = fsub fast half 0xH3C00, %116
  %132 = fpext half %131 to float
  %133 = fsub fast float %117, %132
  %134 = fmul fast float %133, 0x3FC99999A0000000
  %135 = fptrunc float %134 to half
  %136 = fmul fast float %117, 0x3F8EB851E0000000
  %137 = fmul fast float %132, 0x3FA99999A0000000
  %138 = fsub fast float %137, %136
  %139 = fptrunc float %138 to half
  %140 = fmul fast float %117, 0x3FA1EB8520000000
  %141 = fadd fast float %137, %140
  %142 = fptrunc float %141 to half
  %143 = tail call fast half @air.fabs.f16(half %130) #25
  %144 = fpext half %143 to float
  %145 = fcmp fast olt float %144, 0x3EE4F8B580000000
  br i1 %145, label %158, label %146

146:                                              ; preds = %121
  %147 = fmul fast half %130, 0xH4248
  %148 = tail call fast half @air.cos.f16(half %147) #25
  %149 = fmul fast half %148, %135
  %150 = tail call fast half @air.sin.f16(half %147) #25
  %151 = fmul fast half %150, %139
  %152 = fsub fast half %149, %151
  %153 = fmul fast half %152, %150
  %154 = fmul fast half %148, %139
  %155 = fadd fast half %153, %154
  %156 = fmul fast half %148, %142
  %157 = fadd fast half %153, %156
  br label %158

158:                                              ; preds = %146, %121
  %159 = phi half [ %142, %121 ], [ %157, %146 ]
  %160 = phi half [ %139, %121 ], [ %155, %146 ]
  %161 = phi half [ %135, %121 ], [ %152, %146 ]
  %162 = fcmp fast ogt half %116, 0xH3800
  %163 = select i1 %162, half 0xH3548, half 0xH3800
  %164 = insertelement <4 x half> undef, half %161, i64 0
  %165 = insertelement <4 x half> %164, half %160, i64 1
  %166 = insertelement <4 x half> %165, half %159, i64 2
  %167 = insertelement <4 x half> %166, half %163, i64 3
  %168 = tail call fast fastcc <3 x half> @_Z17protectMaskFilterDv3_DhS_S_S_b(<3 x half> noundef %111, <3 x half> noundef %123, <3 x half> noundef %125, <3 x half> noundef %127, i1 noundef zeroext false) #30
  %169 = tail call fast fastcc <3 x half> @_Z12warmthFilterDv3_DhS_Dv4_Dh(<3 x half> noundef %111, <3 x half> noundef %168, <4 x half> noundef %167) #30
  br label %170

170:                                              ; preds = %158, %110
  %171 = phi <3 x half> [ %111, %110 ], [ %169, %158 ]
  %172 = insertelement <3 x half> poison, half %2, i64 0
  %173 = shufflevector <3 x half> %172, <3 x half> poison, <3 x i32> zeroinitializer
  %174 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %86, <3 x half> %171, <3 x half> %173) #25
  call void @llvm.lifetime.end.p0(ptr %4)
  ret <3 x half> %174
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z12warmthFilterDv3_DhS_Dv4_Dh(<3 x half> noundef %0, <3 x half> noundef %1, <4 x half> noundef %2) unnamed_addr #18 {
  %4 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %5 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %6 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %7 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %6, <3 x half> splat (half 0xH3400)) #25
  %8 = shufflevector <3 x half> %7, <3 x half> poison, <3 x i32> zeroinitializer
  %9 = fmul fast <3 x half> %8, <half 0xH34C9, half 0xH38C4, half 0xH32C4>
  %10 = shufflevector <3 x half> %7, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %11 = fmul fast <3 x half> %10, <half 0xH38B2, half 0xHB464, half 0xHB82E>
  %12 = fadd fast <3 x half> %9, %11
  %13 = shufflevector <3 x half> %7, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %14 = fmul fast <3 x half> %13, <half 0xH2F4C, half 0xHB524, half 0xH34FA>
  %15 = fadd fast <3 x half> %12, %14
  %16 = shufflevector <3 x half> %15, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %17 = tail call fast half @air.dot.v2f16(<2 x half> %16, <2 x half> %16) #25
  %18 = fmul fast half %17, 0xH4400
  %19 = tail call fast half @air.fmin.f16(half 0xH3C00, half %18) #25
  %20 = fadd fast half %19, 0xH2666
  %21 = fmul fast half %20, 0xH3BCD
  %22 = tail call fast half @air.clamp.f16(half %21, half 0xH0000, half 0xH3C00) #25
  %23 = fmul fast half %22, %22
  %24 = fmul fast half %22, 0xH4000
  %25 = fsub fast half 0xH4200, %24
  %26 = fmul fast half %23, %25
  %27 = extractelement <3 x half> %15, i64 0
  %28 = tail call fast half @air.fmin.f16(half 0xH3C00, half %27) #25
  %29 = fadd fast half %28, 0xHB266
  %30 = fmul fast half %29, 0xH4500
  %31 = tail call fast half @air.clamp.f16(half %30, half 0xH0000, half 0xH3C00) #25
  %32 = fmul fast half %31, %31
  %33 = fmul fast half %31, 0xH4000
  %34 = fsub fast half 0xH4200, %33
  %35 = fmul fast half %32, %34
  %36 = shufflevector <4 x half> %2, <4 x half> poison, <2 x i32> <i32 0, i32 1>
  %37 = shufflevector <4 x half> %2, <4 x half> undef, <2 x i32> <i32 3, i32 3>
  %38 = shufflevector <4 x half> %2, <4 x half> poison, <2 x i32> <i32 0, i32 2>
  %39 = fmul fast <2 x half> %37, %38
  %40 = extractelement <3 x half> %1, i64 0
  %41 = shufflevector <3 x half> %1, <3 x half> undef, <2 x i32> zeroinitializer
  %42 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %36, <2 x half> %39, <2 x half> %41) #25
  %43 = tail call fast half @air.pow.f16(half %26, half 0xH3266) #25
  %44 = insertelement <2 x half> poison, half %43, i64 0
  %45 = shufflevector <2 x half> %44, <2 x half> poison, <2 x i32> zeroinitializer
  %46 = fmul fast <2 x half> %45, %42
  %47 = fadd fast <2 x half> %46, %16
  %48 = extractelement <3 x half> %1, i64 1
  %49 = fadd fast half %40, %48
  %50 = extractelement <3 x half> %1, i64 2
  %51 = fadd fast half %49, %50
  %52 = insertelement <2 x half> poison, half %51, i64 0
  %53 = shufflevector <2 x half> %52, <2 x half> poison, <2 x i32> zeroinitializer
  %54 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %47, <2 x half> %16, <2 x half> %53) #25
  %55 = shufflevector <2 x half> %54, <2 x half> poison, <3 x i32> <i32 0, i32 1, i32 poison>
  %56 = shufflevector <3 x half> %15, <3 x half> %55, <3 x i32> <i32 0, i32 3, i32 4>
  %57 = fsub fast half 0xH3C00, %35
  %58 = insertelement <3 x half> poison, half %57, i64 0
  %59 = shufflevector <3 x half> %58, <3 x half> poison, <3 x i32> zeroinitializer
  %60 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %56, <3 x half> %15, <3 x half> %59) #25
  %61 = shufflevector <3 x half> %60, <3 x half> poison, <3 x i32> zeroinitializer
  %62 = shufflevector <3 x half> %60, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %63 = fmul fast <3 x half> %62, <half 0xH3BA6, half 0xHB45B, half 0xHBC6E>
  %64 = fadd fast <3 x half> %63, %61
  %65 = shufflevector <3 x half> %60, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %66 = fmul fast <3 x half> %65, <half 0xH38F8, half 0xHB92E, half 0xH3ED2>
  %67 = fadd fast <3 x half> %64, %66
  %68 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %67, <3 x half> splat (half 0xH4400)) #25
  %69 = fadd fast <3 x half> %4, splat (half 0xHBC00)
  %70 = fadd fast <3 x half> %69, %5
  %71 = fadd fast <3 x half> %70, %68
  ret <3 x half> %71
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmin.f16(half, half) local_unnamed_addr #0

; Function Attrs: convergent mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z29whiteBalanceFilterAdjustmentsDv3_DhN5metal6matrixIDhLi3ELi3EvEERU9MTLdevice18SSRCastAdjustmentsDhDh(<3 x half> noundef %0, [3 x <3 x half>] %1, ptr addrspace(1) readnone align 4 captures(none) %2, half noundef %3, half noundef %4) unnamed_addr #19 {
  %6 = fpext half %3 to float
  %7 = fadd fast float %6, -5.000000e-01
  %8 = tail call fast float @air.fast_fabs.f32(float %7) #25
  %9 = fcmp fast olt float %8, 0x3EE4F8B580000000
  br i1 %9, label %28, label %10

10:                                               ; preds = %5
  %11 = fcmp fast olt half %3, 0xH3800
  br i1 %11, label %12, label %20

12:                                               ; preds = %10
  %13 = fmul fast half %3, 0xH4000
  %14 = fsub fast half 0xH3C00, %13
  %15 = fpext half %14 to float
  %16 = fmul fast float %15, 0xBFB99999A0000000
  %17 = fptrunc float %16 to half
  %18 = fmul fast float %15, 0xBFC872B020000000
  %19 = fptrunc float %18 to half
  br label %28

20:                                               ; preds = %10
  %21 = fmul fast float %7, 2.000000e+00
  %22 = fptrunc float %21 to half
  %23 = fpext half %22 to float
  %24 = fmul fast float %23, 0x3FC9FBE760000000
  %25 = fptrunc float %24 to half
  %26 = fmul fast float %23, 0x3FCB573EA0000000
  %27 = fptrunc float %26 to half
  br label %28

28:                                               ; preds = %20, %12, %5
  %29 = phi half [ 0xH0000, %5 ], [ %19, %12 ], [ %27, %20 ]
  %30 = phi half [ 0xH0000, %5 ], [ %17, %12 ], [ %25, %20 ]
  %31 = tail call fast half @air.fabs.f16(half %4) #25
  %32 = fpext half %31 to float
  %33 = fcmp fast olt float %32, 0x3EE4F8B580000000
  br i1 %33, label %44, label %34

34:                                               ; preds = %28
  %35 = fmul fast half %4, 0xHC248
  %36 = tail call fast half @air.cos.f16(half %35) #25
  %37 = fmul fast half %36, %30
  %38 = tail call fast half @air.sin.f16(half %35) #25
  %39 = fmul fast half %38, %29
  %40 = fsub fast half %37, %39
  %41 = fmul fast half %40, %38
  %42 = fmul fast half %36, %29
  %43 = fadd fast half %41, %42
  br label %44

44:                                               ; preds = %34, %28
  %45 = phi half [ %29, %28 ], [ %43, %34 ]
  %46 = phi half [ %30, %28 ], [ %40, %34 ]
  %47 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %0) #25
  %48 = shufflevector <3 x float> %47, <3 x float> poison, <3 x i32> zeroinitializer
  %49 = fmul fast <3 x float> %48, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %50 = shufflevector <3 x float> %47, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %51 = fmul fast <3 x float> %50, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %52 = fadd fast <3 x float> %49, %51
  %53 = shufflevector <3 x float> %47, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %54 = fmul fast <3 x float> %53, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %55 = fadd fast <3 x float> %52, %54
  %56 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %55) #25
  %57 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %55) #25
  %58 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %57, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %59 = fmul fast <3 x float> %58, %56
  %60 = shufflevector <3 x float> %59, <3 x float> poison, <3 x i32> zeroinitializer
  %61 = fmul fast <3 x float> %60, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %62 = shufflevector <3 x float> %59, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %63 = fmul fast <3 x float> %62, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %64 = fadd fast <3 x float> %61, %63
  %65 = shufflevector <3 x float> %59, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %66 = fmul fast <3 x float> %65, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %67 = fadd fast <3 x float> %64, %66
  %68 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %67) #25
  %69 = extractelement <3 x half> %68, i64 2
  %70 = fcmp fast une half %69, 0xH0000
  %71 = extractelement <3 x half> %68, i64 1
  %72 = fcmp fast une half %71, 0xH0000
  %73 = select i1 %70, i1 true, i1 %72
  br i1 %73, label %74, label %77

74:                                               ; preds = %44
  %75 = tail call fast half @air.atan2.f16(half %69, half %71) #25
  %76 = fadd fast half %75, 0xH3F9A
  br label %77

77:                                               ; preds = %74, %44
  %78 = phi half [ %76, %74 ], [ 0xH3F9A, %44 ]
  %79 = insertelement <4 x half> <half 0xH0000, half 0xH0000, half poison, half poison>, half %46, i64 2
  %80 = insertelement <4 x half> %79, half %45, i64 3
  %81 = fmul fast half %78, %78
  %82 = fmul fast half %81, 0xHBF1C
  %83 = tail call fast half @air.exp.f16(half %82) #25
  %84 = insertelement <3 x half> poison, half %83, i64 0
  %85 = shufflevector <3 x half> %84, <3 x half> poison, <3 x i32> zeroinitializer
  %86 = tail call fast fastcc <3 x half> @_Z18whiteBalanceFilterDv3_DhN5metal6matrixIDhLi3ELi3EvEES_Dv4_Dh(<3 x half> noundef %0, [3 x <3 x half>] %1, <3 x half> noundef %85, <4 x half> noundef %80) #28
  ret <3 x half> %86
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z18whiteBalanceFilterDv3_DhN5metal6matrixIDhLi3ELi3EvEES_Dv4_Dh(<3 x half> noundef %0, [3 x <3 x half>] %1, <3 x half> noundef %2, <4 x half> noundef %3) unnamed_addr #9 {
  %5 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %6 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %5) #25
  %7 = shufflevector <3 x float> %6, <3 x float> poison, <3 x i32> zeroinitializer
  %8 = fmul fast <3 x float> %7, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %9 = shufflevector <3 x float> %6, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %10 = fmul fast <3 x float> %9, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %11 = fadd fast <3 x float> %8, %10
  %12 = shufflevector <3 x float> %6, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %13 = fmul fast <3 x float> %12, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %14 = fadd fast <3 x float> %11, %13
  %15 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %14) #25
  %16 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %14) #25
  %17 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %16, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %18 = fmul fast <3 x float> %17, %15
  %19 = shufflevector <3 x float> %18, <3 x float> poison, <3 x i32> zeroinitializer
  %20 = fmul fast <3 x float> %19, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %21 = shufflevector <3 x float> %18, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %22 = fmul fast <3 x float> %21, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %23 = fadd fast <3 x float> %20, %22
  %24 = shufflevector <3 x float> %18, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %25 = fmul fast <3 x float> %24, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %26 = fadd fast <3 x float> %23, %25
  %27 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %26) #25
  %28 = extractelement <3 x half> %27, i64 2
  %29 = fcmp fast une half %28, 0xH0000
  %30 = extractelement <3 x half> %27, i64 1
  %31 = fcmp fast une half %30, 0xH0000
  %32 = select i1 %29, i1 true, i1 %31
  br i1 %32, label %33, label %35

33:                                               ; preds = %4
  %34 = tail call fast half @air.atan2.f16(half %28, half %30) #25
  br label %35

35:                                               ; preds = %33, %4
  %36 = phi fast half [ %34, %33 ], [ 0xH0000, %4 ]
  %37 = shufflevector <4 x half> %3, <4 x half> poison, <2 x i32> <i32 0, i32 1>
  %38 = shufflevector <4 x half> %3, <4 x half> poison, <2 x i32> <i32 2, i32 3>
  %39 = extractelement <3 x half> %27, i64 0
  %40 = fmul fast half %39, %39
  %41 = insertelement <2 x half> poison, half %40, i64 0
  %42 = shufflevector <2 x half> %41, <2 x half> poison, <2 x i32> zeroinitializer
  %43 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %37, <2 x half> %38, <2 x half> %42) #25
  %44 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %45 = fadd fast <3 x half> %44, splat (half 0xHBC00)
  %46 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %47 = extractvalue [3 x <3 x half>] %1, 2
  %48 = extractvalue [3 x <3 x half>] %1, 1
  %49 = extractvalue [3 x <3 x half>] %1, 0
  %50 = extractelement <3 x half> %49, i64 1
  %51 = tail call fast half @air.fmax.f16(half %50, half 0xH0001) #25
  %52 = extractelement <3 x half> %48, i64 1
  %53 = tail call fast half @air.fmax.f16(half %52, half 0xH0001) #25
  %54 = extractelement <3 x half> %47, i64 1
  %55 = tail call fast half @air.fmax.f16(half %54, half 0xH0001) #25
  %56 = extractelement <3 x half> %49, i64 2
  %57 = extractelement <3 x half> %49, i64 0
  %58 = fsub fast half %36, %57
  %59 = fneg fast half %58
  %60 = fmul fast half %58, %59
  %61 = fdiv fast half %60, %51
  %62 = tail call fast half @air.exp.f16(half %61) #25
  %63 = fmul fast half %62, %56
  %64 = extractelement <3 x half> %48, i64 2
  %65 = extractelement <3 x half> %48, i64 0
  %66 = fsub fast half %36, %65
  %67 = fneg fast half %66
  %68 = fmul fast half %66, %67
  %69 = fdiv fast half %68, %53
  %70 = tail call fast half @air.exp.f16(half %69) #25
  %71 = fmul fast half %70, %64
  %72 = extractelement <3 x half> %47, i64 2
  %73 = extractelement <3 x half> %47, i64 0
  %74 = fsub fast half %36, %73
  %75 = fneg fast half %74
  %76 = fmul fast half %74, %75
  %77 = fdiv fast half %76, %55
  %78 = tail call fast half @air.exp.f16(half %77) #25
  %79 = fmul fast half %78, %72
  %80 = fadd fast half %71, %63
  %81 = fadd fast half %80, %79
  %82 = insertelement <2 x half> poison, half %81, i64 0
  %83 = shufflevector <2 x half> %82, <2 x half> poison, <2 x i32> zeroinitializer
  %84 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %43, <2 x half> zeroinitializer, <2 x half> %83) #25
  %85 = shufflevector <3 x half> %27, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %86 = fadd fast <2 x half> %84, %85
  %87 = shufflevector <2 x half> %86, <2 x half> poison, <3 x i32> <i32 0, i32 1, i32 poison>
  %88 = shufflevector <3 x half> %27, <3 x half> %87, <3 x i32> <i32 0, i32 3, i32 4>
  %89 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %88) #25
  %90 = shufflevector <3 x float> %89, <3 x float> poison, <3 x i32> zeroinitializer
  %91 = shufflevector <3 x float> %89, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %92 = fmul fast <3 x float> %91, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %93 = fadd fast <3 x float> %92, %90
  %94 = shufflevector <3 x float> %89, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %95 = fmul fast <3 x float> %94, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %96 = fadd fast <3 x float> %93, %95
  %97 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %96) #25
  %98 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %96) #25
  %99 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %98, <3 x float> splat (float 0x40029ACA60000000)) #25
  %100 = fmul fast <3 x float> %99, %97
  %101 = shufflevector <3 x float> %100, <3 x float> poison, <3 x i32> zeroinitializer
  %102 = fmul fast <3 x float> %101, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %103 = shufflevector <3 x float> %100, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %104 = fmul fast <3 x float> %103, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %105 = fadd fast <3 x float> %102, %104
  %106 = shufflevector <3 x float> %100, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %107 = fmul fast <3 x float> %106, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %108 = fadd fast <3 x float> %105, %107
  %109 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %108) #25
  %110 = shufflevector <3 x half> %2, <3 x half> poison, <3 x i32> zeroinitializer
  %111 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %109, <3 x half> %5, <3 x half> %110) #25
  %112 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %111) #25
  %113 = fadd fast <3 x half> %45, %46
  %114 = fadd fast <3 x half> %113, %112
  ret <3 x half> %114
}

; Function Attrs: convergent mustprogress nofree nosync nounwind willreturn memory(argmem: read)
define internal fastcc <3 x half> @_Z29renderNeutralizingAdjustmentsDv3_DhbRU9MTLdevice18SSRCastAdjustmentsDhDhbRU9MTLdevice8SSRStats(<3 x half> noundef %0, i1 noundef zeroext %1, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(136) %2, half noundef %3, half noundef %4, i1 noundef zeroext %5, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(10640) %6) unnamed_addr #20 {
  br i1 %1, label %8, label %164

8:                                                ; preds = %7
  %9 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %6, i64 0, i32 1, i64 2, i32 4
  %10 = load float, ptr addrspace(1) %9, align 4, !tbaa !132
  %11 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %6, i64 0, i32 1, i64 3, i32 4
  %12 = load float, ptr addrspace(1) %11, align 4, !tbaa !132
  %13 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %6, i64 0, i32 1, i64 4, i32 4
  %14 = load float, ptr addrspace(1) %13, align 4, !tbaa !132
  %15 = fptrunc float %10 to half
  %16 = insertelement <3 x half> undef, half %15, i64 0
  %17 = fptrunc float %12 to half
  %18 = insertelement <3 x half> %16, half %17, i64 1
  %19 = fptrunc float %14 to half
  %20 = insertelement <3 x half> %18, half %19, i64 2
  %21 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %20) #25
  %22 = shufflevector <3 x float> %21, <3 x float> poison, <3 x i32> zeroinitializer
  %23 = fmul fast <3 x float> %22, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %24 = shufflevector <3 x float> %21, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %25 = fmul fast <3 x float> %24, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %26 = fadd fast <3 x float> %23, %25
  %27 = shufflevector <3 x float> %21, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %28 = fmul fast <3 x float> %27, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %29 = fadd fast <3 x float> %26, %28
  %30 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %29) #25
  %31 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %29) #25
  %32 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %31, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %33 = fmul fast <3 x float> %32, %30
  %34 = shufflevector <3 x float> %33, <3 x float> poison, <3 x i32> zeroinitializer
  %35 = fmul fast <3 x float> %34, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %36 = shufflevector <3 x float> %33, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %37 = fmul fast <3 x float> %36, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %38 = fadd fast <3 x float> %35, %37
  %39 = shufflevector <3 x float> %33, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %40 = fmul fast <3 x float> %39, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %41 = fadd fast <3 x float> %38, %40
  %42 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %41) #25
  %43 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %20) #25
  %44 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %20) #25
  %45 = fmul fast <3 x half> %44, splat (half 0xH4A76)
  %46 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %44, <3 x half> splat (half 0xH36AA)) #25
  %47 = fmul fast <3 x half> %46, splat (half 0xH3C38)
  %48 = fadd fast <3 x half> %47, splat (half 0xHAB0A)
  %49 = fcmp fast ogt <3 x half> %44, splat (half 0xH1A69)
  %50 = select fast <3 x i1> %49, <3 x half> %48, <3 x half> %45
  %51 = fmul fast <3 x half> %50, %43
  %52 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %51) #25
  %53 = shufflevector <3 x float> %52, <3 x float> poison, <3 x i32> zeroinitializer
  %54 = fmul fast <3 x float> %53, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %55 = shufflevector <3 x float> %52, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %56 = fmul fast <3 x float> %55, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %57 = fadd fast <3 x float> %54, %56
  %58 = shufflevector <3 x float> %52, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %59 = fmul fast <3 x float> %58, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %60 = fadd fast <3 x float> %57, %59
  %61 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %60) #25
  %62 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %60) #25
  %63 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %62, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %64 = fmul fast <3 x float> %63, %61
  %65 = shufflevector <3 x float> %64, <3 x float> poison, <3 x i32> zeroinitializer
  %66 = fmul fast <3 x float> %65, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %67 = shufflevector <3 x float> %64, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %68 = fmul fast <3 x float> %67, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %69 = fadd fast <3 x float> %66, %68
  %70 = shufflevector <3 x float> %64, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %71 = fmul fast <3 x float> %70, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %72 = fadd fast <3 x float> %69, %71
  %73 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %72) #25
  %74 = select fast i1 %5, half %3, half 0xH0000
  %75 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %2, i64 0, i32 15
  %76 = load float, ptr addrspace(1) %75, align 4, !tbaa !164
  %77 = tail call fast float @air.fast_fabs.f32(float %76) #25
  %78 = fcmp fast olt float %77, 0x3EE4F8B580000000
  br i1 %78, label %145, label %79

79:                                               ; preds = %8
  %80 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %2, i64 0, i32 16
  %81 = load float, ptr addrspace(1) %80, align 4, !tbaa !165
  %82 = tail call fast float @air.fast_fabs.f32(float %81) #25
  %83 = fcmp fast olt float %82, 0x3EE4F8B580000000
  br i1 %83, label %84, label %87

84:                                               ; preds = %79
  %85 = fptrunc float %76 to half
  %86 = tail call fast fastcc <3 x half> @_Z5deRedDv3_DhDhDhS_Dh(<3 x half> noundef %0, half noundef %74, half noundef %4, <3 x half> noundef %42, half noundef %85) #28
  br label %145

87:                                               ; preds = %79
  %88 = extractelement <3 x half> %73, i64 2
  %89 = fcmp fast une half %88, 0xH0000
  %90 = extractelement <3 x half> %73, i64 1
  %91 = fcmp fast une half %90, 0xH0000
  %92 = select i1 %89, i1 true, i1 %91
  br i1 %92, label %93, label %95

93:                                               ; preds = %87
  %94 = tail call fast half @air.atan2.f16(half %88, half %90) #25
  br label %95

95:                                               ; preds = %93, %87
  %96 = phi fast half [ %94, %93 ], [ 0xH0000, %87 ]
  %97 = fadd fast half %96, 0xH4648
  %98 = tail call fast half @air.sign.f16(half %96) #25
  %99 = fpext half %98 to float
  %100 = tail call i1 @air.convert.u.i1.f.f32(float %99) #25
  %101 = select fast i1 %100, half %97, half %96
  %102 = tail call fast half @air.fmod.f16(half %101, half 0xH4648) #25
  %103 = fpext half %102 to float
  %104 = fadd fast float %103, 0xBFD3333340000000
  %105 = tail call fast float @air.fast_fabs.f32(float %104) #25
  %106 = fadd fast float %105, -5.000000e-01
  %107 = fmul fast float %106, 0xC001C71C80000000
  %108 = tail call fast float @air.fast_clamp.f32(float %107, float 0.000000e+00, float 1.000000e+00) #25
  %109 = fmul fast float %108, 2.000000e+00
  %110 = fsub fast float 3.000000e+00, %109
  %111 = fmul fast float %108, %108
  %112 = fmul fast float %111, 5.000000e-01
  %113 = fmul fast float %112, %110
  %114 = fptrunc float %113 to half
  %115 = shufflevector <3 x half> %73, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %116 = tail call fast half @air.dot.v2f16(<2 x half> %115, <2 x half> %115) #25
  %117 = tail call fast half @air.sqrt.f16(half %116) #25
  %118 = fadd fast half %102, 0xHBA00
  %119 = fadd fast half %118, %114
  %120 = fmul fast half %119, 0xH44FF
  %121 = tail call fast half @air.clamp.f16(half %120, half 0xH0000, half 0xH3C00) #25
  %122 = fmul fast half %121, %121
  %123 = fmul fast half %121, 0xH4000
  %124 = fsub fast half 0xH4200, %123
  %125 = fmul fast half %122, %124
  %126 = fsub fast half 0xH3C00, %125
  %127 = fptrunc float %76 to half
  %128 = fptrunc float %81 to half
  %129 = tail call fast fastcc <3 x half> @_Z16deRedNeutralOnlyDv3_DhDhDhS_DhDhDh(<3 x half> noundef %0, half noundef %74, half undef, <3 x half> noundef %73, half noundef %127, half noundef %128, half noundef %126) #28
  %130 = fmul fast half %126, %114
  %131 = fadd fast half %130, %102
  %132 = fsub fast float 1.000000e+00, %81
  %133 = fpext half %117 to float
  %134 = fmul fast float %132, %133
  %135 = tail call fast half @air.cos.f16(half %131) #25
  %136 = fpext half %135 to float
  %137 = fmul fast float %134, %136
  %138 = fptrunc float %137 to half
  %139 = insertelement <3 x half> %73, half %138, i64 1
  %140 = tail call fast half @air.sin.f16(half %131) #25
  %141 = fpext half %140 to float
  %142 = fmul fast float %134, %141
  %143 = fptrunc float %142 to half
  %144 = insertelement <3 x half> %139, half %143, i64 2
  br label %145

145:                                              ; preds = %95, %84, %8
  %146 = phi <3 x half> [ %73, %8 ], [ %73, %84 ], [ %144, %95 ]
  %147 = phi <3 x half> [ %0, %8 ], [ %86, %84 ], [ %129, %95 ]
  %148 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %2, i64 0, i32 17
  %149 = load float, ptr addrspace(1) %148, align 4, !tbaa !166
  %150 = tail call fast float @air.fast_fabs.f32(float %149) #25
  %151 = fcmp fast olt float %150, 0x3EE4F8B580000000
  br i1 %151, label %155, label %152

152:                                              ; preds = %145
  %153 = fptrunc float %149 to half
  %154 = tail call fast fastcc <3 x half> @_Z8deYellowDv3_DhDhDhS_Dh(<3 x half> noundef %147, half noundef %4, half undef, <3 x half> noundef %146, half noundef %153) #28
  br label %155

155:                                              ; preds = %152, %145
  %156 = phi <3 x half> [ %147, %145 ], [ %154, %152 ]
  %157 = getelementptr inbounds %struct.SSRCastAdjustments.2409, ptr addrspace(1) %2, i64 0, i32 18
  %158 = load float, ptr addrspace(1) %157, align 4, !tbaa !167
  %159 = tail call fast float @air.fast_fabs.f32(float %158) #25
  %160 = fcmp fast olt float %159, 0x3EE4F8B580000000
  br i1 %160, label %164, label %161

161:                                              ; preds = %155
  %162 = fptrunc float %158 to half
  %163 = tail call fast fastcc <3 x half> @_Z16skinWarmthFilterDv3_DhDhDhS_DhDh(<3 x half> noundef %156, half noundef %4, half noundef %74, <3 x half> noundef %42, half noundef 0xH3C00, half noundef %162) #28
  br label %164

164:                                              ; preds = %161, %155, %7
  %165 = phi <3 x half> [ %0, %7 ], [ %156, %155 ], [ %163, %161 ]
  ret <3 x half> %165
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z16skinWarmthFilterDv3_DhDhDhS_DhDh(<3 x half> noundef %0, half noundef %1, half noundef %2, <3 x half> noundef %3, half noundef %4, half noundef %5) unnamed_addr #9 {
  %7 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %8 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %7) #25
  %9 = shufflevector <3 x float> %8, <3 x float> poison, <3 x i32> zeroinitializer
  %10 = fmul fast <3 x float> %9, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %11 = shufflevector <3 x float> %8, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %12 = fmul fast <3 x float> %11, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %13 = fadd fast <3 x float> %10, %12
  %14 = shufflevector <3 x float> %8, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %15 = fmul fast <3 x float> %14, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %16 = fadd fast <3 x float> %13, %15
  %17 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %16) #25
  %18 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %16) #25
  %19 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %18, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %20 = fmul fast <3 x float> %19, %17
  %21 = shufflevector <3 x float> %20, <3 x float> poison, <3 x i32> zeroinitializer
  %22 = fmul fast <3 x float> %21, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %23 = shufflevector <3 x float> %20, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %24 = fmul fast <3 x float> %23, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %25 = fadd fast <3 x float> %22, %24
  %26 = shufflevector <3 x float> %20, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %27 = fmul fast <3 x float> %26, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %28 = fadd fast <3 x float> %25, %27
  %29 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %28) #25
  %30 = extractelement <3 x half> %3, i64 2
  %31 = fcmp fast une half %30, 0xH0000
  %32 = extractelement <3 x half> %3, i64 1
  %33 = fcmp fast une half %32, 0xH0000
  %34 = select i1 %31, i1 true, i1 %33
  br i1 %34, label %35, label %37

35:                                               ; preds = %6
  %36 = tail call fast half @air.atan2.f16(half %30, half %32) #25
  br label %37

37:                                               ; preds = %35, %6
  %38 = phi fast half [ %36, %35 ], [ 0xH0000, %6 ]
  %39 = extractelement <3 x half> %29, i64 2
  %40 = fcmp fast une half %39, 0xH0000
  %41 = extractelement <3 x half> %29, i64 1
  %42 = fcmp fast une half %41, 0xH0000
  %43 = select i1 %40, i1 true, i1 %42
  br i1 %43, label %44, label %46

44:                                               ; preds = %37
  %45 = tail call fast half @air.atan2.f16(half %39, half %41) #25
  br label %46

46:                                               ; preds = %44, %37
  %47 = phi fast half [ %45, %44 ], [ 0xH0000, %37 ]
  %48 = fmul fast half %41, %41
  %49 = fmul fast half %39, %39
  %50 = fadd fast half %48, %49
  %51 = tail call fast half @air.sqrt.f16(half %50) #25
  %52 = fpext half %51 to float
  %53 = fcmp fast ogt float %52, 0x3F50624DE0000000
  br i1 %53, label %54, label %59

54:                                               ; preds = %46
  %55 = fdiv fast half %41, %51
  %56 = insertelement <2 x half> undef, half %55, i64 0
  %57 = fdiv fast half %39, %51
  %58 = insertelement <2 x half> %56, half %57, i64 1
  br label %59

59:                                               ; preds = %54, %46
  %60 = phi fast <2 x half> [ %58, %54 ], [ zeroinitializer, %46 ]
  %61 = tail call fast half @air.sqrt.f16(half 0xH3C00) #25
  %62 = extractelement <2 x half> %60, i64 0
  %63 = fmul fast half %62, 0xH3AEE
  %64 = extractelement <2 x half> %60, i64 1
  %65 = fmul fast half %64, 0xH3800
  %66 = fadd fast half %63, %65
  %67 = fdiv fast half %66, %61
  %68 = fadd fast half %67, 0xH2E66
  %69 = fmul fast half %68, 0xH3EAA
  %70 = tail call fast half @air.clamp.f16(half %69, half 0xH0000, half 0xH3C00) #25
  %71 = fmul fast half %70, %70
  %72 = fmul fast half %70, 0xH4000
  %73 = fsub fast half 0xH4200, %72
  %74 = fmul fast half %71, %73
  %75 = fpext half %74 to float
  %76 = fadd fast half %67, 0xHBACD
  %77 = fmul fast half %76, 0xH4723
  %78 = tail call fast half @air.clamp.f16(half %77, half 0xH0000, half 0xH3C00) #25
  %79 = fmul fast half %78, %78
  %80 = fmul fast half %78, 0xH4000
  %81 = fsub fast half 0xH4200, %80
  %82 = fmul fast half %79, %81
  %83 = fpext half %82 to float
  %84 = fmul fast float %83, 5.000000e-01
  %85 = fsub fast float 1.000000e+00, %84
  %86 = fmul fast float %85, %75
  %87 = fptrunc float %86 to half
  %88 = fpext half %87 to float
  %89 = fmul fast float %88, 0x3F947AE140000000
  %90 = fpext half %39 to float
  %91 = fsub fast float %90, %89
  %92 = fptrunc float %91 to half
  %93 = insertelement <3 x half> %29, half %92, i64 2
  %94 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %93) #25
  %95 = shufflevector <3 x float> %94, <3 x float> poison, <3 x i32> zeroinitializer
  %96 = shufflevector <3 x float> %94, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %97 = fmul fast <3 x float> %96, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %98 = fadd fast <3 x float> %97, %95
  %99 = shufflevector <3 x float> %94, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %100 = fmul fast <3 x float> %99, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %101 = fadd fast <3 x float> %98, %100
  %102 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %101) #25
  %103 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %101) #25
  %104 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %103, <3 x float> splat (float 0x40029ACA60000000)) #25
  %105 = fmul fast <3 x float> %104, %102
  %106 = shufflevector <3 x float> %105, <3 x float> poison, <3 x i32> zeroinitializer
  %107 = fmul fast <3 x float> %106, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %108 = shufflevector <3 x float> %105, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %109 = fmul fast <3 x float> %108, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %110 = fadd fast <3 x float> %107, %109
  %111 = shufflevector <3 x float> %105, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %112 = fmul fast <3 x float> %111, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %113 = fadd fast <3 x float> %110, %112
  %114 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %113) #25
  %115 = fmul fast half %32, %32
  %116 = fmul fast half %30, %30
  %117 = fadd fast half %115, %116
  %118 = tail call fast half @air.sqrt.f16(half %117) #25
  %119 = fpext half %118 to float
  %120 = fcmp fast ogt float %119, 0x3F50624DE0000000
  br i1 %120, label %121, label %126

121:                                              ; preds = %59
  %122 = fdiv fast half %32, %118
  %123 = insertelement <2 x half> undef, half %122, i64 0
  %124 = fdiv fast half %30, %118
  %125 = insertelement <2 x half> %123, half %124, i64 1
  br label %126

126:                                              ; preds = %121, %59
  %127 = phi fast <2 x half> [ %125, %121 ], [ zeroinitializer, %59 ]
  %128 = fcmp fast ogt half %4, 0xH0000
  br i1 %128, label %161, label %129

129:                                              ; preds = %126
  %130 = extractelement <2 x half> %127, i64 0
  %131 = fmul fast half %130, 0xH2A66
  %132 = extractelement <2 x half> %127, i64 1
  %133 = fmul fast half %132, 0xH3666
  %134 = fadd fast half %131, %133
  %135 = tail call fast half @air.sqrt.f16(half 0xH3132) #25
  %136 = fdiv fast half %134, %135
  %137 = fadd fast half %136, 0xHB99A
  %138 = fmul fast half %137, 0xH42E5
  %139 = tail call fast half @air.clamp.f16(half %138, half 0xH0000, half 0xH3C00) #25
  %140 = fmul fast half %139, %139
  %141 = fmul fast half %139, 0xH4000
  %142 = fsub fast half 0xH4200, %141
  %143 = fmul fast half %140, %142
  %144 = extractelement <3 x half> %114, i64 1
  %145 = extractelement <3 x half> %114, i64 2
  %146 = fsub fast half %144, %145
  %147 = fmul fast half %146, 0xH5240
  %148 = tail call fast half @air.clamp.f16(half %147, half 0xH0000, half 0xH3C00) #25
  %149 = fmul fast half %148, %148
  %150 = fmul fast half %148, 0xH4000
  %151 = fsub fast half 0xH4200, %150
  %152 = fmul fast half %149, %151
  %153 = fsub fast half 0xH3C00, %143
  %154 = fpext half %153 to float
  %155 = fmul fast float %154, 0x3F847AE140000000
  %156 = fsub fast half 0xH3C00, %152
  %157 = fpext half %156 to float
  %158 = fmul fast float %157, 0x3F747AE140000000
  %159 = fadd fast float %158, %155
  %160 = fptrunc float %159 to half
  br label %161

161:                                              ; preds = %129, %126
  %162 = phi half [ %160, %129 ], [ 0xH27AE, %126 ]
  %163 = tail call fast half @air.sign.f16(half %47) #25
  %164 = fpext half %163 to float
  %165 = tail call i1 @air.convert.u.i1.f.f32(float %164) #25
  %166 = fadd fast half %47, 0xH4648
  %167 = select fast i1 %165, half %166, half %47
  %168 = tail call fast half @air.fmod.f16(half %167, half 0xH4648) #25
  %169 = fpext half %168 to float
  %170 = fadd fast float %169, 0xBFE226C3C0000000
  %171 = tail call fast float @air.fast_fabs.f32(float %170) #25
  %172 = fadd fast float %171, 0xBFE3333340000000
  %173 = fmul fast float %172, 0xC00AAAAAA0000000
  %174 = tail call fast float @air.fast_clamp.f32(float %173, float 0.000000e+00, float 1.000000e+00) #25
  %175 = fmul fast float %174, 2.000000e+00
  %176 = fsub fast float 3.000000e+00, %175
  %177 = tail call fast half @air.sign.f16(half %38) #25
  %178 = fpext half %177 to float
  %179 = tail call i1 @air.convert.u.i1.f.f32(float %178) #25
  %180 = fadd fast half %38, 0xH4648
  %181 = select fast i1 %179, half %180, half %38
  %182 = tail call fast half @air.fmod.f16(half %181, half 0xH4648) #25
  %183 = fpext half %182 to float
  %184 = fadd fast float %183, 0xBFE226C3C0000000
  %185 = tail call fast float @air.fast_fabs.f32(float %184) #25
  %186 = fadd fast float %185, 0xBFE3333340000000
  %187 = fmul fast float %186, 0xC00AAAAAA0000000
  %188 = tail call fast float @air.fast_clamp.f32(float %187, float 0.000000e+00, float 1.000000e+00) #25
  %189 = fmul fast float %188, 2.000000e+00
  %190 = fsub fast float 3.000000e+00, %189
  %191 = fmul fast float %188, %174
  %192 = fmul fast float %52, 0x3FA99999A0000000
  %193 = fmul fast float %192, %176
  %194 = fmul fast float %191, %191
  %195 = fmul fast float %194, %193
  %196 = fmul fast float %195, %190
  %197 = fadd fast float %196, %52
  %198 = fptrunc float %197 to half
  %199 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %200 = fadd fast <3 x half> %199, splat (half 0xHBC00)
  %201 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %202 = fmul fast half %162, %87
  %203 = fadd fast half %202, %41
  %204 = fadd fast half %202, %39
  %205 = tail call fast half @air.cos.f16(half %168) #25
  %206 = fmul fast half %205, %198
  %207 = tail call fast half @air.mix.f16(half %206, half %203, half %2) #25
  %208 = insertelement <2 x half> undef, half %207, i64 0
  %209 = tail call fast half @air.sin.f16(half %168) #25
  %210 = fmul fast half %209, %198
  %211 = tail call fast half @air.mix.f16(half %210, half %204, half %2) #25
  %212 = insertelement <2 x half> %208, half %211, i64 1
  %213 = fadd fast half %118, 0xHADC3
  %214 = fmul fast half %213, 0xH488C
  %215 = tail call fast half @air.clamp.f16(half %214, half 0xH0000, half 0xH3C00) #25
  %216 = fmul fast half %215, %215
  %217 = fmul fast half %215, 0xH4000
  %218 = fsub fast half 0xH4200, %217
  %219 = fmul fast half %216, %218
  %220 = fsub fast half 0xH3C00, %1
  %221 = insertelement <2 x half> poison, half %220, i64 0
  %222 = fsub fast half 0xH3C00, %219
  %223 = fpext half %222 to float
  %224 = fmul fast float %223, 0x3FB99999A0000000
  %225 = fadd fast float %224, 1.000000e+00
  %226 = fptrunc float %225 to half
  %227 = insertelement <2 x half> poison, half %226, i64 0
  %228 = insertelement <2 x half> poison, half %1, i64 0
  %229 = fmul fast <2 x half> %227, %228
  %230 = fadd fast <2 x half> %229, %221
  %231 = shufflevector <2 x half> %230, <2 x half> poison, <2 x i32> zeroinitializer
  %232 = fmul fast <2 x half> %231, %212
  %233 = shufflevector <2 x half> %232, <2 x half> poison, <3 x i32> <i32 0, i32 1, i32 poison>
  %234 = shufflevector <3 x half> %29, <3 x half> %233, <3 x i32> <i32 0, i32 3, i32 4>
  %235 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %234) #25
  %236 = shufflevector <3 x float> %235, <3 x float> poison, <3 x i32> zeroinitializer
  %237 = shufflevector <3 x float> %235, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %238 = fmul fast <3 x float> %237, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %239 = fadd fast <3 x float> %238, %236
  %240 = shufflevector <3 x float> %235, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %241 = fmul fast <3 x float> %240, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %242 = fadd fast <3 x float> %239, %241
  %243 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %242) #25
  %244 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %242) #25
  %245 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %244, <3 x float> splat (float 0x40029ACA60000000)) #25
  %246 = fmul fast <3 x float> %245, %243
  %247 = shufflevector <3 x float> %246, <3 x float> poison, <3 x i32> zeroinitializer
  %248 = fmul fast <3 x float> %247, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %249 = shufflevector <3 x float> %246, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %250 = fmul fast <3 x float> %249, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %251 = fadd fast <3 x float> %248, %250
  %252 = shufflevector <3 x float> %246, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %253 = fmul fast <3 x float> %252, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %254 = fadd fast <3 x float> %251, %253
  %255 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %254) #25
  %256 = insertelement <3 x half> poison, half %5, i64 0
  %257 = shufflevector <3 x half> %256, <3 x half> poison, <3 x i32> zeroinitializer
  %258 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %7, <3 x half> %255, <3 x half> %257) #25
  %259 = fadd fast <3 x half> %200, %201
  %260 = fadd fast <3 x half> %259, %258
  ret <3 x half> %260
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_clamp.f32(float, float, float) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmod.f16(half, half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.sign.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z8deYellowDv3_DhDhDhS_Dh(<3 x half> noundef %0, half noundef %1, half %2, <3 x half> noundef %3, half noundef %4) unnamed_addr #9 {
  %6 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %7 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %6) #25
  %8 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %6) #25
  %9 = fmul fast <3 x half> %8, splat (half 0xH4A76)
  %10 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %8, <3 x half> splat (half 0xH36AA)) #25
  %11 = fmul fast <3 x half> %10, splat (half 0xH3C38)
  %12 = fadd fast <3 x half> %11, splat (half 0xHAB0A)
  %13 = fcmp fast ogt <3 x half> %8, splat (half 0xH1A69)
  %14 = select fast <3 x i1> %13, <3 x half> %12, <3 x half> %9
  %15 = fmul fast <3 x half> %14, %7
  %16 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %15) #25
  %17 = shufflevector <3 x float> %16, <3 x float> poison, <3 x i32> zeroinitializer
  %18 = fmul fast <3 x float> %17, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %19 = shufflevector <3 x float> %16, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %20 = fmul fast <3 x float> %19, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %21 = fadd fast <3 x float> %18, %20
  %22 = shufflevector <3 x float> %16, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %23 = fmul fast <3 x float> %22, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %24 = fadd fast <3 x float> %21, %23
  %25 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %24) #25
  %26 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %24) #25
  %27 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %26, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %28 = fmul fast <3 x float> %27, %25
  %29 = shufflevector <3 x float> %28, <3 x float> poison, <3 x i32> zeroinitializer
  %30 = fmul fast <3 x float> %29, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %31 = shufflevector <3 x float> %28, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %32 = fmul fast <3 x float> %31, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %33 = fadd fast <3 x float> %30, %32
  %34 = shufflevector <3 x float> %28, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %35 = fmul fast <3 x float> %34, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %36 = fadd fast <3 x float> %33, %35
  %37 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %36) #25
  %38 = extractelement <3 x half> %37, i64 1
  %39 = fmul fast half %38, %38
  %40 = extractelement <3 x half> %37, i64 2
  %41 = fmul fast half %40, %40
  %42 = fadd fast half %39, %41
  %43 = tail call fast half @air.sqrt.f16(half %42) #25
  %44 = fpext half %43 to float
  %45 = fcmp fast ogt float %44, 0x3F50624DE0000000
  br i1 %45, label %46, label %51

46:                                               ; preds = %5
  %47 = fdiv fast half %38, %43
  %48 = insertelement <2 x half> undef, half %47, i64 0
  %49 = fdiv fast half %40, %43
  %50 = insertelement <2 x half> %48, half %49, i64 1
  br label %51

51:                                               ; preds = %46, %5
  %52 = phi fast <2 x half> [ %50, %46 ], [ zeroinitializer, %5 ]
  %53 = extractelement <3 x half> %3, i64 1
  %54 = fmul fast half %53, %53
  %55 = extractelement <3 x half> %3, i64 2
  %56 = fmul fast half %55, %55
  %57 = fadd fast half %54, %56
  %58 = tail call fast half @air.sqrt.f16(half %57) #25
  %59 = fpext half %58 to float
  %60 = fcmp fast ogt float %59, 0x3F50624DE0000000
  br i1 %60, label %61, label %66

61:                                               ; preds = %51
  %62 = fdiv fast half %53, %58
  %63 = insertelement <2 x half> undef, half %62, i64 0
  %64 = fdiv fast half %55, %58
  %65 = insertelement <2 x half> %63, half %64, i64 1
  br label %66

66:                                               ; preds = %61, %51
  %67 = phi fast <2 x half> [ %65, %61 ], [ zeroinitializer, %51 ]
  %68 = extractelement <2 x half> %52, i64 0
  %69 = fmul fast half %68, 0xH3AEE
  %70 = extractelement <2 x half> %52, i64 1
  %71 = fmul fast half %70, 0xH3800
  %72 = fadd fast half %69, %71
  %73 = tail call fast half @air.sqrt.f16(half 0xH3C00) #25
  %74 = fdiv fast half %72, %73
  %75 = fadd fast half %74, 0xHBACD
  %76 = fmul fast half %75, 0xH4723
  %77 = tail call fast half @air.clamp.f16(half %76, half 0xH0000, half 0xH3C00) #25
  %78 = fmul fast half %77, %77
  %79 = fmul fast half %77, 0xH4000
  %80 = fsub fast half 0xH4200, %79
  %81 = fmul fast half %78, %80
  %82 = fpext half %81 to float
  %83 = fmul fast float %82, 5.000000e-01
  %84 = fsub fast float 1.000000e+00, %83
  %85 = fadd fast half %74, 0xHB4CD
  %86 = fmul fast half %85, 0xH3F46
  %87 = tail call fast half @air.clamp.f16(half %86, half 0xH0000, half 0xH3C00) #25
  %88 = fmul fast half %87, %87
  %89 = fmul fast half %87, 0xH4000
  %90 = fsub fast half 0xH4200, %89
  %91 = fmul fast half %88, %90
  %92 = fpext half %91 to float
  %93 = fmul fast float %84, %92
  %94 = fptrunc float %93 to half
  %95 = fpext half %94 to float
  %96 = fmul fast float %95, 0x3FA47AE140000000
  %97 = fpext half %40 to float
  %98 = fsub fast float %97, %96
  %99 = fptrunc float %98 to half
  %100 = insertelement <3 x half> %37, half %99, i64 2
  %101 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %100) #25
  %102 = shufflevector <3 x float> %101, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %103 = fmul fast <3 x float> %102, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %104 = shufflevector <3 x float> %101, <3 x float> poison, <3 x i32> zeroinitializer
  %105 = fadd fast <3 x float> %103, %104
  %106 = shufflevector <3 x float> %101, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %107 = fmul fast <3 x float> %106, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %108 = fadd fast <3 x float> %105, %107
  %109 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %108) #25
  %110 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %109, <3 x float> splat (float 0x40029ACA60000000)) #25
  %111 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %108) #25
  %112 = fmul fast <3 x float> %111, %110
  %113 = shufflevector <3 x float> %112, <3 x float> poison, <3 x i32> zeroinitializer
  %114 = fmul fast <3 x float> %113, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %115 = shufflevector <3 x float> %112, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %116 = fmul fast <3 x float> %115, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %117 = fadd fast <3 x float> %114, %116
  %118 = shufflevector <3 x float> %112, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %119 = fmul fast <3 x float> %118, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %120 = fadd fast <3 x float> %117, %119
  %121 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %120) #25
  %122 = extractelement <3 x half> %121, i64 1
  %123 = extractelement <3 x half> %121, i64 2
  %124 = fsub fast half %122, %123
  %125 = fmul fast half %124, 0xH5240
  %126 = tail call fast half @air.clamp.f16(half %125, half 0xH0000, half 0xH3C00) #25
  %127 = fmul fast half %126, 0xH4000
  %128 = fsub fast half 0xH4200, %127
  %129 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %130 = fadd fast <3 x half> %129, splat (half 0xHBC00)
  %131 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %132 = tail call fast half @air.sqrt.f16(half 0xH3132) #25
  %133 = extractelement <2 x half> %67, i64 0
  %134 = fmul fast half %133, 0xH2A66
  %135 = extractelement <2 x half> %67, i64 1
  %136 = fmul fast half %135, 0xH3666
  %137 = fadd fast half %134, %136
  %138 = fdiv fast half %137, %132
  %139 = fadd fast half %138, 0xHBB33
  %140 = fmul fast half %139, 0xH4989
  %141 = tail call fast half @air.clamp.f16(half %140, half 0xH0000, half 0xH3C00) #25
  %142 = fmul fast half %141, %141
  %143 = fmul fast half %141, 0xH4000
  %144 = fsub fast half 0xH4200, %143
  %145 = fmul fast half %142, %144
  %146 = fpext half %145 to float
  %147 = fmul fast float %146, 0x3FA47AE140000000
  %148 = fadd fast float %147, 0x3FA47AE140000000
  %149 = fptrunc float %148 to half
  %150 = fmul fast half %126, %126
  %151 = fmul fast half %150, %94
  %152 = fmul fast half %151, %128
  %153 = fmul fast half %152, %149
  %154 = fsub fast half %40, %153
  %155 = tail call fast half @air.mix.f16(half %40, half %154, half %1) #25
  %156 = insertelement <3 x half> %37, half %155, i64 2
  %157 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %156) #25
  %158 = shufflevector <3 x float> %157, <3 x float> poison, <3 x i32> zeroinitializer
  %159 = shufflevector <3 x float> %157, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %160 = fmul fast <3 x float> %159, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %161 = fadd fast <3 x float> %160, %158
  %162 = shufflevector <3 x float> %157, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %163 = fmul fast <3 x float> %162, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %164 = fadd fast <3 x float> %161, %163
  %165 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %164) #25
  %166 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %164) #25
  %167 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %166, <3 x float> splat (float 0x40029ACA60000000)) #25
  %168 = fmul fast <3 x float> %167, %165
  %169 = shufflevector <3 x float> %168, <3 x float> poison, <3 x i32> zeroinitializer
  %170 = fmul fast <3 x float> %169, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %171 = shufflevector <3 x float> %168, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %172 = fmul fast <3 x float> %171, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %173 = fadd fast <3 x float> %170, %172
  %174 = shufflevector <3 x float> %168, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %175 = fmul fast <3 x float> %174, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %176 = fadd fast <3 x float> %173, %175
  %177 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %176) #25
  %178 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %177) #25
  %179 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %177) #25
  %180 = fmul fast <3 x half> %179, splat (half 0xH2CF4)
  %181 = fadd fast <3 x half> %179, splat (half 0xH2B0A)
  %182 = fmul fast <3 x half> %181, splat (half 0xH3B96)
  %183 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %182, <3 x half> splat (half 0xH40CD)) #25
  %184 = fcmp fast ogt <3 x half> %179, splat (half 0xH292D)
  %185 = select fast <3 x i1> %184, <3 x half> %183, <3 x half> %180
  %186 = fmul fast <3 x half> %185, %178
  %187 = fadd fast <3 x half> %130, %131
  %188 = fadd fast <3 x half> %187, %186
  %189 = insertelement <3 x half> poison, half %4, i64 0
  %190 = shufflevector <3 x half> %189, <3 x half> poison, <3 x i32> zeroinitializer
  %191 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %6, <3 x half> %188, <3 x half> %190) #25
  %192 = insertelement <3 x half> poison, half %1, i64 0
  %193 = shufflevector <3 x half> %192, <3 x half> poison, <3 x i32> zeroinitializer
  %194 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %0, <3 x half> %191, <3 x half> %193) #25
  ret <3 x half> %194
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z16deRedNeutralOnlyDv3_DhDhDhS_DhDhDh(<3 x half> noundef %0, half noundef %1, half %2, <3 x half> noundef %3, half noundef %4, half noundef %5, half noundef %6) unnamed_addr #9 {
  %8 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %9 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %8) #25
  %10 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %8) #25
  %11 = fmul fast <3 x half> %10, splat (half 0xH4A76)
  %12 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %10, <3 x half> splat (half 0xH36AA)) #25
  %13 = fmul fast <3 x half> %12, splat (half 0xH3C38)
  %14 = fadd fast <3 x half> %13, splat (half 0xHAB0A)
  %15 = fcmp fast ogt <3 x half> %10, splat (half 0xH1A69)
  %16 = select fast <3 x i1> %15, <3 x half> %14, <3 x half> %11
  %17 = fmul fast <3 x half> %16, %9
  %18 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %17) #25
  %19 = shufflevector <3 x float> %18, <3 x float> poison, <3 x i32> zeroinitializer
  %20 = fmul fast <3 x float> %19, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %21 = shufflevector <3 x float> %18, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %22 = fmul fast <3 x float> %21, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %23 = fadd fast <3 x float> %20, %22
  %24 = shufflevector <3 x float> %18, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %25 = fmul fast <3 x float> %24, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %26 = fadd fast <3 x float> %23, %25
  %27 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %26) #25
  %28 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %26) #25
  %29 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %28, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %30 = fmul fast <3 x float> %29, %27
  %31 = shufflevector <3 x float> %30, <3 x float> poison, <3 x i32> zeroinitializer
  %32 = fmul fast <3 x float> %31, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %33 = shufflevector <3 x float> %30, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %34 = fmul fast <3 x float> %33, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %35 = fadd fast <3 x float> %32, %34
  %36 = shufflevector <3 x float> %30, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %37 = fmul fast <3 x float> %36, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %38 = fadd fast <3 x float> %35, %37
  %39 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %38) #25
  %40 = extractelement <3 x half> %39, i64 2
  %41 = fcmp fast une half %40, 0xH0000
  %42 = extractelement <3 x half> %39, i64 1
  %43 = fcmp fast une half %42, 0xH0000
  %44 = select i1 %41, i1 true, i1 %43
  br i1 %44, label %45, label %47

45:                                               ; preds = %7
  %46 = tail call fast half @air.atan2.f16(half %40, half %42) #25
  br label %47

47:                                               ; preds = %45, %7
  %48 = phi fast half [ %46, %45 ], [ 0xH0000, %7 ]
  %49 = extractelement <3 x half> %3, i64 1
  %50 = fmul fast half %49, %49
  %51 = extractelement <3 x half> %3, i64 2
  %52 = fmul fast half %51, %51
  %53 = fadd fast half %50, %52
  %54 = tail call fast half @air.sqrt.f16(half %53) #25
  %55 = fadd fast half %54, 0xHB266
  %56 = fmul fast half %55, 0xHCD02
  %57 = tail call fast half @air.clamp.f16(half %56, half 0xH0000, half 0xH3C00) #25
  %58 = fmul fast half %57, %57
  %59 = fmul fast half %57, 0xH4000
  %60 = fsub fast half 0xH4200, %59
  %61 = fmul fast half %58, %60
  %62 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %63 = fadd fast <3 x half> %62, splat (half 0xHBC00)
  %64 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %65 = fadd fast half %48, 0xH4648
  %66 = tail call fast half @air.sign.f16(half %48) #25
  %67 = fpext half %66 to float
  %68 = tail call i1 @air.convert.u.i1.f.f32(float %67) #25
  %69 = select fast i1 %68, half %65, half %48
  %70 = tail call fast half @air.fmod.f16(half %69, half 0xH4648) #25
  %71 = shufflevector <3 x half> %39, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %72 = tail call fast half @air.dot.v2f16(<2 x half> %71, <2 x half> %71) #25
  %73 = tail call fast half @air.sqrt.f16(half %72) #25
  %74 = fpext half %61 to float
  %75 = fpext half %70 to float
  %76 = fadd fast float %75, 0xBFD3333340000000
  %77 = tail call fast float @air.fast_fabs.f32(float %76) #25
  %78 = fadd fast float %77, -5.000000e-01
  %79 = fmul fast float %78, 0xC001C71C80000000
  %80 = tail call fast float @air.fast_clamp.f32(float %79, float 0.000000e+00, float 1.000000e+00) #25
  %81 = fmul fast float %80, 2.000000e+00
  %82 = fsub fast float 3.000000e+00, %81
  %83 = fmul fast float %74, 5.000000e-01
  %84 = fmul fast float %80, %80
  %85 = fmul fast float %84, %83
  %86 = fmul fast float %85, %82
  %87 = fptrunc float %86 to half
  %88 = fmul fast half %87, %6
  %89 = fadd fast half %88, %70
  %90 = fsub fast half 0xH3C00, %5
  %91 = fmul fast half %73, %90
  %92 = tail call fast half @air.cos.f16(half %89) #25
  %93 = fmul fast half %92, %91
  %94 = tail call fast half @air.sin.f16(half %89) #25
  %95 = fmul fast half %94, %91
  %96 = tail call fast half @air.mix.f16(half %42, half %93, half %1) #25
  %97 = insertelement <3 x half> %39, half %96, i64 1
  %98 = tail call fast half @air.mix.f16(half %40, half %95, half %1) #25
  %99 = insertelement <3 x half> %97, half %98, i64 2
  %100 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %99) #25
  %101 = shufflevector <3 x float> %100, <3 x float> poison, <3 x i32> zeroinitializer
  %102 = shufflevector <3 x float> %100, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %103 = fmul fast <3 x float> %102, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %104 = fadd fast <3 x float> %103, %101
  %105 = shufflevector <3 x float> %100, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %106 = fmul fast <3 x float> %105, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %107 = fadd fast <3 x float> %104, %106
  %108 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %107) #25
  %109 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %107) #25
  %110 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %109, <3 x float> splat (float 0x40029ACA60000000)) #25
  %111 = fmul fast <3 x float> %110, %108
  %112 = shufflevector <3 x float> %111, <3 x float> poison, <3 x i32> zeroinitializer
  %113 = fmul fast <3 x float> %112, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %114 = shufflevector <3 x float> %111, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %115 = fmul fast <3 x float> %114, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %116 = fadd fast <3 x float> %113, %115
  %117 = shufflevector <3 x float> %111, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %118 = fmul fast <3 x float> %117, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %119 = fadd fast <3 x float> %116, %118
  %120 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %119) #25
  %121 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %120) #25
  %122 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %120) #25
  %123 = fmul fast <3 x half> %122, splat (half 0xH2CF4)
  %124 = fadd fast <3 x half> %122, splat (half 0xH2B0A)
  %125 = fmul fast <3 x half> %124, splat (half 0xH3B96)
  %126 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %125, <3 x half> splat (half 0xH40CD)) #25
  %127 = fcmp fast ogt <3 x half> %122, splat (half 0xH292D)
  %128 = select fast <3 x i1> %127, <3 x half> %126, <3 x half> %123
  %129 = fmul fast <3 x half> %128, %121
  %130 = fadd fast <3 x half> %63, %64
  %131 = fadd fast <3 x half> %130, %129
  %132 = insertelement <3 x half> poison, half %4, i64 0
  %133 = shufflevector <3 x half> %132, <3 x half> poison, <3 x i32> zeroinitializer
  %134 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %8, <3 x half> %131, <3 x half> %133) #25
  ret <3 x half> %134
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z5deRedDv3_DhDhDhS_Dh(<3 x half> noundef %0, half noundef %1, half noundef %2, <3 x half> noundef %3, half noundef %4) unnamed_addr #9 {
  %6 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %7 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %6) #25
  %8 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %6) #25
  %9 = fmul fast <3 x half> %8, splat (half 0xH4A76)
  %10 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %8, <3 x half> splat (half 0xH36AA)) #25
  %11 = fmul fast <3 x half> %10, splat (half 0xH3C38)
  %12 = fadd fast <3 x half> %11, splat (half 0xHAB0A)
  %13 = fcmp fast ogt <3 x half> %8, splat (half 0xH1A69)
  %14 = select fast <3 x i1> %13, <3 x half> %12, <3 x half> %9
  %15 = fmul fast <3 x half> %14, %7
  %16 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %15) #25
  %17 = shufflevector <3 x float> %16, <3 x float> poison, <3 x i32> zeroinitializer
  %18 = fmul fast <3 x float> %17, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %19 = shufflevector <3 x float> %16, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %20 = fmul fast <3 x float> %19, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %21 = fadd fast <3 x float> %18, %20
  %22 = shufflevector <3 x float> %16, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %23 = fmul fast <3 x float> %22, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %24 = fadd fast <3 x float> %21, %23
  %25 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %24) #25
  %26 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %24) #25
  %27 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %26, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %28 = fmul fast <3 x float> %27, %25
  %29 = shufflevector <3 x float> %28, <3 x float> poison, <3 x i32> zeroinitializer
  %30 = fmul fast <3 x float> %29, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %31 = shufflevector <3 x float> %28, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %32 = fmul fast <3 x float> %31, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %33 = fadd fast <3 x float> %30, %32
  %34 = shufflevector <3 x float> %28, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %35 = fmul fast <3 x float> %34, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %36 = fadd fast <3 x float> %33, %35
  %37 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %36) #25
  %38 = extractelement <3 x half> %37, i64 1
  %39 = fmul fast half %38, %38
  %40 = extractelement <3 x half> %37, i64 2
  %41 = fmul fast half %40, %40
  %42 = fadd fast half %39, %41
  %43 = tail call fast half @air.sqrt.f16(half %42) #25
  %44 = fpext half %43 to float
  %45 = fcmp fast ogt float %44, 0x3F50624DE0000000
  br i1 %45, label %46, label %51

46:                                               ; preds = %5
  %47 = fdiv fast half %38, %43
  %48 = insertelement <2 x half> undef, half %47, i64 0
  %49 = fdiv fast half %40, %43
  %50 = insertelement <2 x half> %48, half %49, i64 1
  br label %51

51:                                               ; preds = %46, %5
  %52 = phi fast <2 x half> [ %50, %46 ], [ zeroinitializer, %5 ]
  %53 = extractelement <3 x half> %3, i64 1
  %54 = fmul fast half %53, %53
  %55 = extractelement <3 x half> %3, i64 2
  %56 = fmul fast half %55, %55
  %57 = fadd fast half %54, %56
  %58 = tail call fast half @air.sqrt.f16(half %57) #25
  %59 = fpext half %58 to float
  %60 = fcmp fast ogt float %59, 0x3F50624DE0000000
  br i1 %60, label %61, label %66

61:                                               ; preds = %51
  %62 = fdiv fast half %53, %58
  %63 = insertelement <2 x half> undef, half %62, i64 0
  %64 = fdiv fast half %55, %58
  %65 = insertelement <2 x half> %63, half %64, i64 1
  br label %66

66:                                               ; preds = %61, %51
  %67 = phi fast <2 x half> [ %65, %61 ], [ zeroinitializer, %51 ]
  %68 = fadd fast half %58, 0xHADC3
  %69 = fmul fast half %68, 0xH5243
  %70 = tail call fast half @air.clamp.f16(half %69, half 0xH0000, half 0xH3C00) #25
  %71 = fmul fast half %70, %70
  %72 = fmul fast half %70, 0xH4000
  %73 = fsub fast half 0xH4200, %72
  %74 = fmul fast half %71, %73
  %75 = extractelement <2 x half> %52, i64 0
  %76 = fmul fast half %75, 0xH3AEE
  %77 = extractelement <2 x half> %52, i64 1
  %78 = fmul fast half %77, 0xH3800
  %79 = fadd fast half %76, %78
  %80 = tail call fast half @air.sqrt.f16(half 0xH3C00) #25
  %81 = fdiv fast half %79, %80
  %82 = fadd fast half %81, 0xHBACD
  %83 = fmul fast half %82, 0xH4723
  %84 = tail call fast half @air.clamp.f16(half %83, half 0xH0000, half 0xH3C00) #25
  %85 = fmul fast half %84, %84
  %86 = fmul fast half %84, 0xH4000
  %87 = fsub fast half 0xH4200, %86
  %88 = fmul fast half %85, %87
  %89 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %90 = fadd fast <3 x half> %89, splat (half 0xHBC00)
  %91 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %92 = extractelement <2 x half> %67, i64 0
  %93 = fmul fast half %92, 0xH3AEE
  %94 = extractelement <2 x half> %67, i64 1
  %95 = fmul fast half %94, 0xH3800
  %96 = fadd fast half %93, %95
  %97 = fdiv fast half %96, %80
  %98 = fadd fast half %97, 0xHBB9A
  %99 = fmul fast half %98, 0xH4E3E
  %100 = tail call fast half @air.clamp.f16(half %99, half 0xH0000, half 0xH3C00) #25
  %101 = fmul fast half %100, %100
  %102 = fmul fast half %100, 0xH4000
  %103 = fsub fast half 0xH4200, %102
  %104 = fmul fast half %101, %103
  %105 = fpext half %38 to float
  %106 = fpext half %88 to float
  %107 = fpext half %104 to float
  %108 = fpext half %74 to float
  %109 = fmul fast float %106, %108
  %110 = fmul fast float %109, 0x3FC3333340000000
  %111 = fmul fast float %110, %105
  %112 = fmul fast float %111, %107
  %113 = fsub fast float %105, %112
  %114 = fptrunc float %113 to half
  %115 = fpext half %40 to float
  %116 = fmul fast float %110, %115
  %117 = fmul fast float %116, %107
  %118 = fsub fast float %115, %117
  %119 = fptrunc float %118 to half
  %120 = fsub fast half 0xH3C00, %1
  %121 = fmul fast half %38, %120
  %122 = fmul fast half %114, %1
  %123 = fadd fast half %122, %121
  %124 = fmul fast half %40, %120
  %125 = fmul fast half %119, %1
  %126 = fadd fast half %125, %124
  %127 = fpext half %123 to float
  %128 = fmul fast float %110, %107
  %129 = fmul fast float %128, %127
  %130 = fsub fast float %127, %129
  %131 = fptrunc float %130 to half
  %132 = fpext half %126 to float
  %133 = fmul fast float %128, %132
  %134 = fsub fast float %132, %133
  %135 = fptrunc float %134 to half
  %136 = extractelement <3 x half> %37, i64 0
  %137 = fpext half %136 to float
  %138 = fmul fast float %109, 0x3F999999A0000000
  %139 = fmul fast float %138, %137
  %140 = fmul fast float %139, %107
  %141 = fadd fast float %140, %137
  %142 = fptrunc float %141 to half
  %143 = fsub fast half 0xH3C00, %2
  %144 = fmul fast half %123, %143
  %145 = fmul fast half %131, %2
  %146 = fadd fast half %145, %144
  %147 = insertelement <3 x half> poison, half %146, i64 1
  %148 = fmul fast half %126, %143
  %149 = fmul fast half %135, %2
  %150 = fadd fast half %149, %148
  %151 = insertelement <3 x half> %147, half %150, i64 2
  %152 = fmul fast half %136, %143
  %153 = fmul fast half %142, %2
  %154 = fadd fast half %153, %152
  %155 = insertelement <3 x half> %151, half %154, i64 0
  %156 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %155) #25
  %157 = shufflevector <3 x float> %156, <3 x float> poison, <3 x i32> zeroinitializer
  %158 = shufflevector <3 x float> %156, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %159 = fmul fast <3 x float> %158, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %160 = fadd fast <3 x float> %159, %157
  %161 = shufflevector <3 x float> %156, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %162 = fmul fast <3 x float> %161, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %163 = fadd fast <3 x float> %160, %162
  %164 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %163) #25
  %165 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %163) #25
  %166 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %165, <3 x float> splat (float 0x40029ACA60000000)) #25
  %167 = fmul fast <3 x float> %166, %164
  %168 = shufflevector <3 x float> %167, <3 x float> poison, <3 x i32> zeroinitializer
  %169 = fmul fast <3 x float> %168, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %170 = shufflevector <3 x float> %167, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %171 = fmul fast <3 x float> %170, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %172 = fadd fast <3 x float> %169, %171
  %173 = shufflevector <3 x float> %167, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %174 = fmul fast <3 x float> %173, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %175 = fadd fast <3 x float> %172, %174
  %176 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %175) #25
  %177 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %176) #25
  %178 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %176) #25
  %179 = fmul fast <3 x half> %178, splat (half 0xH2CF4)
  %180 = fadd fast <3 x half> %178, splat (half 0xH2B0A)
  %181 = fmul fast <3 x half> %180, splat (half 0xH3B96)
  %182 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %181, <3 x half> splat (half 0xH40CD)) #25
  %183 = fcmp fast ogt <3 x half> %178, splat (half 0xH292D)
  %184 = select fast <3 x i1> %183, <3 x half> %182, <3 x half> %179
  %185 = fmul fast <3 x half> %184, %177
  %186 = fadd fast <3 x half> %90, %91
  %187 = fadd fast <3 x half> %186, %185
  %188 = insertelement <3 x half> poison, half %4, i64 0
  %189 = shufflevector <3 x half> %188, <3 x half> poison, <3 x i32> zeroinitializer
  %190 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %6, <3 x half> %187, <3 x half> %189) #25
  %191 = insertelement <3 x half> poison, half %2, i64 0
  %192 = shufflevector <3 x half> %191, <3 x half> poison, <3 x i32> zeroinitializer
  %193 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %0, <3 x half> %190, <3 x half> %192) #25
  ret <3 x half> %193
}

; Function Attrs: convergent mustprogress nofree nosync nounwind willreturn memory(argmem: read)
define internal fastcc <3 x half> @_Z23renderBrightAndContrastDv3_DhS_DhDhDhRU9MTLdevice8SSRStats(<3 x half> noundef %0, <3 x half> noundef %1, half noundef %2, half noundef %3, half noundef %4, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(10640) %5) unnamed_addr #20 {
  %7 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %8 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1) #25
  %9 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %5, i64 0, i32 1, i64 2, i32 4
  %10 = load float, ptr addrspace(1) %9, align 4, !tbaa !132
  %11 = fptrunc float %10 to half
  %12 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %5, i64 0, i32 1, i64 3, i32 4
  %13 = load float, ptr addrspace(1) %12, align 4, !tbaa !132
  %14 = fptrunc float %13 to half
  %15 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %5, i64 0, i32 1, i64 5, i32 0
  %16 = load float, ptr addrspace(1) %15, align 4, !tbaa !168
  %17 = fadd fast half %11, 0xHAE66
  %18 = fmul fast half %17, 0xH41B6
  %19 = tail call fast half @air.clamp.f16(half %18, half 0xH0000, half 0xH3C00) #25
  %20 = fmul fast half %19, %19
  %21 = fmul fast half %19, 0xH4000
  %22 = fsub fast half 0xH4200, %21
  %23 = fmul fast half %20, %22
  %24 = tail call fast half @air.mix.f16(half 0xH3C00, half 0xH3266, half %23) #25
  %25 = tail call fast half @air.fmax.f16(half %14, half 0xH1419) #25
  %26 = fdiv fast half %11, %25
  %27 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %5, i64 0, i32 1, i64 6, i32 6
  %28 = load float, ptr addrspace(1) %27, align 4, !tbaa !169
  %29 = getelementptr inbounds %struct.SSRStats.2419, ptr addrspace(1) %5, i64 0, i32 1, i64 6, i32 4
  %30 = load float, ptr addrspace(1) %29, align 4, !tbaa !132
  %31 = fsub fast float %28, %30
  %32 = fptrunc float %31 to half
  %33 = fmul fast half %32, 0xH4D00
  %34 = fpext half %33 to float
  %35 = fadd fast float %34, -2.000000e+00
  %36 = tail call fast float @air.fast_fmin.f32(float %35, float 1.000000e+00) #25
  %37 = tail call fast float @air.fast_fmax.f32(float %36, float 0.000000e+00) #25
  %38 = fptrunc float %37 to half
  %39 = fpext half %4 to float
  %40 = fmul fast float %39, 2.500000e-01
  %41 = fadd fast float %40, -1.500000e+00
  %42 = tail call fast float @air.fast_fmin.f32(float %41, float 1.000000e+00) #25
  %43 = tail call fast float @air.fast_fmax.f32(float %42, float 0.000000e+00) #25
  %44 = fptrunc float %43 to half
  %45 = fpext half %26 to float
  %46 = fmul fast float %45, 4.000000e+00
  %47 = fadd fast float %46, -9.000000e+00
  %48 = tail call fast float @air.fast_fmin.f32(float %47, float 3.000000e+00) #25
  %49 = tail call fast float @air.fast_fmax.f32(float %48, float 1.000000e+00) #25
  %50 = fptrunc float %49 to half
  %51 = tail call fast half @air.fmin.f16(half %38, half %44) #25
  %52 = fpext half %51 to float
  %53 = fmul fast float %52, 3.000000e+00
  %54 = fadd fast float %53, 1.000000e+00
  %55 = fpext half %50 to float
  %56 = fmul fast float %54, %55
  %57 = tail call fast float @air.fast_fmax.f32(float %56, float 1.000000e+00) #25
  %58 = fptrunc float %57 to half
  %59 = fpext half %24 to float
  %60 = fmul fast float %59, 0x3FEB333340000000
  %61 = tail call fast float @air.fast_pow.f32(float 2.000000e+00, float %60) #25
  %62 = fmul fast float %39, 4.000000e+00
  %63 = fmul fast float %62, %61
  %64 = fptrunc float %63 to half
  %65 = insertelement <3 x half> poison, half %64, i64 0
  %66 = shufflevector <3 x half> %65, <3 x half> poison, <3 x i32> zeroinitializer
  %67 = fmul fast <3 x half> %66, %8
  %68 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %67) #25
  %69 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %7, <3 x half> %68, <3 x half> splat (half 0xH34CD)) #25
  %70 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %69) #25
  %71 = fmul fast <3 x half> %70, splat (half 0xH3C36)
  %72 = fadd fast <3 x half> %71, splat (half 0xH2666)
  %73 = fadd fast half %58, 0xHBC00
  %74 = fmul fast half %73, 0xH3800
  %75 = tail call fast half @air.clamp.f16(half %74, half 0xH0000, half 0xH3C00) #25
  %76 = fmul fast half %75, %75
  %77 = fmul fast half %75, 0xH4000
  %78 = fsub fast half 0xH4200, %77
  %79 = fmul fast half %76, %78
  %80 = tail call fast half @air.mix.f16(half 0xH34CD, half 0xH3666, half %79) #25
  %81 = fmul fast <3 x half> %72, splat (half 0xHC600)
  %82 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> splat (half 0xH4000), <3 x half> %81) #25
  %83 = fsub fast <3 x half> splat (half 0xH3C00), %82
  %84 = insertelement <3 x half> poison, half %80, i64 0
  %85 = shufflevector <3 x half> %84, <3 x half> poison, <3 x i32> zeroinitializer
  %86 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %72, <3 x half> %83, <3 x half> %85) #25
  %87 = tail call fast half @air.dot.v3f16(<3 x half> splat (half 0xH3C00), <3 x half> %7) #25
  %88 = fadd fast half %87, 0xHB8CD
  %89 = fmul fast half %88, 0xH4100
  %90 = tail call fast half @air.clamp.f16(half %89, half 0xH0000, half 0xH3C00) #25
  %91 = fmul fast half %90, %90
  %92 = fmul fast half %90, 0xH4000
  %93 = fsub fast half 0xH4200, %92
  %94 = fmul fast half %91, %93
  %95 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %86) #25
  %96 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %86) #25
  %97 = fmul fast <3 x half> %96, splat (half 0xH4A76)
  %98 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %96, <3 x half> splat (half 0xH36AA)) #25
  %99 = fmul fast <3 x half> %98, splat (half 0xH3C38)
  %100 = fadd fast <3 x half> %99, splat (half 0xHAB0A)
  %101 = fcmp fast ogt <3 x half> %96, splat (half 0xH1A69)
  %102 = select fast <3 x i1> %101, <3 x half> %100, <3 x half> %97
  %103 = fmul fast <3 x half> %102, %95
  %104 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %7) #25
  %105 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %7) #25
  %106 = fmul fast <3 x half> %105, splat (half 0xH4A76)
  %107 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %105, <3 x half> splat (half 0xH36AA)) #25
  %108 = fmul fast <3 x half> %107, splat (half 0xH3C38)
  %109 = fadd fast <3 x half> %108, splat (half 0xHAB0A)
  %110 = fcmp fast ogt <3 x half> %105, splat (half 0xH1A69)
  %111 = select fast <3 x i1> %110, <3 x half> %109, <3 x half> %106
  %112 = fmul fast <3 x half> %111, %104
  %113 = tail call fast half @air.dot.v3f16(<3 x half> %103, <3 x half> %103) #25
  %114 = tail call fast half @air.dot.v3f16(<3 x half> splat (half 0xH3C00), <3 x half> %103) #25
  %115 = fdiv fast half %113, %114
  %116 = tail call fast half @air.dot.v3f16(<3 x half> %103, <3 x half> <half 0xH399A, half 0xH3266, half 0xH2E66>) #25
  %117 = tail call fast half @air.mix.f16(half %115, half %116, half %2) #25
  %118 = insertelement <3 x half> poison, half %117, i64 0
  %119 = shufflevector <3 x half> %118, <3 x half> poison, <3 x i32> zeroinitializer
  %120 = fpext half %94 to float
  %121 = fsub fast float 1.000000e+00, %120
  %122 = fmul fast float %121, 0x3FEE680000000000
  %123 = fptrunc float %122 to half
  %124 = insertelement <3 x half> poison, half %123, i64 0
  %125 = shufflevector <3 x half> %124, <3 x half> poison, <3 x i32> zeroinitializer
  %126 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %119, <3 x half> %103, <3 x half> %125) #25
  %127 = fmul fast half %58, 0xH2E66
  %128 = tail call fast half @air.clamp.f16(half %127, half 0xH0000, half 0xH359A) #25
  %129 = fmul fast <3 x half> %112, %112
  %130 = insertelement <3 x half> poison, half %128, i64 0
  %131 = shufflevector <3 x half> %130, <3 x half> poison, <3 x i32> zeroinitializer
  %132 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %112, <3 x half> %129, <3 x half> %131) #25
  %133 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %132) #25
  %134 = fmul fast <3 x half> %132, splat (half 0xH4C00)
  %135 = fadd fast <3 x half> %134, splat (half 0xHCA00)
  %136 = fmul fast <3 x half> %135, %132
  %137 = fadd fast <3 x half> %136, splat (half 0xH4400)
  %138 = fmul fast <3 x half> %137, %132
  %139 = fcmp fast ole <3 x half> %132, splat (half 0xH3400)
  %140 = select fast <3 x i1> %139, <3 x half> %138, <3 x half> %133
  %141 = fsub fast <3 x half> %140, %132
  %142 = fsub fast <3 x half> splat (half 0xH3C00), %132
  %143 = fmul fast <3 x half> %142, %132
  %144 = fcmp fast ole <3 x half> %126, splat (half 0xH3800)
  %145 = select fast <3 x i1> %144, <3 x half> %143, <3 x half> %141
  %146 = fmul fast <3 x half> %126, splat (half 0xH4000)
  %147 = fadd fast <3 x half> %146, splat (half 0xHBC00)
  %148 = fmul fast <3 x half> %145, %147
  %149 = fadd fast <3 x half> %148, %132
  %150 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %149) #25
  %151 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %132, <3 x half> %150, <3 x half> splat (half 0xH399A)) #25
  %152 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %151) #25
  %153 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %151) #25
  %154 = fmul fast <3 x half> %153, splat (half 0xH2CF4)
  %155 = fadd fast <3 x half> %153, splat (half 0xH2B0A)
  %156 = fmul fast <3 x half> %155, splat (half 0xH3B96)
  %157 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %156, <3 x half> splat (half 0xH40CD)) #25
  %158 = fcmp fast ogt <3 x half> %153, splat (half 0xH292D)
  %159 = select fast <3 x i1> %158, <3 x half> %157, <3 x half> %154
  %160 = fmul fast <3 x half> %159, %152
  %161 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %112) #25
  %162 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %112) #25
  %163 = fmul fast <3 x half> %162, splat (half 0xH2CF4)
  %164 = fadd fast <3 x half> %162, splat (half 0xH2B0A)
  %165 = fmul fast <3 x half> %164, splat (half 0xH3B96)
  %166 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %165, <3 x half> splat (half 0xH40CD)) #25
  %167 = fcmp fast ogt <3 x half> %162, splat (half 0xH292D)
  %168 = select fast <3 x i1> %167, <3 x half> %166, <3 x half> %163
  %169 = fmul fast <3 x half> %168, %161
  %170 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %169, <3 x half> %160, <3 x half> splat (half 0xH399A)) #25
  %171 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %170) #25
  %172 = shufflevector <3 x float> %171, <3 x float> poison, <3 x i32> zeroinitializer
  %173 = fmul fast <3 x float> %172, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %174 = shufflevector <3 x float> %171, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %175 = fmul fast <3 x float> %174, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %176 = fadd fast <3 x float> %173, %175
  %177 = shufflevector <3 x float> %171, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %178 = fmul fast <3 x float> %177, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %179 = fadd fast <3 x float> %176, %178
  %180 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %179) #25
  %181 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %179) #25
  %182 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %181, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %183 = fmul fast <3 x float> %182, %180
  %184 = shufflevector <3 x float> %183, <3 x float> poison, <3 x i32> zeroinitializer
  %185 = fmul fast <3 x float> %184, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %186 = shufflevector <3 x float> %183, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %187 = fmul fast <3 x float> %186, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %188 = fadd fast <3 x float> %185, %187
  %189 = shufflevector <3 x float> %183, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %190 = fmul fast <3 x float> %189, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %191 = fadd fast <3 x float> %188, %190
  %192 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %191) #25
  %193 = extractelement <3 x half> %192, i64 2
  %194 = fcmp fast une half %193, 0xH0000
  %195 = extractelement <3 x half> %192, i64 1
  %196 = fcmp fast une half %195, 0xH0000
  %197 = select i1 %194, i1 true, i1 %196
  br i1 %197, label %198, label %201

198:                                              ; preds = %6
  %199 = tail call fast half @air.atan2.f16(half %193, half %195) #25
  %200 = fadd fast half %199, 0xHBC88
  br label %201

201:                                              ; preds = %198, %6
  %202 = phi half [ %200, %198 ], [ 0xHBC88, %6 ]
  %203 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %169, <3 x half> %160, <3 x half> splat (half 0xH34CD)) #25
  %204 = fmul fast float %52, 0x3FE6666660000000
  %205 = fsub fast float 1.000000e+00, %204
  %206 = tail call fast float @air.fast_fmin.f32(float %47, float 1.000000e+00) #25
  %207 = tail call fast float @air.fast_fmax.f32(float %206, float 0.000000e+00) #25
  %208 = fmul fast float %207, 0x3FE3333340000000
  %209 = fsub fast float 1.000000e+00, %208
  %210 = fptrunc float %209 to half
  %211 = fpext half %210 to float
  %212 = fmul fast float %205, %211
  %213 = fptrunc float %212 to half
  %214 = fsub fast float 1.000000e+00, %16
  %215 = fptrunc float %214 to half
  %216 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %217 = fadd fast <3 x half> %216, splat (half 0xHBC00)
  %218 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %219 = fmul fast half %202, %202
  %220 = fmul fast half %219, 0xHC449
  %221 = tail call fast half @air.exp.f16(half %220) #25
  %222 = fpext half %221 to float
  %223 = tail call fast float @air.fast_saturate.f32(float %222) #25
  %224 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %170, half noundef 0xH34CD) #30
  %225 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %170, <3 x half> %224) #25
  %226 = fptrunc float %223 to half
  %227 = insertelement <3 x half> poison, half %226, i64 0
  %228 = shufflevector <3 x half> %227, <3 x half> poison, <3 x i32> zeroinitializer
  %229 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %170, <3 x half> %225, <3 x half> %228) #25
  %230 = insertelement <3 x half> poison, half %2, i64 0
  %231 = shufflevector <3 x half> %230, <3 x half> poison, <3 x i32> zeroinitializer
  %232 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %203, <3 x half> %229, <3 x half> %231) #25
  %233 = fdiv fast <3 x half> %1, %66
  %234 = tail call fast half @air.dot.v3f16(<3 x half> %233, <3 x half> <half 0xH32D1, half 0xH39B8, half 0xH2C9C>) #25
  %235 = fpext half %234 to float
  %236 = fadd fast float %235, 0x3F1A36E2E0000000
  %237 = tail call fast float @air.fast_fmin.f32(float %236, float 1.000000e+00) #25
  %238 = fmul fast float %39, 5.000000e-01
  %239 = fmul fast float %238, %237
  %240 = fptrunc float %239 to half
  %241 = fadd fast half %240, 0xHB266
  %242 = fmul fast half %241, 0xH4000
  %243 = tail call fast half @air.clamp.f16(half %242, half 0xH0000, half 0xH3C00) #25
  %244 = fmul fast half %243, %243
  %245 = fmul fast half %243, 0xH4000
  %246 = fsub fast half 0xH4200, %245
  %247 = fmul fast half %244, %246
  %248 = tail call fast half @air.pow.f16(half %247, half 0xH3746) #25
  %249 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %233, <3 x half> splat (half 0xH3C00)) #25
  %250 = fpext half %215 to float
  %251 = tail call fast float @air.fast_pow.f32(float %250, float 1.000000e+00) #25
  %252 = fptrunc float %251 to half
  %253 = insertelement <3 x half> poison, half %252, i64 0
  %254 = shufflevector <3 x half> %253, <3 x half> poison, <3 x i32> zeroinitializer
  %255 = fadd fast <3 x half> %254, %249
  %256 = fdiv fast <3 x half> %249, %255
  %257 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %256) #25
  %258 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %257, <3 x half> splat (half 0xH3F33)) #25
  %259 = tail call fast half @air.saturate.f16(half %248) #25
  %260 = insertelement <3 x half> poison, half %259, i64 0
  %261 = shufflevector <3 x half> %260, <3 x half> poison, <3 x i32> zeroinitializer
  %262 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %232, <3 x half> %258, <3 x half> %261) #25
  %263 = fpext half %213 to float
  %264 = fmul fast float %263, 5.000000e-01
  %265 = tail call fast float @air.fast_saturate.f32(float %264) #25
  %266 = fptrunc float %265 to half
  %267 = insertelement <3 x half> poison, half %266, i64 0
  %268 = shufflevector <3 x half> %267, <3 x half> poison, <3 x i32> zeroinitializer
  %269 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %232, <3 x half> %262, <3 x half> %268) #25
  %270 = insertelement <3 x half> poison, half %3, i64 0
  %271 = shufflevector <3 x half> %270, <3 x half> poison, <3 x i32> zeroinitializer
  %272 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %232, <3 x half> %269, <3 x half> %271) #25
  %273 = tail call fast fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %272, half noundef 0xH3C66, half undef, half noundef 0xH4200) #28
  %274 = tail call fast fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %272, half noundef 0xH3C14, half undef, half noundef 0xH4200) #28
  %275 = fadd fast half %3, %2
  %276 = fpext half %275 to float
  %277 = fmul fast float %276, 5.000000e-01
  %278 = tail call fast float @air.fast_saturate.f32(float %277) #25
  %279 = fptrunc float %278 to half
  %280 = insertelement <3 x half> poison, half %279, i64 0
  %281 = shufflevector <3 x half> %280, <3 x half> poison, <3 x i32> zeroinitializer
  %282 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %273, <3 x half> %274, <3 x half> %281) #25
  %283 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %282) #25
  %284 = fadd fast <3 x half> %217, %218
  %285 = fadd fast <3 x half> %284, %283
  ret <3 x half> %285
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_saturate.f32(float) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %0, half noundef %1, half %2, half noundef %3) unnamed_addr #9 {
  %5 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %6 = extractelement <3 x half> %5, i64 0
  %7 = extractelement <3 x half> %5, i64 1
  %8 = fadd fast half %6, %7
  %9 = extractelement <3 x half> %5, i64 2
  %10 = fadd fast half %8, %9
  %11 = fdiv fast half 0xH3C00, %10
  %12 = fmul fast half %11, %6
  %13 = fmul fast half %11, %7
  %14 = fmul fast half %11, %9
  %15 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %5) #25
  %16 = shufflevector <3 x float> %15, <3 x float> poison, <3 x i32> zeroinitializer
  %17 = fmul fast <3 x float> %16, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %18 = shufflevector <3 x float> %15, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %19 = fmul fast <3 x float> %18, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %20 = fadd fast <3 x float> %17, %19
  %21 = shufflevector <3 x float> %15, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %22 = fmul fast <3 x float> %21, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %23 = fadd fast <3 x float> %20, %22
  %24 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %23) #25
  %25 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %23) #25
  %26 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %25, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %27 = fmul fast <3 x float> %26, %24
  %28 = shufflevector <3 x float> %27, <3 x float> poison, <3 x i32> zeroinitializer
  %29 = fmul fast <3 x float> %28, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %30 = shufflevector <3 x float> %27, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %31 = fmul fast <3 x float> %30, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %32 = fadd fast <3 x float> %29, %31
  %33 = shufflevector <3 x float> %27, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %34 = fmul fast <3 x float> %33, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %35 = fadd fast <3 x float> %32, %34
  %36 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %35) #25
  %37 = shufflevector <3 x half> %36, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %38 = tail call fast half @air.dot.v2f16(<2 x half> %37, <2 x half> %37) #25
  %39 = tail call fast half @air.sqrt.f16(half %38) #25
  %40 = extractelement <3 x half> %36, i64 2
  %41 = fcmp fast une half %40, 0xH0000
  %42 = extractelement <3 x half> %36, i64 1
  %43 = fcmp fast une half %42, 0xH0000
  %44 = select i1 %41, i1 true, i1 %43
  br i1 %44, label %45, label %47

45:                                               ; preds = %4
  %46 = tail call fast half @air.atan2.f16(half %40, half %42) #25
  br label %47

47:                                               ; preds = %45, %4
  %48 = phi fast half [ %46, %45 ], [ 0xH0000, %4 ]
  %49 = fmul fast half %39, %1
  %50 = fpext half %12 to float
  %51 = insertelement <2 x float> undef, float %50, i64 0
  %52 = fpext half %13 to float
  %53 = insertelement <2 x float> %51, float %52, i64 1
  %54 = fadd fast <2 x float> %53, splat (float 0xBFD55553E0000000)
  %55 = tail call fast float @air.dot.v2f32(<2 x float> %54, <2 x float> %54) #25
  %56 = tail call fast float @air.fast_sqrt.f32(float %55) #25
  %57 = fptrunc float %56 to half
  %58 = fpext half %14 to float
  %59 = insertelement <2 x float> %51, float %58, i64 1
  %60 = fadd fast <2 x float> %59, splat (float 0xBFD55553E0000000)
  %61 = tail call fast float @air.dot.v2f32(<2 x float> %60, <2 x float> %60) #25
  %62 = tail call fast float @air.fast_sqrt.f32(float %61) #25
  %63 = fptrunc float %62 to half
  %64 = insertelement <2 x float> undef, float %52, i64 0
  %65 = insertelement <2 x float> %64, float %58, i64 1
  %66 = fadd fast <2 x float> %65, splat (float 0xBFD55553E0000000)
  %67 = tail call fast float @air.dot.v2f32(<2 x float> %66, <2 x float> %66) #25
  %68 = tail call fast float @air.fast_sqrt.f32(float %67) #25
  %69 = fptrunc float %68 to half
  %70 = tail call fast half @air.fmax3.f16(half %57, half %63, half %69) #25
  %71 = tail call fast half @air.sqrt.f16(half %70) #25
  %72 = tail call fast half @air.clamp.f16(half %71, half 0xH0000, half 0xH3C00) #25
  %73 = fmul fast half %72, %72
  %74 = fmul fast half %72, 0xH4000
  %75 = fsub fast half 0xH4200, %74
  %76 = fmul fast half %73, %75
  %77 = fpext half %76 to float
  %78 = fsub fast float 1.000000e+00, %77
  %79 = fmul fast float %77, 2.000000e+00
  %80 = fmul fast float %79, %78
  %81 = tail call fast float @air.fast_fmin.f32(float %80, float 1.000000e+00) #25
  %82 = fptrunc float %81 to half
  %83 = fcmp fast ogt half %1, 0xH3A00
  %84 = fcmp fast ogt half %3, 0xH4200
  %85 = select i1 %83, i1 %84, i1 false
  br i1 %85, label %86, label %92

86:                                               ; preds = %47
  %87 = fpext half %1 to float
  %88 = fadd fast float %87, -7.500000e-01
  %89 = fpext half %82 to float
  %90 = fadd fast float %88, %89
  %91 = tail call fast float @air.fast_fmin.f32(float %90, float 1.000000e+00) #25
  br label %94

92:                                               ; preds = %47
  %93 = fpext half %82 to float
  br label %94

94:                                               ; preds = %92, %86
  %95 = phi fast float [ %91, %86 ], [ %93, %92 ]
  %96 = fptrunc float %95 to half
  %97 = extractelement <3 x half> %36, i64 0
  %98 = fmul fast half %97, %96
  %99 = tail call fast half @air.mix.f16(half %39, half %49, half %98) #25
  %100 = tail call fast half @air.cos.f16(half %48) #25
  %101 = fmul fast half %100, %99
  %102 = insertelement <3 x half> %36, half %101, i64 1
  %103 = tail call fast half @air.sin.f16(half %48) #25
  %104 = fmul fast half %103, %99
  %105 = insertelement <3 x half> %102, half %104, i64 2
  %106 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %105) #25
  %107 = shufflevector <3 x float> %106, <3 x float> poison, <3 x i32> zeroinitializer
  %108 = shufflevector <3 x float> %106, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %109 = fmul fast <3 x float> %108, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %110 = fadd fast <3 x float> %109, %107
  %111 = shufflevector <3 x float> %106, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %112 = fmul fast <3 x float> %111, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %113 = fadd fast <3 x float> %110, %112
  %114 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %113) #25
  %115 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %113) #25
  %116 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %115, <3 x float> splat (float 0x40029ACA60000000)) #25
  %117 = fmul fast <3 x float> %116, %114
  %118 = shufflevector <3 x float> %117, <3 x float> poison, <3 x i32> zeroinitializer
  %119 = fmul fast <3 x float> %118, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %120 = shufflevector <3 x float> %117, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %121 = fmul fast <3 x float> %120, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %122 = fadd fast <3 x float> %119, %121
  %123 = shufflevector <3 x float> %117, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %124 = fmul fast <3 x float> %123, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %125 = fadd fast <3 x float> %122, %124
  %126 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %125) #25
  %127 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %126) #25
  %128 = fadd fast half %1, 0xHBC00
  %129 = fmul fast half %128, %3
  %130 = fadd fast half %129, 0xH3C00
  %131 = insertelement <3 x half> poison, half %130, i64 0
  %132 = shufflevector <3 x half> %131, <3 x half> poison, <3 x i32> zeroinitializer
  %133 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %127, <3 x half> %132) #25
  %134 = tail call fast half @air.dot.v3f16(<3 x half> %133, <3 x half> splat (half 0xH3555)) #25
  %135 = fcmp fast ogt half %134, 0xH0000
  br i1 %135, label %136, label %144

136:                                              ; preds = %94
  %137 = tail call fast half @air.dot.v3f16(<3 x half> %127, <3 x half> splat (half 0xH3555)) #25
  %138 = insertelement <3 x half> poison, half %134, i64 0
  %139 = shufflevector <3 x half> %138, <3 x half> poison, <3 x i32> zeroinitializer
  %140 = insertelement <3 x half> poison, half %137, i64 0
  %141 = shufflevector <3 x half> %140, <3 x half> poison, <3 x i32> zeroinitializer
  %142 = fmul fast <3 x half> %141, %133
  %143 = fdiv fast <3 x half> %142, %139
  br label %144

144:                                              ; preds = %136, %94
  %145 = phi fast <3 x half> [ %143, %136 ], [ zeroinitializer, %94 ]
  %146 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %147 = fadd fast <3 x half> %146, splat (half 0xHBC00)
  %148 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %149 = fpext half %48 to float
  %150 = fadd fast float %149, 0xBFFE666660000000
  %151 = fmul fast float %150, %150
  %152 = fmul fast float %151, 0xC00638E380000000
  %153 = tail call fast float @air.fast_exp.f32(float %152) #25
  %154 = fsub fast float 1.000000e+00, %153
  %155 = tail call fast float @air.fast_fmax.f32(float %154, float 5.000000e-01) #25
  %156 = fptrunc float %155 to half
  %157 = fmul fast half %97, %97
  %158 = fpext half %157 to float
  %159 = fsub fast float 1.000000e+00, %158
  %160 = fpext half %96 to float
  %161 = fmul fast float %159, %160
  %162 = fpext half %156 to float
  %163 = fmul fast float %161, %162
  %164 = fptrunc float %163 to half
  %165 = insertelement <3 x half> poison, half %164, i64 0
  %166 = shufflevector <3 x half> %165, <3 x half> poison, <3 x i32> zeroinitializer
  %167 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %127, <3 x half> %145, <3 x half> %166) #25
  %168 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %167) #25
  %169 = fadd fast <3 x half> %147, %148
  %170 = fadd fast <3 x half> %169, %168
  ret <3 x half> %170
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_fmax.f32(float, float) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_sqrt.f32(float) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.dot.v2f32(<2 x float>, <2 x float>) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.saturate.f16(half) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_pow.f32(float, float) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z16highlightRecoverDv3_DhDhDhDhDh(<3 x half> noundef %0, half noundef %1, half %2, half %3, half noundef %4) unnamed_addr #21 {
  %6 = shufflevector <3 x half> %0, <3 x half> poison, <3 x i32> zeroinitializer
  %7 = fmul fast <3 x half> %6, <half 0xH383C, half 0xH2E4C, half 0xH2452>
  %8 = shufflevector <3 x half> %0, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %9 = fmul fast <3 x half> %8, <half 0xH3548, half 0xH3AFD, half 0xH2F88>
  %10 = fadd fast <3 x half> %7, %9
  %11 = shufflevector <3 x half> %0, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %12 = fmul fast <3 x half> %11, <half 0xH307F, half 0xH2734, half 0xH3AEC>
  %13 = fadd fast <3 x half> %10, %12
  %14 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %13, <3 x half> splat (half 0xH3872)) #25
  %15 = fmul fast half %4, 0xH4000
  %16 = fadd fast half %15, 0xH3C00
  %17 = extractelement <3 x half> %14, i64 0
  %18 = extractelement <3 x half> %14, i64 1
  %19 = extractelement <3 x half> %14, i64 2
  %20 = tail call fast half @air.fmin3.f16(half %17, half %18, half %19) #25
  %21 = tail call fast half @air.dot.v3f16(<3 x half> %14, <3 x half> splat (half 0xH3555)) #25
  %22 = tail call fast half @air.mix.f16(half %20, half %21, half 0xH3800) #25
  %23 = tail call fast half @air.pow.f16(half %22, half %16) #25
  %24 = fcmp fast ogt half %22, 0xH0000
  br i1 %24, label %25, label %32

25:                                               ; preds = %5
  %26 = insertelement <3 x half> poison, half %23, i64 0
  %27 = shufflevector <3 x half> %26, <3 x half> poison, <3 x i32> zeroinitializer
  %28 = fmul fast <3 x half> %27, %14
  %29 = insertelement <3 x half> poison, half %22, i64 0
  %30 = shufflevector <3 x half> %29, <3 x half> poison, <3 x i32> zeroinitializer
  %31 = fdiv fast <3 x half> %28, %30
  br label %32

32:                                               ; preds = %25, %5
  %33 = phi fast <3 x half> [ %31, %25 ], [ zeroinitializer, %5 ]
  %34 = insertelement <3 x half> poison, half %20, i64 0
  %35 = shufflevector <3 x half> %34, <3 x half> poison, <3 x i32> zeroinitializer
  %36 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %14, <3 x half> %33, <3 x half> %35) #25
  %37 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %36, <3 x half> splat (half 0xH3F33)) #25
  %38 = shufflevector <3 x half> %37, <3 x half> poison, <3 x i32> zeroinitializer
  %39 = fmul fast <3 x half> %38, <half 0xH4011, half 0xHB353, half 0xHA060>
  %40 = shufflevector <3 x half> %37, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %41 = fmul fast <3 x half> %40, <half 0xHB9D2, half 0xH3CED, half 0xHB0E8>
  %42 = fadd fast <3 x half> %39, %41
  %43 = shufflevector <3 x half> %37, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %44 = fmul fast <3 x half> %43, <half 0xHB4E9, half 0xH99DE, half 0xH3CA6>
  %45 = fadd fast <3 x half> %42, %44
  %46 = fmul fast half %23, %1
  %47 = fdiv fast half %46, %22
  %48 = select i1 %24, half %47, half 0xH0000
  %49 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %45, <3 x half> %0, <3 x half> splat (half 0xH3400)) #25
  %50 = extractelement <3 x half> %49, i64 0
  %51 = extractelement <3 x half> %49, i64 1
  %52 = fadd fast half %50, %51
  %53 = extractelement <3 x half> %49, i64 2
  %54 = fadd fast half %52, %53
  %55 = tail call fast half @air.dot.v3f16(<3 x half> %49, <3 x half> splat (half 0xH3555)) #25
  %56 = tail call fast half @air.fmax.f16(half %55, half 0xH0000) #25
  %57 = tail call fast half @air.sqrt.f16(half %56) #25
  %58 = fmul fast half %4, 0xH3E00
  %59 = tail call fast half @air.mix.f16(half %1, half %48, half %20) #25
  %60 = tail call fast half @air.mix.f16(half %59, half %1, half 0xH3400) #25
  %61 = fmul fast half %60, 0xH4200
  %62 = fsub fast half %54, %61
  %63 = fmul fast half %62, %58
  %64 = fadd fast half %63, %54
  %65 = tail call fast half @air.fmax.f16(half %54, half 0xH068E) #25
  %66 = fdiv fast half %64, %65
  %67 = fpext half %66 to float
  %68 = fadd fast float %67, -1.000000e+00
  %69 = fmul fast float %68, 0x3FF922D0E0000000
  %70 = fptrunc float %69 to half
  %71 = fpext half %70 to float
  %72 = tail call fast half @air.fabs.f16(half %70) #25
  %73 = fpext half %72 to float
  %74 = fadd fast float %73, 1.000000e+00
  %75 = fdiv fast float %71, %74
  %76 = fptrunc float %75 to half
  %77 = fpext half %76 to float
  %78 = fcmp fast oge half %76, 0xH0000
  %79 = select i1 %78, float 0x3FE4CCCCC0000000, float 7.500000e-01
  %80 = fmul fast float %79, %77
  %81 = fadd fast float %80, 1.000000e+00
  %82 = fptrunc float %81 to half
  %83 = fsub fast half 0xH3C00, %58
  %84 = fmul fast half %4, 0xH3B34
  %85 = fadd fast half %84, 0xH3C00
  %86 = tail call fast half @air.clamp.f16(half %82, half %83, half %85) #25
  %87 = insertelement <3 x half> poison, half %86, i64 0
  %88 = shufflevector <3 x half> %87, <3 x half> poison, <3 x i32> zeroinitializer
  %89 = fmul fast <3 x half> %88, %49
  %90 = insertelement <3 x half> poison, half %57, i64 0
  %91 = shufflevector <3 x half> %90, <3 x half> poison, <3 x i32> zeroinitializer
  %92 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %49, <3 x half> %89, <3 x half> %91) #25
  ret <3 x half> %92
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(argmem: read)
define internal fastcc <3 x half> @_Z21renderSkinAdjustmentsDv3_DhRU9MTLdevice15SSRFGAdjustmentDhDh(<3 x half> noundef %0, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(64) %1, half noundef %2, half noundef %3) unnamed_addr #22 {
  %5 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> <half 0xH3C00, half 0xH399A, half 0xH3866>) #25
  %6 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> <half 0xH3C00, half 0xH399A, half 0xH3866>) #25
  %7 = fmul fast <3 x half> %6, splat (half 0xH2CF4)
  %8 = fadd fast <3 x half> %6, splat (half 0xH2B0A)
  %9 = fmul fast <3 x half> %8, splat (half 0xH3B96)
  %10 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %9, <3 x half> splat (half 0xH40CD)) #25
  %11 = fcmp fast ogt <3 x half> %6, splat (half 0xH292D)
  %12 = select fast <3 x i1> %11, <3 x half> %10, <3 x half> %7
  %13 = fmul fast <3 x half> %12, %5
  %14 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %1, i64 0, i32 10
  %15 = load float, ptr addrspace(1) %14, align 4, !tbaa !170
  %16 = tail call fast float @air.fast_fabs.f32(float %15) #25
  %17 = fcmp fast olt float %16, 0x3EE4F8B580000000
  br i1 %17, label %73, label %18

18:                                               ; preds = %4
  %19 = fptrunc float %15 to half
  %20 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %21 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %22 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %23 = tail call fast half @air.dot.v3f16(<3 x half> %22, <3 x half> splat (half 0xH3555)) #25
  %24 = tail call fast half @air.sqrt.f16(half %23) #25
  %25 = fpext half %24 to float
  %26 = fsub fast float 1.000000e+00, %25
  %27 = fmul fast float %26, %25
  %28 = fptrunc float %27 to half
  %29 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %22) #25
  %30 = tail call fast half @air.sqrt.f16(half %3) #25
  %31 = fmul fast half %28, %19
  %32 = fmul fast half %31, 0xH4000
  %33 = fmul fast half %31, 0xHC000
  %34 = fmul fast half %33, %30
  %35 = fpext half %32 to float
  %36 = fmul fast float %35, 0x3FD322D0E0000000
  %37 = fptrunc float %36 to half
  %38 = insertelement <3 x half> poison, half %37, i64 0
  %39 = fmul fast <3 x half> %29, %38
  %40 = shufflevector <3 x half> %39, <3 x half> poison, <3 x i32> zeroinitializer
  %41 = shufflevector <3 x half> %29, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %42 = fmul fast float %35, 0x3FE2C8B440000000
  %43 = fptrunc float %42 to half
  %44 = insertelement <3 x half> poison, half %43, i64 0
  %45 = shufflevector <3 x half> %44, <3 x half> poison, <3 x i32> zeroinitializer
  %46 = fmul fast <3 x half> %41, %45
  %47 = shufflevector <3 x half> %29, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %48 = fmul fast float %35, 0x3FBD2F1AA0000000
  %49 = fptrunc float %48 to half
  %50 = insertelement <3 x half> poison, half %49, i64 0
  %51 = shufflevector <3 x half> %50, <3 x half> poison, <3 x i32> zeroinitializer
  %52 = fmul fast <3 x half> %47, %51
  %53 = insertelement <3 x half> poison, half %34, i64 0
  %54 = shufflevector <3 x half> %53, <3 x half> poison, <3 x i32> zeroinitializer
  %55 = fadd fast <3 x half> %46, %29
  %56 = fadd fast <3 x half> %55, %40
  %57 = fadd fast <3 x half> %56, %52
  %58 = fadd fast <3 x half> %57, %54
  %59 = insertelement <3 x half> poison, half %30, i64 0
  %60 = shufflevector <3 x half> %59, <3 x half> poison, <3 x i32> zeroinitializer
  %61 = fmul fast half %31, 0xHC000
  %62 = insertelement <3 x half> poison, half %61, i64 0
  %63 = shufflevector <3 x half> %62, <3 x half> poison, <3 x i32> zeroinitializer
  %64 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %29, <3 x half> %60, <3 x half> %63) #25
  %65 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %64, <3 x half> %58, <3 x half> splat (half 0xH3A66)) #25
  %66 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %65, <3 x half> zeroinitializer) #25
  %67 = fmul fast <3 x half> %66, %66
  %68 = fadd fast <3 x half> %20, splat (half 0xHBC00)
  %69 = fadd fast <3 x half> %68, %21
  %70 = fadd fast <3 x half> %69, %67
  %71 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %70, <3 x half> %0) #25
  %72 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %70, <3 x half> %71, <3 x half> splat (half 0xH3C00)) #25
  br label %73

73:                                               ; preds = %18, %4
  %74 = phi <3 x half> [ %0, %4 ], [ %72, %18 ]
  %75 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %1, i64 0, i32 9
  %76 = load float, ptr addrspace(1) %75, align 4, !tbaa !171
  %77 = tail call fast float @air.fast_fabs.f32(float %76) #25
  %78 = fcmp fast olt float %77, 0x3EE4F8B580000000
  br i1 %78, label %120, label %79

79:                                               ; preds = %73
  %80 = fmul fast float %76, 2.000000e+00
  %81 = fptrunc float %80 to half
  %82 = tail call fast half @air.dot.v3f16(<3 x half> %74, <3 x half> <half 0xH3800, half 0xH34CD, half 0xH3266>) #25
  %83 = extractelement <3 x half> %74, i64 0
  %84 = extractelement <3 x half> %74, i64 1
  %85 = fadd fast half %83, %84
  %86 = extractelement <3 x half> %74, i64 2
  %87 = fadd fast half %85, %86
  %88 = fdiv fast half 0xH3C00, %87
  %89 = fmul fast half %88, %83
  %90 = fmul fast half %88, %84
  %91 = fmul fast half %88, %86
  %92 = tail call fast half @air.fmax.f16(half %89, half %90) #25
  %93 = tail call fast half @air.fmax.f16(half %90, half %91) #25
  %94 = fadd fast half %82, 0xHB666
  %95 = fmul fast half %94, 0xH3EAA
  %96 = tail call fast half @air.clamp.f16(half %95, half 0xH0000, half 0xH3C00) #25
  %97 = fmul fast half %96, 0xH4000
  %98 = fsub fast half 0xH4200, %97
  %99 = fadd fast half %92, 0xHB555
  %100 = fadd fast half %99, %93
  %101 = fmul fast half %100, 0xH3DFF
  %102 = tail call fast half @air.clamp.f16(half %101, half 0xH0000, half 0xH3C00) #25
  %103 = fmul fast half %102, %102
  %104 = fmul fast half %102, 0xH4000
  %105 = fsub fast half 0xH4200, %104
  %106 = fmul fast half %103, %105
  %107 = fmul fast <3 x half> %13, %74
  %108 = fmul fast half %96, %96
  %109 = fmul fast half %108, %81
  %110 = fmul fast half %109, %98
  %111 = fpext half %110 to float
  %112 = fpext half %106 to float
  %113 = fsub fast float 1.000000e+00, %112
  %114 = fmul fast float %113, %111
  %115 = tail call fast float @air.fast_fmin.f32(float %114, float 1.000000e+00) #25
  %116 = fptrunc float %115 to half
  %117 = insertelement <3 x half> poison, half %116, i64 0
  %118 = shufflevector <3 x half> %117, <3 x half> poison, <3 x i32> zeroinitializer
  %119 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %74, <3 x half> %107, <3 x half> %118) #25
  br label %120

120:                                              ; preds = %79, %73
  %121 = phi <3 x half> [ %74, %73 ], [ %119, %79 ]
  %122 = insertelement <3 x half> poison, half %2, i64 0
  %123 = shufflevector <3 x half> %122, <3 x half> poison, <3 x i32> zeroinitializer
  %124 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %0, <3 x half> %121, <3 x half> %123) #25
  ret <3 x half> %124
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z15smoothSatFilterDv3_DhDh(<3 x half> noundef %0, half noundef %1) unnamed_addr #9 {
  %3 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %4 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %3) #25
  %5 = shufflevector <3 x float> %4, <3 x float> poison, <3 x i32> zeroinitializer
  %6 = fmul fast <3 x float> %5, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %7 = shufflevector <3 x float> %4, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %8 = fmul fast <3 x float> %7, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %9 = fadd fast <3 x float> %6, %8
  %10 = shufflevector <3 x float> %4, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %11 = fmul fast <3 x float> %10, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %12 = fadd fast <3 x float> %9, %11
  %13 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %12) #25
  %14 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %12) #25
  %15 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %14, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %16 = fmul fast <3 x float> %15, %13
  %17 = shufflevector <3 x float> %16, <3 x float> poison, <3 x i32> zeroinitializer
  %18 = fmul fast <3 x float> %17, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %19 = shufflevector <3 x float> %16, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %20 = fmul fast <3 x float> %19, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %21 = fadd fast <3 x float> %18, %20
  %22 = shufflevector <3 x float> %16, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %23 = fmul fast <3 x float> %22, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %24 = fadd fast <3 x float> %21, %23
  %25 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %24) #25
  %26 = extractelement <3 x half> %25, i64 2
  %27 = fcmp fast une half %26, 0xH0000
  %28 = extractelement <3 x half> %25, i64 1
  %29 = fcmp fast une half %28, 0xH0000
  %30 = select i1 %27, i1 true, i1 %29
  br i1 %30, label %31, label %33

31:                                               ; preds = %2
  %32 = tail call fast half @air.atan2.f16(half %26, half %28) #25
  br label %33

33:                                               ; preds = %31, %2
  %34 = phi fast half [ %32, %31 ], [ 0xH0000, %2 ]
  %35 = shufflevector <3 x half> %25, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %36 = tail call fast half @air.dot.v2f16(<2 x half> %35, <2 x half> %35) #25
  %37 = tail call fast half @air.sqrt.f16(half %36) #25
  %38 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %39 = fadd fast <3 x half> %38, splat (half 0xHBC00)
  %40 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %41 = fmul fast half %37, %1
  %42 = tail call fast half @air.cos.f16(half %34) #25
  %43 = fmul fast half %42, %41
  %44 = insertelement <3 x half> %25, half %43, i64 1
  %45 = tail call fast half @air.sin.f16(half %34) #25
  %46 = fmul fast half %45, %41
  %47 = insertelement <3 x half> %44, half %46, i64 2
  %48 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %47) #25
  %49 = shufflevector <3 x float> %48, <3 x float> poison, <3 x i32> zeroinitializer
  %50 = shufflevector <3 x float> %48, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %51 = fmul fast <3 x float> %50, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %52 = fadd fast <3 x float> %51, %49
  %53 = shufflevector <3 x float> %48, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %54 = fmul fast <3 x float> %53, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %55 = fadd fast <3 x float> %52, %54
  %56 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %55) #25
  %57 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %55) #25
  %58 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %57, <3 x float> splat (float 0x40029ACA60000000)) #25
  %59 = fmul fast <3 x float> %58, %56
  %60 = shufflevector <3 x float> %59, <3 x float> poison, <3 x i32> zeroinitializer
  %61 = fmul fast <3 x float> %60, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %62 = shufflevector <3 x float> %59, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %63 = fmul fast <3 x float> %62, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %64 = fadd fast <3 x float> %61, %63
  %65 = shufflevector <3 x float> %59, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %66 = fmul fast <3 x float> %65, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %67 = fadd fast <3 x float> %64, %66
  %68 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %67) #25
  %69 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %68) #25
  %70 = fadd fast <3 x half> %39, %40
  %71 = fadd fast <3 x half> %70, %69
  %72 = fpext half %1 to float
  %73 = fcmp fast olt float %72, 0x3F947AE140000000
  %74 = shufflevector <3 x half> %71, <3 x half> poison, <3 x i32> <i32 1, i32 1, i32 1>
  %75 = select fast i1 %73, <3 x half> %74, <3 x half> %71
  ret <3 x half> %75
}

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(read)
define internal fastcc <3 x half> @_Z19renderFGAdjustmentsDv3_DhS_DhDhDhDhRU9MTLdevice15SSRFGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE(<3 x half> noundef %0, <3 x half> noundef %1, half noundef %2, half %3, half noundef %4, half noundef %5, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(64) %6, ptr addrspace(1) %7) unnamed_addr #12 {
  %9 = fpext half %2 to float
  %10 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %6, i64 0, i32 0
  %11 = load float, ptr addrspace(1) %10, align 4, !tbaa !172
  %12 = fsub fast float 1.000000e+00, %11
  %13 = fmul fast float %12, %9
  %14 = fptrunc float %13 to half
  %15 = insertelement <3 x half> poison, half %14, i64 0
  %16 = shufflevector <3 x half> %15, <3 x half> poison, <3 x i32> zeroinitializer
  %17 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %0, <3 x half> %1, <3 x half> %16) #25
  %18 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %6, i64 0, i32 4
  %19 = load float, ptr addrspace(1) %18, align 4, !tbaa !173
  %20 = tail call fast float @air.fast_fabs.f32(float %19) #25
  %21 = fcmp fast olt float %20, 0x3EE4F8B580000000
  br i1 %21, label %25, label %22

22:                                               ; preds = %8
  %23 = fptrunc float %19 to half
  %24 = tail call fast fastcc <3 x half> @_Z11whitesCurveDv3_DhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEEDhDh(<3 x half> noundef %17, ptr addrspace(1) %7, half noundef %23, half noundef 0xH3C00) #29
  br label %25

25:                                               ; preds = %22, %8
  %26 = phi <3 x half> [ %17, %8 ], [ %24, %22 ]
  %27 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %6, i64 0, i32 6
  %28 = load float, ptr addrspace(1) %27, align 4, !tbaa !174
  %29 = tail call fast float @air.fast_fabs.f32(float %28) #25
  %30 = fcmp fast olt float %29, 0x3EE4F8B580000000
  br i1 %30, label %38, label %31

31:                                               ; preds = %25
  %32 = fcmp fast ogt float %28, 0.000000e+00
  %33 = fptrunc float %28 to half
  br i1 %32, label %34, label %36

34:                                               ; preds = %31
  %35 = tail call fast fastcc <3 x half> @_Z13ShadowsFilterDv3_DhDhDh(<3 x half> noundef %26, half noundef %5, half noundef %33) #28
  br label %38

36:                                               ; preds = %31
  %37 = tail call fast fastcc <3 x half> @_Z21ShadowsNegativeFilterDv3_DhDhDh(<3 x half> noundef %26, half noundef %5, half noundef %33) #28
  br label %38

38:                                               ; preds = %36, %34, %25
  %39 = phi <3 x half> [ %26, %25 ], [ %35, %34 ], [ %37, %36 ]
  %40 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %6, i64 0, i32 15
  %41 = load float, ptr addrspace(1) %40, align 4, !tbaa !175
  %42 = tail call fast float @air.fast_fabs.f32(float %41) #25
  %43 = fcmp fast olt float %42, 0x3EE4F8B580000000
  br i1 %43, label %47, label %44

44:                                               ; preds = %38
  %45 = fptrunc float %41 to half
  %46 = tail call fast fastcc <3 x half> @_Z19tonalContrastFilterDv3_DhDhDh(<3 x half> noundef %39, half noundef %4, half noundef %45) #28
  br label %47

47:                                               ; preds = %44, %38
  %48 = phi <3 x half> [ %39, %38 ], [ %46, %44 ]
  %49 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %6, i64 0, i32 7
  %50 = load float, ptr addrspace(1) %49, align 4, !tbaa !176
  %51 = tail call fast float @air.fast_fabs.f32(float %50) #25
  %52 = fcmp fast olt float %51, 0x3EE4F8B580000000
  br i1 %52, label %56, label %53

53:                                               ; preds = %47
  %54 = fptrunc float %50 to half
  %55 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %48, half noundef %54) #28
  br label %56

56:                                               ; preds = %53, %47
  %57 = phi <3 x half> [ %48, %47 ], [ %55, %53 ]
  %58 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %6, i64 0, i32 11
  %59 = load float, ptr addrspace(1) %58, align 4, !tbaa !177
  %60 = tail call fast float @air.fast_fabs.f32(float %59) #25
  %61 = fcmp fast olt float %60, 0x3EE4F8B580000000
  br i1 %61, label %70, label %62

62:                                               ; preds = %56
  %63 = fcmp fast ogt float %59, 0.000000e+00
  %64 = fadd fast float %59, 1.000000e+00
  %65 = fptrunc float %64 to half
  br i1 %63, label %66, label %68

66:                                               ; preds = %62
  %67 = tail call fast fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %57, half noundef %65, half undef, half noundef 0xH4200) #28
  br label %70

68:                                               ; preds = %62
  %69 = tail call fast fastcc <3 x half> @_Z15smoothSatFilterDv3_DhDh(<3 x half> noundef %57, half noundef %65) #28
  br label %70

70:                                               ; preds = %68, %66, %56
  %71 = phi <3 x half> [ %57, %56 ], [ %67, %66 ], [ %69, %68 ]
  %72 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %6, i64 0, i32 5
  %73 = load float, ptr addrspace(1) %72, align 4, !tbaa !178
  %74 = fadd fast float %73, -1.000000e+00
  %75 = tail call fast float @air.fast_fabs.f32(float %74) #25
  %76 = fcmp fast olt float %75, 0x3EE4F8B580000000
  br i1 %76, label %80, label %77

77:                                               ; preds = %70
  %78 = fptrunc float %73 to half
  %79 = tail call fast fastcc <3 x half> @_Z10airyFilterDv3_DhDh(<3 x half> noundef %71, half noundef %78) #28
  br label %80

80:                                               ; preds = %77, %70
  %81 = phi <3 x half> [ %71, %70 ], [ %79, %77 ]
  %82 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %6, i64 0, i32 2
  %83 = load float, ptr addrspace(1) %82, align 4, !tbaa !179
  %84 = tail call fast float @air.fast_fabs.f32(float %83) #25
  %85 = fcmp fast olt float %84, 0x3EE4F8B580000000
  br i1 %85, label %106, label %86

86:                                               ; preds = %80
  %87 = fptrunc float %83 to half
  %88 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %81, <3 x half> zeroinitializer) #25
  %89 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %81, <3 x half> splat (half 0xH3C00)) #25
  %90 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %81) #25
  %91 = extractelement <3 x half> %90, i64 0
  %92 = extractelement <3 x half> %90, i64 1
  %93 = extractelement <3 x half> %90, i64 2
  %94 = tail call fast half @air.fmax3.f16(half %91, half %92, half %93) #25
  %95 = tail call fast half @air.pow.f16(half %94, half 0xH3800) #25
  %96 = fsub fast half 0xH3C00, %95
  %97 = fmul fast half %96, %87
  %98 = fadd fast half %97, 0xH3C00
  %99 = insertelement <3 x half> poison, half %98, i64 0
  %100 = shufflevector <3 x half> %99, <3 x half> poison, <3 x i32> zeroinitializer
  %101 = fmul fast <3 x half> %100, %90
  %102 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %101) #25
  %103 = fadd fast <3 x half> %88, splat (half 0xHBC00)
  %104 = fadd fast <3 x half> %103, %89
  %105 = fadd fast <3 x half> %104, %102
  br label %106

106:                                              ; preds = %86, %80
  %107 = phi <3 x half> [ %81, %80 ], [ %105, %86 ]
  %108 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %6, i64 0, i32 14
  %109 = load float, ptr addrspace(1) %108, align 4, !tbaa !180
  %110 = tail call fast float @air.fast_fabs.f32(float %109) #25
  %111 = fcmp fast olt float %110, 0x3EE4F8B580000000
  br i1 %111, label %115, label %112

112:                                              ; preds = %106
  %113 = fptrunc float %109 to half
  %114 = tail call fast fastcc <3 x half> @_Z15underToneFilterDv3_DhDhDh(<3 x half> noundef %107, half noundef %4, half noundef %113) #28
  br label %115

115:                                              ; preds = %112, %106
  %116 = phi <3 x half> [ %107, %106 ], [ %114, %112 ]
  %117 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %6, i64 0, i32 3
  %118 = load float, ptr addrspace(1) %117, align 4, !tbaa !181
  %119 = fmul fast float %118, 5.000000e-01
  %120 = fcmp fast ule float %118, 0.000000e+00
  %121 = tail call fast float @air.fast_fabs.f32(float %119) #25
  %122 = fcmp fast olt float %121, 0x3EE4F8B580000000
  %123 = select i1 %120, i1 true, i1 %122
  br i1 %123, label %131, label %124

124:                                              ; preds = %115
  %125 = fcmp fast ogt float %119, 0.000000e+00
  %126 = fptrunc float %119 to half
  br i1 %125, label %127, label %129

127:                                              ; preds = %124
  %128 = tail call fast fastcc <3 x half> @_Z13ShadowsFilterDv3_DhDhDh(<3 x half> noundef %116, half noundef %5, half noundef %126) #28
  br label %131

129:                                              ; preds = %124
  %130 = tail call fast fastcc <3 x half> @_Z21ShadowsNegativeFilterDv3_DhDhDh(<3 x half> noundef %116, half noundef %5, half noundef %126) #28
  br label %131

131:                                              ; preds = %129, %127, %115
  %132 = phi <3 x half> [ %130, %129 ], [ %128, %127 ], [ %116, %115 ]
  %133 = fcmp fast olt float %121, 0x3EE4F8B580000000
  br i1 %133, label %145, label %134

134:                                              ; preds = %131
  %135 = fcmp fast ogt float %119, 0.000000e+00
  %136 = fmul fast float %118, 7.500000e-01
  br i1 %135, label %137, label %140

137:                                              ; preds = %134
  %138 = fptrunc float %136 to half
  %139 = tail call fast fastcc <3 x half> @_Z13lightenFilterDv3_DhDhDh(<3 x half> noundef %132, half noundef %5, half noundef %138) #28
  br label %145

140:                                              ; preds = %134
  %141 = fsub fast float 1.000000e+00, %136
  %142 = tail call fast float @air.fast_fabs.f32(float %141) #25
  %143 = fptrunc float %142 to half
  %144 = tail call fast fastcc <3 x half> @_Z21negativeLightenFilterDv3_DhDhDh(<3 x half> noundef %132, half noundef %5, half noundef %143) #28
  br label %145

145:                                              ; preds = %140, %137, %131
  %146 = phi <3 x half> [ %132, %131 ], [ %139, %137 ], [ %144, %140 ]
  %147 = getelementptr inbounds %struct.SSRFGAdjustment.2414, ptr addrspace(1) %6, i64 0, i32 8
  %148 = load float, ptr addrspace(1) %147, align 4, !tbaa !182
  %149 = tail call fast float @air.fast_fabs.f32(float %148) #25
  %150 = fcmp fast olt float %149, 0x3EE4F8B580000000
  br i1 %150, label %161, label %151

151:                                              ; preds = %145
  %152 = fcmp fast ogt float %148, 0.000000e+00
  br i1 %152, label %153, label %157

153:                                              ; preds = %151
  %154 = fmul fast float %148, 0xBFCC28F5C0000000
  %155 = fptrunc float %154 to half
  %156 = tail call fast fastcc <3 x half> @_Z12highlightNegDv3_DhDhDh(<3 x half> noundef %146, half noundef %5, half noundef %155) #28
  br label %157

157:                                              ; preds = %153, %151
  %158 = phi <3 x half> [ %156, %153 ], [ %146, %151 ]
  %159 = fptrunc float %148 to half
  %160 = tail call fast fastcc <3 x half> @_Z13smartContrastDv3_DhDhDh(<3 x half> noundef %158, half noundef %5, half noundef %159) #28
  br label %161

161:                                              ; preds = %157, %145
  %162 = phi <3 x half> [ %146, %145 ], [ %160, %157 ]
  %163 = insertelement <3 x half> poison, half %2, i64 0
  %164 = shufflevector <3 x half> %163, <3 x half> poison, <3 x i32> zeroinitializer
  %165 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %17, <3 x half> %162, <3 x half> %164) #25
  ret <3 x half> %165
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z13smartContrastDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #10 {
  %4 = tail call fast half @air.dot.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3555)) #25
  %5 = tail call fast half @air.pow.f16(half %4, half 0xH3E00) #25
  %6 = extractelement <3 x half> %0, i64 0
  %7 = fsub fast half %6, %5
  %8 = fmul fast half %7, %7
  %9 = extractelement <3 x half> %0, i64 1
  %10 = fsub fast half %9, %5
  %11 = fmul fast half %10, %10
  %12 = extractelement <3 x half> %0, i64 2
  %13 = fsub fast half %12, %5
  %14 = fmul fast half %13, %13
  %15 = fpext half %5 to float
  %16 = fmul fast float %15, 2.250000e+00
  %17 = fsub fast float 1.000000e+00, %15
  %18 = fmul fast float %16, %17
  %19 = fptrunc float %18 to half
  %20 = fmul fast half %19, %2
  %21 = fpext half %20 to float
  %22 = fmul fast half %20, 0xHB800
  %23 = fmul fast float %21, 0x3FD322D0E0000000
  %24 = fptrunc float %23 to half
  %25 = insertelement <3 x half> poison, half %24, i64 0
  %26 = fmul fast <3 x half> %25, %0
  %27 = shufflevector <3 x half> %26, <3 x half> poison, <3 x i32> zeroinitializer
  %28 = shufflevector <3 x half> %0, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %29 = fmul fast float %21, 0x3FE2C8B440000000
  %30 = fptrunc float %29 to half
  %31 = insertelement <3 x half> poison, half %30, i64 0
  %32 = shufflevector <3 x half> %31, <3 x half> poison, <3 x i32> zeroinitializer
  %33 = fmul fast <3 x half> %32, %28
  %34 = shufflevector <3 x half> %0, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %35 = fmul fast float %21, 0x3FBD2F1AA0000000
  %36 = fptrunc float %35 to half
  %37 = insertelement <3 x half> poison, half %36, i64 0
  %38 = shufflevector <3 x half> %37, <3 x half> poison, <3 x i32> zeroinitializer
  %39 = fmul fast <3 x half> %38, %34
  %40 = insertelement <3 x half> poison, half %22, i64 0
  %41 = shufflevector <3 x half> %40, <3 x half> poison, <3 x i32> zeroinitializer
  %42 = fadd fast <3 x half> %41, %0
  %43 = fadd fast <3 x half> %42, %33
  %44 = fadd fast <3 x half> %43, %27
  %45 = fadd fast <3 x half> %44, %39
  %46 = fneg fast half %2
  %47 = fmul fast half %46, %19
  %48 = insertelement <3 x half> poison, half %47, i64 0
  %49 = shufflevector <3 x half> %48, <3 x half> poison, <3 x i32> zeroinitializer
  %50 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3800), <3 x half> %49) #25
  %51 = fadd fast half %11, 0xH399A
  %52 = fadd fast half %51, %8
  %53 = fadd fast half %52, %14
  %54 = insertelement <3 x half> poison, half %53, i64 0
  %55 = shufflevector <3 x half> %54, <3 x half> poison, <3 x i32> zeroinitializer
  %56 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %50, <3 x half> %45, <3 x half> %55) #25
  %57 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %56, <3 x half> zeroinitializer) #25
  %58 = fmul fast half %1, 0xH42CD
  %59 = fadd fast half %58, 0xHBCCD
  %60 = fpext half %59 to float
  %61 = fadd fast float %60, 0x3FF0FDBF40000000
  %62 = fmul fast float %61, 0x3FDA374BC0000000
  %63 = fptrunc float %62 to half
  %64 = fpext half %63 to float
  %65 = fsub fast float 1.000000e+00, %64
  %66 = fmul fast float %64, 4.000000e+00
  %67 = fmul fast float %66, %65
  %68 = fptrunc float %67 to half
  %69 = insertelement <3 x half> poison, half %68, i64 0
  %70 = shufflevector <3 x half> %69, <3 x half> poison, <3 x i32> zeroinitializer
  %71 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %0, <3 x half> %57, <3 x half> %70) #25
  ret <3 x half> %71
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z12highlightNegDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #10 {
  %4 = fadd fast half %2, 0xHBC00
  %5 = tail call fast half @air.clamp.f16(half %4, half 0xH0000, half 0xH3C00) #25
  %6 = fmul fast half %5, %5
  %7 = fmul fast half %5, 0xH4000
  %8 = fsub fast half 0xH4200, %7
  %9 = fmul fast half %6, %8
  %10 = fsub fast half 0xH3C00, %9
  %11 = fpext half %1 to float
  %12 = fmul fast float %11, 0x400B333340000000
  %13 = fpext half %10 to float
  %14 = fmul fast float %13, 0x3FE99999A0000000
  %15 = fsub fast float %12, %14
  %16 = fptrunc float %15 to half
  %17 = fneg fast half %2
  %18 = tail call fast half @air.mix.f16(half 0xH0000, half %16, half %17) #25
  %19 = fcmp fast ogt half %18, 0xH0000
  %20 = fpext half %18 to float
  %21 = fmul fast float %20, 1.500000e+00
  %22 = fadd fast float %21, 1.000000e+00
  %23 = fptrunc float %22 to half
  %24 = insertelement <3 x half> poison, half %23, i64 0
  %25 = shufflevector <3 x half> %24, <3 x half> poison, <3 x i32> zeroinitializer
  %26 = select fast i1 %19, <3 x half> %25, <3 x half> splat (half 0xH3C00)
  %27 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %28 = tail call fast half @air.dot.v3f16(<3 x half> %27, <3 x half> splat (half 0xH3555)) #25
  %29 = tail call fast half @air.sqrt.f16(half %28) #25
  %30 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %31 = fadd fast <3 x half> %30, splat (half 0xHBC00)
  %32 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %33 = tail call fast half @air.sqrt.f16(half %1) #25
  %34 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %27, <3 x half> %26) #25
  %35 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %34, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #25
  %36 = extractelement <3 x half> %26, i64 0
  %37 = fmul fast half %36, 0xHB800
  %38 = fpext half %29 to float
  %39 = fsub fast float 1.000000e+00, %38
  %40 = fmul fast float %39, %38
  %41 = fptrunc float %40 to half
  %42 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %35) #25
  %43 = fmul fast half %37, %41
  %44 = fneg fast half %33
  %45 = fmul fast half %43, %44
  %46 = fpext half %43 to float
  %47 = fmul fast float %46, 0x3FD322D0E0000000
  %48 = fptrunc float %47 to half
  %49 = insertelement <3 x half> poison, half %48, i64 0
  %50 = fmul fast <3 x half> %49, %42
  %51 = shufflevector <3 x half> %50, <3 x half> poison, <3 x i32> zeroinitializer
  %52 = shufflevector <3 x half> %42, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %53 = fmul fast float %46, 0x3FE2C8B440000000
  %54 = fptrunc float %53 to half
  %55 = insertelement <3 x half> poison, half %54, i64 0
  %56 = shufflevector <3 x half> %55, <3 x half> poison, <3 x i32> zeroinitializer
  %57 = fmul fast <3 x half> %56, %52
  %58 = shufflevector <3 x half> %42, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %59 = fmul fast float %46, 0x3FBD2F1AA0000000
  %60 = fptrunc float %59 to half
  %61 = insertelement <3 x half> poison, half %60, i64 0
  %62 = shufflevector <3 x half> %61, <3 x half> poison, <3 x i32> zeroinitializer
  %63 = fmul fast <3 x half> %62, %58
  %64 = insertelement <3 x half> poison, half %45, i64 0
  %65 = shufflevector <3 x half> %64, <3 x half> poison, <3 x i32> zeroinitializer
  %66 = fadd fast <3 x half> %65, %42
  %67 = fadd fast <3 x half> %66, %57
  %68 = fadd fast <3 x half> %67, %51
  %69 = fadd fast <3 x half> %68, %63
  %70 = insertelement <3 x half> poison, half %33, i64 0
  %71 = shufflevector <3 x half> %70, <3 x half> poison, <3 x i32> zeroinitializer
  %72 = fneg fast half %41
  %73 = fmul fast half %37, %72
  %74 = insertelement <3 x half> poison, half %73, i64 0
  %75 = shufflevector <3 x half> %74, <3 x half> poison, <3 x i32> zeroinitializer
  %76 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %42, <3 x half> %71, <3 x half> %75) #25
  %77 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %76, <3 x half> %69, <3 x half> splat (half 0xH3A66)) #25
  %78 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %77, <3 x half> zeroinitializer) #25
  %79 = fmul fast <3 x half> %78, %78
  %80 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %79) #25
  %81 = fadd fast <3 x half> %31, %32
  %82 = fadd fast <3 x half> %81, %80
  ret <3 x half> %82
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z21negativeLightenFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #10 {
  %4 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %5 = tail call fast half @air.dot.v3f16(<3 x half> %4, <3 x half> <half 0xH363D, half 0xH3800, half 0xH2F0A>) #25
  %6 = fcmp fast ogt half %5, 0xH0000
  br i1 %6, label %7, label %15

7:                                                ; preds = %3
  %8 = tail call fast half @air.pow.f16(half %5, half %2) #25
  %9 = insertelement <3 x half> poison, half %8, i64 0
  %10 = shufflevector <3 x half> %9, <3 x half> poison, <3 x i32> zeroinitializer
  %11 = fmul fast <3 x half> %10, %4
  %12 = insertelement <3 x half> poison, half %5, i64 0
  %13 = shufflevector <3 x half> %12, <3 x half> poison, <3 x i32> zeroinitializer
  %14 = fdiv fast <3 x half> %11, %13
  br label %15

15:                                               ; preds = %7, %3
  %16 = phi fast <3 x half> [ %14, %7 ], [ zeroinitializer, %3 ]
  %17 = insertelement <3 x half> poison, half %2, i64 0
  %18 = shufflevector <3 x half> %17, <3 x half> poison, <3 x i32> zeroinitializer
  %19 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %4, <3 x half> %18) #25
  %20 = fmul fast half %1, 0xH42CD
  %21 = fadd fast half %20, 0xHBCCD
  %22 = fpext half %21 to float
  %23 = fadd fast float %22, 0x3FF0FDBF40000000
  %24 = fmul fast float %23, 0x3FDA374BC0000000
  %25 = fptrunc float %24 to half
  %26 = tail call fast half @air.pow.f16(half %25, half 0xH3400) #25
  %27 = tail call fast half @air.dot.v3f16(<3 x half> %4, <3 x half> <half 0xH3800, half 0xH3800, half 0xH0000>) #25
  %28 = fpext half %27 to float
  %29 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %30 = fadd fast <3 x half> %29, splat (half 0xHBC00)
  %31 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %32 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %19, <3 x half> %16, <3 x half> splat (half 0xH3A66)) #25
  %33 = insertelement <3 x half> poison, half %26, i64 0
  %34 = shufflevector <3 x half> %33, <3 x half> poison, <3 x i32> zeroinitializer
  %35 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %4, <3 x half> %32, <3 x half> %34) #25
  %36 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %35, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #25
  %37 = fpext half %2 to float
  %38 = fmul fast float %37, 0x3FD3333340000000
  %39 = tail call fast float @air.fast_sqrt.f32(float %28) #25
  %40 = fsub fast float 1.000000e+00, %39
  %41 = fmul fast float %40, %39
  %42 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %36) #25
  %43 = tail call fast half @air.sqrt.f16(half %1) #25
  %44 = fmul fast float %41, %38
  %45 = fptrunc float %44 to half
  %46 = fneg fast half %43
  %47 = fmul fast half %46, %45
  %48 = fpext half %45 to float
  %49 = fmul fast float %48, 0x3FD322D0E0000000
  %50 = fptrunc float %49 to half
  %51 = insertelement <3 x half> poison, half %50, i64 0
  %52 = fmul fast <3 x half> %51, %42
  %53 = shufflevector <3 x half> %52, <3 x half> poison, <3 x i32> zeroinitializer
  %54 = shufflevector <3 x half> %42, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %55 = fmul fast float %48, 0x3FE2C8B440000000
  %56 = fptrunc float %55 to half
  %57 = insertelement <3 x half> poison, half %56, i64 0
  %58 = shufflevector <3 x half> %57, <3 x half> poison, <3 x i32> zeroinitializer
  %59 = fmul fast <3 x half> %58, %54
  %60 = shufflevector <3 x half> %42, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %61 = fmul fast float %48, 0x3FBD2F1AA0000000
  %62 = fptrunc float %61 to half
  %63 = insertelement <3 x half> poison, half %62, i64 0
  %64 = shufflevector <3 x half> %63, <3 x half> poison, <3 x i32> zeroinitializer
  %65 = fmul fast <3 x half> %64, %60
  %66 = insertelement <3 x half> poison, half %47, i64 0
  %67 = shufflevector <3 x half> %66, <3 x half> poison, <3 x i32> zeroinitializer
  %68 = fadd fast <3 x half> %67, %42
  %69 = fadd fast <3 x half> %68, %59
  %70 = fadd fast <3 x half> %69, %53
  %71 = fadd fast <3 x half> %70, %65
  %72 = insertelement <3 x half> poison, half %43, i64 0
  %73 = shufflevector <3 x half> %72, <3 x half> poison, <3 x i32> zeroinitializer
  %74 = fmul fast float %37, 0xBFD3333340000000
  %75 = fmul fast float %74, %41
  %76 = fptrunc float %75 to half
  %77 = insertelement <3 x half> poison, half %76, i64 0
  %78 = shufflevector <3 x half> %77, <3 x half> poison, <3 x i32> zeroinitializer
  %79 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %42, <3 x half> %73, <3 x half> %78) #25
  %80 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %79, <3 x half> %71, <3 x half> splat (half 0xH3A66)) #25
  %81 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %80, <3 x half> zeroinitializer) #25
  %82 = fmul fast <3 x half> %81, %81
  %83 = fadd fast <3 x half> %30, %31
  %84 = fadd fast <3 x half> %83, %82
  ret <3 x half> %84
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z13lightenFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #10 {
  %4 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %5 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %6 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %7 = tail call fast half @air.dot.v3f16(<3 x half> %6, <3 x half> <half 0xH3800, half 0xH3800, half 0xH0000>) #25
  %8 = fpext half %1 to float
  %9 = fmul fast float %8, 0x400B333340000000
  %10 = fadd fast float %9, 0xBFF3333340000000
  %11 = fptrunc float %10 to half
  %12 = fpext half %11 to float
  %13 = fadd fast float %12, 0x3FF0FDBF40000000
  %14 = fmul fast float %13, 0x3FDA374BC0000000
  %15 = fptrunc float %14 to half
  %16 = fsub fast half %15, %7
  %17 = fpext half %2 to float
  %18 = fmul fast float %17, 7.500000e-01
  %19 = fpext half %16 to float
  %20 = fmul fast float %18, %19
  %21 = fadd fast float %20, 1.000000e+00
  %22 = fptrunc float %21 to half
  %23 = tail call fast half @air.pow.f16(half %15, half 0xH3800) #25
  %24 = tail call fast half @air.clamp.f16(half %23, half 0xH0000, half 0xH3C00) #25
  %25 = insertelement <3 x half> poison, half %22, i64 0
  %26 = shufflevector <3 x half> %25, <3 x half> poison, <3 x i32> zeroinitializer
  %27 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %6, <3 x half> %26) #25
  %28 = insertelement <3 x half> poison, half %7, i64 0
  %29 = shufflevector <3 x half> %28, <3 x half> poison, <3 x i32> zeroinitializer
  %30 = fsub fast <3 x half> %27, %29
  %31 = fadd fast float %17, 1.000000e+00
  %32 = fpext half %7 to float
  %33 = fmul fast float %31, %32
  %34 = fptrunc float %33 to half
  %35 = insertelement <3 x half> poison, half %34, i64 0
  %36 = shufflevector <3 x half> %35, <3 x half> poison, <3 x i32> zeroinitializer
  %37 = fadd fast <3 x half> %30, %36
  %38 = fsub fast half 0xH3C00, %24
  %39 = insertelement <3 x half> poison, half %38, i64 0
  %40 = shufflevector <3 x half> %39, <3 x half> poison, <3 x i32> zeroinitializer
  %41 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %27, <3 x half> %37, <3 x half> %40) #25
  %42 = fptrunc float %31 to half
  %43 = insertelement <3 x half> poison, half %42, i64 0
  %44 = shufflevector <3 x half> %43, <3 x half> poison, <3 x i32> zeroinitializer
  %45 = fmul fast <3 x half> %27, %44
  %46 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %27, <3 x half> %45, <3 x half> %40) #25
  %47 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %46, <3 x half> %41, <3 x half> %29) #25
  %48 = tail call fast half @air.sqrt.f16(half %7) #25
  %49 = insertelement <3 x half> poison, half %48, i64 0
  %50 = shufflevector <3 x half> %49, <3 x half> poison, <3 x i32> zeroinitializer
  %51 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %47, <3 x half> %6, <3 x half> %50) #25
  %52 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %51, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #25
  %53 = fmul fast half %2, 0xH34CD
  %54 = fpext half %48 to float
  %55 = fsub fast float 1.000000e+00, %54
  %56 = fmul fast float %55, %54
  %57 = fptrunc float %56 to half
  %58 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %52) #25
  %59 = tail call fast half @air.sqrt.f16(half %1) #25
  %60 = fmul fast half %53, %57
  %61 = fneg fast half %59
  %62 = fmul fast half %60, %61
  %63 = fpext half %60 to float
  %64 = fmul fast float %63, 0x3FD322D0E0000000
  %65 = fptrunc float %64 to half
  %66 = insertelement <3 x half> poison, half %65, i64 0
  %67 = fmul fast <3 x half> %66, %58
  %68 = shufflevector <3 x half> %67, <3 x half> poison, <3 x i32> zeroinitializer
  %69 = shufflevector <3 x half> %58, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %70 = fmul fast float %63, 0x3FE2C8B440000000
  %71 = fptrunc float %70 to half
  %72 = insertelement <3 x half> poison, half %71, i64 0
  %73 = shufflevector <3 x half> %72, <3 x half> poison, <3 x i32> zeroinitializer
  %74 = fmul fast <3 x half> %73, %69
  %75 = shufflevector <3 x half> %58, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %76 = fmul fast float %63, 0x3FBD2F1AA0000000
  %77 = fptrunc float %76 to half
  %78 = insertelement <3 x half> poison, half %77, i64 0
  %79 = shufflevector <3 x half> %78, <3 x half> poison, <3 x i32> zeroinitializer
  %80 = fmul fast <3 x half> %79, %75
  %81 = insertelement <3 x half> poison, half %62, i64 0
  %82 = shufflevector <3 x half> %81, <3 x half> poison, <3 x i32> zeroinitializer
  %83 = fadd fast <3 x half> %82, %58
  %84 = fadd fast <3 x half> %83, %74
  %85 = fadd fast <3 x half> %84, %68
  %86 = fadd fast <3 x half> %85, %80
  %87 = insertelement <3 x half> poison, half %59, i64 0
  %88 = shufflevector <3 x half> %87, <3 x half> poison, <3 x i32> zeroinitializer
  %89 = fmul fast half %2, 0xHB4CD
  %90 = fmul fast half %89, %57
  %91 = insertelement <3 x half> poison, half %90, i64 0
  %92 = shufflevector <3 x half> %91, <3 x half> poison, <3 x i32> zeroinitializer
  %93 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %58, <3 x half> %88, <3 x half> %92) #25
  %94 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %93, <3 x half> %86, <3 x half> splat (half 0xH3A66)) #25
  %95 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %94, <3 x half> zeroinitializer) #25
  %96 = fmul fast <3 x half> %95, %95
  %97 = fadd fast <3 x half> %4, splat (half 0xHBC00)
  %98 = fadd fast <3 x half> %97, %5
  %99 = fadd fast <3 x half> %98, %96
  ret <3 x half> %99
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z21ShadowsNegativeFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #10 {
  %4 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %5 = fneg fast half %2
  %6 = fpext half %5 to float
  %7 = fadd fast float %6, -1.000000e+00
  %8 = tail call fast float @air.fast_fmax.f32(float %7, float 1.000000e+00) #25
  %9 = fptrunc float %8 to half
  %10 = fpext half %1 to float
  %11 = fmul fast float %10, 0x400B333340000000
  %12 = fpext half %9 to float
  %13 = fmul fast float %12, 0x3FF3333340000000
  %14 = fsub fast float %11, %13
  %15 = fptrunc float %14 to half
  %16 = tail call fast half @air.mix.f16(half 0xH0000, half %15, half %2) #25
  %17 = fcmp fast olt half %16, 0xH0000
  %18 = fmul fast half %16, %16
  %19 = insertelement <3 x half> poison, half %18, i64 0
  %20 = shufflevector <3 x half> %19, <3 x half> poison, <3 x i32> zeroinitializer
  %21 = fmul fast <3 x half> %20, <half 0xH4180, half 0xH4180, half 0xH4100>
  %22 = select fast i1 %17, <3 x half> zeroinitializer, <3 x half> %21
  %23 = fmul fast <3 x half> %4, %4
  br i1 %17, label %24, label %26

24:                                               ; preds = %3
  %25 = tail call fast half @air.fmin.f16(half %18, half 0xH3C00) #25
  br label %26

26:                                               ; preds = %24, %3
  %27 = phi half [ %25, %24 ], [ 0xH0000, %3 ]
  %28 = fpext half %16 to float
  %29 = fmul fast float %28, 0x3FFD9999A0000000
  %30 = tail call fast half @air.dot.v3f16(<3 x half> %4, <3 x half> splat (half 0xH3555)) #25
  %31 = tail call fast half @air.sqrt.f16(half %30) #25
  %32 = fsub fast half 0xH2E66, %31
  %33 = tail call fast half @air.fmax.f16(half %32, half 0xH0000) #25
  %34 = fpext half %33 to float
  %35 = fmul fast float %29, %34
  %36 = extractelement <3 x half> %4, i64 2
  %37 = fadd fast half %36, 0xHB666
  %38 = fmul fast half %37, 0xH44FF
  %39 = tail call fast half @air.clamp.f16(half %38, half 0xH0000, half 0xH3C00) #25
  %40 = fmul fast half %39, 0xH4000
  %41 = fsub fast half 0xH4200, %40
  %42 = fmul fast half %39, %39
  %43 = fmul fast half %42, 0xH3B33
  %44 = fmul fast half %43, %41
  %45 = fsub fast half 0xH3C00, %44
  %46 = insertelement <3 x half> poison, half %45, i64 0
  %47 = shufflevector <3 x half> %46, <3 x half> poison, <3 x i32> zeroinitializer
  %48 = fmul fast <3 x half> %47, %22
  %49 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %4, <3 x half> %23, <3 x half> %48) #25
  %50 = extractelement <3 x half> %49, i64 2
  %51 = fadd fast half %50, 0xHB666
  %52 = fmul fast half %51, 0xH44FF
  %53 = tail call fast half @air.clamp.f16(half %52, half 0xH0000, half 0xH3C00) #25
  %54 = fmul fast half %53, 0xH4000
  %55 = fsub fast half 0xH4200, %54
  %56 = fmul fast half %53, %53
  %57 = fmul fast half %56, 0xH3B33
  %58 = fmul fast half %57, %55
  %59 = fsub fast half 0xH3C00, %58
  %60 = fpext half %59 to float
  %61 = fmul fast float %35, %60
  %62 = fadd fast float %61, 1.000000e+00
  %63 = fptrunc float %62 to half
  %64 = insertelement <3 x half> poison, half %63, i64 0
  %65 = shufflevector <3 x half> %64, <3 x half> poison, <3 x i32> zeroinitializer
  %66 = fmul fast <3 x half> %65, %49
  %67 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %66, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #25
  %68 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %69 = fadd fast <3 x half> %68, splat (half 0xHBC00)
  %70 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %71 = fpext half %31 to float
  %72 = fsub fast float 1.000000e+00, %71
  %73 = fmul fast float %72, %71
  %74 = fptrunc float %73 to half
  %75 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %67) #25
  %76 = fmul fast half %27, %74
  %77 = fmul fast half %76, 0xHB666
  %78 = fpext half %76 to float
  %79 = fmul fast float %78, 0x3FD322D0E0000000
  %80 = fptrunc float %79 to half
  %81 = insertelement <3 x half> poison, half %80, i64 0
  %82 = fmul fast <3 x half> %81, %75
  %83 = shufflevector <3 x half> %82, <3 x half> poison, <3 x i32> zeroinitializer
  %84 = shufflevector <3 x half> %75, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %85 = fmul fast float %78, 0x3FE2C8B440000000
  %86 = fptrunc float %85 to half
  %87 = insertelement <3 x half> poison, half %86, i64 0
  %88 = shufflevector <3 x half> %87, <3 x half> poison, <3 x i32> zeroinitializer
  %89 = fmul fast <3 x half> %88, %84
  %90 = shufflevector <3 x half> %75, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %91 = fmul fast float %78, 0x3FBD2F1AA0000000
  %92 = fptrunc float %91 to half
  %93 = insertelement <3 x half> poison, half %92, i64 0
  %94 = shufflevector <3 x half> %93, <3 x half> poison, <3 x i32> zeroinitializer
  %95 = fmul fast <3 x half> %94, %90
  %96 = insertelement <3 x half> poison, half %77, i64 0
  %97 = shufflevector <3 x half> %96, <3 x half> poison, <3 x i32> zeroinitializer
  %98 = fadd fast <3 x half> %97, %75
  %99 = fadd fast <3 x half> %98, %89
  %100 = fadd fast <3 x half> %99, %83
  %101 = fadd fast <3 x half> %100, %95
  %102 = fneg fast half %27
  %103 = fmul fast half %102, %74
  %104 = insertelement <3 x half> poison, half %103, i64 0
  %105 = shufflevector <3 x half> %104, <3 x half> poison, <3 x i32> zeroinitializer
  %106 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %75, <3 x half> splat (half 0xH3666), <3 x half> %105) #25
  %107 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %106, <3 x half> %101, <3 x half> splat (half 0xH3A66)) #25
  %108 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %107, <3 x half> zeroinitializer) #25
  %109 = fmul fast <3 x half> %108, %108
  %110 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %109) #25
  %111 = fadd fast <3 x half> %69, %70
  %112 = fadd fast <3 x half> %111, %110
  %113 = extractelement <3 x half> %0, i64 0
  %114 = extractelement <3 x half> %0, i64 1
  %115 = tail call fast half @air.fmin.f16(half %113, half %114) #25
  %116 = extractelement <3 x half> %0, i64 2
  %117 = tail call fast half @air.fmin.f16(half %115, half %116) #25
  %118 = tail call fast half @air.fmax.f16(half %113, half %114) #25
  %119 = tail call fast half @air.fmax.f16(half %118, half %116) #25
  %120 = fsub fast half %119, %117
  %121 = fpext half %120 to float
  %122 = fcmp fast ogt float %121, 0x3EE4F8B580000000
  br i1 %122, label %123, label %142

123:                                              ; preds = %26
  %124 = extractelement <3 x half> %112, i64 0
  %125 = extractelement <3 x half> %112, i64 1
  %126 = tail call fast half @air.fmax.f16(half %124, half %125) #25
  %127 = extractelement <3 x half> %112, i64 2
  %128 = tail call fast half @air.fmax.f16(half %126, half %127) #25
  %129 = tail call fast half @air.fmin.f16(half %124, half %125) #25
  %130 = tail call fast half @air.fmin.f16(half %129, half %127) #25
  %131 = fsub fast half %128, %130
  %132 = insertelement <3 x half> poison, half %130, i64 0
  %133 = shufflevector <3 x half> %132, <3 x half> poison, <3 x i32> zeroinitializer
  %134 = insertelement <3 x half> poison, half %117, i64 0
  %135 = shufflevector <3 x half> %134, <3 x half> poison, <3 x i32> zeroinitializer
  %136 = fsub fast <3 x half> %0, %135
  %137 = fdiv fast half %131, %120
  %138 = insertelement <3 x half> poison, half %137, i64 0
  %139 = shufflevector <3 x half> %138, <3 x half> poison, <3 x i32> zeroinitializer
  %140 = fmul fast <3 x half> %139, %136
  %141 = fadd fast <3 x half> %140, %133
  br label %142

142:                                              ; preds = %123, %26
  %143 = phi fast <3 x half> [ %141, %123 ], [ %112, %26 ]
  ret <3 x half> %143
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z13ShadowsFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #10 {
  %4 = fpext half %1 to float
  %5 = fmul fast float %4, 0x400B333340000000
  %6 = fadd fast float %5, 0xBFF3333340000000
  %7 = fptrunc float %6 to half
  %8 = tail call fast half @air.mix.f16(half 0xH0000, half %7, half %2) #25
  %9 = fmul fast half %8, %8
  %10 = fcmp fast olt half %8, 0xH0000
  br i1 %10, label %11, label %14

11:                                               ; preds = %3
  %12 = tail call fast half @air.fmin.f16(half %9, half 0xH3C00) #25
  %13 = fpext half %12 to float
  br label %14

14:                                               ; preds = %11, %3
  %15 = phi float [ %13, %11 ], [ 0.000000e+00, %3 ]
  %16 = fcmp fast ogt half %8, 0xH0000
  %17 = insertelement <3 x half> poison, half %9, i64 0
  %18 = shufflevector <3 x half> %17, <3 x half> poison, <3 x i32> zeroinitializer
  %19 = fmul fast <3 x half> %18, <half 0xHC180, half 0xHC180, half 0xHC100>
  %20 = select fast i1 %16, <3 x half> zeroinitializer, <3 x half> %19
  %21 = fpext half %8 to float
  %22 = fmul fast float %21, 0x3FFD9999A0000000
  %23 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %24 = tail call fast half @air.dot.v3f16(<3 x half> %23, <3 x half> splat (half 0xH3555)) #25
  %25 = tail call fast half @air.sqrt.f16(half %24) #25
  %26 = fsub fast half 0xH2E66, %25
  %27 = tail call fast half @air.fmax.f16(half %26, half 0xH0000) #25
  %28 = fpext half %27 to float
  %29 = fmul fast float %22, %28
  %30 = extractelement <3 x half> %23, i64 2
  %31 = fadd fast half %30, 0xHB666
  %32 = fmul fast half %31, 0xH44FF
  %33 = tail call fast half @air.clamp.f16(half %32, half 0xH0000, half 0xH3C00) #25
  %34 = fmul fast half %33, %33
  %35 = fmul fast half %33, 0xH4000
  %36 = fsub fast half 0xH4200, %35
  %37 = fmul fast half %34, %36
  %38 = fpext half %37 to float
  %39 = fmul fast float %38, 0x3FECCCCCC0000000
  %40 = fsub fast float 1.000000e+00, %39
  %41 = fptrunc float %40 to half
  %42 = insertelement <3 x half> poison, half %41, i64 0
  %43 = shufflevector <3 x half> %42, <3 x half> poison, <3 x i32> zeroinitializer
  %44 = fmul fast <3 x half> %43, %20
  %45 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> splat (half 0xH3C00), <3 x half> %23, <3 x half> %44) #25
  %46 = fmul fast <3 x half> %45, %23
  %47 = extractelement <3 x half> %46, i64 2
  %48 = fadd fast half %47, 0xHB666
  %49 = fmul fast half %48, 0xH44FF
  %50 = tail call fast half @air.clamp.f16(half %49, half 0xH0000, half 0xH3C00) #25
  %51 = fmul fast half %50, 0xH4000
  %52 = fsub fast half 0xH4200, %51
  %53 = fmul fast half %50, %50
  %54 = fmul fast half %53, 0xH3B33
  %55 = fmul fast half %54, %52
  %56 = fsub fast half 0xH3C00, %55
  %57 = fpext half %56 to float
  %58 = fmul fast float %29, %57
  %59 = fadd fast float %58, 1.000000e+00
  %60 = fptrunc float %59 to half
  %61 = insertelement <3 x half> poison, half %60, i64 0
  %62 = shufflevector <3 x half> %61, <3 x half> poison, <3 x i32> zeroinitializer
  %63 = fmul fast <3 x half> %62, %46
  %64 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %63, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #25
  %65 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %66 = fadd fast <3 x half> %65, splat (half 0xHBC00)
  %67 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %68 = fpext half %25 to float
  %69 = fsub fast float 1.000000e+00, %68
  %70 = fmul fast float %69, %68
  %71 = fptrunc float %70 to half
  %72 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %64) #25
  %73 = fpext half %71 to float
  %74 = fmul fast float %15, %73
  %75 = fmul fast float %74, 0xBFD99999A0000000
  %76 = fmul fast float %74, 0x3FD322D0E0000000
  %77 = fptrunc float %76 to half
  %78 = insertelement <3 x half> poison, half %77, i64 0
  %79 = fmul fast <3 x half> %78, %72
  %80 = shufflevector <3 x half> %79, <3 x half> poison, <3 x i32> zeroinitializer
  %81 = shufflevector <3 x half> %72, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %82 = fmul fast float %74, 0x3FE2C8B440000000
  %83 = fptrunc float %82 to half
  %84 = insertelement <3 x half> poison, half %83, i64 0
  %85 = shufflevector <3 x half> %84, <3 x half> poison, <3 x i32> zeroinitializer
  %86 = fmul fast <3 x half> %85, %81
  %87 = shufflevector <3 x half> %72, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %88 = fmul fast float %74, 0x3FBD2F1AA0000000
  %89 = fptrunc float %88 to half
  %90 = insertelement <3 x half> poison, half %89, i64 0
  %91 = shufflevector <3 x half> %90, <3 x half> poison, <3 x i32> zeroinitializer
  %92 = fmul fast <3 x half> %91, %87
  %93 = fptrunc float %75 to half
  %94 = insertelement <3 x half> poison, half %93, i64 0
  %95 = shufflevector <3 x half> %94, <3 x half> poison, <3 x i32> zeroinitializer
  %96 = fadd fast <3 x half> %95, %72
  %97 = fadd fast <3 x half> %96, %86
  %98 = fadd fast <3 x half> %97, %80
  %99 = fadd fast <3 x half> %98, %92
  %100 = fneg fast half %71
  %101 = fpext half %100 to float
  %102 = fmul fast float %15, %101
  %103 = fptrunc float %102 to half
  %104 = insertelement <3 x half> poison, half %103, i64 0
  %105 = shufflevector <3 x half> %104, <3 x half> poison, <3 x i32> zeroinitializer
  %106 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %72, <3 x half> splat (half 0xH3666), <3 x half> %105) #25
  %107 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %106, <3 x half> %99, <3 x half> splat (half 0xH3A66)) #25
  %108 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %107, <3 x half> zeroinitializer) #25
  %109 = fmul fast <3 x half> %108, %108
  %110 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %109) #25
  %111 = fadd fast <3 x half> %66, %67
  %112 = fadd fast <3 x half> %111, %110
  ret <3 x half> %112
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z15underToneFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #9 {
  %4 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %5 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %4) #25
  %6 = shufflevector <3 x float> %5, <3 x float> poison, <3 x i32> zeroinitializer
  %7 = fmul fast <3 x float> %6, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %8 = shufflevector <3 x float> %5, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %9 = fmul fast <3 x float> %8, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %10 = fadd fast <3 x float> %7, %9
  %11 = shufflevector <3 x float> %5, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %12 = fmul fast <3 x float> %11, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %13 = fadd fast <3 x float> %10, %12
  %14 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %13) #25
  %15 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %13) #25
  %16 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %15, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %17 = fmul fast <3 x float> %16, %14
  %18 = shufflevector <3 x float> %17, <3 x float> poison, <3 x i32> zeroinitializer
  %19 = fmul fast <3 x float> %18, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %20 = shufflevector <3 x float> %17, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %21 = fmul fast <3 x float> %20, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %22 = fadd fast <3 x float> %19, %21
  %23 = shufflevector <3 x float> %17, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %24 = fmul fast <3 x float> %23, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %25 = fadd fast <3 x float> %22, %24
  %26 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %25) #25
  %27 = extractelement <3 x half> %26, i64 2
  %28 = fcmp fast une half %27, 0xH0000
  %29 = extractelement <3 x half> %26, i64 1
  %30 = fcmp fast une half %29, 0xH0000
  %31 = select i1 %28, i1 true, i1 %30
  br i1 %31, label %32, label %34

32:                                               ; preds = %3
  %33 = tail call fast half @air.atan2.f16(half %27, half %29) #25
  br label %34

34:                                               ; preds = %32, %3
  %35 = phi fast half [ %33, %32 ], [ 0xH0000, %3 ]
  %36 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %37 = fadd fast <3 x half> %36, splat (half 0xHBC00)
  %38 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %39 = fpext half %35 to float
  %40 = fpext half %2 to float
  %41 = fmul fast float %40, 0x3FC99999A0000000
  %42 = fadd fast float %41, %39
  %43 = fptrunc float %42 to half
  %44 = fadd fast float %39, 0xBFF79FF020000000
  %45 = fmul fast float %44, %44
  %46 = fmul fast float %45, 0xC000539780000000
  %47 = tail call fast float @air.fast_exp.f32(float %46) #25
  %48 = fptrunc float %47 to half
  %49 = tail call fast half @air.mix.f16(half %35, half %43, half %48) #25
  %50 = fmul fast half %29, %29
  %51 = fmul fast half %27, %27
  %52 = fadd fast half %50, %51
  %53 = tail call fast half @air.sqrt.f16(half %52) #25
  %54 = fpext half %53 to float
  %55 = tail call fast half @air.fabs.f16(half %2) #25
  %56 = extractelement <3 x half> %26, i64 0
  %57 = fmul fast half %55, %56
  %58 = tail call fast half @air.fmax.f16(half %57, half 0xH3800) #25
  %59 = fpext half %58 to float
  %60 = fmul fast float %59, 0x3FC3333340000000
  %61 = fsub fast float 1.000000e+00, %60
  %62 = fmul fast float %61, %54
  %63 = fptrunc float %62 to half
  %64 = tail call fast half @air.cos.f16(half %49) #25
  %65 = fmul fast half %64, %63
  %66 = insertelement <3 x half> %26, half %65, i64 1
  %67 = tail call fast half @air.sin.f16(half %49) #25
  %68 = fmul fast half %67, %63
  %69 = insertelement <3 x half> %66, half %68, i64 2
  %70 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %69) #25
  %71 = shufflevector <3 x float> %70, <3 x float> poison, <3 x i32> zeroinitializer
  %72 = shufflevector <3 x float> %70, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %73 = fmul fast <3 x float> %72, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %74 = fadd fast <3 x float> %73, %71
  %75 = shufflevector <3 x float> %70, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %76 = fmul fast <3 x float> %75, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %77 = fadd fast <3 x float> %74, %76
  %78 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %77) #25
  %79 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %77) #25
  %80 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %79, <3 x float> splat (float 0x40029ACA60000000)) #25
  %81 = fmul fast <3 x float> %80, %78
  %82 = shufflevector <3 x float> %81, <3 x float> poison, <3 x i32> zeroinitializer
  %83 = fmul fast <3 x float> %82, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %84 = shufflevector <3 x float> %81, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %85 = fmul fast <3 x float> %84, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %86 = fadd fast <3 x float> %83, %85
  %87 = shufflevector <3 x float> %81, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %88 = fmul fast <3 x float> %87, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %89 = fadd fast <3 x float> %86, %88
  %90 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %89) #25
  %91 = insertelement <3 x half> poison, half %1, i64 0
  %92 = shufflevector <3 x half> %91, <3 x half> poison, <3 x i32> zeroinitializer
  %93 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %4, <3 x half> %90, <3 x half> %92) #25
  %94 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %93) #25
  %95 = fadd fast <3 x half> %37, %38
  %96 = fadd fast <3 x half> %95, %94
  ret <3 x half> %96
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z19tonalContrastFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #10 {
  %4 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %5 = tail call fast half @air.dot.v3f16(<3 x half> %4, <3 x half> <half 0xH34CD, half 0xH3800, half 0xH3266>) #25
  %6 = fcmp fast ogt half %5, 0xH0000
  br i1 %6, label %7, label %29

7:                                                ; preds = %3
  %8 = tail call fast half @air.pow.f16(half %5, half 0xH4400) #25
  %9 = fpext half %8 to float
  %10 = fmul fast float %9, 0x3FFA182AA0000000
  %11 = tail call fast half @air.pow.f16(half %5, half 0xH4200) #25
  %12 = fpext half %11 to float
  %13 = fmul fast float %12, 0xC00D923A20000000
  %14 = tail call fast half @air.pow.f16(half %5, half 0xH4000) #25
  %15 = fpext half %14 to float
  %16 = fmul fast float %15, 0x4005A02760000000
  %17 = fpext half %5 to float
  %18 = fmul fast float %17, 0x3FD765FD80000000
  %19 = fadd fast float %10, %18
  %20 = fadd fast float %19, %13
  %21 = fadd fast float %20, %16
  %22 = fptrunc float %21 to half
  %23 = insertelement <3 x half> poison, half %5, i64 0
  %24 = shufflevector <3 x half> %23, <3 x half> poison, <3 x i32> zeroinitializer
  %25 = insertelement <3 x half> poison, half %22, i64 0
  %26 = shufflevector <3 x half> %25, <3 x half> poison, <3 x i32> zeroinitializer
  %27 = fmul fast <3 x half> %26, %4
  %28 = fdiv fast <3 x half> %27, %24
  br label %29

29:                                               ; preds = %7, %3
  %30 = phi fast <3 x half> [ %28, %7 ], [ zeroinitializer, %3 ]
  %31 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %32 = fadd fast <3 x half> %31, splat (half 0xHBC00)
  %33 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %34 = insertelement <3 x half> poison, half %2, i64 0
  %35 = shufflevector <3 x half> %34, <3 x half> poison, <3 x i32> zeroinitializer
  %36 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %4, <3 x half> %30, <3 x half> %35) #25
  %37 = fpext half %1 to float
  %38 = fadd fast float %37, 1.000000e+00
  %39 = fmul fast float %38, 5.000000e-01
  %40 = fptrunc float %39 to half
  %41 = insertelement <3 x half> poison, half %40, i64 0
  %42 = shufflevector <3 x half> %41, <3 x half> poison, <3 x i32> zeroinitializer
  %43 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %4, <3 x half> %36, <3 x half> %42) #25
  %44 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %43) #25
  %45 = fadd fast <3 x half> %32, %33
  %46 = fadd fast <3 x half> %45, %44
  ret <3 x half> %46
}

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(read)
define internal fastcc <3 x half> @_Z19renderBGAdjustmentsDv3_DhDhDhDhRU9MTLdevice15SSRBGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE(<3 x half> noundef %0, half noundef %1, half %2, half noundef %3, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(68) %4, ptr addrspace(1) %5) unnamed_addr #12 {
  %7 = getelementptr inbounds %struct.SSRBGAdjustment.2413, ptr addrspace(1) %4, i64 0, i32 3
  %8 = load float, ptr addrspace(1) %7, align 4, !tbaa !183
  %9 = tail call fast float @air.fast_fabs.f32(float %8) #25
  %10 = fcmp fast olt float %9, 0x3EE4F8B580000000
  br i1 %10, label %18, label %11

11:                                               ; preds = %6
  %12 = fcmp fast ogt float %8, 0.000000e+00
  %13 = fptrunc float %8 to half
  br i1 %12, label %14, label %16

14:                                               ; preds = %11
  %15 = tail call fast fastcc <3 x half> @_Z13ShadowsFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %13) #28
  br label %18

16:                                               ; preds = %11
  %17 = tail call fast fastcc <3 x half> @_Z21ShadowsNegativeFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %13) #28
  br label %18

18:                                               ; preds = %16, %14, %6
  %19 = phi <3 x half> [ %0, %6 ], [ %15, %14 ], [ %17, %16 ]
  %20 = getelementptr inbounds %struct.SSRBGAdjustment.2413, ptr addrspace(1) %4, i64 0, i32 1
  %21 = load float, ptr addrspace(1) %20, align 4, !tbaa !184
  %22 = tail call fast float @air.fast_fabs.f32(float %21) #25
  %23 = fcmp fast olt float %22, 0x3EE4F8B580000000
  br i1 %23, label %27, label %24

24:                                               ; preds = %18
  %25 = fptrunc float %21 to half
  %26 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %19, half noundef %25) #28
  br label %27

27:                                               ; preds = %24, %18
  %28 = phi <3 x half> [ %19, %18 ], [ %26, %24 ]
  %29 = getelementptr inbounds %struct.SSRBGAdjustment.2413, ptr addrspace(1) %4, i64 0, i32 0
  %30 = load float, ptr addrspace(1) %29, align 4, !tbaa !185
  %31 = tail call fast float @air.fast_fabs.f32(float %30) #25
  %32 = fcmp fast olt float %31, 0x3EE4F8B580000000
  br i1 %32, label %36, label %33

33:                                               ; preds = %27
  %34 = fptrunc float %30 to half
  %35 = tail call fast fastcc <3 x half> @_Z11whitesCurveDv3_DhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEEDhDh(<3 x half> noundef %28, ptr addrspace(1) %5, half noundef %34, half noundef 0xH0000) #29
  br label %36

36:                                               ; preds = %33, %27
  %37 = phi <3 x half> [ %28, %27 ], [ %35, %33 ]
  %38 = getelementptr inbounds %struct.SSRBGAdjustment.2413, ptr addrspace(1) %4, i64 0, i32 11
  %39 = load float, ptr addrspace(1) %38, align 4, !tbaa !186
  %40 = fadd fast float %39, -1.000000e+00
  %41 = tail call fast float @air.fast_fabs.f32(float %40) #25
  %42 = fcmp fast olt float %41, 0x3EE4F8B580000000
  br i1 %42, label %46, label %43

43:                                               ; preds = %36
  %44 = fptrunc float %39 to half
  %45 = tail call fast fastcc <3 x half> @_Z10airyFilterDv3_DhDh(<3 x half> noundef %37, half noundef %44) #28
  br label %46

46:                                               ; preds = %43, %36
  %47 = phi <3 x half> [ %37, %36 ], [ %45, %43 ]
  %48 = getelementptr inbounds %struct.SSRBGAdjustment.2413, ptr addrspace(1) %4, i64 0, i32 7
  %49 = load float, ptr addrspace(1) %48, align 4, !tbaa !187
  %50 = tail call fast float @air.fast_fabs.f32(float %49) #25
  %51 = fcmp fast olt float %50, 0x3EE4F8B580000000
  br i1 %51, label %72, label %52

52:                                               ; preds = %46
  %53 = fptrunc float %49 to half
  %54 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %47, <3 x half> zeroinitializer) #25
  %55 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %47, <3 x half> splat (half 0xH3C00)) #25
  %56 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %47) #25
  %57 = extractelement <3 x half> %56, i64 0
  %58 = extractelement <3 x half> %56, i64 1
  %59 = extractelement <3 x half> %56, i64 2
  %60 = tail call fast half @air.fmax3.f16(half %57, half %58, half %59) #25
  %61 = tail call fast half @air.pow.f16(half %60, half 0xH3800) #25
  %62 = fsub fast half 0xH3C00, %61
  %63 = fmul fast half %62, %53
  %64 = fadd fast half %63, 0xH3C00
  %65 = insertelement <3 x half> poison, half %64, i64 0
  %66 = shufflevector <3 x half> %65, <3 x half> poison, <3 x i32> zeroinitializer
  %67 = fmul fast <3 x half> %66, %56
  %68 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %67) #25
  %69 = fadd fast <3 x half> %54, splat (half 0xHBC00)
  %70 = fadd fast <3 x half> %69, %55
  %71 = fadd fast <3 x half> %70, %68
  br label %72

72:                                               ; preds = %52, %46
  %73 = phi <3 x half> [ %47, %46 ], [ %71, %52 ]
  %74 = getelementptr inbounds %struct.SSRBGAdjustment.2413, ptr addrspace(1) %4, i64 0, i32 8
  %75 = load float, ptr addrspace(1) %74, align 4, !tbaa !188
  %76 = fadd fast float %75, -1.000000e+00
  %77 = tail call fast float @air.fast_fabs.f32(float %76) #25
  %78 = fcmp fast olt float %77, 0x3EE4F8B580000000
  br i1 %78, label %82, label %79

79:                                               ; preds = %72
  %80 = fptrunc float %75 to half
  %81 = tail call fast fastcc <3 x half> @_Z15smoothSatFilterDv3_DhDh(<3 x half> noundef %73, half noundef %80) #28
  br label %82

82:                                               ; preds = %79, %72
  %83 = phi <3 x half> [ %73, %72 ], [ %81, %79 ]
  %84 = getelementptr inbounds %struct.SSRBGAdjustment.2413, ptr addrspace(1) %4, i64 0, i32 5
  %85 = load float, ptr addrspace(1) %84, align 4, !tbaa !189
  %86 = tail call fast float @air.fast_fabs.f32(float %85) #25
  %87 = fcmp fast olt float %86, 0x3EE4F8B580000000
  br i1 %87, label %143, label %88

88:                                               ; preds = %82
  %89 = fptrunc float %85 to half
  %90 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %83, <3 x half> zeroinitializer) #25
  %91 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %83, <3 x half> splat (half 0xH3C00)) #25
  %92 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %83) #25
  %93 = tail call fast half @air.dot.v3f16(<3 x half> %92, <3 x half> splat (half 0xH3555)) #25
  %94 = tail call fast half @air.sqrt.f16(half %93) #25
  %95 = fpext half %94 to float
  %96 = fsub fast float 1.000000e+00, %95
  %97 = fmul fast float %96, %95
  %98 = fptrunc float %97 to half
  %99 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %92) #25
  %100 = tail call fast half @air.sqrt.f16(half %1) #25
  %101 = fmul fast half %98, %89
  %102 = fmul fast half %101, 0xH4000
  %103 = fmul fast half %101, 0xHC000
  %104 = fmul fast half %103, %100
  %105 = fpext half %102 to float
  %106 = fmul fast float %105, 0x3FD322D0E0000000
  %107 = fptrunc float %106 to half
  %108 = insertelement <3 x half> poison, half %107, i64 0
  %109 = fmul fast <3 x half> %99, %108
  %110 = shufflevector <3 x half> %109, <3 x half> poison, <3 x i32> zeroinitializer
  %111 = shufflevector <3 x half> %99, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %112 = fmul fast float %105, 0x3FE2C8B440000000
  %113 = fptrunc float %112 to half
  %114 = insertelement <3 x half> poison, half %113, i64 0
  %115 = shufflevector <3 x half> %114, <3 x half> poison, <3 x i32> zeroinitializer
  %116 = fmul fast <3 x half> %111, %115
  %117 = shufflevector <3 x half> %99, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %118 = fmul fast float %105, 0x3FBD2F1AA0000000
  %119 = fptrunc float %118 to half
  %120 = insertelement <3 x half> poison, half %119, i64 0
  %121 = shufflevector <3 x half> %120, <3 x half> poison, <3 x i32> zeroinitializer
  %122 = fmul fast <3 x half> %117, %121
  %123 = insertelement <3 x half> poison, half %104, i64 0
  %124 = shufflevector <3 x half> %123, <3 x half> poison, <3 x i32> zeroinitializer
  %125 = fadd fast <3 x half> %116, %99
  %126 = fadd fast <3 x half> %125, %110
  %127 = fadd fast <3 x half> %126, %122
  %128 = fadd fast <3 x half> %127, %124
  %129 = insertelement <3 x half> poison, half %100, i64 0
  %130 = shufflevector <3 x half> %129, <3 x half> poison, <3 x i32> zeroinitializer
  %131 = fmul fast half %101, 0xHC000
  %132 = insertelement <3 x half> poison, half %131, i64 0
  %133 = shufflevector <3 x half> %132, <3 x half> poison, <3 x i32> zeroinitializer
  %134 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %99, <3 x half> %130, <3 x half> %133) #25
  %135 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %134, <3 x half> %128, <3 x half> splat (half 0xH3A66)) #25
  %136 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %135, <3 x half> zeroinitializer) #25
  %137 = fmul fast <3 x half> %136, %136
  %138 = fadd fast <3 x half> %90, splat (half 0xHBC00)
  %139 = fadd fast <3 x half> %138, %91
  %140 = fadd fast <3 x half> %139, %137
  %141 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %140, <3 x half> %83) #25
  %142 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %140, <3 x half> %141, <3 x half> zeroinitializer) #25
  br label %143

143:                                              ; preds = %88, %82
  %144 = phi <3 x half> [ %83, %82 ], [ %142, %88 ]
  %145 = getelementptr inbounds %struct.SSRBGAdjustment.2413, ptr addrspace(1) %4, i64 0, i32 4
  %146 = load float, ptr addrspace(1) %145, align 4, !tbaa !190
  %147 = tail call fast float @air.fast_fabs.f32(float %146) #25
  %148 = fcmp fast olt float %147, 0x3EE4F8B580000000
  br i1 %148, label %175, label %149

149:                                              ; preds = %143
  %150 = fptrunc float %146 to half
  %151 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %144, <3 x half> zeroinitializer) #25
  %152 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %144, <3 x half> splat (half 0xH3C00)) #25
  %153 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %144) #25
  %154 = tail call fast half @air.dot.v3f16(<3 x half> %153, <3 x half> splat (half 0xH3555)) #25
  %155 = fpext half %1 to float
  %156 = fmul fast float %155, 0x400B333340000000
  %157 = fadd fast float %156, 0xBFF3340000000000
  %158 = fptrunc float %157 to half
  %159 = fpext half %158 to float
  %160 = fadd fast float %159, 0x3FF0FDBF40000000
  %161 = fmul fast float %160, 0x3FDA374BC0000000
  %162 = fptrunc float %161 to half
  %163 = fsub fast half %162, %154
  %164 = fmul fast half %150, 0xH4000
  %165 = fmul fast half %164, %163
  %166 = fadd fast half %165, 0xH3C00
  %167 = tail call fast half @air.fmax.f16(half %166, half 0xH0000) #25
  %168 = insertelement <3 x half> poison, half %167, i64 0
  %169 = shufflevector <3 x half> %168, <3 x half> poison, <3 x i32> zeroinitializer
  %170 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %153, <3 x half> %169) #25
  %171 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %170, <3 x half> zeroinitializer) #25
  %172 = fadd fast <3 x half> %151, splat (half 0xHBC00)
  %173 = fadd fast <3 x half> %172, %152
  %174 = fadd fast <3 x half> %173, %171
  br label %175

175:                                              ; preds = %149, %143
  %176 = phi <3 x half> [ %144, %143 ], [ %174, %149 ]
  %177 = getelementptr inbounds %struct.SSRBGAdjustment.2413, ptr addrspace(1) %4, i64 0, i32 9
  %178 = load float, ptr addrspace(1) %177, align 4, !tbaa !191
  %179 = fmul fast float %178, 5.000000e-01
  %180 = fcmp fast ogt float %179, 0.000000e+00
  %181 = tail call fast float @air.fast_fabs.f32(float %179) #25
  %182 = xor i1 %180, true
  %183 = fcmp fast olt float %181, 0x3EE4F8B580000000
  %184 = select i1 %182, i1 true, i1 %183
  br i1 %184, label %188, label %185

185:                                              ; preds = %175
  %186 = fptrunc float %179 to half
  %187 = tail call fast fastcc <3 x half> @_Z13ShadowsFilterDv3_DhDhDh(<3 x half> noundef %176, half noundef %1, half noundef %186) #28
  br label %188

188:                                              ; preds = %185, %175
  %189 = phi <3 x half> [ %187, %185 ], [ %176, %175 ]
  %190 = fcmp fast olt float %181, 0x3EE4F8B580000000
  br i1 %190, label %201, label %191

191:                                              ; preds = %188
  %192 = fmul fast float %178, 7.500000e-01
  br i1 %180, label %193, label %196

193:                                              ; preds = %191
  %194 = fptrunc float %192 to half
  %195 = tail call fast fastcc <3 x half> @_Z13lightenFilterDv3_DhDhDh(<3 x half> noundef %189, half noundef %1, half noundef %194) #28
  br label %201

196:                                              ; preds = %191
  %197 = fsub fast float 1.000000e+00, %192
  %198 = fptrunc float %197 to half
  %199 = tail call fast half @air.fabs.f16(half %198) #25
  %200 = tail call fast fastcc <3 x half> @_Z21negativeLightenFilterDv3_DhDhDh(<3 x half> noundef %189, half noundef %1, half noundef %199) #28
  br label %201

201:                                              ; preds = %196, %193, %188
  %202 = phi <3 x half> [ %189, %188 ], [ %195, %193 ], [ %200, %196 ]
  %203 = getelementptr inbounds %struct.SSRBGAdjustment.2413, ptr addrspace(1) %4, i64 0, i32 10
  %204 = load float, ptr addrspace(1) %203, align 4, !tbaa !192
  %205 = tail call fast float @air.fast_fabs.f32(float %204) #25
  %206 = fcmp fast olt float %205, 0x3EE4F8B580000000
  br i1 %206, label %210, label %207

207:                                              ; preds = %201
  %208 = fptrunc float %204 to half
  %209 = tail call fast fastcc <3 x half> @_Z16underGrassFilterDv3_DhDhDh(<3 x half> noundef %202, half noundef %3, half noundef %208) #28
  br label %210

210:                                              ; preds = %207, %201
  %211 = phi <3 x half> [ %202, %201 ], [ %209, %207 ]
  %212 = getelementptr inbounds %struct.SSRBGAdjustment.2413, ptr addrspace(1) %4, i64 0, i32 2
  %213 = load float, ptr addrspace(1) %212, align 4, !tbaa !193
  %214 = fmul fast float %213, 5.000000e-01
  %215 = fadd fast float %214, 1.000000e+00
  %216 = tail call fast float @air.fast_fabs.f32(float %214) #25
  %217 = fcmp fast olt float %216, 0x3EE4F8B580000000
  br i1 %217, label %227, label %218

218:                                              ; preds = %210
  %219 = fcmp fast ogt float %215, 1.000000e+00
  br i1 %219, label %220, label %224

220:                                              ; preds = %218
  %221 = fadd fast float %213, 1.000000e+00
  %222 = fptrunc float %221 to half
  %223 = tail call fast fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %211, half noundef %222, half undef, half noundef 0xH4200) #28
  br label %227

224:                                              ; preds = %218
  %225 = fptrunc float %215 to half
  %226 = tail call fast fastcc <3 x half> @_Z15smoothSatFilterDv3_DhDh(<3 x half> noundef %211, half noundef %225) #28
  br label %227

227:                                              ; preds = %224, %220, %210
  %228 = phi <3 x half> [ %223, %220 ], [ %226, %224 ], [ %211, %210 ]
  ret <3 x half> %228
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z16underGrassFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #9 {
  %4 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #25
  %5 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %4) #25
  %6 = shufflevector <3 x float> %5, <3 x float> poison, <3 x i32> zeroinitializer
  %7 = fmul fast <3 x float> %6, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %8 = shufflevector <3 x float> %5, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %9 = fmul fast <3 x float> %8, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %10 = fadd fast <3 x float> %7, %9
  %11 = shufflevector <3 x float> %5, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %12 = fmul fast <3 x float> %11, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %13 = fadd fast <3 x float> %10, %12
  %14 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %13) #25
  %15 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %13) #25
  %16 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %15, <3 x float> splat (float 0x3FDB851EC0000000)) #25
  %17 = fmul fast <3 x float> %16, %14
  %18 = shufflevector <3 x float> %17, <3 x float> poison, <3 x i32> zeroinitializer
  %19 = fmul fast <3 x float> %18, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %20 = shufflevector <3 x float> %17, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %21 = fmul fast <3 x float> %20, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %22 = fadd fast <3 x float> %19, %21
  %23 = shufflevector <3 x float> %17, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %24 = fmul fast <3 x float> %23, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %25 = fadd fast <3 x float> %22, %24
  %26 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %25) #25
  %27 = extractelement <3 x half> %26, i64 2
  %28 = fcmp fast une half %27, 0xH0000
  %29 = extractelement <3 x half> %26, i64 1
  %30 = fcmp fast une half %29, 0xH0000
  %31 = select i1 %28, i1 true, i1 %30
  br i1 %31, label %32, label %34

32:                                               ; preds = %3
  %33 = tail call fast half @air.atan2.f16(half %27, half %29) #25
  br label %34

34:                                               ; preds = %32, %3
  %35 = phi fast half [ %33, %32 ], [ 0xH0000, %3 ]
  %36 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #25
  %37 = fadd fast <3 x half> %36, splat (half 0xHBC00)
  %38 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #25
  %39 = fmul fast half %2, 0xH3266
  %40 = fadd fast half %35, %39
  %41 = fpext half %35 to float
  %42 = fadd fast float %41, 0xBFFBA55FE0000000
  %43 = fmul fast float %42, %42
  %44 = fmul fast float %43, 0xC020539780000000
  %45 = tail call fast float @air.fast_exp.f32(float %44) #25
  %46 = fptrunc float %45 to half
  %47 = tail call fast half @air.mix.f16(half %35, half %40, half %46) #25
  %48 = fmul fast half %29, %29
  %49 = fmul fast half %27, %27
  %50 = fadd fast half %48, %49
  %51 = tail call fast half @air.sqrt.f16(half %50) #25
  %52 = fpext half %51 to float
  %53 = tail call fast half @air.fabs.f16(half %2) #25
  %54 = extractelement <3 x half> %26, i64 0
  %55 = fmul fast half %53, %54
  %56 = tail call fast half @air.fmax.f16(half %55, half 0xH3800) #25
  %57 = fmul fast half %56, 0xH2A66
  %58 = fpext half %57 to float
  %59 = fsub fast float 1.000000e+00, %58
  %60 = fmul fast float %59, %52
  %61 = fptrunc float %60 to half
  %62 = tail call fast half @air.cos.f16(half %47) #25
  %63 = fmul fast half %62, %61
  %64 = insertelement <3 x half> %26, half %63, i64 1
  %65 = tail call fast half @air.sin.f16(half %47) #25
  %66 = fmul fast half %65, %61
  %67 = insertelement <3 x half> %64, half %66, i64 2
  %68 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %67) #25
  %69 = shufflevector <3 x float> %68, <3 x float> poison, <3 x i32> zeroinitializer
  %70 = shufflevector <3 x float> %68, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %71 = fmul fast <3 x float> %70, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %72 = fadd fast <3 x float> %71, %69
  %73 = shufflevector <3 x float> %68, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %74 = fmul fast <3 x float> %73, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %75 = fadd fast <3 x float> %72, %74
  %76 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %75) #25
  %77 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %75) #25
  %78 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %77, <3 x float> splat (float 0x40029ACA60000000)) #25
  %79 = fmul fast <3 x float> %78, %76
  %80 = shufflevector <3 x float> %79, <3 x float> poison, <3 x i32> zeroinitializer
  %81 = fmul fast <3 x float> %80, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %82 = shufflevector <3 x float> %79, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %83 = fmul fast <3 x float> %82, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %84 = fadd fast <3 x float> %81, %83
  %85 = shufflevector <3 x float> %79, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %86 = fmul fast <3 x float> %85, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %87 = fadd fast <3 x float> %84, %86
  %88 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %87) #25
  %89 = insertelement <3 x half> poison, half %1, i64 0
  %90 = shufflevector <3 x half> %89, <3 x half> poison, <3 x i32> zeroinitializer
  %91 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %88, <3 x half> %4, <3 x half> %90) #25
  %92 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %91) #25
  %93 = fadd fast <3 x half> %37, %38
  %94 = fadd fast <3 x half> %93, %92
  ret <3 x half> %94
}

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(read)
define internal fastcc <3 x half> @_Z29renderSemanticToneAdjustmentsDv3_DhS_DhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEERU9MTLdevice25SSRSemanticToneAdjustment(<3 x half> noundef %0, <3 x half> noundef %1, half noundef %2, ptr addrspace(1) %3, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(28) %4) unnamed_addr #13 {
  %6 = tail call i32 @air.get_width_texture_2d(ptr addrspace(1) readonly captures(none) %3, i32 0) #27
  %7 = tail call fast half @air.convert.f.f16.u.i32(i32 %6) #25
  %8 = getelementptr inbounds %struct.SSRSemanticToneAdjustment.2415, ptr addrspace(1) %4, i64 0, i32 4
  %9 = load float, ptr addrspace(1) %8, align 4, !tbaa !194
  %10 = fptrunc float %9 to half
  %11 = getelementptr inbounds %struct.SSRSemanticToneAdjustment.2415, ptr addrspace(1) %4, i64 0, i32 2
  %12 = load float, ptr addrspace(1) %11, align 4, !tbaa !195
  %13 = fptrunc float %12 to half
  %14 = insertelement <3 x half> poison, half %13, i64 0
  %15 = shufflevector <3 x half> %14, <3 x half> poison, <3 x i32> zeroinitializer
  %16 = fmul fast <3 x half> %15, %0
  %17 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %16, <3 x half> splat (half 0xH3C00)) #25
  %18 = extractelement <3 x half> %17, i64 0
  %19 = fadd fast half %7, 0xHBC00
  %20 = fmul fast half %18, %19
  %21 = fpext half %20 to float
  %22 = fadd fast float %21, 5.000000e-01
  %23 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %22, i64 0
  %24 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %23, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %25 = extractvalue { <4 x half>, i8 } %24, 0
  %26 = extractelement <4 x half> %25, i64 0
  %27 = insertelement <3 x half> undef, half %26, i64 0
  %28 = extractelement <3 x half> %17, i64 1
  %29 = fmul fast half %28, %19
  %30 = fpext half %29 to float
  %31 = fadd fast float %30, 5.000000e-01
  %32 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %31, i64 0
  %33 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %32, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %34 = extractvalue { <4 x half>, i8 } %33, 0
  %35 = extractelement <4 x half> %34, i64 0
  %36 = insertelement <3 x half> %27, half %35, i64 1
  %37 = extractelement <3 x half> %17, i64 2
  %38 = fmul fast half %37, %19
  %39 = fpext half %38 to float
  %40 = fadd fast float %39, 5.000000e-01
  %41 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %40, i64 0
  %42 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %41, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %43 = extractvalue { <4 x half>, i8 } %42, 0
  %44 = extractelement <4 x half> %43, i64 0
  %45 = insertelement <3 x half> %36, half %44, i64 2
  %46 = insertelement <3 x half> undef, half %10, i64 0
  %47 = shufflevector <3 x half> %46, <3 x half> poison, <3 x i32> zeroinitializer
  %48 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %17, <3 x half> %45, <3 x half> %47) #25
  %49 = fdiv fast <3 x half> %48, %1
  %50 = fadd fast <3 x half> %1, splat (half 0xH9C04)
  %51 = fcmp fast olt <3 x half> %50, zeroinitializer
  %52 = select fast <3 x i1> %51, <3 x half> zeroinitializer, <3 x half> %49
  %53 = getelementptr inbounds %struct.SSRSemanticToneAdjustment.2415, ptr addrspace(1) %4, i64 0, i32 0
  %54 = load float, ptr addrspace(1) %53, align 4, !tbaa !119
  %55 = fptrunc float %54 to half
  %56 = getelementptr inbounds %struct.SSRSemanticToneAdjustment.2415, ptr addrspace(1) %4, i64 0, i32 5
  %57 = load float, ptr addrspace(1) %56, align 4, !tbaa !196
  %58 = fptrunc float %57 to half
  %59 = insertelement <3 x half> poison, half %55, i64 0
  %60 = shufflevector <3 x half> %59, <3 x half> poison, <3 x i32> zeroinitializer
  %61 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %52, <3 x half> splat (half 0xH3C00), <3 x half> %60) #25
  %62 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %61, <3 x half> splat (half 0xH3C00)) #25
  %63 = insertelement <3 x half> poison, half %58, i64 0
  %64 = shufflevector <3 x half> %63, <3 x half> poison, <3 x i32> zeroinitializer
  %65 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %61, <3 x half> %62, <3 x half> %64) #25
  %66 = fmul fast <3 x half> %65, %1
  %67 = getelementptr inbounds %struct.SSRSemanticToneAdjustment.2415, ptr addrspace(1) %4, i64 0, i32 3
  %68 = load float, ptr addrspace(1) %67, align 4, !tbaa !197
  %69 = fptrunc float %68 to half
  %70 = insertelement <3 x half> poison, half %69, i64 0
  %71 = shufflevector <3 x half> %70, <3 x half> poison, <3 x i32> zeroinitializer
  %72 = fmul fast <3 x half> %71, %0
  %73 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %72, <3 x half> splat (half 0xH3C00)) #25
  %74 = extractelement <3 x half> %73, i64 0
  %75 = fmul fast half %74, %19
  %76 = fpext half %75 to float
  %77 = fadd fast float %76, 5.000000e-01
  %78 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %77, i64 0
  %79 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %78, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %80 = extractvalue { <4 x half>, i8 } %79, 0
  %81 = extractelement <4 x half> %80, i64 0
  %82 = insertelement <3 x half> undef, half %81, i64 0
  %83 = extractelement <3 x half> %73, i64 1
  %84 = fmul fast half %83, %19
  %85 = fpext half %84 to float
  %86 = fadd fast float %85, 5.000000e-01
  %87 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %86, i64 0
  %88 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %87, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %89 = extractvalue { <4 x half>, i8 } %88, 0
  %90 = extractelement <4 x half> %89, i64 0
  %91 = insertelement <3 x half> %82, half %90, i64 1
  %92 = extractelement <3 x half> %73, i64 2
  %93 = fmul fast half %92, %19
  %94 = fpext half %93 to float
  %95 = fadd fast float %94, 5.000000e-01
  %96 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %95, i64 0
  %97 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %96, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #26
  %98 = extractvalue { <4 x half>, i8 } %97, 0
  %99 = extractelement <4 x half> %98, i64 0
  %100 = insertelement <3 x half> %91, half %99, i64 2
  %101 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %73, <3 x half> %100, <3 x half> %47) #25
  %102 = fdiv fast <3 x half> %101, %1
  %103 = select fast <3 x i1> %51, <3 x half> zeroinitializer, <3 x half> %102
  %104 = getelementptr inbounds %struct.SSRSemanticToneAdjustment.2415, ptr addrspace(1) %4, i64 0, i32 1
  %105 = load float, ptr addrspace(1) %104, align 4, !tbaa !118
  %106 = fptrunc float %105 to half
  %107 = getelementptr inbounds %struct.SSRSemanticToneAdjustment.2415, ptr addrspace(1) %4, i64 0, i32 6
  %108 = load float, ptr addrspace(1) %107, align 4, !tbaa !198
  %109 = fptrunc float %108 to half
  %110 = insertelement <3 x half> poison, half %106, i64 0
  %111 = shufflevector <3 x half> %110, <3 x half> poison, <3 x i32> zeroinitializer
  %112 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %103, <3 x half> splat (half 0xH3C00), <3 x half> %111) #25
  %113 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %112, <3 x half> splat (half 0xH3C00)) #25
  %114 = insertelement <3 x half> poison, half %109, i64 0
  %115 = shufflevector <3 x half> %114, <3 x half> poison, <3 x i32> zeroinitializer
  %116 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %112, <3 x half> %113, <3 x half> %115) #25
  %117 = fmul fast <3 x half> %116, %1
  %118 = insertelement <3 x half> poison, half %2, i64 0
  %119 = shufflevector <3 x half> %118, <3 x half> poison, <3 x i32> zeroinitializer
  %120 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %66, <3 x half> %117, <3 x half> %119) #25
  ret <3 x half> %120
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.convert.f.f16.u.i32(i32) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none)) local_unnamed_addr #15

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.mix.f32(float, float, float) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.log2.f16(half) local_unnamed_addr #0

; Function Attrs: inlinehint mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_(<3 x half> noundef %0, i32 noundef %1) unnamed_addr #6 {
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
  %5 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %6 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %7 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %6, <3 x half> splat (half 0xH3C00)) #25
  %8 = fmul fast <3 x half> %7, %5
  br label %75

9:                                                ; preds = %2
  %10 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %11 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %12 = fmul fast <3 x half> %11, splat (half 0xH2CF4)
  %13 = fadd fast <3 x half> %11, splat (half 0xH2B0A)
  %14 = fmul fast <3 x half> %13, splat (half 0xH3B96)
  %15 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %14, <3 x half> splat (half 0xH40CD)) #25
  %16 = fcmp fast ogt <3 x half> %11, splat (half 0xH292D)
  %17 = select fast <3 x i1> %16, <3 x half> %15, <3 x half> %12
  %18 = fmul fast <3 x half> %17, %10
  br label %75

19:                                               ; preds = %2
  %20 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %21 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %22 = fmul fast <3 x half> %21, splat (half 0xH331C)
  %23 = fadd fast <3 x half> %21, splat (half 0xH2E56)
  %24 = fmul fast <3 x half> %23, splat (half 0xH3B48)
  %25 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %24, <3 x half> splat (half 0xH4072)) #25
  %26 = fcmp fast ogt <3 x half> %21, splat (half 0xH2D30)
  %27 = select fast <3 x i1> %26, <3 x half> %25, <3 x half> %22
  %28 = fmul fast <3 x half> %27, %20
  br label %75

29:                                               ; preds = %2
  %30 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %31 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %32 = fmul fast <3 x half> %31, splat (half 0xH331C)
  %33 = fadd fast <3 x half> %31, splat (half 0xH2E5B)
  %34 = fmul fast <3 x half> %33, splat (half 0xH3B46)
  %35 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %34, <3 x half> splat (half 0xH4072)) #25
  %36 = fcmp fast ogt <3 x half> %31, splat (half 0xH2D33)
  %37 = select fast <3 x i1> %36, <3 x half> %35, <3 x half> %32
  %38 = fmul fast <3 x half> %37, %30
  br label %75

39:                                               ; preds = %2
  %40 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %41 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %42 = fmul fast <3 x half> %41, %41
  %43 = fmul fast <3 x half> %42, splat (half 0xH3555)
  %44 = fadd fast <3 x half> %41, splat (half 0xHB87B)
  %45 = fmul fast <3 x half> %44, splat (half 0xH4598)
  %46 = tail call fast <3 x half> @air.exp.v3f16(<3 x half> %45) #25
  %47 = fadd fast <3 x half> %46, splat (half 0xH348E)
  %48 = fmul fast <3 x half> %47, splat (half 0xH2D55)
  %49 = fcmp fast ogt <3 x half> %41, splat (half 0xH3800)
  %50 = select fast <3 x i1> %49, <3 x half> %48, <3 x half> %43
  %51 = fmul fast <3 x half> %50, %40
  br label %75

52:                                               ; preds = %2
  %53 = fadd fast <3 x half> %0, splat (half 0xHB98C)
  %54 = fmul fast <3 x half> %53, splat (half 0xH49D9)
  %55 = tail call fast <3 x half> @air.powr.v3f16(<3 x half> splat (half 0xH4000), <3 x half> %54) #25
  %56 = fadd fast <3 x half> %55, splat (half 0xHA0F0)
  %57 = fcmp fast oge <3 x half> %0, splat (half 0xH32AC)
  %58 = select fast <3 x i1> %57, <3 x half> %56, <3 x half> splat (half 0xHAB38)
  %59 = fmul fast <3 x half> %0, splat (half 0xH256A)
  %60 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %59) #25
  %61 = fadd fast <3 x half> %60, splat (half 0xHAB38)
  %62 = fcmp fast oge <3 x half> %0, zeroinitializer
  %63 = fcmp fast olt <3 x half> %0, splat (half 0xH32AC)
  %64 = and <3 x i1> %62, %63
  %65 = select fast <3 x i1> %64, <3 x half> %61, <3 x half> %58
  br label %75

66:                                               ; preds = %2
  %67 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #25
  %68 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #25
  %69 = fadd fast <3 x half> %68, splat (half 0xH3900)
  %70 = fdiv fast <3 x half> %69, zeroinitializer
  %71 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %70, <3 x half> splat (half 0xH3F33)) #25
  %72 = fcmp fast ogt <3 x half> %68, splat (half 0xH1800)
  %73 = select fast <3 x i1> %72, <3 x half> %71, <3 x half> %68
  %74 = fmul fast <3 x half> %73, %67
  br label %75

75:                                               ; preds = %66, %52, %39, %29, %19, %9, %4, %3, %2
  %76 = phi <3 x half> [ zeroinitializer, %2 ], [ %74, %66 ], [ %65, %52 ], [ %51, %39 ], [ %38, %29 ], [ %28, %19 ], [ %18, %9 ], [ %8, %4 ], [ %0, %3 ]
  ret <3 x half> %76
}

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
  %9 = fmul fast half %8, 0xH34C9
  %10 = extractelement <3 x half> %0, i64 1
  %11 = fmul fast half %10, 0xH38B2
  %12 = fadd fast half %9, %11
  %13 = extractelement <3 x half> %0, i64 2
  %14 = fmul fast half %13, 0xH2F4C
  %15 = fadd fast half %12, %14
  %16 = tail call fast half @air.fabs.f16(half %15) #25
  %17 = fcmp fast ult half %16, 0xH0101
  br i1 %17, label %80, label %18

18:                                               ; preds = %7
  %19 = fpext half %15 to float
  %20 = fmul fast float %19, %1
  %21 = fsub fast float 1.000000e+00, %1
  %22 = fsub fast half 0xH3C00, %15
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
  %49 = tail call fast float @air.mix.f32(float %47, float %46, float %48) #25
  %50 = fcmp fast ogt float %49, 0.000000e+00
  %51 = fcmp fast olt float %49, 1.000000e+00
  %52 = select i1 %50, i1 %51, i1 false
  br i1 %52, label %53, label %80

53:                                               ; preds = %45
  %54 = extractelement <3 x half> %0, i64 0
  %55 = fmul fast half %54, 0xH34C9
  %56 = extractelement <3 x half> %0, i64 1
  %57 = fmul fast half %56, 0xH38B2
  %58 = fadd fast half %55, %57
  %59 = extractelement <3 x half> %0, i64 2
  %60 = fmul fast half %59, 0xH2F4C
  %61 = fadd fast half %58, %60
  %62 = tail call fast half @air.fabs.f16(half %61) #25
  %63 = fcmp fast ult half %62, 0xH0101
  br i1 %63, label %80, label %64

64:                                               ; preds = %53
  %65 = fpext half %61 to float
  %66 = fmul fast float %49, %65
  %67 = fsub fast float 1.000000e+00, %49
  %68 = fsub fast half 0xH3C00, %61
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
declare <2 x float> @air.convert.f.v2f32.u.v2i16(<2 x i16>) local_unnamed_addr #0

declare void @llvm.lifetime.end.i64(i64)

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr writeonly captures(none), i8, i64, i1 immarg) #23

declare void @llvm.lifetime.start.i64(i64)

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(ptr captures(none)) #24

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #24

attributes #0 = { mustprogress nofree nosync nounwind willreturn memory(none) }
attributes #1 = { mustprogress nofree nosync nounwind willreturn "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="0" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #2 = { convergent mustprogress nounwind willreturn "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="96" "no-builtins" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #3 = { mustprogress nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { convergent mustprogress nounwind willreturn }
attributes #5 = { mustprogress nofree nounwind willreturn memory(read) }
attributes #6 = { inlinehint mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="48" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #7 = { convergent mustprogress nofree nosync nounwind willreturn memory(argmem: read) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="48" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #8 = { mustprogress nofree nosync nounwind willreturn memory(argmem: read) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="96" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #9 = { mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="96" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #10 = { mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="48" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #11 = { convergent mustprogress nofree nounwind willreturn memory(read) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="48" "no-builtins" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #12 = { convergent mustprogress nofree nounwind willreturn memory(read) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="48" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #13 = { convergent mustprogress nofree nounwind willreturn memory(read) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="64" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #14 = { convergent mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #15 = { mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #16 = { convergent mustprogress nofree nounwind willreturn memory(read) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="96" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #17 = { convergent mustprogress nofree nosync nounwind willreturn memory(argmem: read) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="64" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #18 = { mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="64" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #19 = { convergent mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="96" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #20 = { convergent mustprogress nofree nosync nounwind willreturn memory(argmem: read) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="96" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #21 = { mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="48" "no-builtins" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #22 = { mustprogress nofree nosync nounwind willreturn memory(argmem: read) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="48" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #23 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #24 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #25 = { nounwind willreturn memory(none) }
attributes #26 = { convergent nounwind willreturn memory(argmem: read) }
attributes #27 = { nounwind willreturn memory(argmem: read) }
attributes #28 = { nobuiltin "no-builtins" }
attributes #29 = { convergent nobuiltin "no-builtins" }
attributes #30 = { nobuiltin nounwind "no-builtins" }
attributes #31 = { nounwind willreturn memory(read) }
attributes #32 = { convergent nounwind willreturn }
attributes #33 = { nounwind willreturn memory(argmem: readwrite) }

!llvm.module.flags = !{!0, !1, !2, !3, !4, !5, !6, !7, !8}
!llvm.ident = !{!9}
!air.version = !{!10}
!air.language_version = !{!11}
!air.compile_options = !{!12, !13, !14}
!air.kernel = !{!15}
!air.function_constants = !{!59, !60}
!air.sampler_states = !{!61, !62}

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
!15 = !{ptr @renderFinalAdjustments, !16, !17}
!16 = !{}
!17 = !{!18, !21, !22, !23, !24, !25, !26, !27, !28, !29, !30, !31, !32, !33, !34, !35, !36, !39, !48, !52, !54, !56, !57, !58}
!18 = !{i32 0, !"air.function_constant", !19, !"air.imageblock", !"explicit", !"air.imageblock_data_size", i32 8, !"air.struct_type_info", !20, !"air.arg_type_align_size", i32 8, !"air.arg_type_name", !"imageblock<ImageBlockRGBA, layout_explicit>", !"air.arg_name", !"imgBlk"}
!19 = !{ptr addrspace(2) @__metal_implicit_fc_pred_1.42, !"bool", !"useImageBlock"}
!20 = !{i32 0, i32 8, i32 0, !"half4", !"rgba"}
!21 = !{i32 1, !"air.texture", !"air.location_index", i32 0, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputImageTex"}
!22 = !{i32 2, !"air.texture", !"air.location_index", i32 1, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputLinearImageTex"}
!23 = !{i32 3, !"air.texture", !"air.location_index", i32 2, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputGlobalToneCurveTex"}
!24 = !{i32 4, !"air.texture", !"air.location_index", i32 21, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputCubicSplineToneCurveTex"}
!25 = !{i32 5, !"air.texture", !"air.location_index", i32 7, i32 1, !"air.read", !"air.arg_type_name", !"texture2d<half, read>", !"air.arg_name", !"inputGainMapTex", !"air.arg_unused"}
!26 = !{i32 6, !"air.texture", !"air.location_index", i32 8, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputBgLTMGainMap"}
!27 = !{i32 7, !"air.texture", !"air.location_index", i32 9, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputFgLTMGainMap"}
!28 = !{i32 8, !"air.texture", !"air.location_index", i32 5, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputLightMapTex"}
!29 = !{i32 9, !"air.texture", !"air.location_index", i32 6, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputLinearLightMapTex"}
!30 = !{i32 10, !"air.texture", !"air.location_index", i32 10, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"fgbgMatte"}
!31 = !{i32 11, !"air.texture", !"air.location_index", i32 11, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"skinMatte"}
!32 = !{i32 12, !"air.texture", !"air.location_index", i32 12, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"skyMatte"}
!33 = !{i32 13, !"air.texture", !"air.location_index", i32 22, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"selectiveColorHueSatLumLUTTex"}
!34 = !{i32 14, !"air.texture", !"air.location_index", i32 13, i32 1, !"air.write", !"air.arg_type_name", !"texture2d<half, write>", !"air.arg_name", !"outputImageTex"}
!35 = !{i32 15, !"air.texture", !"air.location_index", i32 14, i32 1, !"air.write", !"air.arg_type_name", !"texture2d<half, write>", !"air.arg_name", !"outputGainMapTex", !"air.arg_unused"}
!36 = !{i32 16, !"air.buffer", !"air.buffer_size", i32 320, !"air.location_index", i32 0, i32 1, !"air.read", !"air.address_space", i32 2, !"air.struct_type_info", !37, !"air.arg_type_size", i32 320, !"air.arg_type_align_size", i32 16, !"air.arg_type_name", !"SSRColorManagement", !"air.arg_name", !"colorManagement"}
!37 = !{!"air.struct_type_info", !38, i32 0, i32 80, i32 0, !"SSRColorConversion", !"inputImage", !"air.struct_type_info", !38, i32 80, i32 80, i32 0, !"SSRColorConversion", !"inputLinearImage", !"air.struct_type_info", !38, i32 160, i32 80, i32 0, !"SSRColorConversion", !"inputMasks", !"air.struct_type_info", !38, i32 240, i32 80, i32 0, !"SSRColorConversion", !"outputImage"}
!38 = !{i32 0, i32 4, i32 0, !"uint", !"transferFunction", i32 16, i32 48, i32 0, !"float3x3", !"colorConversionMatrix", i32 64, i32 1, i32 0, !"bool", !"useVELuma"}
!39 = !{i32 17, !"air.buffer", !"air.buffer_size", i32 672, !"air.location_index", i32 1, i32 1, !"air.read_write", !"air.address_space", i32 1, !"air.struct_type_info", !40, !"air.arg_type_size", i32 672, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"SSRParams", !"air.arg_name", !"params"}
!40 = !{i32 0, i32 4, i32 0, !"uint", !"castType", i32 4, i32 4, i32 0, !"float", !"castIntensity", i32 8, i32 4, i32 0, !"float", !"toneBias", i32 12, i32 4, i32 0, !"float", !"colorBias", i32 16, i32 4, i32 0, !"float", !"fgCastIntensity", i32 20, i32 4, i32 0, !"float", !"bgCastIntensity", i32 24, i32 4, i32 0, !"float", !"linearBaseGain", i32 28, i32 4, i32 0, !"float", !"baselineExposure", i32 32, i32 4, i32 0, !"uint", !"sceneType", !"air.struct_type_info", !41, i32 36, i32 136, i32 0, !"SSRCastAdjustments", !"castAdj", !"air.struct_type_info", !42, i32 172, i32 264, i32 0, !"SSRToneAdjustments", !"toneAdj", !"air.struct_type_info", !43, i32 436, i32 16, i32 0, !"SSRColorAdjustments", !"colorAdj", !"air.struct_type_info", !44, i32 452, i32 36, i32 0, !"SSRHazeAdjustments", !"hazeAdj", !"air.struct_type_info", !45, i32 488, i32 68, i32 0, !"SSRBGAdjustment", !"bgAdj", !"air.struct_type_info", !46, i32 556, i32 64, i32 0, !"SSRFGAdjustment", !"fgAdj", !"air.struct_type_info", !47, i32 620, i32 28, i32 0, !"SSRSemanticToneAdjustment", !"semanticToneAdj", i32 648, i32 4, i32 0, !"float", !"brightnessValue", i32 652, i32 4, i32 0, !"uint", !"tuningType", i32 656, i32 4, i32 0, !"float", !"peopleThresholdLo", i32 660, i32 4, i32 0, !"float", !"peopleThresholdHi", i32 664, i32 4, i32 0, !"float", !"faceBasedGlobalExposureBoostRatio", i32 668, i32 4, i32 0, !"float", !"personMasksValidHint"}
!41 = !{i32 0, i32 4, i32 0, !"float", !"bgWarmth", i32 4, i32 4, i32 0, !"float", !"fgWarmth", i32 8, i32 4, i32 0, !"float", !"bgRotate", i32 12, i32 4, i32 0, !"float", !"fgRotate", i32 16, i32 4, i32 0, !"float", !"personWarmth", i32 20, i32 4, i32 0, !"float", !"personRotate", i32 24, i32 4, i32 3, !"float", !"hue", i32 36, i32 4, i32 3, !"float", !"range", i32 48, i32 4, i32 3, !"float", !"strength", i32 60, i32 4, i32 0, !"float", !"shadow", i32 64, i32 4, i32 0, !"float", !"mids", i32 68, i32 4, i32 0, !"float", !"high", i32 72, i32 4, i32 3, !"float", !"shadowRGB", i32 84, i32 4, i32 3, !"float", !"midsRGB", i32 96, i32 4, i32 3, !"float", !"highRGB", i32 108, i32 4, i32 0, !"float", !"deRed", i32 112, i32 4, i32 0, !"float", !"deRedSatReduction", i32 116, i32 4, i32 0, !"float", !"deYellow", i32 120, i32 4, i32 0, !"float", !"skinWarmth", i32 124, i32 4, i32 0, !"float", !"skinProtectStrength", i32 128, i32 4, i32 0, !"float", !"skinProtectRange", i32 132, i32 4, i32 0, !"float", !"skinRatioThreshold"}
!42 = !{i32 0, i32 4, i32 0, !"float", !"toneMinusMids", i32 4, i32 4, i32 0, !"float", !"toneMinusExposure", i32 8, i32 4, i32 0, !"float", !"toneMinusPersonExposure", i32 12, i32 4, i32 0, !"float", !"toneMinusFGScale", i32 16, i32 4, i32 0, !"float", !"toneMinusPersonSatScale", i32 20, i32 4, i32 0, !"float", !"toneMinusPersonContrastMax", i32 24, i32 4, i32 0, !"float", !"toneMinusPersonContrastScale", i32 28, i32 4, i32 0, !"float", !"toneMinusBGContrastScale", i32 32, i32 4, i32 0, !"float", !"toneMinusBGContrastMax", i32 36, i32 4, i32 0, !"float", !"toneMinusLTMRatio", i32 40, i32 4, i32 0, !"float", !"toneMinusPersonSmartContrastScale", i32 44, i32 4, i32 0, !"float", !"tonePlusPersonSatScale", i32 48, i32 4, i32 0, !"float", !"tonePlusFGScale", i32 52, i32 4, i32 0, !"float", !"tonePlusExposure", i32 56, i32 4, i32 0, !"float", !"tonePlusBGContrast", i32 60, i32 4, i32 0, !"float", !"colorCubeToneBiasMinGamma", i32 64, i32 4, i32 0, !"float", !"colorCubeToneBiasMaxGamma", i32 68, i32 4, i32 0, !"float", !"starkBWBackgroundRed", i32 72, i32 4, i32 0, !"float", !"starkBWBackgroundGreen", i32 76, i32 4, i32 0, !"float", !"starkBWBackgroundBlue", i32 80, i32 4, i32 0, !"float", !"starkBWWhitesMax", i32 84, i32 4, i32 0, !"float", !"defaultContrastBump", i32 88, i32 4, i32 0, !"float", !"defaultSatBump", i32 92, i32 4, i32 0, !"float", !"defaultMidsBump", i32 96, i32 4, i32 0, !"float", !"defaultLightenBump", i32 100, i32 4, i32 0, !"float", !"dfContrastBump", i32 104, i32 4, i32 0, !"float", !"dfSatBump", i32 108, i32 4, i32 0, !"float", !"dfMidsBump", i32 112, i32 4, i32 0, !"float", !"dfLightenBump", i32 116, i32 4, i32 0, !"float", !"dfLowLightStarts", i32 120, i32 4, i32 0, !"float", !"dfLowLightMax", i32 124, i32 4, i32 0, !"float", !"dfLowLightContrastBump", i32 128, i32 4, i32 0, !"float", !"dfLowLightSatBump", i32 132, i32 4, i32 0, !"float", !"dfLowLightMidsBump", i32 136, i32 4, i32 0, !"float", !"dfLowLightLightenBump", i32 140, i32 4, i32 0, !"float", !"ubContrastBump", i32 144, i32 4, i32 0, !"float", !"ubSatBump", i32 148, i32 4, i32 0, !"float", !"ubMidsBump", i32 152, i32 4, i32 0, !"float", !"ubLightenBump", i32 156, i32 4, i32 0, !"float", !"digitalFlashContrastBump", i32 160, i32 4, i32 0, !"float", !"digitalFlashSatBump", i32 164, i32 4, i32 0, !"float", !"digitalFlashMidsBump", i32 168, i32 4, i32 0, !"float", !"digitalFlashLightenBump", i32 172, i32 4, i32 0, !"float", !"swfrContrastBump", i32 176, i32 4, i32 0, !"float", !"swfrSatBump", i32 180, i32 4, i32 0, !"float", !"swfrMidsBump", i32 184, i32 4, i32 0, !"float", !"swfrLightenBump", i32 188, i32 4, i32 0, !"float", !"wysContrastBump", i32 192, i32 4, i32 0, !"float", !"wysSatBump", i32 196, i32 4, i32 0, !"float", !"wysMidsBump", i32 200, i32 4, i32 0, !"float", !"wysLightenBump", i32 204, i32 4, i32 0, !"float", !"sfdContrastBump", i32 208, i32 4, i32 0, !"float", !"sfdSatBump", i32 212, i32 4, i32 0, !"float", !"sfdMidsBump", i32 216, i32 4, i32 0, !"float", !"sfdLightenBump", i32 220, i32 4, i32 0, !"float", !"videoContrastBump", i32 224, i32 4, i32 0, !"float", !"videoSatBump", i32 228, i32 4, i32 0, !"float", !"videoMidsBump", i32 232, i32 4, i32 0, !"float", !"videoLightenBump", i32 236, i32 4, i32 0, !"float", !"foodToneScale", i32 240, i32 4, i32 0, !"float", !"foodColorScale", i32 244, i32 4, i32 0, !"float", !"foodIntensityScale", i32 248, i32 4, i32 0, !"float", !"sunsetToneScale", i32 252, i32 4, i32 0, !"float", !"sunsetColorScale", i32 256, i32 4, i32 0, !"float", !"sunsetIntensityScale", i32 260, i32 4, i32 0, !"float", !"longGrayLiftMix"}
!43 = !{i32 0, i32 4, i32 0, !"float", !"bwBackgroundHue", i32 4, i32 4, i32 0, !"float", !"bwForegroundHue", i32 8, i32 4, i32 0, !"float", !"colorBoostScale", i32 12, i32 4, i32 0, !"float", !"shadMidHighPersonMix"}
!44 = !{i32 0, i32 1, i32 0, !"bool", !"doHazeTuning", i32 4, i32 4, i32 0, !"float", !"liftStrength", i32 8, i32 4, i32 0, !"float", !"bgLift", i32 12, i32 4, i32 0, !"float", !"personLift", i32 16, i32 4, i32 0, !"float", !"bgMids", i32 20, i32 4, i32 0, !"float", !"personMids", i32 24, i32 4, i32 0, !"float", !"satMix", i32 28, i32 4, i32 0, !"float", !"contrast", i32 32, i32 4, i32 0, !"float", !"localContrast"}
!45 = !{i32 0, i32 4, i32 0, !"float", !"whites", i32 4, i32 4, i32 0, !"float", !"contrast", i32 8, i32 4, i32 0, !"float", !"richSat", i32 12, i32 4, i32 0, !"float", !"shadows", i32 16, i32 4, i32 0, !"float", !"gammaContrast", i32 20, i32 4, i32 0, !"float", !"localContrast", i32 24, i32 4, i32 0, !"float", !"airy", i32 28, i32 4, i32 0, !"float", !"mids", i32 32, i32 4, i32 0, !"float", !"sat", i32 36, i32 4, i32 0, !"float", !"lighten", i32 40, i32 4, i32 0, !"float", !"underGrass", i32 44, i32 4, i32 0, !"float", !"airyGamma", i32 48, i32 4, i32 0, !"float", !"warmthMatchI", i32 52, i32 4, i32 0, !"float", !"warmthMatchQ", i32 56, i32 4, i32 0, !"float", !"warmthMatchSkyI", i32 60, i32 4, i32 0, !"float", !"warmthMatchSkyQ", i32 64, i32 4, i32 0, !"float", !"bgGlobalMix"}
!46 = !{i32 0, i32 4, i32 0, !"float", !"personMix", i32 4, i32 4, i32 0, !"float", !"airy", i32 8, i32 4, i32 0, !"float", !"mids", i32 12, i32 4, i32 0, !"float", !"lighten", i32 16, i32 4, i32 0, !"float", !"whites", i32 20, i32 4, i32 0, !"float", !"airyGamma", i32 24, i32 4, i32 0, !"float", !"shadows", i32 28, i32 4, i32 0, !"float", !"contrast", i32 32, i32 4, i32 0, !"float", !"smartContrast", i32 36, i32 4, i32 0, !"float", !"skinHighLights", i32 40, i32 4, i32 0, !"float", !"skinLocalContrast", i32 44, i32 4, i32 0, !"float", !"saturation", i32 48, i32 4, i32 0, !"float", !"faceI", i32 52, i32 4, i32 0, !"float", !"faceQ", i32 56, i32 4, i32 0, !"float", !"underTone", i32 60, i32 4, i32 0, !"float", !"neckShade"}
!47 = !{i32 0, i32 4, i32 0, !"float", !"bgLTM", i32 4, i32 4, i32 0, !"float", !"fgLTM", i32 8, i32 4, i32 0, !"float", !"bgExposureGain", i32 12, i32 4, i32 0, !"float", !"fgExposureGain", i32 16, i32 4, i32 0, !"float", !"GTC", i32 20, i32 4, i32 0, !"float", !"HR", i32 24, i32 4, i32 0, !"float", !"personHR"}
!48 = !{i32 18, !"air.buffer", !"air.buffer_size", i32 10640, !"air.location_index", i32 3, i32 1, !"air.read_write", !"air.address_space", i32 1, !"air.struct_type_info", !49, !"air.arg_type_size", i32 10640, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"SSRStats", !"air.arg_name", !"stats"}
!49 = !{i32 0, i32 4, i32 2560, !"uint", !"globalHistogram", !"air.struct_type_info", !50, i32 10240, i32 36, i32 10, !"SSRGlobalStats", !"globalStats", i32 10600, i32 4, i32 0, !"uint", !"globalPersonCount", i32 10604, i32 4, i32 0, !"uint", !"globalSkinCount", i32 10608, i32 4, i32 0, !"float", !"peopleRatio", i32 10612, i32 4, i32 0, !"float", !"skinRatio", !"air.struct_type_info", !51, i32 10616, i32 12, i32 0, !"SSRBasicStats", !"linBasicStats", !"air.struct_type_info", !51, i32 10628, i32 12, i32 0, !"SSRBasicStats", !"ltmBasicStats"}
!50 = !{i32 0, i32 4, i32 0, !"float", !"highKey", i32 4, i32 4, i32 0, !"float", !"p02", i32 8, i32 4, i32 0, !"float", !"p10", i32 12, i32 4, i32 0, !"float", !"p25", i32 16, i32 4, i32 0, !"float", !"p50", i32 20, i32 4, i32 0, !"float", !"p75", i32 24, i32 4, i32 0, !"float", !"p98", i32 28, i32 4, i32 0, !"float", !"blackPoint", i32 32, i32 4, i32 0, !"float", !"whitePoint"}
!51 = !{i32 0, i32 4, i32 0, !"float", !"min", i32 4, i32 4, i32 0, !"float", !"max", i32 8, i32 4, i32 0, !"float", !"avg"}
!52 = !{i32 19, !"air.buffer", !"air.buffer_size", i32 176, !"air.location_index", i32 5, i32 1, !"air.read", !"air.address_space", i32 2, !"air.struct_type_info", !53, !"air.arg_type_size", i32 176, !"air.arg_type_align_size", i32 16, !"air.arg_type_name", !"SSRRenderROI", !"air.arg_name", !"roi"}
!53 = !{i32 0, i32 4, i32 0, !"ushort2", !"logicalImageSize", i32 4, i32 4, i32 0, !"ushort2", !"renderRegionSize", i32 8, i32 4, i32 0, !"ushort2", !"renderEdge", i32 16, i32 16, i32 0, !"float4", !"logicalImageToInputImageGridScaleAndOffset", i32 32, i32 16, i32 0, !"float4", !"logicalImageToInputLinearImageGridScaleAndOffset", i32 48, i32 16, i32 0, !"float4", !"logicalImageToBgLTMGainMapGridScaleAndOffset", i32 64, i32 16, i32 0, !"float4", !"logicalImageToFgLTMGainMapGridScaleAndOffset", i32 80, i32 16, i32 0, !"float4", !"logicalImageToInputLightMapGridScaleAndOffset", i32 96, i32 16, i32 0, !"float4", !"logicalImageToInputLinearLightMapGridScaleAndOffset", i32 112, i32 16, i32 0, !"float4", !"logicalImageToInputPersonMaskGridScaleAndOffset", i32 128, i32 16, i32 0, !"float4", !"logicalImageToInputSkinMaskGridScaleAndOffset", i32 144, i32 16, i32 0, !"float4", !"logicalImageToInputSkyMaskGridScaleAndOffset", i32 160, i32 4, i32 0, !"ushort2", !"outputImageGridOffset"}
!54 = !{i32 20, !"air.function_constant", !55, !"air.buffer", !"air.buffer_size", i32 4, !"air.location_index", i32 8, i32 1, !"air.read", !"air.address_space", i32 2, !"air.arg_type_size", i32 4, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"float", !"air.arg_name", !"srlPlaybackCurve"}
!55 = !{ptr addrspace(2) @__metal_implicit_fc_pred_2.43, !"bool", !"useSrl"}
!56 = !{i32 21, !"air.thread_position_in_grid", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"gridPos"}
!57 = !{i32 22, !"air.thread_position_in_threadgroup", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"tgPos"}
!58 = !{i32 23, !"air.threads_per_threadgroup", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"tgSize"}
!59 = !{ptr addrspace(2) @_Z13useImageBlock.MTL_FC_INIT_0_b, !"bool", !"useImageBlock", i32 0, i1 true}
!60 = !{ptr addrspace(2) @_Z13useSrlVersion.MTL_FC_INIT_1_i, !"int", !"useSrlVersion", i32 1, i1 true}
!61 = !{!"air.sampler_state", ptr addrspace(2) @__air_sampler_state}
!62 = !{!"air.sampler_state", ptr addrspace(2) @__air_sampler_state.3}
!63 = !{!64, !64, i64 0}
!64 = !{!"bool", !65, i64 0}
!65 = !{!"omnipotent char", !66, i64 0}
!66 = !{!"Simple C++ TBAA"}
!67 = !{i8 0, i8 2}
!68 = !{!69, !69, i64 0}
!69 = !{!"int", !65, i64 0}
!70 = !{!65, !65, i64 0}
!71 = !{!72}
!72 = distinct !{!72, !73, !"air-alias-scope-arg(19)"}
!73 = distinct !{!73, !"air-alias-scopes(renderFinalAdjustments)"}
!74 = !{!75, !76, !77, !78, !79}
!75 = distinct !{!75, !73, !"air-alias-scope-textures"}
!76 = distinct !{!76, !73, !"air-alias-scope-arg(16)"}
!77 = distinct !{!77, !73, !"air-alias-scope-arg(17)"}
!78 = distinct !{!78, !73, !"air-alias-scope-arg(18)"}
!79 = distinct !{!79, !73, !"air-alias-scope-arg(20)"}
!80 = !{!75}
!81 = !{!76, !77, !78, !72, !79}
!82 = !{!83, !85, i64 668}
!83 = !{!"_ZTS9SSRParams", !84, i64 0, !85, i64 4, !85, i64 8, !85, i64 12, !85, i64 16, !85, i64 20, !85, i64 24, !85, i64 28, !86, i64 32, !87, i64 36, !88, i64 172, !89, i64 436, !90, i64 452, !91, i64 488, !92, i64 556, !93, i64 620, !85, i64 648, !94, i64 652, !85, i64 656, !85, i64 660, !85, i64 664, !85, i64 668}
!84 = !{!"_ZTS11SSRCastType", !65, i64 0}
!85 = !{!"float", !65, i64 0}
!86 = !{!"_ZTS12SSRSceneType", !65, i64 0}
!87 = !{!"_ZTS18SSRCastAdjustments", !85, i64 0, !85, i64 4, !85, i64 8, !85, i64 12, !85, i64 16, !85, i64 20, !65, i64 24, !65, i64 36, !65, i64 48, !85, i64 60, !85, i64 64, !85, i64 68, !65, i64 72, !65, i64 84, !65, i64 96, !85, i64 108, !85, i64 112, !85, i64 116, !85, i64 120, !85, i64 124, !85, i64 128, !85, i64 132}
!88 = !{!"_ZTS18SSRToneAdjustments", !85, i64 0, !85, i64 4, !85, i64 8, !85, i64 12, !85, i64 16, !85, i64 20, !85, i64 24, !85, i64 28, !85, i64 32, !85, i64 36, !85, i64 40, !85, i64 44, !85, i64 48, !85, i64 52, !85, i64 56, !85, i64 60, !85, i64 64, !85, i64 68, !85, i64 72, !85, i64 76, !85, i64 80, !85, i64 84, !85, i64 88, !85, i64 92, !85, i64 96, !85, i64 100, !85, i64 104, !85, i64 108, !85, i64 112, !85, i64 116, !85, i64 120, !85, i64 124, !85, i64 128, !85, i64 132, !85, i64 136, !85, i64 140, !85, i64 144, !85, i64 148, !85, i64 152, !85, i64 156, !85, i64 160, !85, i64 164, !85, i64 168, !85, i64 172, !85, i64 176, !85, i64 180, !85, i64 184, !85, i64 188, !85, i64 192, !85, i64 196, !85, i64 200, !85, i64 204, !85, i64 208, !85, i64 212, !85, i64 216, !85, i64 220, !85, i64 224, !85, i64 228, !85, i64 232, !85, i64 236, !85, i64 240, !85, i64 244, !85, i64 248, !85, i64 252, !85, i64 256, !85, i64 260}
!89 = !{!"_ZTS19SSRColorAdjustments", !85, i64 0, !85, i64 4, !85, i64 8, !85, i64 12}
!90 = !{!"_ZTS18SSRHazeAdjustments", !64, i64 0, !85, i64 4, !85, i64 8, !85, i64 12, !85, i64 16, !85, i64 20, !85, i64 24, !85, i64 28, !85, i64 32}
!91 = !{!"_ZTS15SSRBGAdjustment", !85, i64 0, !85, i64 4, !85, i64 8, !85, i64 12, !85, i64 16, !85, i64 20, !85, i64 24, !85, i64 28, !85, i64 32, !85, i64 36, !85, i64 40, !85, i64 44, !85, i64 48, !85, i64 52, !85, i64 56, !85, i64 60, !85, i64 64}
!92 = !{!"_ZTS15SSRFGAdjustment", !85, i64 0, !85, i64 4, !85, i64 8, !85, i64 12, !85, i64 16, !85, i64 20, !85, i64 24, !85, i64 28, !85, i64 32, !85, i64 36, !85, i64 40, !85, i64 44, !85, i64 48, !85, i64 52, !85, i64 56, !85, i64 60}
!93 = !{!"_ZTS25SSRSemanticToneAdjustment", !85, i64 0, !85, i64 4, !85, i64 8, !85, i64 12, !85, i64 16, !85, i64 20, !85, i64 24}
!94 = !{!"_ZTS13SSRTuningType", !65, i64 0}
!95 = !{!77}
!96 = !{!75, !76, !78, !72, !79}
!97 = !{!83, !85, i64 168}
!98 = !{!85, !85, i64 0}
!99 = !{!79}
!100 = !{!75, !76, !77, !78, !72}
!101 = !{!102, !104, i64 0}
!102 = !{!"_ZTS18SSRColorManagement", !103, i64 0, !103, i64 80, !103, i64 160, !103, i64 240}
!103 = !{!"_ZTS18SSRColorConversion", !104, i64 0, !105, i64 16, !64, i64 64}
!104 = !{!"_ZTS19CMITransferFunction", !65, i64 0}
!105 = !{!"_ZTSN5metal6matrixIfLi3ELi3EvEE", !65, i64 0}
!106 = !{!76}
!107 = !{!75, !77, !78, !72, !79}
!108 = !{!102, !64, i64 64}
!109 = !{!83, !85, i64 28}
!110 = !{!83, !85, i64 8}
!111 = !{!83, !85, i64 4}
!112 = !{!83, !84, i64 0}
!113 = !{!83, !85, i64 628}
!114 = !{!83, !85, i64 632}
!115 = !{!83, !85, i64 640}
!116 = !{!83, !85, i64 644}
!117 = !{!83, !85, i64 24}
!118 = !{!93, !85, i64 4}
!119 = !{!93, !85, i64 0}
!120 = !{!83, !85, i64 12}
!121 = !{!83, !85, i64 444}
!122 = !{!78}
!123 = !{!75, !76, !77, !72, !79}
!124 = !{!77, !78}
!125 = !{!75, !76, !72, !79}
!126 = !{!83, !85, i64 448}
!127 = !{!83, !94, i64 652}
!128 = !{!83, !85, i64 432}
!129 = !{!83, !85, i64 16}
!130 = !{!83, !85, i64 20}
!131 = !{!87, !85, i64 124}
!132 = !{!133, !85, i64 16}
!133 = !{!"_ZTS14SSRGlobalStats", !85, i64 0, !85, i64 4, !85, i64 8, !85, i64 12, !85, i64 16, !85, i64 20, !85, i64 24, !85, i64 28, !85, i64 32}
!134 = !{!87, !85, i64 128}
!135 = !{!102, !104, i64 240}
!136 = !{!83, !85, i64 240}
!137 = !{!83, !85, i64 244}
!138 = !{!83, !85, i64 248}
!139 = !{i64 0, i64 4, !98, i64 4, i64 4, !98, i64 8, i64 4, !98, i64 12, i64 4, !98, i64 16, i64 4, !98, i64 20, i64 4, !98, i64 24, i64 4, !98, i64 28, i64 4, !98}
!140 = !{i64 0, i64 4, !98, i64 4, i64 4, !98, i64 8, i64 4, !98, i64 12, i64 4, !98, i64 16, i64 4, !98, i64 20, i64 4, !98, i64 24, i64 4, !98}
!141 = !{i64 0, i64 4, !98, i64 4, i64 4, !98, i64 8, i64 4, !98, i64 12, i64 4, !98, i64 16, i64 4, !98, i64 20, i64 4, !98}
!142 = !{i64 0, i64 4, !98, i64 4, i64 4, !98, i64 8, i64 4, !98, i64 12, i64 4, !98, i64 16, i64 4, !98}
!143 = !{i64 0, i64 4, !98, i64 4, i64 4, !98, i64 8, i64 4, !98, i64 12, i64 4, !98}
!144 = !{i64 0, i64 4, !98, i64 4, i64 4, !98, i64 8, i64 4, !98}
!145 = !{i64 0, i64 4, !98, i64 4, i64 4, !98}
!146 = !{i64 0, i64 4, !98}
!147 = !{!83, !85, i64 252}
!148 = !{!87, !85, i64 60}
!149 = !{!87, !85, i64 64}
!150 = !{!87, !85, i64 68}
!151 = !{!87, !85, i64 0}
!152 = !{!153, !153, i64 0}
!153 = !{!"half", !65, i64 0}
!154 = distinct !{!154, !155}
!155 = !{!"llvm.loop.mustprogress"}
!156 = !{i64 0, i64 24, !70}
!157 = !{i64 0, i64 16, !70}
!158 = !{i64 0, i64 8, !70}
!159 = !{!87, !85, i64 8}
!160 = !{!87, !85, i64 4}
!161 = !{!87, !85, i64 12}
!162 = !{!87, !85, i64 16}
!163 = !{!87, !85, i64 20}
!164 = !{!87, !85, i64 108}
!165 = !{!87, !85, i64 112}
!166 = !{!87, !85, i64 116}
!167 = !{!87, !85, i64 120}
!168 = !{!133, !85, i64 0}
!169 = !{!133, !85, i64 24}
!170 = !{!92, !85, i64 40}
!171 = !{!92, !85, i64 36}
!172 = !{!92, !85, i64 0}
!173 = !{!92, !85, i64 16}
!174 = !{!92, !85, i64 24}
!175 = !{!92, !85, i64 60}
!176 = !{!92, !85, i64 28}
!177 = !{!92, !85, i64 44}
!178 = !{!92, !85, i64 20}
!179 = !{!92, !85, i64 8}
!180 = !{!92, !85, i64 56}
!181 = !{!92, !85, i64 12}
!182 = !{!92, !85, i64 32}
!183 = !{!91, !85, i64 12}
!184 = !{!91, !85, i64 4}
!185 = !{!91, !85, i64 0}
!186 = !{!91, !85, i64 44}
!187 = !{!91, !85, i64 28}
!188 = !{!91, !85, i64 32}
!189 = !{!91, !85, i64 20}
!190 = !{!91, !85, i64 16}
!191 = !{!91, !85, i64 36}
!192 = !{!91, !85, i64 40}
!193 = !{!91, !85, i64 8}
!194 = !{!93, !85, i64 16}
!195 = !{!93, !85, i64 8}
!196 = !{!93, !85, i64 20}
!197 = !{!93, !85, i64 12}
!198 = !{!93, !85, i64 24}
