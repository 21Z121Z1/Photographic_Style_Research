# S21：活跃内部颜色控制的完整点前向与条件可辨识性

本轮只改变**场景缩放后的内部`SSRParams.color`，field3 / byte12 / f32**。它不是已校准的UI滑杆；其余原图、guide、mask、ROI、cast34、BG17/FG16/semantic7、统计、曲线、lookup和版本输入全部固定，没有重新生成UI耦合参数。沿用iPhone17,3 /iOS27.0.1 /24A446，内部SmartStyleV1 /CMISmartStyleProcessorV1；产品Styles2参考与内部编号、HEIC metadata版本分开。IMG_2810的iPhone19,2和精确build缺项不变。

## 一条已有局部证据的活跃控制

S14-C原`native-main-pre393-s14c.json`已覆盖正color的RichSat局部路径。`active_color.py`只接受明确的`np.float32`内部控制，替换原672B参数buffer的唯一field3；不接受Python double代替f32。原数据流是load356→half357，正值选择RichSat；half平方361和加1得到gain364，再按原保护量与person混合392。

模型先筛6个值：0、.01、.02、.03、.3、next-f32(.3)，保存在`color-screen-s21a.json`；随后只选0、.01、.02、.3及next-f32(.3)五个完整3×4合成上下文。原S15源文件hash固定为`ffae597c…0932b11`，新完整raw上下文在编译/原调用前持久化为`active-contexts-s21b.json`。没有使用保存的中间RGB或生成map作为输入oracle。

`color-contract-s21b.json`定向核原AIR7/AIR10的6条SSRParams指针作用域：producer、主入口、BW/haze/channel三个完整buffer消费者，以及channel内部的`getBWChannelMixFromStats`。所有原raw参数指针使用必须匹配已追GEP/转交；原color load356的唯一数值使用是half转换357。该审计限定在这些确切函数，不宣称9个未定位系数consumer已解决。

第一版审计未覆盖channel的两次嵌套BW stats转交，**以未追踪指针失败并停止，没有执行原宿主**；补出该子函数实际只读field0后再通过。失败pre/post/log原件保留在任务scratch，精简SHA/更正记录见`development-s21.json`，没有改成通过。

## 完整原AIR宿主点比较

`native_active_color.py`复用已有编译器、原AIR7 producer、三段guided、完整AIR10根与递归helper和原direct writer。只增加根ABI/观察stores，保留原算术/比较/FP属性；每像素重置参数buffer，使用原有显式CPU纹理/数学shim和单线程写出合同。不是原iOS/GPU运行。

五个上下文各自从raw source重新执行完整链，没有把上游相同当作外供map。每上下文6次producer、36×2次guided、12次带观察main/writer、12次无观察main/writer，合计**510次原kernel调用**，对应5个参数上下文，而非510个独立案例。所有原输出有限，带观察/无观察writer逐位差异0。原输出先落盘，再运行独立模型。

每上下文的**1938个已有half观察逐位差异0**，五个合计9690个分量；这仍是同一源图的有限参数家族。另独立观察原half357、gain364、protect384，不依赖最终混合掩盖内部行为。

|相对raw color=0|saturated374变化分量|output392变化分量|output600 / writer变化RGB分量|writer最大差|
|---|---:|---:|---:|---:|
|.01|0|0|0|0|
|.02|0|0|0|0|
|.3|36|36|35|.0078125|
|next-f32(.3)|36|36|35|.0078125|

因此`.3`的作用实际到达内部颜色处理、392和最终写出。这个点结果不能升级为集合域、其他cast/tuning、活跃UI风格或照片逆解通过。原始点输出、各中间观察、IR/C/source输入哈希及真实差异保存在`native-active-s21c.json`与`active-analysis-s21d.json`。

## 可区分、不可区分与未证

原图和全部辅助上下文已知时，本轮得到：

