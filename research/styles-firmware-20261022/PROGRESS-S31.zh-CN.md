# S31：square132可达域、low/sqrt分支与舍入合同

从实际 `reference=encode(clamp(rgb))` 和strength混合式推导，**不能推出square132≥1/16**。在明确的RN、power范围及mix顺序条件下，可证明外包络 `square132∈[0,2047/2048]`；零、非零次正规值、低于1/16的normal值，以及0.25及其相邻half都有构造见证。外包络端点可达，不表示内部所有half值都可达。

新增数学合同以运算、有限域和舍入条件准入，不使用坐标或完整tuple白名单。没有接入默认模型，没有改v3、S29白名单或旧失败，没有新增原kernel/原生编译。原iOS/GPU、FPCR和libm精度均未认证。

## 从实际指令表达式出发

`square132-proof-s31b.json`绑定现有S25实际执行IR的SHA及相关SSA行哈希，未公开专有IR。SSA104..112对应encode；127..132为strength权重、reference平方与mix；139是 **ordered <= half0x3400**，140在相等时选low138。

下文记 `RN` 为有限binary16 RN-even，η=2^-24。实际half常量由位型精确解码，避免手译：

|常量|位型|精确值|
|---|---|---|
|encode门限 t|0x1a69|1641/524288|
|线性系数 L|0x4a76|827/64|
|指数 α|0x36aa|853/2048|
|非线性 A、C|0x3c38、0xab0a|135/128、-901/16384|
|权重 B、W|0x2e66、0x359a|819/8192、717/2048|
|low/sqrt门限|0x3400|1/4|

前提是clamp输出c为canonical非负有限half，且strength所需half转换、除法及f32中间值均有限。原始buffer有限本身不保证这些中间值有限；未满足前提的调用不能套此推导。

## 可检查的一般外包络推导

strength路径中spread、ev经clamp均在[0,1]，factor取其min；base是`half(clamp(4*ratio-9,1,3))`。由单调舍入及可精确表示的端点，`strength=half(max(1,(3*factor+1)*base))∈[1,12]`，故 `w=clamp(RN(strength*B),0,W)∈[B,W]⊂[0,1]`。这是包含实际strength的外包络，不声称区间内所有half strength均由原stats可达。

reference分支可分别界定：

- c≤t：`r=RN(L*c)`，非负且不超过`RN(L*t)`。
- c>t：α≤1/2，且`t>(7/128)^2`，故理想实数`c^α>7/128`。若最终half power满足弱条件 `P∈[7/128,1]`，则scale/offset的分步或融合RN均给 `0<r≤RN(A+C)`。正的下界由精确有理数不等式及RN检查，而非浮点采样给出。
- c=0的sign结果为0；c>0的sign为1。`RN(L*t)≤RN(A+C)`，因此 `r∈[0,Rmax]`，其中 **Rmax=RN(A+C)=half0x3bff=2047/2048<1**。

该弱power条件可由“理想实数幂正确量化到half”推出，也可作为实际P的检查条件。没有证明任意powf/GPU都满足它；原shim的powf f32→half及误差须独立处理。

令 `u=RN(r*r)`、`d=RN(u-r)`。因为r∈[0,1]且RN单调，`0≤u≤r`，所以 `-r≤d≤0`。于是：

- 减法后分步mix：`v=RN(d*w)∈[d,0]`，`x=RN(r+v)∈[0,r]`。
- 减法后融合mix：精确的`r+d*w∈[0,r]`，故 `x=RN(r+d*w)∈[0,r]`。

两种明确合同均推出 **square132 x∈[0,Rmax]**。此推导使用带量词的区间关系、RN单调性及精确有理数常量检查，不依赖扫描通过率；不是形式化定理证明器认证，也不宣称穷尽fast-math的所有其他重排。若调用方不能建立所用mix/encode合同，应保留unknown。

## 构造见证与不能宣称的可达性

固定合法strength=half1，得到w=B。下列见证由输入c开始，按encode、平方和mix完整计算，不是任意指定square端点：

|c位型|reference112|square132|意义|
|---|---|---|---|
|0x0000|0x0000|0x0000|零确实可在前缀合同内构造|
|0x0001|0x000d|0x000c=12η|非零次正规值；需渐进下溢条件|
|0x1400=1/1024|0x2276|0x21d3|normal且低于1/16；所需前缀/low运算不涉及次正规值|
|0x3c00=1|0x3bff|0x3bff|外包络上端点可构造|

这四组还在现有完整v3 bright helper模型中重放：其他RGB通道固定.3/.6，working为(.2,.3,.4)，person.4、skin.3、exposure.8及原S25 raw stats。全部helper结果有限、strength确为1、112/132与精确前缀相同。没有用原宿主中间数组补值，没有新宿主执行；这不是从同一冻结源图到这些RGB的可达性证明。

