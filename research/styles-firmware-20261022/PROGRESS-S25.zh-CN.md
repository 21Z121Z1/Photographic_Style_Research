# S25：第二个冻结场景、绑定目录API与活跃控制反求

本轮在**第二个预先冻结的合成场景**中重新计算146状态writer目录，再用两个预选原宿主目标作盲查询。真实控制均包含在返回的多解集合中，8个必要新边界与原宿主writer逐half位一致。没有扩大canonical非负f32的`[+0,3/8]`域，也没有移植旧候选区间或重跑旧8边界。

这一结果属于**已知源图、全部辅助上下文已知、指定宿主点精度**的条件反求。内部bright仍有真实位差；两个合成场景不证明任意场景可逆，也不解除原GPU/UI、未知源成片逆解或集合unknown。

## 在输出之前冻结场景与控制

`second_scene_fixture.py`写定3×4冷暖色块与非单调亮度，再用固定公式生成显式linear、guide、matte、guide8/9、person/skin/sky。其余672B参数、raw stats、CCM/SRL、GTC/whites、ROI、2×3 producer网格、5×6 RGBA输出存储、零lookup等完整列在上下文中。这些辅助输入仍是外供条件，没有从成片恢复，没有将linear称为无风格原图。

`second-context-s25a.json` SHA256：`37d3385222f3f42988d79dbbe5db89c3147c6988f5c0b7ef9ff10bab97031be6`。`scene-selection-s25a.json`在任何第二场景前向/宿主调用之前固定目标A raw0.125、B raw0.34375，以及后续边界选择规则。没有根据最终匹配选择或更换图片、目标或辅助输入。

身份保持iPhone17,3 /iOS27.0.1 /24A446，内部SmartStyleV1 /CMISmartStyleProcessorV1。产品Styles2、内部V1及HEIC metadata编号分开；API中的`main_version_argument=0`是该调用ABI参数，**不是HEIC metadata版本0**。没有继承IMG_2810 build或纹理样张链路。

## 先保留并定位真实失败

|步骤|实际发现|处理|
|---|---|---|
|目标A首轮整观察比较|102次原kernel后，bright400有6个half位差，max0.0001220703125；writer及其他观察一致|原整观察验收保持失败|
|同一保存像素[0,1]的两次逐步诊断|首个已观察算术分歧为bright SSA137；其前检查点一致，一次舍入乘加候选吻合|没有把全部bright误差归于同一原因或改为通过|
|目标B原宿主|另102次；output600和writer同一个分量差1个half步长，max0.0001220703125|停止，未最近值兜底|
|同一保存像素[2,1]最终transfer诊断|SSA11/12一致，首差SSA13：原powf→f32→half为12410，double直接→half为12411|明确最终code3点精度合同|
|尝试最终offset FMA的v2合同|重放A/B分别出现12/13个writer位差|假设被拒，原失败与debug输出保留|
|v3合同|system powf返回f32，再转half；SSA14乘和SSA15加分别half舍入|保存的A/B所选路径重放位差0；不改预算、epsilon、clamp或输入域|

原transfer的实际SSA14/15检查点支持**分别舍入**；同一像素的FMA候选不能替代它。`output_code3.py`只改变最终code3的宿主**点**后端，`pixel_output.py`显式接入；其他transfer入口及集合后端继续使用原实现。它采用同一Darwin arm64系统`powf`数学ABI，合同绑定运行profile及源码，不是Apple GPU数学精度证明。没有将旧目录重新标为新精度通过。

实际保存的主入口中，SSA245两条phi输入都读取原cast字段0，只有cast16才令SSA404选bright400；本场景cast0选择skin393，bright结果的其他用途仅为隔离观察写出。`selection_proof`记录实际文件指令hash与首差诊断。因而可继续验**所选writer路径**，同时把bright作为未通过的内部数值模型保留；不宣称整模型逐位吻合。目标A和8边界分别保留6、18个bright分量位差。

三项数值验收失败的pre/post、原始日志SHA和调试结果保留；汇总审计首次另有纯语法错误，发生在执行前、0模型/原kernel调用，后用h2命令修正。4份原始失败日志完整移入任务私有`s25-validation-logs/`，Git只放脱敏输出，映射见`raw-log-storage-s25h3.json`。v2模型假设有源码pre-hash而无独立原源码快照，不把它当持久历史原件；当前接受的v3源码已提交，并在边界phase私有快照中保存。

## 第二场景自己的146状态目录

复用S22已核SHA的13825个half单元、146个branch/gain/protect接口类和覆盖证明，不重新枚举55298端点检查。仅对新场景独立执行146次完整条件点前向，分10批、每批至多16状态，writer unknown0、无缺失/重复状态。扫描代码不读取目标writer；模型扫描计时合计**53.950133750秒**，其他编译/哈希/诊断时间另列。

接受的精度文件为`model-precision-v3-s25c6.json`，SHA `9358741644914631950a72161b25967ba9c433400d1faf3dbb4267db1fb036da`。目录为`context-catalog-s25e.json`，SHA `5e943c91fe441c55c4fd9bd023daf74cbe5db3afbe4365b5cdc727960bfe5ba6`。完整上下文、build/内部class/ABI版本、243份模型源码、API源码、宿主数学profile、原AIR/field3合同、partition和各chunk SHA相连。

