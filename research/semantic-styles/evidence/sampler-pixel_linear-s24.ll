target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v24:32:32-v32:32:32-v48:64:64-v64:64:64-v96:128:128-v128:128:128-v192:256:256-v256:256:256-v512:512:512-v1024:1024:1024-n8:16:32"
target triple = "air64-apple-macosx15.0.0"

@__air_sampler_state.2 = internal addrspace(2) constant i64 -9188470239253722551, align 8

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(argmem: readwrite)
define void @pixel_linear(ptr addrspace(1) readonly captures(none) %t.coerce, ptr addrspace(1) noundef readonly captures(none) "air-buffer-no-alias" %u, ptr addrspace(1) noundef writeonly captures(none) "air-buffer-no-alias" %o, i32 noundef %i) local_unnamed_addr #0 !dbg !26 {
entry:
  %idxprom = zext i32 %i to i64, !dbg !29
  %arrayidx = getelementptr inbounds <2 x float>, ptr addrspace(1) %u, i64 %idxprom, !dbg !29
  %0 = load <2 x float>, ptr addrspace(1) %arrayidx, align 8, !dbg !29, !tbaa !30, !alias.scope !34, !noalias !41
  %1 = tail call { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none) %t.coerce, ptr addrspace(2) readonly captures(none) @__air_sampler_state.2, <2 x float> %0, i1 true, <2 x i32> zeroinitializer, i1 false, float 0.000000e+00, float 0.000000e+00, i32 0) #2, !dbg !48
  %2 = extractvalue { <4 x half>, i8 } %1, 0, !dbg !48
  %arrayidx2 = getelementptr inbounds <4 x half>, ptr addrspace(1) %o, i64 %idxprom, !dbg !52
  store <4 x half> %2, ptr addrspace(1) %arrayidx2, align 8, !dbg !53, !tbaa !54, !alias.scope !56, !noalias !57
  ret void, !dbg !58
}

; Function Attrs: convergent mustprogress nofree nounwind willreturn memory(argmem: read)
declare { <4 x half>, i8 } @air.sample_texture_2d.v4f16(ptr addrspace(1) readonly captures(none), ptr addrspace(2) readonly captures(none), <2 x float>, i1, <2 x i32>, i1, float, float, i32) local_unnamed_addr #1

attributes #0 = { convergent mustprogress nofree nounwind willreturn memory(argmem: readwrite) "approx-func-fp-math"="true" "frame-pointer"="all" "min-legal-vector-width"="64" "no-builtins" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "unsafe-fp-math"="true" }
attributes #1 = { convergent mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #2 = { convergent nounwind willreturn memory(argmem: read) }

!llvm.module.flags = !{!0, !1, !2, !3, !4, !5, !6, !7, !8, !9}
!air.version = !{!10}
!llvm.dbg.cu = !{!11}
!llvm.ident = !{!13}
!air.language_version = !{!14}
!air.compile_options = !{!15, !16, !17}
!air.sampler_states = !{!18}
!air.kernel = !{!19}

