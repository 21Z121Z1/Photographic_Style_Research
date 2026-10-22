# 正Tone其余38字段、场景缩放与consumer接口

本阶段基于 `f7154e38166da99c6a5604d89293f86d549920a1`，使用同一已取得的iPhone17,3 /27.0.1 /24A446资源；没有新下载、挂载、私人照片输入或原iOS/GPU执行。产品Styles2、内部V1和IMG_2810的Styles16仍按前述版本门分开。完整照片正向/逆解没有通过。

## 覆盖清点与复用

S6只验收 `SSRFGAdjustment[9:11]` 的正Tone系数，不代表正Tone的全部输出。本次从原AIR11实际40个store及metadata核字段名和byte offset，并对正/负分支分别追SSA数据依赖，收据 `tone-field-links.json`。它还单列控制依赖，不能把数据依赖集合当一般CFG证明。

|块|字段数/byte范围|本阶段处理|正分支输入依赖|
|---|---|---|---|
|BG|17 /488..552|新增17字段|tone、66项tone tuning中相应base4和tuning14；tuningType；类型4还需brightness/阈值|
|FG|16 /556..616|新增14字段；9/10直接调用已验收实现|tone、castType；saturation另读tuning11。正FG不读stats|
|semantic|7 /620..644|新增7字段|tone、baselineExposure.field7、tuning12/13、stats.globalStats[0].p98/[5].p98/[6].p75|
|负Tone|相同40槽|直接调用S7 `negative_tone.coefficients`|沿用原显式stats、tuningType、brightness、people thresholds、曝光参考等合同|

正分支没有用经验值填stats。`PositiveToneStats` 只含实际读取的三个slot/field；`PositiveToneContext` 独立提供66项tuning、tuningType、castType、brightness和baselineExposure.field7。`positive_tone.py` 复用S7的连续中心/误差包络运算和S6的两字段函数；没有重写θ9/θ10多项式，没有修改已有模型或旧S20证书。

新宿主比较执行原AIR11全文的三个group，**比较掩码排除FG9/10**，只计新增38字段；原shader不可避免写这两槽，不把它们计作新验收或重复原S6大批次。cast、SRL、prior、负Tone和原S6两字段native大批次均未重跑。

## 输入合同、方程与零点

正/零Tone模型域为输入转f32后0≤t≤1（包括−0）；stats三个量各有限、非负、≤16；66项tuning和brightness/reference绝对值≤16；tuningType/castType为显式整数0..255。类型4的两阈值绝对间距须≥2^-8。它们是本模型预算，不能宣称为Apple入口保护。无穷、NaN、负stats、错误向量长度/类型、退化阈值拒绝。

BG使用 `q=t^f32(1.2)`；whites/gammaContrast/localContrast/airy/underGrass为q的分段或clamp函数，contrast把tuning14的动态项与场景base相加，mids/sat/lighten还读不同base。正BG不依赖统计。FG使用 `r=t^.75`，不同字段在r=.5、t=f32(.4)、t=.5处分支；saturation为 `f32(.4)*t*tuning11`。semantic的bgLTM、GTC等有各自下界，fgLTM读取三个统计量与tuning12，fgExposureGain为 `(1-t^f32(.55)*(1-tuning13))*baselineExposure.field7`。这些是系数方程，不是EV、UI百分数、一条gamma或已知P3像素运算。

零Tone走正分支，**不保证所有系数为全局身份**：FG personMix约.2；BG contrast还保留tuning14和base；FG underTone仍受castType14控制；曝光参考也不一定为1。测试保留这些反例。新模型只复用S6两字段的原f32中心；其余字段是连续f64中心和显式宿主f32允许量。

误差传播沿用S7：普通算术2u、pow假设4u，u=2^-24；舍入可能跨条件时保留两支包络。该pow假设不保证所有libm，也不证明Apple GPU fast_pow/FTZ。没有把系数中心或通过的合成域提升为所有上下文的统一精度证书。

## 真实边界差异与宿主比较

`native_positive_blocks_check.py` 校验原AIR canonical SHA，再用原全文和已记录C数学shim宿主编译。153组边界/结构化上下文，加256组固定种子留出，共409组、1227次kernel调用、15542个新字段值：

|指标|实际结果|
|---|---|
|相对f32舍入模型中心的逐位差异|991|
|全局最大绝对差异|0.14999997385244115|
|使用分支包络的上下文|27，保留在结果中|
|其他上下文最大绝对差异|2.232809817037662e-7|
|声明允许量越界|0|

约.15差异不是小误差：FG mids在r<.5时取 `.5*r`，否则取 `f32(1.2)*r-.5`；阈值两侧约为.25和.1。接近 `t=.5^(4/3)≈.396850263` 时，宿主pow舍入与连续中心可能选不同支。收据没有删除该案例、扩大普通算术容差或只报非边界max。传播器在舍入不能确定分支时保留两支，**这表示局部不稳定，不能称边界数值一致**。另外FG whites在t=.5的两侧分别乘.5/.6，测试同样保留跳变；不强加连续或单调假设。

## scene缩放→完整系数→命名字段

`tone_interface.py` 的 `RendererControls` 是传给renderer的已有值，未校准到UI；`ResolvedSceneType` 明确是CPU resolver输出uint32，`ToneFrameContext.tuning_type` 是另一输入。

