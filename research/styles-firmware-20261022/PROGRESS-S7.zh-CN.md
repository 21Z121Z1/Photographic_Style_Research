# cast表、负Tone与prior布局：同参考固件的条件算子

本阶段从已发布的 `d7ae80d2c7b3bf6311e5e458f13e4c8bb4f1dcd2` 继续，只做未完成的cast表插值、负Tone系数及最小接口连接。**没有新下载、照片输入、原iOS/GPU执行或完整逆解验收**。使用已有只读SystemOS缓存；原表、原AIR与固件二进制继续留仓库外，只提交代码、短方法文本和哈希/统计收据。

## 版本与可复用组件

参考来源仍为官方 `iPhone17,3_27.0.1_24A446_Restore.ipsw` 已核包内OS/SystemOS成员，不能把同方法哈希升级成整拍摄链同一。

|层次|实际身份/作用|限制|
|---|---|---|
|产品代际|iPhone16官方规格的Photographic Styles 2|不推出bundle/class编号|
|目标参考固件|iPhone17,3 /27.0.1 /24A446，主cache UUID `0094EE12-3B41-3892-A043-9459D9C749FE`|尚无该硬件/build真实帧执行捕获|
|CPU框架|CMImaging `764.22.14`，UUID `0A9BC064-A4BC-330E-861A-C70A637B14B3`|本文模型只接显式参数/统计上下文|
|实际插件|SmartStyleV1.bundle /CMISmartStyleProcessorV1，已取得官方OS成员|V1不是产品一代；实际帧loader选择未运行核验|
|统计shader|原CMImaging metallib SHA `f6d825a7e5c00d0eec2e4721c51bdb7a6b9554073dc632273dec825ae1bf705f`；RenderingParamsFromStats AIR canonical SHA `5ca4d2dce19c7e8825f0608b04d3637ddf05f3eb507f33430670617624c02c53`|全文宿主重编译，含明确数学shim；非原GPU精度|
|纹理样张链|IMG_2810：iPhone19,2、Styles16、PeopleData3|精确capture build未知；不与本参考硬件混用|

可继续复用：已校验OS插件与metallib、同manifest SystemOS的79个cache文件、原AIR11/108/109、GTC/prior/SRL模型、正Tone→既有皮肤算子和原纹理consumer模型。本文没有改旧S20证书、原生像素阈值或已验收算子。

## cast选择、归一化与精度

`collect_cast_tables.py` 先检查79个cache的UUID/大小集合与主cache SHA，再核完整prior方法原字节；只解释有界的实际跳表路径，不执行ObjC初始化。16个索引×2个startup状态产生32条选择，包含26张不同的2400B表和一条无表路径。每张表是 `[tone5,color5,intensity2,3,4]` f32，实际值范围约[-1.214,2.301]，原表不公开。

名称连接另由 `collect_cast_names.py` 检查实际字典初始化器、CFString、constant integer class及Foundation实际 `unsignedIntegerValue` getter。getter从真实ivar偏移16读数，没有只凭对象字节猜索引。`cast-table-selection.json` 中两个false标记表示**表提取器本身未证明名称/集合**；后续独立证明在 `cast-names.json`。

|索引|内部名称|索引|内部名称|
|---|---|---|---|
|1|Colorful|9|TanWarm|
|2|DreamyHues|10|BlushWarm|
|3|Earthy|11|GoldWarm|
|4|NoFilter|12|Neutral|
|5|StarkBW|13|Cool|
|6|UrbanCool|14|LongGray|
|7|WarmAuthentic|15|Standard|
|8|CloudCover|16|BrightPop|

实际黑白集合为StarkBW、LongGray；Standard非startup为无表基础矩阵。上述是内部名称，未假定等于UI显示文案。`OwnedCastBank` 要求硬件/build/cache UUID和数值getter证明匹配，每次读私有表都核2400B长度与SHA；未知名称、错误版本与非bool startup拒绝。

