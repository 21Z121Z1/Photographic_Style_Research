<!-- SEMANTIC-20261018 -->
## 2026-10-18–19 人物/皮肤语义阶段：SEMANTIC-20261018

**A 阶段尚未完成。** 独立 consumer 皮肤参数已得到非零原生对照，逆向候选及人脸/人身保守估计已有真实样张数值和分开预览；皮肤联合候选仍有像素超过原 `1e-3` 门槛，完整 Studio 上游上下文及原拍摄 counterfactual 尚缺。旧 `acceptance_complete=false` 保留；不再追旧 NumPy/MSL bit-exact，也不以高 PSNR 替代最大误差门槛。

### 证据与适用范围

**已验证数值（SEM-01/02/03）**：IMG_2810 原件 SHA256 `52ea41f0dd16590cef83abfd8093ccf8082994113e0c2cee86f90c42f7ab21c2`，5712×4284，Styles v16。12 张新语义 matte 为 768×576（nose、skinV2、nonFaceSkin、lips、teethV2、person、glassesV2、eyebrows、tattoo、hands、ears、faceSkin），另有 3 张旧 matte；本文件没有 hair matte。`j=1.09765625`，`log2(j)=0.1344263202209261 EV` 只是算术量。metadata-inventory.json、S2 run39134556722 的 facts/metrics 是基线，本轮未重跑 j 干预。其实际值/1/1.2 ×renderer/style-engine，固定 tone0 的四个比较各 589824 个 RGB 分量均 0 差；不能据此宣称撤销了相机提亮。

**已验证数值（SEM-03/20）**：214B texture_styles plist 只有 7 项，没有 TextureStylePostProcessedPeopleData/FaceAttitude；空 aux 字典的原生解析结果 persons=0。S7 的 ImageIO inventory 另找到一个 ExifAux Face region，包含 faceID、位置及角度，但它不能提供完整 imageStats、原始 instance mask 和眼部统计；不能笼统说照片“没有任何人脸位置数据”，也不能把 parser persons0 当作相机从未处理人物的证据。含完整 ImageIO 元数据的文件只留私密加密归档，公开证据只给字段存在性。

macOS 原生结果均来自 **27.0.1/26A434，xcode-27-arm64 20261012.0260.1，Apple Paravirtual Metal**。iOS 静态生产端是用户提供的 iPhone12,1 /27.0 /24A446 cache；与 iPhone18Pro/iOS27.0.1 样张的硬件和版本不一致。CameraColorProcessing UUID `0A211E15-50CA-373B-AD9A-F9E3283C68F4`、已拆文件 SHA `974ffb2895cae06e26e63bd77ab4891f5401d4789449f7a0080d377553b2426e`；24A446 归属是缓存来源记录，不是从样张反推。cache 只读，未搬动/删除；只提交符号、地址和 AIR/反汇编文本。

新结果的逐项 file/line/JSON pointer、原始文件 SHA、run/artifact/ZIP/cipher/manifest SHA 见 [claims.json](evidence/claims.json)、[evidence-index.json](evidence/evidence-index.json)、[runs.md](runs.md) 及各 run 的 archive-audit.json。S4–S9 密文原包均保留；GPG 完整性与 manifest 全文件 SHA 校验独立于 workflow 的 success。

### Consumer 的语义参数、空间与调用顺序

**已验证静态（SEM-07）**：CMImaging AIR0010 `renderSkinAdjustments` 在 4375–4504 行，调用点 486 行。texture10/11/12 分别是 person/skin/sky；AIR 78–150 行对 person 与 skin 乘同一场景权重：若 SSRParams.field21<0，alpha=1，否则 `alpha=max(smoothstep(clamp(L/K,0,1)),0.3)`，K 来自 SSRCastAdjustments.field21。这两个字段的名字不能替代数据流证据。person 还参与前景/背景 LTM 混合，故不通过清零 person matte 来隔离皮肤色彩。

本次 native consumer 的 inputSkinMatteImage 明确取文件的旧 semanticskinmatte，person 取 semanticpersonmatte；新 faceSkin/skinV2 等另外解码供诊断/纹理链使用。它们不是自动绑定到 consumer texture11 的证据。见 run_semantic_s5.py 的 aux suffix 选择和 consumer-toneP035/semantic/results.json 的固定 texture SHA；S8 对所有 texture/buffer/ROI 再做逐字节相同检查。

