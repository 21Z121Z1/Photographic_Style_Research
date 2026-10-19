source_filename = "imageReduction"
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v24:32:32-v32:32:32-v48:64:64-v64:64:64-v96:128:128-v128:128:128-v192:256:256-v256:256:256-v512:512:512-v1024:1024:1024-n8:16:32"
target triple = "air64_v29-apple-macosx27.0.0"

%"struct.metal::_imageblock_base.189" = type { ptr addrspace(4) }
%struct.SSRColorConversion.191 = type <{ i32, [12 x i8], %"struct.metal::matrix.17.190", i8, [15 x i8] }>
%"struct.metal::matrix.17.190" = type { [3 x <3 x float>] }
%struct.SSRBasicStats = type { float, float, float }

@__air_sampler_state = internal addrspace(2) constant [2 x i64] [i64 34901797601053257, i64 0], align 8
@llvm.global_ctors = appending global [0 x { i32, ptr, ptr }] zeroinitializer

; Function Attrs: convergent nounwind
define void @imageReduction(%"struct.metal::_imageblock_base.189" %0, ptr addrspace(1) %1, ptr addrspace(1) %2, ptr addrspace(1) %3, ptr addrspace(1) noundef writeonly align 4 captures(none) dereferenceable(12) "air-buffer-no-alias" %4, ptr addrspace(2) noundef readonly align 16 captures(none) dereferenceable(65) "air-buffer-no-alias" %5, ptr addrspace(2) noundef readonly align 8 captures(none) dereferenceable(8) "air-buffer-no-alias" %6, <2 x i16> noundef %7, <2 x i16> noundef %8, <2 x i16> noundef %9, <2 x i16> noundef %10) local_unnamed_addr #0 {
  %12 = tail call ptr addrspace(4) @air.imageblock_data(<2 x i16> %8, i32 0, i16 0) #9
  %13 = load <4 x i16>, ptr addrspace(2) %6, align 8, !alias.scope !33, !noalias !36
  %14 = shufflevector <4 x i16> %13, <4 x i16> poison, <2 x i32> <i32 0, i32 1>
  %15 = icmp ule <2 x i16> %14, %7
  %16 = shufflevector <4 x i16> %13, <4 x i16> poison, <2 x i32> <i32 2, i32 3>
  %17 = add <2 x i16> %14, %16
  %18 = icmp ugt <2 x i16> %17, %7
  %19 = and <2 x i1> %18, %15
  %20 = tail call i1 @air.all.v2i1(<2 x i1> %19) #10
  %21 = tail call i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none) %1) #11, !alias.scope !40, !noalias !41
  br i1 %21, label %107, label %22

22:                                               ; preds = %11
  %23 = tail call fast <2 x float> @air.convert.f.v2f32.u.v2i16(<2 x i16> %7) #10
  %24 = fadd fast <2 x float> %23, splat (float 5.000000e-01)
  %25 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %1, ptr addrspace(2) readonly captures(none) @__air_sampler_state, <2 x float> %24, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #12
  %26 = extractvalue { <4 x half>, i8 } %25, 0
  %27 = shufflevector <4 x half> %26, <4 x half> poison, <3 x i32> <i32 0, i32 1, i32 2>
  %28 = getelementptr inbounds %struct.SSRColorConversion.191, ptr addrspace(2) %5, i64 0, i32 0
  %29 = load i32, ptr addrspace(2) %28, align 16, !tbaa !42, !alias.scope !49, !noalias !50
  %30 = tail call fastcc <3 x half> @_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_(<3 x half> noundef %27, i32 noundef %29) #13
  %31 = icmp eq i32 %29, 6
  br i1 %31, label %32, label %68

