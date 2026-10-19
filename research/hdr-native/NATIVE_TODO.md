### HDR-NATIVE-20261019：独立 HDR 与 scene 验收分开

**可交给macOS runner（HDR-R1）：** 在S32已定位的原生gain读回域基础上，固定编码矩阵/范围/坐标/位深与tmap元数据。分别用原生primary/raw、ISO aux和CPU decoder捕获同一单通道斜坡/RGB常量/负EV/0黑位，先过每算子maxabs1e-5且PSNR60的原float门槛，再验证编码后目标maxrelative1e-3。不从RGBAh推断位深，不把12bit nil标为普遍不支持。10bit若范围量化仍越界，应报告或寻找经原生验证的有效精度方案，不降低门槛或删点。接着冻结配方，用真实5图（2张冻结后留出）、4032×3024/5712×4284以及低/中/高headroom；保留原SDR coded descendants/property并运行冻结full_sdr_compare.m，max0才过。边缘/色彩/近黑/clamp/codec与thumbnail误差分开。

**可交给macOS runner（HDR-R2 / A仍未完成）：** 已知输入A的原PSO目标反事实可用operator_recipe独立控制consumer local/skin；真实最终Y须完整集合逆F^-1，保留33点原mask与C01–C05全域tight hull缺口。新输出来的RGB比值自洽不解决这些条件。实际生产曲线可调用的代码能先在ARM诊断宿主做条件重放，但没有同帧实际曲线不得标Apple恢复。旧bit-exact方向已按用户收尾，不重新做参数拟合。

**待实机（HDR-DISPLAY）：** 用同一最终载体和同一原SDR，在能记录EDR/HDR headroom、白位/峰值、环境照度的真实屏幕上测试1、1.25、1.5、2、3、4及内容满档。捕获系统实际线性输出或可审计屏幕测量，比较预设H与mid-headroom目标、skin/人物背景EV、色度/边缘/光晕、HDR↔SDR切换。区分OS显示适配与内容图像本身；固定ACES SDR截图不算通过，不做203nit场景标定。

**待实机（D-PAIR-CURVE/D-STUDIO/D-RAW）：** 沿用前述匹配build、冻结同帧A→A与A→B→A方案：原j/仅j=1/WithoutFaceBoost只改单一目标，捕获N、B/T/V、face hist/ROI、allocateTone约束及配对global/local曲线、c/d/GTC重算、实际应用前后RGB/域/clip/plateau。原分支先重建；global/local交叉四对照保留非交换交互。j的β只作内部权重界，未得曲线不能计算实际EV。Studio须原统计，RAW须IMG_2679/IMG_2408配对；这些缺口不由Gain Map承载成功替代。

**可交给macOS runner（HDR-CODEC-12）：** S32的12bit CGImage/CIImage对象均存在而primary render代码错误、ISO aux nil。对这两个确切文件抓ImageIO的bits/layout/provider数据、CGContext16bit CPU转换、CI软件/Metal两种context及aux CVPixelBuffer plane/attachments，先用已知整数code验证，再判定是12bit profile/像素格式、CPU decode还是GPU上传路径。不能笼统归为无Metal或不能开文件；如runner数值路径能解决就继续runner，只有真实设备差异比较列待实机。8/10bit matrix1/6的primary与aux记录的最大误差相同（不能据此断言逐点一致），编码RGB↔YCbCr和native读回误差与理想均匀量化分开记录。