皮肤处理位于 semantic tone、BG/FG 调整和 saturation 之后，highlightRecover、brightness/contrast 及末端颜色处理之前。其输入是该阶段的 working RGB，**不能标成 scene-linear P3**；最终 texture13 与同配置 CI extended-linear-P3 render 的 S5 对照为 0 差，故本文估计输出在这个最终线性 P3 空间比较。独立去除必须通过同一完整 downstream 变换，不能直接在 scene 空间猜一个 gain。

**已验证静态（SEM-07）**：令 x 为 working RGB，m 为 skin 权重，g 为该调用点的 guide，theta9/theta10 为 SSRParams.field14 内的两个 float（绝对偏移592/596）。亮度分支先算 `v=clamp(x,0,1), r=sqrt(v), l=sqrt(.333252*sum(v)), a=l*(1-l)*theta10, s=sqrt(g)`；混合 `r+(s-r)*(-2a)` 与 `r+2a*(dot(r,[.299,.587,.114])-s)`，权重 .799805，再平方非负 root，并保留 x 的区间外分量、逐通道 max(x,...)。随后 theta9 分支按亮度与归一化色度的两个 smoothstep 生成权重，向 `x*inverse_sRGB([1,.700195,.549805])` 混合，最后按 m 与原 x 混合。参数绝对值<1e-5 时对应分支跳过。完整顺序/常数和归一化见独立的 semantic_skin_model.py；这是 AIR 的连续解释，未宣称 half 逐位复刻。

**已验证数值（SEM-11）**：S5 run39139035394 固定 c/d、GTC、两 guide、统计、ROI、颜色上下文及全部 matte，只改上述两个 float。目标参数以外改变字节数为 0；三个 tone 配置的原 Apple pipeline hydration 都为 0 差。tone0/−.35 的 theta9/10 均为0，消融为0；tone+.35 时 theta9=.503125011920929、theta10=−.22238825261592865：

|只中和的参数|改变的 half RGB 分量|相对原生基准 max abs|对照差异 EV MAE（S6重算）|
|---|---:|---:|---:|
|皮肤色彩 theta9|1794|.020263671875|1.330341365e-5|
|皮肤亮度 theta10|4552|.009033203125|8.80063453e-5|
|两者|6346|.020263671875|1.0130983e-4|

这些是**已知输入的受控重新编辑 counterfactual**，不是 IMG_2810 原拍摄已烘焙风格的无风格真值。复合 key1 的 Gaussian 亮度平面与二次 RGB 基函数沿用 C08/C09，不能把8平面解释为8个人物类别。对任意可逆 S，`A∘B=(A∘S^-1)∘(S∘B)`；仅有复合映射不能唯一拆出原拍摄皮肤项（SEM-06）。

### 逆解改进、失败定位与信息界

**已验证数值（SEM-12）**：连续皮肤单位模型在 +.35 时，与派生 MSL 的内部模型观测 max abs=4.5579672e-4；连续 Newton 往返 max relative=1.558759e-6，覆盖率95.08616%，singular0。内部模型不是原生内部捕获；其整幅输出对 Apple 原生仍 max abs=.00537109375、PSNR68.8524dB。该连续模型的往返不能证明原生相机逆向正确，也未达到 half 逐位/float max1e-5 门槛。

**已验证数值（SEM-13/14/18）**：旧完整 native 逆解只用一个输出导出的种子，在正值 box 中解完整 F。S5 已有 70387 个存储 float residual>1e-3；S7 分层发现皮肤内部同样有失败、matte 边缘不是唯一原因，原输入超旧正值 box 的仅323个，皮肤采样足迹外失败约6.66万个。直接 `F0(xhat)` 把完整 F 的误差带到无关背景。

改为 **`Y_est=Y + F0(xhat) − F(xhat)`**：只估计目标参数中和引起的 delta，保留现有 Y。F/F0 都是相同原 Apple kernel、固定上下文。S8 用允许少量负P3的搜索 box[−.02,1.25]、三个不含原输入的种子和加法 RGB LM，只细化皮肤3×3采样足迹（9004个原有效像素）；未重新拟合 c/d/guide 或修改 AIR。**搜索 box 变更不改变验收 mask/1e-3 门槛**；没有 half lattice/逐位搜索。

对原声明的186949个有效像素（全图95.08718%）保留全部失败比较，结果如下。PSNR peak=1；分母为该原生参数中和对照的绝对通道值。皮肤有效足迹只占全图4.57967%，所以同时给该范围 PSNR，避免整幅背景稀释误差。