32:                                               ; preds = %22
  %33 = tail call fast half @air.log2.f16(half 0xH2E66) #10
  %34 = tail call fast half @air.pow.f16(half 0xH3C72, half %33) #10
  %35 = fpext half %34 to float
  %36 = fmul fast float %35, 0x3FF3333340000000
  %37 = fptrunc float %36 to half
  %38 = extractelement <3 x half> %30, i64 0
  %39 = fpext half %38 to float
  %40 = fmul fast float %39, 0x3FD0D013A0000000
  %41 = extractelement <3 x half> %30, i64 1
  %42 = fpext half %41 to float
  %43 = fmul fast float %42, 0x3FE5B22D00000000
  %44 = fadd fast float %40, %43
  %45 = extractelement <3 x half> %30, i64 2
  %46 = fpext half %45 to float
  %47 = fmul fast float %46, 0x3FAE5C91E0000000
  %48 = fadd fast float %44, %47
  %49 = fpext half %37 to float
  %50 = fadd fast float %49, -1.000000e+00
  %51 = tail call fast float @air.fast_pow.f32(float %48, float %50) #10
  %52 = fptrunc float %51 to half
  %53 = fmul fast half %38, 0xH32D1
  %54 = fmul fast half %41, 0xH39B8
  %55 = fadd fast half %53, %54
  %56 = fmul fast half %45, 0xH2C9C
  %57 = fadd fast half %55, %56
  %58 = tail call fast half @air.fmax.f16(half %38, half %41) #10
  %59 = tail call fast half @air.fmax.f16(half %58, half %45) #10
  %60 = fadd fast half %57, %59
  %61 = fmul fast half %60, 0xH3800
  %62 = fadd fast half %37, 0xHBC00
  %63 = tail call fast half @air.pow.f16(half %61, half %62) #10
  %64 = getelementptr inbounds %struct.SSRColorConversion.191, ptr addrspace(2) %5, i64 0, i32 3
  %65 = load i8, ptr addrspace(2) %64, align 16, !tbaa !51, !range !52, !alias.scope !49, !noalias !50
  %66 = icmp eq i8 %65, 0
  %67 = select fast i1 %66, half %52, half %63
  br label %68

68:                                               ; preds = %32, %22
  %69 = phi half [ %67, %32 ], [ 0xH3C00, %22 ]
  %70 = insertelement <3 x half> poison, half %69, i64 0
  %71 = shufflevector <3 x half> %70, <3 x half> poison, <3 x i32> zeroinitializer
  %72 = fmul fast <3 x half> %71, %30
  %73 = getelementptr inbounds %struct.SSRColorConversion.191, ptr addrspace(2) %5, i64 0, i32 2, i32 0, i64 0
  %74 = load <3 x float>, ptr addrspace(2) %73, align 16, !tbaa !53, !alias.scope !49, !noalias !50
  %75 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %74) #10
  %76 = getelementptr inbounds %struct.SSRColorConversion.191, ptr addrspace(2) %5, i64 0, i32 2, i32 0, i64 1
  %77 = load <3 x float>, ptr addrspace(2) %76, align 16, !tbaa !53, !alias.scope !49, !noalias !50
  %78 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %77) #10
  %79 = getelementptr inbounds %struct.SSRColorConversion.191, ptr addrspace(2) %5, i64 0, i32 2, i32 0, i64 2
  %80 = load <3 x float>, ptr addrspace(2) %79, align 16, !tbaa !53, !alias.scope !49, !noalias !50
  %81 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float> %80) #10
  %82 = shufflevector <3 x half> %72, <3 x half> poison, <3 x i32> zeroinitializer
  %83 = fmul fast <3 x half> %82, %75
  %84 = shufflevector <3 x half> %72, <3 x half> undef, <3 x i32> <i32 1, i32 1, i32 1>
  %85 = fmul fast <3 x half> %78, %84
  %86 = fadd fast <3 x half> %83, %85
  %87 = shufflevector <3 x half> %72, <3 x half> undef, <3 x i32> <i32 2, i32 2, i32 2>
  %88 = fmul fast <3 x half> %81, %87
  %89 = fadd fast <3 x half> %86, %88
  %90 = extractelement <3 x half> %89, i64 0
  %91 = extractelement <3 x half> %89, i64 1
  %92 = extractelement <3 x half> %89, i64 2
  %93 = tail call fast half @air.fmin3.f16(half %90, half %91, half %92) #10
  %94 = tail call fast half @air.fmax3.f16(half %90, half %91, half %92) #10
  %95 = tail call fast half @air.dot.v3f16(<3 x half> %89, <3 x half> splat (half 0xH3555)) #10
  %96 = select fast i1 %20, half %93, half 0xH7BFF
  %97 = bitcast ptr addrspace(4) %12 to ptr addrspace(4)
  store half %96, ptr addrspace(4) %97, align 2, !tbaa !55
  %98 = select fast i1 %20, half %94, half 0xHFBFF
  %99 = getelementptr inbounds i8, ptr addrspace(4) %12, i64 2
  %100 = bitcast ptr addrspace(4) %99 to ptr addrspace(4)
  store half %98, ptr addrspace(4) %100, align 2, !tbaa !58
  %101 = select fast i1 %20, half %95, half 0xH0000
  %102 = getelementptr inbounds i8, ptr addrspace(4) %12, i64 4
  %103 = bitcast ptr addrspace(4) %102 to ptr addrspace(4)
  store half %101, ptr addrspace(4) %103, align 2, !tbaa !59
  %104 = select fast i1 %20, half 0xH3C00, half 0xH0000
  %105 = getelementptr inbounds i8, ptr addrspace(4) %12, i64 6
  %106 = bitcast ptr addrspace(4) %105 to ptr addrspace(4)
  store half %104, ptr addrspace(4) %106, align 2, !tbaa !60
  br label %126

