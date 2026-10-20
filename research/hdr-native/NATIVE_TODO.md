### HDR-NATIVE-20261019：独立 HDR 与 scene 验收分开

**可交给macOS runner（HDR-R1）：** 在S32已定位的原生gain读回域基础上，固定编码矩阵/范围/坐标/位深与tmap元数据。分别用原生primary/raw、ISO aux和CPU decoder捕获同一单通道斜坡/RGB常量/负EV/0黑位，先过每算子maxabs1e-5且PSNR60的原float门槛，再验证编码后目标maxrelative1e-3。不从RGBAh推断位深，不把12bit nil标为普遍不支持。10bit若范围量化仍越界，应报告或寻找经原生验证的有效精度方案，不降低门槛或删点。接着冻结配方，用真实5图（2张冻结后留出）、4032×3024/5712×4284以及低/中/高headroom；保留原SDR coded descendants/property并运行冻结full_sdr_compare.m，max0才过。边缘/色彩/近黑/clamp/codec与thumbnail误差分开。

**可交给macOS runner（HDR-R2 / A仍未完成）：** 已知输入A的原PSO目标反事实可用operator_recipe独立控制consumer local/skin；真实最终Y须完整集合逆F^-1，保留33点原mask与C01–C05全域tight hull缺口。新输出来的RGB比值自洽不解决这些条件。实际生产曲线可调用的代码能先在ARM诊断宿主做条件重放，但没有同帧实际曲线不得标Apple恢复。旧bit-exact方向已按用户收尾，不重新做参数拟合。

**待实机（HDR-DISPLAY）：** 用同一最终载体和同一原SDR，在能记录EDR/HDR headroom、白位/峰值、环境照度的真实屏幕上测试1、1.25、1.5、2、3、4及内容满档。捕获系统实际线性输出或可审计屏幕测量，比较预设H与mid-headroom目标、skin/人物背景EV、色度/边缘/光晕、HDR↔SDR切换。区分OS显示适配与内容图像本身；固定ACES SDR截图不算通过，不做203nit场景标定。

**待实机（D-PAIR-CURVE/D-STUDIO/D-RAW）：** 沿用前述匹配build、冻结同帧A→A与A→B→A方案：原j/仅j=1/WithoutFaceBoost只改单一目标，捕获N、B/T/V、face hist/ROI、allocateTone约束及配对global/local曲线、c/d/GTC重算、实际应用前后RGB/域/clip/plateau。原分支先重建；global/local交叉四对照保留非交换交互。j的β只作内部权重界，未得曲线不能计算实际EV。Studio须原统计，RAW须IMG_2679/IMG_2408配对；这些缺口不由Gain Map承载成功替代。

**可交给macOS runner（HDR-CODEC-12）：** S32的12bit CGImage/CIImage对象均存在而primary render代码错误、ISO aux nil。对这两个确切文件抓ImageIO的bits/layout/provider数据、CGContext16bit CPU转换、CI软件/Metal两种context及aux CVPixelBuffer plane/attachments，先用已知整数code验证，再判定是12bit profile/像素格式、CPU decode还是GPU上传路径。不能笼统归为无Metal或不能开文件；如runner数值路径能解决就继续runner，只有真实设备差异比较列待实机。8/10bit matrix1/6的primary与aux记录的最大误差相同（不能据此断言逐点一致），编码RGB↔YCbCr和native读回误差与理想均匀量化分开记录。


### S33–S35后续（旧门槛和待实机清单保持）

**可交给macOS runner / R-RGB-HOST**：S36使用S34同一fixture副本、原prepareToProcess:2、原_processLTMGainMap。必须捕获两次encodeToCommandBuffer、r1/eps.001、全主图RGBAguide、七dispatch；读回small/full半浮点并逐点对照。不接受返回0但无guided参与。S34/S35历史失败归档保留。冻结NumPy只作为已知误差重放，不重启bit-exact拟合。

