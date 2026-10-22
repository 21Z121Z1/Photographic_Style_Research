# 本目录S20：完整共享颜色传播与whites原乘积/商

只重放S15冻结3×4合成上下文的12个像素，以及辅助的原S14-C case0。新增原AIR宿主调用0，GPU调用0，下载/挂载/私人媒体0；9字段CPU桥接按S18断点暂停，没有查找缺失缓存。身份仍为iPhone17,3 /iOS27.0.1 /24A446、内部SmartStyleV1 /CMISmartStyleProcessorV1，产品Styles2参考另列；IMG_2810的iPhone19,2与精确build缺项不变。本文是本目录的阶段S20；既有semantic-styles S20非唯一证书保持原范围。

## 先核实际精度与调用合同

`color-joint-contract-s20a.json`核精确AIR10，smoothSat函数SHA `5163cdebd82f65a95aa8307c0e526c38db38e8e9ce0e174bb8c03997a901e065`。13组原SSA字面常数与共享M/N/P/Q及两次指数全部一致：矩阵与幂为f32，Lab25、极坐标dot/sqrt/atan/cos/sin、重建向量47和converted68为half，原clamp69与外部相加71保留。原半精度gain364由color3决定，392为原half mix。whites原product42后division45的顺序也独立核对，保存函数/指令SHA与源行，不上传原AIR。

新联合路径只接受集合后端、**原raw color3精确为0**的调用。原half `0²+1`精确为1，gray-gain分支不选；这是精确常数事实，没有将非零参数归零。其他颜色/增益继续原模型，点模型未改。精度合同通过后才执行新的数值重放。

## 完整FG→smoothSat→392→warm传播

`joint_lab.py`用同一RGB生成元形成M的三个LMS分量，对实数`x^p,0<p<1`使用凹函数割线与全区间余界，再用同一组root生成元计算N。原f32矩阵/幂误差、half量化、极坐标往返、P·N及Q·M非精确恒等残差、p·q非精确1均继续单列；没有通过实数矩阵组合替换原FP指令。

`neutral_color_joint.py`显式保留`S = X + D`：X是同一FG354，D包含Lab/polar/inverse往返偏移及原exterior/最终half加法误差。原converted clamp的位移用非扩张事实覆盖；clamp是smoothSat原SSA69，没有给selective的pow底数加clamp。392仍按原顺序界`half(X−S)`、`half(difference*w)`、`half(S+product)`；X与D在实数误差证明中共享，未将S和X拆成独立输出盒，也未更改各原half算术2u+tiny预算。

`JointRGB`携带联合表达式及普通V外包络。S15中零皮肤/neutral/warmth控制沿原恒等门控返回同一活值，全部12像素的联合关系实际到达warm409；非中性运算保守退回原V路径。后续selective仍使用原未clamp的converted及原pow域检查，没有pow(1)捷径。

`shared-color-s20b.json`从原raw source/guide/ROI/参数出发，经producer→guided→主入口完整传播，未使用保存宿主warm的局部正界或任何中间结果oracle：

|观察边界|S19最大宽|本轮最大宽|本轮clamp盒仍含RGB110的像素数|
|---|---:|---:|---:|
|FG354|.57839683|.57839683|0|
|saturated374|1.08016296|.74511719|0|
|output392|1.73492788|.66693115|0|
|skin393/neutral408/warm409|1.73492788|.66693115|0|

所有已知范围覆盖保存原宿主值；同一12像素点模型的1938个half观察仍逐位差异0，未新增原宿主案例，也不将分量数当独立案例。当前严格范围仍为cast0/tuning2/中性BGFG/零lookup。

**selective unknown仍为12，未选内部unknown仍24，writer集合未生成。** 12个converted外包络仍各含至少一个负通道，全局最小下界为-.19287109375；首像素约R[-.12085,.56348]、G[-.07123,.46582]、B[-.06995,.43945]。负端点联合可达性未证明。RGB110已被当前完整上游盒排除，不意味着其他负底数域被排除；原S18全clamp域负见证仍被新模型覆盖，没有再追求全clamp非负证明或推断未执行的pow/GPU行为。

