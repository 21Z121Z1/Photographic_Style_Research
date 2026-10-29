# Preview inspection: photographic-fidelity inference withdrawn

**更正：当前探针参考与重建变体均有明显彩色噪点、色阶异常，不能把先前 16.09% / 9.96% 的相对误差改善称为摄影真实性提高。** 三个场景均观察到异常；2604 原始 HEIC 的 SDR 主图使用 libheif 独立解码显示正常。Display P3 参考转换到 sRGB 后异常仍在。尚未定位原生调用、捕获或转换中的具体原因，不把它归咎于联合候选本身。

本轮只新增可选 PNG 导出：原生探针参考、现有默认、固定联合候选在同一 Tone -0.5/+0.5 下比较，使用相同的白色锚点和 Display P3 传递函数，嵌入宿主原生 ICC；没有独立自动曝光或差异增强。18 张原生浮点输出哈希全部与 run-40864970303 一致。它们确为此前报告对应的画面，数值相同不能替代正常成像核验。

[图片导出运行 40869029727](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/40869029727)，artifact `12895522861`。代码 `b1aba0a559c105f99f94be5c23e4055ee8f77102`，原生任务和 41 项便携检查通过，条件固件任务跳过。`passed` 与空间信号检查仅确认程序执行及输出非平坦，未验证图像正常。PR85 未更改或合并。

完整原始数值、PNG 路径与哈希见 [report.json](report.json)，测量代码绑定见 [source-binding.json](source-binding.json)，与上一轮输出的逐张哈希比较、拼图哈希及原始照片独立解码记录见 [provenance.json](provenance.json)。本目录只保存数值和说明；用户请求的 18 张 PNG、六张三列拼图和原始主图预览通过图片附件交付，不把照片提交到 Git。

The native-probe reference and reconstructed variants show severe color artifacts. All 18 floating-point image hashes match the previous spatial run, while IMG_2604's original primary SDR image decodes normally with independent libheif. Color conversion to sRGB does not eliminate the reference artifacts. The fault has not been localized to the native invocation, capture, or export stages. Relative distances remain numerical observations of this pipeline; photographic-fidelity and visual-tolerance conclusions are withdrawn until normal image formation is established. Do not use the current run's success or non-flat-output guard as an acceptance claim.