**可交给macOS runner / R-RGB-FULL**：原host合格后冻结新RGB比值/guide/eps.001配方，用五张原分辨率照片（至少两张该新配方冻结后才验证，注明它们曾参与旧研究），与旧bilinear/area、既有scalar/log-guide候选分开。记录map形状/PSO/actualeps、GTC/nearblack/clamp/nonfinite masks、边缘/锚点EV、参数以外SHA。所有照片输出仅密文；独立global/local/semantic输出，不把620/624=1的consumer identity叫去拍摄local。scene母版候选和HDR渲染分开，不以比值自洽认证物理恢复。

**可交给macOS runner / R-CODEC-PROVIDER**：仅现有12bit文件的provider为nil已确认。下一步需原生可读的更高精度编码/profile或其他合法RGB gain-item codec；固定目标/码值对照并核对provider/原SDRmax0/全图及中间headroom。10bit当前3.5EV码程未过1e-3和PSNR60，不能靠缩码程、改mask或误差门槛宣布原目标通过。实际不支持的型号/codec不能从Paravirt两个文件外推。

S36更新：R-RGB-HOST的三组合成原host参与和读回已验证（run39246456413）；实际RGB eps.001。R-RGB-FULL及物理inverse原门槛保留，尚未完成。


### S40–S41资源边界更新

R-RGB-FULL仍可交给macOS runner：已用原API2GiB type2池排除受控大图的默认144MiB池容量前置条件（S40/S41），小图输出SHA一致。下一轮S42不改变图像公式，必须保留所有非零退出的native.json/checkpoint，检查真实全尺寸两guided、eps.001、source/params SHA、EXR存储重读及Gain Map传输分开门槛。此条件不是Metal不可用，不归入待实机。

真实Photos调用者所供资源预算可在runner原PISemanticStyleFilter调用时hook initWithMetalContext:/FigMetalAllocatorDescriptor.setMemSize:/setWireMemory:捕获，保持原方法返回，记录PSO和资源描述；用同输入小图/大图读回对照，不从属性名推断配置。相机曲线/Studio/RAW与真实HDR观看清单保持原样。


### S42 后续（分类分开）
- 可交给macOS runner：逐区定位原create-kernel 1/255阈值、采样、half和锚点误差；与原2048双线性+2x2面积约束比较同画布边缘/锚点，保留原参数不凭感觉调eps。S42不含该旧基线对照。
- 可交给macOS runner：独立冻结显示曝光策略与中间headroom效果，重用已存母版，禁止暗中改场景候选/旧mask；编码候选须再验全尺寸原SDR ImageIO max0及RGB目标1e-3/PSNR60。S43先以固定合成目标隔离AV1原生码值。
- 待实机解决：真实拍摄global/local曲线/应用域与33点合同、j像素EV原始统计、Studio原统计、RAW2679/2408和实际HDR屏幕，沿用既有可执行方案；S42的自洽性不补造这些证据。


### S47 后的分类与可执行下一步

- 可交给macOS runner：复用S42母版（勿重跑已验证guiding）完成冻结显示配方五图/两张该配方输出留出；现S47只有IMG2600开发图。先按下载/配额规则处理约1.25GB原密文批次及归档期限。每张捕获固定ACES预览、完整headroom、源SHA、近零/负值mask与端点误差。高PSNR不代替1e-3；原SDR完整ImageIO编码max0另验。
- 可交给macOS runner：S47公共offset失败，捕获最坏分量坐标及S/H/o/logmap/原生输出，分别统计logmap存储、exp2/offset消减、原生运算误差；按同一全图目标/原门槛审查表示方式，不删除近零像素求通过。可先用合成近零/跨零输入定位，不重复真实照片完整ISP源准备。
- 可交给macOS runner：旧2048双线性+2x2面积约束对照、原create-kernel近黑阈值/可选main-thumbnail/sampler域与新RGB投影误差；两类guided eps.001/.05保持各自实际上下文，不凭感觉调平滑。只对新问题补实验，旧30scalar oracles不重做。
- 分类勘误：33皮肤点的完整consumer声明域合同与全域tight hull仍是“可交给macOS runner/静态继续研究”的未闭环项，不能整体归入只能实机。S42尾部曾把它与相机域混写，此处明确分开。停止旧NumPy bit-exact拟合，保留C01-C05、原mask、非唯一证书与1e-3。
- 待实机解决：匹配同帧j/WithoutFaceBoost曲线、N、B/T、人脸hist、allocateTone constraints及真实应用域；原Studio统计；RAW2679/2408；真实HDR屏幕/环境/PhotosUI。沿用各自既有可执行测试，beta.1953125仍不是像素EV，S47显示曝光不得替代该缺失值。


