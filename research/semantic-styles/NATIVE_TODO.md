<!-- SEMANTIC-20261018 -->

## 人物/皮肤语义：runner 与实机测试边界（2026-10-19）

旧 bit-exact 方向按用户要求停止；不是待重启清单。本阶段尚未完成，既不放宽阈值，也不把缺 RAW 当作所有失败的原因。

### 可交给 macOS runner：皮肤条件逆、失败归因与区间

已完成基线不重做：S5原生 tone0/±.35 参数隔离、S6预览副本重算、S7残差法、S8三种子native求解、S9保存数组审计。S8 run39156000731 的输入/上下文与S5逐字节一致，联合候选仍296个像素>1e-3；归档后以mask逐点区分solver未收敛、已观察到half非唯一、低有限差分Jacobian秩，不能一概称不可逆。完整F往返仍未通过，不能只取成功皮肤像素作新验收mask。

后续代码入口：research/semantic-styles/{semantic_s8.inc,analyze_semantic_s8.py,semantic_s9_analysis.py,semantic_skin_model.py}。输入为S5/S8不可变捕获副本，固定所有纹理、c/d、GTC、guide、ROI、统计；只中和SSRFG.field9/10的592/596偏移（仅26A434）。原输入只供原生oracle/诊断，禁止用作逆解种子。若继续做区间，应固定原声明域，明确输出量化可行集合的上下界；多个根的跨度只是歧义下界，搜索box不是camera先验。不能重启half lattice追逐来掩盖信息丢失。

捕获：F实际、F参数中和、最终残差估计、每点失败/近黑/低秩/歧义/搜索边界mask、预览前后SHA。判据：原有最大相对误差1e-3、原有效mask覆盖率不改；同时报全有效和目标皮肤足迹指标、边缘误差、非目标区域max0。不得由PSNR高单独宣布通过。连续单位模型的自洽性不是原生精度证明。

### 可交给 macOS runner：SkinSmooth 与 Mattify 非零条件单位测试

S4 persons0使三效果走身份路径；已证这一点，不再重复。S7已跑通UnderEye FinalMix（CoreGraphics补链），受控mix.5原生往返9.5877e-4；该连续forward max3.9244e-4仍未达float1e-5，真实相机效果未认证。

下一次单位探针沿under_eye_final_s6.m的MTL设备、原metallib、函数常量UseImageBlocks=false模式，按AIR0150/0151与0067元数据绑定全部参数、ROI、纹理和stats缓冲。先建人工但完整、有限的person stats/blur/mask上下文，使用同一IMG_2810原始512主图/mattes，明确标注人工上下文。每次只改SkinSmooth强度或Mattify editingStrength，保留另一效果、GTM/LTM及mattes；不能用清空person跳过效果作为去皮肤结果。

捕获：checkpoint、MTL错误、LLDB inferior退出码/原生栈、完整绑定SHA、输入/输出half/float、每个blur/reconstruction/texture-addback项、统计、clamp/plateau标志。先用强度0确认identity，再至少两个非零强度确认真实像素变化；随后冻结上游项求条件逆，并用原Apple kernel forward验证。SkinSmooth最终混合可按AIR0151:207–239的已知a/b/B/S做条件逆；一般Mattify包含HSL/min/clamp、依赖X的addback，不能冒用仿射模型。半精度逐位或既定float门槛如未达，记录实际差值并保留失败。重型计算只在xcode-27 runner，一次一个run、retention-days1、人物数据GPG加密。

### 待实机解决：匹配固件的相机人脸/人身提亮

当前静态cache为iPhone12,1/iOS27.0/24A446，样张为另一硬件/27.0.1。需要可调用CameraColorProcessing内部处理的诊断环境；普通macOS consumer不能制造同一帧原相机统计。不得把旧build地址写入未知build。

输入：同一帧主图、thumbnail统计、faceROI/hist/区域统计、driverInput的只读快照，记录精确OS build、framework UUID/SHA。在副本上分别保持原j与启用WithoutFaceBoost（对应build先静态核对），只变该目标参数/开关。捕获computeLtmComputeInput的j位置、faceWeight/WeightV2、global LUT/GTC、local曲线、c/d打包前后、实际应用空间及最终像素。先以原分支重建基准，再分开报告global/local变化和人物内外EV/边缘/颜色，最后用counterfactual确定保守估计幅度与matte的误差。验收沿既定门槛，不把最终图除j当作测试本身。

当前face/body两个预算的方向、色度、自洽性是已验证数值；幅度/空间mask及平滑器是“假设”。body幅度不由j识别。OPPO类base+gain样本需同帧无语义对照或配对RAW和完整相机上下文；否则只能给预算敏感性，不报Apple幅度精度或有限无先验上界。

### 待实机解决：Studio 原始逐人上下文和已丢失纹理

输入：iPhone18Pro/iOS27.0.1同一冻结帧的TextureStylePostProcessedPeopleData、instanceMaskReferenceKey/实例mask、face/faceSkin/instance ROI、landmarks及类型/坐标缩放、pitch/yaw、imageStats及眼部统计、当时tuning。IMG_2810虽有ExifAux单个Face区域，214B texture_styles没有完整逐人上下文；Vision新检测/合成stats只算诊断假设，不能补称原始数据。

在匹配系统的同一帧副本上分别关闭UnderEye、SkinSmooth、Mattify，按原生顺序逐项抓half/float前后像素、blur/editedTex、mask、strengthFactor/颜色统计与调度。原分支必须重建基准、各中和只改目标参数。条件逆需要E/w等真实上下文；原生forward回放原门槛是必要条件，仍需单独测原输入误差与区间覆盖。w=1、clamp或平滑零频率分量无唯一恢复，输出区间/未知，不生成伪造纹理当真值。

### 待实机解决：RAW 与 Photos UI

Mac上的IMG_2679/IMG_2408配对组用于RAW EV精度。GTM、LTM、人脸/人身、皮肤色彩/亮度、纹理各阶段分别量化，不用无RAW的IMG_2810认定scene-referred。Photos重新编辑等价性需真实图库和UI固定设置；保留原图、每次导出像素/元数据、编辑参数，按同域对照。runner已有Metal，不把普通native编译/接口失败标成无GPU或待实机。
