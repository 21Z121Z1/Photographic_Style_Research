# Texture 泛化结果与导入包

最终 Apple 原生矩阵通过 **38/38**：26 张独立 XDRemux 原图（28 个 manifest 条目，含 2 份字节重复）、双人压力用例、EXIF 八种方向、512/1024/2048 尺寸覆盖、NASA 回归及直接 CLI。2048 完整链路另连续通过 3/3。

[下载导入包](texture-fixture-imports-39388123337.zip)，27,888,153 字节，29 份候选。

SHA-256：`61b77452391415bd79b440eb32a15025929f906532945614ec197c60876e88f5`。

解压后导入 `originals/` 下的 HEIC。建议先测试 Samsung `jpeg-ultrahdr-01`、vivo 店内场景、OPPO `uhdr-portrait-02`、无人像 `uhdr-hr-01`，以及 `derived/derived-two-fixture-faces.heic`。`controls/` 是同一编码主图的普通对照，`previews/` 是逐人原生效果烘焙图；后者不作为可编辑候选。

每份文件均从本图推理和生产资源。共享几何与遮罩用于原始 Mattify、UnderEyeBrighten、SkinSmoothStandalone 生产入口；按概率全局匹配独立人物实例，并验证实例键、实际有符号角度及可用统计回读。最终重放使用 HEIC 的实际主图、读回人物与原生解码遮罩。空人物上下文不构造人物或不存在的群体统计。原生返回空统计的效果组会明确省略，部分人物效果没有像素变化，详见各收据。

这是新建的 sRGB/8-bit SDR 编辑副本，默认长边 1024；`derived/` 另含 512 和 2048 变体。测试覆盖高分辨率源图的解码与缩放，未证明所有原图分辨率均原样输出。原文件不变，HDR 资源与动态视频没有带入副本。鼻唇眉区域由本图原生人脸点派生，耳部/纹身可选保护禁用，并非完整 FSINC 分割认证。

生成源码：[f3414dec](https://github.com/21Z121Z1/Photographic_Style_Research/tree/f3414decdf5b01451a09e467b68b6f7cf1393ffb/research/texture-generalization-20261020)。原生验收：[Actions 39388123337](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39388123337)。原始生成证据提交：`de46763e5f8f4546435bbce69d0d1e5c813c7bef`。

独立复核见 [LOCAL_QA.json](LOCAL_QA.json)：4,165 份 manifest 文件核验，38 份用例数据重新验证，38 组 ImageMagick/libheif 主图逐字节一致，5 项预览方向检查通过；18 份逐人生产/重放输入快照绑定也已核对。每个用例 ZIP 内含逐文件 SHA 与长度 manifest。`matrix.json` 保存所有用例与原生结果，`DELIVERY.json` 保存准确源码、运行 ID 和包 SHA。

[RUN_HISTORY.json](RUN_HISTORY.json) 保留早期失败和诊断：原生字典的负角度序列化问题、线性分量微小负值、一次 2048 UnderEye SIGSEGV、分配池对照，以及修正生命周期后的三轮与最终验收。没有改写旧结果或 Apple 实现。源码分支 `research/texture-generalization-20261020` 的后续 `2bc4e3d…` 只移除临时自动触发并恢复手动工作流，两个原生源码目录与已测提交逐字节一致。

本批新文件还没有设备结果。此前用户确认可激活的是 SHA `a7ac5d0dc8721e0cac4db6bfec153864f96fc83f406adeedc2036bc6f0543a7b` 的 NASA 候选，见[原设备反馈](https://github.com/21Z121Z1/Photographic_Style_Research/blob/38f1216a567cc57c993b5e5646f6b0a0d944a18e/DEVICE_ACTIVATION.json)。请在此前成功的同一台设备上，分别记录本批控件是否出现、纹理/颗粒与柔肤是否变化，以及保存后重新打开是否保留。云端资格标志保留原始值，没有改成 true。