### S49 后：分清插值、面积与真实逆LTM

- 已验证数值：旧2048面积约束/原生RGB结果已做同画布、同GPU half锚点配对；见HDR-41/42，不再重复该基线。更清晰不能替代scene恢复，锚点漂移尚大。
- 可交给macOS runner：对已存母版/低分辨率锚点分区统计中心采样与面积残差、近黑阈值/half/guide边界；若需重放原create-kernel，固定原参数与非目标纹理，只为新归因捕获，不重做旧30scalar oracle或11种否定组合。S49未证明无光晕/振铃，未取得新RAW。
- 可交给macOS runner：公共offset近零目标的float32 logmap/归一化编码是否非单射，用同一原生输入、不同目标的有限碰撞证书区分信息丢失和算术误差；不移除近零像素、不改1e-3。
- 待实机解决：同帧j/WithoutFaceBoost/N/B/T/hist/allocateTone/application domain、原Studio统计、RAW2679/2408和实际HDR屏幕按既有方案；本轮无新实机证据。33皮肤点C01-C05仍属静态/runner可推进的未认证边界，停止旧bit-exact拟合，原mask/阈值保留。


### S50 后：近零 Gain Map 表示边界

- 已验证数值：有限float32 logmap/normalized-code碰撞及原生五档同输入同输出已经归档，禁止把高PSNR替代1e-3。该近零域的统一保证不能靠更精确执行已丢失信息的相同code解决；不是原始33皮肤点tight hull。
- 可交给macOS runner：S47真实最坏坐标、S/H/o/logmap/归一化值/原生输出仍需分项捕获；S50合成o=.03125不替代实际o=.0307447053492归因。零offset在域内通过不赋予符号不匹配/零分母像素可逆性，不缩mask。
- 可交给macOS runner：已准备S51四张既存母版的冻结S44/S47显示配方，合计922251766B仅runner下载；新预览contact加密，VM100MB累计限额不重置。需先等仓库其他研究分支排队run结束，再设置本批四个一次性session secrets与push触发。原始SDR编码max0、新HDR codec目标、实际屏幕和RAW门槛均独立保留。


### S51 后：已完成项与仍可推进项

- 已验证数值：冻结独立显示公式的五图/2配方留出、50个原生未编码对照已完成；不要重复此整批或旧key1/guided。zero域内和公共offset全图结果见HDR-45/46，失败点/旧mask不删。
- 可交给macOS runner：在纯合成输入上单独检验BaseOffset与AlternateOffset不同的原生行为，捕获h1身份和h1.25/2/4/8端点，固定HDR目标。它是新的表示合同问题；若h1不成立，不把降低AlternateOffset当完整方案，不进行无目的精度拟合或重跑五图。实际3图最坏点归因仍需坐标/字段捕获，S50有限碰撞不替代它。
- 可交给macOS runner/静态：native投影保边但锚点漂移，原local生产与consumer、global与semantic的真实逆解不可混同；33点完整声明域C01-C05/紧区间仍未认证。停止旧NumPy bit-exact拟合。
- 待实机解决：同帧j/WithoutFaceBoost/N/B/T/hist/allocateTone/application-domain、Studio生产统计、配对RAW2679/2408、真实HDR显示/环境与PhotosUI，沿用既有可执行计划。本轮没有这些真值。
- 存储边界：原S42完整母版/sidecar密文仍受原artifact一天期限与当前100MB累计许可限制，未宣称整批已在VM落地；不把新日期或自动续轮当配额重置。


### S52 后：offset 合同已检查，不再重复同组对照

