# 从图像生产 Texture 信息并写入 HEIC

本轮已取得真实的 Apple SPI 生产结果，写入并原生验证 HEIC；**用户于 2026-10-20 确认：`texture-candidate.heic 可以激活了`。** 这份已交付单人像候选已有“SPI 生成 → 写入/回读 → 用户确认激活”的完整路径证据。云端验收与用户设备反馈分别保留，不以解码或单效果渲染代替激活反馈。

该候选 SHA-256 为 `a7ac5d0dc8721e0cac4db6bfec153864f96fc83f406adeedc2036bc6f0543a7b`，332177 字节。原话、交付文件绑定及未反馈项目见 [DEVICE_ACTIVATION.json](https://github.com/21Z121Z1/Photographic_Style_Research/blob/38f1216a567cc57c993b5e5646f6b0a0d944a18e/DEVICE_ACTIVATION.json)。用户通过文件名回复交付结果，未提供设备端校验值、设备型号或系统版本；助手未直接观察设备 UI。

## 已取得的生产结果

输入采用公开 NASA 人像 `astronaut.png`，512×512，一个实际检测到的人脸和人物实例。没有使用私人相机样张、模板人脸或其他照片的人物统计。

| 原生生产入口 | 从本图取得的结果 |
|---|---|
| `CMITextureStylesMattify.calculateStats/process` | `AverageFaceColor`、`HighlightsToMaskRatio`、`SkipPerson` |
| `CMITextureStylesUnderEyeBrighten.calculateStats/process` | 左右眼平均颜色、亮度方差、双峰判定 |
| `CMITextureStylesSkinSmoothStandalone.calculateStats/process` | 平均脸色、皮肤粗糙度、跳过判定 |

Mattify 在 EV −1、0、+1 下的平均脸色分别约为 `[0.365,0.278,0.216]`、`[0.729,0.553,0.431]`、`[0.996,0.976,0.780]`；加一档的高光比例约为 `0.573`。输入像素哈希和均值也随曝光改变。这些是未预先提供 `imageStats` 时取得的原生输出。

正确顺序是：原生图像解码与色彩转换 → Vision 检测几何/遮罩 → 原生参数选择 → 绑定 IO、全图区域与人物数据 → 初始化工作输出图 → allocator/setup/prewarm/prepare → calculateStats → 提交并等待 → process/收集统计 → finish。原生统计实际采样 `outputImage`；此前空白输出图导致的全零结果已定位并修正。原生渲染也已得到有限、非零的实际像素变化。

`PITextureStyleAutoCalculator` 的默认编辑值不是统计生产入口。`ANSTFsincAlgorithmV2Dot4` 的系统模型在本运行器报 E5 opset 验证错误；完整错误保留，未改模型或 Apple 实现来规避。

## 写入后的闭合验证

候选同时包含普通 Styles 元数据、Linear Thumbnail、Style Delta、12 类 2026 纹理遮罩、旧版头发遮罩，以及带键的逐人实例。

人物实例必须使用 `semanticpersoninstances` 辅助图，并在 XMP 中写入与人物条目一致的 `fsincMattes:InstanceMaskReferenceKey`。只引用聚合的 `semanticpersonmatte` 会被原生解析器跳过。修正后，原生框架从 HEIC 读回 **1 个人物实例、76 个人脸点及三组完整统计**，内容与生产结果匹配。

生产端与写入端共享同一份检测几何和完整原始遮罩上下文，避免重复检测边界漂移。最后的重放从最终 HEIC 提取全部语义和实例图，由 ImageIO 解码十四份标量输入，再连同该文件的主图和原生读回人物数据调用原生 Mattify，绑定该效果支持的必需和可选项。重放不使用编码前的遮罩或新检测出的几何。验收要求命令完成、输出有限、效果非零，并核对每个最终输入文件的 SHA。

资源来源必须连同候选理解：皮肤、头发、牙齿、眼镜和人物来自原生分割；脸部/非脸部皮肤是实测皮肤概率与脸部边界的派生；鼻唇眉来自本图原生人脸点构造的区域，不冒称 FSINC 分割。手部检测成功且本图结果为零。耳部和纹身的可选保护明确禁用，零图不声称已推理出“没有耳部/纹身”。

普通 Styles 是为当前 SDR 图像新建的中性编辑上下文：使用本图像素/人物/皮肤分布、sRGB 传递曲线、实测 light maps、中性系数和新编码的 Apple Log 缩略图。它没有恢复相机 RAW、原拍摄曝光或原 ISP。硬件等字段用于选择原生 tuning，MakerNote 84 仅声明默认编辑设置；未伪造 EXIF 相机型号、ISO、光圈、曝光或拍摄日期。

## 设备激活结果与后续边界

运行器上的 `PITextureStylePipelineProcessor.isAvailable=true`，但 `supportsSemanticStyleRendering=false`，`PhotographicStyleV2` capability 与 `canRenderTextureStylesOnComposition` 原始值仍为 false。现已取得用户确认的设备激活正样；这些 false 保留为云端历史观测，不作为该候选设备激活失败的结论。

本次验证覆盖这张单人像。纹理/颗粒及柔肤控件的实际效果、修改保存后重新打开是否保留、对照文件表现尚未反馈。多人物匹配、无人像流程、更多方向/分辨率和完整 PhotoImaging 渲染尚未取得通用验收；这次激活成功不扩展为“任意输入通用生成器”已完成。

原生生成采用源码 `27122d06d29909e13709a13e4768419dc4473c1f`，[Actions 39370651344](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39370651344) 通过。此次状态更新只增加设备反馈并修正文档，不重跑或改写原生证据。218 份生成证据再次核验 SHA 和长度；原始 ZIP、云端收据和本地 QA 逐字节保留。因此原交付收据中“激活未证明/未测试”的字段表示反馈前的历史状态，当前设备结果以新增反馈记录为准。

## 导入测试

使用测试包内的 `texture-candidate.heic`；`control.heic` 为同一编码主图的普通对照，`final-file-mattify-preview.heic` 只是原生效果烘焙预览。通过文件或 AirDrop 原件导入，保留 HEIC；不要将预览图当作可编辑候选。

在支持相关功能的 iOS 27 设备中，查看候选是否出现摄影风格、纹理/颗粒、柔肤等控制；比较候选与对照，修改后保存并重新打开。记录控件是否出现、效果是否变化、保存后是否保留。设备结果独立于云端 receipt。

源码和复现见 [README.md](README.md)。原生证据按 Actions job 日志、manifest、逐文件 SHA 和准确源码提交绑定；失败结果也保留。本轮仅使用专用研究分支，未合并或发布。旧容器未提交文件仍未核对，本轮未覆盖它们。