本轮输入FG354外包络自身已有G/B负下界（全局约-.04733/-.07813），其宽度未变；这里没有把它们判为实际可达。继续收紧完整图需要保留更上游semantic335/347中的同一reference、BG/FG gain与person混合关系，以及剩余极坐标误差关系，不能把独立FG盒的每个角当作同帧可达点。本轮止于上述可复验改善和准确unknown。

## whites：先证明原乘积，再证明原商

`whites_joint_ratio.py`只在原集合商超预算、曲线非负/有界且首样本精确0、half amount在[0,1]、原正支z>0时启用。clamp后pow的舍入外包络保留，包括略大于1的上界；另逐步检查原mix中间量有限，不把该外包络强制缩回[0,1]。原曲线仍显式供给，不由成片恢复；不符合准入或新界仍超65504时继续unknown。

保留同一个`z=min(c)`、曲线`target(z)`及`changed=halfMix(z,target,amount)`。零原点分段线性表给出`target≤A*z+B`；A/B包含原half index乘法、原>.75分支、显式宿主f32采样步骤2u误差和half转换，没改门限/epsilon/mask。由原mix三个half步骤得到`|changed|≤C*z+D`，随后：

1. 先界**原half product42**的绝对值并检查有限；代码也先执行原乘积。
2. 再使用同一正z的half下界界**原half quotient45**并检查有限；没有把程序改写成先归一化、先除后乘或约去z。

|原S14-C case0调用|原乘积绝对值界|原商绝对值界|
|---|---:|---:|
|BG whites，half amount约.0400085|1.09995719|7.14773948|
|FG whites，half amount约.0200043|1.05291464|5.58120506|

这仅在声明的宿主采样/舍入合同下给整集合外界；不是原GPU采样精度、实际端点可达性或数值吻合。保持先乘后除，未把负的独立商端点视为原程序结果。

`whites-joint-s20c.json`的新默认链为：Shadows→contrast（宽9483）→BG whites（13404.54）→mids（13483.16）→smoothSat（13548.88）→FG whites（21902.67）→**FG contrast unknown**。BG352条件集合已实际生成并覆盖保存宿主值，但没有标成完整运行/GPU验收。

新的首个未处理失败在FG354的contrast，half amount=.0200042724609375，不符合已准入BG amount=.029998779296875的域。失败原`newspan/span`分子约[0,22010.3450]，正分母约[1.001358e-5,21924.0557]，独立商超half有限预算。端点联合可达性仍未证明；不能用宽BG包络宣布完整管线通过。

## 新测试在运行前绑定源码

S19旧原运行没有源码哈希清单，恢复阶段关联仅基于恢复哈希与mtime；原`verification-s19.json`保持不变。本轮使用`bound_validation.py`：**先持久化源码/输入SHA清单，再启动命令**，完成后检查来源和已存输入未变，保存退出码与完整日志SHA。静态合同、12像素完整传播、辅助case0及测试均有独立pre/post记录；首个静态合同使用的初版wrapper保存了pre输入SHA，post只记录源码未变、未保存输入未变字段，故不能补记该检查通过。原AIR身份仍由既有精确hash门控。后续数值重放和正式测试均有源码/输入未变字段；正式测试绑定为`test-binding-s20d.pre.json`与`test-binding-s20d.json`，包含本次229个Python源码和220项测试的实际版本，而非事后mtime关联。

220项测试通过，新增9项聚焦精度/原算术顺序、联合载体、完整12像素传播与unknown保留、旧负见证、凹函数余界、whites分步有限性与非法域拒绝、raw非零参数拒绝，以及测试文件自身的预执行哈希。旧24/8 unknown、tuning field17/byte652、18个全局encode负例、S19历史范围和非唯一逆证书均保留。没有新原GPU、真实同帧、活跃风格或照片逆解验收。

仓库根复验；输出须不存在。完整数值/静态重放命令也保存在各pre清单中：

```sh
python3 research/styles-firmware-20261022/bound_validation.py \
  s20-recheck /tmp/psr-s20-tests-new.json \
  python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
```

精度合同、完整传播与辅助收据分别为`color-joint-contract-s20a.json`、`shared-color-s20b.json`、`whites-joint-s20c.json`。源码/收据/绑定清单与日志精确SHA见`evidence/verification-s20.json`；最新覆盖清单为`evidence/pixel-inventory-s20.json`。9字段CPU桥接继续沿S18准确缺件/Proxy方法/binding清单暂停，本轮未新增搜索、下载或挂载。