- 已验证数值：独立B/A的4组合成×5headroom合同，固定offset模型匹配，h8通过/h1身份失败；不把这一末端改进推广成完整承载方案，不因此重跑五图或降低门槛。
- 可交给macOS runner/静态：继续原生产/消费端global、local、semantic分别的可识别域与区间；native保边投影锚点残差、33点C01-C05完整合同仍未认证。真实HDR编码/完整ImageIO SDR max0与所有原算子门槛未通过，不以新显示公式通过替代。
- 本地交付约束：用户100MB累计上限仍有效。已提125MB小方案，只流式取一份27.79MB原EXR；未答复不得写，完整母版不宣称已在VM落地。`stream_verified_master.py`通过原ZIP/cipher/GPG/member SHA核验，只复制字节；本机Python仍须内存scope。
- 待实机：同帧j/WithoutFaceBoost/N/B/T/hist/allocateTone/application域、Studio原统计、RAW2679/2408、真实HDR屏幕与PhotosUI；沿用既有执行清单。A阶段尚未完成。


### S53–S54：配对生产曲线的可执行捕获方案（待实机）

机器清单：`research/hdr-native/evidence/s54/producer-paired-capture-plan.json`。新节点前像decoder仅适用于参考writer的516B global记录，未读取真正iOS输出；不把它当成完整相机逆。

1. 在匹配IMG_2810的设备/系统上，保存`sw_vers`或iOS实际系统build、硬件型号、loaded Mach-O UUID及binary/source SHA。LLDB先用`image list -u -f CameraColorProcessing`和`image lookup -n '+[LTMMetadataWriterV2 _addLTMCurvesToMetadata:curvesType:fromOutput:statistics:geometryData:isSIFR:ltcNumNodes:]'`定位；若UUID/布局不同，先重拆，禁止照抄24A446绝对地址。参考UUID/地址仅用于对齐。
2. 同一RAW/合成输入和同一HITH统计固定后做A→A。writer真入口读取`register read x2 x3 x4 x5 x6 x7 sp fpcr fpsr`：type=w3、output=x4，分别保存output+0x18504与+0x18908的1028B原float节点。例：在**已验证参考布局的真入口**用`memory read --binary --outfile <private>/global-tone.f32 -s 1 -c 1028 '$x4+0x18908'`。函数序言后sp不再是第九参数位置，不凭当前sp猜ltcNumNodes。
3. 按symbol load address与函数内偏移设置三处before-call断点（参考0x256b8ce34/ce4c/ce64）。此时`x2`是字节指针、`x3`是长度；global两处必须516B，保存全部258个u16，不只存256half纹理。记录type0..3、字典/线程/帧标识、CV transfer/primaries、实际GTC generic键的SHA与word256、word257。CMI复制纹理前（参考0x1d476c6dc）另捕获x4的512B。断点只读，不改变原方法/返回。
4. 做B-only-j：仅在已验证的j字段设1，输入其他字节/统计/ROI/全部matte不变；再单独执行C-WithoutFaceBoost，保存完整driver byte diff。参考C还写+0x554/+0x558，不等于B。每次恢复可写common T，保存N、B/T/V、face hist/ROI、allocateTone上下界/预算/knots、所有实际global/local曲线、baseGain/曝光的更新过程和应用前后RGB。
5. 原分支先按原half/float/1e-3门槛重建。在已证明的实际像素应用层分别替换global、local两组操作，得到G_A/L_A、G_B/L_A、G_A/L_B、G_B/L_B，报告每步EV区间、coverage、plateau/近黑/clamp/nonfinite、边缘/色偏/断层、参数外SHA及A→B→A往返。不能依据字段名把GlobalLTM直接归成global；key3与c/d的序列化来源须逐边绑定。预览仍同一固定ACES，预览前后输入SHA相同。
6. 全部原始像素/可重建数据只在私有临时目录，GPG加密后才上传；临时secret/release/分支用后清理。没有无风格真值的base+gain-only样张继续只报条件反事实和幅度敏感性，不把预算当Apple EV。

