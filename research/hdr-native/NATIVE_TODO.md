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
