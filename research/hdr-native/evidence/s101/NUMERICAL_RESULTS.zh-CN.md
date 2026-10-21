# S101 完整文件交付与证据边界

run 39518274902，source 90d565c7686cd45f55e1d1e4e5fd9b0f6af31ef7，26A434 / image 20261012.0260.1。

**已验证数值：文件交付闭合，未宣称场景恢复或A阶段完成。** 五套各含共同key1 R、global GTC假设、local thumbnail projection候选、相对scene候选四份HALF P3 EXR，独立HDR显示目标FLOAT P3 EXR与HEIC；25 EXR、5HEIC、flags/mask和预览的实际tar成员已逐文件核size/SHA。134public、115private成员认证。5份FLOAT目标EXR与源HDR.f32存储逐位相同，原master EXR匹配旧S42 SHA，5个carrier和M/S/H输入字节匹配旧S89。不是只交清单/hash，也不是新五张或新留出。

ImageIO明确DecodeToSDR的完整整数raster每行active bytes与ICC/格式均相同，变更bytes0；原native CI SDR另行0差。这里只排除row padding，未裁照片，原件不改。全部固定ACES预览输入SHA不变，共55组，30个预览文件留加密包。

| 照片 | headroom2 p99 EV | headroom8 p99 EV | H8有效 / 排除像素 | HDR对目标PSNR(peak1) dB | 锚点area mean EV |
|---|---:|---:|---:|---:|---:|
|IMG_2600|0.0715222056|0.229329278|24374885 / 95323|47.672055|0.33088219|
|IMG_2604|0.00453058794|0.0125815105|24468599 / 1609|50.583226|0.13766734|
|IMG_0032|0.00291300153|0.00873854818|12192768 / 0|55.6757|0.0095316123|
|IMG_2608|0.0111151128|0.0260136114|24440835 / 29373|50.895455|0.20433658|
|IMG_0033|0.00302886086|0.00910381973|12184745 / 8023|56.007563|0.020794927|

EV域沿用旧验证：RGB有限，Yactual>0、Yref>1e-6；排除数量如表，不当作全体像素EV。h1 max abs≤5.96046448e-8；h2/h8相对理想目标的差包含真实量化/codec/provider/metadata，而不是只比实际解码gain方程。HDR最大绝对差最高0.0926685，PSNR47.67–56.01dB，旧max1e-5/PSNR60门槛不通过。原native“实际解码gain代入方程”max仅≤3.91955e-6，并不能替代它与目标HDR的误差。量化与codec/provider分开保存，后者也不可忽略；未归因成新的反演缺项。

原native RGB guided projection的area锚点误差仍如表，IMG2600 mean0.330882/p993.40247EV；原生算法并不保证面积锚点相等，不能把Apple GF的真实性当母版准确性。RGB projection实际r1/eps0.001，与c/d scalar上采样r1/eps0.05区分；无新参数调整。全局结果仍只是假定生产域/顺序的GTC逆，clamp/plateau/nonfinite处NaN/flags保留；各local/global文件共用先逆key1的R，不宣称原片上已独立逆掉真实GTM/LTM。完整文件留存不增加RAW或相机语义真值。

已验证数值（复用，不重跑）：IMG2600的carrier、M/S/H及native HDR/h1/h2/h8数组SHA均与S90已完成10bit variant相同，原ACES配置也相同。原H8全图99.0915443%像素最大RGB码差≤1，267像素>2、23像素>4、max8码；可将该完成的诊断绑定到本次同一文件。不能把它扩大为五张全frame显示验收或真实HDR屏幕/scene精度；其余4张的完整固定ACES与边缘/分亮度统计仍可runner补，12bit provider nil不再测。

大包共2081208288B直接GitHub→日本，private artifact12310032763 SHAb26a2c7c006fc931d93e312b71d64ba556d18ec00f58919fb6d5c14548379908。香港只取738875B公开原始payload、163840B密文头、19314B校验摘要，编码/SSH开销另计，无大包回传。没有新增输入secret/release，临时分支已在PR零引用、源保留、归档校验后清理。五套23成员cipher与完整清单见archive-receipt/full-file-inventory。

下一步：对其余4个同一目标/载体做固定ACES与边缘/亮度分层实用验证，复用已完成IMG2600；不重建旧master或重跑bit-exact。A语义实际烘焙因子仍未识别、face j→实际EV/原Studio统计/配对RAW/实屏按NATIVE_TODO实机计划。S100新增小型ABI读取已因审批拒绝而保持未执行，此限制不波及公开五图的HDR交付与验证。
