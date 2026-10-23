# S30：从源图重算上游，连接独立bright精度版本

在同一冻结合成context中，以三个既有field3控制重算 **source→producer→guided→主入口**。上游模型输出逐位命中S29四组完整bright认证输入；新helper的每组52个保存检查点吻合。三帧各1938个保存观察分量（共5814）均无half位差，最终writer各120half亦一致。**没有用宿主中间数组补值或作为像素运行输入。**

这补齐四组已知输入的source→bright模型组合证据。cast0的实际selected404来自skin393，不选择bright400；因此writer一致只验证实际skin分支，**不是bright被选入writer的证明**。未解禁cast16/多参数，也未提升为通用v4或原GPU认证。

## 冻结目标与独立实验版本

`connected-bright-plan-s30a.json`在执行前固定：沿S29残差row顺序，第一次遇到每个完整输入指纹时选取该控制和坐标，不根据本轮结果挑点。恰好三个控制覆盖四个不同输入：

|控制；raw f32位型|认证坐标[x,y]|完整输入指纹前缀|
|---|---|---|
|target_A；1040187392|[0,1]、[2,1]|493b9b2a91a8、a21d240af44e|
|boundary-0；1039921151|[0,1]|10c7aad9aff3|
|boundary-3；1040322561|[2,1]|5a53a0bdab43|

context仍为 `second-context-s25a.json`，SHA `37d3385222f3f42988d79dbbe5db89c3147c6988f5c0b7ef9ff10bab97031be6`。身份为iPhone17,3 /iOS27.0.1 /24A446、SmartStyleV1 /CMISmartStyleProcessorV1；产品、内部class/bundle与HEIC编号不混同。仅cast0/tuning2、既有内部field3域，其他参数和辅助输入固定。原图在本实验指明确供给的合成source/linear，不指从照片恢复的无风格原图。

独立实验 `source-connected-bright-s30-four-approved-sites-point-v1` 不改原v3。`connected_bright.py`复制原complete_forward函数的AST/globals，只替换唯一bright调用，并传入当前坐标。四个目标站点必须命中原S29精确输入白名单；其余32次bright调用保持原v3。全局原函数、v3源码和目录均未改。

## 模型运行输入与预期比较分开

`source_run`只读取冻结context的source、linear、显式辅助纹理及原始ABI参数/统计/曲线，替换既有field3控制后，从头计算producer、guided和主入口。没有接受生成BG/FG图、working286、skin393、person96或skin95数组的参数接口。

bright运行操作数来自当前模型的 `skin393`、`working286`、`person96`、`skin95`、曝光和五个f32 stats。每组完整指纹包含9个half及5个f32分量，本轮全部与S29认证值逐位相同，差异列表为空；没有转换为近似邻域或数值容差后放行。

S29内部仍读取旧证据做身份和白名单预期比较；这些数组只用于检查，FMA的操作数来自传入的模型V值。测试拦截 `bright_saved_replay.arguments`、`Saved137.apply`和原生库加载后，模型tuple仍能通过独立helper；未调用旧native参数构造器或用其操作数代入。

三个模型全部完成、输出数组已序列化后，比较阶段才读取S25整帧宿主参考。逐个核对producer/guided观察、原主入口中间结果、bright及output600/writer。参考数组没有回传给模型，没有用比较结果修补后重新运行。

## 结果与实际writer路径

|控制|完整认证输入数|bright保存检查点差异|全部1938分量位差|writer位差|point unknown|
|---|---:|---:|---:|---:|---:|
|target_A|2|0|0|0|0|
|boundary-0|1|0|0|0|0|
|boundary-3|1|0|0|0|0|

四组source→helper没有出现新的首差；所有保存观察的首个分歧均为空。helper内部共208个检查点比较，包含原f32检查点；完整帧5814个比较分量按宿主保存的half观察合同核对。完整输入指纹及每个模型观察数组均保存，不能将这些计数解释成独立场景数或任意输入域证明。

原cast0模型明确执行 `selected404=skin393`。bright400作为内部观察完成，但其输出不进入该writer路径。当前结果应分别读取为：四组source→bright组合通过；原cast0 source→skin→后续→writer的模型观察与旧CPU结果一致。没有新增一条允许bright影响writer的分支，也没有原GPU端到端执行。

## 拒绝合同与测试

若目标输入指纹不吻合，Dispatch记录真实模型输入、差异字段与位型索引，抛出unknown；**目标站点没有退回v3，也没有native补值**。即使cast0的独立writer分支继续生成，组合状态仍必须失败。

10项定向测试通过（unittest .045秒）：四组完整输入、52检查点、5814分量、原writer选择、源码与旧证据身份，以及相邻half、错误context/控制和无副作用克隆等边界。相邻输入在算术前拒绝，测试同时禁止目标profile计算和v3 fallback。另一个明确标为mock的失败fixture让writer存在但目标拒绝，验证状态仍是失败；它不是新真实图像或原生见证。

本轮没有实际源图重放失败，故无失败像素传播可归因；保存上述负例用于回归，不把它们计为真实上游失配。原S29失败源码/常量修正记录和旧v3残差保持原样。

新增完整模型重放 **3次**，内含36次bright helper（4次原S29独立profile、32次原v3）；测试另有1次helper回放、1次mock管线fixture，**没有追加完整模型重放**。审计只核保存结果。新增原CPU宿主/GPU调用、原生编译均为0；未重复S29的三次原调用或旧批次。

复验已有结果：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p test_connected_bright.py -v
python3 research/styles-firmware-20261022/bound_validation.py s30-evidence-replay /tmp/psr-s30-binding-new.json python3 research/styles-firmware-20261022/verify_connected_bright.py /tmp/psr-s30-verification-new.json
```

输出路径须不存在。机器结果为 `connected-bright-result-s30b.json`，最终收据为 `verification-s30.json`，均在evidence下；source/输入执行前后SHA一致。复验命令不重新运行完整管线或原kernel。

## 未验证项

结论仅限同一冻结合成context的三个raw控制、四个认证输入和point精度。S29完整profile仍是四组精确tuple；square叶的RN假设、未测FPCR、未观察SSA、任意bright调用域尚未认证。v3与历史失败不改，cast16/多参数仍禁入。

原GPU、真实同帧、UI映射、IMG_2810精确build、未知源成片逆解，旧集合unknown、9字段缺缓存软件桥接及历史IR原因等缺口保留。统计、lookup、guide/mask等辅助条件仍外供。本轮未下载或挂载、搜索缓存、读取私人媒体、重试被拒ps、操作Metal/XD或更改安全和预算。