VM/runner仍能推进：metadata序列化/调用者换绑、c/d生成连接、原PSO的C01-C05全域合同、可读高精度HDR载体与原SDR ImageIO max0。只能实机：匹配机型同帧生产曲线与统计/应用域、Studio原统计、2679/2408 RAW、真实HDR headroom观看。S54的CPU量化界不替代这些项；33点紧外包络仍未认证，原mask与门槛不改。


### S55–S59 后的分离测试清单（未通过门槛不变）

**可交给 macOS runner：** 用同一份加密原图/Apple Log LinearThumbnail，至少5张且2张在完整配方冻结后才参与验证，调用真正计算 global/local stats 的原 host 分支。捕获是否沿用输入 c/d、prepare/config flags、transfer/CCM/VE/SRL、ROI/grid、stats 全部10640B、params672B、GTC及scalar17/18前后纹理；记录原PSO/UUID/dispatch/sampler和每输入SHA。先不改变任何上下文，核对实测M_A/M_T与S58候选、输出与文件c/d的逐码关系；不能以候选回填零stats冒充捕获。再分别仅改global或local参数，GTC、guides、c/d、stats、其他matte保持各自指定的固定外部上下文。half仍逐位、float仍maxabs1e-5及图像PSNR60、逆仍可逆mask内1e-3；S59只验证编码桶，不替代这些。继续静态追实际写文件字段的绑定/格式和33皮肤点C01–C05；前述任务均未转成“等Mac文件”。

**待实机解决：** 在IMG_2810匹配OS build/UUID上按evidence/s54/producer-paired-capture-plan.json重定址，而非搬用24A446绝对地址。同帧冻结输入/N、B/T/V、人脸直方图、allocateTone约束/knots、应用域，分别抓only-j、原WithoutFaceBoost（还改driver554/558）和四组global/local表的原float与packed记录；重放G_A/L_A、G_B/L_A、G_A/L_B、G_B/L_B，判定像素EV、交互、clamp/plateau区间及原误差门槛。β=.1953125不换算假像素EV。RAW2679/2408、Studio原统计与实际HDR屏幕/中间headroom另按原计划；相对母版与显示渲染继续独立验收。

本阶段没有新图像预览或RAW误差；此前固定ACES显示预览不变。独立HDR渲染/封装/SDR max0门槛不因代码本成功而通过。A与acceptance_complete仍false。


### S60–S64 后（global / local / semantic 分开，未认证）

- 已验证数值：五图原stats host/45 dispatch已捕获，默认分支不更新gain；c/d的9279/10240 half码不匹配。S64颜色/D4检查不解释差异。不要重复整批stats或把默认style重算当文件生产结果。
- 可交给macOS runner/静态：追NeutrinoCore/PhotoImaging到CMI生成分支实际输入、style/processing type、ROI与c/d文件写入者；原文件只读。先捕获同一输入的默认A→A，再在绑定明确的调用者只改目标global或local字段，其他GTC/guides/stats/mattes与SHA冻结；比对原half/float1e-5+PSNR60与可逆mask内1e-3，记录plateau/clamp/near-black区间，不把候选M回填作实测。33皮肤点C01–C05、原生完整往返、封装后ImageIO SDR max0仍可runner推进，不能归为等实机。
- 待实机：匹配IMG_2810 build/UUID、同帧j-only/WithoutFaceBoost四组曲线及N/B/T/V/face histogram/allocateTone约束与应用域，按evidence/s54/producer-paired-capture-plan.json第1–6步执行；冻结其他字节、抓原float/packed记录/实际像素四组合，报告EV区间和交互。原Studio统计、RAW2679/2408、实际HDR显示与中间headroom方案沿用，β仍不换算假EV。


S69之后（runner）：在原UUID/PSO下使用1024×768恒灰main/linear、32×24阶跃目标matte，固定GTC/params/其他matte及输出，分别测试zero crop/显式full-matte crop。以原_encodeRenderRegionForStats的176B、输入SHA、sampler与per-tile person/skin计数为oracle，先从AIR推导UV，再判定配准；不得按观感调smooth或据字段名选择比例。原调用者的实际stats源/ROI/尺寸和封装后SDR max0、33点全域合同仍可runner推进。CPU ROI检查0不是图像前向通过；S63大图全局统计不认证为相机上下文。实机j/WithoutFaceBoost四曲线和N/B/T/V/face hist/allocateTone/app域、RAW2679/2408/原Studio/HDR观看按原清单，β不换算假EV。