|逆向分量|S7残差法超1e-3像素|S8超1e-3像素|S8 max relative|S8 max abs|S8 PSNR全有效/皮肤足迹|S8 EV MAE/max|
|---|---:|---:|---:|---:|---:|---:|
|仅皮肤色彩|179|91|.004085802|.001953125|94.6885 /81.5156dB|1.06394e-6 / .00335257|
|仅皮肤亮度|434|205|.006788866|.0009765625|103.3200 /90.1471dB|1.81137e-6 / .00346258|
|两者|613|296|.006788866|.001953125|94.1307 /80.9578dB|2.87531e-6 / .00346258|

全部三项在皮肤足迹外改变 max abs=0。联合旧 direct PSNR约47.319dB，S8为94.131dB；这是有证据的改进，**并非通过最大误差门槛**。原整体 F 往返仍有大量背景失败；S8仅细化皮肤区，不能将这一范围误写成整幅完整逆解已通过。原有效 mask 不按求解成功与否缩小。S9 另保存失败、近黑、低有限差分Jacobian秩、matte边缘、观察到非唯一性的独立 masks；低数值秩不命名为已确证 plateau/clamp。

S8 在已知可行原输入处的有限差分 Jacobian（h=.004）中，全有效197个低秩、皮肤足迹9个低秩；旧70387失败集内仅43个低秩，条件数中位1.4922、p99=8.5631。有限尺度诊断不证明严格可逆，但不能把7万个失败统称为 clamp/不可识别；大部分仍属于迭代方法/量化停滞。使用的是原生完整 F，故这次失败不能归咎于 NumPy 缺算子。严格区分这个结论与未认证的内部连续模型。

**已验证数值（SEM-19）**：S8 三种独立种子找到不同的量化 half 输入，原生 F 输出逐位相同，但 F0 输出不同。联合中和的三个种子对分别有44/42/47个这样的见证，最大输出分离9.765625e-4；不能相加当独立像素。色彩为18/14/14、亮度为26/28/33个见证。它们证明部分量化反解确实不唯一；并不证明所有296个未达标点均不可识别。原始见证值只在密文中，公开只给计数/范围。

样本根之间的跨度只是歧义的**下界**，不是完整误差上界。完整 camera inverse 在缺统计、未知分支、clamp/近黑处不声称有限界；完整区间仍未获得。不要把 recovered residual mask 或搜索范围当作唯一性证书。S9 的更细边缘指标与阈值审计见补表及 evidence-index。

### 拍摄端 j：传参、曲线重算与保守去提亮估计

**已验证静态（SEM-05/15）**：FaceBasedGlobalExposureBoostRatio 在0x256b65b14..44进入 driverInput+0x24；LTMDriverV2::Process 在0x256bab880读取、884写入 common input，结合0x256bab574..578 的基址，该位置为 computeInput+0xa92c。faceWeight/faceWeightV2 在0x256bab700/0x256bab9d0 等路径由 face ROI、histogram/区域统计计算；这里不能确认它等于文件的 faceSkin matte。

`-[LTMCurvesComputeV2 compute]` 0x256b86e30..0x256b86eec 的 WithoutFaceBoost 分支将 j 改为1，并重新 computeLtmComputeInput、computeLTM，再写 curvesType2/3；不是消费端给最终图除j。LTCGridCalcAlgo 的一个受控分支（meta+0xc==1）在0x256ba9edc..0x256ba9f28计算：

`a=clamp(1−1/(κ*sqrt(N)),0,1)`，`cap=clamp(a+2*(1−a)*(j−1),0,1)`，`κ=.22360679507255554`；0x256ba9f34..50 将局部权重以 cap 截顶。N 是此分支读入的统计标量，完整物理语义及本样张是否经过该分支未确认。a=0、j=1.09765625 时 cap=.1953125，不能解释为每像素固定增加.134426EV。S6 对确切20条AArch64指令/常数字节做64个输入重放，float32全部0差（SEM-16）；这不是原生 iOS 全曲线 oracle。

之前把另一处257点曲线幂指数说成1/j的推断撤回：0x256ba5a44读取的是派生内部参数，当前数据流没有证明它直接等于 j。生产端求曲线的完整应用域、匹配固件下的 face统计/matte和最终 c/d/GTC 打包因果关系仍**待实机解决**，测试见 NATIVE_TODO.md。静态摘录含原文件行号和地址，不凭字段名推结论。