107:                                              ; preds = %11
  %108 = tail call ptr addrspace(2) @air.get_read_sampler() #14
  %109 = tail call { <4 x half>, i8 } @air.read_texture_2d.i16.v4f16(ptr addrspace(1) readonly captures(none) %2, ptr addrspace(2) %108, <2 x i16> %7, <2 x i16> zeroinitializer, i16 0, i32 3) #11
  %110 = extractvalue { <4 x half>, i8 } %109, 0
  %111 = extractelement <4 x half> %110, i64 0
  %112 = select fast i1 %20, half %111, half 0xH7BFF
  %113 = bitcast ptr addrspace(4) %12 to ptr addrspace(4)
  store half %112, ptr addrspace(4) %113, align 2, !tbaa !55
  %114 = extractelement <4 x half> %110, i64 1
  %115 = select fast i1 %20, half %114, half 0xHFBFF
  %116 = getelementptr inbounds i8, ptr addrspace(4) %12, i64 2
  %117 = bitcast ptr addrspace(4) %116 to ptr addrspace(4)
  store half %115, ptr addrspace(4) %117, align 2, !tbaa !58
  %118 = extractelement <4 x half> %110, i64 2
  %119 = select fast i1 %20, half %118, half 0xH0000
  %120 = getelementptr inbounds i8, ptr addrspace(4) %12, i64 4
  %121 = bitcast ptr addrspace(4) %120 to ptr addrspace(4)
  store half %119, ptr addrspace(4) %121, align 2, !tbaa !59
  %122 = extractelement <4 x half> %110, i64 3
  %123 = select fast i1 %20, half %122, half 0xH0000
  %124 = getelementptr inbounds i8, ptr addrspace(4) %12, i64 6
  %125 = bitcast ptr addrspace(4) %124 to ptr addrspace(4)
  store half %123, ptr addrspace(4) %125, align 2, !tbaa !60
  br label %126

126:                                              ; preds = %107, %68
  %127 = phi half [ %123, %107 ], [ %104, %68 ]
  %128 = phi half [ %119, %107 ], [ %101, %68 ]
  %129 = phi half [ %115, %107 ], [ %98, %68 ]
  %130 = phi half [ %112, %107 ], [ %96, %68 ]
  %131 = extractelement <2 x i16> %9, i64 0
  %132 = icmp ult i16 %131, 2
  br i1 %132, label %192, label %133

133:                                              ; preds = %126
  %134 = bitcast ptr addrspace(4) %12 to ptr addrspace(4)
  %135 = getelementptr inbounds i8, ptr addrspace(4) %12, i64 2
  %136 = bitcast ptr addrspace(4) %135 to ptr addrspace(4)
  %137 = getelementptr inbounds i8, ptr addrspace(4) %12, i64 4
  %138 = bitcast ptr addrspace(4) %137 to ptr addrspace(4)
  %139 = getelementptr inbounds i8, ptr addrspace(4) %12, i64 6
  %140 = bitcast ptr addrspace(4) %139 to ptr addrspace(4)
  br label %141

