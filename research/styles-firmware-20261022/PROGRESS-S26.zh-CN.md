# S26：同v3精度的两场景目录与保存bright137局部修正

本轮先用已接受v3重放第一场景的13个已有有限宿主输出，全部25194个half观察逐位差异0；随后**实际重新计算**第一场景146状态目录。与第二场景使用同一精度比较后，第一场景有140个不同writer、第二场景145个，9个状态的等价类成员改变。新增原kernel调用**0**，没有重新执行旧8边界、扩域或多参数搜索。

同精度模型目录可比不等于原GPU、完整拍摄或未知源照片逆解通过。新增碰撞组仍没有对应原宿主穷尽；两个场景的源图及显式辅助输入共同改变，不能归因于单独某一颜色或亮度因素。

## 先有限宿主保存值重放，再重建目录

身份仍为iPhone17,3 /iOS27.0.1 /24A446，内部SmartStyleV1 /CMISmartStyleProcessorV1；产品代际、内部版本、HEIC编号分开，ABI的main version0不作HEIC版本0解释。

精度文件没有修改：`model-precision-v3-s25c6.json`，SHA256 `9358741644914631950a72161b25967ba9c433400d1faf3dbb4267db1fb036da`。API源码、243份模型源码及宿主数学profile仍与该合同一致，包括最终code3的powf f32→half、分别half乘/加。没有把bright局部修正塞入此版本。

`same_precision_scenes.py replay`读取原SHA核验后的S21五个控制与S24八个边界，合计13个不同raw f32、六个接口状态。每个从第一场景冻结源图和辅助输入重新执行完整**模型**前向，与保存的producer/guided/main/writer观察比较，没有运行原AIR。全部25194分量位差0、writer/点域unknown0；实际模型重放4.819847秒。它只延续这13个有限保存见证，不增加原宿主状态覆盖。

通过该门禁后，复用既有half分区和接口关系，执行10批共146次新完整模型前向，不读目标writer，writer unknown0、无缺失或重复状态。模型扫描合计55.172357秒；未重新枚举half端点，没有用旧候选区间代替计算。

新第一场景目录为`first-context-catalog-v3-s26c.json`，SHA `6c49f76d35aef61b1c6c4bf432aa5d24e72b343e6e15fe9f351914e80a29b6ce`，引用新的`scan-*-s26b.json`。第二场景继续使用原S25 v3目录SHA `5e943c91fe441c55c4fd9bd023daf74cbe5db3afbe4365b5cdc727960bfe5ba6`。两者完整上下文SHA分别为`ffae597ca79f92447a2bdae45bbc007450be27ae9165bef78d0e6b3cb0932b11`和`37d3385222f3f42988d79dbbe5db89c3147c6988f5c0b7ef9ff10bab97031be6`，不能互换。

新第一场景146个writer与S22旧目录的全部uint16数组恰好逐位相同，旧目录仍未改标签。这个有限上下文的输出一致，不能推成旧/新精度模块全等或其他上下文兼容；S25目标B已留下反例。新目录有实际前向计数、计时及完整新身份，不能因为结果相同就免做重建。

## 同精度类成员与候选集合

`same-precision-comparison-s26c.json`比较全部146类和全部跨状态精确writer碰撞对，不只比较少量目标，也不假定writer单调。两个场景同state的writer数组146/146都不同，但每个场景内的等价类可直接按共同接口状态比较：

|项|第一场景v3|第二场景v3|
|---|---|---|
|不同writer数|140|145|
|跨接口碰撞组|`[0,1] [4,5] [7,8,9] [31,32] [71,72]`|`[0,1]`|
|碰撞状态对数|7|1|

状态4/5/7/8/9/31/32/71/72共9类的成员改变；第一→第二去掉6个碰撞对，没有新增对。状态0/1的碰撞仍存在。以下API查询均使用该场景自己的state writer作显式目标，在同一canonical `[+0,3/8]`域返回全部精确模型匹配，未输入真实控制：

|目标state|第一场景匹配类 /f32人口|第二场景匹配类 /f32人口|
|---|---|---|
|4|4/5，4022273|4，2424832|
|7|7/8/9，2400255|7，860159|
|31|31/32，376832|31，188415|
|71|71/72，131072|71，65536|

