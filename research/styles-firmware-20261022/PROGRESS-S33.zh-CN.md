# S33：单次封存CPU原语调用的只读FPCR绑定

**本次同一原生线程在调用前后读到FPCR均为`0x0000000000000000`，RMode均为0（RN）**。新增wrapper只调用封存CPU重编译产物的`psr_sqrt_scalar`一次，返回位型符合S32证书。本次当前调用的RN缺口已关闭；不能追认S25/S29历史FPCR、其他线程、原iOS/GPU或完整管线。

## 调用与身份

预先固定输入half `0x3880`（9/16），期望sqrt为3/4。两者均为normal且结果精确，避免把此次状态绑定做成不必要的inexact/trap压力测试。没有重跑2047个输入，也没有测试powf。

|观察|本次保存结果|
|---|---|
|C调用前/后线程ID|4036989 /4036989|
|Python调用前/后native线程ID|4036989 /4036989|
|pthread_self前/后|相等；公开只保留其hash|
|FPCR前/后|0 /0；RMode = `(FPCR >> 22) & 3` =0|
|输入half /f32|0x3880 /0x3f100000|
|输出f32 /half|0x3f400000 /0x3a00|
|新增封存原语调用|1；wrapper同步间接调用，无工作线程|
|FPCR写入或主动模式切换|0|

调用的原产物SHA256仍为`47185c09c0407d7c96aa9dc55e0581ae4e781836951c8b236d17f2ac6f8efbbe`。`dladdr`绑定实际加载文件、其SHA和image offset `0x15908`；封存函数在`0x15914`执行`FSQRT s0,s0`，本体没有调用或FPCR写指令。实际地址、完整反汇编和72字节原始报告留在本任务Git外私有封存目录。

**两侧half↔f32转换属于新增wrapper，旧half helper没有执行。** 新wrapper产物SHA256为`8bd7b654a4a0c30a39076a0a2b6136090cbbf5533da2c3b55947a0305bc5a787`。实际机器码顺序为：

`0x4ec MRS FPCR → 0x4f8 FCVT s0,h0 → 0x508 BLR → 0x514 FCVT h0,s0 → 0x51c MRS FPCR`。

两个MRS之间只有这一次函数指针调用；线程查询在窗口之外。静态检查没有用C源码顺序代替机器码。所调封存leaf及整个新增wrapper没有MSR FPCR；未调用舍入模式setter。原二进制未修改或重新编译。

编译前持久保存wrapper源码、driver、固定输入和原二进制副本，封存manifest；编译只读取该源码。编译器、参数、产物与原输入均保留SHA。编译前后、加载前/调用后再次校验一致；运行标记在调用前写入，禁止对已开始或结果不明的调用自动重试。公开结果见`fpcr-prepared-s33a.json`、`fpcr-current-run-s33b.json`和`verification-s33.json`。

## 架构语义来源

本轮通过公开后台浏览器读取了以下Arm官方页面的相关正文，版本分别记录在`architecture-s33c.json`；没有将S32当时未读到完整正文的记录改写。只保存短摘录、释义和链接，没有完整手册正文hash或再分发全文。

