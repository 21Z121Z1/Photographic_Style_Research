# 导入测试与激活结果

**2026-10-20：用户确认 `texture-candidate.heic 可以激活了`。** 反馈对应此前交付的候选，SHA-256 为 `a7ac5d0dc8721e0cac4db6bfec153864f96fc83f406adeedc2036bc6f0543a7b`。本文件已有用户确认的设备激活正样；原话、交付绑定与验证范围见 [DEVICE_ACTIVATION.json](DEVICE_ACTIVATION.json)。未提供设备型号、系统版本或设备端文件校验值。

请导入 `import/texture-candidate.heic`；`control.heic` 是同一编码主图的普通对照。
`final-file-mattify-preview.heic` 是效果烘焙预览，不是可编辑候选。

通过文件或 AirDrop 原件保存到照片。在支持相关功能的 iOS 27 设备上，检查候选是否出现摄影风格、纹理/颗粒、柔肤控制；比较对照，修改后保存并重新打开。

云端已验证三组真实 Apple SPI 统计、1 个人物实例、元数据回读，以及最终文件全部遮罩解码后的非零原生重放。结合本次用户反馈，这份单人像候选已有“SPI 生成 → 写入/回读 → 用户确认激活”的完整路径证据。纹理/颗粒与柔肤控件的实际变化、保存后重新打开的保留情况尚未反馈。

运行器的平台支持标志、PhotographicStyleV2 capability 和编辑资格原始值仍为 false，这是云端观测，不推翻用户的设备激活结果。`DELIVERY.json`、`PACKAGE.json`、`LOCAL_QA.json`、`import/acceptance.json` 及原始 ZIP 保留交付当时的内容；其中激活未证明或未测试的字段是反馈前的历史状态。当前设备结果见新增记录，原始证据与 ZIP 字节不变。

这是从公开 NASA 单人像新建的编辑上下文，不是原相机 RAW/拍摄信息恢复。鼻唇眉区域由本图人脸点派生，耳部和纹身的可选保护禁用；手部检测结果为零。通用多人物/无人像和更多方向、分辨率尚未认证。

文件 SHA、准确源码提交和工作流见 `DELIVERY.json` 与 `import/acceptance.json`；完整生成证据见 `evidence/`。
