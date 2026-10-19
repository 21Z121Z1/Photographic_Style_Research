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
