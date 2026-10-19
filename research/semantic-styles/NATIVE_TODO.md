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


<!-- SEMANTIC-S19-S20-20261019 -->

### S20 后的证据闭环与仍缺条件

已完成，不重复：完整原捕获512×384的F(A)=F(B)=原Y逐位0差，F0不同，6/29/35共70个operator-pixel精确有理数证书；非零tone只改consumer j仍0差；给定曲线的区间逆经23148个原ARM插值观测0漏包。原33个联合失败不能再仅记成“需要更强点求解器”。不能把不能保证与碰巧匹配本张原输入混为一谈。

**可交给macOS runner，尚未完成：全consumer集合紧外包络。** 不重复±8/±24或再拟合半精度参数。先声明并证明输入域合法性（解码/原key1/CI转换及有限中间态），保存相应证书。S19用原shader在人工srl0上下文证实有限输入可能非有限输出，但没有证明这些异常是本张正值Y的可行根。不能将其直接变成全图irreversible mask。若按完整half域作level-set认证，须包含原后端/fast函数/纹理数学的保守语义与非有限路径，分支排除要有覆盖证书；未决盒保留unknown。区间过宽应如实给出，不报告tight。现有[-65504,65504]只在F0有限条件下成立，非有限候选未排除时不给有限误差保证。这个认证工作仍可在runner研究，不伪装成只有实机能做，也不让它改写已证非唯一下界或原验收mask。

**待实机解决：把j接到真实像素EV。** 输入须为匹配iPhone18Pro/iOS27.0.1的同一冻结帧。先按UUID/SHA重定址，不照抄24A446地址。抓完整compute input/meta/tuning、N、ROI/faceRect/hist、B/T/V、allocateTone全部约束/显示budget、分支bool、knots、with-j输出曲线及像素应用前后RGB。仅在副本将j实际值改1或启用WithoutFaceBoost；原路径先精确重建，GTM/local/semantic各算子独立对照，记录j是否间接改变global曲线。24A446参考：0x256ba11e4 allocateTone；0x256ba13fc..1400读取tuning+0xc到w28；0x256ba1ffc判断插值/copy；0x256ba2030..2104仅插值分支末端clamp。实际C_with/C_without与应用坐标取得后，才调用semantic_curve_inverse.inverse_curve_pair，逐段验证native pixel forward和区间覆盖、plateau/近黑/clamp/越界；标量曲线不代替CCM/key1/空间混合。没有完整曲线就维持预算假设，不用S19节点EV范围充当样张像素界。

**待实机解决：原Studio/RAW/UI。** 保留前述原逐人stats/instance/眼部editedTex/blur/tuning的逐项中和方案，不能用合成stats替代原相机。UnderEye/SkinSmooth/Mattify最终单位的已知上下文往返与完整原拍摄去处理分开。RAW仍需Mac IMG_2679/IMG_2408的HEIC+配对RAW；只允许预约定全局曝光对齐，GTM/LTM/人物皮肤分开报EV、覆盖与边缘，203nit不标定。Photos UI仍需实际图库对照。


<!-- SEMANTIC-S21-20261019 -->

### S21 后：全域认证条件与同帧相机提亮捕获

**可交给runner；与实机数据缺口分开。** C01–C05及其当前false见consumer-contract-audit-s21.json。输入使用已加密的S5/S17/S20副本、同26A434 metallib/PSO/function constants/ROI与逐字节相同的固定上下文。优先取得原pipeline对应的lowered程序文本/执行语义；若用MTLBinaryArchive辅助，只在runner暂存，上传反汇编文本与SHA/标识，整份Apple二进制仍须另行获准。必须证明所导出的程序就是原retained PSO，独立编译helper、改safe/关FTZ或替换oracle不够。对半精度pow、重写、取倒数/FMA、RN/RTZ/FTZ、纹理格式/有限坐标和footprint逐项建立包络。原生有限域全覆盖也可作替代路径；不把已有百万级局部查询当全域证书。判定：保留原mask和1e-3，全部声明域覆盖且未决盒0、每个排除有证据，才签发紧上界；宽区间如实交付。S20非唯一下界不因补上上界而消失。