`CastControls`、`CastTable`、`PriorResult` 将用户值、表和结果分开。输入是CPU该方法的tone/color/intensity及prior strength，不能当UI百分数或EV。tone/color先clamp[-1,1]，f32 `(x+1)*.5` 后乘4；intensity clamp[0,1]。索引floor、上邻居封顶[4,4,1]，分数上限为f32 `0x3f7fffff`。三线性顺序为**intensity→color→tone**；每次先f32减，再一次fused f32乘加。最后对基础矩阵和采样值按未clamp的prior strength混合；无表分支直接返回基础矩阵并忽略strength。

独立模型保留每一步f32/RN-even和原FMA顺序。声明的输入预算为有限轴绝对值≤16、strength绝对值≤8、表值绝对值≤64；这是本模型域，**不是Apple入口保护条件**。clamp后的多组控制可同输出、strength0可抹去表依赖，测试保留这些非唯一反例。

完整 `_ssccmpg_float3x4FromMatrix` 的152B叶函数先依原lane布局重排；黑白路径每列乘f32的1/3，再按原顺序相加、复制各通道。不把它解释成某个已知像素色域。结果是3×4系数；enqueue中60B原循环把它转为4个term×3通道，前3个为常数项，后9个为线性项。`shader_prior_matrix()` 接回既有 `rhs_updates`，只证明系数布局/接口，未执行整个线性系统求解或像素渲染。

## 负Tone三个完整系数块

`negative_tone.py` 覆盖原AIR11的三个负分支：BG17、FG16、semantic7，共40个输出。对应SSRParams输出byte488/556/620。输入tone为byte8，必须是CPU已做场景缩放后的SSR tone；与正分支保持分开。

`ToneStats` 显式标出8个SSRGlobalStats slot/field和额外stats.field4（byte10608）；`NegativeToneContext` 显式提供66个tone tuning、scene/cast code、scene brightness、blend阈值、FG modulation和semantic reference.field7。没有填经验人物统计或从成片猜原统计。scene2..8选择不同base4；scene4还按brightness和tuning阈值插值。负Tone使用幂1.2/.4、统计比值及clamp、smoothstep与两层semantic混合，不能等价成单一gamma或曝光增益。

声明域：tone∈[-1,-2^-24]；8个统计slot非负且≤16，额外blend输入绝对值≤16；66个tuning和其他标量有限且绝对值≤16；blend阈值递增并相隔至少2^-8；scene4专用阈值的绝对间距至少2^-8；scene/cast为0..255显式整数。小于该负tone幅度的情况、无穷/NaN、不合法阈值均拒绝，零统计保留。负分支FG θ9/θ10为0，但其他FG项非零，不能因此把负Tone当作整个皮肤/前景身份变换。

模型中心使用连续f64值，另逐操作传播宿主f32绝对误差允许量：普通算术按2u，pow显式假设4u（u=2^-24），分支不确定时保留两支包络。原f32字面量按确切位值读取。该允许量不是对所有libm或Apple GPU fast_pow/denormal行为的形式保证；本次通过只覆盖下面实际宿主输入集。颜色空间仍为调用方kernel工作域，未证明scene-linear P3、GTM/LTM或capture/edit通用顺序。

## 实际比较与更正记录

|检查|新增实际输入/输出|结果|可支持的结论|
|---|---|---|---|
|原cast CPU块+完整转换叶|26张实际私有表+1张合成表，756组；两阶段各9072个f32|插值逐位差异0、转换逐位差异0|同参考算术块/叶函数在该宿主、输入域上的符合|
|原AIR11宿主重编译|135结构化+256固定种子留出+1零统计=392上下文；1176次kernel调用、15680系数|对f32舍入中心834个逐位差异；max绝对误差2.1577695719088297e-7；允许量越界0；max误差/允许量0.4805732271|负分支系数的限定宿主比较；非逐位相同或GPU认证|
|原enqueue打包循环|34组、408个uint32位模式（含NaN原始位模式）|逐位差异0|矩阵term/channel布局符合|
|名称接口组合|16名称×2 startup，32次|1次基础矩阵fallback；记录输出与打包SHA|新接口接线和版本准入，非原初始化器运行|
|单元回归|56项|0失败/错误|边界、负例、分支和既有模型回归|

cast测试保留原556B算术块中的两条ADRP，利用宿主自有padding保持相对code/constant page位置；未改任何原指令字。转换叶152B、打包循环60B也均未改指令。收据含代码、输入/输出、源码、临时可执行文件SHA，FPCR等；临时二进制不提交。ObjC表选择、分配及完整iOS库未运行。