|连接|原证据|独立实现/状态|
|---|---|---|
|scene resolver→SSR sceneType|CPU `_SSRSceneTypeEnumFromSemanticStyleSceneType` 符号0x1d42f3ce4；结果写byte32|接口要求已解析值；resolver本身未建模|
|resolved sceneType→控制缩放|已核 `render-static-parameters.asm.txt` 0x1d42f2328..2368|code3用tuning59/60/61，code21用62/63/64，依次作用于tone/color/intensity；其他code在此块不缩放|
|缩放→SSR控制值|原0x1d42f2378/+237c写intensity/tone/color到byte4/8/12|显式f32乘法，原块没有clamp；缩放后按tone符号选模型|
|tuning字符串→tuningType|另一个 `_SSRTuningTypeEnumFromString` 符号0x1d42f3a68；写byte652|输入独立提供；不把它与byte32的sceneType共用编号|
|正负系数→SSR块|AIR11实际40 store/schema|命名bg/fg/semantic字段与offset；输出160B近似f32块，只对应byte488..648，不补整个672B参数|
|FG9/10→已有码|AIR10 `renderSkinAdjustments` 明确读取这两个槽|`skin_only_forward` 调用既有连续皮肤模型，只处理这两字段|

场景缩放新增原68B分支块宿主测试：80组、240个f32值，逐位差异0，原指令字未改。外壳只提供控制值、672B合成存储和resolved code；没有执行scene classifier、ObjC或iOS library。没有假设缩放只能保持符号，测试覆盖code21将正输入tone缩成负值的接口选择。

`SuppliedToneStats` 复用S7 stats并只补正分支新增的两个slot，避免同一个[5].p98复制成两份不一致输入。正/零→新模型、负→S7原模型，输出冻结为40项；字典带原字段名/偏移。`ssr_block_f32()` 是中心转f32后的近似块；其额外量化偏差须加上 `abs(float32(center)-center)` 再与中心允许量合并，不能当原GPU实际参数dump。

场景缩放可把tone推到模型域外，接口直接拒绝，不静默clamp。负分支沿用S7域[-1,-2^-24]，(-2^-24,0)仍是明确未覆盖区间；−0走正分支。以上都是数值合同限制，并非iOS/GPU环境阻塞。

## consumer映射与真正未完成的部分

`audit_tone_links.py` 对匹配的AIR10检查完整canonical SHA，并记录函数体SHA、行号及GEP读取定位。当前31个系数槽在 `renderFinalAdjustments` 和skin/FG/BG/semantic helper中有选定读取点。剩下9槽为BG airy、四个warmthMatch分量、bgGlobalMix，及FG airy、faceI/faceQ：当前已选AIR清单未找到读取点；**不是这些字段全局无用或功能不存在的证明**。它们仍属于静态调用链缺项。

|尚未建模或验收的对象|已有定位/可复用项|下一步性质|
|---|---|---|
|完整BG像素helper|AIR10:5589..5873；whitesCurve、ShadowsFilter/Negative、airyFilter、contrastFilter、smoothSatFilter、lighten/negativeLighten、underGrass、RichSat等调用已列|可继续静态和独立单位建模；本次系数比较不覆盖这些像素算子|
|完整FG像素helper|AIR10:4590..4813；whites、shadows、contrast、lighten、airy、underTone、smartContrast、tonalContrast等；只有skin9/10已有独立模型|可继续静态和单位建模；不能用skin接线代替FG全体|
|semantic像素helper|AIR10:5976..6093；GTC采样、BG/FG曝光、LTM/HR与人物权重|通用已知曲线逆/空间曲线混合工具可复用，尚未证明此完整helper等价于它们；`semantic_exposure.py` 的EV预算是假设，不接成Apple曝光标定|
|外层pixel流程|AIR10 renderFinalAdjustments:54..737的采样、颜色变换、gates和调用；另有S3 StyleEngine Apply差异|仍需静态/独立模型与精确颜色域/存储合同；接口拼接不等于管线通过|
|9个未连读取槽、两个enum resolver|字段/符号定位如上|静态缺项，不冒充运行环境阻塞|
|同机型原iOS/GPU、真实帧像素留出|本阶段均未执行|真正待依赖：iPhone17,3 /24A446可调用运行环境、实际bindings/function constants和授权同帧params/stats/tuning/mattes/guides/曲线/颜色域/配对输入输出|
|IMG_2810与完整逆问题|iPhone19,2精确capture build仍未知；旧S20保留|不能混机型/代际，不能承诺仅成片唯一恢复|

共65项单元测试通过，0失败/错误；新增9项覆盖完整块、依赖单变量、零点、两处跳变、错误stats/阈值/代码、场景缩放、两种编号、正负适配、160B布局、原皮肤复用、超域和负小幅缺口。没有重跑旧native大批次；没有触碰Photos、私人媒体、其他项目/进程、caffeinate或锁屏；既有ps拒绝未重试/绕过。

## 复验

仓库根执行；Python3+NumPy，原指令测试需Apple Silicon/xcrun，AIR宿主编译需本机LLVM。输出文件必须尚不存在。私有AIR继续在Git外。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_positive_blocks_check.py /path/to/private/0011.ll.txt research/styles-firmware-20261022/evidence/render-params-air.json /tmp/psr-positive-blocks-new.json
python3 research/styles-firmware-20261022/native_scene_scale_check.py /tmp/psr-scene-scale-new.json
python3 research/styles-firmware-20261022/audit_tone_links.py /path/to/private/0011.ll.txt /path/to/private/0010.ll.txt /tmp/psr-tone-links-new.json
```

实际收据：`native-positive-blocks.json`、`native-scene-scaling.json`、`tone-field-links.json`；本阶段没有生成新Apple二进制交付物或发布原始AIR/表/固件。