141:                                              ; preds = %156, %133
  %142 = phi i16 [ %131, %133 ], [ %143, %156 ]
  %143 = lshr i16 %142, 1
  %144 = insertelement <2 x i16> poison, i16 %143, i64 0
  %145 = shufflevector <2 x i16> %144, <2 x i16> poison, <2 x i32> zeroinitializer
  %146 = icmp ule <2 x i16> %145, %8
  %147 = tail call i1 @air.any.v2i1(<2 x i1> %146) #10
  br i1 %147, label %212, label %148

148:                                              ; preds = %141
  tail call void @air.wg.barrier(i32 8, i32 5, i32 1) #15
  br label %149

149:                                              ; preds = %162, %148
  %150 = phi i16 [ 0, %148 ], [ %163, %162 ]
  %151 = phi half [ 0xH0000, %148 ], [ %191, %162 ]
  %152 = phi half [ 0xH0000, %148 ], [ %190, %162 ]
  %153 = phi half [ 0xHFBFF, %148 ], [ %182, %162 ]
  %154 = phi half [ 0xH7BFF, %148 ], [ %178, %162 ]
  %155 = insertelement <2 x i16> undef, i16 %150, i64 0
  br label %165

156:                                              ; preds = %162
  %157 = fdiv fast half %190, %191
  %158 = fcmp fast ogt half %191, 0xH1400
  %159 = select fast i1 %158, half %157, half 0xH0000
  %160 = fmul fast half %191, 0xH3400
  store half %178, ptr addrspace(4) %134, align 2, !tbaa !55
  store half %182, ptr addrspace(4) %136, align 2, !tbaa !58
  store half %159, ptr addrspace(4) %138, align 2, !tbaa !59
  store half %160, ptr addrspace(4) %140, align 2, !tbaa !60
  %161 = icmp ult i16 %142, 4
  br i1 %161, label %192, label %141, !llvm.loop !61

162:                                              ; preds = %165
  %163 = add nuw nsw i16 %150, 1
  %164 = icmp eq i16 %163, 2
  br i1 %164, label %156, label %149, !llvm.loop !63

165:                                              ; preds = %165, %149
  %166 = phi i1 [ true, %149 ], [ false, %165 ]
  %167 = phi i16 [ 0, %149 ], [ 1, %165 ]
  %168 = phi half [ %151, %149 ], [ %191, %165 ]
  %169 = phi half [ %152, %149 ], [ %190, %165 ]
  %170 = phi half [ %153, %149 ], [ %182, %165 ]
  %171 = phi half [ %154, %149 ], [ %178, %165 ]
  %172 = insertelement <2 x i16> %155, i16 %167, i64 1
  %173 = mul <2 x i16> %172, %145
  %174 = add <2 x i16> %173, %8
  %175 = tail call ptr addrspace(4) @air.imageblock_data(<2 x i16> %174, i32 0, i16 0) #9
  %176 = bitcast ptr addrspace(4) %175 to ptr addrspace(4)
  %177 = load half, ptr addrspace(4) %176, align 2, !tbaa !55
  %178 = tail call fast half @air.fmin.f16(half %171, half %177) #10
  %179 = getelementptr inbounds i8, ptr addrspace(4) %175, i64 2
  %180 = bitcast ptr addrspace(4) %179 to ptr addrspace(4)
  %181 = load half, ptr addrspace(4) %180, align 2, !tbaa !58
  %182 = tail call fast half @air.fmax.f16(half %170, half %181) #10
  %183 = getelementptr inbounds i8, ptr addrspace(4) %175, i64 4
  %184 = bitcast ptr addrspace(4) %183 to ptr addrspace(4)
  %185 = load half, ptr addrspace(4) %184, align 2, !tbaa !59
  %186 = getelementptr inbounds i8, ptr addrspace(4) %175, i64 6
  %187 = bitcast ptr addrspace(4) %186 to ptr addrspace(4)
  %188 = load half, ptr addrspace(4) %187, align 2, !tbaa !60
  %189 = fmul fast half %188, %185
  %190 = fadd fast half %189, %169
  %191 = fadd fast half %188, %168
  br i1 %166, label %165, label %162, !llvm.loop !64