**待实机：j → 曲线 → 像素EV，执行协议。**

1. 使用能观测CameraColorProcessing的匹配iPhone18Pro/iOS27.0.1测试宿主；先记录实际OS build、UUID、text基址/SHA并重定址LTMDriverV2::Process、LTCGridCalcAlgo、allocateTone及-[LTMCurvesComputeV2 compute]，不直接使用24A446地址。捕获同一冻结RAW/ISP输入帧及原mattes、AE/曝光和所有compute输入；记录真实分配长度，不能按合成实验的128点/任意结构大小猜。
2. 原路径A完整捕获driver j（参考24A446 driver+0x24→computeInput+0xa92c）、N、ROI/faceRect/HITHStat、原face/global histogram、B/T/V/count、完整tuning、allocateTone约束/分支/budget/knots、global/local输出曲线和c/d/GTC。参考24A446可写common T在0x27994b2d0，来自当帧input+0x7210；匹配版本须重新核对。记录allocateTone入口参数寄存器/栈和调用者给定数组长度，按这些真实长度抓缓冲。
3. 用同一份冻结输入的副本运行B：只将实际j设1，其余compute输入字节/数组内容保持。每次恢复所有可写common/cache（含T），先做A→A重复验证输入/输出SHA不变，再做A→B→A。运行C：原WithoutFaceBoost路径；比较其输入和B，若除j还有变化，分别报告，不能把C自动等同B。上游统计重新计算仍须来自同一冻结帧。
4. 捕获三路生产曲线以及实际ISP应用前后RGB/纹理、色彩空间/transfer、GTM/LTM/semantic顺序和全部clamp。c/d/GTC是生产输出时允许随j重算，逐项记录变化；这不改变consumer参数隔离实验冻结c/d/GTC/guides/统计/mattes的规则。若global和local都受影响，固定其他语义项，交叉组合两套global/local上下文作四个对照，单列各自作用与非交换交互，不把两项混成一步。
5. 实际C_with/C_without与曲线坐标已确认后，按native实现误差合同调用semantic_curve_inverse；RGB/矩阵/key1/空间混合另按真实顺序重放。只有经同一native颜色变换得到的线性P3像素才用于EV：正值luma上log2(Y_with/Y_without)，零/plateau/clamp给区间和unknown。原节点比值不能直接称像素EV。判定按原half/float前向门槛及可逆mask往返maxrelative≤1e-3，报告mask覆盖，不以拟合曝光或缩mask过关。
6. 人脸/人身分别评估真实native增益的背景变化、EV梯度/光晕/振铃、色度、断层及往返；原文件faceSkin/person与生产faceROI权重的绑定必须从原调用抓取确认。预览统一现有固定ACES1.0 SDR Video、0EV，显示操作只处理副本并检查输入前后SHA。没有实际曲线时保留预算假设，不标Apple精度。Studio原始people/eye/blur/instance/tuning与RAW IMG_2679/IMG_2408继续沿前述独立测试计划；RAW不做203nit标定。


<!-- GPT-S22-DEVICE-PLAN -->

### S22之后：runner 数值合同与必须实机的提亮验证

**runner 项（不需要人像）**：`research/semantic-styles/semantic_numeric_s22.m` 与 `validate.py` 已在 macOS `26A434` 的 [run 39215654333](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39215654333) 成功执行。它们证明原 Apple PSO 可建立，并验证独立 synthetic kernel 的 half pow、safe/relaxed/fast 差别和 sampler 基础行为。尚缺的 runner 任务依次是：

