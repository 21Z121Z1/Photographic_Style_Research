# S32：实际sqrt链身份与完整选中域双舍入证书

对sqrt被选中的完整half输入域 **0x3401..0x3bff，共2047值**，精确证明：若sqrt先正确RN到f32，再RN到half，结果与理想直接RN-half sqrt相同。**域内双舍入反例0，f32结果落half中点次数0**。证书包含全部输入与逐项中点平方间隙，不是浮点采样或整个管线验收。

封存宿主的实际实现也已核：C源码虽写sqrtf，产物在 **0x15914执行f32 FSQRT**，没有外部libm调用；其前后为half→f32及f32→half的FCVT。数学双舍入不确定项已关闭，但实际RN/FPCR和架构实现符合性仍是前提，不把数学结果当本轮实际宿主/GPU精度测量。

## 实际链与二进制身份

仅复用S25封存IR、C shim和dylib，无重新编译或执行。产物SHA256为 `47185c09c0407d7c96aa9dc55e0581ae4e781836951c8b236d17f2ac6f8efbbe`，IR为 `b2511df6788aba904212217293d3a668457ea5d5d942e3cb43902cccc8a55c23`。封存输入/产物在静态读取前后核SHA；原始反汇编留本任务私有目录，公开只提交哈希、地址和脱敏合同。

链路分别由原IR、C和机器码确认：

|位置|实际作用|
|---|---|
|bright SSA133；根调用0xcf40|调用air.sqrt.v3f16|
|air.sqrt.v3f16|独立调用scalar half helper三次|
|0x15608 FCVT s0,h0|将half精确扩展为f32|
|0x1560c附近调用psr_sqrt_scalar|C源是sqrtf(a)，须以机器产物为准|
|0x15914 FSQRT s0,s0|直接f32硬件sqrt；该函数没有libm调用|
|0x15610 FCVT h0,s0|将f32结果转换成half|

选中域输入和sqrt输出在half/f32中均为normal正数，扩展精确，没有NaN/overflow/subnormal分支。因此本域没有flush-to-zero数值依赖；舍入模式及完成执行的条件仍须满足。局部链没有写FPCR，不代表整个进程的FPCR已知。

## 精确数学证书

`sqrt_double_round.py`不调用float、numpy或libm。对每个输入x，用精确Fraction比较候选舍入中点的平方与x，分别确定理想RN-half sqrt与正确RN-f32 sqrt，再对该精确f32数RN-half。每行保存：

- 输入half位型及精确有理数。
- 理想half结果、正确RN-f32结果和第二次half结果。
- 两个格式舍入区间的四个精确平方间隙。
- f32结果距理想half舍入边界的两个精确间隙。

独立验证器不重跑sqrt二分算法，只检查正平方根必落入各声称的最近舍入cell；全域间隙均严格为正。输入按位型顺序无缺失/重复，并记录编码序列SHA。`sqrt-domain-certificate-s32c.json`含2047行完整证书、反例列表及域覆盖。

这里证明的前提是 **正确RN-even f32 sqrt及RN-even half转换**。该前提不从“C调用sqrtf”或少量保存结果推断；静态审计另行识别真实机器指令。

## 为什么此域不会双舍入

本域 `1/4<x≤2047/2048`，所以 `1/2<√x<1`。在此根范围，相邻half舍入中点为 `M=(2m+1)/4096`，m=1024..2047。因此 `M²=(奇数)/2^24`。

half输入x的 `x·2^24` 则是偶整数：低bin的1023值为2^12倍数，高bin的1024值为2^13倍数。故对任一相关中点，`|x-M²|≥2^-24`，不可能相等。于是：

`|√x-M|=|x-M²|/(√x+M)>2^-25`。

f32在(1/2,1)的ULP是2^-24，正确RN误差至多2^-25，所以f32舍入结果不可能落在half中点。所有half中点本身可由f32精确表示；f32量化也无法越过一个更远的half边界。因此两级RN与直接RN-half选择同一值。这个奇偶性论证解释全域结果；完整有限证书逐输入独立核验它，不推广至别的原语、任意实数输入或整条管线。