- S71已完成有限阶跃matte原CPU ROI+原PSO计数验证：7组/14336格max0，见evidence/s70-s71；C04全声明域仍未证明。下一步原PhotoImaging调用点/参数常量/ABI取证，固定实际logical/render/crop和context后再验证真实consumer，不把默认wrapper比例强加于已有冻结输入。33点、完整往返、编码后ImageIO SDR max0仍可runner推进；相机同帧j四曲线/N/B/T/V/face hist/allocateTone/应用域、原Studio统计、RAW与屏幕仍按实机方案。

- S72（evidence/s72）：原PI消费者26 selector/15常量/4 ABI已绑定；下一步可runner用显式extents和full/tile输出调用原ROI(IMP0x1cbef066c)，捕获mapped region/实际texture尺寸和scale，并保留非目标上下文SHA。不能把S71默认wrapper比例当真实consumer。33点全域/完整往返/编码SDRmax0继续未证；同帧相机j曲线/统计、RAW、原Studio统计与实屏沿用原实机方案。

- S73之后的runner测试（HDR-87）：先核对原getter0x1d0088a70和NC UUID5E0B3F6B-554E-3373-A411-4A4D1CF0A057；读取double常量槽0x1c5cf52a8、0x1c5cf5450及其bits，不猜epsilon。按原ABI四个int64的PixelRect，从NUPixelRectFromCGRect→Scale(policy0)→ToCGRect→FlipYOrigin逐项保存输入/输出。输入含整数、±.25、小数边界及精确文件比例5712/1024=5.578125、4032/1024=3.9375、main/matte比例；只测有证正尺寸/正scale，未覆盖的非有限域继续列C04。判定：整数四分量逐位一致、有限double几何预冻结gate1e-12；这不是RGB线性1e-5/PSNR60和原1e-3像素gate的替代。随后用同一合成图、全帧/分块CI实际处理捕获getter返回CGRect、分配texture宽高、mapped region、scale和SHA；保留GTC/guides/c/d/统计/其他matte。未获实际分配证据前，S73仅请求ROI。


S74之后（HDR-91，可交给macOS runner）：原region getter、±1e-6两个double常量及有限正scale四int64几何已完成，不重复54例。下一步在同UUID原PISemanticStyleProcessor实际CI运行中，只读hook原process方法、保留返回，记录每个输入region、format、bytesPerRow、metalTexture width/height/pixelFormat以及原mapped-region/scale setter；先从原formatForInputAtIndex的0x1cbef041c/table0x1e1fcb0b8与outputFormat0x1cbef063c绑定9个format数值/常量（不猜格式），并复核outputIsOpaque/synchronizeInputs/allowPartialOutputRegion/allowCompressedInputsAndOutputs。全帧、分块、带非零原点合成输入各A→A，原global/local/semantic参数及GTC/guides/c/d/stats/其他matte分别冻结并SHA检查；保存实际分配CGRect与S74转换的逐项差，再按原像素门槛核对。请求ROI和CPU整数链不是实际纹理证书；C01-C05完整声明域、33点紧区间、完整往返及封装ImageIO SDR max0仍待runner/静态继续。只有匹配相机同帧j曲线/统计、原Studio、RAW和实屏按既有方案列待实机，β不当EV。没有修改原mask或声明域。


S80之后（HDR-97，可交给macOS runner/静态继续）：原CI合法type2合成入口已建立，不重复S75编译错误或S76 nil-stats+maps无效成功。固定S80 ordered统计、九路纹理、tone+.35及logical extents，保留原process返回和PSO；whole/tile/translated各AA。先在final dispatch保留并读回实际guides、五组guided结果、c/d、三个matte、params/stats/ROI和输出；记录所有shape/dtype/OS/UUID/PSO来源及SHA，未知padding不上传。原生完整输出对照外，仅替换单项whole的对应crop到tile，其他输入/统计/参数逐字节不变，分别测RGB maxabs、PSNR、half差分、边缘距离；最后做完整native往返，可逆mask内仍≤1e-3。判定不能只看PI返回YES，必须有实际final dispatch、有限非零源响应和正确capture。tile当前max2.44140625e-4未过float1e-5，定位前不归因于half或边界。PI上游对skin/sky/person的resize来源仍需原调用者证据；S79的全尺寸控制不当作相机合同。C01–C05与33点全域tight hull依旧未认证，不能整体转为只能实机。