!0 = !{i32 7, !"air.max_device_buffers", i32 31}
!1 = !{i32 7, !"air.max_constant_buffers", i32 31}
!2 = !{i32 7, !"air.max_threadgroup_buffers", i32 31}
!3 = !{i32 7, !"air.max_textures", i32 128}
!4 = !{i32 7, !"air.max_read_write_textures", i32 8}
!5 = !{i32 7, !"air.max_samplers", i32 16}
!6 = !{i32 2, !"Debug Info Version", i32 3}
!7 = !{i32 1, !"wchar_size", i32 4}
!8 = !{i32 7, !"frame-pointer", i32 2}
!9 = !{i32 7, !"air.workaround.sampler_state_variable_length_encoding", i1 true}
!10 = !{i32 2, i32 7, i32 0}
!11 = distinct !DICompileUnit(language: DW_LANG_Metal, file: !12, producer: "Apple metal version 32023.921 (metalfe-32023.921.5)", isOptimized: true, runtimeVersion: 0, emissionKind: LineTablesOnly, splitDebugInlining: false, nameTableKind: None)
!12 = !DIFile(filename: "<stdin>", directory: "/")
!13 = !{!"Apple metal version 32023.921 (metalfe-32023.921.5)"}
!14 = !{!"Metal", i32 3, i32 2, i32 0}
!15 = !{!"air.compile.denorms_disable"}
!16 = !{!"air.compile.fast_math_enable"}
!17 = !{!"air.compile.framebuffer_fetch_enable"}
!18 = !{!"air.sampler_state", ptr addrspace(2) @__air_sampler_state.2}
!19 = !{ptr @pixel_linear, !20, !21}
!20 = !{}
!21 = !{!22, !23, !24, !25}
!22 = !{i32 0, !"air.texture", !"air.location_index", i32 0, i32 1, !"air.sample", !"air.arg_type_name", !"texture2d<half, sample>", !"air.arg_name", !"t"}
!23 = !{i32 1, !"air.buffer", !"air.location_index", i32 0, i32 1, !"air.read", !"air.address_space", i32 1, !"air.arg_type_size", i32 8, !"air.arg_type_align_size", i32 8, !"air.arg_type_name", !"float2", !"air.arg_name", !"u"}
!24 = !{i32 2, !"air.buffer", !"air.location_index", i32 1, i32 1, !"air.read_write", !"air.address_space", i32 1, !"air.arg_type_size", i32 8, !"air.arg_type_align_size", i32 8, !"air.arg_type_name", !"half4", !"air.arg_name", !"o"}
!25 = !{i32 3, !"air.thread_position_in_grid", !"air.arg_type_name", !"uint", !"air.arg_name", !"i"}
!26 = distinct !DISubprogram(name: "pixel_linear", scope: !27, file: !27, line: 5, type: !28, scopeLine: 5, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !11, retainedNodes: !20)
!27 = !DIFile(filename: "program_source", directory: "/")
!28 = !DISubroutineType(types: !20)
!29 = !DILocation(line: 5, column: 258, scope: !26)
!30 = !{!31, !31, i64 0}
!31 = !{!"float", !32, i64 0}
!32 = !{!"omnipotent char", !33, i64 0}
!33 = !{!"Simple C++ TBAA"}
!34 = !{!35, !37, !39}
!35 = distinct !{!35, !36, !"air-alias-scope-arg(1)"}
!36 = distinct !{!36, !"air-alias-scopes(pixel_linear)"}
!37 = distinct !{!37, !38, !"air-alias-scope-arg(1)"}
!38 = distinct !{!38, !"air-alias-scopes-loader(pixel_linear)"}
!39 = distinct !{!39, !40, !"air-alias-scope-arg(1)"}
!40 = distinct !{!40, !"air-alias-scopes-device-lowering(pixel_linear)"}
!41 = !{!42, !43, !44, !45, !46, !47}
!42 = distinct !{!42, !36, !"air-alias-scope-textures"}
!43 = distinct !{!43, !36, !"air-alias-scope-arg(2)"}
!44 = distinct !{!44, !38, !"air-alias-scope-textures"}
!45 = distinct !{!45, !38, !"air-alias-scope-arg(2)"}
!46 = distinct !{!46, !40, !"air-alias-scope-textures"}
!47 = distinct !{!47, !40, !"air-alias-scope-arg(2)"}
!48 = !DILocation(line: 47, column: 12, scope: !49, inlinedAt: !51)
!49 = distinct !DISubprogram(name: "sample", scope: !50, file: !50, line: 44, type: !28, scopeLine: 45, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !11, retainedNodes: !20)
!50 = !DIFile(filename: "/System/Library/PrivateFrameworks/GPUCompiler.framework/Versions/32023/Libraries/lib/clang/32023/include/metal/__bits/metal_texture2d", directory: "")
!51 = distinct !DILocation(line: 5, column: 249, scope: !26)
!52 = !DILocation(line: 5, column: 242, scope: !26)
!53 = !DILocation(line: 5, column: 246, scope: !26)
!54 = !{!55, !55, i64 0}
!55 = !{!"half", !32, i64 0}
!56 = !{!43, !45, !47}
!57 = !{!42, !35, !44, !37, !46, !39}
!58 = !DILocation(line: 5, column: 264, scope: !26)