192:                                              ; preds = %156, %126
  %193 = phi half [ %127, %126 ], [ %160, %156 ]
  %194 = phi half [ %128, %126 ], [ %159, %156 ]
  %195 = phi half [ %129, %126 ], [ %182, %156 ]
  %196 = phi half [ %130, %126 ], [ %178, %156 ]
  %197 = icmp eq <2 x i16> %10, splat (i16 1)
  %198 = tail call i1 @air.all.v2i1(<2 x i1> %197) #10
  br i1 %198, label %199, label %206

199:                                              ; preds = %192
  %200 = fpext half %196 to float
  %201 = getelementptr inbounds %struct.SSRBasicStats, ptr addrspace(1) %4, i64 0, i32 0
  store float %200, ptr addrspace(1) %201, align 4, !tbaa !65, !alias.scope !67, !noalias !68
  %202 = fpext half %195 to float
  %203 = getelementptr inbounds %struct.SSRBasicStats, ptr addrspace(1) %4, i64 0, i32 1
  store float %202, ptr addrspace(1) %203, align 4, !tbaa !69, !alias.scope !67, !noalias !68
  %204 = fpext half %194 to float
  %205 = getelementptr inbounds %struct.SSRBasicStats, ptr addrspace(1) %4, i64 0, i32 2
  store float %204, ptr addrspace(1) %205, align 4, !tbaa !70, !alias.scope !67, !noalias !68
  br label %212

206:                                              ; preds = %192
  %207 = insertelement <4 x half> undef, half %196, i64 0
  %208 = insertelement <4 x half> %207, half %195, i64 1
  %209 = insertelement <4 x half> %208, half %194, i64 2
  %210 = insertelement <4 x half> %209, half %193, i64 3
  %211 = udiv <2 x i16> %7, %9
  tail call void @air.write_texture_2d.i16.v4f16(ptr addrspace(1) captures(none) %3, <2 x i16> %211, <4 x half> %210, i16 0, i32 3) #16, !alias.scope !40, !noalias !41
  br label %212

212:                                              ; preds = %206, %199, %141
  ret void
}

; Function Attrs: mustprogress nounwind willreturn memory(argmem: readwrite)
declare void @air.write_texture_2d.i16.v4f16(ptr addrspace(1) captures(none), <2 x i16>, <4 x half>, i16, i32) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i1 @air.all.v2i1(<2 x i1>) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmax.f16(half, half) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmin.f16(half, half) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nounwind willreturn memory(read)
declare ptr addrspace(4) @air.imageblock_data(<2 x i16>, i32, i16) local_unnamed_addr #3

; Function Attrs: convergent mustprogress nounwind willreturn
declare void @air.wg.barrier(i32, i32, i32) local_unnamed_addr #4

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare i1 @air.any.v2i1(<2 x i1>) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare { <4 x half>, i8 } @air.read_texture_2d.i16.v4f16(ptr addrspace(1) readonly captures(none), ptr addrspace(2), <2 x i16>, <2 x i16>, i16, i32) local_unnamed_addr #5

; Function Attrs: mustprogress nofree nounwind willreturn memory(inaccessiblemem: read)
declare ptr addrspace(2) @air.get_read_sampler() local_unnamed_addr #6

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.dot.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmax3.f16(half, half, half) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.fmin3.f16(half, half, half) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.convert.f.v3f16.f.v3f32(<3 x float>) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.pow.f16(half, half) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare float @air.fast_pow.f32(float, float) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare half @air.log2.f16(half) local_unnamed_addr #2

; Function Attrs: inlinehint mustprogress nofree nosync nounwind willreturn memory(none)
define internal fastcc <3 x half> @_ZN3CMIL16linearFromCurvedIDhLj3EEEDvT0__T_S2_19CMITransferFunctionS1_(<3 x half> noundef %0, i32 noundef %1) unnamed_addr #7 {
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
  %5 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #10
  %6 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #10
  %7 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %6, <3 x half> splat (half 0xH3C00)) #10
  %8 = fmul fast <3 x half> %7, %5
  br label %75