实机计划不变：匹配IMG2810设备/OS，在同一合成帧/统计的j-only对照中捕获j与WithoutFaceBoost的四组global/local曲线，完整N、B/T/V、face histogram、allocateTone约束、实际应用域及clamp/plateau标记；每次只改变j，其他matte/key1/GTC/cd/曝光固定并SHA。按曲线区间传播β，输出可辨识EV区间和不可恢复mask，不把内部权重界当RGB增益。Studio需原始统计的目标参数反事实，RAW需Mac的2679/2408配对；实屏按低/中/高headroom与同一SDR基底验证，ACES预览不替代显示测试。


### S81 用户调整后的执行优先级（2026-10-20）

当前改做实用效果：先用已有真实样张/分离反事实配方在 runner 输出 global-only、local-only、semantic-only、联合 HDR 与原 SDR，统一固定 ACES/曝光，验证肤色、背景、连续性、边缘与三档 headroom，至少五图且两张冻结后留出。报告 EV median/p95/p99/max、覆盖率和不可恢复区域；不把“99%效果”转换为未经定义的准确率。完整清单在 PRACTICAL_ACCEPTANCE.zh-CN.md / evidence/s81/scope-change.json。

33 点全域 tight hull、C01–C05 完整覆盖、逐像素唯一逆解及 S80 微小 tile 残差定位列为已知未认证/暂缓研究，暂不阻塞实用交付；它们没有被证明，也没有改称只能实机。出现可见缺陷或用户重新要求时才重开。原件、冻结模型/验收脚本及历史门槛不改，原严格失败保留，不强求完整 native 往返成为实用前提。

实机清单继续执行：匹配 IMG2810 的同帧 j-only/WithoutFaceBoost 四曲线、N/B/T/V、face histogram、allocateTone 与应用域；原 Studio 统计；RAW2679/2408；实际 HDR 屏幕/观看条件。用户接受实用效果不构成这些物理量已恢复的证据。全图新载体 SDR max0、非有限值/隐私/内存检查仍为实用质量要求。


S82/S83：实用语义控制源码已实现、S83合成结构检查已通过（run39399353600）。下一步是S82真实捕获强度/区域指标与密文预览，输入为原S5/S8两份已归档密文；自动审批要求用户明确批准“公开预发布release+两条临时session secret”目的地，当前确认待答，两次被拒动作均未执行，S82无运行/secret/release/分支。不得通过别的通道绕过该拒绝；源码保持contents:read，setup脚本额外要求s82-user-transport-approval.json。若批准，先重新核对单run/远端资源、完整ZIP/GPG/manifest，再运行；终态下载校验后删本次secret/release/tag/触发分支。

该验证只是384x512真实consumer捕获，不替代全原件五图/两张留出与global/local分离预览。不得使用S15/S16按oracle误差挑点补丁冒充泛化算法。新增控制的强度不是Apple tone值；同一上下文的F/F0求差只给条件估计。半精度/33点全域证明继续按S81暂缓，实机j/RAW/Studio/实屏按既有可执行清单；全分辨率、背景/边缘/色偏和SDR max0仍可runner推进。


### SEMANTIC-20261018 / S82–S87 后续：按实用效果推进

可交给macOS runner：S82的三种皮肤控制已取得同一真实384×512捕获的15变体及目标外零变化；固定默认.5，保持c/d、GTC、guides、统计和其他matte。下一项是原尺寸语义目标、更多照片及两张新配方留出；预先记录质量标准，比较原SDR、只去global、只去local、只去语义、联合HDR五路。检查真实受影响区域方向/色偏、相对原生的梯度/Laplacian残差、皮肤/背景边界接缝及统一ACES预览，不能用整图p99=0或自选gain往返冒充Apple真值。原33点/half失败暂不作为工程阻塞，但不可逆mask/区间继续保留。

