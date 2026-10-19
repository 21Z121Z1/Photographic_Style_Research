# 当前目标状态（S42）

目标active，A阶段和总acceptance_complete=false。GTM、LTM、语义/人物/纹理逆向分开；相对场景母版与独立HDR显示渲染/承载分开。

已验证数值：原RGB map host在五张原尺寸照片完成r1/eps.001上采样（区别于c/d scalar eps.05），含两张本新配方冻结后留出；十份EXR实际保存重读分量差0；25次未编码原生headroom公式maxabs 5.60320626897e-07、PSNR最低148.357935dB；保存map自洽maxrelative 6.60515477177e-07。固定ACES预览输入SHA不变，预览密文已GPG/manifest验证。

尚未通过：原生锚点均值误差0.0095–0.3309EV，近黑极值更大；旧2048+面积约束基线尚缺，不能称消除边缘伪像。给定GTC的global-only与local-only投影是有边界的候选，不证明拍摄端完整逆。0EV显示下候选偏暗，独立显示曝光仍需设计。新HEIF编码后目标1e-3/PSNR60与全尺寸SDR ImageIO max0未过；S43正在隔离AV1编码候选，不重复源照片投影。旧NumPy half不一致如实保留，不继续追拟合。

只靠实机/额外原始证据：匹配同帧j/WithoutFaceBoost曲线、N/B/T/hist/allocateTone域、原Studio统计、RAW2679/2408、实际HDR屏幕。33点全域tight hull未认证，原mask不动。完整5图EXR/GainMap密文约1.25GB尚未本地下载，受100MB写入和4GB底线限制；指标与预览已归档，额外存储许可待答。

具体source commit、run/artifact/SHA见run-provenance-s42.json，验证见evidence/validation-through-s42.json；master和冻结模型未改。