9:                                                ; preds = %2
  %10 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #10
  %11 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #10
  %12 = fmul fast <3 x half> %11, splat (half 0xH2CF4)
  %13 = fadd fast <3 x half> %11, splat (half 0xH2B0A)
  %14 = fmul fast <3 x half> %13, splat (half 0xH3B96)
  %15 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %14, <3 x half> splat (half 0xH40CD)) #10
  %16 = fcmp fast ogt <3 x half> %11, splat (half 0xH292D)
  %17 = select fast <3 x i1> %16, <3 x half> %15, <3 x half> %12
  %18 = fmul fast <3 x half> %17, %10
  br label %75

19:                                               ; preds = %2
  %20 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #10
  %21 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #10
  %22 = fmul fast <3 x half> %21, splat (half 0xH331C)
  %23 = fadd fast <3 x half> %21, splat (half 0xH2E56)
  %24 = fmul fast <3 x half> %23, splat (half 0xH3B48)
  %25 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %24, <3 x half> splat (half 0xH4072)) #10
  %26 = fcmp fast ogt <3 x half> %21, splat (half 0xH2D30)
  %27 = select fast <3 x i1> %26, <3 x half> %25, <3 x half> %22
  %28 = fmul fast <3 x half> %27, %20
  br label %75

29:                                               ; preds = %2
  %30 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #10
  %31 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #10
  %32 = fmul fast <3 x half> %31, splat (half 0xH331C)
  %33 = fadd fast <3 x half> %31, splat (half 0xH2E5B)
  %34 = fmul fast <3 x half> %33, splat (half 0xH3B46)
  %35 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %34, <3 x half> splat (half 0xH4072)) #10
  %36 = fcmp fast ogt <3 x half> %31, splat (half 0xH2D33)
  %37 = select fast <3 x i1> %36, <3 x half> %35, <3 x half> %32
  %38 = fmul fast <3 x half> %37, %30
  br label %75

39:                                               ; preds = %2
  %40 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #10
  %41 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #10
  %42 = fmul fast <3 x half> %41, %41
  %43 = fmul fast <3 x half> %42, splat (half 0xH3555)
  %44 = fadd fast <3 x half> %41, splat (half 0xHB87B)
  %45 = fmul fast <3 x half> %44, splat (half 0xH4598)
  %46 = tail call fast <3 x half> @air.exp.v3f16(<3 x half> %45) #10
  %47 = fadd fast <3 x half> %46, splat (half 0xH348E)
  %48 = fmul fast <3 x half> %47, splat (half 0xH2D55)
  %49 = fcmp fast ogt <3 x half> %41, splat (half 0xH3800)
  %50 = select fast <3 x i1> %49, <3 x half> %48, <3 x half> %43
  %51 = fmul fast <3 x half> %50, %40
  br label %75

52:                                               ; preds = %2
  %53 = fadd fast <3 x half> %0, splat (half 0xHB98C)
  %54 = fmul fast <3 x half> %53, splat (half 0xH49D9)
  %55 = tail call fast <3 x half> @air.powr.v3f16(<3 x half> splat (half 0xH4000), <3 x half> %54) #10
  %56 = fadd fast <3 x half> %55, splat (half 0xHA0F0)
  %57 = fcmp fast oge <3 x half> %0, splat (half 0xH32AC)
  %58 = select fast <3 x i1> %57, <3 x half> %56, <3 x half> splat (half 0xHAB38)
  %59 = fmul fast <3 x half> %0, splat (half 0xH256A)
  %60 = tail call fast <3 x half> @air.sqrt.v3f16(<3 x half> %59) #10
  %61 = fadd fast <3 x half> %60, splat (half 0xHAB38)
  %62 = fcmp fast oge <3 x half> %0, zeroinitializer
  %63 = fcmp fast olt <3 x half> %0, splat (half 0xH32AC)
  %64 = and <3 x i1> %62, %63
  %65 = select fast <3 x i1> %64, <3 x half> %61, <3 x half> %58
  br label %75

66:                                               ; preds = %2
  %67 = tail call fast <3 x half> @air.sign.v3f16(<3 x half> %0) #10
  %68 = tail call fast <3 x half> @air.fabs.v3f16(<3 x half> %0) #10
  %69 = fadd fast <3 x half> %68, splat (half 0xH3900)
  %70 = fdiv fast <3 x half> %69, zeroinitializer
  %71 = tail call fast <3 x half> @air.pow.v3f16(<3 x half> %70, <3 x half> splat (half 0xH3F33)) #10
  %72 = fcmp fast ogt <3 x half> %68, splat (half 0xH1800)
  %73 = select fast <3 x i1> %72, <3 x half> %71, <3 x half> %68
  %74 = fmul fast <3 x half> %73, %67
  br label %75