可交给macOS runner：S87五图承载及最大EV点的每case结果以phase-summary.json为准。失败case先读原run日志和native extents；若完成，继续用独立设计HDR目标替代本次RGB压力图，并对headroom1/2/8和中间值做颜色/边缘/目标及量化分离比较。完整ImageIO原整数SDR max0仍独立执行。对最大EV点的RGB/坐标使用密文witness核对signed RGB、近零Y和显示后差异；分类只解释条件数，不构成肉眼无缺陷证明。新完整载体和EXR目前未持久归档，下载/写入必须先核预算；不把SHA或过期artifact当完整交付。

待实机：IMG2810同帧CameraColorProcessing，冻结输入/统计/其他参数，分别捕获j与WithoutFaceBoost四组global/local曲线、N、B/T/V、人脸/人身直方图、allocateTone上下限及应用域的前后RGB。记录build/UUID/SHA和原始buffer dtype/shape，对照曲线变化与最终像素EV、plateau/clamp/近黑区间；β=0.1953125只约束局部权重上限，不能作为RGB或EV预算。Studio在同帧原统计下分别关眼下提亮、SkinSmooth、Mattify，保留输入/其他算子和纹理SHA，对比像素/边界/色彩；人工统计的既有条件逆不替代此测试。RAW仍需IMG2679/IMG2408配对、曝光/色彩对齐后报告EV；真实HDR屏幕/观看环境、Photos UI另按既有步骤验证。缺这些证据时维持假设/待实机分类。


2026-10-20 S88更新：真实独立HDR目标已在IMG0032原尺寸HEIC原生回读，ImageIO/CI SDR0、实际gain及1/2/8公式满足原float门槛。此项从单图封装阻塞移出；五图独立HDR目标、理想中间headroom、全尺寸语义和独立global/local五路质量仍可在runner推进。真实屏幕需将S88密文成品在受控本地解密，分别在可记录headroom约1/2/8和室内/室外环境下查看同一原片/新片，记录亮度/剪切、肤色、边缘接缝及SDR未变；固定ACES小预览不能代替。相机同帧曲线/统计、Studio原统计及RAW配对仍按已有步骤；没有新增像素EV的j标定。


S89更新：5张真实独立HDR目标均已完成原尺寸像素计算，SDR全0，但最差IMG2600亮度p99达0.229329EV；不能把S87压力图或S88单图成功外推为自然度通过。继续在runner测固定ACES全图误差和目标亮度分层，并做最差样张10/12bit配对；保留所有非正亮度/符号变化计数。真实屏幕仍按S88受控headroom1/2/8查看方案，完整语义/独立GTM-LTM质量仍属runner工作；camera同帧曲线/统计、Studio原统计、RAW配对只待实机。


S90更新：最差IMG2600的完整固定ACES诊断已完成（h8像素误差p99=1/255，>2码267个，最大8码），这是中性SDR预览而非HDR屏幕验收；原SDR完整0差。真实HDR屏幕按已有headroom1/2/8/环境方案查看暗部色块与23个>4码极值，确认观看条件记录，不能用本预览推物理scene精度。12bit实编码但当前26A434 aux gain getter=nil：先做runner独立item解码/aux-tmap getter控制再定位，不直接归到“只能实机”。全尺寸语义和GTM/LTM分离质量仍可runner推进。相机同帧曲线/统计、Studio原统计、配对RAW继续待实机。


S91补充：原尺寸语义探针在编译guard处失败，尚无新consumer或逆解像素结果；先在runner以显式id<MTLTexture>修复pixelFormat类型冲突，再测原尺寸坐标ROI，不改旧模型。日本存储已实际保存并核验本run原ZIP/GPG，可容纳后续较大密文。该编译问题可runner解决，不归到实机。相机同帧曲线/统计、Studio原统计、RAW与HDR屏幕清单不变。