边界候选由预先冻结的两个有限窗口生成，仅作寻路；随后以整数幂验证理想power的half舍入，并用精确有理数重算全部前缀。α=853/2048，检验`c^853`与候选half舍入中点的`2048`次幂关系，检查ties-to-even；不调用浮点pow作为证书。最终18个前缀见证包括两个mix顺序，不能解释成18个场景或一般GPU见证。

|目标square132|输入c位型；两种mix均有相同见证|结论|
|---|---|---|
|0x2c00=1/16|0x1dfd|旧叶下边界可构造|
|0x2c01|0x1dff|旧叶下界后一half可构造|
|0x33ff|0x2b8b|quarter前一half可构造，选low|
|0x3400=1/4|0x2b8f|quarter本身可构造，等号选low|
|0x3401|0x2b93|quarter后一half可构造，选sqrt|

0x2bff（1/16前一half）未在冻结窗口找到；保留为**窗口内未找到、一般可达性未决**，没有靠扩大扫描或最近值兜底，也不据此宣告不可能。上述非线性见证的证书证明理想幂量化条件下的构造，不证明native powf误差。固定源图/真实同帧/原GPU可达性均另列未验证。

## SSA134–140的算术和准入条件

每通道令x=square132。由S29已映射的CPU片段，独立数学合同使用：134=`RN(16*x)`；135=`RN_fma(16*x-12)`；136=`RN(135*x)`；137=`RN_fma(135*x+4)`；138=`RN(137*x)`。乘16在该有限half域内可精确表示，但136的舍入不能代替137内的FMA乘积。新有理数实现显式处理zero符号和ties-even；没有改原默认算术。

|x条件|140选择|旧S29 `[1/16,1]` 叶的意义|新独立数学合同|
|---|---|---|---|
|0≤x<1/16|low|旧叶必须unknown，包含已构造的zero/subnormal/normal反例|RN前提明确；若所需操作数/结果有次正规值，还须渐进下溢前提|
|1/16≤x≤1/4|low|覆盖所选low分支|原normal/零算术条件，RN前提仍需明确|
|1/4<x≤Rmax|sqrt|旧叶即使能算多项式，也不是被选中的140|正normal sqrt定义域成立；最终sqrtf→half精度条件未建立则数值unknown|
|Rmax<x≤1|不在所证前缀外包络|旧叶接受这些数不表示实际前缀可达|不clamp回范围；条件外调用拒绝/unknown|

在x=half.25时，low路径为134=4、135=-8、136=-2、137=2、138=.5，等号返回half0x3800。sqrt分支只在严格大于quarter时被选中。独立`square140_contract.py`的sqrt理想RN结果用中点平方比较计算，但实际数值接受仍要求单独声明正确最终half量化；不能把理想sqrt直接当原CPU/GPU结果。

新准入按运算检查normality，而非新建tuple表。例如x=0x21d3在RN前提下可计算，所需输入和中间结果全是normal/零，不需要推断FZ16状态；x=12η缺少渐进下溢前提时返回unknown。RN未建立时也返回unknown。**这些是独立条件数学模型，没有更新旧S29守卫或默认v3。**

## 验证、成本与剩余项

12项测试通过（unittest .029秒），包括half ties/zero符号、精确幂证书禁止numpy.pow、构造边界、旧叶域外拒绝、新运算条件、缺少RN/flush/sqrt条件的unknown、窗口未找到不升级为不可能，以及用保存S29节点核对精确算术，未重执行原kernel。

主运行含1028次浮点候选前缀预测（**不是一般证明**）、18个精确前缀证书、4次现有完整bright helper模型见证。审计另复核18个证书；测试和审计没有追加helper重放。完整source管线、新原CPU/GPU调用、原生编译均0。原243份v3源码、S29/S30及历史失败/白名单均保持哈希。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p test_square_contract.py -v
python3 research/styles-firmware-20261022/bound_validation.py s31-evidence-replay /tmp/psr-s31-binding-new.json python3 research/styles-firmware-20261022/verify_square_domain.py /tmp/psr-s31-verification-new.json
```

输出须不存在；私有IR只核原文件SHA，不重建或下载。详细推导/见证为 `square132-proof-s31b.json`，准入结果为 `square140-admission-s31c.json`，最终收据 `verification-s31.json`，均在evidence下。源代码/输入执行前后SHA一致。

版本仍是iPhone17,3 /iOS27.0.1 /24A446、SmartStyleV1 /CMISmartStyleProcessorV1，产品代际、内部版本和HEIC编号分开。FPCR的RN/flush状态、native pow/sqrt精度、未观察SSA及原GPU未验；没有声称全clamp域的完整bright通过。cast16/多参数仍禁入，旧集合unknown、9字段缺缓存软件桥接、历史IR/UI/真实同帧/IMG_2810 build和未知源成片逆解缺口保留。没有下载、挂载、缓存搜索、私人媒体、被拒ps重试或其他项目/安全预算操作。