**假设（SEM-17），数值性质已验证**：提供分开的人脸/人身去提亮候选，`Y=X*2^(-b*w)`，同一 scalar 乘 RGB；b分别为 .5log2j=.06721316 和log2j=.13442632 EV。face 用 faceSkin，body 用 person*(1−face)；固定正系数5tap binomial平滑及smoothstep是显式工程假设，**不是 Apple 已证算法**。j 不识别人身幅度；API要求调用者指定 budget，人身预算不能自动认定为log2j。候选在已解码 primary 线性P3上应用，GTM/LTM不改；不是scene-referred或真实camera inverse。

S6 run39140025554 重算后的四个候选：

|分量/预算|ROI中位 EV|最大校正梯度 EV/像素|校正Laplacian p99|标量往返 max relative|
|---|---:|---:|---:|---:|
|face .5×|−.06649225|.03174190|0（脸占比很小）|1.39321e-7|
|face 1×|−.13298450|.06348380|0（不能据此说无边缘）|1.47140e-7|
|body .5×|−.06721316|.03494947|.00639622|1.61358e-7|
|body 1×|−.13442633|.06989895|.01279245|1.75812e-7|

共同性质：背景 max abs=0、预算 overshoot像素=0，最大色度变化1.1920929e-7；正值 mask 往返覆盖94.68486%，max abs5.9604645e-8。梯度与Laplacian是当前512网格上的测量，无断层/平滑没有另造已通过的感知阈值。0.5×/1×并列供幅度敏感性检查，不能用自洽往返误差当作去提亮真值误差。base+gain map 的 OPPO 类文件只给最后输出与传输比值：空间照明、语义提亮、材质反射不能唯一分离，本次没有独立 OPPO 无风格配对验证，不报告 Apple 幅度一致性。

### Studio：SIGABRT、AIR 与条件逆解

**已验证数值（SEM-08）**：S4 run39135794320 已获准下载并完成流式校验；177文件23,419,764B、GPG/SHA失败0，未重复下载。修正 NSValue extents→CIVector、加入受限getter和checkpoint后，LLDB正常退出。UnderEye、SkinSmooth、Mattify各对589824个RGB分量0差，但persons=0、三效果requiresPersonData=true；这是缺上下文的身份路径，不能声称已撤销相机皮肤处理。S3辅助接口遍历SIGABRT未有证据锁定某一个getter为根因，保留边界。

S4 单一 llvmlite wheel 导出61/61相关 AIR 文本；未上传 Apple metallib/binary。CMImaging default.metallib SHA `16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11`。S1原生 Studio 顺序是 UnderEye→SkinSmoothStandalone→Mattify，macOS iPhone19,2/back/still/Common tuning 的 brightnessMix=.5、Mattify.editingStrength=.3 等已存证；与相机固件完全等价未证。

**已验证静态（SEM-21）**：AIR0138:140–158 的 UnderEye FinalMix 为 `w=clamp((face−lip−ear−tattoo−glasses−hair)*instance,0,1)*blendCondition*brightnessMix*stats.strengthFactor`、`Y=mix(X,E,w)`，先后次序按half指令。E是上游 edited image；不是由j直接得到。已知E/w时，连续条件逆为 `(Y−wE)/(1−w)`；w接近1给plateau/区间，不猜唯一值。

**已验证数值（SEM-22）**：S6该探针仅因漏链CoreGraphics失败；S7 run39155124218加上该framework后原生FinalMix正常执行。用真实主图/mattes，固定人工 edited=1.15×input、strengthFactor=1（无原始上游统计），0/1输入独立探测w，再冻结E/w逆解并送回原Apple kernel。brightnessMix=.5：wmax=.5，非零覆盖.191752%；原生往返 max relative=9.58772784e-4，覆盖94.68384%，PSNR114.0602dB。连续仿射 forward 对原生 max abs3.92436981e-4，虽PSNR112.28dB，仍不通过float max1e-5。逆解与已知原输入 max relative=.00133366，说明原生往返通过也不等于精确恢复输入。

提供明确先验RGB∈[0,1.25]时，保守half/FTZ区间在该有效mask内排除原输入的像素0，最大宽.0130410；这不是scene/camera无先验上界。mix1有49个plateau像素（全图.0249227%），有效94.65892%，区间可扩到整个先验box。原输入可能的负P3及相机真实域不能沿用这一box；接口默认box仅属本受控单位实验，未认证实际相机逆向。

**已验证静态（SEM-23），可交给 macOS runner 的条件重放尚未完成**：SkinSmooth AIR0151:207–239 最终形式为 `Y=(1−a−b)X+b(X−B+S)+aS`，其中S为此前saturate过的重建项，B是另一blur采样，a/b由mask²、统计和亮度相关函数生成；可写成`(1−a)X+(a+b)S−bB`。冻结这些项时可条件反解，但a/b及上游平滑项不是已识别的原拍摄常量；仅凭最后图无法恢复被抹掉的纹理。

