# 当前目标状态（S47）

目标active。A阶段尚未完成，总acceptance_complete=false。HDR制作/承载与物理scene恢复分别验收，global/local/人物/皮肤/纹理独立，原门槛/mask/Apple Log不改，不重启旧bit-exact拟合。

已验证数值：S42五张原尺寸原host RGB guided（r1/eps.001），两张本配方留出；10EXR实际存读一致，25未编码headroom公式通过。S47复用IMG2600母版做独立显示曝光+3.718534EV与全局滚降，母版/原件SHA不变；10个原生公式maxabs 4.7088888806e-06 /PSNR最低132.827092dB。零offset承载coverage97.7627%，该区native目标maxrelative 1.56001707439e-06；公共offset100%数学覆盖但relative 0.0253673864137、h1差5.96e-8，未过。两种mask都不替代原逆mask。

未完成：新显示配方仍仅1开发照片；新编码HEIF目标/全尺寸原ImageIO SDR max0、旧2048+面积约束对照和锚点近零/阈值分类仍需runner。33皮肤点全域tight hull/C01-C05可继续静态/runner，不归成全只能实机。S42相对母版仍是假设，global-only给定GTC并不等于真实相机GTM恢复，语义/纹理残留不冒充清除。

只能实机补证：同帧j/WithoutFaceBoost曲线/统计/应用域、原Studio统计、RAW2679/2408、HDR屏幕/观看环境及PhotosUI。参照NATIVE_TODO执行方案。

预览固定ACES1.0 SDR Video/0EV；原生不同headroom可看候选contact，实际HDR屏幕另验。S42/S47预览只密文传输且已流式GPG/manifest全成员核验。完整S42密文约1.25GB未全套本地保存，额外存储许可待答；其2600密文只做过无持久文件的完整SHA/GPG校验。S47未另归档完整新H/logmap，只保留可再计算配方/输入SHA/指标/密文预览。

临时secret均已删除、无release；研究临时分支在exact source保留和引用检查后清理。source/run/artifact/SHA见run-provenance-s33-s35、s37-s41、s42至s47及各receipt；验证evidence/validation-through-s47.json。master和原件/冻结文件保持。

收尾已完成：15条远端/16条本地本阶段临时分支已在源码保留和引用审查后清理；secret、release、在跑/排队run均为空。审计见final-audit-s33-s47.json。