75:                                               ; preds = %66, %52, %39, %29, %19, %9, %4, %3, %2
  %76 = phi <3 x half> [ zeroinitializer, %2 ], [ %74, %66 ], [ %65, %52 ], [ %51, %39 ], [ %38, %29 ], [ %28, %19 ], [ %18, %9 ], [ %8, %4 ], [ %0, %3 ]
  ret <3 x half> %76
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.pow.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.fabs.v3f16(<3 x half>) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.sign.v3f16(<3 x half>) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.sqrt.v3f16(<3 x half>) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.powr.v3f16(<3 x half>, <3 x half>) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <3 x half> @air.exp.v3f16(<3 x half>) local_unnamed_addr #2

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(argmem: read)
declare { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none), ptr addrspace(2) readonly captures(none), <2 x float>, i1, <2 x i32>, i1, float, float, i32) local_unnamed_addr #8

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare <2 x float> @air.convert.f.v2f32.u.v2i16(<2 x i16>) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i1 @air.is_null_texture_2d(ptr addrspace(1) readonly captures(none)) local_unnamed_addr #5

attributes #0 = { convergent nounwind "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="64" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #1 = { mustprogress nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { mustprogress nofree nosync nounwind willreturn memory(none) }
attributes #3 = { mustprogress nofree nounwind willreturn memory(read) }
attributes #4 = { convergent mustprogress nounwind willreturn }
attributes #5 = { mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #6 = { mustprogress nofree nounwind willreturn memory(inaccessiblemem: read) }
attributes #7 = { inlinehint mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="48" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #8 = { convergent mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #9 = { nounwind willreturn memory(read) }
attributes #10 = { nounwind willreturn memory(none) }
attributes #11 = { nounwind willreturn memory(argmem: read) }
attributes #12 = { convergent nounwind willreturn memory(argmem: read) }
attributes #13 = { nobuiltin "no-builtins" }
attributes #14 = { nounwind willreturn memory(inaccessiblemem: read) }
attributes #15 = { convergent nounwind willreturn }
attributes #16 = { nounwind willreturn memory(argmem: readwrite) }