例如state7的第一场景候选为开区间`(.073272705078125,.091156005859375)`，raw `0x3d961001..0x3dbaafff`；第二场景为开区间`(.073272705078125,.079681396484375)`，raw `0x3d961001..0x3da32fff`。没有任选中心点或声称唯一参数。所选17/93/122类也另列，不能把某些类未变扩大成全部不变。

`changed-class-queries-s26c2.json`保存完整候选端点/人口及旧新目录逐位比较。API在两个方向都拒绝错上下文target；测试还交换实际context文件验证目录拒绝。未知/缺失state的既有语义不变，不作为排除证据。

## S25文字勘误

S25报告曾把旧场景误写成145个writer、仅`[0,1]`碰撞。原`context-analysis-s25e.json`一直正确记录**140及5组**，本轮未修改它或其他S25原收据。S25文字已明确更正；旧历史提交保留。这不是v3产生了新碰撞，也不是本轮修改旧数据得到的结论。同v3的新目录重建消除了当时未检验的精度混杂，确认当前两个条件上下文的类成员差异。

## bright：只修正已认证输入的SSA137节点

`bright137_witness.py`只读取SHA `825f669b…3353a`的既有S25诊断，绑定第二场景、保存像素[0,1]及SSA132/135精确half3操作数。此前SSA132..136检查点相同；原SSA137为`[16889,16417,16630]`，逐步乘后加模型为`[16889,16418,16630]`。局部一次舍入乘加从输入重新计算，137处位差由1降为0。

这不是把整bright改成FMA：新算子不接入`pixel_bright`或v3，拒绝相邻half输入、set/f32、错误shape或未认证证据。它只给该保存操作数域的节点修正，不认证新caller、邻域、后续节点或完整bright。没有回放其余残差像素，S25目标6个及边界18个bright位差继续完整保留。

`require_inverse_scope`在本轮两个场景的类查询前明确要求cast0、唯一自由字段3；cast16和多自由参数拒绝。原Context也拒绝cast16。本轮不新增这些调用域的入口，不能用当前cast0 writer不受影响来隐去bright缺口。

## 测试、成本与保留范围

14项定向测试通过，unittest0.146秒，覆盖两目录同精度/不同context、全部类变化、候选人口/开闭端点、旧新writer实际相同、双向context文件与target拒绝、SSA137局部修正及域外负例、cast16/多参数禁止、v3源码与旧成本限制未变。未重跑旧246项或再次执行旧8个原边界。

本轮精确新增完整模型前向**159次=13保存重放+146新目录**，其他比较/查询及SSA137节点运算不计作完整前向。新增原kernel、编译、下载均0。S25失败v2的完整点成本**162–163**及原源码快照限制保持，不追溯生成精确计数。每次新命令执行前绑定源码/输入SHA，执行后均未变；最终收据为`verification-s26.json`。

仓库根复验（输出必须不存在；前两条命令不增加完整前向或原kernel）：

```sh
python3 research/styles-firmware-20261022/same_precision_scenes.py compare \
  research/styles-firmware-20261022/evidence/complete-context-s15a.json \
  research/styles-firmware-20261022/evidence/second-context-s25a.json \
  research/styles-firmware-20261022/evidence/model-precision-v3-s25c6.json \
  research/styles-firmware-20261022/evidence/color-partition-s22a.json \
  research/styles-firmware-20261022/evidence/first-context-catalog-v3-s26c.json \
  research/styles-firmware-20261022/evidence/context-catalog-s25e.json \
  research/styles-firmware-20261022/evidence/first-scene-v3-replay-s26a.json /tmp/psr-s26-compare-new.json
python3 research/styles-firmware-20261022/bright137_witness.py \
  research/styles-firmware-20261022/evidence/bright-detail-s25c.json /tmp/psr-bright137-new.json
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_same_precision_scenes.py' -v
```

每场景仍只有六类有限原宿主见证，其余140类未宿主穷尽，不能跨场景合并计数。集合unknown、9字段缺缓存软件断点、历史S21/S22 IR原因未知、原GPU/真实同帧、UI、IMG_2810精确build、未知源成片逆解及S19恢复审计限制继续保留。本轮只读现有合成数据，未找缓存、私人媒体、重试被拒ps或触碰其他项目/安全预算。