旧S22目录保持旧精度身份；本轮修改了最终code3点实现，不能再声称旧目录的源码身份在当前代码下全都未变。两场景的碰撞组比较为历史描述，**不是消除精度差异后的纯场景因果实验**。

## 盲查询与必要边界

`blind-target-A/B-s25e.json`只含绑定身份、目录hash和完整uint16 writer数组，不含真实raw控制。`BoundCatalog.query(Target(...))`不接收真实控制；查询完成后，独立步骤才读取冻结selection核包含性并选边界。

|原宿主目标|完整模型匹配区间|含端点raw f32位型|人口/状态|
|---|---|---|---|
|A：0.125|`[.123016357421875,.12701416015625]`|`0x3dfbf000..0x3e021000`|401409 /17|
|B：0.34375|`[.3431396484375,.3443603515625]`|`0x3eafb000..0x3eb05000`|40961 /122|

两目标都包含真实控制且明确多解。与本场景state0 writer相比，A/B分别改变34/36个half分量，不能以平坦全无作用冒充活跃控制。模型目录共有145个不同writer，唯一跨接口碰撞组为`[0,1]`。旧场景历史目录同样有145个writer及`[0,1]`碰撞；对同接口状态17/122，其历史writer的等价类也分别为17/122。本轮**未观察到这些类随场景改变**，没有假造“泛化变窄”结论，也不以两个场景推断其他场景仍相同或唯一。

按预冻结规则各取候选并集首/末包含f32及紧邻域内排除值，共8个新值，与旧S22八边界及两目标raw值均不重合。新原宿主再生成一次78调用前缀，8控制各24次观察/plain main，共270次；前缀与本轮首个原输出位型相同。所有writer与对应新目录完整数组逐位相同；A/B端点包含及两侧相邻排除全部符合模型预期。原half357/gain364/protect384也与逻辑接口键一致。

两个目标的v3保存输出重放及8个新边界，所选路径逐half位差0；bright未选差异另外保留。新场景只有state16/17/18/121/122/123六类有有限宿主见证，**其余140类没有宿主穷尽**，不能与旧场景另外六类跨上下文合并计数。

## 可复用API与拒绝合同

`context_color_api.py`提供强类型`Identity`、只读拷贝`Target`和`BoundCatalog`。每次查询复核上下文完整bytes SHA、版本/模型/API精度身份、目录SHA、chunk SHA、代表值/接口键和writer digest。错误上下文（包括单个stats bit）、错误build/target身份、旧/被拒精度合同、错误目录hash、篡改chunk、重复state、非uint16/非有限目标均拒绝。未绑定新schema的旧S22目录不能自动混入本API。

部分目录允许查询，但`missing_state_ids`和`unknown_state_ids`保留，并给`unresolved_possible_union`；它们不能作为排除证据。不匹配目标返回空精确候选，不返回最近值，也不输出伪唯一控制。

仓库根重放盲查询，无新前向或宿主调用；输出路径必须不存在：

```sh
python3 research/styles-firmware-20261022/context_inverse_workflow.py solve \
  research/styles-firmware-20261022/evidence/second-context-s25a.json \
  research/styles-firmware-20261022/evidence/model-precision-v3-s25c6.json \
  research/styles-firmware-20261022/evidence/color-partition-s22a.json \
  research/styles-firmware-20261022/evidence/context-catalog-s25e.json \
  research/styles-firmware-20261022/evidence/blind-target-A-s25e.json /tmp/psr-s25-query-new.json

python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_context_color_api.py' -v
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_pixel_output.py' -v
```

20项新API/精度测试通过，0.183秒；4项既有输出算子回归通过，0.027秒。未重跑旧246项或新增孤立叶批次。测试含unknown/缺失不得排除、错上下文拒绝、无最近值兜底、真实tie与被拒FMA回归、原失败不改写。

## 持久证据、成本及未完成范围

实际新5段host IR、plain main及C shim在编译前封存，三个单像素诊断各自的实际trace IR/shim同样先保存再编译。7份原主链输入及其产物随后按SHA复用，没有因模型修正重编译或重跑原目标。4个新私有archive及phase约13.83MB，均在Git外；每根64MiB上限、2GiB预留。实际编译器、参数、输入AIR、源码快照、上下文、产物、日志和前后proof均保留，h2/h3审计再次核其身份。Git不含专有IR/AIR或dylib。

原kernel调用精确总数**477**：A102、B102、三个单像素诊断3、新边界270；不是477个独立场景。完整点前向有161次直接记录，另被拒v2失败命令没有运行时逐state计数，范围1..2次（源码/后续debug指向首个A失败，不能冒充实测counter）；因此全点成本保留为**162..163**，不伪造无歧义精确总数。146次新目录计算和8次新边界点计算分别可直接核验；两个bright诊断另有同一保存像素定位中的小型helper重放，未计作完整前向。

`stage-audit-s25h2.json`、`private-product-audit-s25h3.json`与最终`verification-s25.json`给完整hash、失败、调用及范围证据。下一软件缺口仍有未选bright的泛化数值模型和原有集合unknown；未假称硬件阻塞。9字段缺缓存的CPU桥接继续暂停。历史S21/S22 IR差异原因仍未知；原GPU、真实同帧、UI校准、IMG_2810精确build、未知源成片逆解及S19恢复审计限制全部保留。本轮没有新下载、挂载、找缓存、私人媒体、被拒ps重试或其他项目/安全预算操作。