!llvm.module.flags = !{!0, !1, !2, !3, !4, !5, !6, !7, !8}
!llvm.ident = !{!9}
!air.version = !{!10}
!air.language_version = !{!11}
!air.compile_options = !{!12, !13, !14}
!air.kernel = !{!15}
!air.sampler_states = !{!32}

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
!15 = !{ptr @imageReduction, !16, !17}
!16 = !{}
!17 = !{!18, !20, !21, !22, !23, !25, !27, !28, !29, !30, !31}
!18 = !{i32 0, !"air.imageblock", !"explicit", !"air.imageblock_data_size", i32 8, !"air.struct_type_info", !19, !"air.arg_type_align_size", i32 2, !"air.arg_type_name", !"imageblock<IBImageReduction, layout_explicit>", !"air.arg_name", !"ib"}
!19 = !{i32 0, i32 2, i32 0, !"half", !"min", i32 2, i32 2, i32 0, !"half", !"max", i32 4, i32 2, i32 0, !"half", !"avg", i32 6, i32 2, i32 0, !"half", !"occ"}
!20 = !{i32 1, !"air.texture", !"air.location_index", i32 0, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"inputTex"}
!21 = !{i32 2, !"air.texture", !"air.location_index", i32 3, i32 1, !"air.read_write", !"air.arg_type_name", !"texture2d<half, read_write>", !"air.arg_name", !"reductionSrcTex"}
!22 = !{i32 3, !"air.texture", !"air.location_index", i32 4, i32 1, !"air.read_write", !"air.arg_type_name", !"texture2d<half, read_write>", !"air.arg_name", !"reductionDstTex"}
!23 = !{i32 4, !"air.buffer", !"air.buffer_size", i32 12, !"air.location_index", i32 2, i32 1, !"air.read_write", !"air.address_space", i32 1, !"air.struct_type_info", !24, !"air.arg_type_size", i32 12, !"air.arg_type_align_size", i32 4, !"air.arg_type_name", !"SSRBasicStats", !"air.arg_name", !"stats"}
!24 = !{i32 0, i32 4, i32 0, !"float", !"min", i32 4, i32 4, i32 0, !"float", !"max", i32 8, i32 4, i32 0, !"float", !"avg"}
!25 = !{i32 5, !"air.buffer", !"air.buffer_size", i32 80, !"air.location_index", i32 0, i32 1, !"air.read", !"air.address_space", i32 2, !"air.struct_type_info", !26, !"air.arg_type_size", i32 80, !"air.arg_type_align_size", i32 16, !"air.arg_type_name", !"SSRColorConversion", !"air.arg_name", !"colorConversion"}
!26 = !{i32 0, i32 4, i32 0, !"uint", !"transferFunction", i32 16, i32 48, i32 0, !"float3x3", !"colorConversionMatrix", i32 64, i32 1, i32 0, !"bool", !"useVELuma"}
!27 = !{i32 6, !"air.buffer", !"air.buffer_size", i32 8, !"air.location_index", i32 5, i32 1, !"air.read", !"air.address_space", i32 2, !"air.arg_type_size", i32 8, !"air.arg_type_align_size", i32 8, !"air.arg_type_name", !"ushort4", !"air.arg_name", !"roi"}
!28 = !{i32 7, !"air.thread_position_in_grid", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"gid"}
!29 = !{i32 8, !"air.thread_position_in_threadgroup", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"tid"}
!30 = !{i32 9, !"air.threads_per_threadgroup", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"tgSize"}
!31 = !{i32 10, !"air.threadgroups_per_grid", !"air.arg_type_name", !"ushort2", !"air.arg_name", !"tgCount"}
!32 = !{!"air.sampler_state", ptr addrspace(2) @__air_sampler_state}
!33 = !{!34}
!34 = distinct !{!34, !35, !"air-alias-scope-arg(6)"}
!35 = distinct !{!35, !"air-alias-scopes(imageReduction)"}
!36 = !{!37, !38, !39}
!37 = distinct !{!37, !35, !"air-alias-scope-textures"}
!38 = distinct !{!38, !35, !"air-alias-scope-arg(4)"}
!39 = distinct !{!39, !35, !"air-alias-scope-arg(5)"}
!40 = !{!37}
!41 = !{!38, !39, !34}
!42 = !{!43, !44, i64 0}
!43 = !{!"_ZTS18SSRColorConversion", !44, i64 0, !47, i64 16, !48, i64 64}
!44 = !{!"_ZTS19CMITransferFunction", !45, i64 0}
!45 = !{!"omnipotent char", !46, i64 0}
!46 = !{!"Simple C++ TBAA"}
!47 = !{!"_ZTSN5metal6matrixIfLi3ELi3EvEE", !45, i64 0}
!48 = !{!"bool", !45, i64 0}
!49 = !{!39}
!50 = !{!37, !38, !34}
!51 = !{!43, !48, i64 64}
!52 = !{i8 0, i8 2}
!53 = !{!54, !54, i64 0}
!54 = !{!"float", !45, i64 0}
!55 = !{!56, !57, i64 0}
!56 = !{!"_ZTS16IBImageReduction", !57, i64 0, !57, i64 2, !57, i64 4, !57, i64 6}
!57 = !{!"half", !45, i64 0}
!58 = !{!56, !57, i64 2}
!59 = !{!56, !57, i64 4}
!60 = !{!56, !57, i64 6}
!61 = distinct !{!61, !62}
!62 = !{!"llvm.loop.mustprogress"}
!63 = distinct !{!63, !62}
!64 = distinct !{!64, !62}
!65 = !{!66, !54, i64 0}
!66 = !{!"_ZTS13SSRBasicStats", !54, i64 0, !54, i64 4, !54, i64 8}
!67 = !{!38}
!68 = !{!37, !39, !34}
!69 = !{!66, !54, i64 4}
!70 = !{!66, !54, i64 8}
