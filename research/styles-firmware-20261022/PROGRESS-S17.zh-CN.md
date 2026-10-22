# S17：selective联合误差、保存bright残差和BG cell0

沿用S15的同一个3×4合成上下文，SHA256 `ffae597ca79f92447a2bdae45bbc007450be27ae9165bef78d0e6b3cb0932b11`；仍限cast0、tuning2、中性BG/FG、零lookup。参考身份是iPhone17,3 / iOS27.0.1 /24A446，产品Styles2参考与内部SmartStyleV1 /CMISmartStyleProcessorV1分开。IMG_2810的iPhone19,2、Styles16、TextureStylePeopleDataVersion3仍属另一身份链，精确capture build未核验。

本轮只新增**两个保存像素的2次原AIR完整主入口宿主诊断调用**，使用已有宿主数学/采样shim与保存guided输出；不算新的完整producer链运行。没有新增叶输入案例、上下文、原GPU执行、私人媒体或下载，没有重跑S15的102次调用批次。1938个观察分量不是1938个独立案例。

## 先定位一个selective像素，再重放原12像素

`selective-baseline-s17a.json`保留原集合图，首像素(0,0)的warm409输入宽约1.73493，经**原SSA11输入clamp**覆盖整个[0,1]³。M的三行共享RGB，原盒表示在分别计算LMS/root后没有保留三者联合关系；到含正负系数的Lab矩阵N时，相消依赖首次明显丢失，a宽9.703125。后续独立极坐标重建、再次Lab混合和逆幂继续放大。

|首像素边界|原独立盒最大宽|本轮联合包络最大宽|
|---|---:|---:|
|Lab|9.703125|保留原诊断盒；联合证明另持共享变量|
|basic极坐标重建|10.254995|同上|
|changed Lab|19.166216|同上|
|inverse_v|15.47496|1.0874501|
|inverse_root|269.87537|1.2152439|
|converted half RGB|587（R约±293.5）|1.88427734375|
|gamma|.01082108（约.994589..1.005411）|0，值精确为1|

`color_matrices.py`让点模型与误差证明共享字面常数；`color-constant-links-s17a.json`核同一已取得AIR10的13组SSA常数（含两次幂指数），全部一致，保留函数、原指令和模块哈希。这里使用该build的工作域矩阵，不给它猜命名ICC空间。

`selective_neutral_joint.Inputs`只接受有限half整盒RGB、三个整盒mask、显式4×360 RGBA零lookup、三个零offset、零amplitude和零output_mix；非零参数不套此证明。零纹理采样与同值混合使saturation/luminosity/gamma精确为1、hue为0；mask保持原范围，不换中心。零权重后的Lab向量保持同一活变量。新的联合界不读取原生中间输出来替代模型输入。

实数参考保持 `z=Mx; u=z^p; L=Nu; v=PL; converted=Q·signedPow(v,q)` 的共同来源。仅在**误差证明**中组成P·N和Q·M；原矩阵每步f32舍入、half量化、极坐标往返和p·q≠1的残差均单列。p·q约.999999980871，未当作精确逆。原f32/half算术2u、超越函数4u、tiny、half转换预算保留；f64记账另向外扩。最终Q·M映射沿用整个RGB盒的共享生成元，常数项不是输入替代值。

`selective-one-pixel-s17a.json`记录(0,0)一次原helper宿主观察，12个f32和21个half探针共33分量逐位差异0；inverse_v、inverse_root、converted、gamma的原观察均在联合包络内，selective413与output600观察器稳定。该点检查支持保存见证，**不能单独证明整个输入域**；整盒覆盖论证来自上述解析界，且以声明的宿主舍入/数学预算为条件，未做形式化全参数或GPU证明。

converted首像素包络为R[-.44189453125,1.4423828125]、G[-.15576171875,1.1552734375]、B[-.134521484375,1.134765625]。负端点仍没有联合可达性证明。没有clamp pow底数、改变原输入域或给后端pow补界；原`V.pow`仍对这个负外包络返回unknown，即使gamma为1也没有放宽成整数指数捷径。

先完成上述单像素论证和观察，再运行`selective-replay-s17a.json`的原12像素纯模型重放：已知前缀范围继续覆盖保存宿主值，converted最大宽587→1.88428、gamma全部精确1；**12个像素仍首次unknown于selective413，未选highlight/bright内部仍24个unknown，writer集合仍不存在**。最小未决表达式仍是`converted.pow(1)`在含负端点的外包络上的定义域。负端点可能来自量化/极坐标误差的独立余界，也可能包含真实边缘负值，当前证据不能择一。宽度收紧不等于数值吻合。

## bright：保存像素的首次差异

`bright-residual-pixel-s17b.json`只观察剩余差异所在的保存像素(1,0)。已探mixture126、square132、delta145在首次分歧前均一致；第一个有差异的已探边界是SSA150，三个half中1个位差：native `[14569,14487,14473]`，旧模型 `[14569,14488,14473]`，max误差.00048828125。