- [FPCR，DDI0487 M.b /C5.2.8](https://support.arm.com/documentation/ddi0487/mb/-Part-C-The-AArch64-Instruction-Set/-Chapter-C5-The-A64-System-Instruction-Class/-C5-2-Special-purpose-registers/-C5-2-8-FPCR--Floating-point-Control-Register)：RMode位23:22，00为RN；成功MRS访问把FPCR值读入通用寄存器。AHP位26为0选择IEEE half。
- [Rounding，M.b /A1.5.8](https://support.arm.com/documentation/ddi0487/mb/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A1-Introduction-to-the-Arm-Architecture/-A1-5-Floating-point-support/-A1-5-8-Rounding?lang=en#babdgead)：RN选择最近目的格式数，等距时选择最低有效位为偶数者。
- [精度转换，M.c /C3.8.4.1](https://support.arm.com/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point/-C3-8-4-Floating-point-conversion?lang=en)：scalar FCVT使用FPCR.RMode；不能与带固定舍入模式的浮点转整数指令混用。
- [FPSqrt，M.b /J1.4.353](https://support.arm.com/documentation/ddi0487/mb/-Part-J-Architectural-Pseudocode/-Chapter-J1-A-profile-Architecture-Pseudocode/-J1-4-Shared-pseudocode/-J1-4-353-FPSqrt)：正数普通路径在N=32时使用prec26的SqrtRounded，再把结果与fpcr传给FPRound。没有把阅读该函数当作完整嵌套伪代码或硬件符合性的独立证明。

以上页面标为Superseded，版本明确保留。架构符合性仍是前提；单个精确normal值不会证明全域运行精度。S32的2047值数学证书继续复用，本轮状态只绑定这一当前CPU原语边界，不升级通用bright或v4。

## 仅静态的powf下一断点

封存bright中的pow调用位于SSA82/98/107/157/166/248/249/258。IR中vector拆成三次scalar；两个half操作数扩为f32，调用`psr_pow_scalar`再转half。C源码写powf，但以机器码和Mach-O表为准：`0x15904`是tail branch到stub `0x16244`，该stub的indirect-symbol index136为`_powf`。反汇编的近邻符号注释指向无关的未定义符号，不能用它当导入身份。

首次静态收据的地址正则漏掉`0x`前缀，错误地报告stub unresolved；该收据保留。随后只重放同一已保存metadata，按整数地址解析定位正确行，并增加3项失败回归；没有再次执行静态工具或powf。正确闭环记录在`verification-s33.json`的`static_pow_followup`，完整表留私有。

**下一实际缺口**是运行时dyld解析的powf镜像/版本及具体输入相对half中点的误差。此处未执行powf、没有绑定它的FPCR，也没有用sqrt的奇偶性证书推断超越函数精度。cast16/多参数仍禁止，当前参数域不扩大。

## 验证与成本

13项FPCR报告/拒绝路径测试和3项保存stub解析测试通过，合计16项（unittest分别.027秒、.001秒）。覆盖错误ABI、线程查询失败/线程改变、FPCR改变、稳定非RN、0或多次调用、输入/输出位型损坏、公开成功标签不符、额外调用/MSR注入及已存在运行标记拒绝重入。测试和最终审计均不加载或调用原生代码。

新增成本为wrapper编译1次、封存f32原语调用1次；整kernel/helper/管线和powf调用0，原产物重新编译0。静态工具为wrapper反汇编1次、pow定向反汇编1次、Mach-O metadata1次；另1次工具`--help`只确认可用只读选项。没有以2047次运行替代数学证书。所有科学命令在执行前绑定源码/输入hash、结束后核一致；首次stub解析缺陷及历史失败均保留。

只读复核保存结果（不会再次调用原语）：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p test_fpcr_binding.py -v
python3 -m unittest discover -s research/styles-firmware-20261022 -p test_pow_stub_metadata.py -v
python3 research/styles-firmware-20261022/bound_validation.py --bind-input research/styles-firmware-20261022/fpcr_read_call.c s33-evidence-replay /tmp/psr-s33-binding-new.json python3 research/styles-firmware-20261022/verify_fpcr_binding.py /tmp/psr-s33-verification-new.json
```

输出路径须不存在。完整复核需要本任务私有封存产物；GitHub公开只含自写源码、哈希、合同和脱敏结果，没有Apple IR/二进制。不要再运行已完成的`fpcr_binding.py run`；其标记也会在原生加载前拒绝重入。

身份仍限定iPhone17,3 /iOS27.0.1 /24A446 /SmartStyleV1 /CMISmartStyleProcessorV1的CPU重编译研究，产品/内部/HEIC编号分开。v3的243份源码及S29–32证据不变。历史FPCR、原GPU/真实同帧、9字段缺缓存软件桥接、集合unknown、UI/IMG_2810 build和未知源成片逆解等缺口保留。没有下载/挂载固件、全盘找缓存、重试被拒ps、读取私人媒体或操作其他项目/系统安全预算。