cast大批次完成后只澄清docstring并新增独立打包accessor，原算术未改；`cast-model-source-link.json` 同时保留比较时和当前完整源SHA及相同算术AST SHA，未把旧收据改写成新运行。正Tone、SRL、GTC与已有prior原生大批次均未重复。

开发中第一版负Tone semantic.field5错误地从.7开始内层mix，原SSA525实际使用 `a484=mix(1,a457,amount)`，另一支a505已含.7。第一次392组有252个允许量越界，max误差约.3。已修正公式，**未放宽误差界、未删除输入/失败案例**；新增近零连续性回归。失败全收据保留在任务私有scratch，公开更正摘要/哈希为 `negative-tone-development-erratum.json`。最终成功收据与更正前分开保留。

新增10个短方法共704B：配置/Builder prior getter-setter、黑白集合初始化、字典初始化、once冷路径、实际参数绑定helper及Foundation getter。连同既有35方法55680B，当前选定CPU静态文本为45方法56384B，均有原字节/文本SHA。导出器新增本地同名符号歧义拒绝与确切地址选择，避免以字典最后一项误选 `_OUTLINED_FUNCTION_28`。

## 复验命令

仓库根、Python3+NumPy；原CPU测试还需Apple Silicon/xcrun，AIR重编译需本机LLVM。单元测试不依赖私有表或照片。以下命令的输出路径必须尚不存在；不必重新跑已验收的大批次。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/collect_cast_tables.py /path/to/verified/cache /tmp/psr-private-tables-new /tmp/psr-cast-selection-new.json
python3 research/styles-firmware-20261022/collect_cast_names.py /path/to/verified/cache /tmp/psr-cast-names-new.json
python3 research/styles-firmware-20261022/native_cast_prior_check.py /tmp/psr-private-tables-new /tmp/psr-cast-selection-new.json /tmp/psr-native-cast-new.json
python3 research/styles-firmware-20261022/cast_bank.py /tmp/psr-private-tables-new /tmp/psr-cast-selection-new.json /tmp/psr-cast-names-new.json /tmp/psr-named-cast-new.json
python3 research/styles-firmware-20261022/native_negative_tone_check.py /path/to/private/0011.ll.txt research/styles-firmware-20261022/evidence/render-params-air.json /tmp/psr-negative-tone-new.json
python3 research/styles-firmware-20261022/native_prior_pack_check.py /tmp/psr-prior-pack-new.json
```

## 仍需的最小材料与验收边界

本阶段最小静态缺口“名称→索引/黑白集合”和“3×4 prior→shader RHS布局”已补。仍有更多动态统计、调参和像素调用链可研究，不能以本文40系数或方法数量声称全管线静态分析已完。

|验收层|当前状态|缺项/处理|
|---|---|---|
|静态调用链|实际参考框架/参数、cast表、系数、prior布局有定位和哈希|通过限定段；未声称完整capture/edit顺序|
|宿主CPU|原算术/叶指令及原AIR重编译如上|通过各自域；保留逐位差异和pow假设|
|原iOS/GPU|本阶段未运行|待依赖：iPhone17,3 /24A446可调用环境及实际loaded入口、function constants、buffer/texture/sampler绑定；当前Mac无法加载该iOS框架，停止相应验收|
|同帧像素与真实照片留出|本阶段0张|待依赖：授权的同帧params、原始stats/tuning、matte/guide、曲线、颜色转换/存储域与配对输入输出；不读私人图库、不以重生成stats代替原值|
|纹理样张链准入|仍未准入|IMG_2810精确capture build及iPhone19,2实际对应资源/原帧上下文；不新下另一机型整包|
|逆问题|保留原S20及clamp反例|原图+成片参数识别、完整HEIC条件逆、仅成片近似/集合分别处理；未证明唯一恢复丢失细节|

既有 `ps -ax -o pid=,command=` 曾遭拒绝，未重试或换进程列表路径；这不阻塞独立源码和已有固件静态分析。未操作其他项目、进程、caffeinate、锁屏/安全设置或私人媒体。只清理本任务只读挂载，不合并、删分支或force push。