1. **C01 半精度 pow 真实边界**：从原 `renderFinalAdjustments` 特化的实编译后端取得可审核的 `pow/powr` 实际实现、或在保持原 PSO 和捕获配置时逐一证明调用不可达。仅对另编译 kernel 扫描多个参数不足以转移成原 PSO 的误差合同。
2. **C02–C04 全域可定义性与纹理依赖**：逐语句处理 RN/RTZ、FTZ、FMA、重结合、reciprocal；同时认证原 `F`、`F0` 对所有合法前像不会进入无定义操作。冻结原 512×384 capture 的 function constants、stats、c/d/GTC、ROI、mattes 和 sampler，显示主图邻域 footprint；若无法排除，必须将邻域 RGB 作为额外变量。不得将 S22 自编译模式当原 PSO 的可改写证明。
3. **C05 全部输入域证书**：保持 S21 的全有限 halfRGB 域及已证明必要的变量纹理域，用带可靠向外取整的区间/枚举或等效方法。保存每个目标像素 `[min,max]`、非有限可能性、未证盒数、条件与可复算证书；任何未决盒都令“tight hull certified”门槛红色。结果必须包含联合皮肤余下 33 点，不能靠旧70个已知多解见证确定上界。

**实机项（无相机真实采集数据不能替代）**：为拍摄端脸部和身体提亮单独建立下面的可执行配对方案，推荐选同机型、同系统 build 的静止场景；人物、光线、焦距、WB、曝光、画面取景保持一致，关闭会导致场景漂移的自动变量，记录 capture/session/ISP 元数据但不要上传原件。

1. 固定 RAW/JPEG/HEIC 可追溯的同一帧源，采集 **A=默认实际 j**、**B=固定其它输入后只将 j 置 1**、**C=WithoutFaceBoost 重新走完整 producer** 三条路径；确保 A/B 比较仅改变 j，A/C 显式记录 producer 重算了哪些 stats/曲线/coefficients。无法固定源时，用同一帧的私有重放和确定性输入代替两次手持拍摄。
2. 每条路径在 producer 端保存 **N、B/T、工作向量 V、预算与约束、face/body matte、直方图、派生 `c/d/GTC`、曲线 knots/外插规则、色彩管理参数**，并记录恢复已修改 common T 的重放证据。至少导出应用前和应用后**线性 P3-D65 RGB**、A/B/C 的局部与全图差图；不要仅保存一张最后效果图。
3. 各 ROI 同时给出脸部、身体、背景、边缘带的 `median/p05/p95/max |ΔEV|`，计算 `EV=log2(Y_after/Y_before)` 仅在两者正且高于明确噪声地板时有效；同时报告线性 RGB 通道比、色度漂移和 mask 边缘 halo/梯度，分别估算 face 与 body 的真实幅度。读取姿态、RGB 曝光、光源变化；单独用等灰中性基准排除自动曝光导致的伪差异。
4. **Studio**：在相同原始帧/输出条件下固定逐人 personIDs、眼下 region、语义 mask、skin smooth/mattify/under-eye 参数，分别测关闭/开启单效果及组合结果；至少取零效果和多组非零 strength 对照，记录每个核的 inputs、输出、thread/imageblock 配置。消失的私有 matte 不得填零后冒称原相机条件。
5. **RAW/full-res**：获取同帧 ProRAW/DNG（如设备允许）和 HEIC 的配对、LinearThumbnail/传递曲线依据，覆盖 512×384 以外的原分辨率和边缘 crop/orientation，分别测 GTM 与 LTM，再单独测人物语义与纹理；最终 Photos UI 的可编辑性作独立验收，不得由 macOS ImageIO decode 推断。

**隐私与归档**：所有原件、RGB、RAW、人物/人身 matte、同帧完整元数据都视为私有。仅在额外明确授权并具备临时 secret 的方案时通过 GPG 加密传递到 runner；公开分支、issue、PR、Actions 日志和 artifact 只允许严格去标识的摘要/密文，`retention-days:1`。该轮结束立即撤销临时 secret、release、tag 和临时私有分支并记录 API 404 复核；本次 S22 未创建上述临时资源。