Mattify AIR0067:100–227/232起函数包括 mask归一化blurred color、与averageColor混合、HSL亮度/饱和度编辑、region blend、纹理addback及editingStrength门控，不是只乘skin×gain。一般含min/clamp和依赖X的addback，不能套UnderEye仿射逆。完整逐算子 native 非零/条件逆仍属runner工作；原始人脸统计不可由字段名或一张Face ROI补齐。原拍摄Studio上下文、前后对照及缺失纹理的恢复仍待实机，不把普通编译/接口失败归为实机限制。

### 预览污染纠正、独立交付与后续

**已验证数值（SEM-24）**：S5 preview 对 C-contiguous候选RGB使用ascontiguousarray，OCIO原地修改同一数组，污染随后的人脸/人身指标及保存的RGB候选。S5这些指标/NPZ全部作废，原归档不改。S6只在runner解密副本后用`np.array(...,copy=True)`重算；20/20次预览前后input SHA相同。S7/S8预览亦检查输入不变；原生S5参数干预和独立连续单位模型指标没有被该显示alias污染。orientation文字在S2/S4错误，实际np.rot90(k=3)是90°顺时针，符合irot3；更正仅写errata，不改归档。

预览统一 OCIO2.6 `cg-config-v2.2.0_aces-v1.3_ocio-v2.4`，Linear P3-D65→sRGB Display /ACES1.0 SDR Video，0EV，无逐图曝光拟合；配置SHA `5aefc668796eabb1902b9593340496231758eceaec18ce290e12901042bd4440`。本地预览索引见 [PREVIEWS.md](REPRODUCE.md)，含reference、仅皮肤色彩、仅皮肤亮度、两者、人脸/人身 .5×/1×及受控眼下条件逆。它们未明文提交/上传。HDR gain候选保存在私密NPZ，GTM、LTM、语义三部分不合并；没有新建已认证24MP scene输出或203nit标定，原SDR文件未写入。

本轮额外写入预算100MB、剩余磁盘不低于4GB；只在macOS runner做图像计算。本地Python均用scripts/local-python-scope.sh；原件、历史归档、冻结模型、两个未跟踪consumer-goto-v8文件保持不变。临时传输资源在结果校验后清理，准确复核记录见transport-cleanup-20261019.json；永久源码仅提交研究分支，不动master/PR/merge。

下一步的可执行边界：皮肤逆解剩余失败与低秩/歧义分别保留mask，完整误差上界尚缺；SkinSmooth/Mattify在固定人工上下文下的非零native单位探针可继续交runner。真实相机WithoutFaceBoost曲线重算、Studio原始person stats/眼部上下文及匹配RAW的精度由实机计划提供输入、捕获项和判据，不将其伪装成已完成。RAW仍需Mac上的IMG_2679/IMG_2408配对组。


### S9 补表：剩余误差、边缘与量化歧义（已验证数值，SEM-25）

run39156641912仅审计S5/S8保存数组，无新逆解搜索。matte边缘定义为3×3局部max−min>1/255；以下“误差梯度”对比估计和原生参数中和对照的EV误差场，单位EV/512网格像素，不是完整24MP的感知验收。

|分量|失败/其中位于边缘|观察到非唯一像素（种子对并集）|失败与非唯一交集|边缘误差梯度p99/max|
|---|---:|---:|---:|---:|
|skin-color|91 / 82|30|5|0.00260439 / 0.00496115|
|skin-brightness|205 / 181|57|23|0.00311269 / 0.00642184|
|skin-both|296 / 263|87|28|0.00337250 / 0.00642184|

三项失败像素与h=.004数值低秩的交集都是0。剩余失败主要集中边缘，但并非全由matte边缘或已证歧义解释：联合296个失败中263个在边缘，28个同时是已观察到的非唯一点。不要将未知原因归因过度。失败/近黑/边缘/观察到非唯一/低有限差分秩/搜索边界mask已加密保存，完整上界仍缺。

阈值审计同时保留两种定义：S5存储float32 residual转float64比较有70387个失败；从原生half像素重新以float64计算有70381个。差6个恰在float32(0.001)，该float值略大于实数0.001；未改门槛。S8/S9参数中和的91/205/296个失败来自half像素重新算出的float64误差。旧存储值统计与新重算值不混用，原归档不改。
