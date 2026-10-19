<!-- SEMANTIC-20261018 -->

## 人物/皮肤语义：runner 与实机测试边界（2026-10-19）

旧 bit-exact 方向按用户要求停止；不是待重启清单。本阶段尚未完成，既不放宽阈值，也不把缺 RAW 当作所有失败的原因。

### 可交给 macOS runner：皮肤条件逆、失败归因与区间

已完成基线不重做：S5原生 tone0/±.35 参数隔离、S6预览副本重算、S7残差法、S8三种子native求解、S9保存数组审计。S8 run39156000731 的输入/上下文与S5逐字节一致，联合候选仍296个像素>1e-3；归档后以mask逐点区分solver未收敛、已观察到half非唯一、低有限差分Jacobian秩，不能一概称不可逆。完整F往返仍未通过，不能只取成功皮肤像素作新验收mask。

后续代码入口：research/semantic-styles/{semantic_s8.inc,analyze_semantic_s8.py,semantic_s9_analysis.py,semantic_skin_model.py}。输入为S5/S8不可变捕获副本，固定所有纹理、c/d、GTC、guide、ROI、统计；只中和SSRFG.field9/10的592/596偏移（仅26A434）。原输入只供原生oracle/诊断，禁止用作逆解种子。若继续做区间，应固定原声明域，明确输出量化可行集合的上下界；多个根的跨度只是歧义下界，搜索box不是camera先验。不能重启half lattice追逐来掩盖信息丢失。

捕获：F实际、F参数中和、最终残差估计、每点失败/近黑/低秩/歧义/搜索边界mask、预览前后SHA。判据：原有最大相对误差1e-3、原有效mask覆盖率不改；同时报全有效和目标皮肤足迹指标、边缘误差、非目标区域max0。不得由PSNR高单独宣布通过。连续单位模型的自洽性不是原生精度证明。

### 可交给 macOS runner：SkinSmooth 与 Mattify 非零条件单位测试

S4 persons0使三效果走身份路径；已证这一点，不再重复。S7已跑通UnderEye FinalMix（CoreGraphics补链），受控mix.5原生往返9.5877e-4；该连续forward max3.9244e-4仍未达float1e-5，真实相机效果未认证。

最终单位已由S11/S13补上非零条件结果；下述方案保留供扩展完整链。使用原metallib，SkinSmooth须显式分配imageblock，Mattify在本runner须UseImageBlocks=true；不能照搬UnderEye的false模式，按AIR0150/0151与0067元数据绑定全部参数、ROI、纹理和stats缓冲。先建人工但完整、有限的person stats/blur/mask上下文，使用同一IMG_2810原始512主图/mattes，明确标注人工上下文。每次只改SkinSmooth强度或Mattify editingStrength，保留另一效果、GTM/LTM及mattes；不能用清空person跳过效果作为去皮肤结果。

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

<!-- SEMANTIC-TEXTURE-S10-S13 -->

S11 SkinSmooth / S13 Mattify各两个非零配置的原生往返通过1e-3，覆盖94.68282%；原输入误差仍有40/203与186/343个像素>1e-3。完整原拍摄Studio仍缺上游逐人stats与中间图，保持待实机计划；不再把已跑通的最终单位列为未执行。剩余runner方向是皮肤可行集合/区间与完整链的人工上下文诊断，不重启旧bit-exact。


<!-- SEMANTIC-S14-S18-20261019 -->

### S18 后的紧区间与幅度计划（覆盖前文历史“下一步”）

**可交给macOS runner：完整consumer可行集外包络认证。** S15/S16已完成声明的局部half码集合与原PSO查询；S17证明剩余33个联合失败全部有同观测/异F0见证。无需重复已有±8/±24集合，不重启旧NumPy/MSL精度拟合。输入为S5固定纹理/参数、S15/S16加密记录与S17逐点分类的只读副本。入口audit_semantic_s17.py、audit_semantic_s18.py、原AIR0010和native PSO。先按完整有限half域与非有限路径定义问题；以保守区间、可证明分支排除或完整离散覆盖给出 `F(x)=Y` 的每通道F0上/下界，保存覆盖证书和未决盒。fast数学/采样语义无可认证界时明确标未决，不以稠密采样或局部最小值替代。RGBA16Float有限输出[-65504,65504]只是粗外包络，Inf/NaN可达性未知。非唯一性不阻止求集合上界，但阻止保证唯一点恢复；不删原mask的失败点、不把solverbox当camera先验。判定：所有声明域已覆盖/安全排除、原oracle落在界内、区间宽和非有限未决逐点报告；原1e-3点门槛独立保留false，不能因改成交付区间而写true。

**待实机解决：j从内部权重到最终EV。** 需要与IMG_2810匹配机型/build的可调用相机诊断环境。先对新固件核对UUID/SHA、符号/指令，以下地址只指24A446参考：driver+0xa910/+0xa92c的N/j写入、LTCGridCalcAlgo0x256baa9dc、generateSpatialLTC0x256ba3808、allocateTone0x256ba15b8及0x256ba19e8..1a94。同一冻结帧副本上抓N/HITHStat及尺寸、faceRect/ROI权重、input+7210→运行时0x27994b2d0的T、混合前B/后V、allocateTone全部约束向量/分配budget/tuning和分支、输入输出曲线；不要读取zerofill0当T。分别只改j实际值→1/WithoutFaceBoost，捕获global/local曲线、c/d/GTC、实际ISP应用前后RGB及color domain/clip/plateau。原分支先重建基准，half逐位/float原门槛后，逐像素在可逆mask给 `log2(Y_with/Y_without)`、RGB/luma与face/body/背景EV区间，记录未知/clip而非强行正值。判定支持哪个file matte必须实测对齐ROI/权重，不能由名称认定faceSkin。CPU ARM短块90例只验证工作向量，不代替本项。

**待实机解决：原Studio与RAW。** 原逐人stats/眼部editedTex/instance/blur等没有由S11/S13人工上下文恢复；继续按上文完整单项中和方案捕获，完整链与最终单位验收分开。RAW仍需Mac IMG_2679/IMG_2408配对组；GTM、LTM、皮肤、人脸、人身和纹理独立输出同一固定ACES预览，不能用无RAW本张认定scene精度。Metal在runner可用，不增加无GPU借口。