- **可区分**：raw0与raw.3在原宿主writer有35个half分量不同，其余不等参数对也逐项记录；这是有限见证，不是全域单调或唯一性证明。
- **不可区分的具体见证**：raw.01与raw.02转成不同的half控制，但gain364都为1，protect384相同，全部科学RGB中间输出和writer逐位相同。raw.3与它的下一个f32也逐位相同。
- **声明合同下的等价区间**：`.3`所在half为`.300048828125`，最近偶数转换的raw f32原像为`(.2999267578125,.3001708984375)`，两端均开，含8191个f32值。限定审计入口只消费同一half控制，所以该接口信息已经合并，不能逐一反推raw f32。
- **另一有界平台**：raw f32闭区间`[float32(.01),float32(.02)]`的half均为正，最大rounded square为`.0004000663757324219`；加1严格小于half的下一个中点`1.00048828125`，gain恒为1，保护max也恒选原`.2`。这是该内部指令/IEEE合同的有界接口等价论证，原宿主核了两端见证；不称已验证GPU精度或最大等价类。
- **未证**：等价类之外是否单射、其他参数/上下文、UI映射、原GPU、未知原图的成片逆解。有限差分、拟合或本轮精确点匹配均不能补上这些证明。

## 区间只辅助一个共源关系

新增可选`shared_semantic=True`，默认路径保持原设置。`semantic_shared.py`只保留precomputed315..335的同一reference196、各BG/FG gain分支、semantic权重与person96，按原half mix的减→乘→加、原min和乘积顺序逐步加原2u+tiny预算。`min(x,1)`不加下界clamp，也不改变epsilon、门限或mask。没有触碰FG contrast约.0200043的专用准入，更没有套用BG约.0299988域。

仅重放本轮color=.3的同一完整raw上下文：

|观察边界|独立盒最大宽|可选共源界最大宽|
|---|---:|---:|
|precomputed335 / semantic347|.57839683|.09057617|
|BG352 / FG354|.57839683|.09057617|

此前已知边界的集合均覆盖原宿主观察，但**两条活跃集合路径仍全部12像素在外围RichSat unknown，writer集合都未生成**。不能把提前停止后的内部unknown计数当作旧24个unknown减少。

`active-set-diagnostic-s21e.json`定位首像素下一失败：RichSat原`dot(pow(work),1/3)`均值外包络为`[0,.777062274813108]`，用于归一化的原除法含零。原clamp后的work外包络约`[0,0,0]..[1,.703125,.76855469]`，分子仍有限。零端点的联合可达性未证明，剩余关系在Lab/polar→work→power均值；没有给除数加epsilon、用中心兜底或用万级包络换取后续可执行。

## 运行与保留限制

230项测试通过，新增10项覆盖内部类型/单字段修改、half等价区间两端偶数规则、完整调用和非零作用、不同half控制碰撞、共源min不加clamp、opt-in集合失败保留、显式输入变更的预绑定失败，以及测试自身运行前hash。`bound_validation.py`现可用`--bind-input`绑定已有AIR等显式文件；本轮原宿主运行前绑定5个原AIR、全部源码和raw上下文/筛选输入，运行后检查未变。S19历史source hash/mtime限制仍原样保留。

仓库根复验：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
```

全部命令、pre/post清单和收据SHA见`evidence/verification-s21.json`。原宿主重编译另需本机既有5个匹配AIR和既有LLVM；完整参数见`native-binding-s21c.pre.json`，无需下载固件。原始固件/专有二进制不入Git。

旧中性12个selective+24个内部unknown、旧24组合/8叶域unknown、FG contrast失败、9字段CPU桥接缺缓存断点、tuning field17/byte652失败回归及既有非唯一逆证书均保留。未新下载/挂载/查找缓存，未读取私人媒体或重试被拒ps，未触碰Metal/XD或安全预算。原GPU、真实同帧辅助输入、IMG_2810 build和照片逆解仍未验收。
