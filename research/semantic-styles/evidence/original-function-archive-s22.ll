target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v24:32:32-v32:32:32-v48:64:64-v64:64:64-v96:128:128-v128:128:128-v192:256:256-v256:256:256-v512:512:512-v1024:1024:1024-n8:16:32"
target triple = "air64-apple-macosx15.0.0"

%"struct.metal::_imageblock_base.189" = type { ptr addrspace(4) }
%"struct.metal::matrix.194" = type { [3 x <3 x half>] }
%struct.SSRRenderROI = type { <2 x i16>, <2 x i16>, <2 x i16>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <4 x float>, <2 x i16>, [12 x i8] }
%struct.SSRParams = type { i32, float, float, float, float, float, float, float, i32, %struct.SSRCastAdjustments, %struct.SSRToneAdjustments, %struct.SSRColorAdjustments, %struct.SSRHazeAdjustments, %struct.SSRBGAdjustment, %struct.SSRFGAdjustment, %struct.SSRSemanticToneAdjustment, float, i32, float, float, float, float }
%struct.SSRCastAdjustments = type { float, float, float, float, float, float, [3 x float], [3 x float], [3 x float], float, float, float, [3 x float], [3 x float], [3 x float], float, float, float, float, float, float, float }
%struct.SSRToneAdjustments = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRColorAdjustments = type { float, float, float, float }
%struct.SSRHazeAdjustments = type { i8, float, float, float, float, float, float, float, float }
%struct.SSRBGAdjustment = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRFGAdjustment = type { float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float }
%struct.SSRSemanticToneAdjustment = type { float, float, float, float, float, float, float }
%struct.SSRColorManagement.192 = type { %struct.SSRColorConversion.191, %struct.SSRColorConversion.191, %struct.SSRColorConversion.191, %struct.SSRColorConversion.191 }
%struct.SSRColorConversion.191 = type <{ i32, [12 x i8], %"struct.metal::matrix.17.190", i8, [15 x i8] }>
%"struct.metal::matrix.17.190" = type { [3 x <3 x float>] }
%struct.SSRStats = type { [10 x [256 x i32]], [10 x %struct.SSRGlobalStats], i32, i32, float, float, %struct.SSRBasicStats, %struct.SSRBasicStats }
%struct.SSRGlobalStats = type { float, float, float, float, float, float, float, float, float }
%struct.SSRBasicStats = type { float, float, float }

@llvm.global_ctors = appending global [0 x { i32, ptr, ptr }] zeroinitializer
@__air_sampler_state = internal addrspace(2) constant i64 -9188470239253722551, align 8
@__air_sampler_state.3 = internal addrspace(2) constant i64 -9188470239253755319, align 8

; Function Attrs: convergent mustprogress nounwind willreturn
define void @renderFinalAdjustments(%"struct.metal::_imageblock_base.189" %0, ptr addrspace(1) readonly captures(none) %1, ptr addrspace(1) readonly captures(none) %2, ptr addrspace(1) readonly captures(none) %3, ptr addrspace(1) readonly captures(none) %4, ptr addrspace(1) readnone captures(none) %5, ptr addrspace(1) readonly captures(none) %6, ptr addrspace(1) readonly captures(none) %7, ptr addrspace(1) readonly captures(none) %8, ptr addrspace(1) readonly captures(none) %9, ptr addrspace(1) readonly captures(none) %10, ptr addrspace(1) readonly captures(none) %11, ptr addrspace(1) readonly captures(none) %12, ptr addrspace(1) readonly captures(none) %13, ptr addrspace(1) captures(none) %14, ptr addrspace(1) readnone captures(none) %15, ptr addrspace(2) noundef readonly align 16 captures(none) dereferenceable(320) "air-buffer-no-alias" %16, ptr addrspace(1) noundef align 4 captures(none) dereferenceable(672) "air-buffer-no-alias" %17, ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(10640) "air-buffer-no-alias" %18, ptr addrspace(2) noundef readonly align 16 captures(none) dereferenceable(176) "air-buffer-no-alias" %19, <2 x i16> noundef %20, <2 x i16> noundef %21, <2 x i16> noundef %22) local_unnamed_addr #0 {
  %24 = alloca %"struct.metal::matrix.194", align 8
  %25 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %19, i64 0, i32 12
  %26 = load <2 x i16>, ptr addrspace(2) %25, align 16, !tbaa !59, !alias.scope !62, !noalias !69
  %27 = add <2 x i16> %26, %20
  %28 = tail call fast <2 x float> @air.convert.f.v2f32.u.v2i16(<2 x i16> %20) #14
  %29 = fadd fast <2 x float> %28, splat (float 5.000000e-01)
  %30 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %19, i64 0, i32 3
  %31 = load <4 x float>, ptr addrspace(2) %30, align 16, !alias.scope !62, !noalias !69
  %32 = shufflevector <4 x float> %31, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %33 = fmul fast <2 x float> %32, %29
  %34 = shufflevector <4 x float> %31, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %35 = fadd fast <2 x float> %33, %34
  %36 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %1, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %35, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %37 = extractvalue { <4 x half>, i8 } %36, 0
  %38 = shufflevector <4 x half> %37, <4 x half> poison, <3 x i32> <i32 0, i32 1, i32 2>
  %39 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %19, i64 0, i32 10
  %40 = load <4 x float>, ptr addrspace(2) %39, align 16, !alias.scope !62, !noalias !69
  %41 = shufflevector <4 x float> %40, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %42 = fmul fast <2 x float> %41, %29
  %43 = shufflevector <4 x float> %40, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %44 = fadd fast <2 x float> %42, %43
  %45 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %19, i64 0, i32 11
  %46 = load <4 x float>, ptr addrspace(2) %45, align 16, !alias.scope !62, !noalias !69
  %47 = shufflevector <4 x float> %46, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %48 = fmul fast <2 x float> %47, %29
  %49 = shufflevector <4 x float> %46, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %50 = fadd fast <2 x float> %48, %49
  %51 = tail call i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none) %10) #16, !alias.scope !82, !noalias !83
  br i1 %51, label %62, label %52

52:                                               ; preds = %23
  %53 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %19, i64 0, i32 9
  %54 = load <4 x float>, ptr addrspace(2) %53, align 16, !alias.scope !62, !noalias !69
  %55 = shufflevector <4 x float> %54, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %56 = fmul fast <2 x float> %55, %29
  %57 = shufflevector <4 x float> %54, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %58 = fadd fast <2 x float> %56, %57
  %59 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %10, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %58, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %60 = extractvalue { <4 x half>, i8 } %59, 0
  %61 = extractelement <4 x half> %60, i64 0
  br label %62

62:                                               ; preds = %52, %23
  %63 = phi fast half [ %61, %52 ], [ 0xH0000, %23 ]
  %64 = tail call i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none) %11) #16, !alias.scope !82, !noalias !83
  br i1 %64, label %69, label %65

65:                                               ; preds = %62
  %66 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %11, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %44, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %67 = extractvalue { <4 x half>, i8 } %66, 0
  %68 = extractelement <4 x half> %67, i64 0
  br label %69

69:                                               ; preds = %65, %62
  %70 = phi fast half [ %68, %65 ], [ 0xH0000, %62 ]
  %71 = tail call i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none) %12) #16, !alias.scope !82, !noalias !83
  br i1 %71, label %76, label %72

72:                                               ; preds = %69
  %73 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %12, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %50, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %74 = extractvalue { <4 x half>, i8 } %73, 0
  %75 = extractelement <4 x half> %74, i64 0
  br label %76

76:                                               ; preds = %72, %69
  %77 = phi fast half [ %75, %72 ], [ 0xH0000, %69 ]
  %78 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 21
  %79 = load float, ptr addrspace(1) %78, align 4, !tbaa !84, !alias.scope !98, !noalias !99
  %80 = fcmp fast ult float %79, 0.000000e+00
  br i1 %80, label %94, label %81

81:                                               ; preds = %76
  %82 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 21
  %83 = load float, ptr addrspace(1) %82, align 4, !tbaa !100, !alias.scope !98, !noalias !99
  %84 = fdiv fast float %79, %83
  %85 = tail call fast float @air.fast_clamp.f32(float %84, float 0.000000e+00, float 1.000000e+00) #14
  %86 = fmul fast float %85, %85
  %87 = fmul fast float %85, 2.000000e+00
  %88 = fsub fast float 3.000000e+00, %87
  %89 = fmul fast float %86, %88
  %90 = tail call fast float @air.fast_fmax.f32(float %89, float 0x3FD3333340000000) #14
  %91 = fptrunc float %90 to half
  %92 = fmul fast half %63, %91
  %93 = fmul fast half %70, %91
  br label %94

94:                                               ; preds = %81, %76
  %95 = phi half [ %93, %81 ], [ %70, %76 ]
  %96 = phi half [ %92, %81 ], [ %63, %76 ]
  %97 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 0, i32 0
  %98 = load i32, ptr addrspace(2) %97, align 16, !tbaa !101, !alias.scope !106, !noalias !107
  switch i32 %98, label %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit [
    i32 0, label %99
    i32 1, label %99
    i32 2, label %100
    i32 3, label %105
    i32 4, label %115
    i32 5, label %125
    i32 6, label %135
    i32 7, label %148
    i32 8, label %162
  ]

99:                                               ; preds = %94, %94
  br label %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

100:                                              ; preds = %94
  %101 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %38) #14
  %102 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %38) #14
  %103 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %102, <3 x half> splat (half 0xH3C00)) #14
  %104 = fmul fast <3 x half> %103, %101
  br label %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

105:                                              ; preds = %94
  %106 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %38) #14
  %107 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %38) #14
  %108 = fmul fast <3 x half> %107, splat (half 0xH2CF4)
  %109 = fadd fast <3 x half> %107, splat (half 0xH2B0A)
  %110 = fmul fast <3 x half> %109, splat (half 0xH3B96)
  %111 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %110, <3 x half> splat (half 0xH40CD)) #14
  %112 = fcmp fast ogt <3 x half> %107, splat (half 0xH292D)
  %113 = select fast <3 x i1> %112, <3 x half> %111, <3 x half> %108
  %114 = fmul fast <3 x half> %113, %106
  br label %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

115:                                              ; preds = %94
  %116 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %38) #14
  %117 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %38) #14
  %118 = fmul fast <3 x half> %117, splat (half 0xH331C)
  %119 = fadd fast <3 x half> %117, splat (half 0xH2E56)
  %120 = fmul fast <3 x half> %119, splat (half 0xH3B48)
  %121 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %120, <3 x half> splat (half 0xH4072)) #14
  %122 = fcmp fast ogt <3 x half> %117, splat (half 0xH2D30)
  %123 = select fast <3 x i1> %122, <3 x half> %121, <3 x half> %118
  %124 = fmul fast <3 x half> %123, %116
  br label %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

125:                                              ; preds = %94
  %126 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %38) #14
  %127 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %38) #14
  %128 = fmul fast <3 x half> %127, splat (half 0xH331C)
  %129 = fadd fast <3 x half> %127, splat (half 0xH2E5B)
  %130 = fmul fast <3 x half> %129, splat (half 0xH3B46)
  %131 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %130, <3 x half> splat (half 0xH4072)) #14
  %132 = fcmp fast ogt <3 x half> %127, splat (half 0xH2D33)
  %133 = select fast <3 x i1> %132, <3 x half> %131, <3 x half> %128
  %134 = fmul fast <3 x half> %133, %126
  br label %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

135:                                              ; preds = %94
  %136 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %38) #14
  %137 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %38) #14
  %138 = fmul fast <3 x half> %137, %137
  %139 = fmul fast <3 x half> %138, splat (half 0xH3555)
  %140 = fadd fast <3 x half> %137, splat (half 0xHB87B)
  %141 = fmul fast <3 x half> %140, splat (half 0xH4598)
  %142 = tail call fast <3 x half> @air.exp.v3f16(<3 x half> %141) #14
  %143 = fadd fast <3 x half> %142, splat (half 0xH348E)
  %144 = fmul fast <3 x half> %143, splat (half 0xH2D55)
  %145 = fcmp fast ogt <3 x half> %137, splat (half 0xH3800)
  %146 = select fast <3 x i1> %145, <3 x half> %144, <3 x half> %139
  %147 = fmul fast <3 x half> %146, %136
  br label %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

148:                                              ; preds = %94
  %149 = fadd fast <3 x half> %38, splat (half 0xHB98C)
  %150 = fmul fast <3 x half> %149, splat (half 0xH49D9)
  %151 = tail call fast <3 x half> @air.powr.v3f16(<3 x half> splat (half 0xH4000), <3 x half> %150) #14
  %152 = fadd fast <3 x half> %151, splat (half 0xHA0F0)
  %153 = fcmp fast oge <3 x half> %38, splat (half 0xH32AC)
  %154 = select fast <3 x i1> %153, <3 x half> %152, <3 x half> splat (half 0xHAB38)
  %155 = fmul fast <3 x half> %38, splat (half 0xH256A)
  %156 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %155) #14
  %157 = fadd fast <3 x half> %156, splat (half 0xHAB38)
  %158 = fcmp fast oge <3 x half> %38, zeroinitializer
  %159 = fcmp fast olt <3 x half> %38, splat (half 0xH32AC)
  %160 = and <3 x i1> %158, %159
  %161 = select fast <3 x i1> %160, <3 x half> %157, <3 x half> %154
  br label %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

162:                                              ; preds = %94
  %163 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %38) #14
  %164 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %38) #14
  %165 = fadd fast <3 x half> %164, splat (half 0xH3900)
  %166 = fdiv fast <3 x half> %165, zeroinitializer
  %167 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %166, <3 x half> splat (half 0xH3F33)) #14
  %168 = fcmp fast ogt <3 x half> %164, splat (half 0xH1800)
  %169 = select fast <3 x i1> %168, <3 x half> %167, <3 x half> %164
  %170 = fmul fast <3 x half> %169, %163
  br label %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit: ; preds = %162, %148, %135, %125, %115, %105, %100, %99, %94
  %171 = phi <3 x half> [ zeroinitializer, %94 ], [ %170, %162 ], [ %161, %148 ], [ %147, %135 ], [ %134, %125 ], [ %124, %115 ], [ %114, %105 ], [ %104, %100 ], [ %38, %99 ]
  %172 = icmp eq i32 %98, 6
  br i1 %172, label %173, label %209

173:                                              ; preds = %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit
  %174 = tail call fast half @air.log2.f16(half 0xH2E66) #14
  %175 = tail call fast half @air.pow.f16(half 0xH3C72, half %174) #14
  %176 = fpext half %175 to float
  %177 = fmul fast float %176, 0x3FF3333340000000
  %178 = fptrunc float %177 to half
  %179 = extractelement <3 x half> %171, i64 0
  %180 = fpext half %179 to float
  %181 = fmul fast float %180, 0x3FD0D013A0000000
  %182 = extractelement <3 x half> %171, i64 1
  %183 = fpext half %182 to float
  %184 = fmul fast float %183, 0x3FE5B22D00000000
  %185 = fadd fast float %181, %184
  %186 = extractelement <3 x half> %171, i64 2
  %187 = fpext half %186 to float
  %188 = fmul fast float %187, 0x3FAE5C91E0000000
  %189 = fadd fast float %185, %188
  %190 = fpext half %178 to float
  %191 = fadd fast float %190, -1.000000e+00
  %192 = tail call fast float @air.fast_pow.f32(float %189, float %191) #14
  %193 = fptrunc float %192 to half
  %194 = fmul fast half %179, 0xH32D1
  %195 = fmul fast half %182, 0xH39B8
  %196 = fadd fast half %194, %195
  %197 = fmul fast half %186, 0xH2C9C
  %198 = fadd fast half %196, %197
  %199 = tail call fast half @air.fmax.f16(half %179, half %182) #14
  %200 = tail call fast half @air.fmax.f16(half %199, half %186) #14
  %201 = fadd fast half %198, %200
  %202 = fmul fast half %201, 0xH3800
  %203 = fadd fast half %178, 0xHBC00
  %204 = tail call fast half @air.pow.f16(half %202, half %203) #14
  %205 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 0, i32 3
  %206 = load i8, ptr addrspace(2) %205, align 16, !tbaa !108, !range !109, !alias.scope !106, !noalias !107
  %207 = icmp eq i8 %206, 0
  %208 = select fast i1 %207, half %193, half %204
  br label %209

209:                                              ; preds = %173, %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit
  %210 = phi half [ %208, %173 ], [ 0xH3C00, %_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit ]
  %211 = insertelement <3 x half> poison, half %210, i64 0
  %212 = shufflevector <3 x half> %211, <3 x half> poison, <3 x i32> zeroinitializer
  %213 = fmul fast <3 x half> %212, %171
  %214 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 0, i32 2, i32 0, i64 0
  %215 = load <3 x float>, ptr addrspace(2) %214, align 16, !tbaa !110, !alias.scope !106, !noalias !107
  %216 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %215) #14
  %217 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 0, i32 2, i32 0, i64 1
  %218 = load <3 x float>, ptr addrspace(2) %217, align 16, !tbaa !110, !alias.scope !106, !noalias !107
  %219 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %218) #14
  %220 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 0, i32 2, i32 0, i64 2
  %221 = load <3 x float>, ptr addrspace(2) %220, align 16, !tbaa !110, !alias.scope !106, !noalias !107
  %222 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %221) #14
  %223 = shufflevector <3 x half> %213, <3 x half> poison, <3 x i32> zeroinitializer
  %224 = fmul fast <3 x half> %223, %216
  %225 = shufflevector <3 x half> %213, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %226 = fmul fast <3 x half> %219, %225
  %227 = fadd fast <3 x half> %224, %226
  %228 = shufflevector <3 x half> %213, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %229 = fmul fast <3 x half> %222, %228
  %230 = fadd fast <3 x half> %227, %229
  %231 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %19, i64 0, i32 7
  %232 = load <4 x float>, ptr addrspace(2) %231, align 16, !alias.scope !62, !noalias !69
  %233 = shufflevector <4 x float> %232, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %234 = fmul fast <2 x float> %233, %29
  %235 = shufflevector <4 x float> %232, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %236 = fadd fast <2 x float> %234, %235
  %237 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %19, i64 0, i32 8
  %238 = load <4 x float>, ptr addrspace(2) %237, align 16, !alias.scope !62, !noalias !69
  %239 = shufflevector <4 x float> %238, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %240 = fmul fast <2 x float> %239, %29
  %241 = shufflevector <4 x float> %238, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %242 = fadd fast <2 x float> %240, %241
  %243 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %8, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %236, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %244 = extractvalue { <4 x half>, i8 } %243, 0
  %245 = extractelement <4 x half> %244, i64 0
  %246 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %9, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %242, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %247 = extractvalue { <4 x half>, i8 } %246, 0
  %248 = extractelement <4 x half> %247, i64 0
  %249 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 7
  %250 = load float, ptr addrspace(1) %249, align 4, !tbaa !111, !alias.scope !98, !noalias !99
  %251 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 2
  %252 = load float, ptr addrspace(1) %251, align 4, !tbaa !112, !alias.scope !98, !noalias !99
  %253 = fcmp fast ugt float %252, 0.000000e+00
  br i1 %253, label %254, label %261

254:                                              ; preds = %209
  %255 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 1
  %256 = load float, ptr addrspace(1) %255, align 4, !tbaa !113, !alias.scope !98, !noalias !99
  %257 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 0
  %258 = load i32, ptr addrspace(1) %257, align 4, !tbaa !114, !alias.scope !98, !noalias !99
  %259 = fmul fast float %256, 5.000000e-01
  %260 = fsub fast float 1.000000e+00, %259
  br label %277

261:                                              ; preds = %209
  %262 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 15, i32 2
  %263 = load float, ptr addrspace(1) %262, align 4, !tbaa !115, !alias.scope !98, !noalias !99
  %264 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 1
  %265 = load float, ptr addrspace(1) %264, align 4, !tbaa !113, !alias.scope !98, !noalias !99
  %266 = fmul fast float %265, 5.000000e-01
  %267 = fsub fast float 1.000000e+00, %266
  %268 = tail call fast float @air.mix.f32(float %263, float %250, float %267) #14
  %269 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 0
  %270 = load i32, ptr addrspace(1) %269, align 4, !tbaa !114, !alias.scope !98, !noalias !99
  %271 = icmp eq i32 %270, 2
  %272 = select reassoc nsz arcp contract afn i1 %271, float %268, float %263
  store float %272, ptr addrspace(1) %262, align 4, !tbaa !115, !alias.scope !98, !noalias !99
  %273 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 15, i32 3
  %274 = load float, ptr addrspace(1) %273, align 4, !tbaa !116, !alias.scope !98, !noalias !99
  %275 = tail call fast float @air.mix.f32(float %274, float %250, float %267) #14
  %276 = select reassoc nsz arcp contract afn i1 %271, float %275, float %274
  store float %276, ptr addrspace(1) %273, align 4, !tbaa !116, !alias.scope !98, !noalias !99
  br label %277

277:                                              ; preds = %261, %254
  %278 = phi float [ %260, %254 ], [ %267, %261 ]
  %279 = phi i32 [ %258, %254 ], [ %270, %261 ]
  %280 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 15
  %281 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 15, i32 5
  %282 = load float, ptr addrspace(1) %281, align 4, !tbaa !117, !alias.scope !98, !noalias !99
  %283 = tail call fast float @air.mix.f32(float %282, float 1.000000e+00, float %278) #14
  %284 = icmp eq i32 %279, 2
  %285 = select reassoc nsz arcp contract afn i1 %284, float %283, float %282
  store float %285, ptr addrspace(1) %281, align 4, !tbaa !117, !alias.scope !98, !noalias !99
  %286 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 15, i32 6
  %287 = load float, ptr addrspace(1) %286, align 4, !tbaa !118, !alias.scope !98, !noalias !99
  %288 = tail call fast float @air.mix.f32(float %287, float 1.000000e+00, float %278) #14
  %289 = select reassoc nsz arcp contract afn i1 %284, float %288, float %287
  store float %289, ptr addrspace(1) %286, align 4, !tbaa !118, !alias.scope !98, !noalias !99
  %290 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %19, i64 0, i32 4
  %291 = load <4 x float>, ptr addrspace(2) %290, align 16, !alias.scope !62, !noalias !69
  %292 = shufflevector <4 x float> %291, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %293 = fmul fast <2 x float> %292, %29
  %294 = shufflevector <4 x float> %291, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %295 = fadd fast <2 x float> %293, %294
  %296 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %2, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %295, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %297 = extractvalue { <4 x half>, i8 } %296, 0
  %298 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 1, i32 2, i32 0, i64 0
  %299 = load <3 x float>, ptr addrspace(2) %298, align 16, !tbaa !110, !alias.scope !106, !noalias !107
  %300 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %299) #14
  %301 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 1, i32 2, i32 0, i64 1
  %302 = load <3 x float>, ptr addrspace(2) %301, align 16, !tbaa !110, !alias.scope !106, !noalias !107
  %303 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %302) #14
  %304 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 1, i32 2, i32 0, i64 2
  %305 = load <3 x float>, ptr addrspace(2) %304, align 16, !tbaa !110, !alias.scope !106, !noalias !107
  %306 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %305) #14
  %307 = shufflevector <4 x half> %297, <4 x half> undef, <3 x i32> zeroinitializer
  %308 = fmul fast <3 x half> %300, %307
  %309 = shufflevector <4 x half> %297, <4 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %310 = fmul fast <3 x half> %303, %309
  %311 = fadd fast <3 x half> %310, %308
  %312 = shufflevector <4 x half> %297, <4 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %313 = fmul fast <3 x half> %306, %312
  %314 = fadd fast <3 x half> %311, %313
  %315 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 6
  %316 = load float, ptr addrspace(1) %315, align 4, !tbaa !119, !alias.scope !98, !noalias !99
  %317 = fptrunc float %316 to half
  %318 = insertelement <3 x half> poison, half %317, i64 0
  %319 = shufflevector <3 x half> %318, <3 x half> poison, <3 x i32> zeroinitializer
  %320 = fmul fast <3 x half> %319, %314
  %321 = tail call i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none) %6) #16, !alias.scope !82, !noalias !83
  br i1 %321, label %370, label %322

322:                                              ; preds = %277
  %323 = tail call i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none) %7) #16, !alias.scope !82, !noalias !83
  br i1 %323, label %370, label %324

324:                                              ; preds = %322
  %325 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %19, i64 0, i32 5
  %326 = load <4 x float>, ptr addrspace(2) %325, align 16, !alias.scope !62, !noalias !69
  %327 = shufflevector <4 x float> %326, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %328 = fmul fast <2 x float> %327, %29
  %329 = shufflevector <4 x float> %326, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %330 = fadd fast <2 x float> %328, %329
  %331 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %19, i64 0, i32 6
  %332 = load <4 x float>, ptr addrspace(2) %331, align 16, !alias.scope !62, !noalias !69
  %333 = shufflevector <4 x float> %332, <4 x float> poison, <2 x i32> <i32 0, i32 1>
  %334 = fmul fast <2 x float> %333, %29
  %335 = shufflevector <4 x float> %332, <4 x float> poison, <2 x i32> <i32 2, i32 3>
  %336 = fadd fast <2 x float> %334, %335
  %337 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %6, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %330, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %338 = extractvalue { <4 x half>, i8 } %337, 0
  %339 = shufflevector <4 x half> %338, <4 x half> poison, <3 x i32> <i32 0, i32 1, i32 2>
  %340 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %7, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %336, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %341 = extractvalue { <4 x half>, i8 } %340, 0
  %342 = shufflevector <4 x half> %341, <4 x half> poison, <3 x i32> <i32 0, i32 1, i32 2>
  %343 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 15, i32 1
  %344 = load float, ptr addrspace(1) %343, align 4, !tbaa !120, !alias.scope !98, !noalias !99
  %345 = fptrunc float %344 to half
  %346 = fptrunc float %289 to half
  %347 = insertelement <3 x half> poison, half %345, i64 0
  %348 = shufflevector <3 x half> %347, <3 x half> poison, <3 x i32> zeroinitializer
  %349 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %342, <3 x half> splat (half 0xH3C00), <3 x half> %348) #14
  %350 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %349, <3 x half> splat (half 0xH3C00)) #14
  %351 = insertelement <3 x half> poison, half %346, i64 0
  %352 = shufflevector <3 x half> %351, <3 x half> poison, <3 x i32> zeroinitializer
  %353 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %349, <3 x half> %350, <3 x half> %352) #14
  %354 = fmul fast <3 x half> %353, %230
  %355 = getelementptr inbounds %struct.SSRSemanticToneAdjustment, ptr addrspace(1) %280, i64 0, i32 0
  %356 = load float, ptr addrspace(1) %355, align 4, !tbaa !121, !alias.scope !98, !noalias !99
  %357 = fptrunc float %356 to half
  %358 = fptrunc float %285 to half
  %359 = insertelement <3 x half> poison, half %357, i64 0
  %360 = shufflevector <3 x half> %359, <3 x half> poison, <3 x i32> zeroinitializer
  %361 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %339, <3 x half> splat (half 0xH3C00), <3 x half> %360) #14
  %362 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %361, <3 x half> splat (half 0xH3C00)) #14
  %363 = insertelement <3 x half> poison, half %358, i64 0
  %364 = shufflevector <3 x half> %363, <3 x half> poison, <3 x i32> zeroinitializer
  %365 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %361, <3 x half> %362, <3 x half> %364) #14
  %366 = fmul fast <3 x half> %365, %230
  %367 = insertelement <3 x half> poison, half %96, i64 0
  %368 = shufflevector <3 x half> %367, <3 x half> poison, <3 x i32> zeroinitializer
  %369 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %366, <3 x half> %354, <3 x half> %368) #14
  br label %482

370:                                              ; preds = %322, %277
  %371 = tail call i32 @air.get_width_texture_2d(ptr addrspace(1) readonly captures(none) %3, i32 0) #16, !alias.scope !82, !noalias !83
  %372 = tail call fast half @air.convert.f.f16.u.i32(i32 %371) #14
  %373 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 15, i32 4
  %374 = load float, ptr addrspace(1) %373, align 4, !tbaa !122, !alias.scope !98, !noalias !99
  %375 = fptrunc float %374 to half
  %376 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 15, i32 2
  %377 = load float, ptr addrspace(1) %376, align 4, !tbaa !123, !alias.scope !98, !noalias !99
  %378 = fptrunc float %377 to half
  %379 = insertelement <3 x half> poison, half %378, i64 0
  %380 = shufflevector <3 x half> %379, <3 x half> poison, <3 x i32> zeroinitializer
  %381 = fmul fast <3 x half> %380, %320
  %382 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %381, <3 x half> splat (half 0xH3C00)) #14
  %383 = extractelement <3 x half> %382, i64 0
  %384 = fadd fast half %372, 0xHBC00
  %385 = fmul fast half %383, %384
  %386 = fpext half %385 to float
  %387 = fadd fast float %386, 5.000000e-01
  %388 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %387, i64 0
  %389 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %388, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %390 = extractvalue { <4 x half>, i8 } %389, 0
  %391 = extractelement <4 x half> %390, i64 0
  %392 = insertelement <3 x half> undef, half %391, i64 0
  %393 = extractelement <3 x half> %382, i64 1
  %394 = fmul fast half %393, %384
  %395 = fpext half %394 to float
  %396 = fadd fast float %395, 5.000000e-01
  %397 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %396, i64 0
  %398 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %397, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %399 = extractvalue { <4 x half>, i8 } %398, 0
  %400 = extractelement <4 x half> %399, i64 0
  %401 = insertelement <3 x half> %392, half %400, i64 1
  %402 = extractelement <3 x half> %382, i64 2
  %403 = fmul fast half %402, %384
  %404 = fpext half %403 to float
  %405 = fadd fast float %404, 5.000000e-01
  %406 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %405, i64 0
  %407 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %406, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %408 = extractvalue { <4 x half>, i8 } %407, 0
  %409 = extractelement <4 x half> %408, i64 0
  %410 = insertelement <3 x half> %401, half %409, i64 2
  %411 = insertelement <3 x half> undef, half %375, i64 0
  %412 = shufflevector <3 x half> %411, <3 x half> poison, <3 x i32> zeroinitializer
  %413 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %382, <3 x half> %410, <3 x half> %412) #14
  %414 = fdiv fast <3 x half> %413, %230
  %415 = fadd fast <3 x half> %230, splat (half 0xH9C04)
  %416 = fcmp fast olt <3 x half> %415, zeroinitializer
  %417 = select fast <3 x i1> %416, <3 x half> zeroinitializer, <3 x half> %414
  %418 = getelementptr inbounds %struct.SSRSemanticToneAdjustment, ptr addrspace(1) %280, i64 0, i32 0
  %419 = load float, ptr addrspace(1) %418, align 4, !tbaa !121, !alias.scope !98, !noalias !99
  %420 = fptrunc float %419 to half
  %421 = fptrunc float %285 to half
  %422 = insertelement <3 x half> poison, half %420, i64 0
  %423 = shufflevector <3 x half> %422, <3 x half> poison, <3 x i32> zeroinitializer
  %424 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %417, <3 x half> splat (half 0xH3C00), <3 x half> %423) #14
  %425 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %424, <3 x half> splat (half 0xH3C00)) #14
  %426 = insertelement <3 x half> poison, half %421, i64 0
  %427 = shufflevector <3 x half> %426, <3 x half> poison, <3 x i32> zeroinitializer
  %428 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %424, <3 x half> %425, <3 x half> %427) #14
  %429 = fmul fast <3 x half> %428, %230
  %430 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 15, i32 3
  %431 = load float, ptr addrspace(1) %430, align 4, !tbaa !124, !alias.scope !98, !noalias !99
  %432 = fptrunc float %431 to half
  %433 = insertelement <3 x half> poison, half %432, i64 0
  %434 = shufflevector <3 x half> %433, <3 x half> poison, <3 x i32> zeroinitializer
  %435 = fmul fast <3 x half> %434, %320
  %436 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %435, <3 x half> splat (half 0xH3C00)) #14
  %437 = extractelement <3 x half> %436, i64 0
  %438 = fmul fast half %437, %384
  %439 = fpext half %438 to float
  %440 = fadd fast float %439, 5.000000e-01
  %441 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %440, i64 0
  %442 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %441, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %443 = extractvalue { <4 x half>, i8 } %442, 0
  %444 = extractelement <4 x half> %443, i64 0
  %445 = insertelement <3 x half> undef, half %444, i64 0
  %446 = extractelement <3 x half> %436, i64 1
  %447 = fmul fast half %446, %384
  %448 = fpext half %447 to float
  %449 = fadd fast float %448, 5.000000e-01
  %450 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %449, i64 0
  %451 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %450, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %452 = extractvalue { <4 x half>, i8 } %451, 0
  %453 = extractelement <4 x half> %452, i64 0
  %454 = insertelement <3 x half> %445, half %453, i64 1
  %455 = extractelement <3 x half> %436, i64 2
  %456 = fmul fast half %455, %384
  %457 = fpext half %456 to float
  %458 = fadd fast float %457, 5.000000e-01
  %459 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %458, i64 0
  %460 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %3, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %459, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %461 = extractvalue { <4 x half>, i8 } %460, 0
  %462 = extractelement <4 x half> %461, i64 0
  %463 = insertelement <3 x half> %454, half %462, i64 2
  %464 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %436, <3 x half> %463, <3 x half> %412) #14
  %465 = fdiv fast <3 x half> %464, %230
  %466 = select fast <3 x i1> %416, <3 x half> zeroinitializer, <3 x half> %465
  %467 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 15, i32 1
  %468 = load float, ptr addrspace(1) %467, align 4, !tbaa !120, !alias.scope !98, !noalias !99
  %469 = fptrunc float %468 to half
  %470 = fptrunc float %289 to half
  %471 = insertelement <3 x half> poison, half %469, i64 0
  %472 = shufflevector <3 x half> %471, <3 x half> poison, <3 x i32> zeroinitializer
  %473 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %466, <3 x half> splat (half 0xH3C00), <3 x half> %472) #14
  %474 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %473, <3 x half> splat (half 0xH3C00)) #14
  %475 = insertelement <3 x half> poison, half %470, i64 0
  %476 = shufflevector <3 x half> %475, <3 x half> poison, <3 x i32> zeroinitializer
  %477 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %473, <3 x half> %474, <3 x half> %476) #14
  %478 = fmul fast <3 x half> %477, %230
  %479 = insertelement <3 x half> poison, half %96, i64 0
  %480 = shufflevector <3 x half> %479, <3 x half> poison, <3 x i32> zeroinitializer
  %481 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %429, <3 x half> %478, <3 x half> %480) #14
  br label %482

482:                                              ; preds = %370, %324
  %483 = phi half [ %469, %370 ], [ %345, %324 ]
  %484 = phi half [ %420, %370 ], [ %357, %324 ]
  %485 = phi <3 x half> [ %481, %370 ], [ %369, %324 ]
  %486 = tail call fast half @air.mix.f16(half %248, half %245, half %484) #14
  %487 = tail call fast half @air.mix.f16(half %248, half %245, half %483) #14
  %488 = tail call fast half @air.mix.f16(half %486, half %487, half %96) #14
  %489 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 13, i32 3
  %490 = load float, ptr addrspace(1) %489, align 4, !tbaa !125, !alias.scope !98, !noalias !99
  %491 = tail call fast float @air.fast_fabs.f32(float %490) #14
  %492 = fcmp fast olt float %491, 0x3EE4F8B580000000
  br i1 %492, label %500, label %493

493:                                              ; preds = %482
  %494 = fcmp fast ogt float %490, 0.000000e+00
  %495 = fptrunc float %490 to half
  br i1 %494, label %496, label %498

496:                                              ; preds = %493
  %497 = tail call fast fastcc <3 x half> @_Z13ShadowsFilterDv3_DhDhDh(<3 x half> noundef %485, half noundef %488, half noundef %495) #17
  br label %500

498:                                              ; preds = %493
  %499 = tail call fast fastcc <3 x half> @_Z21ShadowsNegativeFilterDv3_DhDhDh(<3 x half> noundef %485, half noundef %488, half noundef %495) #17
  br label %500

500:                                              ; preds = %498, %496, %482
  %501 = phi <3 x half> [ %485, %482 ], [ %497, %496 ], [ %499, %498 ]
  %502 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 13, i32 1
  %503 = load float, ptr addrspace(1) %502, align 4, !tbaa !126, !alias.scope !98, !noalias !99
  %504 = tail call fast float @air.fast_fabs.f32(float %503) #14
  %505 = fcmp fast olt float %504, 0x3EE4F8B580000000
  br i1 %505, label %509, label %506

506:                                              ; preds = %500
  %507 = fptrunc float %503 to half
  %508 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %501, half noundef %507) #17
  br label %509

509:                                              ; preds = %506, %500
  %510 = phi <3 x half> [ %501, %500 ], [ %508, %506 ]
  %511 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 13, i32 0
  %512 = load float, ptr addrspace(1) %511, align 4, !tbaa !127, !alias.scope !98, !noalias !99
  %513 = tail call fast float @air.fast_fabs.f32(float %512) #14
  %514 = fcmp fast olt float %513, 0x3EE4F8B580000000
  br i1 %514, label %518, label %515

515:                                              ; preds = %509
  %516 = fptrunc float %512 to half
  %517 = tail call fast fastcc <3 x half> @_Z11whitesCurveDv3_DhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEEDhDh(<3 x half> noundef %510, ptr addrspace(1) %4, half noundef %516, half noundef 0xH0000) #18, !alias.scope !82, !noalias !83
  br label %518

518:                                              ; preds = %515, %509
  %519 = phi <3 x half> [ %510, %509 ], [ %517, %515 ]
  %520 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 13, i32 11
  %521 = load float, ptr addrspace(1) %520, align 4, !tbaa !128, !alias.scope !98, !noalias !99
  %522 = fadd fast float %521, -1.000000e+00
  %523 = tail call fast float @air.fast_fabs.f32(float %522) #14
  %524 = fcmp fast olt float %523, 0x3EE4F8B580000000
  br i1 %524, label %528, label %525

525:                                              ; preds = %518
  %526 = fptrunc float %521 to half
  %527 = tail call fast fastcc <3 x half> @_Z10airyFilterDv3_DhDh(<3 x half> noundef %519, half noundef %526) #17
  br label %528

528:                                              ; preds = %525, %518
  %529 = phi <3 x half> [ %519, %518 ], [ %527, %525 ]
  %530 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 13, i32 7
  %531 = load float, ptr addrspace(1) %530, align 4, !tbaa !129, !alias.scope !98, !noalias !99
  %532 = tail call fast float @air.fast_fabs.f32(float %531) #14
  %533 = fcmp fast olt float %532, 0x3EE4F8B580000000
  br i1 %533, label %554, label %534

534:                                              ; preds = %528
  %535 = fptrunc float %531 to half
  %536 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %529, <3 x half> zeroinitializer) #14
  %537 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %529, <3 x half> splat (half 0xH3C00)) #14
  %538 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %529) #14
  %539 = extractelement <3 x half> %538, i64 0
  %540 = extractelement <3 x half> %538, i64 1
  %541 = extractelement <3 x half> %538, i64 2
  %542 = tail call fast half @air.fmax3.f16(half %539, half %540, half %541) #14
  %543 = tail call fast half @air.pow.f16(half %542, half 0xH3800) #14
  %544 = fsub fast half 0xH3C00, %543
  %545 = fmul fast half %544, %535
  %546 = fadd fast half %545, 0xH3C00
  %547 = insertelement <3 x half> poison, half %546, i64 0
  %548 = shufflevector <3 x half> %547, <3 x half> poison, <3 x i32> zeroinitializer
  %549 = fmul fast <3 x half> %548, %538
  %550 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %549) #14
  %551 = fadd fast <3 x half> %536, splat (half 0xHBC00)
  %552 = fadd fast <3 x half> %551, %537
  %553 = fadd fast <3 x half> %552, %550
  br label %554

554:                                              ; preds = %534, %528
  %555 = phi <3 x half> [ %529, %528 ], [ %553, %534 ]
  %556 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 13, i32 8
  %557 = load float, ptr addrspace(1) %556, align 4, !tbaa !130, !alias.scope !98, !noalias !99
  %558 = fadd fast float %557, -1.000000e+00
  %559 = tail call fast float @air.fast_fabs.f32(float %558) #14
  %560 = fcmp fast olt float %559, 0x3EE4F8B580000000
  br i1 %560, label %564, label %561

561:                                              ; preds = %554
  %562 = fptrunc float %557 to half
  %563 = tail call fast fastcc <3 x half> @_Z15smoothSatFilterDv3_DhDh(<3 x half> noundef %555, half noundef %562) #17
  br label %564

564:                                              ; preds = %561, %554
  %565 = phi <3 x half> [ %555, %554 ], [ %563, %561 ]
  %566 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 13, i32 5
  %567 = load float, ptr addrspace(1) %566, align 4, !tbaa !131, !alias.scope !98, !noalias !99
  %568 = tail call fast float @air.fast_fabs.f32(float %567) #14
  %569 = fcmp fast olt float %568, 0x3EE4F8B580000000
  br i1 %569, label %624, label %570

570:                                              ; preds = %564
  %571 = fptrunc float %567 to half
  %572 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %565, <3 x half> zeroinitializer) #14
  %573 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %565, <3 x half> splat (half 0xH3C00)) #14
  %574 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %565) #14
  %575 = tail call fast half @air.dot.v3f16(<3 x half> %574, <3 x half> splat (half 0xH3555)) #14
  %576 = tail call fast half @air.sqrt.f16(half %575) #14
  %577 = fpext half %576 to float
  %578 = fsub fast float 1.000000e+00, %577
  %579 = fmul fast float %578, %577
  %580 = fptrunc float %579 to half
  %581 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %574) #14
  %582 = tail call fast half @air.sqrt.f16(half %488) #14
  %583 = fmul fast half %580, %571
  %584 = fmul fast half %583, 0xH4000
  %585 = fmul fast half %583, 0xHC000
  %586 = fmul fast half %585, %582
  %587 = fpext half %584 to float
  %588 = fmul fast float %587, 0x3FD322D0E0000000
  %589 = fptrunc float %588 to half
  %590 = insertelement <3 x half> poison, half %589, i64 0
  %591 = fmul fast <3 x half> %590, %581
  %592 = shufflevector <3 x half> %591, <3 x half> poison, <3 x i32> zeroinitializer
  %593 = shufflevector <3 x half> %581, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %594 = fmul fast float %587, 0x3FE2C8B440000000
  %595 = fptrunc float %594 to half
  %596 = insertelement <3 x half> poison, half %595, i64 0
  %597 = shufflevector <3 x half> %596, <3 x half> poison, <3 x i32> zeroinitializer
  %598 = fmul fast <3 x half> %597, %593
  %599 = shufflevector <3 x half> %581, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %600 = fmul fast float %587, 0x3FBD2F1AA0000000
  %601 = fptrunc float %600 to half
  %602 = insertelement <3 x half> poison, half %601, i64 0
  %603 = shufflevector <3 x half> %602, <3 x half> poison, <3 x i32> zeroinitializer
  %604 = fmul fast <3 x half> %603, %599
  %605 = insertelement <3 x half> poison, half %586, i64 0
  %606 = shufflevector <3 x half> %605, <3 x half> poison, <3 x i32> zeroinitializer
  %607 = fadd fast <3 x half> %606, %581
  %608 = fadd fast <3 x half> %607, %598
  %609 = fadd fast <3 x half> %608, %592
  %610 = fadd fast <3 x half> %609, %604
  %611 = insertelement <3 x half> poison, half %582, i64 0
  %612 = shufflevector <3 x half> %611, <3 x half> poison, <3 x i32> zeroinitializer
  %613 = insertelement <3 x half> poison, half %585, i64 0
  %614 = shufflevector <3 x half> %613, <3 x half> poison, <3 x i32> zeroinitializer
  %615 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %581, <3 x half> %612, <3 x half> %614) #14
  %616 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %615, <3 x half> %610, <3 x half> splat (half 0xH3A66)) #14
  %617 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %616, <3 x half> zeroinitializer) #14
  %618 = fmul fast <3 x half> %617, %617
  %619 = fadd fast <3 x half> %572, splat (half 0xHBC00)
  %620 = fadd fast <3 x half> %619, %573
  %621 = fadd fast <3 x half> %620, %618
  %622 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %621, <3 x half> %565) #14
  %623 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %621, <3 x half> %622, <3 x half> zeroinitializer) #14
  br label %624

624:                                              ; preds = %570, %564
  %625 = phi <3 x half> [ %565, %564 ], [ %623, %570 ]
  %626 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 13, i32 4
  %627 = load float, ptr addrspace(1) %626, align 4, !tbaa !132, !alias.scope !98, !noalias !99
  %628 = tail call fast float @air.fast_fabs.f32(float %627) #14
  %629 = fcmp fast olt float %628, 0x3EE4F8B580000000
  br i1 %629, label %656, label %630

630:                                              ; preds = %624
  %631 = fptrunc float %627 to half
  %632 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %625, <3 x half> zeroinitializer) #14
  %633 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %625, <3 x half> splat (half 0xH3C00)) #14
  %634 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %625) #14
  %635 = tail call fast half @air.dot.v3f16(<3 x half> %634, <3 x half> splat (half 0xH3555)) #14
  %636 = fpext half %488 to float
  %637 = fmul fast float %636, 0x400B333340000000
  %638 = fadd fast float %637, 0xBFF3340000000000
  %639 = fptrunc float %638 to half
  %640 = fpext half %639 to float
  %641 = fadd fast float %640, 0x3FF0FDBF40000000
  %642 = fmul fast float %641, 0x3FDA374BC0000000
  %643 = fptrunc float %642 to half
  %644 = fsub fast half %643, %635
  %645 = fmul fast half %631, 0xH4000
  %646 = fmul fast half %645, %644
  %647 = fadd fast half %646, 0xH3C00
  %648 = tail call fast half @air.fmax.f16(half %647, half 0xH0000) #14
  %649 = insertelement <3 x half> poison, half %648, i64 0
  %650 = shufflevector <3 x half> %649, <3 x half> poison, <3 x i32> zeroinitializer
  %651 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %634, <3 x half> %650) #14
  %652 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %651, <3 x half> zeroinitializer) #14
  %653 = fadd fast <3 x half> %632, splat (half 0xHBC00)
  %654 = fadd fast <3 x half> %653, %633
  %655 = fadd fast <3 x half> %654, %652
  br label %656

656:                                              ; preds = %630, %624
  %657 = phi <3 x half> [ %625, %624 ], [ %655, %630 ]
  %658 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 13, i32 9
  %659 = load float, ptr addrspace(1) %658, align 4, !tbaa !133, !alias.scope !98, !noalias !99
  %660 = fmul fast float %659, 5.000000e-01
  %661 = fcmp fast ogt float %660, 0.000000e+00
  %662 = tail call fast float @air.fast_fabs.f32(float %660) #14
  %663 = xor i1 %661, true
  %664 = fcmp fast olt float %662, 0x3EE4F8B580000000
  %665 = select i1 %663, i1 true, i1 %664
  br i1 %665, label %669, label %666

666:                                              ; preds = %656
  %667 = fptrunc float %660 to half
  %668 = tail call fast fastcc <3 x half> @_Z13ShadowsFilterDv3_DhDhDh(<3 x half> noundef %657, half noundef %488, half noundef %667) #17
  br label %669

669:                                              ; preds = %666, %656
  %670 = phi <3 x half> [ %668, %666 ], [ %657, %656 ]
  br i1 %664, label %681, label %671

671:                                              ; preds = %669
  %672 = fmul fast float %659, 7.500000e-01
  br i1 %661, label %673, label %676

673:                                              ; preds = %671
  %674 = fptrunc float %672 to half
  %675 = tail call fast fastcc <3 x half> @_Z13lightenFilterDv3_DhDhDh(<3 x half> noundef %670, half noundef %488, half noundef %674) #17
  br label %681

676:                                              ; preds = %671
  %677 = fsub fast float 1.000000e+00, %672
  %678 = fptrunc float %677 to half
  %679 = tail call fast half @air.fabs.f16(half %678) #14
  %680 = tail call fast fastcc <3 x half> @_Z21negativeLightenFilterDv3_DhDhDh(<3 x half> noundef %670, half noundef %488, half noundef %679) #17
  br label %681

681:                                              ; preds = %676, %673, %669
  %682 = phi <3 x half> [ %670, %669 ], [ %675, %673 ], [ %680, %676 ]
  %683 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 13, i32 10
  %684 = load float, ptr addrspace(1) %683, align 4, !tbaa !134, !alias.scope !98, !noalias !99
  %685 = tail call fast float @air.fast_fabs.f32(float %684) #14
  %686 = fcmp fast olt float %685, 0x3EE4F8B580000000
  br i1 %686, label %779, label %687

687:                                              ; preds = %681
  %688 = fptrunc float %684 to half
  %689 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %682) #14
  %690 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %689) #14
  %691 = shufflevector <3 x float> %690, <3 x float> poison, <3 x i32> zeroinitializer
  %692 = fmul fast <3 x float> %691, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %693 = shufflevector <3 x float> %690, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %694 = fmul fast <3 x float> %693, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %695 = fadd fast <3 x float> %692, %694
  %696 = shufflevector <3 x float> %690, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %697 = fmul fast <3 x float> %696, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %698 = fadd fast <3 x float> %695, %697
  %699 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %698) #14
  %700 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %698) #14
  %701 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %700, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %702 = fmul fast <3 x float> %701, %699
  %703 = shufflevector <3 x float> %702, <3 x float> poison, <3 x i32> zeroinitializer
  %704 = fmul fast <3 x float> %703, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %705 = shufflevector <3 x float> %702, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %706 = fmul fast <3 x float> %705, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %707 = fadd fast <3 x float> %704, %706
  %708 = shufflevector <3 x float> %702, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %709 = fmul fast <3 x float> %708, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %710 = fadd fast <3 x float> %707, %709
  %711 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %710) #14
  %712 = extractelement <3 x half> %711, i64 2
  %713 = fcmp fast une half %712, 0xH0000
  %714 = extractelement <3 x half> %711, i64 1
  %715 = fcmp fast une half %714, 0xH0000
  %716 = select i1 %713, i1 true, i1 %715
  br i1 %716, label %717, label %_Z16underGrassFilterDv3_DhDhDh.exit.i

717:                                              ; preds = %687
  %718 = tail call fast half @air.atan2.f16(half %712, half %714) #14
  br label %_Z16underGrassFilterDv3_DhDhDh.exit.i

_Z16underGrassFilterDv3_DhDhDh.exit.i:            ; preds = %717, %687
  %719 = phi fast half [ %718, %717 ], [ 0xH0000, %687 ]
  %720 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %682, <3 x half> splat (half 0xH3C00)) #14
  %721 = fadd fast <3 x half> %720, splat (half 0xHBC00)
  %722 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %682, <3 x half> zeroinitializer) #14
  %723 = fmul fast half %688, 0xH3266
  %724 = fadd fast half %719, %723
  %725 = fpext half %719 to float
  %726 = fadd fast float %725, 0xBFFBA55FE0000000
  %727 = fmul fast float %726, %726
  %728 = fmul fast float %727, 0xC020539780000000
  %729 = tail call fast float @air.fast_exp.f32(float %728) #14
  %730 = fptrunc float %729 to half
  %731 = tail call fast half @air.mix.f16(half %719, half %724, half %730) #14
  %732 = fmul fast half %714, %714
  %733 = fmul fast half %712, %712
  %734 = fadd fast half %732, %733
  %735 = tail call fast half @air.sqrt.f16(half %734) #14
  %736 = fpext half %735 to float
  %737 = tail call fast half @air.fabs.f16(half %688) #14
  %738 = extractelement <3 x half> %711, i64 0
  %739 = fmul fast half %737, %738
  %740 = tail call fast half @air.fmax.f16(half %739, half 0xH3800) #14
  %741 = fmul fast half %740, 0xH2A66
  %742 = fpext half %741 to float
  %743 = fsub fast float 1.000000e+00, %742
  %744 = fmul fast float %743, %736
  %745 = fptrunc float %744 to half
  %746 = tail call fast half @air.cos.f16(half %731) #14
  %747 = fmul fast half %746, %745
  %748 = insertelement <3 x half> %711, half %747, i64 1
  %749 = tail call fast half @air.sin.f16(half %731) #14
  %750 = fmul fast half %749, %745
  %751 = insertelement <3 x half> %748, half %750, i64 2
  %752 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %751) #14
  %753 = shufflevector <3 x float> %752, <3 x float> poison, <3 x i32> zeroinitializer
  %754 = shufflevector <3 x float> %752, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %755 = fmul fast <3 x float> %754, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %756 = fadd fast <3 x float> %755, %753
  %757 = shufflevector <3 x float> %752, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %758 = fmul fast <3 x float> %757, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %759 = fadd fast <3 x float> %756, %758
  %760 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %759) #14
  %761 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %759) #14
  %762 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %761, <3 x float> splat (float 0x40029ACA60000000)) #14
  %763 = fmul fast <3 x float> %762, %760
  %764 = shufflevector <3 x float> %763, <3 x float> poison, <3 x i32> zeroinitializer
  %765 = fmul fast <3 x float> %764, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %766 = shufflevector <3 x float> %763, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %767 = fmul fast <3 x float> %766, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %768 = fadd fast <3 x float> %765, %767
  %769 = shufflevector <3 x float> %763, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %770 = fmul fast <3 x float> %769, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %771 = fadd fast <3 x float> %768, %770
  %772 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %771) #14
  %773 = insertelement <3 x half> poison, half %96, i64 0
  %774 = shufflevector <3 x half> %773, <3 x half> poison, <3 x i32> zeroinitializer
  %775 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %772, <3 x half> %689, <3 x half> %774) #14
  %776 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %775) #14
  %777 = fadd fast <3 x half> %721, %722
  %778 = fadd fast <3 x half> %777, %776
  br label %779

779:                                              ; preds = %_Z16underGrassFilterDv3_DhDhDh.exit.i, %681
  %780 = phi <3 x half> [ %682, %681 ], [ %778, %_Z16underGrassFilterDv3_DhDhDh.exit.i ]
  %781 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 13, i32 2
  %782 = load float, ptr addrspace(1) %781, align 4, !tbaa !135, !alias.scope !98, !noalias !99
  %783 = fmul fast float %782, 5.000000e-01
  %784 = fadd fast float %783, 1.000000e+00
  %785 = tail call fast float @air.fast_fabs.f32(float %783) #14
  %786 = fcmp fast olt float %785, 0x3EE4F8B580000000
  br i1 %786, label %_Z19renderBGAdjustmentsDv3_DhDhDhDhRU9MTLdevice15SSRBGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit, label %787

787:                                              ; preds = %779
  %788 = fcmp fast ogt float %784, 1.000000e+00
  br i1 %788, label %789, label %793

789:                                              ; preds = %787
  %790 = fadd fast float %782, 1.000000e+00
  %791 = fptrunc float %790 to half
  %792 = tail call fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %780, half noundef %791, half noundef 0xH4200) #17
  br label %_Z19renderBGAdjustmentsDv3_DhDhDhDhRU9MTLdevice15SSRBGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit

793:                                              ; preds = %787
  %794 = fptrunc float %784 to half
  %795 = tail call fast fastcc <3 x half> @_Z15smoothSatFilterDv3_DhDh(<3 x half> noundef %780, half noundef %794) #17
  br label %_Z19renderBGAdjustmentsDv3_DhDhDhDhRU9MTLdevice15SSRBGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit

_Z19renderBGAdjustmentsDv3_DhDhDhDhRU9MTLdevice15SSRBGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit: ; preds = %793, %789, %779
  %796 = phi <3 x half> [ %792, %789 ], [ %795, %793 ], [ %780, %779 ]
  %797 = fpext half %96 to float
  %798 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 0
  %799 = load float, ptr addrspace(1) %798, align 4, !tbaa !136, !alias.scope !98, !noalias !99
  %800 = fsub fast float 1.000000e+00, %799
  %801 = fmul fast float %800, %797
  %802 = fptrunc float %801 to half
  %803 = insertelement <3 x half> poison, half %802, i64 0
  %804 = shufflevector <3 x half> %803, <3 x half> poison, <3 x i32> zeroinitializer
  %805 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %796, <3 x half> %485, <3 x half> %804) #14
  %806 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 4
  %807 = load float, ptr addrspace(1) %806, align 4, !tbaa !137, !alias.scope !98, !noalias !99
  %808 = tail call fast float @air.fast_fabs.f32(float %807) #14
  %809 = fcmp fast olt float %808, 0x3EE4F8B580000000
  br i1 %809, label %813, label %810

810:                                              ; preds = %_Z19renderBGAdjustmentsDv3_DhDhDhDhRU9MTLdevice15SSRBGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit
  %811 = fptrunc float %807 to half
  %812 = tail call fast fastcc <3 x half> @_Z11whitesCurveDv3_DhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEEDhDh(<3 x half> noundef %805, ptr addrspace(1) %4, half noundef %811, half noundef 0xH3C00) #18, !alias.scope !82, !noalias !83
  br label %813

813:                                              ; preds = %810, %_Z19renderBGAdjustmentsDv3_DhDhDhDhRU9MTLdevice15SSRBGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit
  %814 = phi <3 x half> [ %805, %_Z19renderBGAdjustmentsDv3_DhDhDhDhRU9MTLdevice15SSRBGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit ], [ %812, %810 ]
  %815 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 6
  %816 = load float, ptr addrspace(1) %815, align 4, !tbaa !138, !alias.scope !98, !noalias !99
  %817 = tail call fast float @air.fast_fabs.f32(float %816) #14
  %818 = fcmp fast olt float %817, 0x3EE4F8B580000000
  br i1 %818, label %826, label %819

819:                                              ; preds = %813
  %820 = fcmp fast ogt float %816, 0.000000e+00
  %821 = fptrunc float %816 to half
  br i1 %820, label %822, label %824

822:                                              ; preds = %819
  %823 = tail call fast fastcc <3 x half> @_Z13ShadowsFilterDv3_DhDhDh(<3 x half> noundef %814, half noundef %488, half noundef %821) #17
  br label %826

824:                                              ; preds = %819
  %825 = tail call fast fastcc <3 x half> @_Z21ShadowsNegativeFilterDv3_DhDhDh(<3 x half> noundef %814, half noundef %488, half noundef %821) #17
  br label %826

826:                                              ; preds = %824, %822, %813
  %827 = phi <3 x half> [ %814, %813 ], [ %823, %822 ], [ %825, %824 ]
  %828 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 15
  %829 = load float, ptr addrspace(1) %828, align 4, !tbaa !139, !alias.scope !98, !noalias !99
  %830 = tail call fast float @air.fast_fabs.f32(float %829) #14
  %831 = fcmp fast olt float %830, 0x3EE4F8B580000000
  br i1 %831, label %876, label %832

832:                                              ; preds = %826
  %833 = fptrunc float %829 to half
  %834 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %827) #14
  %835 = tail call fast half @air.dot.v3f16(<3 x half> %834, <3 x half> <half 0xH34CD, half 0xH3800, half 0xH3266>) #14
  %836 = fcmp fast ogt half %835, 0xH0000
  br i1 %836, label %837, label %_Z19tonalContrastFilterDv3_DhDhDh.exit.i

837:                                              ; preds = %832
  %838 = tail call fast half @air.pow.f16(half %835, half 0xH4400) #14
  %839 = fpext half %838 to float
  %840 = fmul fast float %839, 0x3FFA182AA0000000
  %841 = tail call fast half @air.pow.f16(half %835, half 0xH4200) #14
  %842 = fpext half %841 to float
  %843 = fmul fast float %842, 0xC00D923A20000000
  %844 = tail call fast half @air.pow.f16(half %835, half 0xH4000) #14
  %845 = fpext half %844 to float
  %846 = fmul fast float %845, 0x4005A02760000000
  %847 = fpext half %835 to float
  %848 = fmul fast float %847, 0x3FD765FD80000000
  %849 = fadd fast float %840, %848
  %850 = fadd fast float %849, %843
  %851 = fadd fast float %850, %846
  %852 = fptrunc float %851 to half
  %853 = insertelement <3 x half> poison, half %835, i64 0
  %854 = shufflevector <3 x half> %853, <3 x half> poison, <3 x i32> zeroinitializer
  %855 = insertelement <3 x half> poison, half %852, i64 0
  %856 = shufflevector <3 x half> %855, <3 x half> poison, <3 x i32> zeroinitializer
  %857 = fmul fast <3 x half> %856, %834
  %858 = fdiv fast <3 x half> %857, %854
  br label %_Z19tonalContrastFilterDv3_DhDhDh.exit.i

_Z19tonalContrastFilterDv3_DhDhDh.exit.i:         ; preds = %837, %832
  %859 = phi fast <3 x half> [ %858, %837 ], [ zeroinitializer, %832 ]
  %860 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %827, <3 x half> splat (half 0xH3C00)) #14
  %861 = fadd fast <3 x half> %860, splat (half 0xHBC00)
  %862 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %827, <3 x half> zeroinitializer) #14
  %863 = insertelement <3 x half> poison, half %833, i64 0
  %864 = shufflevector <3 x half> %863, <3 x half> poison, <3 x i32> zeroinitializer
  %865 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %834, <3 x half> %859, <3 x half> %864) #14
  %866 = fpext half %95 to float
  %867 = fadd fast float %866, 1.000000e+00
  %868 = fmul fast float %867, 5.000000e-01
  %869 = fptrunc float %868 to half
  %870 = insertelement <3 x half> poison, half %869, i64 0
  %871 = shufflevector <3 x half> %870, <3 x half> poison, <3 x i32> zeroinitializer
  %872 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %834, <3 x half> %865, <3 x half> %871) #14
  %873 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %872) #14
  %874 = fadd fast <3 x half> %861, %862
  %875 = fadd fast <3 x half> %874, %873
  br label %876

876:                                              ; preds = %_Z19tonalContrastFilterDv3_DhDhDh.exit.i, %826
  %877 = phi <3 x half> [ %827, %826 ], [ %875, %_Z19tonalContrastFilterDv3_DhDhDh.exit.i ]
  %878 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 7
  %879 = load float, ptr addrspace(1) %878, align 4, !tbaa !140, !alias.scope !98, !noalias !99
  %880 = tail call fast float @air.fast_fabs.f32(float %879) #14
  %881 = fcmp fast olt float %880, 0x3EE4F8B580000000
  br i1 %881, label %885, label %882

882:                                              ; preds = %876
  %883 = fptrunc float %879 to half
  %884 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %877, half noundef %883) #17
  br label %885

885:                                              ; preds = %882, %876
  %886 = phi <3 x half> [ %877, %876 ], [ %884, %882 ]
  %887 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 11
  %888 = load float, ptr addrspace(1) %887, align 4, !tbaa !141, !alias.scope !98, !noalias !99
  %889 = tail call fast float @air.fast_fabs.f32(float %888) #14
  %890 = fcmp fast olt float %889, 0x3EE4F8B580000000
  br i1 %890, label %899, label %891

891:                                              ; preds = %885
  %892 = fcmp fast ogt float %888, 0.000000e+00
  %893 = fadd fast float %888, 1.000000e+00
  %894 = fptrunc float %893 to half
  br i1 %892, label %895, label %897

895:                                              ; preds = %891
  %896 = tail call fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %886, half noundef %894, half noundef 0xH4200) #17
  br label %899

897:                                              ; preds = %891
  %898 = tail call fast fastcc <3 x half> @_Z15smoothSatFilterDv3_DhDh(<3 x half> noundef %886, half noundef %894) #17
  br label %899

899:                                              ; preds = %897, %895, %885
  %900 = phi <3 x half> [ %886, %885 ], [ %896, %895 ], [ %898, %897 ]
  %901 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 5
  %902 = load float, ptr addrspace(1) %901, align 4, !tbaa !142, !alias.scope !98, !noalias !99
  %903 = fadd fast float %902, -1.000000e+00
  %904 = tail call fast float @air.fast_fabs.f32(float %903) #14
  %905 = fcmp fast olt float %904, 0x3EE4F8B580000000
  br i1 %905, label %909, label %906

906:                                              ; preds = %899
  %907 = fptrunc float %902 to half
  %908 = tail call fast fastcc <3 x half> @_Z10airyFilterDv3_DhDh(<3 x half> noundef %900, half noundef %907) #17
  br label %909

909:                                              ; preds = %906, %899
  %910 = phi <3 x half> [ %900, %899 ], [ %908, %906 ]
  %911 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 2
  %912 = load float, ptr addrspace(1) %911, align 4, !tbaa !143, !alias.scope !98, !noalias !99
  %913 = tail call fast float @air.fast_fabs.f32(float %912) #14
  %914 = fcmp fast olt float %913, 0x3EE4F8B580000000
  br i1 %914, label %935, label %915

915:                                              ; preds = %909
  %916 = fptrunc float %912 to half
  %917 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %910, <3 x half> zeroinitializer) #14
  %918 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %910, <3 x half> splat (half 0xH3C00)) #14
  %919 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %910) #14
  %920 = extractelement <3 x half> %919, i64 0
  %921 = extractelement <3 x half> %919, i64 1
  %922 = extractelement <3 x half> %919, i64 2
  %923 = tail call fast half @air.fmax3.f16(half %920, half %921, half %922) #14
  %924 = tail call fast half @air.pow.f16(half %923, half 0xH3800) #14
  %925 = fsub fast half 0xH3C00, %924
  %926 = fmul fast half %925, %916
  %927 = fadd fast half %926, 0xH3C00
  %928 = insertelement <3 x half> poison, half %927, i64 0
  %929 = shufflevector <3 x half> %928, <3 x half> poison, <3 x i32> zeroinitializer
  %930 = fmul fast <3 x half> %929, %919
  %931 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %930) #14
  %932 = fadd fast <3 x half> %917, splat (half 0xHBC00)
  %933 = fadd fast <3 x half> %932, %918
  %934 = fadd fast <3 x half> %933, %931
  br label %935

935:                                              ; preds = %915, %909
  %936 = phi <3 x half> [ %910, %909 ], [ %934, %915 ]
  %937 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 14
  %938 = load float, ptr addrspace(1) %937, align 4, !tbaa !144, !alias.scope !98, !noalias !99
  %939 = tail call fast float @air.fast_fabs.f32(float %938) #14
  %940 = fcmp fast olt float %939, 0x3EE4F8B580000000
  br i1 %940, label %1035, label %941

941:                                              ; preds = %935
  %942 = fptrunc float %938 to half
  %943 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %936) #14
  %944 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %943) #14
  %945 = shufflevector <3 x float> %944, <3 x float> poison, <3 x i32> zeroinitializer
  %946 = fmul fast <3 x float> %945, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %947 = shufflevector <3 x float> %944, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %948 = fmul fast <3 x float> %947, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %949 = fadd fast <3 x float> %946, %948
  %950 = shufflevector <3 x float> %944, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %951 = fmul fast <3 x float> %950, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %952 = fadd fast <3 x float> %949, %951
  %953 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %952) #14
  %954 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %952) #14
  %955 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %954, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %956 = fmul fast <3 x float> %955, %953
  %957 = shufflevector <3 x float> %956, <3 x float> poison, <3 x i32> zeroinitializer
  %958 = fmul fast <3 x float> %957, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %959 = shufflevector <3 x float> %956, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %960 = fmul fast <3 x float> %959, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %961 = fadd fast <3 x float> %958, %960
  %962 = shufflevector <3 x float> %956, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %963 = fmul fast <3 x float> %962, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %964 = fadd fast <3 x float> %961, %963
  %965 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %964) #14
  %966 = extractelement <3 x half> %965, i64 2
  %967 = fcmp fast une half %966, 0xH0000
  %968 = extractelement <3 x half> %965, i64 1
  %969 = fcmp fast une half %968, 0xH0000
  %970 = select i1 %967, i1 true, i1 %969
  br i1 %970, label %971, label %_Z15underToneFilterDv3_DhDhDh.exit.i

971:                                              ; preds = %941
  %972 = tail call fast half @air.atan2.f16(half %966, half %968) #14
  br label %_Z15underToneFilterDv3_DhDhDh.exit.i

_Z15underToneFilterDv3_DhDhDh.exit.i:             ; preds = %971, %941
  %973 = phi fast half [ %972, %971 ], [ 0xH0000, %941 ]
  %974 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %936, <3 x half> splat (half 0xH3C00)) #14
  %975 = fadd fast <3 x half> %974, splat (half 0xHBC00)
  %976 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %936, <3 x half> zeroinitializer) #14
  %977 = fpext half %973 to float
  %978 = fpext half %942 to float
  %979 = fmul fast float %978, 0x3FC99999A0000000
  %980 = fadd fast float %979, %977
  %981 = fptrunc float %980 to half
  %982 = fadd fast float %977, 0xBFF79FF020000000
  %983 = fmul fast float %982, %982
  %984 = fmul fast float %983, 0xC000539780000000
  %985 = tail call fast float @air.fast_exp.f32(float %984) #14
  %986 = fptrunc float %985 to half
  %987 = tail call fast half @air.mix.f16(half %973, half %981, half %986) #14
  %988 = fmul fast half %968, %968
  %989 = fmul fast half %966, %966
  %990 = fadd fast half %988, %989
  %991 = tail call fast half @air.sqrt.f16(half %990) #14
  %992 = fpext half %991 to float
  %993 = tail call fast half @air.fabs.f16(half %942) #14
  %994 = extractelement <3 x half> %965, i64 0
  %995 = fmul fast half %993, %994
  %996 = tail call fast half @air.fmax.f16(half %995, half 0xH3800) #14
  %997 = fpext half %996 to float
  %998 = fmul fast float %997, 0x3FC3333340000000
  %999 = fsub fast float 1.000000e+00, %998
  %1000 = fmul fast float %999, %992
  %1001 = fptrunc float %1000 to half
  %1002 = tail call fast half @air.cos.f16(half %987) #14
  %1003 = fmul fast half %1002, %1001
  %1004 = insertelement <3 x half> %965, half %1003, i64 1
  %1005 = tail call fast half @air.sin.f16(half %987) #14
  %1006 = fmul fast half %1005, %1001
  %1007 = insertelement <3 x half> %1004, half %1006, i64 2
  %1008 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %1007) #14
  %1009 = shufflevector <3 x float> %1008, <3 x float> poison, <3 x i32> zeroinitializer
  %1010 = shufflevector <3 x float> %1008, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1011 = fmul fast <3 x float> %1010, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %1012 = fadd fast <3 x float> %1011, %1009
  %1013 = shufflevector <3 x float> %1008, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1014 = fmul fast <3 x float> %1013, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %1015 = fadd fast <3 x float> %1012, %1014
  %1016 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %1015) #14
  %1017 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %1015) #14
  %1018 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %1017, <3 x float> splat (float 0x40029ACA60000000)) #14
  %1019 = fmul fast <3 x float> %1018, %1016
  %1020 = shufflevector <3 x float> %1019, <3 x float> poison, <3 x i32> zeroinitializer
  %1021 = fmul fast <3 x float> %1020, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %1022 = shufflevector <3 x float> %1019, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1023 = fmul fast <3 x float> %1022, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %1024 = fadd fast <3 x float> %1021, %1023
  %1025 = shufflevector <3 x float> %1019, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1026 = fmul fast <3 x float> %1025, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %1027 = fadd fast <3 x float> %1024, %1026
  %1028 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %1027) #14
  %1029 = insertelement <3 x half> poison, half %95, i64 0
  %1030 = shufflevector <3 x half> %1029, <3 x half> poison, <3 x i32> zeroinitializer
  %1031 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %943, <3 x half> %1028, <3 x half> %1030) #14
  %1032 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1031) #14
  %1033 = fadd fast <3 x half> %975, %976
  %1034 = fadd fast <3 x half> %1033, %1032
  br label %1035

1035:                                             ; preds = %_Z15underToneFilterDv3_DhDhDh.exit.i, %935
  %1036 = phi <3 x half> [ %936, %935 ], [ %1034, %_Z15underToneFilterDv3_DhDhDh.exit.i ]
  %1037 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 3
  %1038 = load float, ptr addrspace(1) %1037, align 4, !tbaa !145, !alias.scope !98, !noalias !99
  %1039 = fmul fast float %1038, 5.000000e-01
  %1040 = fcmp fast ule float %1038, 0.000000e+00
  %1041 = tail call fast float @air.fast_fabs.f32(float %1039) #14
  %1042 = fcmp fast olt float %1041, 0x3EE4F8B580000000
  %1043 = select i1 %1040, i1 true, i1 %1042
  br i1 %1043, label %1051, label %1044

1044:                                             ; preds = %1035
  %1045 = fcmp fast ogt float %1039, 0.000000e+00
  %1046 = fptrunc float %1039 to half
  br i1 %1045, label %1047, label %1049

1047:                                             ; preds = %1044
  %1048 = tail call fast fastcc <3 x half> @_Z13ShadowsFilterDv3_DhDhDh(<3 x half> noundef %1036, half noundef %488, half noundef %1046) #17
  br label %1051

1049:                                             ; preds = %1044
  %1050 = tail call fast fastcc <3 x half> @_Z21ShadowsNegativeFilterDv3_DhDhDh(<3 x half> noundef %1036, half noundef %488, half noundef %1046) #17
  br label %1051

1051:                                             ; preds = %1049, %1047, %1035
  %1052 = phi <3 x half> [ %1050, %1049 ], [ %1048, %1047 ], [ %1036, %1035 ]
  br i1 %1042, label %1064, label %1053

1053:                                             ; preds = %1051
  %1054 = fcmp fast ogt float %1039, 0.000000e+00
  %1055 = fmul fast float %1038, 7.500000e-01
  br i1 %1054, label %1056, label %1059

1056:                                             ; preds = %1053
  %1057 = fptrunc float %1055 to half
  %1058 = tail call fast fastcc <3 x half> @_Z13lightenFilterDv3_DhDhDh(<3 x half> noundef %1052, half noundef %488, half noundef %1057) #17
  br label %1064

1059:                                             ; preds = %1053
  %1060 = fsub fast float 1.000000e+00, %1055
  %1061 = tail call fast float @air.fast_fabs.f32(float %1060) #14
  %1062 = fptrunc float %1061 to half
  %1063 = tail call fast fastcc <3 x half> @_Z21negativeLightenFilterDv3_DhDhDh(<3 x half> noundef %1052, half noundef %488, half noundef %1062) #17
  br label %1064

1064:                                             ; preds = %1059, %1056, %1051
  %1065 = phi <3 x half> [ %1052, %1051 ], [ %1058, %1056 ], [ %1063, %1059 ]
  %1066 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 8
  %1067 = load float, ptr addrspace(1) %1066, align 4, !tbaa !146, !alias.scope !98, !noalias !99
  %1068 = tail call fast float @air.fast_fabs.f32(float %1067) #14
  %1069 = fcmp fast olt float %1068, 0x3EE4F8B580000000
  br i1 %1069, label %_Z19renderFGAdjustmentsDv3_DhS_DhDhDhDhRU9MTLdevice15SSRFGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit, label %1070

1070:                                             ; preds = %1064
  %1071 = fcmp fast ogt float %1067, 0.000000e+00
  br i1 %1071, label %1072, label %1154

1072:                                             ; preds = %1070
  %1073 = fmul fast float %1067, 0xBFCC28F5C0000000
  %1074 = fptrunc float %1073 to half
  %1075 = fadd fast half %1074, 0xHBC00
  %1076 = tail call fast half @air.clamp.f16(half %1075, half 0xH0000, half 0xH3C00) #14
  %1077 = fmul fast half %1076, %1076
  %1078 = fmul fast half %1076, 0xH4000
  %1079 = fsub fast half 0xH4200, %1078
  %1080 = fmul fast half %1077, %1079
  %1081 = fsub fast half 0xH3C00, %1080
  %1082 = fpext half %488 to float
  %1083 = fmul fast float %1082, 0x400B333340000000
  %1084 = fpext half %1081 to float
  %1085 = fmul fast float %1084, 0x3FE99999A0000000
  %1086 = fsub fast float %1083, %1085
  %1087 = fptrunc float %1086 to half
  %1088 = fneg fast half %1074
  %1089 = tail call fast half @air.mix.f16(half 0xH0000, half %1087, half %1088) #14
  %1090 = fcmp fast ogt half %1089, 0xH0000
  %1091 = fpext half %1089 to float
  %1092 = fmul fast float %1091, 1.500000e+00
  %1093 = fadd fast float %1092, 1.000000e+00
  %1094 = fptrunc float %1093 to half
  %1095 = insertelement <3 x half> poison, half %1094, i64 0
  %1096 = shufflevector <3 x half> %1095, <3 x half> poison, <3 x i32> zeroinitializer
  %1097 = select fast i1 %1090, <3 x half> %1096, <3 x half> splat (half 0xH3C00)
  %1098 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1065) #14
  %1099 = tail call fast half @air.dot.v3f16(<3 x half> %1098, <3 x half> splat (half 0xH3555)) #14
  %1100 = tail call fast half @air.sqrt.f16(half %1099) #14
  %1101 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %1065, <3 x half> splat (half 0xH3C00)) #14
  %1102 = fadd fast <3 x half> %1101, splat (half 0xHBC00)
  %1103 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %1065, <3 x half> zeroinitializer) #14
  %1104 = tail call fast half @air.sqrt.f16(half %488) #14
  %1105 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1098, <3 x half> %1097) #14
  %1106 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %1105, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #14
  %1107 = extractelement <3 x half> %1097, i64 0
  %1108 = fmul fast half %1107, 0xHB800
  %1109 = fpext half %1100 to float
  %1110 = fsub fast float 1.000000e+00, %1109
  %1111 = fmul fast float %1110, %1109
  %1112 = fptrunc float %1111 to half
  %1113 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %1106) #14
  %1114 = fmul fast half %1108, %1112
  %1115 = fneg fast half %1104
  %1116 = fmul fast half %1114, %1115
  %1117 = fpext half %1114 to float
  %1118 = fmul fast float %1117, 0x3FD322D0E0000000
  %1119 = fptrunc float %1118 to half
  %1120 = insertelement <3 x half> poison, half %1119, i64 0
  %1121 = fmul fast <3 x half> %1120, %1113
  %1122 = shufflevector <3 x half> %1121, <3 x half> poison, <3 x i32> zeroinitializer
  %1123 = shufflevector <3 x half> %1113, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1124 = fmul fast float %1117, 0x3FE2C8B440000000
  %1125 = fptrunc float %1124 to half
  %1126 = insertelement <3 x half> poison, half %1125, i64 0
  %1127 = shufflevector <3 x half> %1126, <3 x half> poison, <3 x i32> zeroinitializer
  %1128 = fmul fast <3 x half> %1127, %1123
  %1129 = shufflevector <3 x half> %1113, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1130 = fmul fast float %1117, 0x3FBD2F1AA0000000
  %1131 = fptrunc float %1130 to half
  %1132 = insertelement <3 x half> poison, half %1131, i64 0
  %1133 = shufflevector <3 x half> %1132, <3 x half> poison, <3 x i32> zeroinitializer
  %1134 = fmul fast <3 x half> %1133, %1129
  %1135 = insertelement <3 x half> poison, half %1116, i64 0
  %1136 = shufflevector <3 x half> %1135, <3 x half> poison, <3 x i32> zeroinitializer
  %1137 = fadd fast <3 x half> %1136, %1113
  %1138 = fadd fast <3 x half> %1137, %1128
  %1139 = fadd fast <3 x half> %1138, %1122
  %1140 = fadd fast <3 x half> %1139, %1134
  %1141 = insertelement <3 x half> poison, half %1104, i64 0
  %1142 = shufflevector <3 x half> %1141, <3 x half> poison, <3 x i32> zeroinitializer
  %1143 = fneg fast half %1112
  %1144 = fmul fast half %1108, %1143
  %1145 = insertelement <3 x half> poison, half %1144, i64 0
  %1146 = shufflevector <3 x half> %1145, <3 x half> poison, <3 x i32> zeroinitializer
  %1147 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1113, <3 x half> %1142, <3 x half> %1146) #14
  %1148 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1147, <3 x half> %1140, <3 x half> splat (half 0xH3A66)) #14
  %1149 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %1148, <3 x half> zeroinitializer) #14
  %1150 = fmul fast <3 x half> %1149, %1149
  %1151 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1150) #14
  %1152 = fadd fast <3 x half> %1102, %1103
  %1153 = fadd fast <3 x half> %1152, %1151
  br label %1154

1154:                                             ; preds = %1072, %1070
  %1155 = phi <3 x half> [ %1153, %1072 ], [ %1065, %1070 ]
  %1156 = fptrunc float %1067 to half
  %1157 = tail call fast half @air.dot.v3f16(<3 x half> %1155, <3 x half> splat (half 0xH3555)) #14
  %1158 = tail call fast half @air.pow.f16(half %1157, half 0xH3E00) #14
  %1159 = extractelement <3 x half> %1155, i64 0
  %1160 = fsub fast half %1159, %1158
  %1161 = fmul fast half %1160, %1160
  %1162 = extractelement <3 x half> %1155, i64 1
  %1163 = fsub fast half %1162, %1158
  %1164 = fmul fast half %1163, %1163
  %1165 = extractelement <3 x half> %1155, i64 2
  %1166 = fsub fast half %1165, %1158
  %1167 = fmul fast half %1166, %1166
  %1168 = fpext half %1158 to float
  %1169 = fmul fast float %1168, 2.250000e+00
  %1170 = fsub fast float 1.000000e+00, %1168
  %1171 = fmul fast float %1169, %1170
  %1172 = fptrunc float %1171 to half
  %1173 = fmul fast half %1172, %1156
  %1174 = fpext half %1173 to float
  %1175 = fmul fast half %1173, 0xHB800
  %1176 = fmul fast float %1174, 0x3FD322D0E0000000
  %1177 = fptrunc float %1176 to half
  %1178 = insertelement <3 x half> poison, half %1177, i64 0
  %1179 = fmul fast <3 x half> %1178, %1155
  %1180 = shufflevector <3 x half> %1179, <3 x half> poison, <3 x i32> zeroinitializer
  %1181 = shufflevector <3 x half> %1155, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1182 = fmul fast float %1174, 0x3FE2C8B440000000
  %1183 = fptrunc float %1182 to half
  %1184 = insertelement <3 x half> poison, half %1183, i64 0
  %1185 = shufflevector <3 x half> %1184, <3 x half> poison, <3 x i32> zeroinitializer
  %1186 = fmul fast <3 x half> %1185, %1181
  %1187 = shufflevector <3 x half> %1155, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1188 = fmul fast float %1174, 0x3FBD2F1AA0000000
  %1189 = fptrunc float %1188 to half
  %1190 = insertelement <3 x half> poison, half %1189, i64 0
  %1191 = shufflevector <3 x half> %1190, <3 x half> poison, <3 x i32> zeroinitializer
  %1192 = fmul fast <3 x half> %1191, %1187
  %1193 = insertelement <3 x half> poison, half %1175, i64 0
  %1194 = shufflevector <3 x half> %1193, <3 x half> poison, <3 x i32> zeroinitializer
  %1195 = fadd fast <3 x half> %1194, %1155
  %1196 = fadd fast <3 x half> %1195, %1186
  %1197 = fadd fast <3 x half> %1196, %1180
  %1198 = fadd fast <3 x half> %1197, %1192
  %1199 = fneg fast half %1156
  %1200 = fmul fast half %1199, %1172
  %1201 = insertelement <3 x half> poison, half %1200, i64 0
  %1202 = shufflevector <3 x half> %1201, <3 x half> poison, <3 x i32> zeroinitializer
  %1203 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1155, <3 x half> splat (half 0xH3800), <3 x half> %1202) #14
  %1204 = fadd fast half %1164, 0xH399A
  %1205 = fadd fast half %1204, %1161
  %1206 = fadd fast half %1205, %1167
  %1207 = insertelement <3 x half> poison, half %1206, i64 0
  %1208 = shufflevector <3 x half> %1207, <3 x half> poison, <3 x i32> zeroinitializer
  %1209 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1203, <3 x half> %1198, <3 x half> %1208) #14
  %1210 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %1209, <3 x half> zeroinitializer) #14
  %1211 = fmul fast half %488, 0xH42CD
  %1212 = fadd fast half %1211, 0xHBCCD
  %1213 = fpext half %1212 to float
  %1214 = fadd fast float %1213, 0x3FF0FDBF40000000
  %1215 = fmul fast float %1214, 0x3FDA374BC0000000
  %1216 = fptrunc float %1215 to half
  %1217 = fpext half %1216 to float
  %1218 = fsub fast float 1.000000e+00, %1217
  %1219 = fmul fast float %1217, 4.000000e+00
  %1220 = fmul fast float %1219, %1218
  %1221 = fptrunc float %1220 to half
  %1222 = insertelement <3 x half> poison, half %1221, i64 0
  %1223 = shufflevector <3 x half> %1222, <3 x half> poison, <3 x i32> zeroinitializer
  %1224 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1155, <3 x half> %1210, <3 x half> %1223) #14
  br label %_Z19renderFGAdjustmentsDv3_DhS_DhDhDhDhRU9MTLdevice15SSRFGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit

_Z19renderFGAdjustmentsDv3_DhS_DhDhDhDhRU9MTLdevice15SSRFGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit: ; preds = %1154, %1064
  %1225 = phi <3 x half> [ %1065, %1064 ], [ %1224, %1154 ]
  %1226 = insertelement <3 x half> poison, half %96, i64 0
  %1227 = shufflevector <3 x half> %1226, <3 x half> poison, <3 x i32> zeroinitializer
  %1228 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %805, <3 x half> %1225, <3 x half> %1227) #14
  %1229 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 3
  %1230 = load float, ptr addrspace(1) %1229, align 4, !tbaa !147, !alias.scope !98, !noalias !99
  %1231 = fptrunc float %1230 to half
  %1232 = fpext half %1231 to float
  %1233 = fcmp fast olt half %1231, 0xH0000
  %1234 = fmul fast float %1232, 0x3FE99999A0000000
  %1235 = fmul fast half %1231, %1231
  %1236 = fptrunc float %1234 to half
  %1237 = select fast i1 %1233, half %1236, half %1235
  %1238 = fadd fast half %1237, 0xH3C00
  %1239 = fcmp fast ogt half %1231, 0xH0000
  br i1 %1239, label %1240, label %1245

1240:                                             ; preds = %_Z19renderFGAdjustmentsDv3_DhS_DhDhDhDhRU9MTLdevice15SSRFGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit
  %1241 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 11, i32 2
  %1242 = load float, ptr addrspace(1) %1241, align 4, !tbaa !148, !alias.scope !98, !noalias !99
  %1243 = fptrunc float %1242 to half
  %1244 = tail call fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %1228, half noundef %1238, half noundef %1243) #17
  br label %1247

1245:                                             ; preds = %_Z19renderFGAdjustmentsDv3_DhS_DhDhDhDhRU9MTLdevice15SSRFGAdjustmentN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEE.exit
  %1246 = tail call fast fastcc <3 x half> @_Z15smoothSatFilterDv3_DhDh(<3 x half> noundef %1228, half noundef %1238) #17
  br label %1247

1247:                                             ; preds = %1245, %1240
  %1248 = phi <3 x half> [ %1244, %1240 ], [ %1246, %1245 ]
  br i1 %1239, label %1249, label %1252

1249:                                             ; preds = %1247
  %1250 = fadd fast float %1232, 0xBFE3333340000000
  %1251 = tail call fast float @air.fast_fmax.f32(float %1250, float 0x3FC99999A0000000) #14
  br label %1256

1252:                                             ; preds = %1247
  %1253 = fmul fast float %1232, 0x3FE3333340000000
  %1254 = fsub fast float 0x3FB99999A0000000, %1253
  %1255 = tail call fast float @air.fast_fmax.f32(float %1254, float 0x3FC99999A0000000) #14
  br label %1256

1256:                                             ; preds = %1252, %1249
  %1257 = phi fast float [ %1251, %1249 ], [ %1255, %1252 ]
  %1258 = fptrunc float %1257 to half
  %1259 = fpext half %1258 to float
  %1260 = fsub fast float 1.000000e+00, %1259
  %1261 = fmul fast float %1260, %797
  %1262 = fptrunc float %1261 to half
  %1263 = insertelement <3 x half> poison, half %1262, i64 0
  %1264 = shufflevector <3 x half> %1263, <3 x half> poison, <3 x i32> zeroinitializer
  %1265 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1248, <3 x half> %1228, <3 x half> %1264) #14
  %1266 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> <half 0xH3C00, half 0xH399A, half 0xH3866>) #14
  %1267 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> <half 0xH3C00, half 0xH399A, half 0xH3866>) #14
  %1268 = fmul fast <3 x half> %1267, splat (half 0xH2CF4)
  %1269 = fadd fast <3 x half> %1267, splat (half 0xH2B0A)
  %1270 = fmul fast <3 x half> %1269, splat (half 0xH3B96)
  %1271 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1270, <3 x half> splat (half 0xH40CD)) #14
  %1272 = fcmp fast ogt <3 x half> %1267, splat (half 0xH292D)
  %1273 = select fast <3 x i1> %1272, <3 x half> %1271, <3 x half> %1268
  %1274 = fmul fast <3 x half> %1273, %1266
  %1275 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 10
  %1276 = load float, ptr addrspace(1) %1275, align 4, !tbaa !149, !alias.scope !98, !noalias !99
  %1277 = tail call fast float @air.fast_fabs.f32(float %1276) #14
  %1278 = fcmp fast olt float %1277, 0x3EE4F8B580000000
  br i1 %1278, label %1333, label %1279

1279:                                             ; preds = %1256
  %1280 = fptrunc float %1276 to half
  %1281 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %1265, <3 x half> zeroinitializer) #14
  %1282 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %1265, <3 x half> splat (half 0xH3C00)) #14
  %1283 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1265) #14
  %1284 = tail call fast half @air.dot.v3f16(<3 x half> %1283, <3 x half> splat (half 0xH3555)) #14
  %1285 = tail call fast half @air.sqrt.f16(half %1284) #14
  %1286 = fpext half %1285 to float
  %1287 = fsub fast float 1.000000e+00, %1286
  %1288 = fmul fast float %1287, %1286
  %1289 = fptrunc float %1288 to half
  %1290 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %1283) #14
  %1291 = tail call fast half @air.sqrt.f16(half %488) #14
  %1292 = fmul fast half %1289, %1280
  %1293 = fmul fast half %1292, 0xH4000
  %1294 = fmul fast half %1292, 0xHC000
  %1295 = fmul fast half %1294, %1291
  %1296 = fpext half %1293 to float
  %1297 = fmul fast float %1296, 0x3FD322D0E0000000
  %1298 = fptrunc float %1297 to half
  %1299 = insertelement <3 x half> poison, half %1298, i64 0
  %1300 = fmul fast <3 x half> %1299, %1290
  %1301 = shufflevector <3 x half> %1300, <3 x half> poison, <3 x i32> zeroinitializer
  %1302 = shufflevector <3 x half> %1290, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1303 = fmul fast float %1296, 0x3FE2C8B440000000
  %1304 = fptrunc float %1303 to half
  %1305 = insertelement <3 x half> poison, half %1304, i64 0
  %1306 = shufflevector <3 x half> %1305, <3 x half> poison, <3 x i32> zeroinitializer
  %1307 = fmul fast <3 x half> %1306, %1302
  %1308 = shufflevector <3 x half> %1290, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1309 = fmul fast float %1296, 0x3FBD2F1AA0000000
  %1310 = fptrunc float %1309 to half
  %1311 = insertelement <3 x half> poison, half %1310, i64 0
  %1312 = shufflevector <3 x half> %1311, <3 x half> poison, <3 x i32> zeroinitializer
  %1313 = fmul fast <3 x half> %1312, %1308
  %1314 = insertelement <3 x half> poison, half %1295, i64 0
  %1315 = shufflevector <3 x half> %1314, <3 x half> poison, <3 x i32> zeroinitializer
  %1316 = fadd fast <3 x half> %1315, %1290
  %1317 = fadd fast <3 x half> %1316, %1307
  %1318 = fadd fast <3 x half> %1317, %1301
  %1319 = fadd fast <3 x half> %1318, %1313
  %1320 = insertelement <3 x half> poison, half %1291, i64 0
  %1321 = shufflevector <3 x half> %1320, <3 x half> poison, <3 x i32> zeroinitializer
  %1322 = insertelement <3 x half> poison, half %1294, i64 0
  %1323 = shufflevector <3 x half> %1322, <3 x half> poison, <3 x i32> zeroinitializer
  %1324 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1290, <3 x half> %1321, <3 x half> %1323) #14
  %1325 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1324, <3 x half> %1319, <3 x half> splat (half 0xH3A66)) #14
  %1326 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %1325, <3 x half> zeroinitializer) #14
  %1327 = fmul fast <3 x half> %1326, %1326
  %1328 = fadd fast <3 x half> %1281, splat (half 0xHBC00)
  %1329 = fadd fast <3 x half> %1328, %1282
  %1330 = fadd fast <3 x half> %1329, %1327
  %1331 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %1330, <3 x half> %1265) #14
  %1332 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1330, <3 x half> %1331, <3 x half> splat (half 0xH3C00)) #14
  br label %1333

1333:                                             ; preds = %1279, %1256
  %1334 = phi <3 x half> [ %1265, %1256 ], [ %1332, %1279 ]
  %1335 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 14, i32 9
  %1336 = load float, ptr addrspace(1) %1335, align 4, !tbaa !150, !alias.scope !98, !noalias !99
  %1337 = tail call fast float @air.fast_fabs.f32(float %1336) #14
  %1338 = fcmp fast olt float %1337, 0x3EE4F8B580000000
  br i1 %1338, label %_Z21renderSkinAdjustmentsDv3_DhRU9MTLdevice15SSRFGAdjustmentDhDh.exit, label %1339

1339:                                             ; preds = %1333
  %1340 = fmul fast float %1336, 2.000000e+00
  %1341 = fptrunc float %1340 to half
  %1342 = tail call fast half @air.dot.v3f16(<3 x half> %1334, <3 x half> <half 0xH3800, half 0xH34CD, half 0xH3266>) #14
  %1343 = extractelement <3 x half> %1334, i64 0
  %1344 = extractelement <3 x half> %1334, i64 1
  %1345 = fadd fast half %1343, %1344
  %1346 = extractelement <3 x half> %1334, i64 2
  %1347 = fadd fast half %1345, %1346
  %1348 = fdiv fast half 0xH3C00, %1347
  %1349 = fmul fast half %1348, %1343
  %1350 = fmul fast half %1348, %1344
  %1351 = fmul fast half %1348, %1346
  %1352 = tail call fast half @air.fmax.f16(half %1349, half %1350) #14
  %1353 = tail call fast half @air.fmax.f16(half %1350, half %1351) #14
  %1354 = fadd fast half %1342, 0xHB666
  %1355 = fmul fast half %1354, 0xH3EAA
  %1356 = tail call fast half @air.clamp.f16(half %1355, half 0xH0000, half 0xH3C00) #14
  %1357 = fmul fast half %1356, 0xH4000
  %1358 = fsub fast half 0xH4200, %1357
  %1359 = fadd fast half %1352, 0xHB555
  %1360 = fadd fast half %1359, %1353
  %1361 = fmul fast half %1360, 0xH3DFF
  %1362 = tail call fast half @air.clamp.f16(half %1361, half 0xH0000, half 0xH3C00) #14
  %1363 = fmul fast half %1362, %1362
  %1364 = fmul fast half %1362, 0xH4000
  %1365 = fsub fast half 0xH4200, %1364
  %1366 = fmul fast half %1363, %1365
  %1367 = fmul fast <3 x half> %1274, %1334
  %1368 = fmul fast half %1356, %1356
  %1369 = fmul fast half %1368, %1341
  %1370 = fmul fast half %1369, %1358
  %1371 = fpext half %1370 to float
  %1372 = fpext half %1366 to float
  %1373 = fsub fast float 1.000000e+00, %1372
  %1374 = fmul fast float %1373, %1371
  %1375 = tail call fast float @air.fast_fmin.f32(float %1374, float 1.000000e+00) #14
  %1376 = fptrunc float %1375 to half
  %1377 = insertelement <3 x half> poison, half %1376, i64 0
  %1378 = shufflevector <3 x half> %1377, <3 x half> poison, <3 x i32> zeroinitializer
  %1379 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1334, <3 x half> %1367, <3 x half> %1378) #14
  br label %_Z21renderSkinAdjustmentsDv3_DhRU9MTLdevice15SSRFGAdjustmentDhDh.exit

_Z21renderSkinAdjustmentsDv3_DhRU9MTLdevice15SSRFGAdjustmentDhDh.exit: ; preds = %1339, %1333
  %1380 = phi <3 x half> [ %1334, %1333 ], [ %1379, %1339 ]
  %1381 = insertelement <3 x half> poison, half %95, i64 0
  %1382 = shufflevector <3 x half> %1381, <3 x half> poison, <3 x i32> zeroinitializer
  %1383 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1265, <3 x half> %1380, <3 x half> %1382) #14
  %1384 = shufflevector <3 x half> %1383, <3 x half> poison, <3 x i32> zeroinitializer
  %1385 = fmul fast <3 x half> %1384, <half 0xH383C, half 0xH2E4C, half 0xH2452>
  %1386 = shufflevector <3 x half> %1383, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1387 = fmul fast <3 x half> %1386, <half 0xH3548, half 0xH3AFD, half 0xH2F88>
  %1388 = fadd fast <3 x half> %1385, %1387
  %1389 = shufflevector <3 x half> %1383, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1390 = fmul fast <3 x half> %1389, <half 0xH307F, half 0xH2734, half 0xH3AEC>
  %1391 = fadd fast <3 x half> %1388, %1390
  %1392 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1391, <3 x half> splat (half 0xH3872)) #14
  %1393 = extractelement <3 x half> %1392, i64 0
  %1394 = extractelement <3 x half> %1392, i64 1
  %1395 = extractelement <3 x half> %1392, i64 2
  %1396 = tail call fast half @air.fmin3.f16(half %1393, half %1394, half %1395) #14
  %1397 = tail call fast half @air.dot.v3f16(<3 x half> %1392, <3 x half> splat (half 0xH3555)) #14
  %1398 = tail call fast half @air.mix.f16(half %1396, half %1397, half 0xH3800) #14
  %1399 = tail call fast half @air.pow.f16(half %1398, half 0xH4500) #14
  %1400 = fcmp fast ogt half %1398, 0xH0000
  br i1 %1400, label %1401, label %_Z16highlightRecoverDv3_DhDhDhDhDh.exit

1401:                                             ; preds = %_Z21renderSkinAdjustmentsDv3_DhRU9MTLdevice15SSRFGAdjustmentDhDh.exit
  %1402 = insertelement <3 x half> poison, half %1399, i64 0
  %1403 = shufflevector <3 x half> %1402, <3 x half> poison, <3 x i32> zeroinitializer
  %1404 = fmul fast <3 x half> %1403, %1392
  %1405 = insertelement <3 x half> poison, half %1398, i64 0
  %1406 = shufflevector <3 x half> %1405, <3 x half> poison, <3 x i32> zeroinitializer
  %1407 = fdiv fast <3 x half> %1404, %1406
  br label %_Z16highlightRecoverDv3_DhDhDhDhDh.exit

_Z16highlightRecoverDv3_DhDhDhDhDh.exit:          ; preds = %1401, %_Z21renderSkinAdjustmentsDv3_DhRU9MTLdevice15SSRFGAdjustmentDhDh.exit
  %1408 = phi fast <3 x half> [ %1407, %1401 ], [ zeroinitializer, %_Z21renderSkinAdjustmentsDv3_DhRU9MTLdevice15SSRFGAdjustmentDhDh.exit ]
  %1409 = insertelement <3 x half> poison, half %1396, i64 0
  %1410 = shufflevector <3 x half> %1409, <3 x half> poison, <3 x i32> zeroinitializer
  %1411 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1392, <3 x half> %1408, <3 x half> %1410) #14
  %1412 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1411, <3 x half> splat (half 0xH3F33)) #14
  %1413 = shufflevector <3 x half> %1412, <3 x half> poison, <3 x i32> zeroinitializer
  %1414 = fmul fast <3 x half> %1413, <half 0xH4011, half 0xHB353, half 0xHA060>
  %1415 = shufflevector <3 x half> %1412, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1416 = fmul fast <3 x half> %1415, <half 0xHB9D2, half 0xH3CED, half 0xHB0E8>
  %1417 = fadd fast <3 x half> %1414, %1416
  %1418 = shufflevector <3 x half> %1412, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1419 = fmul fast <3 x half> %1418, <half 0xHB4E9, half 0xH99DE, half 0xH3CA6>
  %1420 = fadd fast <3 x half> %1417, %1419
  %1421 = fmul fast half %1399, %488
  %1422 = fdiv fast half %1421, %1398
  %1423 = select i1 %1400, half %1422, half 0xH0000
  %1424 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1420, <3 x half> %1383, <3 x half> splat (half 0xH3400)) #14
  %1425 = extractelement <3 x half> %1424, i64 0
  %1426 = extractelement <3 x half> %1424, i64 1
  %1427 = fadd fast half %1425, %1426
  %1428 = extractelement <3 x half> %1424, i64 2
  %1429 = fadd fast half %1427, %1428
  %1430 = tail call fast half @air.dot.v3f16(<3 x half> %1424, <3 x half> splat (half 0xH3555)) #14
  %1431 = tail call fast half @air.fmax.f16(half %1430, half 0xH0000) #14
  %1432 = tail call fast half @air.sqrt.f16(half %1431) #14
  %1433 = tail call fast half @air.mix.f16(half %488, half %1423, half %1396) #14
  %1434 = tail call fast half @air.mix.f16(half %1433, half %488, half 0xH3400) #14
  %1435 = fmul fast half %1434, 0xH4200
  %1436 = fsub fast half %1429, %1435
  %1437 = fmul fast half %1436, 0xH4200
  %1438 = fadd fast half %1437, %1429
  %1439 = tail call fast half @air.fmax.f16(half %1429, half 0xH068E) #14
  %1440 = fdiv fast half %1438, %1439
  %1441 = fpext half %1440 to float
  %1442 = fadd fast float %1441, -1.000000e+00
  %1443 = fmul fast float %1442, 0x3FF922D0E0000000
  %1444 = fptrunc float %1443 to half
  %1445 = fpext half %1444 to float
  %1446 = tail call fast half @air.fabs.f16(half %1444) #14
  %1447 = fpext half %1446 to float
  %1448 = fadd fast float %1447, 1.000000e+00
  %1449 = fdiv fast float %1445, %1448
  %1450 = fptrunc float %1449 to half
  %1451 = fpext half %1450 to float
  %1452 = fcmp fast oge half %1450, 0xH0000
  %1453 = select i1 %1452, float 0x3FE4CCCCC0000000, float 7.500000e-01
  %1454 = fmul fast float %1453, %1451
  %1455 = fadd fast float %1454, 1.000000e+00
  %1456 = fptrunc float %1455 to half
  %1457 = tail call fast half @air.clamp.f16(half %1456, half 0xHC000, half 0xH419A) #14
  %1458 = insertelement <3 x half> poison, half %1457, i64 0
  %1459 = shufflevector <3 x half> %1458, <3 x half> poison, <3 x i32> zeroinitializer
  %1460 = fmul fast <3 x half> %1459, %1424
  %1461 = insertelement <3 x half> poison, half %1432, i64 0
  %1462 = shufflevector <3 x half> %1461, <3 x half> poison, <3 x i32> zeroinitializer
  %1463 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1424, <3 x half> %1460, <3 x half> %1462) #14
  %1464 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1383, <3 x half> %1463, <3 x half> splat (half 0xH3800)) #14
  %1465 = insertelement <3 x i1> poison, i1 %284, i64 0
  %1466 = shufflevector <3 x i1> %1465, <3 x i1> poison, <3 x i32> zeroinitializer
  %1467 = select fast <3 x i1> %1466, <3 x half> %1464, <3 x half> %1383
  %1468 = fptrunc float %250 to half
  %1469 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1383) #14
  %1470 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %320) #14
  %1471 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %18, i64 0, i32 1, i64 2, i32 4
  %1472 = load float, ptr addrspace(1) %1471, align 4, !tbaa !151, !alias.scope !153, !noalias !154
  %1473 = fptrunc float %1472 to half
  %1474 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %18, i64 0, i32 1, i64 3, i32 4
  %1475 = load float, ptr addrspace(1) %1474, align 4, !tbaa !151, !alias.scope !153, !noalias !154
  %1476 = fptrunc float %1475 to half
  %1477 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %18, i64 0, i32 1, i64 5, i32 0
  %1478 = load float, ptr addrspace(1) %1477, align 4, !tbaa !155, !alias.scope !153, !noalias !154
  %1479 = fadd fast half %1473, 0xHAE66
  %1480 = fmul fast half %1479, 0xH41B6
  %1481 = tail call fast half @air.clamp.f16(half %1480, half 0xH0000, half 0xH3C00) #14
  %1482 = fmul fast half %1481, %1481
  %1483 = fmul fast half %1481, 0xH4000
  %1484 = fsub fast half 0xH4200, %1483
  %1485 = fmul fast half %1482, %1484
  %1486 = tail call fast half @air.mix.f16(half 0xH3C00, half 0xH3266, half %1485) #14
  %1487 = tail call fast half @air.fmax.f16(half %1476, half 0xH1419) #14
  %1488 = fdiv fast half %1473, %1487
  %1489 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %18, i64 0, i32 1, i64 6, i32 6
  %1490 = load float, ptr addrspace(1) %1489, align 4, !tbaa !156, !alias.scope !153, !noalias !154
  %1491 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %18, i64 0, i32 1, i64 6, i32 4
  %1492 = load float, ptr addrspace(1) %1491, align 4, !tbaa !151, !alias.scope !153, !noalias !154
  %1493 = fsub fast float %1490, %1492
  %1494 = fptrunc float %1493 to half
  %1495 = fmul fast half %1494, 0xH4D00
  %1496 = fpext half %1495 to float
  %1497 = fadd fast float %1496, -2.000000e+00
  %1498 = tail call fast float @air.fast_fmin.f32(float %1497, float 1.000000e+00) #14
  %1499 = tail call fast float @air.fast_fmax.f32(float %1498, float 0.000000e+00) #14
  %1500 = fptrunc float %1499 to half
  %1501 = fpext half %1468 to float
  %1502 = fmul fast float %1501, 2.500000e-01
  %1503 = fadd fast float %1502, -1.500000e+00
  %1504 = tail call fast float @air.fast_fmin.f32(float %1503, float 1.000000e+00) #14
  %1505 = tail call fast float @air.fast_fmax.f32(float %1504, float 0.000000e+00) #14
  %1506 = fptrunc float %1505 to half
  %1507 = fpext half %1488 to float
  %1508 = fmul fast float %1507, 4.000000e+00
  %1509 = fadd fast float %1508, -9.000000e+00
  %1510 = tail call fast float @air.fast_fmin.f32(float %1509, float 3.000000e+00) #14
  %1511 = tail call fast float @air.fast_fmax.f32(float %1510, float 1.000000e+00) #14
  %1512 = fptrunc float %1511 to half
  %1513 = tail call fast half @air.fmin.f16(half %1500, half %1506) #14
  %1514 = fpext half %1513 to float
  %1515 = fmul fast float %1514, 3.000000e+00
  %1516 = fadd fast float %1515, 1.000000e+00
  %1517 = fpext half %1512 to float
  %1518 = fmul fast float %1516, %1517
  %1519 = tail call fast float @air.fast_fmax.f32(float %1518, float 1.000000e+00) #14
  %1520 = fptrunc float %1519 to half
  %1521 = fpext half %1486 to float
  %1522 = fmul fast float %1521, 0x3FEB333340000000
  %1523 = tail call fast float @air.fast_pow.f32(float 2.000000e+00, float %1522) #14
  %1524 = fmul fast float %1501, 4.000000e+00
  %1525 = fmul fast float %1524, %1523
  %1526 = fptrunc float %1525 to half
  %1527 = insertelement <3 x half> poison, half %1526, i64 0
  %1528 = shufflevector <3 x half> %1527, <3 x half> poison, <3 x i32> zeroinitializer
  %1529 = fmul fast <3 x half> %1528, %1470
  %1530 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1529) #14
  %1531 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1469, <3 x half> %1530, <3 x half> splat (half 0xH34CD)) #14
  %1532 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1531) #14
  %1533 = fmul fast <3 x half> %1532, splat (half 0xH3C36)
  %1534 = fadd fast <3 x half> %1533, splat (half 0xH2666)
  %1535 = fadd fast half %1520, 0xHBC00
  %1536 = fmul fast half %1535, 0xH3800
  %1537 = tail call fast half @air.clamp.f16(half %1536, half 0xH0000, half 0xH3C00) #14
  %1538 = fmul fast half %1537, %1537
  %1539 = fmul fast half %1537, 0xH4000
  %1540 = fsub fast half 0xH4200, %1539
  %1541 = fmul fast half %1538, %1540
  %1542 = tail call fast half @air.mix.f16(half 0xH34CD, half 0xH3666, half %1541) #14
  %1543 = fmul fast <3 x half> %1534, splat (half 0xHC600)
  %1544 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> splat (half 0xH4000), <3 x half> %1543) #14
  %1545 = fsub fast <3 x half> splat (half 0xH3C00), %1544
  %1546 = insertelement <3 x half> poison, half %1542, i64 0
  %1547 = shufflevector <3 x half> %1546, <3 x half> poison, <3 x i32> zeroinitializer
  %1548 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1534, <3 x half> %1545, <3 x half> %1547) #14
  %1549 = tail call fast half @air.dot.v3f16(<3 x half> splat (half 0xH3C00), <3 x half> %1469) #14
  %1550 = fadd fast half %1549, 0xHB8CD
  %1551 = fmul fast half %1550, 0xH4100
  %1552 = tail call fast half @air.clamp.f16(half %1551, half 0xH0000, half 0xH3C00) #14
  %1553 = fmul fast half %1552, %1552
  %1554 = fmul fast half %1552, 0xH4000
  %1555 = fsub fast half 0xH4200, %1554
  %1556 = fmul fast half %1553, %1555
  %1557 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %1548) #14
  %1558 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %1548) #14
  %1559 = fmul fast <3 x half> %1558, splat (half 0xH4A76)
  %1560 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1558, <3 x half> splat (half 0xH36AA)) #14
  %1561 = fmul fast <3 x half> %1560, splat (half 0xH3C38)
  %1562 = fadd fast <3 x half> %1561, splat (half 0xHAB0A)
  %1563 = fcmp fast ogt <3 x half> %1558, splat (half 0xH1A69)
  %1564 = select fast <3 x i1> %1563, <3 x half> %1562, <3 x half> %1559
  %1565 = fmul fast <3 x half> %1564, %1557
  %1566 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %1469) #14
  %1567 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %1469) #14
  %1568 = fmul fast <3 x half> %1567, splat (half 0xH4A76)
  %1569 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1567, <3 x half> splat (half 0xH36AA)) #14
  %1570 = fmul fast <3 x half> %1569, splat (half 0xH3C38)
  %1571 = fadd fast <3 x half> %1570, splat (half 0xHAB0A)
  %1572 = fcmp fast ogt <3 x half> %1567, splat (half 0xH1A69)
  %1573 = select fast <3 x i1> %1572, <3 x half> %1571, <3 x half> %1568
  %1574 = fmul fast <3 x half> %1573, %1566
  %1575 = tail call fast half @air.dot.v3f16(<3 x half> %1565, <3 x half> %1565) #14
  %1576 = tail call fast half @air.dot.v3f16(<3 x half> splat (half 0xH3C00), <3 x half> %1565) #14
  %1577 = fdiv fast half %1575, %1576
  %1578 = tail call fast half @air.dot.v3f16(<3 x half> %1565, <3 x half> <half 0xH399A, half 0xH3266, half 0xH2E66>) #14
  %1579 = tail call fast half @air.mix.f16(half %1577, half %1578, half %96) #14
  %1580 = insertelement <3 x half> poison, half %1579, i64 0
  %1581 = shufflevector <3 x half> %1580, <3 x half> poison, <3 x i32> zeroinitializer
  %1582 = fpext half %1556 to float
  %1583 = fsub fast float 1.000000e+00, %1582
  %1584 = fmul fast float %1583, 0x3FEE680000000000
  %1585 = fptrunc float %1584 to half
  %1586 = insertelement <3 x half> poison, half %1585, i64 0
  %1587 = shufflevector <3 x half> %1586, <3 x half> poison, <3 x i32> zeroinitializer
  %1588 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1581, <3 x half> %1565, <3 x half> %1587) #14
  %1589 = fmul fast half %1520, 0xH2E66
  %1590 = tail call fast half @air.clamp.f16(half %1589, half 0xH0000, half 0xH359A) #14
  %1591 = fmul fast <3 x half> %1574, %1574
  %1592 = insertelement <3 x half> poison, half %1590, i64 0
  %1593 = shufflevector <3 x half> %1592, <3 x half> poison, <3 x i32> zeroinitializer
  %1594 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1574, <3 x half> %1591, <3 x half> %1593) #14
  %1595 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %1594) #14
  %1596 = fmul fast <3 x half> %1594, splat (half 0xH4C00)
  %1597 = fadd fast <3 x half> %1596, splat (half 0xHCA00)
  %1598 = fmul fast <3 x half> %1597, %1594
  %1599 = fadd fast <3 x half> %1598, splat (half 0xH4400)
  %1600 = fmul fast <3 x half> %1599, %1594
  %1601 = fcmp fast ole <3 x half> %1594, splat (half 0xH3400)
  %1602 = select fast <3 x i1> %1601, <3 x half> %1600, <3 x half> %1595
  %1603 = fsub fast <3 x half> %1602, %1594
  %1604 = fsub fast <3 x half> splat (half 0xH3C00), %1594
  %1605 = fmul fast <3 x half> %1604, %1594
  %1606 = fcmp fast ole <3 x half> %1588, splat (half 0xH3800)
  %1607 = select fast <3 x i1> %1606, <3 x half> %1605, <3 x half> %1603
  %1608 = fmul fast <3 x half> %1588, splat (half 0xH4000)
  %1609 = fadd fast <3 x half> %1608, splat (half 0xHBC00)
  %1610 = fmul fast <3 x half> %1607, %1609
  %1611 = fadd fast <3 x half> %1610, %1594
  %1612 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1611) #14
  %1613 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1594, <3 x half> %1612, <3 x half> splat (half 0xH399A)) #14
  %1614 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %1613) #14
  %1615 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %1613) #14
  %1616 = fmul fast <3 x half> %1615, splat (half 0xH2CF4)
  %1617 = fadd fast <3 x half> %1615, splat (half 0xH2B0A)
  %1618 = fmul fast <3 x half> %1617, splat (half 0xH3B96)
  %1619 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1618, <3 x half> splat (half 0xH40CD)) #14
  %1620 = fcmp fast ogt <3 x half> %1615, splat (half 0xH292D)
  %1621 = select fast <3 x i1> %1620, <3 x half> %1619, <3 x half> %1616
  %1622 = fmul fast <3 x half> %1621, %1614
  %1623 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %1574) #14
  %1624 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %1574) #14
  %1625 = fmul fast <3 x half> %1624, splat (half 0xH2CF4)
  %1626 = fadd fast <3 x half> %1624, splat (half 0xH2B0A)
  %1627 = fmul fast <3 x half> %1626, splat (half 0xH3B96)
  %1628 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1627, <3 x half> splat (half 0xH40CD)) #14
  %1629 = fcmp fast ogt <3 x half> %1624, splat (half 0xH292D)
  %1630 = select fast <3 x i1> %1629, <3 x half> %1628, <3 x half> %1625
  %1631 = fmul fast <3 x half> %1630, %1623
  %1632 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1631, <3 x half> %1622, <3 x half> splat (half 0xH399A)) #14
  %1633 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %1632) #14
  %1634 = shufflevector <3 x float> %1633, <3 x float> poison, <3 x i32> zeroinitializer
  %1635 = fmul fast <3 x float> %1634, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %1636 = shufflevector <3 x float> %1633, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1637 = fmul fast <3 x float> %1636, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %1638 = fadd fast <3 x float> %1635, %1637
  %1639 = shufflevector <3 x float> %1633, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1640 = fmul fast <3 x float> %1639, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %1641 = fadd fast <3 x float> %1638, %1640
  %1642 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %1641) #14
  %1643 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %1641) #14
  %1644 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %1643, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %1645 = fmul fast <3 x float> %1644, %1642
  %1646 = shufflevector <3 x float> %1645, <3 x float> poison, <3 x i32> zeroinitializer
  %1647 = fmul fast <3 x float> %1646, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %1648 = shufflevector <3 x float> %1645, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1649 = fmul fast <3 x float> %1648, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %1650 = fadd fast <3 x float> %1647, %1649
  %1651 = shufflevector <3 x float> %1645, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1652 = fmul fast <3 x float> %1651, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %1653 = fadd fast <3 x float> %1650, %1652
  %1654 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %1653) #14
  %1655 = extractelement <3 x half> %1654, i64 2
  %1656 = fcmp fast une half %1655, 0xH0000
  %1657 = extractelement <3 x half> %1654, i64 1
  %1658 = fcmp fast une half %1657, 0xH0000
  %1659 = select i1 %1656, i1 true, i1 %1658
  br i1 %1659, label %1660, label %_Z23renderBrightAndContrastDv3_DhS_DhDhDhRU9MTLdevice8SSRStats.exit

1660:                                             ; preds = %_Z16highlightRecoverDv3_DhDhDhDhDh.exit
  %1661 = tail call fast half @air.atan2.f16(half %1655, half %1657) #14
  %1662 = fadd fast half %1661, 0xHBC88
  br label %_Z23renderBrightAndContrastDv3_DhS_DhDhDhRU9MTLdevice8SSRStats.exit

_Z23renderBrightAndContrastDv3_DhS_DhDhDhRU9MTLdevice8SSRStats.exit: ; preds = %1660, %_Z16highlightRecoverDv3_DhDhDhDhDh.exit
  %1663 = phi half [ %1662, %1660 ], [ 0xHBC88, %_Z16highlightRecoverDv3_DhDhDhDhDh.exit ]
  %1664 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1631, <3 x half> %1622, <3 x half> splat (half 0xH34CD)) #14
  %1665 = fmul fast float %1514, 0x3FE6666660000000
  %1666 = fsub fast float 1.000000e+00, %1665
  %1667 = tail call fast float @air.fast_fmin.f32(float %1509, float 1.000000e+00) #14
  %1668 = tail call fast float @air.fast_fmax.f32(float %1667, float 0.000000e+00) #14
  %1669 = fmul fast float %1668, 0x3FE3333340000000
  %1670 = fsub fast float 1.000000e+00, %1669
  %1671 = fptrunc float %1670 to half
  %1672 = fpext half %1671 to float
  %1673 = fmul fast float %1666, %1672
  %1674 = fptrunc float %1673 to half
  %1675 = fsub fast float 1.000000e+00, %1478
  %1676 = fptrunc float %1675 to half
  %1677 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %1383, <3 x half> splat (half 0xH3C00)) #14
  %1678 = fadd fast <3 x half> %1677, splat (half 0xHBC00)
  %1679 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %1383, <3 x half> zeroinitializer) #14
  %1680 = fmul fast half %1663, %1663
  %1681 = fmul fast half %1680, 0xHC449
  %1682 = tail call fast half @air.exp.f16(half %1681) #14
  %1683 = fpext half %1682 to float
  %1684 = tail call fast float @air.fast_saturate.f32(float %1683) #14
  %1685 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %1632, half noundef 0xH34CD) #17
  %1686 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %1632, <3 x half> %1685) #14
  %1687 = fptrunc float %1684 to half
  %1688 = insertelement <3 x half> poison, half %1687, i64 0
  %1689 = shufflevector <3 x half> %1688, <3 x half> poison, <3 x i32> zeroinitializer
  %1690 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1632, <3 x half> %1686, <3 x half> %1689) #14
  %1691 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1664, <3 x half> %1690, <3 x half> %1227) #14
  %1692 = fdiv fast <3 x half> %320, %1528
  %1693 = tail call fast half @air.dot.v3f16(<3 x half> %1692, <3 x half> <half 0xH32D1, half 0xH39B8, half 0xH2C9C>) #14
  %1694 = fpext half %1693 to float
  %1695 = fadd fast float %1694, 0x3F1A36E2E0000000
  %1696 = tail call fast float @air.fast_fmin.f32(float %1695, float 1.000000e+00) #14
  %1697 = fmul fast float %1501, 5.000000e-01
  %1698 = fmul fast float %1697, %1696
  %1699 = fptrunc float %1698 to half
  %1700 = fadd fast half %1699, 0xHB266
  %1701 = fmul fast half %1700, 0xH4000
  %1702 = tail call fast half @air.clamp.f16(half %1701, half 0xH0000, half 0xH3C00) #14
  %1703 = fmul fast half %1702, %1702
  %1704 = fmul fast half %1702, 0xH4000
  %1705 = fsub fast half 0xH4200, %1704
  %1706 = fmul fast half %1703, %1705
  %1707 = tail call fast half @air.pow.f16(half %1706, half 0xH3746) #14
  %1708 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1692, <3 x half> splat (half 0xH3C00)) #14
  %1709 = fpext half %1676 to float
  %1710 = tail call fast float @air.fast_pow.f32(float %1709, float 1.000000e+00) #14
  %1711 = fptrunc float %1710 to half
  %1712 = insertelement <3 x half> poison, half %1711, i64 0
  %1713 = shufflevector <3 x half> %1712, <3 x half> poison, <3 x i32> zeroinitializer
  %1714 = fadd fast <3 x half> %1713, %1708
  %1715 = fdiv fast <3 x half> %1708, %1714
  %1716 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1715) #14
  %1717 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1716, <3 x half> splat (half 0xH3F33)) #14
  %1718 = tail call fast half @air.saturate.f16(half %1707) #14
  %1719 = insertelement <3 x half> poison, half %1718, i64 0
  %1720 = shufflevector <3 x half> %1719, <3 x half> poison, <3 x i32> zeroinitializer
  %1721 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1691, <3 x half> %1717, <3 x half> %1720) #14
  %1722 = fpext half %1674 to float
  %1723 = fmul fast float %1722, 5.000000e-01
  %1724 = tail call fast float @air.fast_saturate.f32(float %1723) #14
  %1725 = fptrunc float %1724 to half
  %1726 = insertelement <3 x half> poison, half %1725, i64 0
  %1727 = shufflevector <3 x half> %1726, <3 x half> poison, <3 x i32> zeroinitializer
  %1728 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1691, <3 x half> %1721, <3 x half> %1727) #14
  %1729 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1691, <3 x half> %1728, <3 x half> %1382) #14
  %1730 = tail call fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %1729, half noundef 0xH3C66, half noundef 0xH4200) #17
  %1731 = tail call fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %1729, half noundef 0xH3C14, half noundef 0xH4200) #17
  %1732 = fadd fast half %96, %95
  %1733 = fpext half %1732 to float
  %1734 = fmul fast float %1733, 5.000000e-01
  %1735 = tail call fast float @air.fast_saturate.f32(float %1734) #14
  %1736 = fptrunc float %1735 to half
  %1737 = insertelement <3 x half> poison, half %1736, i64 0
  %1738 = shufflevector <3 x half> %1737, <3 x half> poison, <3 x i32> zeroinitializer
  %1739 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1730, <3 x half> %1731, <3 x half> %1738) #14
  %1740 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1739) #14
  %1741 = fadd fast <3 x half> %1678, %1679
  %1742 = fadd fast <3 x half> %1741, %1740
  %1743 = icmp eq i32 %279, 16
  %1744 = insertelement <3 x i1> poison, i1 %1743, i64 0
  %1745 = shufflevector <3 x i1> %1744, <3 x i1> poison, <3 x i32> zeroinitializer
  %1746 = select fast <3 x i1> %1745, <3 x half> %1742, <3 x half> %1383
  br i1 %51, label %_Z29renderNeutralizingAdjustmentsDv3_DhbRU9MTLdevice18SSRCastAdjustmentsDhDhbRU9MTLdevice8SSRStats.exit, label %1747

1747:                                             ; preds = %_Z23renderBrightAndContrastDv3_DhS_DhDhDhRU9MTLdevice8SSRStats.exit
  %1748 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %18, i64 0, i32 1, i64 4, i32 4
  %1749 = load float, ptr addrspace(1) %1748, align 4, !tbaa !151, !alias.scope !153, !noalias !154
  %1750 = insertelement <3 x half> undef, half %1473, i64 0
  %1751 = insertelement <3 x half> %1750, half %1476, i64 1
  %1752 = fptrunc float %1749 to half
  %1753 = insertelement <3 x half> %1751, half %1752, i64 2
  %1754 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %1753) #14
  %1755 = shufflevector <3 x float> %1754, <3 x float> poison, <3 x i32> zeroinitializer
  %1756 = fmul fast <3 x float> %1755, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %1757 = shufflevector <3 x float> %1754, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1758 = fmul fast <3 x float> %1757, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %1759 = fadd fast <3 x float> %1756, %1758
  %1760 = shufflevector <3 x float> %1754, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1761 = fmul fast <3 x float> %1760, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %1762 = fadd fast <3 x float> %1759, %1761
  %1763 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %1762) #14
  %1764 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %1762) #14
  %1765 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %1764, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %1766 = fmul fast <3 x float> %1765, %1763
  %1767 = shufflevector <3 x float> %1766, <3 x float> poison, <3 x i32> zeroinitializer
  %1768 = fmul fast <3 x float> %1767, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %1769 = shufflevector <3 x float> %1766, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1770 = fmul fast <3 x float> %1769, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %1771 = fadd fast <3 x float> %1768, %1770
  %1772 = shufflevector <3 x float> %1766, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1773 = fmul fast <3 x float> %1772, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %1774 = fadd fast <3 x float> %1771, %1773
  %1775 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %1774) #14
  %1776 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %1753) #14
  %1777 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %1753) #14
  %1778 = fmul fast <3 x half> %1777, splat (half 0xH4A76)
  %1779 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1777, <3 x half> splat (half 0xH36AA)) #14
  %1780 = fmul fast <3 x half> %1779, splat (half 0xH3C38)
  %1781 = fadd fast <3 x half> %1780, splat (half 0xHAB0A)
  %1782 = fcmp fast ogt <3 x half> %1777, splat (half 0xH1A69)
  %1783 = select fast <3 x i1> %1782, <3 x half> %1781, <3 x half> %1778
  %1784 = fmul fast <3 x half> %1783, %1776
  %1785 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %1784) #14
  %1786 = shufflevector <3 x float> %1785, <3 x float> poison, <3 x i32> zeroinitializer
  %1787 = fmul fast <3 x float> %1786, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %1788 = shufflevector <3 x float> %1785, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1789 = fmul fast <3 x float> %1788, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %1790 = fadd fast <3 x float> %1787, %1789
  %1791 = shufflevector <3 x float> %1785, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1792 = fmul fast <3 x float> %1791, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %1793 = fadd fast <3 x float> %1790, %1792
  %1794 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %1793) #14
  %1795 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %1793) #14
  %1796 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %1795, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %1797 = fmul fast <3 x float> %1796, %1794
  %1798 = shufflevector <3 x float> %1797, <3 x float> poison, <3 x i32> zeroinitializer
  %1799 = fmul fast <3 x float> %1798, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %1800 = shufflevector <3 x float> %1797, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1801 = fmul fast <3 x float> %1800, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %1802 = fadd fast <3 x float> %1799, %1801
  %1803 = shufflevector <3 x float> %1797, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1804 = fmul fast <3 x float> %1803, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %1805 = fadd fast <3 x float> %1802, %1804
  %1806 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %1805) #14
  %1807 = select fast i1 %64, half 0xH0000, half %95
  %1808 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 15
  %1809 = load float, ptr addrspace(1) %1808, align 4, !tbaa !157, !alias.scope !98, !noalias !99
  %1810 = tail call fast float @air.fast_fabs.f32(float %1809) #14
  %1811 = fcmp fast olt float %1810, 0x3EE4F8B580000000
  br i1 %1811, label %2182, label %1812

1812:                                             ; preds = %1747
  %1813 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 16
  %1814 = load float, ptr addrspace(1) %1813, align 4, !tbaa !158, !alias.scope !98, !noalias !99
  %1815 = tail call fast float @air.fast_fabs.f32(float %1814) #14
  %1816 = fcmp fast olt float %1815, 0x3EE4F8B580000000
  br i1 %1816, label %1817, label %2001

1817:                                             ; preds = %1812
  %1818 = fptrunc float %1809 to half
  %1819 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1746) #14
  %1820 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %1819) #14
  %1821 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %1819) #14
  %1822 = fmul fast <3 x half> %1821, splat (half 0xH4A76)
  %1823 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1821, <3 x half> splat (half 0xH36AA)) #14
  %1824 = fmul fast <3 x half> %1823, splat (half 0xH3C38)
  %1825 = fadd fast <3 x half> %1824, splat (half 0xHAB0A)
  %1826 = fcmp fast ogt <3 x half> %1821, splat (half 0xH1A69)
  %1827 = select fast <3 x i1> %1826, <3 x half> %1825, <3 x half> %1822
  %1828 = fmul fast <3 x half> %1827, %1820
  %1829 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %1828) #14
  %1830 = shufflevector <3 x float> %1829, <3 x float> poison, <3 x i32> zeroinitializer
  %1831 = fmul fast <3 x float> %1830, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %1832 = shufflevector <3 x float> %1829, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1833 = fmul fast <3 x float> %1832, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %1834 = fadd fast <3 x float> %1831, %1833
  %1835 = shufflevector <3 x float> %1829, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1836 = fmul fast <3 x float> %1835, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %1837 = fadd fast <3 x float> %1834, %1836
  %1838 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %1837) #14
  %1839 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %1837) #14
  %1840 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %1839, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %1841 = fmul fast <3 x float> %1840, %1838
  %1842 = shufflevector <3 x float> %1841, <3 x float> poison, <3 x i32> zeroinitializer
  %1843 = fmul fast <3 x float> %1842, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %1844 = shufflevector <3 x float> %1841, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1845 = fmul fast <3 x float> %1844, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %1846 = fadd fast <3 x float> %1843, %1845
  %1847 = shufflevector <3 x float> %1841, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1848 = fmul fast <3 x float> %1847, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %1849 = fadd fast <3 x float> %1846, %1848
  %1850 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %1849) #14
  %1851 = extractelement <3 x half> %1850, i64 1
  %1852 = fmul fast half %1851, %1851
  %1853 = extractelement <3 x half> %1850, i64 2
  %1854 = fmul fast half %1853, %1853
  %1855 = fadd fast half %1852, %1854
  %1856 = tail call fast half @air.sqrt.f16(half %1855) #14
  %1857 = fpext half %1856 to float
  %1858 = fcmp fast ogt float %1857, 0x3F50624DE0000000
  br i1 %1858, label %1859, label %1864

1859:                                             ; preds = %1817
  %1860 = fdiv fast half %1851, %1856
  %1861 = insertelement <2 x half> undef, half %1860, i64 0
  %1862 = fdiv fast half %1853, %1856
  %1863 = insertelement <2 x half> %1861, half %1862, i64 1
  br label %1864

1864:                                             ; preds = %1859, %1817
  %1865 = phi fast <2 x half> [ %1863, %1859 ], [ zeroinitializer, %1817 ]
  %1866 = extractelement <3 x half> %1775, i64 1
  %1867 = fmul fast half %1866, %1866
  %1868 = extractelement <3 x half> %1775, i64 2
  %1869 = fmul fast half %1868, %1868
  %1870 = fadd fast half %1867, %1869
  %1871 = tail call fast half @air.sqrt.f16(half %1870) #14
  %1872 = fpext half %1871 to float
  %1873 = fcmp fast ogt float %1872, 0x3F50624DE0000000
  br i1 %1873, label %1874, label %_Z5deRedDv3_DhDhDhS_Dh.exit.i

1874:                                             ; preds = %1864
  %1875 = fdiv fast half %1866, %1871
  %1876 = insertelement <2 x half> undef, half %1875, i64 0
  %1877 = fdiv fast half %1868, %1871
  %1878 = insertelement <2 x half> %1876, half %1877, i64 1
  br label %_Z5deRedDv3_DhDhDhS_Dh.exit.i

_Z5deRedDv3_DhDhDhS_Dh.exit.i:                    ; preds = %1874, %1864
  %1879 = phi fast <2 x half> [ %1878, %1874 ], [ zeroinitializer, %1864 ]
  %1880 = fadd fast half %1871, 0xHADC3
  %1881 = fmul fast half %1880, 0xH5243
  %1882 = tail call fast half @air.clamp.f16(half %1881, half 0xH0000, half 0xH3C00) #14
  %1883 = fmul fast half %1882, %1882
  %1884 = fmul fast half %1882, 0xH4000
  %1885 = fsub fast half 0xH4200, %1884
  %1886 = fmul fast half %1883, %1885
  %1887 = extractelement <2 x half> %1865, i64 0
  %1888 = fmul fast half %1887, 0xH3AEE
  %1889 = extractelement <2 x half> %1865, i64 1
  %1890 = fmul fast half %1889, 0xH3800
  %1891 = fadd fast half %1888, %1890
  %1892 = tail call fast half @air.sqrt.f16(half 0xH3C00) #14
  %1893 = fdiv fast half %1891, %1892
  %1894 = fadd fast half %1893, 0xHBACD
  %1895 = fmul fast half %1894, 0xH4723
  %1896 = tail call fast half @air.clamp.f16(half %1895, half 0xH0000, half 0xH3C00) #14
  %1897 = fmul fast half %1896, %1896
  %1898 = fmul fast half %1896, 0xH4000
  %1899 = fsub fast half 0xH4200, %1898
  %1900 = fmul fast half %1897, %1899
  %1901 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %1746, <3 x half> splat (half 0xH3C00)) #14
  %1902 = fadd fast <3 x half> %1901, splat (half 0xHBC00)
  %1903 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %1746, <3 x half> zeroinitializer) #14
  %1904 = extractelement <2 x half> %1879, i64 0
  %1905 = fmul fast half %1904, 0xH3AEE
  %1906 = extractelement <2 x half> %1879, i64 1
  %1907 = fmul fast half %1906, 0xH3800
  %1908 = fadd fast half %1905, %1907
  %1909 = fdiv fast half %1908, %1892
  %1910 = fadd fast half %1909, 0xHBB9A
  %1911 = fmul fast half %1910, 0xH4E3E
  %1912 = tail call fast half @air.clamp.f16(half %1911, half 0xH0000, half 0xH3C00) #14
  %1913 = fmul fast half %1912, %1912
  %1914 = fmul fast half %1912, 0xH4000
  %1915 = fsub fast half 0xH4200, %1914
  %1916 = fmul fast half %1913, %1915
  %1917 = fpext half %1851 to float
  %1918 = fpext half %1900 to float
  %1919 = fpext half %1916 to float
  %1920 = fpext half %1886 to float
  %1921 = fmul fast float %1918, %1920
  %1922 = fmul fast float %1921, %1919
  %1923 = fmul fast float %1922, 0x3FC3333340000000
  %1924 = fmul fast float %1923, %1917
  %1925 = fsub fast float %1917, %1924
  %1926 = fptrunc float %1925 to half
  %1927 = fpext half %1853 to float
  %1928 = fmul fast float %1923, %1927
  %1929 = fsub fast float %1927, %1928
  %1930 = fptrunc float %1929 to half
  %1931 = fsub fast half 0xH3C00, %1807
  %1932 = fmul fast half %1851, %1931
  %1933 = fmul fast half %1807, %1926
  %1934 = fadd fast half %1933, %1932
  %1935 = fmul fast half %1853, %1931
  %1936 = fmul fast half %1807, %1930
  %1937 = fadd fast half %1936, %1935
  %1938 = fpext half %1934 to float
  %1939 = fmul fast float %1923, %1938
  %1940 = fsub fast float %1938, %1939
  %1941 = fptrunc float %1940 to half
  %1942 = fpext half %1937 to float
  %1943 = fmul fast float %1923, %1942
  %1944 = fsub fast float %1942, %1943
  %1945 = fptrunc float %1944 to half
  %1946 = extractelement <3 x half> %1850, i64 0
  %1947 = fpext half %1946 to float
  %1948 = fmul fast float %1947, 0x3F999999A0000000
  %1949 = fmul fast float %1948, %1922
  %1950 = fadd fast float %1949, %1947
  %1951 = fptrunc float %1950 to half
  %1952 = fsub fast half 0xH3C00, %96
  %1953 = fmul fast half %1934, %1952
  %1954 = fmul fast half %96, %1941
  %1955 = fadd fast half %1954, %1953
  %1956 = insertelement <3 x half> poison, half %1955, i64 1
  %1957 = fmul fast half %1937, %1952
  %1958 = fmul fast half %96, %1945
  %1959 = fadd fast half %1958, %1957
  %1960 = insertelement <3 x half> %1956, half %1959, i64 2
  %1961 = fmul fast half %1946, %1952
  %1962 = fmul fast half %96, %1951
  %1963 = fadd fast half %1962, %1961
  %1964 = insertelement <3 x half> %1960, half %1963, i64 0
  %1965 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %1964) #14
  %1966 = shufflevector <3 x float> %1965, <3 x float> poison, <3 x i32> zeroinitializer
  %1967 = shufflevector <3 x float> %1965, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1968 = fmul fast <3 x float> %1967, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %1969 = fadd fast <3 x float> %1968, %1966
  %1970 = shufflevector <3 x float> %1965, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1971 = fmul fast <3 x float> %1970, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %1972 = fadd fast <3 x float> %1969, %1971
  %1973 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %1972) #14
  %1974 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %1972) #14
  %1975 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %1974, <3 x float> splat (float 0x40029ACA60000000)) #14
  %1976 = fmul fast <3 x float> %1975, %1973
  %1977 = shufflevector <3 x float> %1976, <3 x float> poison, <3 x i32> zeroinitializer
  %1978 = fmul fast <3 x float> %1977, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %1979 = shufflevector <3 x float> %1976, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %1980 = fmul fast <3 x float> %1979, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %1981 = fadd fast <3 x float> %1978, %1980
  %1982 = shufflevector <3 x float> %1976, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %1983 = fmul fast <3 x float> %1982, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %1984 = fadd fast <3 x float> %1981, %1983
  %1985 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %1984) #14
  %1986 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %1985) #14
  %1987 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %1985) #14
  %1988 = fmul fast <3 x half> %1987, splat (half 0xH2CF4)
  %1989 = fadd fast <3 x half> %1987, splat (half 0xH2B0A)
  %1990 = fmul fast <3 x half> %1989, splat (half 0xH3B96)
  %1991 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %1990, <3 x half> splat (half 0xH40CD)) #14
  %1992 = fcmp fast ogt <3 x half> %1987, splat (half 0xH292D)
  %1993 = select fast <3 x i1> %1992, <3 x half> %1991, <3 x half> %1988
  %1994 = fmul fast <3 x half> %1993, %1986
  %1995 = fadd fast <3 x half> %1902, %1903
  %1996 = fadd fast <3 x half> %1995, %1994
  %1997 = insertelement <3 x half> poison, half %1818, i64 0
  %1998 = shufflevector <3 x half> %1997, <3 x half> poison, <3 x i32> zeroinitializer
  %1999 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1819, <3 x half> %1996, <3 x half> %1998) #14
  %2000 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %1746, <3 x half> %1999, <3 x half> %1227) #14
  br label %2182

2001:                                             ; preds = %1812
  %2002 = extractelement <3 x half> %1806, i64 2
  %2003 = fcmp fast une half %2002, 0xH0000
  %2004 = extractelement <3 x half> %1806, i64 1
  %2005 = fcmp fast une half %2004, 0xH0000
  %2006 = select i1 %2003, i1 true, i1 %2005
  br i1 %2006, label %2007, label %2009

2007:                                             ; preds = %2001
  %2008 = tail call fast half @air.atan2.f16(half %2002, half %2004) #14
  br label %2009

2009:                                             ; preds = %2007, %2001
  %2010 = phi fast half [ %2008, %2007 ], [ 0xH0000, %2001 ]
  %2011 = fadd fast half %2010, 0xH4648
  %2012 = tail call fast half @air.sign.f16(half %2010) #14
  %2013 = fpext half %2012 to float
  %2014 = tail call i1 @air.convert.u.i1.f.f32(float %2013) #14
  %2015 = select fast i1 %2014, half %2011, half %2010
  %2016 = tail call fast half @air.fmod.f16(half %2015, half 0xH4648) #14
  %2017 = fpext half %2016 to float
  %2018 = fadd fast float %2017, 0xBFD3333340000000
  %2019 = tail call fast float @air.fast_fabs.f32(float %2018) #14
  %2020 = fadd fast float %2019, -5.000000e-01
  %2021 = fmul fast float %2020, 0xC001C71C80000000
  %2022 = tail call fast float @air.fast_clamp.f32(float %2021, float 0.000000e+00, float 1.000000e+00) #14
  %2023 = fmul fast float %2022, 2.000000e+00
  %2024 = fsub fast float 3.000000e+00, %2023
  %2025 = fmul fast float %2022, %2022
  %2026 = fmul fast float %2025, 5.000000e-01
  %2027 = fmul fast float %2026, %2024
  %2028 = fptrunc float %2027 to half
  %2029 = shufflevector <3 x half> %1806, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %2030 = tail call fast half @air.dot.v2f16(<2 x half> %2029, <2 x half> %2029) #14
  %2031 = tail call fast half @air.sqrt.f16(half %2030) #14
  %2032 = fadd fast half %2016, 0xHBA00
  %2033 = fadd fast half %2032, %2028
  %2034 = fmul fast half %2033, 0xH44FF
  %2035 = tail call fast half @air.clamp.f16(half %2034, half 0xH0000, half 0xH3C00) #14
  %2036 = fmul fast half %2035, %2035
  %2037 = fmul fast half %2035, 0xH4000
  %2038 = fsub fast half 0xH4200, %2037
  %2039 = fmul fast half %2036, %2038
  %2040 = fsub fast half 0xH3C00, %2039
  %2041 = fptrunc float %1809 to half
  %2042 = fptrunc float %1814 to half
  %2043 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %1746) #14
  %2044 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %2043) #14
  %2045 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %2043) #14
  %2046 = fmul fast <3 x half> %2045, splat (half 0xH4A76)
  %2047 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %2045, <3 x half> splat (half 0xH36AA)) #14
  %2048 = fmul fast <3 x half> %2047, splat (half 0xH3C38)
  %2049 = fadd fast <3 x half> %2048, splat (half 0xHAB0A)
  %2050 = fcmp fast ogt <3 x half> %2045, splat (half 0xH1A69)
  %2051 = select fast <3 x i1> %2050, <3 x half> %2049, <3 x half> %2046
  %2052 = fmul fast <3 x half> %2051, %2044
  %2053 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2052) #14
  %2054 = shufflevector <3 x float> %2053, <3 x float> poison, <3 x i32> zeroinitializer
  %2055 = fmul fast <3 x float> %2054, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %2056 = shufflevector <3 x float> %2053, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2057 = fmul fast <3 x float> %2056, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %2058 = fadd fast <3 x float> %2055, %2057
  %2059 = shufflevector <3 x float> %2053, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2060 = fmul fast <3 x float> %2059, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %2061 = fadd fast <3 x float> %2058, %2060
  %2062 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2061) #14
  %2063 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2061) #14
  %2064 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2063, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %2065 = fmul fast <3 x float> %2064, %2062
  %2066 = shufflevector <3 x float> %2065, <3 x float> poison, <3 x i32> zeroinitializer
  %2067 = fmul fast <3 x float> %2066, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %2068 = shufflevector <3 x float> %2065, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2069 = fmul fast <3 x float> %2068, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %2070 = fadd fast <3 x float> %2067, %2069
  %2071 = shufflevector <3 x float> %2065, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2072 = fmul fast <3 x float> %2071, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %2073 = fadd fast <3 x float> %2070, %2072
  %2074 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %2073) #14
  %2075 = extractelement <3 x half> %2074, i64 2
  %2076 = fcmp fast une half %2075, 0xH0000
  %2077 = extractelement <3 x half> %2074, i64 1
  %2078 = fcmp fast une half %2077, 0xH0000
  %2079 = select i1 %2076, i1 true, i1 %2078
  br i1 %2079, label %2080, label %_Z16deRedNeutralOnlyDv3_DhDhDhS_DhDhDh.exit.i

2080:                                             ; preds = %2009
  %2081 = tail call fast half @air.atan2.f16(half %2075, half %2077) #14
  br label %_Z16deRedNeutralOnlyDv3_DhDhDhS_DhDhDh.exit.i

_Z16deRedNeutralOnlyDv3_DhDhDhS_DhDhDh.exit.i:    ; preds = %2080, %2009
  %2082 = phi fast half [ %2081, %2080 ], [ 0xH0000, %2009 ]
  %2083 = fmul fast half %2004, %2004
  %2084 = fmul fast half %2002, %2002
  %2085 = fadd fast half %2083, %2084
  %2086 = tail call fast half @air.sqrt.f16(half %2085) #14
  %2087 = fadd fast half %2086, 0xHB266
  %2088 = fmul fast half %2087, 0xHCD02
  %2089 = tail call fast half @air.clamp.f16(half %2088, half 0xH0000, half 0xH3C00) #14
  %2090 = fmul fast half %2089, %2089
  %2091 = fmul fast half %2089, 0xH4000
  %2092 = fsub fast half 0xH4200, %2091
  %2093 = fmul fast half %2090, %2092
  %2094 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %1746, <3 x half> splat (half 0xH3C00)) #14
  %2095 = fadd fast <3 x half> %2094, splat (half 0xHBC00)
  %2096 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %1746, <3 x half> zeroinitializer) #14
  %2097 = fadd fast half %2082, 0xH4648
  %2098 = tail call fast half @air.sign.f16(half %2082) #14
  %2099 = fpext half %2098 to float
  %2100 = tail call i1 @air.convert.u.i1.f.f32(float %2099) #14
  %2101 = select fast i1 %2100, half %2097, half %2082
  %2102 = tail call fast half @air.fmod.f16(half %2101, half 0xH4648) #14
  %2103 = shufflevector <3 x half> %2074, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %2104 = tail call fast half @air.dot.v2f16(<2 x half> %2103, <2 x half> %2103) #14
  %2105 = tail call fast half @air.sqrt.f16(half %2104) #14
  %2106 = fpext half %2093 to float
  %2107 = fpext half %2102 to float
  %2108 = fadd fast float %2107, 0xBFD3333340000000
  %2109 = tail call fast float @air.fast_fabs.f32(float %2108) #14
  %2110 = fadd fast float %2109, -5.000000e-01
  %2111 = fmul fast float %2110, 0xC001C71C80000000
  %2112 = tail call fast float @air.fast_clamp.f32(float %2111, float 0.000000e+00, float 1.000000e+00) #14
  %2113 = fmul fast float %2112, 2.000000e+00
  %2114 = fsub fast float 3.000000e+00, %2113
  %2115 = fmul fast float %2106, 5.000000e-01
  %2116 = fmul fast float %2112, %2112
  %2117 = fmul fast float %2116, %2115
  %2118 = fmul fast float %2117, %2114
  %2119 = fptrunc float %2118 to half
  %2120 = fmul fast half %2040, %2119
  %2121 = fadd fast half %2120, %2102
  %2122 = fsub fast half 0xH3C00, %2042
  %2123 = fmul fast half %2105, %2122
  %2124 = tail call fast half @air.cos.f16(half %2121) #14
  %2125 = fmul fast half %2124, %2123
  %2126 = tail call fast half @air.sin.f16(half %2121) #14
  %2127 = fmul fast half %2126, %2123
  %2128 = tail call fast half @air.mix.f16(half %2077, half %2125, half %1807) #14
  %2129 = insertelement <3 x half> %2074, half %2128, i64 1
  %2130 = tail call fast half @air.mix.f16(half %2075, half %2127, half %1807) #14
  %2131 = insertelement <3 x half> %2129, half %2130, i64 2
  %2132 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2131) #14
  %2133 = shufflevector <3 x float> %2132, <3 x float> poison, <3 x i32> zeroinitializer
  %2134 = shufflevector <3 x float> %2132, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2135 = fmul fast <3 x float> %2134, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %2136 = fadd fast <3 x float> %2135, %2133
  %2137 = shufflevector <3 x float> %2132, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2138 = fmul fast <3 x float> %2137, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %2139 = fadd fast <3 x float> %2136, %2138
  %2140 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2139) #14
  %2141 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2139) #14
  %2142 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2141, <3 x float> splat (float 0x40029ACA60000000)) #14
  %2143 = fmul fast <3 x float> %2142, %2140
  %2144 = shufflevector <3 x float> %2143, <3 x float> poison, <3 x i32> zeroinitializer
  %2145 = fmul fast <3 x float> %2144, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %2146 = shufflevector <3 x float> %2143, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2147 = fmul fast <3 x float> %2146, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %2148 = fadd fast <3 x float> %2145, %2147
  %2149 = shufflevector <3 x float> %2143, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2150 = fmul fast <3 x float> %2149, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %2151 = fadd fast <3 x float> %2148, %2150
  %2152 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %2151) #14
  %2153 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %2152) #14
  %2154 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %2152) #14
  %2155 = fmul fast <3 x half> %2154, splat (half 0xH2CF4)
  %2156 = fadd fast <3 x half> %2154, splat (half 0xH2B0A)
  %2157 = fmul fast <3 x half> %2156, splat (half 0xH3B96)
  %2158 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %2157, <3 x half> splat (half 0xH40CD)) #14
  %2159 = fcmp fast ogt <3 x half> %2154, splat (half 0xH292D)
  %2160 = select fast <3 x i1> %2159, <3 x half> %2158, <3 x half> %2155
  %2161 = fmul fast <3 x half> %2160, %2153
  %2162 = fadd fast <3 x half> %2095, %2096
  %2163 = fadd fast <3 x half> %2162, %2161
  %2164 = insertelement <3 x half> poison, half %2041, i64 0
  %2165 = shufflevector <3 x half> %2164, <3 x half> poison, <3 x i32> zeroinitializer
  %2166 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %2043, <3 x half> %2163, <3 x half> %2165) #14
  %2167 = fmul fast half %2040, %2028
  %2168 = fadd fast half %2167, %2016
  %2169 = fsub fast float 1.000000e+00, %1814
  %2170 = fpext half %2031 to float
  %2171 = fmul fast float %2169, %2170
  %2172 = tail call fast half @air.cos.f16(half %2168) #14
  %2173 = fpext half %2172 to float
  %2174 = fmul fast float %2171, %2173
  %2175 = fptrunc float %2174 to half
  %2176 = insertelement <3 x half> %1806, half %2175, i64 1
  %2177 = tail call fast half @air.sin.f16(half %2168) #14
  %2178 = fpext half %2177 to float
  %2179 = fmul fast float %2171, %2178
  %2180 = fptrunc float %2179 to half
  %2181 = insertelement <3 x half> %2176, half %2180, i64 2
  br label %2182

2182:                                             ; preds = %_Z16deRedNeutralOnlyDv3_DhDhDhS_DhDhDh.exit.i, %_Z5deRedDv3_DhDhDhS_Dh.exit.i, %1747
  %2183 = phi <3 x half> [ %1806, %1747 ], [ %1806, %_Z5deRedDv3_DhDhDhS_Dh.exit.i ], [ %2181, %_Z16deRedNeutralOnlyDv3_DhDhDhS_DhDhDh.exit.i ]
  %2184 = phi <3 x half> [ %1746, %1747 ], [ %2000, %_Z5deRedDv3_DhDhDhS_Dh.exit.i ], [ %2166, %_Z16deRedNeutralOnlyDv3_DhDhDhS_DhDhDh.exit.i ]
  %2185 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 17
  %2186 = load float, ptr addrspace(1) %2185, align 4, !tbaa !159, !alias.scope !98, !noalias !99
  %2187 = tail call fast float @air.fast_fabs.f32(float %2186) #14
  %2188 = fcmp fast olt float %2187, 0x3EE4F8B580000000
  br i1 %2188, label %2377, label %2189

2189:                                             ; preds = %2182
  %2190 = fptrunc float %2186 to half
  %2191 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %2184) #14
  %2192 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %2191) #14
  %2193 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %2191) #14
  %2194 = fmul fast <3 x half> %2193, splat (half 0xH4A76)
  %2195 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %2193, <3 x half> splat (half 0xH36AA)) #14
  %2196 = fmul fast <3 x half> %2195, splat (half 0xH3C38)
  %2197 = fadd fast <3 x half> %2196, splat (half 0xHAB0A)
  %2198 = fcmp fast ogt <3 x half> %2193, splat (half 0xH1A69)
  %2199 = select fast <3 x i1> %2198, <3 x half> %2197, <3 x half> %2194
  %2200 = fmul fast <3 x half> %2199, %2192
  %2201 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2200) #14
  %2202 = shufflevector <3 x float> %2201, <3 x float> poison, <3 x i32> zeroinitializer
  %2203 = fmul fast <3 x float> %2202, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %2204 = shufflevector <3 x float> %2201, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2205 = fmul fast <3 x float> %2204, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %2206 = fadd fast <3 x float> %2203, %2205
  %2207 = shufflevector <3 x float> %2201, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2208 = fmul fast <3 x float> %2207, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %2209 = fadd fast <3 x float> %2206, %2208
  %2210 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2209) #14
  %2211 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2209) #14
  %2212 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2211, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %2213 = fmul fast <3 x float> %2212, %2210
  %2214 = shufflevector <3 x float> %2213, <3 x float> poison, <3 x i32> zeroinitializer
  %2215 = fmul fast <3 x float> %2214, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %2216 = shufflevector <3 x float> %2213, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2217 = fmul fast <3 x float> %2216, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %2218 = fadd fast <3 x float> %2215, %2217
  %2219 = shufflevector <3 x float> %2213, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2220 = fmul fast <3 x float> %2219, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %2221 = fadd fast <3 x float> %2218, %2220
  %2222 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %2221) #14
  %2223 = extractelement <3 x half> %2222, i64 1
  %2224 = fmul fast half %2223, %2223
  %2225 = extractelement <3 x half> %2222, i64 2
  %2226 = fmul fast half %2225, %2225
  %2227 = fadd fast half %2224, %2226
  %2228 = tail call fast half @air.sqrt.f16(half %2227) #14
  %2229 = fpext half %2228 to float
  %2230 = fcmp fast ogt float %2229, 0x3F50624DE0000000
  br i1 %2230, label %2231, label %2236

2231:                                             ; preds = %2189
  %2232 = fdiv fast half %2223, %2228
  %2233 = insertelement <2 x half> undef, half %2232, i64 0
  %2234 = fdiv fast half %2225, %2228
  %2235 = insertelement <2 x half> %2233, half %2234, i64 1
  br label %2236

2236:                                             ; preds = %2231, %2189
  %2237 = phi fast <2 x half> [ %2235, %2231 ], [ zeroinitializer, %2189 ]
  %2238 = extractelement <3 x half> %2183, i64 1
  %2239 = fmul fast half %2238, %2238
  %2240 = extractelement <3 x half> %2183, i64 2
  %2241 = fmul fast half %2240, %2240
  %2242 = fadd fast half %2239, %2241
  %2243 = tail call fast half @air.sqrt.f16(half %2242) #14
  %2244 = fpext half %2243 to float
  %2245 = fcmp fast ogt float %2244, 0x3F50624DE0000000
  br i1 %2245, label %2246, label %_Z8deYellowDv3_DhDhDhS_Dh.exit.i

2246:                                             ; preds = %2236
  %2247 = fdiv fast half %2238, %2243
  %2248 = insertelement <2 x half> undef, half %2247, i64 0
  %2249 = fdiv fast half %2240, %2243
  %2250 = insertelement <2 x half> %2248, half %2249, i64 1
  br label %_Z8deYellowDv3_DhDhDhS_Dh.exit.i

_Z8deYellowDv3_DhDhDhS_Dh.exit.i:                 ; preds = %2246, %2236
  %2251 = phi fast <2 x half> [ %2250, %2246 ], [ zeroinitializer, %2236 ]
  %2252 = extractelement <2 x half> %2237, i64 0
  %2253 = fmul fast half %2252, 0xH3AEE
  %2254 = extractelement <2 x half> %2237, i64 1
  %2255 = fmul fast half %2254, 0xH3800
  %2256 = fadd fast half %2253, %2255
  %2257 = tail call fast half @air.sqrt.f16(half 0xH3C00) #14
  %2258 = fdiv fast half %2256, %2257
  %2259 = fadd fast half %2258, 0xHBACD
  %2260 = fmul fast half %2259, 0xH4723
  %2261 = tail call fast half @air.clamp.f16(half %2260, half 0xH0000, half 0xH3C00) #14
  %2262 = fmul fast half %2261, %2261
  %2263 = fmul fast half %2261, 0xH4000
  %2264 = fsub fast half 0xH4200, %2263
  %2265 = fmul fast half %2262, %2264
  %2266 = fpext half %2265 to float
  %2267 = fmul fast float %2266, 5.000000e-01
  %2268 = fsub fast float 1.000000e+00, %2267
  %2269 = fadd fast half %2258, 0xHB4CD
  %2270 = fmul fast half %2269, 0xH3F46
  %2271 = tail call fast half @air.clamp.f16(half %2270, half 0xH0000, half 0xH3C00) #14
  %2272 = fmul fast half %2271, %2271
  %2273 = fmul fast half %2271, 0xH4000
  %2274 = fsub fast half 0xH4200, %2273
  %2275 = fmul fast half %2272, %2274
  %2276 = fpext half %2275 to float
  %2277 = fmul fast float %2268, %2276
  %2278 = fptrunc float %2277 to half
  %2279 = fpext half %2278 to float
  %2280 = fmul fast float %2279, 0x3FA47AE140000000
  %2281 = fpext half %2225 to float
  %2282 = fsub fast float %2281, %2280
  %2283 = fptrunc float %2282 to half
  %2284 = insertelement <3 x half> %2222, half %2283, i64 2
  %2285 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2284) #14
  %2286 = shufflevector <3 x float> %2285, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2287 = fmul fast <3 x float> %2286, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %2288 = shufflevector <3 x float> %2285, <3 x float> poison, <3 x i32> zeroinitializer
  %2289 = fadd fast <3 x float> %2287, %2288
  %2290 = shufflevector <3 x float> %2285, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2291 = fmul fast <3 x float> %2290, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %2292 = fadd fast <3 x float> %2289, %2291
  %2293 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2292) #14
  %2294 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2293, <3 x float> splat (float 0x40029ACA60000000)) #14
  %2295 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2292) #14
  %2296 = fmul fast <3 x float> %2295, %2294
  %2297 = shufflevector <3 x float> %2296, <3 x float> poison, <3 x i32> zeroinitializer
  %2298 = fmul fast <3 x float> %2297, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %2299 = shufflevector <3 x float> %2296, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2300 = fmul fast <3 x float> %2299, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %2301 = fadd fast <3 x float> %2298, %2300
  %2302 = shufflevector <3 x float> %2296, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2303 = fmul fast <3 x float> %2302, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %2304 = fadd fast <3 x float> %2301, %2303
  %2305 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %2304) #14
  %2306 = extractelement <3 x half> %2305, i64 1
  %2307 = extractelement <3 x half> %2305, i64 2
  %2308 = fsub fast half %2306, %2307
  %2309 = fmul fast half %2308, 0xH5240
  %2310 = tail call fast half @air.clamp.f16(half %2309, half 0xH0000, half 0xH3C00) #14
  %2311 = fmul fast half %2310, 0xH4000
  %2312 = fsub fast half 0xH4200, %2311
  %2313 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %2184, <3 x half> splat (half 0xH3C00)) #14
  %2314 = fadd fast <3 x half> %2313, splat (half 0xHBC00)
  %2315 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %2184, <3 x half> zeroinitializer) #14
  %2316 = tail call fast half @air.sqrt.f16(half 0xH3132) #14
  %2317 = extractelement <2 x half> %2251, i64 0
  %2318 = fmul fast half %2317, 0xH2A66
  %2319 = extractelement <2 x half> %2251, i64 1
  %2320 = fmul fast half %2319, 0xH3666
  %2321 = fadd fast half %2318, %2320
  %2322 = fdiv fast half %2321, %2316
  %2323 = fadd fast half %2322, 0xHBB33
  %2324 = fmul fast half %2323, 0xH4989
  %2325 = tail call fast half @air.clamp.f16(half %2324, half 0xH0000, half 0xH3C00) #14
  %2326 = fmul fast half %2325, %2325
  %2327 = fmul fast half %2325, 0xH4000
  %2328 = fsub fast half 0xH4200, %2327
  %2329 = fmul fast half %2326, %2328
  %2330 = fpext half %2329 to float
  %2331 = fmul fast float %2330, 0x3FA47AE140000000
  %2332 = fadd fast float %2331, 0x3FA47AE140000000
  %2333 = fptrunc float %2332 to half
  %2334 = fmul fast half %2310, %2310
  %2335 = fmul fast half %2334, %2278
  %2336 = fmul fast half %2335, %2312
  %2337 = fmul fast half %2336, %2333
  %2338 = fsub fast half %2225, %2337
  %2339 = tail call fast half @air.mix.f16(half %2225, half %2338, half %96) #14
  %2340 = insertelement <3 x half> %2222, half %2339, i64 2
  %2341 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2340) #14
  %2342 = shufflevector <3 x float> %2341, <3 x float> poison, <3 x i32> zeroinitializer
  %2343 = shufflevector <3 x float> %2341, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2344 = fmul fast <3 x float> %2343, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %2345 = fadd fast <3 x float> %2344, %2342
  %2346 = shufflevector <3 x float> %2341, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2347 = fmul fast <3 x float> %2346, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %2348 = fadd fast <3 x float> %2345, %2347
  %2349 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2348) #14
  %2350 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2348) #14
  %2351 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2350, <3 x float> splat (float 0x40029ACA60000000)) #14
  %2352 = fmul fast <3 x float> %2351, %2349
  %2353 = shufflevector <3 x float> %2352, <3 x float> poison, <3 x i32> zeroinitializer
  %2354 = fmul fast <3 x float> %2353, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %2355 = shufflevector <3 x float> %2352, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2356 = fmul fast <3 x float> %2355, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %2357 = fadd fast <3 x float> %2354, %2356
  %2358 = shufflevector <3 x float> %2352, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2359 = fmul fast <3 x float> %2358, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %2360 = fadd fast <3 x float> %2357, %2359
  %2361 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %2360) #14
  %2362 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %2361) #14
  %2363 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %2361) #14
  %2364 = fmul fast <3 x half> %2363, splat (half 0xH2CF4)
  %2365 = fadd fast <3 x half> %2363, splat (half 0xH2B0A)
  %2366 = fmul fast <3 x half> %2365, splat (half 0xH3B96)
  %2367 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %2366, <3 x half> splat (half 0xH40CD)) #14
  %2368 = fcmp fast ogt <3 x half> %2363, splat (half 0xH292D)
  %2369 = select fast <3 x i1> %2368, <3 x half> %2367, <3 x half> %2364
  %2370 = fmul fast <3 x half> %2369, %2362
  %2371 = fadd fast <3 x half> %2314, %2315
  %2372 = fadd fast <3 x half> %2371, %2370
  %2373 = insertelement <3 x half> poison, half %2190, i64 0
  %2374 = shufflevector <3 x half> %2373, <3 x half> poison, <3 x i32> zeroinitializer
  %2375 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %2191, <3 x half> %2372, <3 x half> %2374) #14
  %2376 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %2184, <3 x half> %2375, <3 x half> %1227) #14
  br label %2377

2377:                                             ; preds = %_Z8deYellowDv3_DhDhDhS_Dh.exit.i, %2182
  %2378 = phi <3 x half> [ %2184, %2182 ], [ %2376, %_Z8deYellowDv3_DhDhDhS_Dh.exit.i ]
  %2379 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 18
  %2380 = load float, ptr addrspace(1) %2379, align 4, !tbaa !160, !alias.scope !98, !noalias !99
  %2381 = tail call fast float @air.fast_fabs.f32(float %2380) #14
  %2382 = fcmp fast olt float %2381, 0x3EE4F8B580000000
  br i1 %2382, label %_Z29renderNeutralizingAdjustmentsDv3_DhbRU9MTLdevice18SSRCastAdjustmentsDhDhbRU9MTLdevice8SSRStats.exit, label %2383

2383:                                             ; preds = %2377
  %2384 = fptrunc float %2380 to half
  %2385 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %2378) #14
  %2386 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2385) #14
  %2387 = shufflevector <3 x float> %2386, <3 x float> poison, <3 x i32> zeroinitializer
  %2388 = fmul fast <3 x float> %2387, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %2389 = shufflevector <3 x float> %2386, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2390 = fmul fast <3 x float> %2389, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %2391 = fadd fast <3 x float> %2388, %2390
  %2392 = shufflevector <3 x float> %2386, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2393 = fmul fast <3 x float> %2392, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %2394 = fadd fast <3 x float> %2391, %2393
  %2395 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2394) #14
  %2396 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2394) #14
  %2397 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2396, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %2398 = fmul fast <3 x float> %2397, %2395
  %2399 = shufflevector <3 x float> %2398, <3 x float> poison, <3 x i32> zeroinitializer
  %2400 = fmul fast <3 x float> %2399, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %2401 = shufflevector <3 x float> %2398, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2402 = fmul fast <3 x float> %2401, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %2403 = fadd fast <3 x float> %2400, %2402
  %2404 = shufflevector <3 x float> %2398, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2405 = fmul fast <3 x float> %2404, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %2406 = fadd fast <3 x float> %2403, %2405
  %2407 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %2406) #14
  %2408 = extractelement <3 x half> %1775, i64 2
  %2409 = fcmp fast une half %2408, 0xH0000
  %2410 = extractelement <3 x half> %1775, i64 1
  %2411 = fcmp fast une half %2410, 0xH0000
  %2412 = select i1 %2409, i1 true, i1 %2411
  br i1 %2412, label %2413, label %2415

2413:                                             ; preds = %2383
  %2414 = tail call fast half @air.atan2.f16(half %2408, half %2410) #14
  br label %2415

2415:                                             ; preds = %2413, %2383
  %2416 = phi fast half [ %2414, %2413 ], [ 0xH0000, %2383 ]
  %2417 = extractelement <3 x half> %2407, i64 2
  %2418 = fcmp fast une half %2417, 0xH0000
  %2419 = extractelement <3 x half> %2407, i64 1
  %2420 = fcmp fast une half %2419, 0xH0000
  %2421 = select i1 %2418, i1 true, i1 %2420
  br i1 %2421, label %2422, label %2424

2422:                                             ; preds = %2415
  %2423 = tail call fast half @air.atan2.f16(half %2417, half %2419) #14
  br label %2424

2424:                                             ; preds = %2422, %2415
  %2425 = phi fast half [ %2423, %2422 ], [ 0xH0000, %2415 ]
  %2426 = fmul fast half %2419, %2419
  %2427 = fmul fast half %2417, %2417
  %2428 = fadd fast half %2426, %2427
  %2429 = tail call fast half @air.sqrt.f16(half %2428) #14
  %2430 = fpext half %2429 to float
  %2431 = fcmp fast ogt float %2430, 0x3F50624DE0000000
  br i1 %2431, label %2432, label %_Z16skinWarmthFilterDv3_DhDhDhS_DhDh.exit.i

2432:                                             ; preds = %2424
  %2433 = fdiv fast half %2419, %2429
  %2434 = insertelement <2 x half> undef, half %2433, i64 0
  %2435 = fdiv fast half %2417, %2429
  %2436 = insertelement <2 x half> %2434, half %2435, i64 1
  br label %_Z16skinWarmthFilterDv3_DhDhDhS_DhDh.exit.i

_Z16skinWarmthFilterDv3_DhDhDhS_DhDh.exit.i:      ; preds = %2432, %2424
  %2437 = phi fast <2 x half> [ %2436, %2432 ], [ zeroinitializer, %2424 ]
  %2438 = fmul fast half %2410, %2410
  %2439 = fmul fast half %2408, %2408
  %2440 = fadd fast half %2438, %2439
  %2441 = tail call fast half @air.sqrt.f16(half %2440) #14
  %2442 = extractelement <2 x half> %2437, i64 0
  %2443 = fmul fast half %2442, 0xH3AEE
  %2444 = extractelement <2 x half> %2437, i64 1
  %2445 = fmul fast half %2444, 0xH3800
  %2446 = fadd fast half %2443, %2445
  %2447 = tail call fast half @air.sqrt.f16(half 0xH3C00) #14
  %2448 = fdiv fast half %2446, %2447
  %2449 = fadd fast half %2448, 0xHBACD
  %2450 = fmul fast half %2449, 0xH4723
  %2451 = tail call fast half @air.clamp.f16(half %2450, half 0xH0000, half 0xH3C00) #14
  %2452 = fmul fast half %2451, %2451
  %2453 = fmul fast half %2451, 0xH4000
  %2454 = fsub fast half 0xH4200, %2453
  %2455 = fmul fast half %2452, %2454
  %2456 = fpext half %2455 to float
  %2457 = fmul fast float %2456, 5.000000e-01
  %2458 = fsub fast float 1.000000e+00, %2457
  %2459 = fadd fast half %2448, 0xH2E66
  %2460 = fmul fast half %2459, 0xH3EAA
  %2461 = tail call fast half @air.clamp.f16(half %2460, half 0xH0000, half 0xH3C00) #14
  %2462 = fmul fast half %2461, %2461
  %2463 = fmul fast half %2461, 0xH4000
  %2464 = fsub fast half 0xH4200, %2463
  %2465 = fmul fast half %2462, %2464
  %2466 = fpext half %2465 to float
  %2467 = fmul fast float %2458, %2466
  %2468 = fptrunc float %2467 to half
  %2469 = tail call fast half @air.sign.f16(half %2425) #14
  %2470 = fpext half %2469 to float
  %2471 = tail call i1 @air.convert.u.i1.f.f32(float %2470) #14
  %2472 = fadd fast half %2425, 0xH4648
  %2473 = select fast i1 %2471, half %2472, half %2425
  %2474 = tail call fast half @air.fmod.f16(half %2473, half 0xH4648) #14
  %2475 = fpext half %2474 to float
  %2476 = fadd fast float %2475, 0xBFE226C3C0000000
  %2477 = tail call fast float @air.fast_fabs.f32(float %2476) #14
  %2478 = fadd fast float %2477, 0xBFE3333340000000
  %2479 = fmul fast float %2478, 0xC00AAAAAA0000000
  %2480 = tail call fast float @air.fast_clamp.f32(float %2479, float 0.000000e+00, float 1.000000e+00) #14
  %2481 = fmul fast float %2480, 2.000000e+00
  %2482 = fsub fast float 3.000000e+00, %2481
  %2483 = tail call fast half @air.sign.f16(half %2416) #14
  %2484 = fpext half %2483 to float
  %2485 = tail call i1 @air.convert.u.i1.f.f32(float %2484) #14
  %2486 = fadd fast half %2416, 0xH4648
  %2487 = select fast i1 %2485, half %2486, half %2416
  %2488 = tail call fast half @air.fmod.f16(half %2487, half 0xH4648) #14
  %2489 = fpext half %2488 to float
  %2490 = fadd fast float %2489, 0xBFE226C3C0000000
  %2491 = tail call fast float @air.fast_fabs.f32(float %2490) #14
  %2492 = fadd fast float %2491, 0xBFE3333340000000
  %2493 = fmul fast float %2492, 0xC00AAAAAA0000000
  %2494 = tail call fast float @air.fast_clamp.f32(float %2493, float 0.000000e+00, float 1.000000e+00) #14
  %2495 = fmul fast float %2494, 2.000000e+00
  %2496 = fsub fast float 3.000000e+00, %2495
  %2497 = fmul fast float %2494, %2480
  %2498 = fmul fast float %2430, 0x3FA99999A0000000
  %2499 = fmul fast float %2498, %2482
  %2500 = fmul fast float %2497, %2497
  %2501 = fmul fast float %2500, %2499
  %2502 = fmul fast float %2501, %2496
  %2503 = fadd fast float %2502, %2430
  %2504 = fptrunc float %2503 to half
  %2505 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %2378, <3 x half> splat (half 0xH3C00)) #14
  %2506 = fadd fast <3 x half> %2505, splat (half 0xHBC00)
  %2507 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %2378, <3 x half> zeroinitializer) #14
  %2508 = fmul fast half %2468, 0xH27AE
  %2509 = fadd fast half %2508, %2419
  %2510 = fadd fast half %2508, %2417
  %2511 = tail call fast half @air.cos.f16(half %2474) #14
  %2512 = fmul fast half %2511, %2504
  %2513 = tail call fast half @air.mix.f16(half %2512, half %2509, half %1807) #14
  %2514 = insertelement <2 x half> undef, half %2513, i64 0
  %2515 = tail call fast half @air.sin.f16(half %2474) #14
  %2516 = fmul fast half %2515, %2504
  %2517 = tail call fast half @air.mix.f16(half %2516, half %2510, half %1807) #14
  %2518 = insertelement <2 x half> %2514, half %2517, i64 1
  %2519 = fadd fast half %2441, 0xHADC3
  %2520 = fmul fast half %2519, 0xH488C
  %2521 = tail call fast half @air.clamp.f16(half %2520, half 0xH0000, half 0xH3C00) #14
  %2522 = fmul fast half %2521, %2521
  %2523 = fmul fast half %2521, 0xH4000
  %2524 = fsub fast half 0xH4200, %2523
  %2525 = fmul fast half %2522, %2524
  %2526 = fsub fast half 0xH3C00, %96
  %2527 = insertelement <2 x half> poison, half %2526, i64 0
  %2528 = fsub fast half 0xH3C00, %2525
  %2529 = fpext half %2528 to float
  %2530 = fmul fast float %2529, 0x3FB99999A0000000
  %2531 = fadd fast float %2530, 1.000000e+00
  %2532 = fptrunc float %2531 to half
  %2533 = insertelement <2 x half> poison, half %2532, i64 0
  %2534 = insertelement <2 x half> poison, half %96, i64 0
  %2535 = fmul fast <2 x half> %2533, %2534
  %2536 = fadd fast <2 x half> %2535, %2527
  %2537 = shufflevector <2 x half> %2536, <2 x half> poison, <2 x i32> zeroinitializer
  %2538 = fmul fast <2 x half> %2537, %2518
  %2539 = shufflevector <2 x half> %2538, <2 x half> poison, <3 x i32> <i32 0, i32 1, i32 poison>
  %2540 = shufflevector <3 x half> %2407, <3 x half> %2539, <3 x i32> <i32 0, i32 3, i32 4>
  %2541 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2540) #14
  %2542 = shufflevector <3 x float> %2541, <3 x float> poison, <3 x i32> zeroinitializer
  %2543 = shufflevector <3 x float> %2541, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2544 = fmul fast <3 x float> %2543, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %2545 = fadd fast <3 x float> %2544, %2542
  %2546 = shufflevector <3 x float> %2541, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2547 = fmul fast <3 x float> %2546, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %2548 = fadd fast <3 x float> %2545, %2547
  %2549 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2548) #14
  %2550 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2548) #14
  %2551 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2550, <3 x float> splat (float 0x40029ACA60000000)) #14
  %2552 = fmul fast <3 x float> %2551, %2549
  %2553 = shufflevector <3 x float> %2552, <3 x float> poison, <3 x i32> zeroinitializer
  %2554 = fmul fast <3 x float> %2553, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %2555 = shufflevector <3 x float> %2552, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2556 = fmul fast <3 x float> %2555, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %2557 = fadd fast <3 x float> %2554, %2556
  %2558 = shufflevector <3 x float> %2552, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2559 = fmul fast <3 x float> %2558, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %2560 = fadd fast <3 x float> %2557, %2559
  %2561 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %2560) #14
  %2562 = insertelement <3 x half> poison, half %2384, i64 0
  %2563 = shufflevector <3 x half> %2562, <3 x half> poison, <3 x i32> zeroinitializer
  %2564 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %2385, <3 x half> %2561, <3 x half> %2563) #14
  %2565 = fadd fast <3 x half> %2506, %2507
  %2566 = fadd fast <3 x half> %2565, %2564
  br label %_Z29renderNeutralizingAdjustmentsDv3_DhbRU9MTLdevice18SSRCastAdjustmentsDhDhbRU9MTLdevice8SSRStats.exit

_Z29renderNeutralizingAdjustmentsDv3_DhbRU9MTLdevice18SSRCastAdjustmentsDhDhbRU9MTLdevice8SSRStats.exit: ; preds = %_Z16skinWarmthFilterDv3_DhDhDhS_DhDh.exit.i, %2377, %_Z23renderBrightAndContrastDv3_DhS_DhDhDhRU9MTLdevice8SSRStats.exit
  %2567 = phi <3 x half> [ %1746, %_Z23renderBrightAndContrastDv3_DhS_DhDhDhRU9MTLdevice8SSRStats.exit ], [ %2378, %2377 ], [ %2566, %_Z16skinWarmthFilterDv3_DhDhDhS_DhDh.exit.i ]
  %2568 = bitcast ptr %24 to ptr
  call void @llvm.lifetime.start.p0(ptr %24)
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 8 dereferenceable(24) %2568, i8 0, i64 24, i1 false) #19
  br label %2579

2569:                                             ; preds = %2579
  %2570 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 0
  %2571 = load float, ptr addrspace(1) %2570, align 4, !tbaa !161, !alias.scope !98, !noalias !99
  %2572 = fmul fast float %2571, 5.000000e-01
  %2573 = fadd fast float %2572, 5.000000e-01
  %2574 = fptrunc float %2573 to half
  %2575 = fpext half %2574 to float
  %2576 = fadd fast float %2575, -5.000000e-01
  %2577 = tail call fast float @air.fast_fabs.f32(float %2576) #14
  %2578 = fcmp fast olt float %2577, 0x3EE4F8B580000000
  br i1 %2578, label %2648, label %2599

2579:                                             ; preds = %2579, %_Z29renderNeutralizingAdjustmentsDv3_DhbRU9MTLdevice18SSRCastAdjustmentsDhDhbRU9MTLdevice8SSRStats.exit
  %2580 = phi i32 [ 0, %_Z29renderNeutralizingAdjustmentsDv3_DhbRU9MTLdevice18SSRCastAdjustmentsDhDhbRU9MTLdevice8SSRStats.exit ], [ %2597, %2579 ]
  %2581 = zext i32 %2580 to i64
  %2582 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 6, i64 %2581
  %2583 = load float, ptr addrspace(1) %2582, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %2584 = fptrunc float %2583 to half
  %2585 = insertelement <3 x half> undef, half %2584, i64 0
  %2586 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 7, i64 %2581
  %2587 = load float, ptr addrspace(1) %2586, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %2588 = fmul fast float %2587, %2587
  %2589 = fmul fast float %2588, 0x3EF02E85C0000000
  %2590 = fptrunc float %2589 to half
  %2591 = insertelement <3 x half> %2585, half %2590, i64 1
  %2592 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 8, i64 %2581
  %2593 = load float, ptr addrspace(1) %2592, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %2594 = fptrunc float %2593 to half
  %2595 = insertelement <3 x half> %2591, half %2594, i64 2
  %2596 = getelementptr inbounds %"struct.metal::matrix.194", ptr %24, i64 0, i32 0, i64 %2581
  store <3 x half> %2595, ptr %2596, align 8, !tbaa !162
  %2597 = add nuw nsw i32 %2580, 1
  %2598 = icmp eq i32 %2597, 3
  br i1 %2598, label %2569, label %2579, !llvm.loop !164

2599:                                             ; preds = %2569
  %2600 = getelementptr inbounds %"struct.metal::matrix.194", ptr %24, i64 0, i32 0, i64 0
  %2601 = load <3 x half>, ptr %2600, align 8, !tbaa.struct !166
  %2602 = getelementptr inbounds %"struct.metal::matrix.194", ptr %24, i64 0, i32 0, i64 1
  %2603 = load <3 x half>, ptr %2602, align 8, !tbaa.struct !167
  %2604 = getelementptr inbounds %"struct.metal::matrix.194", ptr %24, i64 0, i32 0, i64 2
  %2605 = load <3 x half>, ptr %2604, align 8, !tbaa.struct !168
  %2606 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 2
  %2607 = load float, ptr addrspace(1) %2606, align 4, !tbaa !169, !alias.scope !98, !noalias !99
  %2608 = fptrunc float %2607 to half
  %2609 = fsub fast half 0xH3C00, %2574
  %2610 = fpext half %2609 to float
  %2611 = fsub fast float %2575, %2610
  %2612 = fmul fast float %2611, 0x3FC99999A0000000
  %2613 = fptrunc float %2612 to half
  %2614 = fmul fast float %2575, 0x3F8EB851E0000000
  %2615 = fmul fast float %2610, 0x3FA99999A0000000
  %2616 = fsub fast float %2615, %2614
  %2617 = fptrunc float %2616 to half
  %2618 = fmul fast float %2575, 0x3FA1EB8520000000
  %2619 = fadd fast float %2615, %2618
  %2620 = fptrunc float %2619 to half
  %2621 = tail call fast half @air.fabs.f16(half %2608) #14
  %2622 = fpext half %2621 to float
  %2623 = fcmp fast olt float %2622, 0x3EE4F8B580000000
  br i1 %2623, label %2636, label %2624

2624:                                             ; preds = %2599
  %2625 = fmul fast half %2608, 0xH4248
  %2626 = tail call fast half @air.cos.f16(half %2625) #14
  %2627 = fmul fast half %2626, %2613
  %2628 = tail call fast half @air.sin.f16(half %2625) #14
  %2629 = fmul fast half %2628, %2617
  %2630 = fsub fast half %2627, %2629
  %2631 = fmul fast half %2630, %2628
  %2632 = fmul fast half %2626, %2617
  %2633 = fadd fast half %2631, %2632
  %2634 = fmul fast half %2626, %2620
  %2635 = fadd fast half %2631, %2634
  br label %2636

2636:                                             ; preds = %2624, %2599
  %2637 = phi half [ %2620, %2599 ], [ %2635, %2624 ]
  %2638 = phi half [ %2617, %2599 ], [ %2633, %2624 ]
  %2639 = phi half [ %2613, %2599 ], [ %2630, %2624 ]
  %2640 = fcmp fast ogt half %2574, 0xH3800
  %2641 = select i1 %2640, half 0xH3548, half 0xH3800
  %2642 = insertelement <4 x half> undef, half %2639, i64 0
  %2643 = insertelement <4 x half> %2642, half %2638, i64 1
  %2644 = insertelement <4 x half> %2643, half %2637, i64 2
  %2645 = insertelement <4 x half> %2644, half %2641, i64 3
  %2646 = tail call fast fastcc <3 x half> @_Z17protectMaskFilterDv3_DhS_S_S_b(<3 x half> noundef %2567, <3 x half> noundef %2601, <3 x half> noundef %2603, <3 x half> noundef %2605, i1 noundef zeroext false) #17
  %2647 = tail call fast fastcc <3 x half> @_Z12warmthFilterDv3_DhS_Dv4_Dh(<3 x half> noundef %2567, <3 x half> noundef %2646, <4 x half> noundef %2645) #17
  br label %2648

2648:                                             ; preds = %2636, %2569
  %2649 = phi <3 x half> [ %2567, %2569 ], [ %2647, %2636 ]
  %2650 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 1
  %2651 = load float, ptr addrspace(1) %2650, align 4, !tbaa !170, !alias.scope !98, !noalias !99
  %2652 = fmul fast float %2651, 5.000000e-01
  %2653 = fadd fast float %2652, 5.000000e-01
  %2654 = fptrunc float %2653 to half
  %2655 = fpext half %2654 to float
  %2656 = fadd fast float %2655, -5.000000e-01
  %2657 = tail call fast float @air.fast_fabs.f32(float %2656) #14
  %2658 = fcmp fast olt float %2657, 0x3EE4F8B580000000
  br i1 %2658, label %2843, label %2659

2659:                                             ; preds = %2648
  %2660 = getelementptr inbounds %"struct.metal::matrix.194", ptr %24, i64 0, i32 0, i64 0
  %2661 = load <3 x half>, ptr %2660, align 8, !tbaa.struct !166
  %2662 = getelementptr inbounds %"struct.metal::matrix.194", ptr %24, i64 0, i32 0, i64 1
  %2663 = load <3 x half>, ptr %2662, align 8, !tbaa.struct !167
  %2664 = getelementptr inbounds %"struct.metal::matrix.194", ptr %24, i64 0, i32 0, i64 2
  %2665 = load <3 x half>, ptr %2664, align 8, !tbaa.struct !168
  %2666 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 3
  %2667 = load float, ptr addrspace(1) %2666, align 4, !tbaa !171, !alias.scope !98, !noalias !99
  %2668 = fptrunc float %2667 to half
  %2669 = fcmp fast olt half %2654, 0xH3800
  br i1 %2669, label %2670, label %2676

2670:                                             ; preds = %2659
  %2671 = fmul fast half %2654, 0xH4000
  %2672 = fsub fast half 0xH3C00, %2671
  %2673 = fpext half %2672 to float
  %2674 = fmul fast float %2673, 0xBFB99999A0000000
  %2675 = fmul fast float %2673, 0xBFC872B020000000
  br label %2682

2676:                                             ; preds = %2659
  %2677 = fmul fast float %2656, 2.000000e+00
  %2678 = fptrunc float %2677 to half
  %2679 = fpext half %2678 to float
  %2680 = fmul fast float %2679, 0x3FC9FBE760000000
  %2681 = fmul fast float %2679, 0x3FCB573EA0000000
  br label %2682

2682:                                             ; preds = %2676, %2670
  %.in.i = phi float [ %2675, %2670 ], [ %2681, %2676 ]
  %.in1.i = phi float [ %2674, %2670 ], [ %2680, %2676 ]
  %2683 = fptrunc float %.in1.i to half
  %2684 = fptrunc float %.in.i to half
  %2685 = tail call fast half @air.fabs.f16(half %2668) #14
  %2686 = fpext half %2685 to float
  %2687 = fcmp fast olt float %2686, 0x3EE4F8B580000000
  br i1 %2687, label %2698, label %2688

2688:                                             ; preds = %2682
  %2689 = fmul fast half %2668, 0xHC248
  %2690 = tail call fast half @air.cos.f16(half %2689) #14
  %2691 = fmul fast half %2690, %2683
  %2692 = tail call fast half @air.sin.f16(half %2689) #14
  %2693 = fmul fast half %2692, %2684
  %2694 = fsub fast half %2691, %2693
  %2695 = fmul fast half %2694, %2692
  %2696 = fmul fast half %2690, %2684
  %2697 = fadd fast half %2695, %2696
  br label %2698

2698:                                             ; preds = %2688, %2682
  %2699 = phi half [ %2684, %2682 ], [ %2697, %2688 ]
  %2700 = phi half [ %2683, %2682 ], [ %2694, %2688 ]
  %2701 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2567) #14
  %2702 = shufflevector <3 x float> %2701, <3 x float> poison, <3 x i32> zeroinitializer
  %2703 = fmul fast <3 x float> %2702, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %2704 = shufflevector <3 x float> %2701, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2705 = fmul fast <3 x float> %2704, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %2706 = fadd fast <3 x float> %2703, %2705
  %2707 = shufflevector <3 x float> %2701, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2708 = fmul fast <3 x float> %2707, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %2709 = fadd fast <3 x float> %2706, %2708
  %2710 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2709) #14
  %2711 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2709) #14
  %2712 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2711, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %2713 = fmul fast <3 x float> %2712, %2710
  %2714 = shufflevector <3 x float> %2713, <3 x float> poison, <3 x i32> zeroinitializer
  %2715 = fmul fast <3 x float> %2714, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %2716 = shufflevector <3 x float> %2713, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2717 = fmul fast <3 x float> %2716, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %2718 = fadd fast <3 x float> %2715, %2717
  %2719 = shufflevector <3 x float> %2713, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2720 = fmul fast <3 x float> %2719, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %2721 = fadd fast <3 x float> %2718, %2720
  %2722 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %2721) #14
  %2723 = extractelement <3 x half> %2722, i64 2
  %2724 = fcmp fast une half %2723, 0xH0000
  %2725 = extractelement <3 x half> %2722, i64 1
  %2726 = fcmp fast une half %2725, 0xH0000
  %2727 = select i1 %2724, i1 true, i1 %2726
  br i1 %2727, label %2728, label %2731

2728:                                             ; preds = %2698
  %2729 = tail call fast half @air.atan2.f16(half %2723, half %2725) #14
  %2730 = fadd fast half %2729, 0xH3F9A
  br label %2731

2731:                                             ; preds = %2728, %2698
  %2732 = phi half [ %2730, %2728 ], [ 0xH3F9A, %2698 ]
  %2733 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %2567) #14
  %2734 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2733) #14
  %2735 = shufflevector <3 x float> %2734, <3 x float> poison, <3 x i32> zeroinitializer
  %2736 = fmul fast <3 x float> %2735, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %2737 = shufflevector <3 x float> %2734, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2738 = fmul fast <3 x float> %2737, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %2739 = fadd fast <3 x float> %2736, %2738
  %2740 = shufflevector <3 x float> %2734, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2741 = fmul fast <3 x float> %2740, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %2742 = fadd fast <3 x float> %2739, %2741
  %2743 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2742) #14
  %2744 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2742) #14
  %2745 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2744, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %2746 = fmul fast <3 x float> %2745, %2743
  %2747 = shufflevector <3 x float> %2746, <3 x float> poison, <3 x i32> zeroinitializer
  %2748 = fmul fast <3 x float> %2747, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %2749 = shufflevector <3 x float> %2746, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2750 = fmul fast <3 x float> %2749, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %2751 = fadd fast <3 x float> %2748, %2750
  %2752 = shufflevector <3 x float> %2746, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2753 = fmul fast <3 x float> %2752, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %2754 = fadd fast <3 x float> %2751, %2753
  %2755 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %2754) #14
  %2756 = extractelement <3 x half> %2755, i64 2
  %2757 = fcmp fast une half %2756, 0xH0000
  %2758 = extractelement <3 x half> %2755, i64 1
  %2759 = fcmp fast une half %2758, 0xH0000
  %2760 = select i1 %2757, i1 true, i1 %2759
  br i1 %2760, label %2761, label %_Z29whiteBalanceFilterAdjustmentsDv3_DhN5metal6matrixIDhLi3ELi3EvEERU9MTLdevice18SSRCastAdjustmentsDhDh.exit.i

2761:                                             ; preds = %2731
  %2762 = tail call fast half @air.atan2.f16(half %2756, half %2758) #14
  br label %_Z29whiteBalanceFilterAdjustmentsDv3_DhN5metal6matrixIDhLi3ELi3EvEERU9MTLdevice18SSRCastAdjustmentsDhDh.exit.i

_Z29whiteBalanceFilterAdjustmentsDv3_DhN5metal6matrixIDhLi3ELi3EvEERU9MTLdevice18SSRCastAdjustmentsDhDh.exit.i: ; preds = %2761, %2731
  %2763 = phi fast half [ %2762, %2761 ], [ 0xH0000, %2731 ]
  %2764 = fmul fast half %2732, %2732
  %2765 = fmul fast half %2764, 0xHBF1C
  %2766 = tail call fast half @air.exp.f16(half %2765) #14
  %2767 = insertelement <3 x half> poison, half %2766, i64 0
  %2768 = shufflevector <3 x half> %2767, <3 x half> poison, <3 x i32> zeroinitializer
  %2769 = insertelement <2 x half> undef, half %2700, i64 0
  %2770 = insertelement <2 x half> %2769, half %2699, i64 1
  %2771 = extractelement <3 x half> %2755, i64 0
  %2772 = fmul fast half %2771, %2771
  %2773 = insertelement <2 x half> poison, half %2772, i64 0
  %2774 = shufflevector <2 x half> %2773, <2 x half> poison, <2 x i32> zeroinitializer
  %2775 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> zeroinitializer, <2 x half> %2770, <2 x half> %2774) #14
  %2776 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %2567, <3 x half> splat (half 0xH3C00)) #14
  %2777 = fadd fast <3 x half> %2776, splat (half 0xHBC00)
  %2778 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %2567, <3 x half> zeroinitializer) #14
  %2779 = extractelement <3 x half> %2661, i64 1
  %2780 = tail call fast half @air.fmax.f16(half %2779, half 0xH0001) #14
  %2781 = extractelement <3 x half> %2663, i64 1
  %2782 = tail call fast half @air.fmax.f16(half %2781, half 0xH0001) #14
  %2783 = extractelement <3 x half> %2665, i64 1
  %2784 = tail call fast half @air.fmax.f16(half %2783, half 0xH0001) #14
  %2785 = extractelement <3 x half> %2661, i64 2
  %2786 = extractelement <3 x half> %2661, i64 0
  %2787 = fsub fast half %2763, %2786
  %2788 = fneg fast half %2787
  %2789 = fmul fast half %2787, %2788
  %2790 = fdiv fast half %2789, %2780
  %2791 = tail call fast half @air.exp.f16(half %2790) #14
  %2792 = fmul fast half %2791, %2785
  %2793 = extractelement <3 x half> %2663, i64 2
  %2794 = extractelement <3 x half> %2663, i64 0
  %2795 = fsub fast half %2763, %2794
  %2796 = fneg fast half %2795
  %2797 = fmul fast half %2795, %2796
  %2798 = fdiv fast half %2797, %2782
  %2799 = tail call fast half @air.exp.f16(half %2798) #14
  %2800 = fmul fast half %2799, %2793
  %2801 = extractelement <3 x half> %2665, i64 2
  %2802 = extractelement <3 x half> %2665, i64 0
  %2803 = fsub fast half %2763, %2802
  %2804 = fneg fast half %2803
  %2805 = fmul fast half %2803, %2804
  %2806 = fdiv fast half %2805, %2784
  %2807 = tail call fast half @air.exp.f16(half %2806) #14
  %2808 = fmul fast half %2807, %2801
  %2809 = fadd fast half %2800, %2792
  %2810 = fadd fast half %2809, %2808
  %2811 = insertelement <2 x half> poison, half %2810, i64 0
  %2812 = shufflevector <2 x half> %2811, <2 x half> poison, <2 x i32> zeroinitializer
  %2813 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %2775, <2 x half> zeroinitializer, <2 x half> %2812) #14
  %2814 = shufflevector <3 x half> %2755, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %2815 = fadd fast <2 x half> %2813, %2814
  %2816 = shufflevector <2 x half> %2815, <2 x half> poison, <3 x i32> <i32 0, i32 1, i32 poison>
  %2817 = shufflevector <3 x half> %2755, <3 x half> %2816, <3 x i32> <i32 0, i32 3, i32 4>
  %2818 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2817) #14
  %2819 = shufflevector <3 x float> %2818, <3 x float> poison, <3 x i32> zeroinitializer
  %2820 = shufflevector <3 x float> %2818, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2821 = fmul fast <3 x float> %2820, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %2822 = fadd fast <3 x float> %2821, %2819
  %2823 = shufflevector <3 x float> %2818, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2824 = fmul fast <3 x float> %2823, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %2825 = fadd fast <3 x float> %2822, %2824
  %2826 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2825) #14
  %2827 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2825) #14
  %2828 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2827, <3 x float> splat (float 0x40029ACA60000000)) #14
  %2829 = fmul fast <3 x float> %2828, %2826
  %2830 = shufflevector <3 x float> %2829, <3 x float> poison, <3 x i32> zeroinitializer
  %2831 = fmul fast <3 x float> %2830, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %2832 = shufflevector <3 x float> %2829, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2833 = fmul fast <3 x float> %2832, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %2834 = fadd fast <3 x float> %2831, %2833
  %2835 = shufflevector <3 x float> %2829, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2836 = fmul fast <3 x float> %2835, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %2837 = fadd fast <3 x float> %2834, %2836
  %2838 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %2837) #14
  %2839 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %2838, <3 x half> %2733, <3 x half> %2768) #14
  %2840 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %2839) #14
  %2841 = fadd fast <3 x half> %2777, %2778
  %2842 = fadd fast <3 x half> %2841, %2840
  br label %2843

2843:                                             ; preds = %_Z29whiteBalanceFilterAdjustmentsDv3_DhN5metal6matrixIDhLi3ELi3EvEERU9MTLdevice18SSRCastAdjustmentsDhDh.exit.i, %2648
  %2844 = phi <3 x half> [ %2567, %2648 ], [ %2842, %_Z29whiteBalanceFilterAdjustmentsDv3_DhN5metal6matrixIDhLi3ELi3EvEERU9MTLdevice18SSRCastAdjustmentsDhDh.exit.i ]
  %2845 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 4
  %2846 = load float, ptr addrspace(1) %2845, align 4, !tbaa !172, !alias.scope !98, !noalias !99
  %2847 = fmul fast float %2846, 5.000000e-01
  %2848 = fadd fast float %2847, 5.000000e-01
  %2849 = fptrunc float %2848 to half
  %2850 = fpext half %2849 to float
  %2851 = fadd fast float %2850, -5.000000e-01
  %2852 = tail call fast float @air.fast_fabs.f32(float %2851) #14
  %2853 = fcmp fast olt float %2852, 0x3EE4F8B580000000
  br i1 %2853, label %_Z27renderWarmthCastAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsDh.exit, label %2854

2854:                                             ; preds = %2843
  %2855 = getelementptr inbounds %"struct.metal::matrix.194", ptr %24, i64 0, i32 0, i64 0
  %2856 = load <3 x half>, ptr %2855, align 8, !tbaa.struct !166
  %2857 = getelementptr inbounds %"struct.metal::matrix.194", ptr %24, i64 0, i32 0, i64 1
  %2858 = load <3 x half>, ptr %2857, align 8, !tbaa.struct !167
  %2859 = getelementptr inbounds %"struct.metal::matrix.194", ptr %24, i64 0, i32 0, i64 2
  %2860 = load <3 x half>, ptr %2859, align 8, !tbaa.struct !168
  %2861 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 5
  %2862 = load float, ptr addrspace(1) %2861, align 4, !tbaa !173, !alias.scope !98, !noalias !99
  %2863 = fptrunc float %2862 to half
  %2864 = fsub fast half 0xH3C00, %2849
  %2865 = fpext half %2864 to float
  %2866 = fsub fast float %2850, %2865
  %2867 = fmul fast float %2866, 0x3FC99999A0000000
  %2868 = fptrunc float %2867 to half
  %2869 = fmul fast float %2850, 0x3F8EB851E0000000
  %2870 = fmul fast float %2865, 0x3FA99999A0000000
  %2871 = fsub fast float %2870, %2869
  %2872 = fptrunc float %2871 to half
  %2873 = fmul fast float %2850, 0x3FA1EB8520000000
  %2874 = fadd fast float %2870, %2873
  %2875 = fptrunc float %2874 to half
  %2876 = tail call fast half @air.fabs.f16(half %2863) #14
  %2877 = fpext half %2876 to float
  %2878 = fcmp fast olt float %2877, 0x3EE4F8B580000000
  br i1 %2878, label %2891, label %2879

2879:                                             ; preds = %2854
  %2880 = fmul fast half %2863, 0xH4248
  %2881 = tail call fast half @air.cos.f16(half %2880) #14
  %2882 = fmul fast half %2881, %2868
  %2883 = tail call fast half @air.sin.f16(half %2880) #14
  %2884 = fmul fast half %2883, %2872
  %2885 = fsub fast half %2882, %2884
  %2886 = fmul fast half %2885, %2883
  %2887 = fmul fast half %2881, %2872
  %2888 = fadd fast half %2886, %2887
  %2889 = fmul fast half %2881, %2875
  %2890 = fadd fast half %2886, %2889
  br label %2891

2891:                                             ; preds = %2879, %2854
  %2892 = phi half [ %2875, %2854 ], [ %2890, %2879 ]
  %2893 = phi half [ %2872, %2854 ], [ %2888, %2879 ]
  %2894 = phi half [ %2868, %2854 ], [ %2885, %2879 ]
  %2895 = fcmp fast ogt half %2849, 0xH3800
  %2896 = select i1 %2895, half 0xH3548, half 0xH3800
  %2897 = insertelement <4 x half> undef, half %2894, i64 0
  %2898 = insertelement <4 x half> %2897, half %2893, i64 1
  %2899 = insertelement <4 x half> %2898, half %2892, i64 2
  %2900 = insertelement <4 x half> %2899, half %2896, i64 3
  %2901 = tail call fast fastcc <3 x half> @_Z17protectMaskFilterDv3_DhS_S_S_b(<3 x half> noundef %2844, <3 x half> noundef %2856, <3 x half> noundef %2858, <3 x half> noundef %2860, i1 noundef zeroext false) #17
  %2902 = tail call fast fastcc <3 x half> @_Z12warmthFilterDv3_DhS_Dv4_Dh(<3 x half> noundef %2844, <3 x half> noundef %2901, <4 x half> noundef %2900) #17
  br label %_Z27renderWarmthCastAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsDh.exit

_Z27renderWarmthCastAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsDh.exit: ; preds = %2891, %2843
  %2903 = phi <3 x half> [ %2844, %2843 ], [ %2902, %2891 ]
  %2904 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %2649, <3 x half> %2903, <3 x half> %1227) #14
  call void @llvm.lifetime.end.p0(ptr %24)
  %2905 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 11, i32 3
  %2906 = load float, ptr addrspace(1) %2905, align 4, !tbaa !174, !alias.scope !98, !noalias !99
  %2907 = fptrunc float %2906 to half
  %2908 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 9
  %2909 = load float, ptr addrspace(1) %2908, align 4, !tbaa !175, !alias.scope !98, !noalias !99
  %2910 = tail call i1 @air.convert.u.i1.f.f32(float %2909) #14
  br i1 %2910, label %2911, label %2958

2911:                                             ; preds = %_Z27renderWarmthCastAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsDh.exit
  %2912 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 12, i64 0
  %2913 = load float, ptr addrspace(1) %2912, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %2914 = fptrunc float %2913 to half
  %2915 = insertelement <3 x half> undef, half %2914, i64 0
  %2916 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 12, i64 1
  %2917 = load float, ptr addrspace(1) %2916, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %2918 = fptrunc float %2917 to half
  %2919 = insertelement <3 x half> %2915, half %2918, i64 1
  %2920 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 12, i64 2
  %2921 = load float, ptr addrspace(1) %2920, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %2922 = fptrunc float %2921 to half
  %2923 = insertelement <3 x half> %2919, half %2922, i64 2
  %2924 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %2923) #14
  %2925 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %2923) #14
  %2926 = fmul fast <3 x half> %2925, splat (half 0xH2CF4)
  %2927 = fadd fast <3 x half> %2925, splat (half 0xH2B0A)
  %2928 = fmul fast <3 x half> %2927, splat (half 0xH3B96)
  %2929 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %2928, <3 x half> splat (half 0xH40CD)) #14
  %2930 = fcmp fast ogt <3 x half> %2925, splat (half 0xH292D)
  %2931 = select fast <3 x i1> %2930, <3 x half> %2929, <3 x half> %2926
  %2932 = fmul fast <3 x half> %2931, %2924
  %2933 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2932) #14
  %2934 = shufflevector <3 x float> %2933, <3 x float> poison, <3 x i32> zeroinitializer
  %2935 = fmul fast <3 x float> %2934, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %2936 = shufflevector <3 x float> %2933, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2937 = fmul fast <3 x float> %2936, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %2938 = fadd fast <3 x float> %2935, %2937
  %2939 = shufflevector <3 x float> %2933, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2940 = fmul fast <3 x float> %2939, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %2941 = fadd fast <3 x float> %2938, %2940
  %2942 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2941) #14
  %2943 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2941) #14
  %2944 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2943, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %2945 = fmul fast <3 x float> %2944, %2942
  %2946 = shufflevector <3 x float> %2945, <3 x float> poison, <3 x i32> zeroinitializer
  %2947 = fmul fast <3 x float> %2946, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %2948 = shufflevector <3 x float> %2945, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2949 = fmul fast <3 x float> %2948, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %2950 = fadd fast <3 x float> %2947, %2949
  %2951 = shufflevector <3 x float> %2945, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2952 = fmul fast <3 x float> %2951, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %2953 = fadd fast <3 x float> %2950, %2952
  %2954 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %2953) #14
  %2955 = shufflevector <3 x half> %2954, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %2956 = fptrunc float %2909 to half
  %2957 = insertelement <3 x half> <half poison, half 0xH0000, half 0xH0000>, half %2956, i64 0
  br label %2958

2958:                                             ; preds = %2911, %_Z27renderWarmthCastAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsDh.exit
  %2959 = phi <3 x half> [ %2957, %2911 ], [ zeroinitializer, %_Z27renderWarmthCastAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsDh.exit ]
  %2960 = phi <2 x half> [ %2955, %2911 ], [ zeroinitializer, %_Z27renderWarmthCastAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsDh.exit ]
  %2961 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 10
  %2962 = load float, ptr addrspace(1) %2961, align 4, !tbaa !176, !alias.scope !98, !noalias !99
  %2963 = tail call i1 @air.convert.u.i1.f.f32(float %2962) #14
  br i1 %2963, label %2964, label %3011

2964:                                             ; preds = %2958
  %2965 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 13, i64 0
  %2966 = load float, ptr addrspace(1) %2965, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %2967 = fptrunc float %2966 to half
  %2968 = insertelement <3 x half> undef, half %2967, i64 0
  %2969 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 13, i64 1
  %2970 = load float, ptr addrspace(1) %2969, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %2971 = fptrunc float %2970 to half
  %2972 = insertelement <3 x half> %2968, half %2971, i64 1
  %2973 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 13, i64 2
  %2974 = load float, ptr addrspace(1) %2973, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %2975 = fptrunc float %2974 to half
  %2976 = insertelement <3 x half> %2972, half %2975, i64 2
  %2977 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %2976) #14
  %2978 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %2976) #14
  %2979 = fmul fast <3 x half> %2978, splat (half 0xH2CF4)
  %2980 = fadd fast <3 x half> %2978, splat (half 0xH2B0A)
  %2981 = fmul fast <3 x half> %2980, splat (half 0xH3B96)
  %2982 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %2981, <3 x half> splat (half 0xH40CD)) #14
  %2983 = fcmp fast ogt <3 x half> %2978, splat (half 0xH292D)
  %2984 = select fast <3 x i1> %2983, <3 x half> %2982, <3 x half> %2979
  %2985 = fmul fast <3 x half> %2984, %2977
  %2986 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %2985) #14
  %2987 = shufflevector <3 x float> %2986, <3 x float> poison, <3 x i32> zeroinitializer
  %2988 = fmul fast <3 x float> %2987, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %2989 = shufflevector <3 x float> %2986, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %2990 = fmul fast <3 x float> %2989, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %2991 = fadd fast <3 x float> %2988, %2990
  %2992 = shufflevector <3 x float> %2986, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %2993 = fmul fast <3 x float> %2992, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %2994 = fadd fast <3 x float> %2991, %2993
  %2995 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %2994) #14
  %2996 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %2994) #14
  %2997 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %2996, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %2998 = fmul fast <3 x float> %2997, %2995
  %2999 = shufflevector <3 x float> %2998, <3 x float> poison, <3 x i32> zeroinitializer
  %3000 = fmul fast <3 x float> %2999, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %3001 = shufflevector <3 x float> %2998, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3002 = fmul fast <3 x float> %3001, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %3003 = fadd fast <3 x float> %3000, %3002
  %3004 = shufflevector <3 x float> %2998, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3005 = fmul fast <3 x float> %3004, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %3006 = fadd fast <3 x float> %3003, %3005
  %3007 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %3006) #14
  %3008 = shufflevector <3 x half> %3007, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %3009 = fptrunc float %2962 to half
  %3010 = insertelement <3 x half> %2959, half %3009, i64 1
  br label %3011

3011:                                             ; preds = %2964, %2958
  %3012 = phi <3 x half> [ %3010, %2964 ], [ %2959, %2958 ]
  %3013 = phi <2 x half> [ %3008, %2964 ], [ zeroinitializer, %2958 ]
  %3014 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 11
  %3015 = load float, ptr addrspace(1) %3014, align 4, !tbaa !177, !alias.scope !98, !noalias !99
  %3016 = tail call i1 @air.convert.u.i1.f.f32(float %3015) #14
  br i1 %3016, label %3017, label %3064

3017:                                             ; preds = %3011
  %3018 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 14, i64 0
  %3019 = load float, ptr addrspace(1) %3018, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %3020 = fptrunc float %3019 to half
  %3021 = insertelement <3 x half> undef, half %3020, i64 0
  %3022 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 14, i64 1
  %3023 = load float, ptr addrspace(1) %3022, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %3024 = fptrunc float %3023 to half
  %3025 = insertelement <3 x half> %3021, half %3024, i64 1
  %3026 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 14, i64 2
  %3027 = load float, ptr addrspace(1) %3026, align 4, !tbaa !110, !alias.scope !98, !noalias !99
  %3028 = fptrunc float %3027 to half
  %3029 = insertelement <3 x half> %3025, half %3028, i64 2
  %3030 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %3029) #14
  %3031 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %3029) #14
  %3032 = fmul fast <3 x half> %3031, splat (half 0xH2CF4)
  %3033 = fadd fast <3 x half> %3031, splat (half 0xH2B0A)
  %3034 = fmul fast <3 x half> %3033, splat (half 0xH3B96)
  %3035 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %3034, <3 x half> splat (half 0xH40CD)) #14
  %3036 = fcmp fast ogt <3 x half> %3031, splat (half 0xH292D)
  %3037 = select fast <3 x i1> %3036, <3 x half> %3035, <3 x half> %3032
  %3038 = fmul fast <3 x half> %3037, %3030
  %3039 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %3038) #14
  %3040 = shufflevector <3 x float> %3039, <3 x float> poison, <3 x i32> zeroinitializer
  %3041 = fmul fast <3 x float> %3040, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %3042 = shufflevector <3 x float> %3039, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3043 = fmul fast <3 x float> %3042, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %3044 = fadd fast <3 x float> %3041, %3043
  %3045 = shufflevector <3 x float> %3039, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3046 = fmul fast <3 x float> %3045, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %3047 = fadd fast <3 x float> %3044, %3046
  %3048 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %3047) #14
  %3049 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %3047) #14
  %3050 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %3049, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %3051 = fmul fast <3 x float> %3050, %3048
  %3052 = shufflevector <3 x float> %3051, <3 x float> poison, <3 x i32> zeroinitializer
  %3053 = fmul fast <3 x float> %3052, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %3054 = shufflevector <3 x float> %3051, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3055 = fmul fast <3 x float> %3054, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %3056 = fadd fast <3 x float> %3053, %3055
  %3057 = shufflevector <3 x float> %3051, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3058 = fmul fast <3 x float> %3057, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %3059 = fadd fast <3 x float> %3056, %3058
  %3060 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %3059) #14
  %3061 = shufflevector <3 x half> %3060, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %3062 = fptrunc float %3015 to half
  %3063 = insertelement <3 x half> %3012, half %3062, i64 2
  br label %3064

3064:                                             ; preds = %3017, %3011
  %3065 = phi <3 x half> [ %3063, %3017 ], [ %3012, %3011 ]
  %3066 = phi <2 x half> [ %3061, %3017 ], [ zeroinitializer, %3011 ]
  %3067 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %2904) #14
  %3068 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %3067) #14
  %3069 = shufflevector <3 x float> %3068, <3 x float> poison, <3 x i32> zeroinitializer
  %3070 = fmul fast <3 x float> %3069, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %3071 = shufflevector <3 x float> %3068, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3072 = fmul fast <3 x float> %3071, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %3073 = fadd fast <3 x float> %3070, %3072
  %3074 = shufflevector <3 x float> %3068, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3075 = fmul fast <3 x float> %3074, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %3076 = fadd fast <3 x float> %3073, %3075
  %3077 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %3076) #14
  %3078 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %3076) #14
  %3079 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %3078, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %3080 = fmul fast <3 x float> %3079, %3077
  %3081 = shufflevector <3 x float> %3080, <3 x float> poison, <3 x i32> zeroinitializer
  %3082 = fmul fast <3 x float> %3081, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %3083 = shufflevector <3 x float> %3080, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3084 = fmul fast <3 x float> %3083, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %3085 = fadd fast <3 x float> %3082, %3084
  %3086 = shufflevector <3 x float> %3080, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3087 = fmul fast <3 x float> %3086, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %3088 = fadd fast <3 x float> %3085, %3087
  %3089 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %3088) #14
  %3090 = extractelement <3 x half> %3089, i64 2
  %3091 = fcmp fast une half %3090, 0xH0000
  %3092 = extractelement <3 x half> %3089, i64 1
  %3093 = fcmp fast une half %3092, 0xH0000
  %3094 = select i1 %3091, i1 true, i1 %3093
  br i1 %3094, label %3095, label %3097

3095:                                             ; preds = %3064
  %3096 = tail call fast half @air.atan2.f16(half %3090, half %3092) #14
  br label %3097

3097:                                             ; preds = %3095, %3064
  %3098 = phi fast half [ %3096, %3095 ], [ 0xH0000, %3064 ]
  %3099 = shufflevector <3 x half> %3089, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %3100 = tail call fast half @air.dot.v2f16(<2 x half> %3099, <2 x half> %3099) #14
  %3101 = tail call fast half @air.sqrt.f16(half %3100) #14
  %3102 = fpext half %3098 to float
  %3103 = fmul fast float %3102, 0x404C9178A0000000
  %3104 = fadd fast float %3103, 1.795000e+02
  %3105 = fptrunc float %3104 to half
  %3106 = tail call fast half @air.clamp.f16(half %3105, half 0xH0000, half 0xH5D9C) #14
  %3107 = fadd fast half %3106, 0xH3800
  %3108 = fpext half %3107 to float
  %3109 = insertelement <2 x float> undef, float %3108, i64 0
  %3110 = insertelement <2 x float> %3109, float 5.000000e-01, i64 1
  %3111 = fmul fast <2 x float> %3110, <float 0x3F66C16C20000000, float 2.500000e-01>
  %3112 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %13, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %3111, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %3113 = extractvalue { <4 x half>, i8 } %3112, 0
  %3114 = insertelement <2 x float> %3109, float 1.500000e+00, i64 1
  %3115 = fmul fast <2 x float> %3114, <float 0x3F66C16C20000000, float 2.500000e-01>
  %3116 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %13, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %3115, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %3117 = extractvalue { <4 x half>, i8 } %3116, 0
  %3118 = insertelement <2 x float> %3109, float 2.500000e+00, i64 1
  %3119 = fmul fast <2 x float> %3118, <float 0x3F66C16C20000000, float 2.500000e-01>
  %3120 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %13, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %3119, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %3121 = extractvalue { <4 x half>, i8 } %3120, 0
  %3122 = insertelement <2 x float> %3109, float 3.500000e+00, i64 1
  %3123 = fmul fast <2 x float> %3122, <float 0x3F66C16C20000000, float 2.500000e-01>
  %3124 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %13, ptr addrspace(2) readonly captures(none) @__air_sampler_state.3, <2 x float> %3123, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %3125 = extractvalue { <4 x half>, i8 } %3124, 0
  %3126 = extractelement <4 x half> %3113, i64 1
  %3127 = fadd fast half %3126, 0xH3C00
  %3128 = extractelement <4 x half> %3117, i64 1
  %3129 = fadd fast half %3128, 0xH3C00
  %3130 = extractelement <4 x half> %3121, i64 1
  %3131 = fadd fast half %3130, 0xH3C00
  %3132 = extractelement <4 x half> %3125, i64 1
  %3133 = fadd fast half %3132, 0xH3C00
  %3134 = tail call fast half @air.mix.f16(half %3127, half %3133, half %77) #14
  %3135 = tail call fast half @air.mix.f16(half %3129, half %3131, half %95) #14
  %3136 = tail call fast half @air.mix.f16(half %3134, half %3135, half %96) #14
  %3137 = fcmp fast ogt half %3136, 0xH3C00
  br i1 %3137, label %3140, label %3138

3138:                                             ; preds = %3097
  %3139 = extractelement <3 x half> %3089, i64 0
  br label %_Z31renderSelectiveColorAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEEDhDhDhDh.exit

3140:                                             ; preds = %3097
  %3141 = fmul fast half %3101, 0xH4900
  %3142 = tail call fast half @air.clamp.f16(half %3141, half 0xH0000, half 0xH3C00) #14
  %3143 = fmul fast half %3142, 0xH4000
  %3144 = fsub fast half 0xH4200, %3143
  %3145 = extractelement <3 x half> %3089, i64 0
  %3146 = fmul fast half %3145, %3145
  %3147 = fsub fast half 0xH3C00, %3146
  %3148 = fmul fast half %3142, %3142
  %3149 = fmul fast half %3148, %3147
  %3150 = fmul fast half %3149, %3144
  %3151 = tail call fast half @air.mix.f16(half %3136, half 0xH3C00, half %3150) #14
  br label %_Z31renderSelectiveColorAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEEDhDhDhDh.exit

_Z31renderSelectiveColorAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEEDhDhDhDh.exit: ; preds = %3140, %3138
  %3152 = phi half [ %3139, %3138 ], [ %3145, %3140 ]
  %3153 = phi fast half [ %3136, %3138 ], [ %3151, %3140 ]
  %3154 = extractelement <4 x half> %3113, i64 2
  %3155 = fadd fast half %3154, 0xH3C00
  %3156 = extractelement <4 x half> %3125, i64 2
  %3157 = fadd fast half %3156, 0xH3C00
  %3158 = tail call fast half @air.mix.f16(half %3155, half %3157, half %77) #14
  %3159 = extractelement <4 x half> %3117, i64 2
  %3160 = fadd fast half %3159, 0xH3C00
  %3161 = extractelement <4 x half> %3121, i64 2
  %3162 = fadd fast half %3161, 0xH3C00
  %3163 = tail call fast half @air.mix.f16(half %3160, half %3162, half %95) #14
  %3164 = tail call fast half @air.mix.f16(half %3158, half %3163, half %96) #14
  %3165 = extractelement <4 x half> %3113, i64 0
  %3166 = extractelement <4 x half> %3125, i64 0
  %3167 = tail call fast half @air.mix.f16(half %3165, half %3166, half %77) #14
  %3168 = extractelement <4 x half> %3117, i64 0
  %3169 = extractelement <4 x half> %3121, i64 0
  %3170 = tail call fast half @air.mix.f16(half %3168, half %3169, half %95) #14
  %3171 = tail call fast half @air.mix.f16(half %3167, half %3170, half %96) #14
  %3172 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %2904, <3 x half> splat (half 0xH3C00)) #14
  %3173 = fadd fast <3 x half> %3172, splat (half 0xHBC00)
  %3174 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %2904, <3 x half> zeroinitializer) #14
  %3175 = fmul fast half %3153, %3101
  %3176 = fadd fast half %3171, %3098
  %3177 = tail call fast half @air.clamp.f16(half %3175, half 0xHB99A, half 0xH399A) #14
  %3178 = tail call fast half @air.mix.f16(half 0xH3C00, half %3164, half %3177) #14
  %3179 = fmul fast half %3178, %3152
  %3180 = insertelement <3 x half> poison, half %3179, i64 0
  %3181 = tail call fast half @air.cos.f16(half %3176) #14
  %3182 = fmul fast half %3181, %3175
  %3183 = insertelement <3 x half> %3180, half %3182, i64 1
  %3184 = tail call fast half @air.sin.f16(half %3176) #14
  %3185 = fmul fast half %3184, %3175
  %3186 = insertelement <3 x half> %3183, half %3185, i64 2
  %3187 = extractelement <3 x half> %3065, i64 2
  %3188 = fpext half %3187 to float
  %3189 = fpext half %3152 to float
  %3190 = fadd fast float %3189, -1.000000e+00
  %3191 = fmul fast float %3190, %3190
  %3192 = fmul fast float %3191, -1.600000e+01
  %3193 = tail call fast float @air.fast_exp.f32(float %3192) #14
  %3194 = fmul fast float %3193, %3188
  %3195 = fptrunc float %3194 to half
  %3196 = extractelement <3 x half> %3065, i64 1
  %3197 = fpext half %3196 to float
  %3198 = fadd fast float %3189, -5.000000e-01
  %3199 = fmul fast float %3198, %3198
  %3200 = fmul fast float %3199, -1.600000e+01
  %3201 = tail call fast float @air.fast_exp.f32(float %3200) #14
  %3202 = fmul fast float %3201, %3197
  %3203 = fptrunc float %3202 to half
  %3204 = extractelement <3 x half> %3065, i64 0
  %3205 = fpext half %3204 to float
  %3206 = fneg fast half %3152
  %3207 = fmul fast half %3152, %3206
  %3208 = fpext half %3207 to float
  %3209 = fmul fast float %3208, 1.600000e+01
  %3210 = tail call fast float @air.fast_exp.f32(float %3209) #14
  %3211 = fmul fast float %3210, %3205
  %3212 = fptrunc float %3211 to half
  %3213 = shufflevector <3 x half> %3186, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %3214 = fadd fast <2 x half> %3213, %2960
  %3215 = insertelement <2 x half> poison, half %3212, i64 0
  %3216 = shufflevector <2 x half> %3215, <2 x half> poison, <2 x i32> zeroinitializer
  %3217 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %3213, <2 x half> %3214, <2 x half> %3216) #14
  %3218 = fadd fast <2 x half> %3217, %3013
  %3219 = insertelement <2 x half> poison, half %3203, i64 0
  %3220 = shufflevector <2 x half> %3219, <2 x half> poison, <2 x i32> zeroinitializer
  %3221 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %3217, <2 x half> %3218, <2 x half> %3220) #14
  %3222 = fadd fast <2 x half> %3221, %3066
  %3223 = insertelement <2 x half> poison, half %3195, i64 0
  %3224 = shufflevector <2 x half> %3223, <2 x half> poison, <2 x i32> zeroinitializer
  %3225 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %3221, <2 x half> %3222, <2 x half> %3224) #14
  %3226 = shufflevector <2 x half> %3225, <2 x half> poison, <3 x i32> <i32 0, i32 1, i32 poison>
  %3227 = shufflevector <3 x half> %3180, <3 x half> %3226, <3 x i32> <i32 0, i32 3, i32 4>
  %3228 = insertelement <3 x half> poison, half %2907, i64 0
  %3229 = shufflevector <3 x half> %3228, <3 x half> poison, <3 x i32> zeroinitializer
  %3230 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3186, <3 x half> %3227, <3 x half> %3229) #14
  %3231 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3227, <3 x half> %3230, <3 x half> %1227) #14
  %3232 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %3231) #14
  %3233 = shufflevector <3 x float> %3232, <3 x float> poison, <3 x i32> zeroinitializer
  %3234 = shufflevector <3 x float> %3232, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3235 = fmul fast <3 x float> %3234, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %3236 = fadd fast <3 x float> %3235, %3233
  %3237 = shufflevector <3 x float> %3232, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3238 = fmul fast <3 x float> %3237, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %3239 = fadd fast <3 x float> %3236, %3238
  %3240 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %3239) #14
  %3241 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %3239) #14
  %3242 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %3241, <3 x float> splat (float 0x40029ACA60000000)) #14
  %3243 = fmul fast <3 x float> %3242, %3240
  %3244 = shufflevector <3 x float> %3243, <3 x float> poison, <3 x i32> zeroinitializer
  %3245 = fmul fast <3 x float> %3244, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %3246 = shufflevector <3 x float> %3243, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3247 = fmul fast <3 x float> %3246, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %3248 = fadd fast <3 x float> %3245, %3247
  %3249 = shufflevector <3 x float> %3243, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3250 = fmul fast <3 x float> %3249, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %3251 = fadd fast <3 x float> %3248, %3250
  %3252 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %3251) #14
  %3253 = extractelement <4 x half> %3113, i64 3
  %3254 = fadd fast half %3253, 0xH3C00
  %3255 = extractelement <4 x half> %3117, i64 3
  %3256 = fadd fast half %3255, 0xH3C00
  %3257 = extractelement <4 x half> %3121, i64 3
  %3258 = fadd fast half %3257, 0xH3C00
  %3259 = extractelement <4 x half> %3125, i64 3
  %3260 = fadd fast half %3259, 0xH3C00
  %3261 = tail call fast half @air.mix.f16(half %3254, half %3260, half %77) #14
  %3262 = tail call fast half @air.mix.f16(half %3256, half %3258, half %95) #14
  %3263 = tail call fast half @air.mix.f16(half %3261, half %3262, half %96) #14
  %3264 = insertelement <3 x half> poison, half %3263, i64 0
  %3265 = shufflevector <3 x half> %3264, <3 x half> poison, <3 x i32> zeroinitializer
  %3266 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %3252, <3 x half> %3265) #14
  %3267 = tail call fast half @air.sqrt.f16(half %3175) #14
  %3268 = fsub fast half 0xH2E66, %3267
  %3269 = fneg fast half %3267
  %3270 = fdiv fast half %3268, %3269
  %3271 = tail call fast half @air.clamp.f16(half %3270, half 0xH0000, half 0xH3C00) #14
  %3272 = fmul fast half %3271, %3271
  %3273 = fmul fast half %3271, 0xH4000
  %3274 = fsub fast half 0xH4200, %3273
  %3275 = tail call fast half @air.sqrt.f16(half %3152) #14
  %3276 = fmul fast half %3272, %3275
  %3277 = fmul fast half %3276, %3274
  %3278 = insertelement <3 x half> poison, half %3277, i64 0
  %3279 = shufflevector <3 x half> %3278, <3 x half> poison, <3 x i32> zeroinitializer
  %3280 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3252, <3 x half> %3266, <3 x half> %3279) #14
  %3281 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %3280) #14
  %3282 = fadd fast <3 x half> %3173, %3174
  %3283 = fadd fast <3 x half> %3282, %3281
  %3284 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 17
  %3285 = load i32, ptr addrspace(1) %3284, align 4, !tbaa !178, !alias.scope !98, !noalias !99
  %3286 = icmp eq i32 %3285, 5
  %3287 = select i1 %3286, half 0xH399A, half 0xH3B33
  %3288 = tail call fast float @air.fast_fmin.f32(float %252, float 0.000000e+00) #14
  %3289 = fptrunc float %3288 to half
  %3290 = fneg fast half %3289
  %3291 = tail call fast half @air.mix.f16(half %3287, half 0xHACCD, half %3290) #14
  %3292 = tail call fast half @air.mix.f16(half 0xH3C00, half 0xH38CD, half %3290) #14
  %3293 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 10, i32 65
  %3294 = load float, ptr addrspace(1) %3293, align 4, !tbaa !179, !alias.scope !98, !noalias !99
  %3295 = fmul fast half %3287, 0xH3800
  %3296 = tail call fast fastcc <3 x half> @_Z10airyFilterDv3_DhDh(<3 x half> noundef %3283, half noundef %3295) #17
  %3297 = fpext half %3291 to float
  %3298 = fmul fast float %3297, 0x3FA99999A0000000
  %3299 = fptrunc float %3298 to half
  %3300 = fmul fast half %3299, 0xH4000
  %3301 = fpext half %3300 to float
  %3302 = fsub fast float 1.000000e+00, %3301
  %3303 = fdiv fast float 1.000000e+00, %3302
  %3304 = fptrunc float %3303 to half
  %3305 = insertelement <3 x half> poison, half %3304, i64 0
  %3306 = shufflevector <3 x half> %3305, <3 x half> poison, <3 x i32> zeroinitializer
  %3307 = fmul fast <3 x half> %3306, %3296
  %3308 = insertelement <3 x half> poison, half %3299, i64 0
  %3309 = shufflevector <3 x half> %3308, <3 x half> poison, <3 x i32> zeroinitializer
  %3310 = fadd fast <3 x half> %3307, %3309
  %3311 = tail call fast half @air.dot.v3f16(<3 x half> %3296, <3 x half> splat (half 0xH3555)) #14
  %3312 = fpext half %3311 to float
  %3313 = fpext half %3304 to float
  %3314 = fmul fast float %3313, %3312
  %3315 = fpext half %3299 to float
  %3316 = fadd fast float %3314, %3315
  %3317 = fdiv fast float %3316, %3312
  %3318 = fptrunc float %3317 to half
  %3319 = insertelement <3 x half> poison, half %3318, i64 0
  %3320 = shufflevector <3 x half> %3319, <3 x half> poison, <3 x i32> zeroinitializer
  %3321 = fmul fast <3 x half> %3320, %3296
  %3322 = fcmp fast ogt half %3311, 0xH0000
  %3323 = insertelement <3 x i1> poison, i1 %3322, i64 0
  %3324 = shufflevector <3 x i1> %3323, <3 x i1> poison, <3 x i32> zeroinitializer
  %3325 = select fast <3 x i1> %3324, <3 x half> %3321, <3 x half> zeroinitializer
  %3326 = insertelement <3 x half> poison, half %3292, i64 0
  %3327 = shufflevector <3 x half> %3326, <3 x half> poison, <3 x i32> zeroinitializer
  %3328 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3325, <3 x half> %3310, <3 x half> %3327) #14
  %3329 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3328, <3 x half> zeroinitializer) #14
  %3330 = fmul fast float %3297, 0xBFC99999A0000000
  %3331 = fptrunc float %3330 to half
  %3332 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %3329, half noundef %3331) #17
  %3333 = fsub fast float 1.000000e+00, %3294
  %3334 = fmul fast float %3333, %797
  %3335 = fptrunc float %3334 to half
  %3336 = insertelement <3 x half> poison, half %3335, i64 0
  %3337 = shufflevector <3 x half> %3336, <3 x half> poison, <3 x i32> zeroinitializer
  %3338 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3332, <3 x half> %3283, <3 x half> %3337) #14
  %3339 = icmp eq i32 %279, 3
  %3340 = insertelement <3 x i1> poison, i1 %3339, i64 0
  %3341 = shufflevector <3 x i1> %3340, <3 x i1> poison, <3 x i32> zeroinitializer
  %3342 = select fast <3 x i1> %3341, <3 x half> %3338, <3 x half> %3283
  %3343 = icmp eq i32 %279, 4
  %3344 = insertelement <3 x i1> poison, i1 %3343, i64 0
  %3345 = shufflevector <3 x i1> %3344, <3 x i1> poison, <3 x i32> zeroinitializer
  %3346 = select fast <3 x i1> %3345, <3 x half> %3342, <3 x half> %1467
  %3347 = fptrunc float %252 to half
  %3348 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 10, i32 20
  %3349 = load float, ptr addrspace(1) %3348, align 4, !tbaa !180, !alias.scope !98, !noalias !99
  %3350 = fptrunc float %3349 to half
  %3351 = fcmp fast ogt half %3347, 0xH0000
  %3352 = fpext half %3347 to float
  %3353 = fmul fast float %3352, 0x3FD99999A0000000
  %3354 = fneg fast half %3347
  %3355 = fptrunc float %3353 to half
  %3356 = select fast i1 %3351, half %3355, half %3354
  %3357 = fmul fast half %3356, %3350
  %3358 = tail call fast fastcc <3 x half> @_Z11whitesCurveDv3_DhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEEDhDh(<3 x half> noundef %3342, ptr addrspace(1) %4, half noundef %3357, half noundef 0xH3C00) #18, !alias.scope !82, !noalias !83
  %3359 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %3358, <3 x half> zeroinitializer) #14
  %3360 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3358, <3 x half> splat (half 0xH3C00)) #14
  %3361 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %3358) #14
  %3362 = tail call fast half @air.dot.v3f16(<3 x half> %3361, <3 x half> splat (half 0xH3555)) #14
  %3363 = tail call fast half @air.sqrt.f16(half %3362) #14
  %3364 = fpext half %3363 to float
  %3365 = fsub fast float 1.000000e+00, %3364
  %3366 = fmul fast float %3365, %3364
  %3367 = fptrunc float %3366 to half
  %3368 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %3361) #14
  %3369 = tail call fast half @air.sqrt.f16(half %488) #14
  %3370 = fneg fast half %3369
  %3371 = fmul fast half %3370, %3367
  %3372 = fpext half %3367 to float
  %3373 = fmul fast float %3372, 0x3FD322D0E0000000
  %3374 = fptrunc float %3373 to half
  %3375 = insertelement <3 x half> poison, half %3374, i64 0
  %3376 = fmul fast <3 x half> %3375, %3368
  %3377 = shufflevector <3 x half> %3376, <3 x half> poison, <3 x i32> zeroinitializer
  %3378 = shufflevector <3 x half> %3368, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3379 = fmul fast float %3372, 0x3FE2C8B440000000
  %3380 = fptrunc float %3379 to half
  %3381 = insertelement <3 x half> poison, half %3380, i64 0
  %3382 = shufflevector <3 x half> %3381, <3 x half> poison, <3 x i32> zeroinitializer
  %3383 = fmul fast <3 x half> %3382, %3378
  %3384 = shufflevector <3 x half> %3368, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3385 = fmul fast float %3372, 0x3FBD2F1AA0000000
  %3386 = fptrunc float %3385 to half
  %3387 = insertelement <3 x half> poison, half %3386, i64 0
  %3388 = shufflevector <3 x half> %3387, <3 x half> poison, <3 x i32> zeroinitializer
  %3389 = fmul fast <3 x half> %3388, %3384
  %3390 = insertelement <3 x half> poison, half %3371, i64 0
  %3391 = shufflevector <3 x half> %3390, <3 x half> poison, <3 x i32> zeroinitializer
  %3392 = fadd fast <3 x half> %3391, %3368
  %3393 = fadd fast <3 x half> %3392, %3383
  %3394 = fadd fast <3 x half> %3393, %3377
  %3395 = fadd fast <3 x half> %3394, %3389
  %3396 = insertelement <3 x half> poison, half %3369, i64 0
  %3397 = shufflevector <3 x half> %3396, <3 x half> poison, <3 x i32> zeroinitializer
  %3398 = fneg fast half %3367
  %3399 = insertelement <3 x half> poison, half %3398, i64 0
  %3400 = shufflevector <3 x half> %3399, <3 x half> poison, <3 x i32> zeroinitializer
  %3401 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3368, <3 x half> %3397, <3 x half> %3400) #14
  %3402 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3401, <3 x half> %3395, <3 x half> splat (half 0xH3A66)) #14
  %3403 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3402, <3 x half> zeroinitializer) #14
  %3404 = fmul fast <3 x half> %3403, %3403
  %3405 = fadd fast <3 x half> %3359, splat (half 0xHBC00)
  %3406 = fadd fast <3 x half> %3405, %3360
  %3407 = fadd fast <3 x half> %3406, %3404
  %3408 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3407, <3 x half> %3358) #14
  %3409 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3407, <3 x half> %3408, <3 x half> zeroinitializer) #14
  %3410 = fmul fast float %797, 0x3FE99999A0000000
  %3411 = fptrunc float %3410 to half
  %3412 = insertelement <3 x half> poison, half %3411, i64 0
  %3413 = shufflevector <3 x half> %3412, <3 x half> poison, <3 x i32> zeroinitializer
  %3414 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3409, <3 x half> %3342, <3 x half> %3413) #14
  %3415 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 0
  %3416 = load i32, ptr addrspace(1) %3415, align 4, !tbaa !114, !alias.scope !98, !noalias !99
  %3417 = icmp eq i32 %3416, 4
  %3418 = insertelement <3 x i1> poison, i1 %3417, i64 0
  %3419 = shufflevector <3 x i1> %3418, <3 x i1> poison, <3 x i32> zeroinitializer
  %3420 = select fast <3 x i1> %3419, <3 x half> %3414, <3 x half> %3342
  %3421 = select i1 %3286, half 0xH399A, half 0xH3C00
  %3422 = fmul fast half %3421, 0xH3800
  %3423 = tail call fast fastcc <3 x half> @_Z10airyFilterDv3_DhDh(<3 x half> noundef %3420, half noundef %3422) #17
  %3424 = fpext half %3421 to float
  %3425 = fmul fast float %3424, 0x3FA99999A0000000
  %3426 = fptrunc float %3425 to half
  %3427 = fmul fast half %3426, 0xH4000
  %3428 = fpext half %3427 to float
  %3429 = fsub fast float 1.000000e+00, %3428
  %3430 = fdiv fast float 1.000000e+00, %3429
  %3431 = fptrunc float %3430 to half
  %3432 = insertelement <3 x half> poison, half %3431, i64 0
  %3433 = shufflevector <3 x half> %3432, <3 x half> poison, <3 x i32> zeroinitializer
  %3434 = fmul fast <3 x half> %3423, %3433
  %3435 = insertelement <3 x half> poison, half %3426, i64 0
  %3436 = shufflevector <3 x half> %3435, <3 x half> poison, <3 x i32> zeroinitializer
  %3437 = fadd fast <3 x half> %3434, %3436
  %3438 = tail call fast half @air.dot.v3f16(<3 x half> %3423, <3 x half> splat (half 0xH3555)) #14
  %3439 = fpext half %3438 to float
  %3440 = fpext half %3431 to float
  %3441 = fmul fast float %3439, %3440
  %3442 = fpext half %3426 to float
  %3443 = fadd fast float %3441, %3442
  %3444 = fdiv fast float %3443, %3439
  %3445 = fptrunc float %3444 to half
  %3446 = insertelement <3 x half> poison, half %3445, i64 0
  %3447 = shufflevector <3 x half> %3446, <3 x half> poison, <3 x i32> zeroinitializer
  %3448 = fmul fast <3 x half> %3447, %3423
  %3449 = fcmp fast ogt half %3438, 0xH0000
  %3450 = insertelement <3 x i1> poison, i1 %3449, i64 0
  %3451 = shufflevector <3 x i1> %3450, <3 x i1> poison, <3 x i32> zeroinitializer
  %3452 = select fast <3 x i1> %3451, <3 x half> %3448, <3 x half> zeroinitializer
  %3453 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3452, <3 x half> %3437, <3 x half> splat (half 0xH3C00)) #14
  %3454 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3453, <3 x half> zeroinitializer) #14
  %3455 = fmul fast float %3424, 0xBFC99999A0000000
  %3456 = fptrunc float %3455 to half
  %3457 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %3454, half noundef %3456) #17
  %3458 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3457, <3 x half> %3420, <3 x half> %3337) #14
  %3459 = icmp eq i32 %3416, 15
  %3460 = insertelement <3 x i1> poison, i1 %3459, i64 0
  %3461 = shufflevector <3 x i1> %3460, <3 x i1> poison, <3 x i32> zeroinitializer
  %3462 = select fast <3 x i1> %3461, <3 x half> %3458, <3 x half> %3420
  %3463 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 4
  %3464 = load float, ptr addrspace(1) %3463, align 4, !tbaa !181, !alias.scope !98, !noalias !99
  %3465 = fptrunc float %3464 to half
  %3466 = insertelement <3 x half> poison, half %3465, i64 0
  %3467 = shufflevector <3 x half> %3466, <3 x half> poison, <3 x i32> zeroinitializer
  %3468 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3346, <3 x half> %3462, <3 x half> %3467) #14
  %3469 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 5
  %3470 = load float, ptr addrspace(1) %3469, align 4, !tbaa !182, !alias.scope !98, !noalias !99
  %3471 = fptrunc float %3470 to half
  %3472 = insertelement <3 x half> poison, half %3471, i64 0
  %3473 = shufflevector <3 x half> %3472, <3 x half> poison, <3 x i32> zeroinitializer
  %3474 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3346, <3 x half> %3462, <3 x half> %3473) #14
  %3475 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3474, <3 x half> %3468, <3 x half> %1227) #14
  %3476 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 12, i32 1
  %3477 = load float, ptr addrspace(1) %3476, align 4, !tbaa.struct !183, !alias.scope !98, !noalias !99
  %3478 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 12, i32 2
  %3479 = load float, ptr addrspace(1) %3478, align 4, !tbaa.struct !184, !alias.scope !98, !noalias !99
  %3480 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 12, i32 3
  %3481 = load float, ptr addrspace(1) %3480, align 4, !tbaa.struct !185, !alias.scope !98, !noalias !99
  %3482 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 12, i32 4
  %3483 = load float, ptr addrspace(1) %3482, align 4, !tbaa.struct !186, !alias.scope !98, !noalias !99
  %3484 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 12, i32 5
  %3485 = load float, ptr addrspace(1) %3484, align 4, !tbaa.struct !187, !alias.scope !98, !noalias !99
  %3486 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 12, i32 6
  %3487 = load float, ptr addrspace(1) %3486, align 4, !tbaa.struct !188, !alias.scope !98, !noalias !99
  %3488 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 12, i32 7
  %3489 = load float, ptr addrspace(1) %3488, align 4, !tbaa.struct !189, !alias.scope !98, !noalias !99
  %3490 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 12, i32 8
  %3491 = load float, ptr addrspace(1) %3490, align 4, !tbaa.struct !190, !alias.scope !98, !noalias !99
  %3492 = fdiv fast float %3477, %3479
  %3493 = fptrunc float %3492 to half
  %3494 = fpext half %3493 to float
  %3495 = fsub fast float 1.000000e+00, %3494
  %3496 = fdiv fast float 1.000000e+00, %3495
  %3497 = fptrunc float %3496 to half
  %3498 = fptrunc float %3487 to half
  %3499 = insertelement <3 x half> poison, half %3497, i64 0
  %3500 = shufflevector <3 x half> %3499, <3 x half> poison, <3 x i32> zeroinitializer
  %3501 = fmul fast <3 x half> %3500, %3475
  %3502 = insertelement <3 x half> poison, half %3493, i64 0
  %3503 = shufflevector <3 x half> %3502, <3 x half> poison, <3 x i32> zeroinitializer
  %3504 = fadd fast <3 x half> %3501, %3503
  %3505 = tail call fast half @air.dot.v3f16(<3 x half> %3475, <3 x half> splat (half 0xH3555)) #14
  %3506 = fpext half %3505 to float
  %3507 = fpext half %3497 to float
  %3508 = fmul fast float %3506, %3507
  %3509 = fadd fast float %3508, %3494
  %3510 = fdiv fast float %3509, %3506
  %3511 = fptrunc float %3510 to half
  %3512 = insertelement <3 x half> poison, half %3511, i64 0
  %3513 = shufflevector <3 x half> %3512, <3 x half> poison, <3 x i32> zeroinitializer
  %3514 = fmul fast <3 x half> %3513, %3475
  %3515 = fcmp fast ogt half %3505, 0xH0000
  %3516 = insertelement <3 x i1> poison, i1 %3515, i64 0
  %3517 = shufflevector <3 x i1> %3516, <3 x i1> poison, <3 x i32> zeroinitializer
  %3518 = select fast <3 x i1> %3517, <3 x half> %3514, <3 x half> zeroinitializer
  %3519 = insertelement <3 x half> poison, half %3498, i64 0
  %3520 = shufflevector <3 x half> %3519, <3 x half> poison, <3 x i32> zeroinitializer
  %3521 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3518, <3 x half> %3504, <3 x half> %3520) #14
  %3522 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3521, <3 x half> zeroinitializer) #14
  %3523 = fdiv fast float %3477, %3481
  %3524 = fptrunc float %3523 to half
  %3525 = fpext half %3524 to float
  %3526 = fsub fast float 1.000000e+00, %3525
  %3527 = fdiv fast float 1.000000e+00, %3526
  %3528 = fptrunc float %3527 to half
  %3529 = insertelement <3 x half> poison, half %3528, i64 0
  %3530 = shufflevector <3 x half> %3529, <3 x half> poison, <3 x i32> zeroinitializer
  %3531 = fmul fast <3 x half> %3530, %3475
  %3532 = insertelement <3 x half> poison, half %3524, i64 0
  %3533 = shufflevector <3 x half> %3532, <3 x half> poison, <3 x i32> zeroinitializer
  %3534 = fadd fast <3 x half> %3531, %3533
  %3535 = fpext half %3528 to float
  %3536 = fmul fast float %3506, %3535
  %3537 = fadd fast float %3536, %3525
  %3538 = fdiv fast float %3537, %3506
  %3539 = fptrunc float %3538 to half
  %3540 = insertelement <3 x half> poison, half %3539, i64 0
  %3541 = shufflevector <3 x half> %3540, <3 x half> poison, <3 x i32> zeroinitializer
  %3542 = fmul fast <3 x half> %3541, %3475
  %3543 = select fast <3 x i1> %3517, <3 x half> %3542, <3 x half> zeroinitializer
  %3544 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3543, <3 x half> %3534, <3 x half> %3520) #14
  %3545 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3544, <3 x half> zeroinitializer) #14
  %3546 = fptrunc float %3483 to half
  %3547 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %3522, <3 x half> zeroinitializer) #14
  %3548 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3522, <3 x half> splat (half 0xH3C00)) #14
  %3549 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %3522) #14
  %3550 = extractelement <3 x half> %3549, i64 0
  %3551 = extractelement <3 x half> %3549, i64 1
  %3552 = extractelement <3 x half> %3549, i64 2
  %3553 = tail call fast half @air.fmax3.f16(half %3550, half %3551, half %3552) #14
  %3554 = tail call fast half @air.pow.f16(half %3553, half 0xH3800) #14
  %3555 = fsub fast half 0xH3C00, %3554
  %3556 = fmul fast half %3555, %3546
  %3557 = fadd fast half %3556, 0xH3C00
  %3558 = insertelement <3 x half> poison, half %3557, i64 0
  %3559 = shufflevector <3 x half> %3558, <3 x half> poison, <3 x i32> zeroinitializer
  %3560 = fmul fast <3 x half> %3559, %3549
  %3561 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %3560) #14
  %3562 = fadd fast <3 x half> %3547, splat (half 0xHBC00)
  %3563 = fadd fast <3 x half> %3562, %3548
  %3564 = fadd fast <3 x half> %3563, %3561
  %3565 = fptrunc float %3485 to half
  %3566 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %3545, <3 x half> zeroinitializer) #14
  %3567 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3545, <3 x half> splat (half 0xH3C00)) #14
  %3568 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %3545) #14
  %3569 = extractelement <3 x half> %3568, i64 0
  %3570 = extractelement <3 x half> %3568, i64 1
  %3571 = extractelement <3 x half> %3568, i64 2
  %3572 = tail call fast half @air.fmax3.f16(half %3569, half %3570, half %3571) #14
  %3573 = tail call fast half @air.pow.f16(half %3572, half 0xH3800) #14
  %3574 = fsub fast half 0xH3C00, %3573
  %3575 = fmul fast half %3574, %3565
  %3576 = fadd fast half %3575, 0xH3C00
  %3577 = insertelement <3 x half> poison, half %3576, i64 0
  %3578 = shufflevector <3 x half> %3577, <3 x half> poison, <3 x i32> zeroinitializer
  %3579 = fmul fast <3 x half> %3578, %3568
  %3580 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %3579) #14
  %3581 = fadd fast <3 x half> %3566, splat (half 0xHBC00)
  %3582 = fadd fast <3 x half> %3581, %3567
  %3583 = fadd fast <3 x half> %3582, %3580
  %3584 = fptrunc float %3489 to half
  %3585 = tail call fast fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %3564, half noundef %3584) #17
  %3586 = fptrunc float %3491 to half
  %3587 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %3585, <3 x half> zeroinitializer) #14
  %3588 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3585, <3 x half> splat (half 0xH3C00)) #14
  %3589 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %3585) #14
  %3590 = tail call fast half @air.dot.v3f16(<3 x half> %3589, <3 x half> splat (half 0xH3555)) #14
  %3591 = tail call fast half @air.sqrt.f16(half %3590) #14
  %3592 = fpext half %3591 to float
  %3593 = fsub fast float 1.000000e+00, %3592
  %3594 = fmul fast float %3593, %3592
  %3595 = fptrunc float %3594 to half
  %3596 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %3589) #14
  %3597 = tail call fast half @air.sqrt.f16(half %245) #14
  %3598 = fmul fast half %3595, %3586
  %3599 = fmul fast half %3598, 0xH4000
  %3600 = fmul fast half %3598, 0xHC000
  %3601 = fmul fast half %3600, %3597
  %3602 = fpext half %3599 to float
  %3603 = fmul fast float %3602, 0x3FD322D0E0000000
  %3604 = fptrunc float %3603 to half
  %3605 = insertelement <3 x half> poison, half %3604, i64 0
  %3606 = fmul fast <3 x half> %3605, %3596
  %3607 = shufflevector <3 x half> %3606, <3 x half> poison, <3 x i32> zeroinitializer
  %3608 = shufflevector <3 x half> %3596, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3609 = fmul fast float %3602, 0x3FE2C8B440000000
  %3610 = fptrunc float %3609 to half
  %3611 = insertelement <3 x half> poison, half %3610, i64 0
  %3612 = shufflevector <3 x half> %3611, <3 x half> poison, <3 x i32> zeroinitializer
  %3613 = fmul fast <3 x half> %3612, %3608
  %3614 = shufflevector <3 x half> %3596, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3615 = fmul fast float %3602, 0x3FBD2F1AA0000000
  %3616 = fptrunc float %3615 to half
  %3617 = insertelement <3 x half> poison, half %3616, i64 0
  %3618 = shufflevector <3 x half> %3617, <3 x half> poison, <3 x i32> zeroinitializer
  %3619 = fmul fast <3 x half> %3618, %3614
  %3620 = insertelement <3 x half> poison, half %3601, i64 0
  %3621 = shufflevector <3 x half> %3620, <3 x half> poison, <3 x i32> zeroinitializer
  %3622 = fadd fast <3 x half> %3621, %3596
  %3623 = fadd fast <3 x half> %3622, %3613
  %3624 = fadd fast <3 x half> %3623, %3607
  %3625 = fadd fast <3 x half> %3624, %3619
  %3626 = insertelement <3 x half> poison, half %3597, i64 0
  %3627 = shufflevector <3 x half> %3626, <3 x half> poison, <3 x i32> zeroinitializer
  %3628 = insertelement <3 x half> poison, half %3600, i64 0
  %3629 = shufflevector <3 x half> %3628, <3 x half> poison, <3 x i32> zeroinitializer
  %3630 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3596, <3 x half> %3627, <3 x half> %3629) #14
  %3631 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3630, <3 x half> %3625, <3 x half> splat (half 0xH3A66)) #14
  %3632 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3631, <3 x half> zeroinitializer) #14
  %3633 = fmul fast <3 x half> %3632, %3632
  %3634 = fadd fast <3 x half> %3587, splat (half 0xHBC00)
  %3635 = fadd fast <3 x half> %3634, %3588
  %3636 = fadd fast <3 x half> %3635, %3633
  %3637 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %3636, <3 x half> %3585) #14
  %3638 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3636, <3 x half> %3637, <3 x half> zeroinitializer) #14
  %3639 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3638, <3 x half> %3583, <3 x half> %1227) #14
  %3640 = icmp eq i32 %3285, 7
  %3641 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 12, i32 0
  %3642 = load i8, ptr addrspace(1) %3641, align 4, !alias.scope !98, !noalias !99
  %3643 = icmp ne i8 %3642, 0
  %3644 = select i1 %3640, i1 %3643, i1 false
  %3645 = insertelement <3 x i1> poison, i1 %3644, i64 0
  %3646 = shufflevector <3 x i1> %3645, <3 x i1> poison, <3 x i32> zeroinitializer
  %3647 = select fast <3 x i1> %3646, <3 x half> %3639, <3 x half> %3475
  %3648 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 19
  %3649 = load float, ptr addrspace(1) %3648, align 4, !tbaa !191, !alias.scope !98, !noalias !99
  %3650 = fcmp fast olt float %3649, 0x3F847AE140000000
  %3651 = or i1 %51, %3650
  br i1 %3651, label %3705, label %3652

3652:                                             ; preds = %_Z31renderSelectiveColorAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEEDhDhDhDh.exit
  %3653 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %18, i64 0, i32 1, i64 4, i32 4
  %3654 = load float, ptr addrspace(1) %3653, align 4, !tbaa !151, !alias.scope !153, !noalias !154
  %3655 = insertelement <3 x half> undef, half %1473, i64 0
  %3656 = insertelement <3 x half> %3655, half %1476, i64 1
  %3657 = fptrunc float %3654 to half
  %3658 = insertelement <3 x half> %3656, half %3657, i64 2
  %3659 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %3658) #14
  %3660 = shufflevector <3 x float> %3659, <3 x float> poison, <3 x i32> zeroinitializer
  %3661 = fmul fast <3 x float> %3660, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %3662 = shufflevector <3 x float> %3659, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3663 = fmul fast <3 x float> %3662, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %3664 = fadd fast <3 x float> %3661, %3663
  %3665 = shufflevector <3 x float> %3659, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3666 = fmul fast <3 x float> %3665, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %3667 = fadd fast <3 x float> %3664, %3666
  %3668 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %3667) #14
  %3669 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %3667) #14
  %3670 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %3669, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %3671 = fmul fast <3 x float> %3670, %3668
  %3672 = shufflevector <3 x float> %3671, <3 x float> poison, <3 x i32> zeroinitializer
  %3673 = fmul fast <3 x float> %3672, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %3674 = shufflevector <3 x float> %3671, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3675 = fmul fast <3 x float> %3674, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %3676 = fadd fast <3 x float> %3673, %3675
  %3677 = shufflevector <3 x float> %3671, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3678 = fmul fast <3 x float> %3677, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %3679 = fadd fast <3 x float> %3676, %3678
  %3680 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %3679) #14
  %3681 = extractelement <3 x half> %3680, i64 2
  %3682 = fcmp fast une half %3681, 0xH0000
  %3683 = extractelement <3 x half> %3680, i64 1
  %3684 = fcmp fast une half %3683, 0xH0000
  %3685 = select i1 %3682, i1 true, i1 %3684
  br i1 %3685, label %3686, label %3688

3686:                                             ; preds = %3652
  %3687 = tail call fast half @air.atan2.f16(half %3681, half %3683) #14
  br label %3688

3688:                                             ; preds = %3686, %3652
  %3689 = phi fast half [ %3687, %3686 ], [ 0xH0000, %3652 ]
  %3690 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 9, i32 20
  %3691 = load float, ptr addrspace(1) %3690, align 4, !tbaa !192, !alias.scope !98, !noalias !99
  %3692 = fmul fast float %3691, %3691
  %3693 = fmul fast float %3692, 0x3F19690E20000000
  %3694 = fptrunc float %3693 to half
  %3695 = insertelement <3 x half> <half poison, half poison, half 0xH3C00>, half %3689, i64 0
  %3696 = insertelement <3 x half> %3695, half %3694, i64 1
  %3697 = tail call fast fastcc <3 x half> @_Z17protectMaskFilterDv3_DhS_S_S_b(<3 x half> noundef %3647, <3 x half> noundef %3696, <3 x half> noundef %3696, <3 x half> noundef %3696, i1 noundef zeroext true) #17
  %3698 = extractelement <3 x half> %3697, i64 0
  %3699 = fpext half %3698 to float
  %3700 = fmul fast float %3649, %3699
  %3701 = fptrunc float %3700 to half
  %3702 = insertelement <3 x half> poison, half %3701, i64 0
  %3703 = shufflevector <3 x half> %3702, <3 x half> poison, <3 x i32> zeroinitializer
  %3704 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %3647, <3 x half> %3346, <3 x half> %3703) #14
  br label %3705

3705:                                             ; preds = %3688, %_Z31renderSelectiveColorAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEEDhDhDhDh.exit
  %3706 = phi <3 x half> [ %3704, %3688 ], [ %3647, %_Z31renderSelectiveColorAdjustmentsDv3_DhRU9MTLdevice18SSRCastAdjustmentsN5metal9texture2dIDhLNS3_6accessE0ELNS3_16memory_coherenceE0EvEEDhDhDhDh.exit ]
  switch i32 %3416, label %_Z26renderChannelMixForBWCastsDhDv3_DhRU9MTLdevice9SSRParamsRU9MTLdevice8SSRStats.exit [
    i32 4, label %3707
    i32 15, label %3745
  ]

3707:                                             ; preds = %3705
  %3708 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 10, i32 17
  %3709 = load float, ptr addrspace(1) %3708, align 4, !tbaa !193, !alias.scope !98, !noalias !99
  %3710 = fptrunc float %3709 to half
  %3711 = insertelement <3 x half> undef, half %3710, i64 0
  %3712 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 10, i32 18
  %3713 = load float, ptr addrspace(1) %3712, align 4, !tbaa !194, !alias.scope !98, !noalias !99
  %3714 = fptrunc float %3713 to half
  %3715 = insertelement <3 x half> %3711, half %3714, i64 1
  %3716 = getelementptr inbounds %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 10, i32 19
  %3717 = load float, ptr addrspace(1) %3716, align 4, !tbaa !195, !alias.scope !98, !noalias !99
  %3718 = fptrunc float %3717 to half
  %3719 = insertelement <3 x half> %3715, half %3718, i64 2
  %3720 = getelementptr %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 0
  %.val1 = load i32, ptr addrspace(1) %3720, align 4, !alias.scope !196, !noalias !197
  %3721 = tail call fastcc <3 x half> @_Z24getBWChannelMixFromStatsRU9MTLdevice8SSRStatsRU9MTLdevice9SSRParams(ptr addrspace(1) noundef align 4 dereferenceable(10640) %18, i32 %.val1) #17, !alias.scope !198, !noalias !199
  %3722 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %3706) #14
  %3723 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %3706) #14
  %3724 = fmul fast <3 x half> %3723, splat (half 0xH4A76)
  %3725 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %3723, <3 x half> splat (half 0xH36AA)) #14
  %3726 = fmul fast <3 x half> %3725, splat (half 0xH3C38)
  %3727 = fadd fast <3 x half> %3726, splat (half 0xHAB0A)
  %3728 = fcmp fast ogt <3 x half> %3723, splat (half 0xH1A69)
  %3729 = select fast <3 x i1> %3728, <3 x half> %3727, <3 x half> %3724
  %3730 = fmul fast <3 x half> %3729, %3722
  %3731 = tail call fast half @air.dot.v3f16(<3 x half> %3730, <3 x half> %3719) #14
  %3732 = tail call fast half @air.dot.v3f16(<3 x half> %3730, <3 x half> %3721) #14
  %3733 = tail call fast half @air.mix.f16(half %3731, half %3732, half %96) #14
  %3734 = insertelement <3 x half> poison, half %3733, i64 0
  %3735 = shufflevector <3 x half> %3734, <3 x half> poison, <3 x i32> zeroinitializer
  %3736 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %3735) #14
  %3737 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %3735) #14
  %3738 = fmul fast <3 x half> %3737, splat (half 0xH2CF4)
  %3739 = fadd fast <3 x half> %3737, splat (half 0xH2B0A)
  %3740 = fmul fast <3 x half> %3739, splat (half 0xH3B96)
  %3741 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %3740, <3 x half> splat (half 0xH40CD)) #14
  %3742 = fcmp fast ogt <3 x half> %3737, splat (half 0xH292D)
  %3743 = select fast <3 x i1> %3742, <3 x half> %3741, <3 x half> %3738
  %3744 = fmul fast <3 x half> %3743, %3736
  br label %_Z26renderChannelMixForBWCastsDhDv3_DhRU9MTLdevice9SSRParamsRU9MTLdevice8SSRStats.exit

3745:                                             ; preds = %3705
  %3746 = getelementptr %struct.SSRParams, ptr addrspace(1) %17, i64 0, i32 0
  %.val = load i32, ptr addrspace(1) %3746, align 4, !alias.scope !196, !noalias !197
  %3747 = tail call fastcc <3 x half> @_Z24getBWChannelMixFromStatsRU9MTLdevice8SSRStatsRU9MTLdevice9SSRParams(ptr addrspace(1) noundef align 4 dereferenceable(10640) %18, i32 %.val) #17, !alias.scope !198, !noalias !199
  %3748 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %3706) #14
  %3749 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %3706) #14
  %3750 = fmul fast <3 x half> %3749, splat (half 0xH4A76)
  %3751 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %3749, <3 x half> splat (half 0xH36AA)) #14
  %3752 = fmul fast <3 x half> %3751, splat (half 0xH3C38)
  %3753 = fadd fast <3 x half> %3752, splat (half 0xHAB0A)
  %3754 = fcmp fast ogt <3 x half> %3749, splat (half 0xH1A69)
  %3755 = select fast <3 x i1> %3754, <3 x half> %3753, <3 x half> %3750
  %3756 = fmul fast <3 x half> %3755, %3748
  %3757 = tail call fast half @air.dot.v3f16(<3 x half> %3756, <3 x half> %3756) #14
  %3758 = extractelement <3 x half> %3756, i64 0
  %3759 = extractelement <3 x half> %3756, i64 1
  %3760 = fadd fast half %3758, %3759
  %3761 = extractelement <3 x half> %3756, i64 2
  %3762 = fadd fast half %3760, %3761
  %3763 = fdiv fast half %3757, %3762
  %3764 = tail call fast half @air.dot.v3f16(<3 x half> %3756, <3 x half> %3747) #14
  %3765 = tail call fast half @air.mix.f16(half %3763, half %3764, half %96) #14
  %3766 = insertelement <3 x half> poison, half %3765, i64 0
  %3767 = shufflevector <3 x half> %3766, <3 x half> poison, <3 x i32> zeroinitializer
  %3768 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %3767) #14
  %3769 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %3767) #14
  %3770 = fmul fast <3 x half> %3769, splat (half 0xH2CF4)
  %3771 = fadd fast <3 x half> %3769, splat (half 0xH2B0A)
  %3772 = fmul fast <3 x half> %3771, splat (half 0xH3B96)
  %3773 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %3772, <3 x half> splat (half 0xH40CD)) #14
  %3774 = fcmp fast ogt <3 x half> %3769, splat (half 0xH292D)
  %3775 = select fast <3 x i1> %3774, <3 x half> %3773, <3 x half> %3770
  %3776 = fmul fast <3 x half> %3775, %3768
  br label %_Z26renderChannelMixForBWCastsDhDv3_DhRU9MTLdevice9SSRParamsRU9MTLdevice8SSRStats.exit

_Z26renderChannelMixForBWCastsDhDv3_DhRU9MTLdevice9SSRParamsRU9MTLdevice8SSRStats.exit: ; preds = %3745, %3707, %3705
  %3777 = phi <3 x half> [ %3744, %3707 ], [ %3776, %3745 ], [ %3706, %3705 ]
  br i1 %172, label %3778, label %3785

3778:                                             ; preds = %_Z26renderChannelMixForBWCastsDhDv3_DhRU9MTLdevice9SSRParamsRU9MTLdevice8SSRStats.exit
  %3779 = fmul fast float %252, 2.000000e+00
  %3780 = fcmp fast ogt float %252, 0.000000e+00
  %3781 = tail call fast float @air.fast_fabs.f32(float %3779) #14
  %3782 = fptrunc float %3781 to half
  %3783 = tail call fast half @air.mix.f16(half 0xH3C00, half 0xH3C00, half %3782) #14
  %3784 = select i1 %3780, half %3783, half 0xH3C00
  br label %3785

3785:                                             ; preds = %3778, %_Z26renderChannelMixForBWCastsDhDv3_DhRU9MTLdevice9SSRParamsRU9MTLdevice8SSRStats.exit
  %3786 = phi half [ 0xH3C00, %_Z26renderChannelMixForBWCastsDhDv3_DhRU9MTLdevice9SSRParamsRU9MTLdevice8SSRStats.exit ], [ %3784, %3778 ]
  %3787 = fdiv fast half %3786, %210
  %3788 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 3, i32 2, i32 0, i64 0
  %3789 = load <3 x float>, ptr addrspace(2) %3788, align 16, !tbaa !110, !alias.scope !106, !noalias !107
  %3790 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %3789) #14
  %3791 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 3, i32 2, i32 0, i64 1
  %3792 = load <3 x float>, ptr addrspace(2) %3791, align 16, !tbaa !110, !alias.scope !106, !noalias !107
  %3793 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %3792) #14
  %3794 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 3, i32 2, i32 0, i64 2
  %3795 = load <3 x float>, ptr addrspace(2) %3794, align 16, !tbaa !110, !alias.scope !106, !noalias !107
  %3796 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %3795) #14
  %3797 = shufflevector <3 x half> %3777, <3 x half> poison, <3 x i32> zeroinitializer
  %3798 = fmul fast <3 x half> %3790, %3797
  %3799 = shufflevector <3 x half> %3777, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %3800 = fmul fast <3 x half> %3793, %3799
  %3801 = fadd fast <3 x half> %3800, %3798
  %3802 = shufflevector <3 x half> %3777, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %3803 = fmul fast <3 x half> %3796, %3802
  %3804 = fadd fast <3 x half> %3801, %3803
  %3805 = insertelement <3 x half> poison, half %3787, i64 0
  %3806 = shufflevector <3 x half> %3805, <3 x half> poison, <3 x i32> zeroinitializer
  %3807 = fmul fast <3 x half> %3804, %3806
  %3808 = getelementptr inbounds %struct.SSRColorManagement.192, ptr addrspace(2) %16, i64 0, i32 3, i32 0
  %3809 = load i32, ptr addrspace(2) %3808, align 16, !tbaa !200, !alias.scope !106, !noalias !107
  switch i32 %3809, label %_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit [
    i32 0, label %3810
    i32 1, label %3810
    i32 2, label %3811
    i32 3, label %3816
    i32 4, label %3826
    i32 5, label %3836
    i32 6, label %3846
    i32 7, label %3862
    i32 8, label %3876
  ]

3810:                                             ; preds = %3785, %3785
  br label %_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

3811:                                             ; preds = %3785
  %3812 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %3807) #14
  %3813 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %3807) #14
  %3814 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %3813, <3 x half> splat (half 0xH3C00)) #14
  %3815 = fmul fast <3 x half> %3814, %3812
  br label %_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

3816:                                             ; preds = %3785
  %3817 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %3807) #14
  %3818 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %3807) #14
  %3819 = fmul fast <3 x half> %3818, splat (half 0xH4A76)
  %3820 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %3818, <3 x half> splat (half 0xH36AA)) #14
  %3821 = fmul fast <3 x half> %3820, splat (half 0xH3C38)
  %3822 = fadd fast <3 x half> %3821, splat (half 0xHAB0A)
  %3823 = fcmp fast ogt <3 x half> %3818, splat (half 0xH1A69)
  %3824 = select fast <3 x i1> %3823, <3 x half> %3822, <3 x half> %3819
  %3825 = fmul fast <3 x half> %3824, %3817
  br label %_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

3826:                                             ; preds = %3785
  %3827 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %3807) #14
  %3828 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %3807) #14
  %3829 = fmul fast <3 x half> %3828, splat (half 0xH4480)
  %3830 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %3828, <3 x half> splat (half 0xH3733)) #14
  %3831 = fmul fast <3 x half> %3830, splat (half 0xH3C65)
  %3832 = fadd fast <3 x half> %3831, splat (half 0xHAE56)
  %3833 = fcmp fast ogt <3 x half> %3828, splat (half 0xH249C)
  %3834 = select fast <3 x i1> %3833, <3 x half> %3832, <3 x half> %3829
  %3835 = fmul fast <3 x half> %3834, %3827
  br label %_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

3836:                                             ; preds = %3785
  %3837 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %3807) #14
  %3838 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %3807) #14
  %3839 = fmul fast <3 x half> %3838, splat (half 0xH4480)
  %3840 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %3838, <3 x half> splat (half 0xH3733)) #14
  %3841 = fmul fast <3 x half> %3840, splat (half 0xH3C66)
  %3842 = fadd fast <3 x half> %3841, splat (half 0xHAE5B)
  %3843 = fcmp fast ogt <3 x half> %3838, splat (half 0xH249F)
  %3844 = select fast <3 x i1> %3843, <3 x half> %3842, <3 x half> %3839
  %3845 = fmul fast <3 x half> %3844, %3837
  br label %_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

3846:                                             ; preds = %3785
  %3847 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %3807) #14
  %3848 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %3807) #14
  %3849 = tail call fast <3 x half> @air.log.v3f16(<3 x half> splat (half 0xH39B9)) #14
  %3850 = fmul fast <3 x half> %3849, splat (half 0xHB1B9)
  %3851 = fadd fast <3 x half> %3850, splat (half 0xH3800)
  %3852 = fmul fast <3 x half> %3848, splat (half 0xH4200)
  %3853 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %3852) #14
  %3854 = fmul fast <3 x half> %3848, splat (half 0xH4A00)
  %3855 = fadd fast <3 x half> %3854, splat (half 0xHB48E)
  %3856 = tail call fast <3 x half> @air.log.v3f16(<3 x half> %3855) #14
  %3857 = fmul fast <3 x half> %3856, splat (half 0xH31B9)
  %3858 = fadd fast <3 x half> %3851, %3857
  %3859 = fcmp fast ogt <3 x half> %3848, splat (half 0xH2D55)
  %3860 = select fast <3 x i1> %3859, <3 x half> %3858, <3 x half> %3853
  %3861 = fmul fast <3 x half> %3860, %3847
  br label %_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

3862:                                             ; preds = %3785
  %3863 = fadd fast <3 x half> %3807, splat (half 0xH20F0)
  %3864 = tail call fast <3 x half> @air.log2.v3f16(<3 x half> %3863) #14
  %3865 = fmul fast <3 x half> %3864, splat (half 0xH2D79)
  %3866 = fadd fast <3 x half> %3865, splat (half 0xH398C)
  %3867 = fcmp fast oge <3 x half> %3807, splat (half 0xH211F)
  %3868 = select fast <3 x i1> %3867, <3 x half> %3866, <3 x half> zeroinitializer
  %3869 = fadd fast <3 x half> %3807, splat (half 0xH2B38)
  %3870 = fmul fast <3 x half> %3869, %3869
  %3871 = fmul fast <3 x half> %3870, splat (half 0xH51E9)
  %3872 = fcmp fast ogt <3 x half> %3807, splat (half 0xHAB38)
  %3873 = fcmp fast olt <3 x half> %3807, splat (half 0xH211F)
  %3874 = and <3 x i1> %3872, %3873
  %3875 = select fast <3 x i1> %3874, <3 x half> %3871, <3 x half> %3868
  br label %_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

3876:                                             ; preds = %3785
  %3877 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %3807) #14
  %3878 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %3807) #14
  %3879 = fcmp fast ogt <3 x half> %3878, splat (half 0xH1800)
  %3880 = select fast <3 x i1> %3879, <3 x half> splat (half 0xHB900), <3 x half> %3878
  %3881 = fmul fast <3 x half> %3880, %3877
  br label %_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit

_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit: ; preds = %3876, %3862, %3846, %3836, %3826, %3816, %3811, %3810, %3785
  %3882 = phi <3 x half> [ zeroinitializer, %3785 ], [ %3881, %3876 ], [ %3875, %3862 ], [ %3861, %3846 ], [ %3845, %3836 ], [ %3835, %3826 ], [ %3825, %3816 ], [ %3815, %3811 ], [ %3807, %3810 ]
  %3883 = tail call ptr addrspace(4) @air.imageblock_data(<2 x i16> %21, i32 0, i16 0) #20
  %3884 = shufflevector <3 x half> %3882, <3 x half> poison, <4 x i32> <i32 0, i32 1, i32 2, i32 poison>
  %3885 = insertelement <4 x half> %3884, half 0xH3C00, i64 3
  %3886 = bitcast ptr addrspace(4) %3883 to ptr addrspace(4)
  store <4 x half> %3885, ptr addrspace(4) %3886, align 8, !tbaa !59
  call void @air.wg.barrier(i32 8, i32 1) #11
  %3887 = icmp eq <2 x i16> %21, zeroinitializer
  %3888 = tail call i1 @air.all.v2i1(<2 x i1> %3887) #14
  br i1 %3888, label %3889, label %3894

3889:                                             ; preds = %_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit
  %3890 = getelementptr inbounds %struct.SSRRenderROI, ptr addrspace(2) %19, i64 0, i32 2
  %3891 = load <2 x i16>, ptr addrspace(2) %3890, align 8, !tbaa !59, !alias.scope !62, !noalias !69
  %3892 = sub <2 x i16> %3891, %27
  %3893 = tail call <2 x i16> @air.min.u.v2i16(<2 x i16> %22, <2 x i16> %3892) #14
  tail call void @air.write_imageblock_slice_to_texture_2d.i16.v4f16(ptr addrspace(1) captures(none) %14, ptr addrspace(4) captures(none) %3883, i1 true, <2 x i16> zeroinitializer, <2 x i16> %3893, <2 x i16> %27, i16 0, i1 false, i32 2) #21
  br label %3894

3894:                                             ; preds = %3889, %_ZN3CMIL16curvedFromLinearIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_.exit
  ret void
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <2 x float> @air.convert.f.v2f32.u.v2i16(<2 x i16>) local_unnamed_addr #1

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(argmem: read)
declare { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none), ptr addrspace(2) readonly captures(none), <2 x float>, i1, <2 x i32>, i1, float, float, i32) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none)) local_unnamed_addr #3

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_clamp.f32(float, float, float) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_fmax.f32(float, float) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.sign.v3f16(<3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.fabs.v3f16(<3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.pow.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.exp.v3f16(<3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.powr.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.sqrt.v3f16(<3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.log2.f16(half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.pow.f16(half, half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_pow.f32(float, float) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmax.f16(half, half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.mix.f32(float, float, float) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.mix.v3f16(<3 x half>, <3 x half>, <3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.fmin.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i32 @air.get_width_texture_2d(ptr addrspace(1) readonly captures(none), i32) local_unnamed_addr #3

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.convert.f.f16.u.i32(i32) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.mix.f16(half, half, half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_fabs.f32(float) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z13ShadowsFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #4 {
  %4 = fpext half %1 to float
  %5 = fmul fast float %4, 0x400B333340000000
  %6 = fadd fast float %5, 0xBFF3333340000000
  %7 = fptrunc float %6 to half
  %8 = tail call fast half @air.mix.f16(half 0xH0000, half %7, half %2) #14
  %9 = fmul fast half %8, %8
  %10 = fcmp fast olt half %8, 0xH0000
  br i1 %10, label %11, label %14

11:                                               ; preds = %3
  %12 = tail call fast half @air.fmin.f16(half %9, half 0xH3C00) #14
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
  %23 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #14
  %24 = tail call fast half @air.dot.v3f16(<3 x half> %23, <3 x half> splat (half 0xH3555)) #14
  %25 = tail call fast half @air.sqrt.f16(half %24) #14
  %26 = fsub fast half 0xH2E66, %25
  %27 = tail call fast half @air.fmax.f16(half %26, half 0xH0000) #14
  %28 = fpext half %27 to float
  %29 = fmul fast float %22, %28
  %30 = extractelement <3 x half> %23, i64 2
  %31 = fadd fast half %30, 0xHB666
  %32 = fmul fast half %31, 0xH44FF
  %33 = tail call fast half @air.clamp.f16(half %32, half 0xH0000, half 0xH3C00) #14
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
  %45 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> splat (half 0xH3C00), <3 x half> %23, <3 x half> %44) #14
  %46 = fmul fast <3 x half> %45, %23
  %47 = extractelement <3 x half> %46, i64 2
  %48 = fadd fast half %47, 0xHB666
  %49 = fmul fast half %48, 0xH44FF
  %50 = tail call fast half @air.clamp.f16(half %49, half 0xH0000, half 0xH3C00) #14
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
  %64 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %63, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #14
  %65 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #14
  %66 = fadd fast <3 x half> %65, splat (half 0xHBC00)
  %67 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #14
  %68 = fpext half %25 to float
  %69 = fsub fast float 1.000000e+00, %68
  %70 = fmul fast float %69, %68
  %71 = fptrunc float %70 to half
  %72 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %64) #14
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
  %106 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %72, <3 x half> splat (half 0xH3666), <3 x half> %105) #14
  %107 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %106, <3 x half> %99, <3 x half> splat (half 0xH3A66)) #14
  %108 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %107, <3 x half> zeroinitializer) #14
  %109 = fmul fast <3 x half> %108, %108
  %110 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %109) #14
  %111 = fadd fast <3 x half> %66, %67
  %112 = fadd fast <3 x half> %111, %110
  ret <3 x half> %112
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z21ShadowsNegativeFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #4 {
  %4 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #14
  %5 = fneg fast half %2
  %6 = fpext half %5 to float
  %7 = fadd fast float %6, -1.000000e+00
  %8 = tail call fast float @air.fast_fmax.f32(float %7, float 1.000000e+00) #14
  %9 = fptrunc float %8 to half
  %10 = fpext half %1 to float
  %11 = fmul fast float %10, 0x400B333340000000
  %12 = fpext half %9 to float
  %13 = fmul fast float %12, 0x3FF3333340000000
  %14 = fsub fast float %11, %13
  %15 = fptrunc float %14 to half
  %16 = tail call fast half @air.mix.f16(half 0xH0000, half %15, half %2) #14
  %17 = fcmp fast olt half %16, 0xH0000
  %18 = fmul fast half %16, %16
  %19 = insertelement <3 x half> poison, half %18, i64 0
  %20 = shufflevector <3 x half> %19, <3 x half> poison, <3 x i32> zeroinitializer
  %21 = fmul fast <3 x half> %20, <half 0xH4180, half 0xH4180, half 0xH4100>
  %22 = select fast i1 %17, <3 x half> zeroinitializer, <3 x half> %21
  %23 = fmul fast <3 x half> %4, %4
  br i1 %17, label %24, label %26

24:                                               ; preds = %3
  %25 = tail call fast half @air.fmin.f16(half %18, half 0xH3C00) #14
  br label %26

26:                                               ; preds = %24, %3
  %27 = phi half [ %25, %24 ], [ 0xH0000, %3 ]
  %28 = fpext half %16 to float
  %29 = fmul fast float %28, 0x3FFD9999A0000000
  %30 = tail call fast half @air.dot.v3f16(<3 x half> %4, <3 x half> splat (half 0xH3555)) #14
  %31 = tail call fast half @air.sqrt.f16(half %30) #14
  %32 = fsub fast half 0xH2E66, %31
  %33 = tail call fast half @air.fmax.f16(half %32, half 0xH0000) #14
  %34 = fpext half %33 to float
  %35 = fmul fast float %29, %34
  %36 = extractelement <3 x half> %4, i64 2
  %37 = fadd fast half %36, 0xHB666
  %38 = fmul fast half %37, 0xH44FF
  %39 = tail call fast half @air.clamp.f16(half %38, half 0xH0000, half 0xH3C00) #14
  %40 = fmul fast half %39, 0xH4000
  %41 = fsub fast half 0xH4200, %40
  %42 = fmul fast half %39, %39
  %43 = fmul fast half %42, 0xH3B33
  %44 = fmul fast half %43, %41
  %45 = fsub fast half 0xH3C00, %44
  %46 = insertelement <3 x half> poison, half %45, i64 0
  %47 = shufflevector <3 x half> %46, <3 x half> poison, <3 x i32> zeroinitializer
  %48 = fmul fast <3 x half> %47, %22
  %49 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %4, <3 x half> %23, <3 x half> %48) #14
  %50 = extractelement <3 x half> %49, i64 2
  %51 = fadd fast half %50, 0xHB666
  %52 = fmul fast half %51, 0xH44FF
  %53 = tail call fast half @air.clamp.f16(half %52, half 0xH0000, half 0xH3C00) #14
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
  %67 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %66, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #14
  %68 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #14
  %69 = fadd fast <3 x half> %68, splat (half 0xHBC00)
  %70 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #14
  %71 = fpext half %31 to float
  %72 = fsub fast float 1.000000e+00, %71
  %73 = fmul fast float %72, %71
  %74 = fptrunc float %73 to half
  %75 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %67) #14
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
  %106 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %75, <3 x half> splat (half 0xH3666), <3 x half> %105) #14
  %107 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %106, <3 x half> %101, <3 x half> splat (half 0xH3A66)) #14
  %108 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %107, <3 x half> zeroinitializer) #14
  %109 = fmul fast <3 x half> %108, %108
  %110 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %109) #14
  %111 = fadd fast <3 x half> %69, %70
  %112 = fadd fast <3 x half> %111, %110
  %113 = extractelement <3 x half> %0, i64 0
  %114 = extractelement <3 x half> %0, i64 1
  %115 = tail call fast half @air.fmin.f16(half %113, half %114) #14
  %116 = extractelement <3 x half> %0, i64 2
  %117 = tail call fast half @air.fmin.f16(half %115, half %116) #14
  %118 = tail call fast half @air.fmax.f16(half %113, half %114) #14
  %119 = tail call fast half @air.fmax.f16(half %118, half %116) #14
  %120 = fsub fast half %119, %117
  %121 = fpext half %120 to float
  %122 = fcmp fast ogt float %121, 0x3EE4F8B580000000
  br i1 %122, label %123, label %142

123:                                              ; preds = %26
  %124 = extractelement <3 x half> %112, i64 0
  %125 = extractelement <3 x half> %112, i64 1
  %126 = tail call fast half @air.fmax.f16(half %124, half %125) #14
  %127 = extractelement <3 x half> %112, i64 2
  %128 = tail call fast half @air.fmax.f16(half %126, half %127) #14
  %129 = tail call fast half @air.fmin.f16(half %124, half %125) #14
  %130 = tail call fast half @air.fmin.f16(half %129, half %127) #14
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
define internal fastcc <3 x half> @_Z14contrastFilterDv3_DhDh(<3 x half> noundef %0, half noundef %1) unnamed_addr #4 {
  %3 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #14
  %4 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #14
  %5 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #14
  %6 = tail call fast half @air.dot.v3f16(<3 x half> %5, <3 x half> splat (half 0xH3555)) #14
  %7 = tail call fast half @air.sqrt.f16(half %6) #14
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
  %23 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %5) #14
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
  %57 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %23, <3 x half> splat (half 0xH3800), <3 x half> %56) #14
  %58 = fpext half %18 to float
  %59 = fadd fast float %58, 0x3FE99999A0000000
  %60 = fptrunc float %59 to half
  %61 = insertelement <3 x half> poison, half %60, i64 0
  %62 = shufflevector <3 x half> %61, <3 x half> poison, <3 x i32> zeroinitializer
  %63 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %57, <3 x half> %52, <3 x half> %62) #14
  %64 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %63, <3 x half> zeroinitializer) #14
  %65 = fmul fast <3 x half> %64, %64
  %66 = fadd fast <3 x half> %3, splat (half 0xHBC00)
  %67 = fadd fast <3 x half> %66, %4
  %68 = fadd fast <3 x half> %67, %65
  %69 = extractelement <3 x half> %0, i64 0
  %70 = extractelement <3 x half> %0, i64 1
  %71 = extractelement <3 x half> %0, i64 2
  %72 = tail call fast half @air.fmin3.f16(half %69, half %70, half %71) #14
  %73 = tail call fast half @air.fmax3.f16(half %69, half %70, half %71) #14
  %74 = fsub fast half %73, %72
  %75 = fpext half %74 to float
  %76 = fcmp fast ogt float %75, 0x3EE4F8B580000000
  br i1 %76, label %77, label %94

77:                                               ; preds = %2
  %78 = extractelement <3 x half> %68, i64 0
  %79 = extractelement <3 x half> %68, i64 1
  %80 = extractelement <3 x half> %68, i64 2
  %81 = tail call fast half @air.fmax3.f16(half %78, half %79, half %80) #14
  %82 = tail call fast half @air.fmin3.f16(half %78, half %79, half %80) #14
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

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(argmem: read)
define internal fastcc <3 x half> @_Z11whitesCurveDv3_DhN5metal9texture2dIDhLNS0_6accessE0ELNS0_16memory_coherenceE0EvEEDhDh(<3 x half> noundef %0, ptr addrspace(1) readonly captures(none) %1, half noundef %2, half noundef %3) unnamed_addr #5 {
  %5 = shufflevector <3 x half> %0, <3 x half> poison, <3 x i32> zeroinitializer
  %6 = fmul fast <3 x half> %5, <half 0xH383C, half 0xH2E4C, half 0xH2452>
  %7 = shufflevector <3 x half> %0, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %8 = fmul fast <3 x half> %7, <half 0xH3548, half 0xH3AFD, half 0xH2F88>
  %9 = fadd fast <3 x half> %6, %8
  %10 = shufflevector <3 x half> %0, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %11 = fmul fast <3 x half> %10, <half 0xH307F, half 0xH2734, half 0xH3AEC>
  %12 = fadd fast <3 x half> %9, %11
  %13 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %12) #14
  %14 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %13, <3 x half> splat (half 0xH3872)) #14
  %15 = extractelement <3 x half> %14, i64 0
  %16 = extractelement <3 x half> %14, i64 1
  %17 = extractelement <3 x half> %14, i64 2
  %18 = tail call fast half @air.fmin3.f16(half %15, half %16, half %17) #14
  %19 = tail call i32 @air.get_width_texture_2d(ptr addrspace(1) readonly captures(none) %1, i32 0) #16
  %20 = add nsw i32 %19, -1
  %21 = tail call fast half @air.convert.f.f16.s.i32(i32 %20) #14
  %22 = fmul fast half %21, %18
  %23 = fpext half %22 to float
  %24 = fadd fast float %23, 5.000000e-01
  %25 = insertelement <2 x float> <float poison, float 5.000000e-01>, float %24, i64 0
  %26 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %1, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %25, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #15
  %27 = extractvalue { <4 x half>, i8 } %26, 0
  %28 = extractelement <4 x half> %27, i64 0
  %29 = tail call fast half @air.clamp.f16(half %28, half 0xH0000, half 0xH3C00) #14
  %30 = fcmp fast ogt half %18, 0xH3A00
  %31 = select i1 %30, half 0xH3C00, half %29
  %32 = tail call fast half @air.mix.f16(half %18, half %31, half %2) #14
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
  %46 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %14, <3 x half> %45, <3 x half> %44) #14
  br label %47

47:                                               ; preds = %39, %34
  %48 = phi <3 x half> [ %38, %34 ], [ %41, %39 ]
  %49 = phi <3 x half> [ %36, %34 ], [ %44, %39 ]
  %50 = phi fast <3 x half> [ %14, %34 ], [ %46, %39 ]
  %51 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %12, <3 x half> splat (half 0xH3C00)) #14
  %52 = fadd fast <3 x half> %51, splat (half 0xHBC00)
  %53 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %12, <3 x half> zeroinitializer) #14
  %54 = tail call fast half @air.mix.f16(half %18, half %32, half %3) #14
  %55 = fadd fast <3 x half> %48, %14
  %56 = fsub fast <3 x half> %55, %49
  %57 = insertelement <3 x half> poison, half %54, i64 0
  %58 = shufflevector <3 x half> %57, <3 x half> poison, <3 x i32> zeroinitializer
  %59 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %14, <3 x half> %56, <3 x half> %58) #14
  %60 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %50, <3 x half> %59, <3 x half> %49) #14
  %61 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %60, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #14
  %62 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %61, <3 x half> splat (half 0xH3F33)) #14
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
  %73 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %72, <3 x half> zeroinitializer) #14
  ret <3 x half> %73
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z10airyFilterDv3_DhDh(<3 x half> noundef %0, half noundef %1) unnamed_addr #4 {
  %3 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #14
  %4 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #14
  %5 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #14
  %6 = extractelement <3 x half> %5, i64 0
  %7 = extractelement <3 x half> %5, i64 1
  %8 = fadd fast half %6, %7
  %9 = extractelement <3 x half> %5, i64 2
  %10 = fadd fast half %8, %9
  %11 = fdiv fast half 0xH3C00, %10
  %12 = fmul fast half %11, %6
  %13 = fmul fast half %11, %7
  %14 = fmul fast half %11, %9
  %15 = tail call fast half @air.fmax.f16(half %12, half %13) #14
  %16 = tail call fast half @air.fmax.f16(half %13, half %14) #14
  %17 = fadd fast half %15, 0xHB555
  %18 = fadd fast half %17, %16
  %19 = fmul fast half %18, 0xH3DFF
  %20 = tail call fast half @air.clamp.f16(half %19, half 0xH0000, half 0xH3C00) #14
  %21 = fmul fast half %20, %20
  %22 = fmul fast half %20, 0xH4000
  %23 = fsub fast half 0xH4200, %22
  %24 = fmul fast half %21, %23
  %25 = tail call fast half @air.dot.v3f16(<3 x half> %5, <3 x half> splat (half 0xH3555)) #14
  %26 = tail call fast half @air.sqrt.f16(half %25) #14
  %27 = insertelement <3 x half> poison, half %1, i64 0
  %28 = shufflevector <3 x half> %27, <3 x half> poison, <3 x i32> zeroinitializer
  %29 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %5, <3 x half> %28) #14
  %30 = fmul fast half %24, %26
  %31 = insertelement <3 x half> poison, half %30, i64 0
  %32 = shufflevector <3 x half> %31, <3 x half> poison, <3 x i32> zeroinitializer
  %33 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %5, <3 x half> %29, <3 x half> %32) #14
  %34 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %33) #14
  %35 = fadd fast <3 x half> %3, splat (half 0xHBC00)
  %36 = fadd fast <3 x half> %35, %4
  %37 = fadd fast <3 x half> %36, %34
  ret <3 x half> %37
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.fmax.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.saturate.v3f16(<3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmax3.f16(half, half, half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z15smoothSatFilterDv3_DhDh(<3 x half> noundef %0, half noundef %1) unnamed_addr #6 {
  %3 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #14
  %4 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %3) #14
  %5 = shufflevector <3 x float> %4, <3 x float> poison, <3 x i32> zeroinitializer
  %6 = fmul fast <3 x float> %5, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %7 = shufflevector <3 x float> %4, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %8 = fmul fast <3 x float> %7, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %9 = fadd fast <3 x float> %6, %8
  %10 = shufflevector <3 x float> %4, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %11 = fmul fast <3 x float> %10, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %12 = fadd fast <3 x float> %9, %11
  %13 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %12) #14
  %14 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %12) #14
  %15 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %14, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %16 = fmul fast <3 x float> %15, %13
  %17 = shufflevector <3 x float> %16, <3 x float> poison, <3 x i32> zeroinitializer
  %18 = fmul fast <3 x float> %17, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %19 = shufflevector <3 x float> %16, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %20 = fmul fast <3 x float> %19, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %21 = fadd fast <3 x float> %18, %20
  %22 = shufflevector <3 x float> %16, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %23 = fmul fast <3 x float> %22, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %24 = fadd fast <3 x float> %21, %23
  %25 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %24) #14
  %26 = extractelement <3 x half> %25, i64 2
  %27 = fcmp fast une half %26, 0xH0000
  %28 = extractelement <3 x half> %25, i64 1
  %29 = fcmp fast une half %28, 0xH0000
  %30 = select i1 %27, i1 true, i1 %29
  br i1 %30, label %31, label %33

31:                                               ; preds = %2
  %32 = tail call fast half @air.atan2.f16(half %26, half %28) #14
  br label %33

33:                                               ; preds = %31, %2
  %34 = phi fast half [ %32, %31 ], [ 0xH0000, %2 ]
  %35 = shufflevector <3 x half> %25, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %36 = tail call fast half @air.dot.v2f16(<2 x half> %35, <2 x half> %35) #14
  %37 = tail call fast half @air.sqrt.f16(half %36) #14
  %38 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #14
  %39 = fadd fast <3 x half> %38, splat (half 0xHBC00)
  %40 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #14
  %41 = fmul fast half %37, %1
  %42 = tail call fast half @air.cos.f16(half %34) #14
  %43 = fmul fast half %42, %41
  %44 = insertelement <3 x half> %25, half %43, i64 1
  %45 = tail call fast half @air.sin.f16(half %34) #14
  %46 = fmul fast half %45, %41
  %47 = insertelement <3 x half> %44, half %46, i64 2
  %48 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %47) #14
  %49 = shufflevector <3 x float> %48, <3 x float> poison, <3 x i32> zeroinitializer
  %50 = shufflevector <3 x float> %48, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %51 = fmul fast <3 x float> %50, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %52 = fadd fast <3 x float> %51, %49
  %53 = shufflevector <3 x float> %48, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %54 = fmul fast <3 x float> %53, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %55 = fadd fast <3 x float> %52, %54
  %56 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %55) #14
  %57 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %55) #14
  %58 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %57, <3 x float> splat (float 0x40029ACA60000000)) #14
  %59 = fmul fast <3 x float> %58, %56
  %60 = shufflevector <3 x float> %59, <3 x float> poison, <3 x i32> zeroinitializer
  %61 = fmul fast <3 x float> %60, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %62 = shufflevector <3 x float> %59, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %63 = fmul fast <3 x float> %62, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %64 = fadd fast <3 x float> %61, %63
  %65 = shufflevector <3 x float> %59, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %66 = fmul fast <3 x float> %65, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %67 = fadd fast <3 x float> %64, %66
  %68 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %67) #14
  %69 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %68) #14
  %70 = fadd fast <3 x half> %39, %40
  %71 = fadd fast <3 x half> %70, %69
  %72 = fpext half %1 to float
  %73 = fcmp fast olt float %72, 0x3F947AE140000000
  %74 = shufflevector <3 x half> %71, <3 x half> poison, <3 x i32> <i32 1, i32 1, i32 1>
  %75 = select fast i1 %73, <3 x half> %74, <3 x half> %71
  ret <3 x half> %75
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.dot.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.sqrt.f16(half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z13lightenFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #4 {
  %4 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #14
  %5 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #14
  %6 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #14
  %7 = tail call fast half @air.dot.v3f16(<3 x half> %6, <3 x half> <half 0xH3800, half 0xH3800, half 0xH0000>) #14
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
  %23 = tail call fast half @air.pow.f16(half %15, half 0xH3800) #14
  %24 = tail call fast half @air.clamp.f16(half %23, half 0xH0000, half 0xH3C00) #14
  %25 = insertelement <3 x half> poison, half %22, i64 0
  %26 = shufflevector <3 x half> %25, <3 x half> poison, <3 x i32> zeroinitializer
  %27 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %6, <3 x half> %26) #14
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
  %41 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %27, <3 x half> %37, <3 x half> %40) #14
  %42 = fptrunc float %31 to half
  %43 = insertelement <3 x half> poison, half %42, i64 0
  %44 = shufflevector <3 x half> %43, <3 x half> poison, <3 x i32> zeroinitializer
  %45 = fmul fast <3 x half> %27, %44
  %46 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %27, <3 x half> %45, <3 x half> %40) #14
  %47 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %46, <3 x half> %41, <3 x half> %29) #14
  %48 = tail call fast half @air.sqrt.f16(half %7) #14
  %49 = insertelement <3 x half> poison, half %48, i64 0
  %50 = shufflevector <3 x half> %49, <3 x half> poison, <3 x i32> zeroinitializer
  %51 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %47, <3 x half> %6, <3 x half> %50) #14
  %52 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %51, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #14
  %53 = fpext half %48 to float
  %54 = fsub fast float 1.000000e+00, %53
  %55 = fmul fast float %54, %53
  %56 = fptrunc float %55 to half
  %57 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %52) #14
  %58 = tail call fast half @air.sqrt.f16(half %1) #14
  %59 = fmul fast half %56, %2
  %60 = fmul fast half %59, 0xH34CD
  %61 = fmul fast half %59, 0xHB4CD
  %62 = fmul fast half %61, %58
  %63 = fpext half %60 to float
  %64 = fmul fast float %63, 0x3FD322D0E0000000
  %65 = fptrunc float %64 to half
  %66 = insertelement <3 x half> poison, half %65, i64 0
  %67 = fmul fast <3 x half> %57, %66
  %68 = shufflevector <3 x half> %67, <3 x half> poison, <3 x i32> zeroinitializer
  %69 = shufflevector <3 x half> %57, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %70 = fmul fast float %63, 0x3FE2C8B440000000
  %71 = fptrunc float %70 to half
  %72 = insertelement <3 x half> poison, half %71, i64 0
  %73 = shufflevector <3 x half> %72, <3 x half> poison, <3 x i32> zeroinitializer
  %74 = fmul fast <3 x half> %69, %73
  %75 = shufflevector <3 x half> %57, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %76 = fmul fast float %63, 0x3FBD2F1AA0000000
  %77 = fptrunc float %76 to half
  %78 = insertelement <3 x half> poison, half %77, i64 0
  %79 = shufflevector <3 x half> %78, <3 x half> poison, <3 x i32> zeroinitializer
  %80 = fmul fast <3 x half> %75, %79
  %81 = insertelement <3 x half> poison, half %62, i64 0
  %82 = shufflevector <3 x half> %81, <3 x half> poison, <3 x i32> zeroinitializer
  %83 = fadd fast <3 x half> %74, %57
  %84 = fadd fast <3 x half> %83, %68
  %85 = fadd fast <3 x half> %84, %80
  %86 = fadd fast <3 x half> %85, %82
  %87 = insertelement <3 x half> poison, half %58, i64 0
  %88 = shufflevector <3 x half> %87, <3 x half> poison, <3 x i32> zeroinitializer
  %89 = insertelement <3 x half> poison, half %61, i64 0
  %90 = shufflevector <3 x half> %89, <3 x half> poison, <3 x i32> zeroinitializer
  %91 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %57, <3 x half> %88, <3 x half> %90) #14
  %92 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %91, <3 x half> %86, <3 x half> splat (half 0xH3A66)) #14
  %93 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %92, <3 x half> zeroinitializer) #14
  %94 = fmul fast <3 x half> %93, %93
  %95 = fadd fast <3 x half> %4, splat (half 0xHBC00)
  %96 = fadd fast <3 x half> %95, %5
  %97 = fadd fast <3 x half> %96, %94
  ret <3 x half> %97
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fabs.f16(half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z21negativeLightenFilterDv3_DhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #4 {
  %4 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #14
  %5 = tail call fast half @air.dot.v3f16(<3 x half> %4, <3 x half> <half 0xH363D, half 0xH3800, half 0xH2F0A>) #14
  %6 = fcmp fast ogt half %5, 0xH0000
  br i1 %6, label %7, label %15

7:                                                ; preds = %3
  %8 = tail call fast half @air.pow.f16(half %5, half %2) #14
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
  %19 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %4, <3 x half> %18) #14
  %20 = fmul fast half %1, 0xH42CD
  %21 = fadd fast half %20, 0xHBCCD
  %22 = fpext half %21 to float
  %23 = fadd fast float %22, 0x3FF0FDBF40000000
  %24 = fmul fast float %23, 0x3FDA374BC0000000
  %25 = fptrunc float %24 to half
  %26 = tail call fast half @air.pow.f16(half %25, half 0xH3400) #14
  %27 = tail call fast half @air.dot.v3f16(<3 x half> %4, <3 x half> <half 0xH3800, half 0xH3800, half 0xH0000>) #14
  %28 = fpext half %27 to float
  %29 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #14
  %30 = fadd fast <3 x half> %29, splat (half 0xHBC00)
  %31 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #14
  %32 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %19, <3 x half> %16, <3 x half> splat (half 0xH3A66)) #14
  %33 = insertelement <3 x half> poison, half %26, i64 0
  %34 = shufflevector <3 x half> %33, <3 x half> poison, <3 x i32> zeroinitializer
  %35 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %4, <3 x half> %32, <3 x half> %34) #14
  %36 = tail call fast <3 x half> @air.clamp.v3f16(<3 x half> %35, <3 x half> zeroinitializer, <3 x half> splat (half 0xH3C00)) #14
  %37 = fpext half %2 to float
  %38 = tail call fast float @air.fast_sqrt.f32(float %28) #14
  %39 = fsub fast float 1.000000e+00, %38
  %40 = fmul fast float %39, %38
  %41 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %36) #14
  %42 = tail call fast half @air.sqrt.f16(half %1) #14
  %43 = fmul fast float %40, %37
  %44 = fmul fast float %43, 0x3FD3333340000000
  %45 = fptrunc float %44 to half
  %46 = fneg fast half %45
  %47 = fmul fast half %42, %46
  %48 = fpext half %45 to float
  %49 = fmul fast float %48, 0x3FD322D0E0000000
  %50 = fptrunc float %49 to half
  %51 = insertelement <3 x half> poison, half %50, i64 0
  %52 = fmul fast <3 x half> %41, %51
  %53 = shufflevector <3 x half> %52, <3 x half> poison, <3 x i32> zeroinitializer
  %54 = shufflevector <3 x half> %41, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %55 = fmul fast float %48, 0x3FE2C8B440000000
  %56 = fptrunc float %55 to half
  %57 = insertelement <3 x half> poison, half %56, i64 0
  %58 = shufflevector <3 x half> %57, <3 x half> poison, <3 x i32> zeroinitializer
  %59 = fmul fast <3 x half> %54, %58
  %60 = shufflevector <3 x half> %41, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %61 = fmul fast float %48, 0x3FBD2F1AA0000000
  %62 = fptrunc float %61 to half
  %63 = insertelement <3 x half> poison, half %62, i64 0
  %64 = shufflevector <3 x half> %63, <3 x half> poison, <3 x i32> zeroinitializer
  %65 = fmul fast <3 x half> %60, %64
  %66 = insertelement <3 x half> poison, half %47, i64 0
  %67 = shufflevector <3 x half> %66, <3 x half> poison, <3 x i32> zeroinitializer
  %68 = fadd fast <3 x half> %59, %41
  %69 = fadd fast <3 x half> %68, %53
  %70 = fadd fast <3 x half> %69, %65
  %71 = fadd fast <3 x half> %70, %67
  %72 = insertelement <3 x half> poison, half %42, i64 0
  %73 = shufflevector <3 x half> %72, <3 x half> poison, <3 x i32> zeroinitializer
  %74 = fmul fast float %43, 0xBFD3333340000000
  %75 = fptrunc float %74 to half
  %76 = insertelement <3 x half> poison, half %75, i64 0
  %77 = shufflevector <3 x half> %76, <3 x half> poison, <3 x i32> zeroinitializer
  %78 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %41, <3 x half> %73, <3 x half> %77) #14
  %79 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %78, <3 x half> %71, <3 x half> splat (half 0xH3A66)) #14
  %80 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %79, <3 x half> zeroinitializer) #14
  %81 = fmul fast <3 x half> %80, %80
  %82 = fadd fast <3 x half> %30, %31
  %83 = fadd fast <3 x half> %82, %81
  ret <3 x half> %83
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x float> @air.sign.v3f32(<3 x float>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x float> @air.fast_fabs.v3f32(<3 x float>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x float> @air.fast_pow.v3f32(<3 x float>, <3 x float>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.atan2.f16(half, half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_exp.f32(float) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.cos.f16(half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.sin.f16(half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z7RichSatDv3_DhDhDhDh(<3 x half> noundef %0, half noundef %1, half noundef %2) unnamed_addr #6 {
  %4 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #14
  %5 = extractelement <3 x half> %4, i64 0
  %6 = extractelement <3 x half> %4, i64 1
  %7 = fadd fast half %5, %6
  %8 = extractelement <3 x half> %4, i64 2
  %9 = fadd fast half %7, %8
  %10 = fdiv fast half 0xH3C00, %9
  %11 = fmul fast half %10, %5
  %12 = fmul fast half %10, %6
  %13 = fmul fast half %10, %8
  %14 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %4) #14
  %15 = shufflevector <3 x float> %14, <3 x float> poison, <3 x i32> zeroinitializer
  %16 = fmul fast <3 x float> %15, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %17 = shufflevector <3 x float> %14, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %18 = fmul fast <3 x float> %17, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %19 = fadd fast <3 x float> %16, %18
  %20 = shufflevector <3 x float> %14, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %21 = fmul fast <3 x float> %20, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %22 = fadd fast <3 x float> %19, %21
  %23 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %22) #14
  %24 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %22) #14
  %25 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %24, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %26 = fmul fast <3 x float> %25, %23
  %27 = shufflevector <3 x float> %26, <3 x float> poison, <3 x i32> zeroinitializer
  %28 = fmul fast <3 x float> %27, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %29 = shufflevector <3 x float> %26, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %30 = fmul fast <3 x float> %29, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %31 = fadd fast <3 x float> %28, %30
  %32 = shufflevector <3 x float> %26, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %33 = fmul fast <3 x float> %32, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %34 = fadd fast <3 x float> %31, %33
  %35 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %34) #14
  %36 = shufflevector <3 x half> %35, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %37 = tail call fast half @air.dot.v2f16(<2 x half> %36, <2 x half> %36) #14
  %38 = tail call fast half @air.sqrt.f16(half %37) #14
  %39 = extractelement <3 x half> %35, i64 2
  %40 = fcmp fast une half %39, 0xH0000
  %41 = extractelement <3 x half> %35, i64 1
  %42 = fcmp fast une half %41, 0xH0000
  %43 = select i1 %40, i1 true, i1 %42
  br i1 %43, label %44, label %46

44:                                               ; preds = %3
  %45 = tail call fast half @air.atan2.f16(half %39, half %41) #14
  br label %46

46:                                               ; preds = %44, %3
  %47 = phi fast half [ %45, %44 ], [ 0xH0000, %3 ]
  %48 = fmul fast half %38, %1
  %49 = fpext half %11 to float
  %50 = insertelement <2 x float> undef, float %49, i64 0
  %51 = fpext half %12 to float
  %52 = insertelement <2 x float> %50, float %51, i64 1
  %53 = fadd fast <2 x float> %52, splat (float 0xBFD55553E0000000)
  %54 = tail call fast float @air.dot.v2f32(<2 x float> %53, <2 x float> %53) #14
  %55 = tail call fast float @air.fast_sqrt.f32(float %54) #14
  %56 = fptrunc float %55 to half
  %57 = fpext half %13 to float
  %58 = insertelement <2 x float> %50, float %57, i64 1
  %59 = fadd fast <2 x float> %58, splat (float 0xBFD55553E0000000)
  %60 = tail call fast float @air.dot.v2f32(<2 x float> %59, <2 x float> %59) #14
  %61 = tail call fast float @air.fast_sqrt.f32(float %60) #14
  %62 = fptrunc float %61 to half
  %63 = insertelement <2 x float> undef, float %51, i64 0
  %64 = insertelement <2 x float> %63, float %57, i64 1
  %65 = fadd fast <2 x float> %64, splat (float 0xBFD55553E0000000)
  %66 = tail call fast float @air.dot.v2f32(<2 x float> %65, <2 x float> %65) #14
  %67 = tail call fast float @air.fast_sqrt.f32(float %66) #14
  %68 = fptrunc float %67 to half
  %69 = tail call fast half @air.fmax3.f16(half %56, half %62, half %68) #14
  %70 = tail call fast half @air.sqrt.f16(half %69) #14
  %71 = tail call fast half @air.clamp.f16(half %70, half 0xH0000, half 0xH3C00) #14
  %72 = fmul fast half %71, %71
  %73 = fmul fast half %71, 0xH4000
  %74 = fsub fast half 0xH4200, %73
  %75 = fmul fast half %72, %74
  %76 = fpext half %75 to float
  %77 = fsub fast float 1.000000e+00, %76
  %78 = fmul fast float %76, 2.000000e+00
  %79 = fmul fast float %78, %77
  %80 = tail call fast float @air.fast_fmin.f32(float %79, float 1.000000e+00) #14
  %81 = fptrunc float %80 to half
  %82 = fcmp fast ogt half %1, 0xH3A00
  %83 = fcmp fast ogt half %2, 0xH4200
  %84 = select i1 %82, i1 %83, i1 false
  br i1 %84, label %85, label %91

85:                                               ; preds = %46
  %86 = fpext half %1 to float
  %87 = fadd fast float %86, -7.500000e-01
  %88 = fpext half %81 to float
  %89 = fadd fast float %87, %88
  %90 = tail call fast float @air.fast_fmin.f32(float %89, float 1.000000e+00) #14
  br label %93

91:                                               ; preds = %46
  %92 = fpext half %81 to float
  br label %93

93:                                               ; preds = %91, %85
  %94 = phi fast float [ %90, %85 ], [ %92, %91 ]
  %95 = fptrunc float %94 to half
  %96 = extractelement <3 x half> %35, i64 0
  %97 = fmul fast half %96, %95
  %98 = tail call fast half @air.mix.f16(half %38, half %48, half %97) #14
  %99 = tail call fast half @air.cos.f16(half %47) #14
  %100 = fmul fast half %99, %98
  %101 = insertelement <3 x half> %35, half %100, i64 1
  %102 = tail call fast half @air.sin.f16(half %47) #14
  %103 = fmul fast half %102, %98
  %104 = insertelement <3 x half> %101, half %103, i64 2
  %105 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %104) #14
  %106 = shufflevector <3 x float> %105, <3 x float> poison, <3 x i32> zeroinitializer
  %107 = shufflevector <3 x float> %105, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %108 = fmul fast <3 x float> %107, <float 0x3FB8FA4700000000, float 0xBFBD270280000000, float 0x3FA0B2ED80000000>
  %109 = fadd fast <3 x float> %108, %106
  %110 = shufflevector <3 x float> %105, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %111 = fmul fast <3 x float> %110, <float 0x3FCA44DC20000000, float 0x3FC10D4280000000, float 0xBFE5A90F40000000>
  %112 = fadd fast <3 x float> %109, %111
  %113 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %112) #14
  %114 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %112) #14
  %115 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %114, <3 x float> splat (float 0x40029ACA60000000)) #14
  %116 = fmul fast <3 x float> %115, %113
  %117 = shufflevector <3 x float> %116, <3 x float> poison, <3 x i32> zeroinitializer
  %118 = fmul fast <3 x float> %117, <float 0x4015E38B80000000, float 0xBFF200FDA0000000, float 0x3F9E845300000000>
  %119 = shufflevector <3 x float> %116, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %120 = fmul fast <3 x float> %119, <float 0xC012915E00000000, float 0x4002586A00000000, float 0xBFC8BA2560000000>
  %121 = fadd fast <3 x float> %118, %120
  %122 = shufflevector <3 x float> %116, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %123 = fmul fast <3 x float> %122, <float 0x3FC5B6AB00000000, float 0xBFC57D9700000000, float 0x3FF29E4D40000000>
  %124 = fadd fast <3 x float> %121, %123
  %125 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %124) #14
  %126 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %125) #14
  %127 = fadd fast half %1, 0xHBC00
  %128 = fmul fast half %127, %2
  %129 = fadd fast half %128, 0xH3C00
  %130 = insertelement <3 x half> poison, half %129, i64 0
  %131 = shufflevector <3 x half> %130, <3 x half> poison, <3 x i32> zeroinitializer
  %132 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %126, <3 x half> %131) #14
  %133 = tail call fast half @air.dot.v3f16(<3 x half> %132, <3 x half> splat (half 0xH3555)) #14
  %134 = fcmp fast ogt half %133, 0xH0000
  br i1 %134, label %135, label %143

135:                                              ; preds = %93
  %136 = tail call fast half @air.dot.v3f16(<3 x half> %126, <3 x half> splat (half 0xH3555)) #14
  %137 = insertelement <3 x half> poison, half %133, i64 0
  %138 = shufflevector <3 x half> %137, <3 x half> poison, <3 x i32> zeroinitializer
  %139 = insertelement <3 x half> poison, half %136, i64 0
  %140 = shufflevector <3 x half> %139, <3 x half> poison, <3 x i32> zeroinitializer
  %141 = fmul fast <3 x half> %140, %132
  %142 = fdiv fast <3 x half> %141, %138
  br label %143

143:                                              ; preds = %135, %93
  %144 = phi fast <3 x half> [ %142, %135 ], [ zeroinitializer, %93 ]
  %145 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #14
  %146 = fadd fast <3 x half> %145, splat (half 0xHBC00)
  %147 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #14
  %148 = fpext half %47 to float
  %149 = fadd fast float %148, 0xBFFE666660000000
  %150 = fmul fast float %149, %149
  %151 = fmul fast float %150, 0xC00638E380000000
  %152 = tail call fast float @air.fast_exp.f32(float %151) #14
  %153 = fsub fast float 1.000000e+00, %152
  %154 = tail call fast float @air.fast_fmax.f32(float %153, float 5.000000e-01) #14
  %155 = fptrunc float %154 to half
  %156 = fmul fast half %96, %96
  %157 = fpext half %156 to float
  %158 = fsub fast float 1.000000e+00, %157
  %159 = fpext half %95 to float
  %160 = fmul fast float %158, %159
  %161 = fpext half %155 to float
  %162 = fmul fast float %160, %161
  %163 = fptrunc float %162 to half
  %164 = insertelement <3 x half> poison, half %163, i64 0
  %165 = shufflevector <3 x half> %164, <3 x half> poison, <3 x i32> zeroinitializer
  %166 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %126, <3 x half> %144, <3 x half> %165) #14
  %167 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %166) #14
  %168 = fadd fast <3 x half> %146, %147
  %169 = fadd fast <3 x half> %168, %167
  ret <3 x half> %169
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.clamp.f16(half, half, half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.clamp.v3f16(<3 x half>, <3 x half>, <3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_fmin.f32(float, float) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmin3.f16(half, half, half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmin.f16(half, half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.exp.f16(half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_saturate.f32(float) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.saturate.f16(half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.sign.f16(half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i1 @air.convert.u.i1.f.f32(float) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmod.f16(half, half) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.dot.v2f16(<2 x half>, <2 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_Z17protectMaskFilterDv3_DhS_S_S_b(<3 x half> noundef %0, <3 x half> noundef %1, <3 x half> noundef %2, <3 x half> noundef %3, i1 noundef zeroext %4) unnamed_addr #6 {
  %6 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %0) #14
  %7 = shufflevector <3 x float> %6, <3 x float> poison, <3 x i32> zeroinitializer
  %8 = fmul fast <3 x float> %7, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %9 = shufflevector <3 x float> %6, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %10 = fmul fast <3 x float> %9, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %11 = fadd fast <3 x float> %8, %10
  %12 = shufflevector <3 x float> %6, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %13 = fmul fast <3 x float> %12, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %14 = fadd fast <3 x float> %11, %13
  %15 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %14) #14
  %16 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %14) #14
  %17 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %16, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %18 = fmul fast <3 x float> %17, %15
  %19 = shufflevector <3 x float> %18, <3 x float> poison, <3 x i32> zeroinitializer
  %20 = fmul fast <3 x float> %19, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %21 = shufflevector <3 x float> %18, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %22 = fmul fast <3 x float> %21, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %23 = fadd fast <3 x float> %20, %22
  %24 = shufflevector <3 x float> %18, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %25 = fmul fast <3 x float> %24, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %26 = fadd fast <3 x float> %23, %25
  %27 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %26) #14
  %28 = extractelement <3 x half> %1, i64 1
  %29 = tail call fast half @air.fmax.f16(half %28, half 0xH0001) #14
  %30 = extractelement <3 x half> %2, i64 1
  %31 = tail call fast half @air.fmax.f16(half %30, half 0xH0001) #14
  %32 = extractelement <3 x half> %3, i64 1
  %33 = tail call fast half @air.fmax.f16(half %32, half 0xH0001) #14
  %34 = extractelement <3 x half> %27, i64 2
  %35 = fcmp fast une half %34, 0xH0000
  %36 = extractelement <3 x half> %27, i64 1
  %37 = fcmp fast une half %36, 0xH0000
  %38 = select i1 %35, i1 true, i1 %37
  br i1 %38, label %39, label %41

39:                                               ; preds = %5
  %40 = tail call fast half @air.atan2.f16(half %34, half %36) #14
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
  %53 = tail call fast float @air.fast_exp.f32(float %52) #14
  br label %61

54:                                               ; preds = %41
  %55 = fadd fast float %46, 6.281250e+00
  %56 = fneg fast float %55
  %57 = fmul fast float %55, %56
  %58 = fpext half %29 to float
  %59 = fdiv fast float %57, %58
  %60 = tail call fast float @air.fast_exp.f32(float %59) #14
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
  %72 = tail call fast float @air.fast_exp.f32(float %71) #14
  br label %80

73:                                               ; preds = %61
  %74 = fadd fast float %65, 6.281250e+00
  %75 = fneg fast float %74
  %76 = fmul fast float %74, %75
  %77 = fpext half %31 to float
  %78 = fdiv fast float %76, %77
  %79 = tail call fast float @air.fast_exp.f32(float %78) #14
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
  %91 = tail call fast float @air.fast_exp.f32(float %90) #14
  br label %99

92:                                               ; preds = %80
  %93 = fadd fast float %84, 6.281250e+00
  %94 = fneg fast float %93
  %95 = fmul fast float %93, %94
  %96 = fpext half %33 to float
  %97 = fdiv fast float %95, %96
  %98 = tail call fast float @air.fast_exp.f32(float %97) #14
  br label %99

99:                                               ; preds = %92, %85
  %100 = phi float [ %91, %85 ], [ %98, %92 ]
  %101 = fneg fast half %83
  %102 = fmul fast half %83, %101
  %103 = fdiv fast half %102, %33
  %104 = tail call fast half @air.exp.f16(half %103) #14
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
  %117 = tail call fast half @air.exp.f16(half %116) #14
  %118 = fmul fast half %117, %111
  %119 = fpext half %118 to float
  %120 = fadd fast float %113, %119
  %121 = extractelement <3 x half> %1, i64 2
  %122 = fpext half %121 to float
  %123 = fmul fast float %62, %122
  %124 = fneg fast half %44
  %125 = fmul fast half %44, %124
  %126 = fdiv fast half %125, %29
  %127 = tail call fast half @air.exp.f16(half %126) #14
  %128 = fmul fast half %127, %121
  %129 = fpext half %128 to float
  %130 = fadd fast float %123, %129
  %131 = shufflevector <3 x half> %27, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %132 = tail call fast half @air.dot.v2f16(<2 x half> %131, <2 x half> %131) #14
  %133 = tail call fast half @air.sqrt.f16(half %132) #14
  %134 = fptrunc float %120 to half
  %135 = fptrunc float %130 to half
  %136 = fadd fast half %133, 0xHAA66
  %137 = fmul fast half %136, 0xH4E3E
  %138 = tail call fast half @air.clamp.f16(half %137, half 0xH0000, half 0xH3C00) #14
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
define internal fastcc <3 x half> @_Z12warmthFilterDv3_DhS_Dv4_Dh(<3 x half> noundef %0, <3 x half> noundef %1, <4 x half> noundef %2) unnamed_addr #7 {
  %4 = tail call fast <3 x half> @air.fmin.v3f16(<3 x half> %0, <3 x half> zeroinitializer) #14
  %5 = tail call fast <3 x half> @air.fmax.v3f16(<3 x half> %0, <3 x half> splat (half 0xH3C00)) #14
  %6 = tail call fast <3 x half> @air.saturate.v3f16(<3 x half> %0) #14
  %7 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %6, <3 x half> splat (half 0xH3400)) #14
  %8 = shufflevector <3 x half> %7, <3 x half> poison, <3 x i32> zeroinitializer
  %9 = fmul fast <3 x half> %8, <half 0xH34C9, half 0xH38C4, half 0xH32C4>
  %10 = shufflevector <3 x half> %7, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %11 = fmul fast <3 x half> %10, <half 0xH38B2, half 0xHB464, half 0xHB82E>
  %12 = fadd fast <3 x half> %9, %11
  %13 = shufflevector <3 x half> %7, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %14 = fmul fast <3 x half> %13, <half 0xH2F4C, half 0xHB524, half 0xH34FA>
  %15 = fadd fast <3 x half> %12, %14
  %16 = shufflevector <3 x half> %15, <3 x half> poison, <2 x i32> <i32 1, i32 2>
  %17 = tail call fast half @air.dot.v2f16(<2 x half> %16, <2 x half> %16) #14
  %18 = fmul fast half %17, 0xH4400
  %19 = tail call fast half @air.fmin.f16(half 0xH3C00, half %18) #14
  %20 = fadd fast half %19, 0xH2666
  %21 = fmul fast half %20, 0xH3BCD
  %22 = tail call fast half @air.clamp.f16(half %21, half 0xH0000, half 0xH3C00) #14
  %23 = fmul fast half %22, %22
  %24 = fmul fast half %22, 0xH4000
  %25 = fsub fast half 0xH4200, %24
  %26 = fmul fast half %23, %25
  %27 = extractelement <3 x half> %15, i64 0
  %28 = tail call fast half @air.fmin.f16(half 0xH3C00, half %27) #14
  %29 = fadd fast half %28, 0xHB266
  %30 = fmul fast half %29, 0xH4500
  %31 = tail call fast half @air.clamp.f16(half %30, half 0xH0000, half 0xH3C00) #14
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
  %42 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %36, <2 x half> %39, <2 x half> %41) #14
  %43 = tail call fast half @air.pow.f16(half %26, half 0xH3266) #14
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
  %54 = tail call fast <2 x half> @air.mix.v2f16(<2 x half> %47, <2 x half> %16, <2 x half> %53) #14
  %55 = shufflevector <2 x half> %54, <2 x half> poison, <3 x i32> <i32 0, i32 1, i32 poison>
  %56 = shufflevector <3 x half> %15, <3 x half> %55, <3 x i32> <i32 0, i32 3, i32 4>
  %57 = fsub fast half 0xH3C00, %35
  %58 = insertelement <3 x half> poison, half %57, i64 0
  %59 = shufflevector <3 x half> %58, <3 x half> poison, <3 x i32> zeroinitializer
  %60 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> %56, <3 x half> %15, <3 x half> %59) #14
  %61 = shufflevector <3 x half> %60, <3 x half> poison, <3 x i32> zeroinitializer
  %62 = shufflevector <3 x half> %60, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %63 = fmul fast <3 x half> %62, <half 0xH3BA6, half 0xHB45B, half 0xHBC6E>
  %64 = fadd fast <3 x half> %63, %61
  %65 = shufflevector <3 x half> %60, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %66 = fmul fast <3 x half> %65, <half 0xH38F8, half 0xHB92E, half 0xH3ED2>
  %67 = fadd fast <3 x half> %64, %66
  %68 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %67, <3 x half> splat (half 0xH4400)) #14
  %69 = fadd fast <3 x half> %4, splat (half 0xHBC00)
  %70 = fadd fast <3 x half> %69, %5
  %71 = fadd fast <3 x half> %70, %68
  ret <3 x half> %71
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <2 x half> @air.mix.v2f16(<2 x half>, <2 x half>, <2 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(argmem: read)
define internal fastcc <3 x half> @_Z24getBWChannelMixFromStatsRU9MTLdevice8SSRStatsRU9MTLdevice9SSRParams(ptr addrspace(1) noundef readonly align 4 captures(none) dereferenceable(10640) %0, i32 %.0.val) unnamed_addr #8 {
  %2 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %0, i64 0, i32 1, i64 2, i32 4
  %3 = load float, ptr addrspace(1) %2, align 4, !tbaa !151
  %4 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %0, i64 0, i32 1, i64 3, i32 4
  %5 = load float, ptr addrspace(1) %4, align 4, !tbaa !151
  %6 = getelementptr inbounds %struct.SSRStats, ptr addrspace(1) %0, i64 0, i32 1, i64 4, i32 4
  %7 = load float, ptr addrspace(1) %6, align 4, !tbaa !151
  %8 = fptrunc float %3 to half
  %9 = insertelement <3 x half> undef, half %8, i64 0
  %10 = fptrunc float %5 to half
  %11 = insertelement <3 x half> %9, half %10, i64 1
  %12 = fptrunc float %7 to half
  %13 = insertelement <3 x half> %11, half %12, i64 2
  %14 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16(<3 x half> %13) #14
  %15 = shufflevector <3 x float> %14, <3 x float> poison, <3 x i32> zeroinitializer
  %16 = fmul fast <3 x float> %15, <float 0x3FD4186A60000000, float 0x3FC3E33E40000000, float 0x3F922DAE80000000>
  %17 = shufflevector <3 x float> %14, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %18 = fmul fast <3 x float> %17, <float 0x3FE476E3E0000000, float 0x3FE840ABE0000000, float 0x3FBC0465A0000000>
  %19 = fadd fast <3 x float> %16, %18
  %20 = shufflevector <3 x float> %14, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %21 = fmul fast <3 x float> %20, <float 0x3FA7CE86C0000000, float 0x3FB6321060000000, float 0x3FEBEC1640000000>
  %22 = fadd fast <3 x float> %19, %21
  %23 = tail call fast <3 x float> @air.sign.v3f32(<3 x float> %22) #14
  %24 = tail call fast <3 x float> @air.fast_fabs.v3f32(<3 x float> %22) #14
  %25 = tail call fast <3 x float> @air.fast_pow.v3f32(<3 x float> %24, <3 x float> splat (float 0x3FDB851EC0000000)) #14
  %26 = fmul fast <3 x float> %25, %23
  %27 = shufflevector <3 x float> %26, <3 x float> poison, <3 x i32> zeroinitializer
  %28 = fmul fast <3 x float> %27, <float 0x3FD99999A0000000, float 0x4011D1EB80000000, float 0x3FE9C779A0000000>
  %29 = shufflevector <3 x float> %26, <3 x float> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %30 = fmul fast <3 x float> %29, <float 0x3FD99999A0000000, float 0xC013676C80000000, float 0x3FD6DC5D60000000>
  %31 = fadd fast <3 x float> %28, %30
  %32 = shufflevector <3 x float> %26, <3 x float> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %33 = fmul fast <3 x float> %32, <float 0x3FC99999A0000000, float 0x3FD9581060000000, float 0xBFF29AD420000000>
  %34 = fadd fast <3 x float> %31, %33
  %35 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %34) #14
  %36 = extractelement <3 x half> %35, i64 2
  %37 = fcmp fast une half %36, 0xH0000
  %38 = extractelement <3 x half> %35, i64 1
  %39 = fcmp fast une half %38, 0xH0000
  %40 = select i1 %37, i1 true, i1 %39
  br i1 %40, label %41, label %43

41:                                               ; preds = %1
  %42 = tail call fast half @air.atan2.f16(half %36, half %38) #14
  br label %43

43:                                               ; preds = %41, %1
  %44 = phi fast half [ %42, %41 ], [ 0xH0000, %1 ]
  %45 = tail call fast half @air.fabs.f16(half %44) #14
  %46 = fmul fast half %45, 0xH3C72
  %47 = tail call fast half @air.clamp.f16(half %46, half 0xH0000, half 0xH3C00) #14
  %48 = fmul fast half %47, %47
  %49 = fmul fast half %47, 0xH4000
  %50 = fsub fast half 0xH4200, %49
  %51 = fmul fast half %48, %50
  switch i32 %.0.val, label %60 [
    i32 4, label %52
    i32 15, label %56
  ]

52:                                               ; preds = %43
  %53 = insertelement <3 x half> poison, half %51, i64 0
  %54 = shufflevector <3 x half> %53, <3 x half> poison, <3 x i32> zeroinitializer
  %55 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> splat (half 0xH3555), <3 x half> <half 0xH3883, half 0xH3629, half 0xH2A87>, <3 x half> %54) #14
  br label %60

56:                                               ; preds = %43
  %57 = insertelement <3 x half> poison, half %51, i64 0
  %58 = shufflevector <3 x half> %57, <3 x half> poison, <3 x i32> zeroinitializer
  %59 = tail call fast <3 x half> @air.mix.v3f16(<3 x half> splat (half 0xH3555), <3 x half> <half 0xH38F8, half 0xH3558, half 0xH2B0A>, <3 x half> %58) #14
  br label %60

60:                                               ; preds = %56, %52, %43
  %61 = phi <3 x half> [ %55, %52 ], [ %59, %56 ], [ undef, %43 ]
  %62 = extractelement <3 x half> %61, i64 0
  %63 = extractelement <3 x half> %61, i64 1
  %64 = fadd fast half %62, %63
  %65 = extractelement <3 x half> %61, i64 2
  %66 = fadd fast half %64, %65
  %67 = fdiv fast half %62, %66
  %68 = fdiv fast half %63, %66
  %69 = fdiv fast half %65, %66
  %70 = insertelement <3 x half> undef, half %67, i64 0
  %71 = insertelement <3 x half> %70, half %68, i64 1
  %72 = insertelement <3 x half> %71, half %69, i64 2
  ret <3 x half> %72
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.log.v3f16(<3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.log2.v3f16(<3 x half>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nounwind willreturn memory(read)
declare ptr addrspace(4) @air.imageblock_data(<2 x i16>, i32, i16) local_unnamed_addr #9

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i1 @air.all.v2i1(<2 x i1>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <2 x i16> @air.min.u.v2i16(<2 x i16>, <2 x i16>) local_unnamed_addr #1

; Function Attrs: mustprogress nounwind willreturn memory(argmem: readwrite)
declare void @air.write_imageblock_slice_to_texture_2d.i16.v4f16(ptr addrspace(1) captures(none), ptr addrspace(4) captures(none), i1, <2 x i16>, <2 x i16>, <2 x i16>, i16, i1, i32) local_unnamed_addr #10

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.dot.v2f32(<2 x float>, <2 x float>) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_sqrt.f32(float) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.convert.f.f16.s.i32(i32) local_unnamed_addr #1

; Function Attrs: convergent nounwind willreturn
declare void @air.wg.barrier(i32, i32) #11

declare void @llvm.lifetime.start.i64(i64)

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr writeonly captures(none), i8, i64, i1 immarg) #12

declare void @llvm.lifetime.end.i64(i64)

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(ptr captures(none)) #13

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #13

attributes #0 = { convergent mustprogress nounwind willreturn "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="96" "no-builtins" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" }
attributes #1 = { mustprogress nofree nosync nounwind willreturn memory(none) }
attributes #2 = { convergent mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #3 = { mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #4 = { mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="48" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #5 = { convergent mustprogress nofree nounwind willreturn memory(argmem: read) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="64" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #6 = { mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="96" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #7 = { mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="64" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #8 = { mustprogress nofree nosync nounwind willreturn memory(argmem: read) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="96" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #9 = { mustprogress nofree nounwind willreturn memory(read) }
attributes #10 = { mustprogress nounwind willreturn memory(argmem: readwrite) }
attributes #11 = { convergent nounwind willreturn }
attributes #12 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #13 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #14 = { nounwind willreturn memory(none) }
attributes #15 = { convergent nounwind willreturn memory(argmem: read) }
attributes #16 = { nounwind willreturn memory(argmem: read) }
attributes #17 = { nobuiltin nounwind "no-builtins" }
attributes #18 = { convergent nobuiltin nounwind "no-builtins" }
attributes #19 = { nounwind }
attributes #20 = { nounwind willreturn memory(read) }
attributes #21 = { nounwind willreturn memory(argmem: readwrite) }

!llvm.module.flags = !{!0, !1, !2, !3, !4, !5, !6, !7, !8, !9}
!air.version = !{!10}
!llvm.ident = !{!11}
!air.language_version = !{!12}
!air.compile_options = !{!13, !14, !15}
!air.sampler_states = !{!16, !17}
!air.kernel = !{!18}

!0 = !{i32 7, !"air.max_device_buffers", i32 31}
!1 = !{i32 7, !"air.max_constant_buffers", i32 31}
!2 = !{i32 7, !"air.max_threadgroup_buffers", i32 31}
!3 = !{i32 7, !"air.max_textures", i32 128}
!4 = !{i32 7, !"air.max_read_write_textures", i32 8}
!5 = !{i32 7, !"air.max_samplers", i32 16}
!6 = !{i32 2, !"SDK Version", [2 x i32] [i32 27, i32 0]}
!7 = !{i32 1, !"wchar_size", i32 4}
!8 = !{i32 7, !"frame-pointer", i32 2}
!9 = !{i32 7, !"air.workaround.sampler_state_variable_length_encoding", i1 true}
!10 = !{i32 2, i32 7, i32 0}
!11 = !{!"Apple metal version 32023.921 (metalfe-32023.921.4)"}
!12 = !{!"Metal", i32 3, i32 2, i32 0}
!13 = !{!"air.compile.denorms_disable"}
!14 = !{!"air.compile.fast_math_enable"}
!15 = !{!"air.compile.framebuffer_fetch_enable"}
!16 = !{!"air.sampler_state", ptr addrspace(2) @__air_sampler_state}
!17 = !{!"air.sampler_state", ptr addrspace(2) @__air_sampler_state.3}
!18 = !{ptr @renderFinalAdjustments, !19, !20}
!19 = !{}
!20 = !{!21, !23, !24, !25, !26, !27, !28, !29, !30, !31, !32, !33, !34, !35, !36, !37, !38, !41, !50, !54, !56, !57, !58}
!21 = !{i32 0, !"air.imageblock", !"explicit", !"air.imageblock_data_size", i32 8, !"air.struct_type_info", !22, !"air.arg_type_align_size", i32 8, !"air.arg_type_name", !"imageblock<ImageBlockRGBA, layout_explicit>", !"air.arg_name", !"imgBlk"}
!22 = !{i32 0, i32 8, i32 0, !"half4", !"rgba"}
!23 = !{i32 1, !"air.texture", !"air.location_index", i32 0, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputImageTex"}
!24 = !{i32 2, !"air.texture", !"air.location_index", i32 1, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputLinearImageTex"}
!25 = !{i32 3, !"air.texture", !"air.location_index", i32 2, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputGlobalToneCurveTex"}
!26 = !{i32 4, !"air.texture", !"air.location_index", i32 21, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputCubicSplineToneCurveTex"}
!27 = !{i32 5, !"air.texture", !"air.location_index", i32 7, i32 1, !"air.read", !"air.arg_type_name", !"texture2d<half, read>", !"air.arg_name", !"inputGainMapTex", !"air.arg_unused"}
!28 = !{i32 6, !"air.texture", !"air.location_index", i32 8, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputBgLTMGainMap"}
!29 = !{i32 7, !"air.texture", !"air.location_index", i32 9, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputFgLTMGainMap"}
!30 = !{i32 8, !"air.texture", !"air.location_index", i32 5, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputLightMapTex"}
!31 = !{i32 9, !"air.texture", !"air.location_index", i32 6, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputLinearLightMapTex"}
!32 = !{i32 10, !"air.texture", !"air.location_index", i32 10, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"fgbgMatte"}
!33 = !{i32 11, !"air.texture", !"air.location_index", i32 11, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"skinMatte"}
!34 = !{i32 12, !"air.texture", !"air.location_index", i32 12, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"skyMatte"}
!35 = !{i32 13, !"air.texture", !"air.location_index", i32 22, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"selectiveColorHueSatLumLUTTex"}
!36 = !{i32 14, !"air.texture", !"air.location_index", i32 13, i32 1, !"air.write", !"air.arg_type_name", !"texture2d<half, write>", !"air.arg_name", !"outputImageTex"}
!37 = !{i32 15, !"air.texture", !"air.location_index", i32 14, i32 1, !"air.write", !"air.arg_type_name", !"texture2d<half, write>", !"air.arg_name", !"outputGainMapTex", !"air.arg_unused"}
!38 = !{i32 16, !"air.buffer", !"air.buffer_size", i32 320, !"air.location_index", i32 0, i32 1, !"air.read", !"air.address_space", i32 2, !"air.struct_type_info", !39, !"air.arg_type_size", i32 320, !"air.arg_type_align_size", i32 16, !"air.arg_type_name", !"SSRColorManagement", !"air.arg_name", !"colorManagement"}
!39 = !{!"air.struct_type_info", !40, i32 0, i32 80, i32 0, !"SSRColorConversion", !"inputImage", !"air.struct_type_info", !40, i32 80, i32 80, i32 0, !"SSRColorConversion", !"inputLinearImage", !"air.struct_type_info", !40, i32 160, i32 80, i32 0, !"SSRColorConversion", !"inputMasks", !"air.struct_type_info", !40, i32 240, i32 80, i32 0, !"SSRColorConversion", !"outputImage"}
!40 = !{i32 0, i32 4, i32 0, !"uint", !"transferFunction", i32 16, i32 48, i32 0, !"float3x3", !"colorConversionMatrix", i32 64, i32 1, i32 0, !"bool", !"useVELuma"}
!41 = !{i32 17, !"air.buffer", !"air.buffer_size", i32 672, !"air.location_index", i32 1, i32 1, !"air.read_write", !"air.address_space", i32 1, !"air.struct_type_info", !42, !"air.arg_type_size", i32 672, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"SSRParams", !"air.arg_name", !"params"}
!42 = !{i32 0, i32 4, i32 0, !"uint", !"castType", i32 4, i32 4, i32 0, !"float", !"castIntensity", i32 8, i32 4, i32 0, !"float", !"toneBias", i32 12, i32 4, i32 0, !"float", !"colorBias", i32 16, i32 4, i32 0, !"float", !"fgCastIntensity", i32 20, i32 4, i32 0, !"float", !"bgCastIntensity", i32 24, i32 4, i32 0, !"float", !"linearBaseGain", i32 28, i32 4, i32 0, !"float", !"baselineExposure", i32 32, i32 4, i32 0, !"uint", !"sceneType", !"air.struct_type_info", !43, i32 36, i32 136, i32 0, !"SSRCastAdjustments", !"castAdj", !"air.struct_type_info", !44, i32 172, i32 264, i32 0, !"SSRToneAdjustments", !"toneAdj", !"air.struct_type_info", !45, i32 436, i32 16, i32 0, !"SSRColorAdjustments", !"colorAdj", !"air.struct_type_info", !46, i32 452, i32 36, i32 0, !"SSRHazeAdjustments", !"hazeAdj", !"air.struct_type_info", !47, i32 488, i32 68, i32 0, !"SSRBGAdjustment", !"bgAdj", !"air.struct_type_info", !48, i32 556, i32 64, i32 0, !"SSRFGAdjustment", !"fgAdj", !"air.struct_type_info", !49, i32 620, i32 28, i32 0, !"SSRSemanticToneAdjustment", !"semanticToneAdj", i32 648, i32 4, i32 0, !"float", !"brightnessValue", i32 652, i32 4, i32 0, !"uint", !"tuningType", i32 656, i32 4, i32 0, !"float", !"peopleThresholdLo", i32 660, i32 4, i32 0, !"float", !"peopleThresholdHi", i32 664, i32 4, i32 0, !"float", !"faceBasedGlobalExposureBoostRatio", i32 668, i32 4, i32 0, !"float", !"personMasksValidHint"}
!43 = !{i32 0, i32 4, i32 0, !"float", !"bgWarmth", i32 4, i32 4, i32 0, !"float", !"fgWarmth", i32 8, i32 4, i32 0, !"float", !"bgRotate", i32 12, i32 4, i32 0, !"float", !"fgRotate", i32 16, i32 4, i32 0, !"float", !"personWarmth", i32 20, i32 4, i32 0, !"float", !"personRotate", i32 24, i32 4, i32 3, !"float", !"hue", i32 36, i32 4, i32 3, !"float", !"range", i32 48, i32 4, i32 3, !"float", !"strength", i32 60, i32 4, i32 0, !"float", !"shadow", i32 64, i32 4, i32 0, !"float", !"mids", i32 68, i32 4, i32 0, !"float", !"high", i32 72, i32 4, i32 3, !"float", !"shadowRGB", i32 84, i32 4, i32 3, !"float", !"midsRGB", i32 96, i32 4, i32 3, !"float", !"highRGB", i32 108, i32 4, i32 0, !"float", !"deRed", i32 112, i32 4, i32 0, !"float", !"deRedSatReduction", i32 116, i32 4, i32 0, !"float", !"deYellow", i32 120, i32 4, i32 0, !"float", !"skinWarmth", i32 124, i32 4, i32 0, !"float", !"skinProtectStrength", i32 128, i32 4, i32 0, !"float", !"skinProtectRange", i32 132, i32 4, i32 0, !"float", !"skinRatioThreshold"}
!44 = !{i32 0, i32 4, i32 0, !"float", !"toneMinusMids", i32 4, i32 4, i32 0, !"float", !"toneMinusExposure", i32 8, i32 4, i32 0, !"float", !"toneMinusPersonExposure", i32 12, i32 4, i32 0, !"float", !"toneMinusFGScale", i32 16, i32 4, i32 0, !"float", !"toneMinusPersonSatScale", i32 20, i32 4, i32 0, !"float", !"toneMinusPersonContrastMax", i32 24, i32 4, i32 0, !"float", !"toneMinusPersonContrastScale", i32 28, i32 4, i32 0, !"float", !"toneMinusBGContrastScale", i32 32, i32 4, i32 0, !"float", !"toneMinusBGContrastMax", i32 36, i32 4, i32 0, !"float", !"toneMinusLTMRatio", i32 40, i32 4, i32 0, !"float", !"toneMinusPersonSmartContrastScale", i32 44, i32 4, i32 0, !"float", !"tonePlusPersonSatScale", i32 48, i32 4, i32 0, !"float", !"tonePlusFGScale", i32 52, i32 4, i32 0, !"float", !"tonePlusExposure", i32 56, i32 4, i32 0, !"float", !"tonePlusBGContrast", i32 60, i32 4, i32 0, !"float", !"colorCubeToneBiasMinGamma", i32 64, i32 4, i32 0, !"float", !"colorCubeToneBiasMaxGamma", i32 68, i32 4, i32 0, !"float", !"starkBWBackgroundRed", i32 72, i32 4, i32 0, !"float", !"starkBWBackgroundGreen", i32 76, i32 4, i32 0, !"float", !"starkBWBackgroundBlue", i32 80, i32 4, i32 0, !"float", !"starkBWWhitesMax", i32 84, i32 4, i32 0, !"float", !"defaultContrastBump", i32 88, i32 4, i32 0, !"float", !"defaultSatBump", i32 92, i32 4, i32 0, !"float", !"defaultMidsBump", i32 96, i32 4, i32 0, !"float", !"defaultLightenBump", i32 100, i32 4, i32 0, !"float", !"dfContrastBump", i32 104, i32 4, i32 0, !"float", !"dfSatBump", i32 108, i32 4, i32 0, !"float", !"dfMidsBump", i32 112, i32 4, i32 0, !"float", !"dfLightenBump", i32 116, i32 4, i32 0, !"float", !"dfLowLightStarts", i32 120, i32 4, i32 0, !"float", !"dfLowLightMax", i32 124, i32 4, i32 0, !"float", !"dfLowLightContrastBump", i32 128, i32 4, i32 0, !"float", !"dfLowLightSatBump", i32 132, i32 4, i32 0, !"float", !"dfLowLightMidsBump", i32 136, i32 4, i32 0, !"float", !"dfLowLightLightenBump", i32 140, i32 4, i32 0, !"float", !"ubContrastBump", i32 144, i32 4, i32 0, !"float", !"ubSatBump", i32 148, i32 4, i32 0, !"float", !"ubMidsBump", i32 152, i32 4, i32 0, !"float", !"ubLightenBump", i32 156, i32 4, i32 0, !"float", !"digitalFlashContrastBump", i32 160, i32 4, i32 0, !"float", !"digitalFlashSatBump", i32 164, i32 4, i32 0, !"float", !"digitalFlashMidsBump", i32 168, i32 4, i32 0, !"float", !"digitalFlashLightenBump", i32 172, i32 4, i32 0, !"float", !"swfrContrastBump", i32 176, i32 4, i32 0, !"float", !"swfrSatBump", i32 180, i32 4, i32 0, !"float", !"swfrMidsBump", i32 184, i32 4, i32 0, !"float", !"swfrLightenBump", i32 188, i32 4, i32 0, !"float", !"wysContrastBump", i32 192, i32 4, i32 0, !"float", !"wysSatBump", i32 196, i32 4, i32 0, !"float", !"wysMidsBump", i32 200, i32 4, i32 0, !"float", !"wysLightenBump", i32 204, i32 4, i32 0, !"float", !"sfdContrastBump", i32 208, i32 4, i32 0, !"float", !"sfdSatBump", i32 212, i32 4, i32 0, !"float", !"sfdMidsBump", i32 216, i32 4, i32 0, !"float", !"sfdLightenBump", i32 220, i32 4, i32 0, !"float", !"videoContrastBump", i32 224, i32 4, i32 0, !"float", !"videoSatBump", i32 228, i32 4, i32 0, !"float", !"videoMidsBump", i32 232, i32 4, i32 0, !"float", !"videoLightenBump", i32 236, i32 4, i32 0, !"float", !"foodToneScale", i32 240, i32 4, i32 0, !"float", !"foodColorScale", i32 244, i32 4, i32 0, !"float", !"foodIntensityScale", i32 248, i32 4, i32 0, !"float", !"sunsetToneScale", i32 252, i32 4, i32 0, !"float", !"sunsetColorScale", i32 256, i32 4, i32 0, !"float", !"sunsetIntensityScale", i32 260, i32 4, i32 0, !"float", !"longGrayLiftMix"}
!45 = !{i32 0, i32 4, i32 0, !"float", !"bwBackgroundHue", i32 4, i32 4, i32 0, !"float", !"bwForegroundHue", i32 8, i32 4, i32 0, !"float", !"colorBoostScale", i32 12, i32 4, i32 0, !"float", !"shadMidHighPersonMix"}
!46 = !{i32 0, i32 1, i32 0, !"bool", !"doHazeTuning", i32 4, i32 4, i32 0, !"float", !"liftStrength", i32 8, i32 4, i32 0, !"float", !"bgLift", i32 12, i32 4, i32 0, !"float", !"personLift", i32 16, i32 4, i32 0, !"float", !"bgMids", i32 20, i32 4, i32 0, !"float", !"personMids", i32 24, i32 4, i32 0, !"float", !"satMix", i32 28, i32 4, i32 0, !"float", !"contrast", i32 32, i32 4, i32 0, !"float", !"localContrast"}
!47 = !{i32 0, i32 4, i32 0, !"float", !"whites", i32 4, i32 4, i32 0, !"float", !"contrast", i32 8, i32 4, i32 0, !"float", !"richSat", i32 12, i32 4, i32 0, !"float", !"shadows", i32 16, i32 4, i32 0, !"float", !"gammaContrast", i32 20, i32 4, i32 0, !"float", !"localContrast", i32 24, i32 4, i32 0, !"float", !"airy", i32 28, i32 4, i32 0, !"float", !"mids", i32 32, i32 4, i32 0, !"float", !"sat", i32 36, i32 4, i32 0, !"float", !"lighten", i32 40, i32 4, i32 0, !"float", !"underGrass", i32 44, i32 4, i32 0, !"float", !"airyGamma", i32 48, i32 4, i32 0, !"float", !"warmthMatchI", i32 52, i32 4, i32 0, !"float", !"warmthMatchQ", i32 56, i32 4, i32 0, !"float", !"warmthMatchSkyI", i32 60, i32 4, i32 0, !"float", !"warmthMatchSkyQ", i32 64, i32 4, i32 0, !"float", !"bgGlobalMix"}
!48 = !{i32 0, i32 4, i32 0, !"float", !"personMix", i32 4, i32 4, i32 0, !"float", !"airy", i32 8, i32 4, i32 0, !"float", !"mids", i32 12, i32 4, i32 0, !"float", !"lighten", i32 16, i32 4, i32 0, !"float", !"whites", i32 20, i32 4, i32 0, !"float", !"airyGamma", i32 24, i32 4, i32 0, !"float", !"shadows", i32 28, i32 4, i32 0, !"float", !"contrast", i32 32, i32 4, i32 0, !"float", !"smartContrast", i32 36, i32 4, i32 0, !"float", !"skinHighLights", i32 40, i32 4, i32 0, !"float", !"skinLocalContrast", i32 44, i32 4, i32 0, !"float", !"saturation", i32 48, i32 4, i32 0, !"float", !"faceI", i32 52, i32 4, i32 0, !"float", !"faceQ", i32 56, i32 4, i32 0, !"float", !"underTone", i32 60, i32 4, i32 0, !"float", !"neckShade"}
!49 = !{i32 0, i32 4, i32 0, !"float", !"bgLTM", i32 4, i32 4, i32 0, !"float", !"fgLTM", i32 8, i32 4, i32 0, !"float", !"bgExposureGain", i32 12, i32 4, i32 0, !"float", !"fgExposureGain", i32 16, i32 4, i32 0, !"float", !"GTC", i32 20, i32 4, i32 0, !"float", !"HR", i32 24, i32 4, i32 0, !"float", !"personHR"}
!50 = !{i32 18, !"air.buffer", !"air.buffer_size", i32 10640, !"air.location_index", i32 3, i32 1, !"air.read_write", !"air.address_space", i32 1, !"air.struct_type_info", !51, !"air.arg_type_size", i32 10640, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"SSRStats", !"air.arg_name", !"stats"}
!51 = !{i32 0, i32 4, i32 2560, !"uint", !"globalHistogram", !"air.struct_type_info", !52, i32 10240, i32 36, i32 10, !"SSRGlobalStats", !"globalStats", i32 10600, i32 4, i32 0, !"uint", !"globalPersonCount", i32 10604, i32 4, i32 0, !"uint", !"globalSkinCount", i32 10608, i32 4, i32 0, !"float", !"peopleRatio", i32 10612, i32 4, i32 0, !"float", !"skinRatio", !"air.struct_type_info", !53, i32 10616, i32 12, i32 0, !"SSRBasicStats", !"linBasicStats", !"air.struct_type_info", !53, i32 10628, i32 12, i32 0, !"SSRBasicStats", !"ltmBasicStats"}
!52 = !{i32 0, i32 4, i32 0, !"float", !"highKey", i32 4, i32 4, i32 0, !"float", !"p02", i32 8, i32 4, i32 0, !"float", !"p10", i32 12, i32 4, i32 0, !"float", !"p25", i32 16, i32 4, i32 0, !"float", !"p50", i32 20, i32 4, i32 0, !"float", !"p75", i32 24, i32 4, i32 0, !"float", !"p98", i32 28, i32 4, i32 0, !"float", !"blackPoint", i32 32, i32 4, i32 0, !"float", !"whitePoint"}
!53 = !{i32 0, i32 4, i32 0, !"float", !"min", i32 4, i32 4, i32 0, !"float", !"max", i32 8, i32 4, i32 0, !"float", !"avg"}
!54 = !{i32 19, !"air.buffer", !"air.buffer_size", i32 176, !"air.location_index", i32 5, i32 1, !"air.read", !"air.address_space", i32 2, !"air.struct_type_info", !55, !"air.arg_type_size", i32 176, !"air.arg_type_align_size", i32 16, !"air.arg_type_name", !"SSRRenderROI", !"air.arg_name", !"roi"}
!55 = !{i32 0, i32 4, i32 0, !"ushort2", !"logicalImageSize", i32 4, i32 4, i32 0, !"ushort2", !"renderRegionSize", i32 8, i32 4, i32 0, !"ushort2", !"renderEdge", i32 16, i32 16, i32 0, !"float4", !"logicalImageToInputImageGridScaleAndOffset", i32 32, i32 16, i32 0, !"float4", !"logicalImageToInputLinearImageGridScaleAndOffset", i32 48, i32 16, i32 0, !"float4", !"logicalImageToBgLTMGainMapGridScaleAndOffset", i32 64, i32 16, i32 0, !"float4", !"logicalImageToFgLTMGainMapGridScaleAndOffset", i32 80, i32 16, i32 0, !"float4", !"logicalImageToInputLightMapGridScaleAndOffset", i32 96, i32 16, i32 0, !"float4", !"logicalImageToInputLinearLightMapGridScaleAndOffset", i32 112, i32 16, i32 0, !"float4", !"logicalImageToInputPersonMaskGridScaleAndOffset", i32 128, i32 16, i32 0, !"float4", !"logicalImageToInputSkinMaskGridScaleAndOffset", i32 144, i32 16, i32 0, !"float4", !"logicalImageToInputSkyMaskGridScaleAndOffset", i32 160, i32 4, i32 0, !"ushort2", !"outputImageGridOffset"}
!56 = !{i32 20, !"air.thread_position_in_grid", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"gridPos"}
!57 = !{i32 21, !"air.thread_position_in_threadgroup", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"tgPos"}
!58 = !{i32 22, !"air.threads_per_threadgroup", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"tgSize"}
!59 = !{!60, !60, i64 0}
!60 = !{!"omnipotent char", !61, i64 0}
!61 = !{!"Simple C++ TBAA"}
!62 = !{!63, !65, !67}
!63 = distinct !{!63, !64, !"air-alias-scope-arg(19)"}
!64 = distinct !{!64, !"air-alias-scopes(renderFinalAdjustments)"}
!65 = distinct !{!65, !66, !"air-alias-scope-arg(19)"}
!66 = distinct !{!66, !"air-alias-scopes-loader(renderFinalAdjustments)"}
!67 = distinct !{!67, !68, !"air-alias-scope-arg(19)"}
!68 = distinct !{!68, !"air-alias-scopes-device-lowering(renderFinalAdjustments)"}
!69 = !{!70, !71, !72, !73, !74, !75, !76, !77, !78, !79, !80, !81}
!70 = distinct !{!70, !64, !"air-alias-scope-textures"}
!71 = distinct !{!71, !64, !"air-alias-scope-arg(16)"}
!72 = distinct !{!72, !64, !"air-alias-scope-arg(17)"}
!73 = distinct !{!73, !64, !"air-alias-scope-arg(18)"}
!74 = distinct !{!74, !66, !"air-alias-scope-textures"}
!75 = distinct !{!75, !66, !"air-alias-scope-arg(16)"}
!76 = distinct !{!76, !66, !"air-alias-scope-arg(17)"}
!77 = distinct !{!77, !66, !"air-alias-scope-arg(18)"}
!78 = distinct !{!78, !68, !"air-alias-scope-textures"}
!79 = distinct !{!79, !68, !"air-alias-scope-arg(16)"}
!80 = distinct !{!80, !68, !"air-alias-scope-arg(17)"}
!81 = distinct !{!81, !68, !"air-alias-scope-arg(18)"}
!82 = !{!70, !74, !78}
!83 = !{!71, !72, !73, !63, !75, !76, !77, !65, !79, !80, !81, !67}
!84 = !{!85, !87, i64 668}
!85 = !{!"_ZTS9SSRParams", !86, i64 0, !87, i64 4, !87, i64 8, !87, i64 12, !87, i64 16, !87, i64 20, !87, i64 24, !87, i64 28, !88, i64 32, !89, i64 36, !90, i64 172, !91, i64 436, !92, i64 452, !94, i64 488, !95, i64 556, !96, i64 620, !87, i64 648, !97, i64 652, !87, i64 656, !87, i64 660, !87, i64 664, !87, i64 668}
!86 = !{!"_ZTS11SSRCastType", !60, i64 0}
!87 = !{!"float", !60, i64 0}
!88 = !{!"_ZTS12SSRSceneType", !60, i64 0}
!89 = !{!"_ZTS18SSRCastAdjustments", !87, i64 0, !87, i64 4, !87, i64 8, !87, i64 12, !87, i64 16, !87, i64 20, !60, i64 24, !60, i64 36, !60, i64 48, !87, i64 60, !87, i64 64, !87, i64 68, !60, i64 72, !60, i64 84, !60, i64 96, !87, i64 108, !87, i64 112, !87, i64 116, !87, i64 120, !87, i64 124, !87, i64 128, !87, i64 132}
!90 = !{!"_ZTS18SSRToneAdjustments", !87, i64 0, !87, i64 4, !87, i64 8, !87, i64 12, !87, i64 16, !87, i64 20, !87, i64 24, !87, i64 28, !87, i64 32, !87, i64 36, !87, i64 40, !87, i64 44, !87, i64 48, !87, i64 52, !87, i64 56, !87, i64 60, !87, i64 64, !87, i64 68, !87, i64 72, !87, i64 76, !87, i64 80, !87, i64 84, !87, i64 88, !87, i64 92, !87, i64 96, !87, i64 100, !87, i64 104, !87, i64 108, !87, i64 112, !87, i64 116, !87, i64 120, !87, i64 124, !87, i64 128, !87, i64 132, !87, i64 136, !87, i64 140, !87, i64 144, !87, i64 148, !87, i64 152, !87, i64 156, !87, i64 160, !87, i64 164, !87, i64 168, !87, i64 172, !87, i64 176, !87, i64 180, !87, i64 184, !87, i64 188, !87, i64 192, !87, i64 196, !87, i64 200, !87, i64 204, !87, i64 208, !87, i64 212, !87, i64 216, !87, i64 220, !87, i64 224, !87, i64 228, !87, i64 232, !87, i64 236, !87, i64 240, !87, i64 244, !87, i64 248, !87, i64 252, !87, i64 256, !87, i64 260}
!91 = !{!"_ZTS19SSRColorAdjustments", !87, i64 0, !87, i64 4, !87, i64 8, !87, i64 12}
!92 = !{!"_ZTS18SSRHazeAdjustments", !93, i64 0, !87, i64 4, !87, i64 8, !87, i64 12, !87, i64 16, !87, i64 20, !87, i64 24, !87, i64 28, !87, i64 32}
!93 = !{!"bool", !60, i64 0}
!94 = !{!"_ZTS15SSRBGAdjustment", !87, i64 0, !87, i64 4, !87, i64 8, !87, i64 12, !87, i64 16, !87, i64 20, !87, i64 24, !87, i64 28, !87, i64 32, !87, i64 36, !87, i64 40, !87, i64 44, !87, i64 48, !87, i64 52, !87, i64 56, !87, i64 60, !87, i64 64}
!95 = !{!"_ZTS15SSRFGAdjustment", !87, i64 0, !87, i64 4, !87, i64 8, !87, i64 12, !87, i64 16, !87, i64 20, !87, i64 24, !87, i64 28, !87, i64 32, !87, i64 36, !87, i64 40, !87, i64 44, !87, i64 48, !87, i64 52, !87, i64 56, !87, i64 60}
!96 = !{!"_ZTS25SSRSemanticToneAdjustment", !87, i64 0, !87, i64 4, !87, i64 8, !87, i64 12, !87, i64 16, !87, i64 20, !87, i64 24}
!97 = !{!"_ZTS13SSRTuningType", !60, i64 0}
!98 = !{!72, !76, !80}
!99 = !{!70, !71, !73, !63, !74, !75, !77, !65, !78, !79, !81, !67}
!100 = !{!85, !87, i64 168}
!101 = !{!102, !104, i64 0}
!102 = !{!"_ZTS18SSRColorManagement", !103, i64 0, !103, i64 80, !103, i64 160, !103, i64 240}
!103 = !{!"_ZTS18SSRColorConversion", !104, i64 0, !105, i64 16, !93, i64 64}
!104 = !{!"_ZTS19CMITransferFunction", !60, i64 0}
!105 = !{!"_ZTSN5metal6matrixIfLi3ELi3EvEE", !60, i64 0}
!106 = !{!71, !75, !79}
!107 = !{!70, !72, !73, !63, !74, !76, !77, !65, !78, !80, !81, !67}
!108 = !{!102, !93, i64 64}
!109 = !{i8 0, i8 2}
!110 = !{!87, !87, i64 0}
!111 = !{!85, !87, i64 28}
!112 = !{!85, !87, i64 8}
!113 = !{!85, !87, i64 4}
!114 = !{!85, !86, i64 0}
!115 = !{!85, !87, i64 628}
!116 = !{!85, !87, i64 632}
!117 = !{!85, !87, i64 640}
!118 = !{!85, !87, i64 644}
!119 = !{!85, !87, i64 24}
!120 = !{!96, !87, i64 4}
!121 = !{!96, !87, i64 0}
!122 = !{!96, !87, i64 16}
!123 = !{!96, !87, i64 8}
!124 = !{!96, !87, i64 12}
!125 = !{!94, !87, i64 12}
!126 = !{!94, !87, i64 4}
!127 = !{!94, !87, i64 0}
!128 = !{!94, !87, i64 44}
!129 = !{!94, !87, i64 28}
!130 = !{!94, !87, i64 32}
!131 = !{!94, !87, i64 20}
!132 = !{!94, !87, i64 16}
!133 = !{!94, !87, i64 36}
!134 = !{!94, !87, i64 40}
!135 = !{!94, !87, i64 8}
!136 = !{!95, !87, i64 0}
!137 = !{!95, !87, i64 16}
!138 = !{!95, !87, i64 24}
!139 = !{!95, !87, i64 60}
!140 = !{!95, !87, i64 28}
!141 = !{!95, !87, i64 44}
!142 = !{!95, !87, i64 20}
!143 = !{!95, !87, i64 8}
!144 = !{!95, !87, i64 56}
!145 = !{!95, !87, i64 12}
!146 = !{!95, !87, i64 32}
!147 = !{!85, !87, i64 12}
!148 = !{!85, !87, i64 444}
!149 = !{!95, !87, i64 40}
!150 = !{!95, !87, i64 36}
!151 = !{!152, !87, i64 16}
!152 = !{!"_ZTS14SSRGlobalStats", !87, i64 0, !87, i64 4, !87, i64 8, !87, i64 12, !87, i64 16, !87, i64 20, !87, i64 24, !87, i64 28, !87, i64 32}
!153 = !{!73, !77, !81}
!154 = !{!70, !71, !72, !63, !74, !75, !76, !65, !78, !79, !80, !67}
!155 = !{!152, !87, i64 0}
!156 = !{!152, !87, i64 24}
!157 = !{!89, !87, i64 108}
!158 = !{!89, !87, i64 112}
!159 = !{!89, !87, i64 116}
!160 = !{!89, !87, i64 120}
!161 = !{!89, !87, i64 0}
!162 = !{!163, !163, i64 0}
!163 = !{!"half", !60, i64 0}
!164 = distinct !{!164, !165}
!165 = !{!"llvm.loop.mustprogress"}
!166 = !{i64 0, i64 24, !59}
!167 = !{i64 0, i64 16, !59}
!168 = !{i64 0, i64 8, !59}
!169 = !{!89, !87, i64 8}
!170 = !{!89, !87, i64 4}
!171 = !{!89, !87, i64 12}
!172 = !{!89, !87, i64 16}
!173 = !{!89, !87, i64 20}
!174 = !{!85, !87, i64 448}
!175 = !{!89, !87, i64 60}
!176 = !{!89, !87, i64 64}
!177 = !{!89, !87, i64 68}
!178 = !{!85, !97, i64 652}
!179 = !{!85, !87, i64 432}
!180 = !{!85, !87, i64 252}
!181 = !{!85, !87, i64 16}
!182 = !{!85, !87, i64 20}
!183 = !{i64 0, i64 4, !110, i64 4, i64 4, !110, i64 8, i64 4, !110, i64 12, i64 4, !110, i64 16, i64 4, !110, i64 20, i64 4, !110, i64 24, i64 4, !110, i64 28, i64 4, !110}
!184 = !{i64 0, i64 4, !110, i64 4, i64 4, !110, i64 8, i64 4, !110, i64 12, i64 4, !110, i64 16, i64 4, !110, i64 20, i64 4, !110, i64 24, i64 4, !110}
!185 = !{i64 0, i64 4, !110, i64 4, i64 4, !110, i64 8, i64 4, !110, i64 12, i64 4, !110, i64 16, i64 4, !110, i64 20, i64 4, !110}
!186 = !{i64 0, i64 4, !110, i64 4, i64 4, !110, i64 8, i64 4, !110, i64 12, i64 4, !110, i64 16, i64 4, !110}
!187 = !{i64 0, i64 4, !110, i64 4, i64 4, !110, i64 8, i64 4, !110, i64 12, i64 4, !110}
!188 = !{i64 0, i64 4, !110, i64 4, i64 4, !110, i64 8, i64 4, !110}
!189 = !{i64 0, i64 4, !110, i64 4, i64 4, !110}
!190 = !{i64 0, i64 4, !110}
!191 = !{!89, !87, i64 124}
!192 = !{!89, !87, i64 128}
!193 = !{!85, !87, i64 240}
!194 = !{!85, !87, i64 244}
!195 = !{!85, !87, i64 248}
!196 = !{!80}
!197 = !{!78, !79, !81, !67}
!198 = !{!81}
!199 = !{!78, !79, !80, !67}
!200 = !{!102, !104, i64 240}