AIR原图的146/147计算`2*mixture-1`，148乘delta，149加square，150饱和；148/149带fast属性，宿主允许收缩。原150值严格在(0,1)，饱和未激活，因此保存150同时给出149的目标。仅把该处建成`fma_half(delta, 2*mixture-1, square)`即逐位匹配此目标，符合宿主的收缩合同。没有把AIR的fadd描述成显式GPU FMA指令，也未先归因libm。这个限定修正不改变output600 transfer的encode合同。

随后以保存原始bits纯重放同一完整条件链：**1938个half观察差异0**，包括独立335、392、bright400、tonal468、477、567、600与最终writer120。该结论仅覆盖一个保存上下文；没有因最终混合相同就忽略内部结果。S16全局改变encode导致18个600/writer差异的负例、tuning field17 /byte652包装错误及历史失败收据继续保留，其他上下文的历史差异未升级通过。

## BG只处理cell0的newspan/span关联

`contrast_span_joint.py`只对保存cell0另建局部界，**未接入默认BG/FG，也不改记完整BG通过**。半精度正分支门限仍是原f32约1e-5，最小可取half span为1.0013580322265625e-5；原else分支保留。

令D为同一RGB的实数max−min，σ为原half减法得到的span。保存的共同标量、sqrt Hölder界和原舍入误差给出：

`spread(changed) ≤ D + A√D + B`，A约4.91000227436，B约.05534556221；

`D ≤ (σ+tiny)/(1−2u)`。

代回后D/σ、√D/σ与1/σ在正分支递减，先于后续乘法证明**原half商**有界：raw≤7091.97955，计商舍入后≤7098.90531，低于65504。再用同一通道的`half(rgb_i−minRGB)/σ`关联界及newspan自身的范围界，得到原乘法≤1.67755948，最终RGB整盒最大宽约**1.68080284096**，含原else并集。没有先归一化、代数重排half商乘顺序、改门限或缩mask。`bg-cell0-joint-s17c.json`保存全部常数、范围和原失败收据哈希；Decimal高精度只检查标量误差链，不生成新叶案例。

这是声明预算下cell0局部contrast表达式的条件解析包络，不是原GPU、全部BG叶或全参数形式化证明。默认BG模型的历史cell0 unknown仍在；后续接线及组合验收是软件未完项。旧8个叶域unknown、24个全激活组合unknown和155.125/17941.5513历史宽包络均不改记通过。

## 证据分类与剩余项

`unresolved-software-s17.json`更正S16把9个消费者列入external dependency的分类：BG airy、warmthMatch四分量、bgGlobalMix，FG airy、faceI/faceQ，SSRParams byte512/536/540/544/548/552/560/604/608，均是**未完成软件追踪**。此处只核先前映射并改分类，没有重复215资源同范围扫描，也没有称unused。未覆盖的无类型指针、拷贝/别名和其他consumer仍可继续静态追踪，不必等待硬件。

|结论|最低证据|本轮状态|
|---|---|---|
|保存上下文点模型|原宿主bits与独立中间观察|1938 half差异0；2次定向宿主诊断，范围受限|
|neutral selective局部整盒|共享变量解析误差界及保存点覆盖|converted/gamma已收紧；pow域未决|
|完整ROI集合链|每个算子定义域及输出覆盖|12+24 unknown；无writer集合|
|BG cell0|原商先有限、再界乘法与else|局部界已给出；默认BG接线/组合未验|
|原iOS/GPU、真实照片与逆解|匹配设备/build/同帧辅助上下文及原GPU运行|未完成；合成宿主结果不能替代|

还需软件工作：selective底数的可达性/更紧联合域、未选内部域、cell0局部界接线及完整BG集合、9消费者剩余静态追踪。实际运行验收另需原iOS/GPU、同帧source/guide/ROI、人物mask、统计、曲线、lookup、34值cast及完整系数；当前均显式供给，未从成片恢复。IMG_2810还缺精确build及匹配iPhone19,2链。S20同观测但不同中和结果的非唯一证书保留，不承诺恢复丢失纹理或唯一照片逆。

## 复验

仓库根目录，Python3与NumPy；纯模型命令不编译或调用原AIR：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/replay_selective_joint.py \
  research/styles-firmware-20261022/evidence/complete-context-s15a.json \
  research/styles-firmware-20261022/evidence/native-complete-s15a.json \
  research/styles-firmware-20261022/evidence/selective-baseline-s17a.json \
  research/styles-firmware-20261022/evidence/selective-one-pixel-s17a.json \
  /tmp/psr-selective-s17-replay-new.json
```

实际198项测试通过；包含原样本配对SHA拒绝、非零控制拒绝、负底数unknown、独立原helper目标、cell0原商乘顺序与else、9消费者分类。输出文件必须不存在。原AIR诊断复验入口是`native_selective_pixel.py`与`diagnose_internal_pixel.py`，需要已取得的私有缓存`../air-cmi-compare/ios/0010.ll.txt`、本机ARM64 clang和显式宿主shim；没有把这些原文件或编译二进制提交Git。静态覆盖清单及精确源码/收据/测试日志哈希见`evidence/pixel-inventory-s17.json`、`evidence/verification-s17.json`。