## 数学、宿主实现与运行状态分层

|证据层|本轮结果|
|---|---|
|数学双舍入|全2047值精确证书，无反例|
|实际实现身份|封存CPU产物是f32 FSQRT及scalar FCVT链，无外部libm sqrtf调用|
|实现精度合同|若架构FSQRT/FCVT按正确RN语义工作、FPCR处于RN且执行完成，可应用上述证书；不是本轮运行精度实测|
|已有原宿主观察|保存S29有2条选中分支观察、仅1个不同输入，与证书吻合；不是全域宿主穷尽|
|FPCR|未测；局部未写不足以推断调用前状态|
|原iOS/GPU|没有运行或精度认证|

官方架构索引包括 [FSQRT](https://developer.arm.com/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C7-A64-Advanced-SIMD-and-floating-point-Instruction-Descriptions/-C7-2-Alphabetical-list-of-A64-Advanced-SIMD-and-floating-point-instructions/-C7-2-199-FSQRT--scalar-?lang=en)、[浮点精度转换](https://developer.arm.com/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point/-C3-8-4-Floating-point-conversion?lang=en) 和 [FPCR](https://developer.arm.com/documentation/ddi0487/mb/-Part-C-The-AArch64-Instruction-Set/-Chapter-C5-The-A64-System-Instruction-Class/-C5-2-Special-purpose-registers/-C5-2-8-FPCR--Floating-point-Control-Register)。官方搜索摘要确认转换使用当前舍入模式、FPCR RMode定义RN；动态页面/完整伪代码正文未能完整读取，因此链接不记为本轮独立完成的架构实现证明，更不替代实际FPCR测量。

## 域外反例与测试

一般双舍入确实可能出现。测试用 `M=2049/4096`、`y=M+2^-27`：y的RN-f32是M，再RN-half在中点取较低偶数0x3800；直接RN-half(y)则为0x3801。相应输入 `x=y²` **不是half值**，所以它是防止外推的域外实数反例，不能混入本域反例数。

11项测试通过（unittest .066秒），包括全部2047行的独立cell核验、端点/缺失检查、f32精确解码、禁止浮点sqrt/原生加载的证书生成、损坏证书拒绝、奇偶性、域外反例和原记录身份。保存S29的2条原宿主观察只作有限校准，没有重跑。

新增数学证书生成2047行，审计再检查2047行；测试另重生成2行并做整数/有理数检查。静态工具仅1次nm和1次定向objdump。**新增原CPU宿主/GPU函数调用、helper/整图模型调用、原生编译均0**。

可公开重建数学证书，无需Apple二进制：

```sh
python3 research/styles-firmware-20261022/certify_sqrt_domain.py certify research/styles-firmware-20261022/evidence/sqrt-domain-plan-s32b.json /tmp/psr-sqrt-certificate-new.json
python3 -m unittest discover -s research/styles-firmware-20261022 -p test_sqrt_double_round.py -v
python3 research/styles-firmware-20261022/bound_validation.py s32-evidence-replay /tmp/psr-s32-binding-new.json python3 research/styles-firmware-20261022/verify_sqrt_domain.py /tmp/psr-s32-verification-new.json
```

输出路径须不存在；最后一项完整静态身份复核需要本任务原私有封存目录，缺件应报告，不重建/下载。`sqrt-static-s32a.json`、完整证书和最终 `verification-s32.json` 均在evidence下；源码/输入执行前后SHA一致。

v3及S29–31原模型、白名单和失败记录未改，没有新增通用bright或管线验收；powf、cast16/多参数未扩展。版本仍为iPhone17,3 /iOS27.0.1 /24A446、SmartStyleV1 /CMISmartStyleProcessorV1，产品、内部版本与HEIC编号分开。旧集合unknown、9字段缺缓存桥接、历史IR/UI/真实同帧/IMG_2810 build和未知源逆解缺口保留；未下载/挂载固件、搜全盘缓存、重试被拒ps、访问私人媒体或操作其他项目/安全预算。
