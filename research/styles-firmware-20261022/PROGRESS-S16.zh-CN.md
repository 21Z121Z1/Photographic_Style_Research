# S16：共享窗口误差、定向half差异与8个BG子域

复用S15冻结的同一个3×4合成上下文，SHA256 `ffae597ca79f92447a2bdae45bbc007450be27ae9165bef78d0e6b3cb0932b11`。硬件/build仍为iPhone17,3 /24A446；产品Styles2参考与内部SmartStyleV1编号分开；cast0、tuning2、中性BG/FG、零lookup及全部原始参数/纹理/ROI不变。S15的102次调用只属一个上下文，不是102个独立案例。本轮不新增叶输入批次、下载或私人媒体，也没有原iOS/GPU执行。

## 共享窗口：不把整盒替换成中心

`guided_affine.py`用常数项加具名[-1,1]生成元表示**整个输入盒**。常数项只是表达式坐标；输入、乘积余项、舍入误差均未丢弃。相同texel和相同确定性采样表达式复用生成元，mean_p/mean_i/mean_ip/mean_ii、covariance、epsilon和后续a/b保持共享关系；乘积保留同生成元平方的非负事实与交叉项余界，除法使用带余项的倒数展开，跨零仍拒绝。

沿用S15-B已证的ARM64宿主顺序：inv9乘法；cov FMA；`epsilon_plus_mii=fma(sum_ii,inv9,epsilon)`；`var=fma(-mean_i,mean_i,epsilon_plus_mii)`；b FMA。每个原f32算术/FMA继续用2u+tiny预算；half转换覆盖所有可能bin，采样保留v3量化与tie-up合同。f64记账另加保守外扩，未减预算。a在转half前用于b，mean及apply继续保持a/b关联。非有限、跨零、过预算保持unknown。`shared=False`只保留历史独立盒诊断，不作当前前向默认。

另补集合模式的**变量身份**事实：有限IEEE `mix(x,x,w)`保持x；只在同一V对象、后端/精度与广播合同通过时使用。相等上下界的两个独立V不视为同一变量，point模式仍执行原舍入图；不改half除法顺序或任何门限。

`shared-window-s16-final.json`为纯保存结果重放，原调用0，所有已知范围覆盖原宿主值，保存窗口(3,0)的52个f32检查值也全部覆盖。

|观察|S15最大宽度|S16最大宽度|
|---|---:|---:|
|producer FG gain|0.690287|0.690287|
|BG系数a|1653.5|4.339844|
|FG系数a|1980.5|5.195313|
|BG guided output|1384.5|0.522461|
|FG guided output|1664|0.625|
|335|1429.764897|0.578397|
|392|5035.518229|1.734928|
|393|7972.548811|1.734928|
|warm409|15824.084180|1.734928|

共享窗口内FG mean_i/mean_ii最大宽约1.430512e-6，cov约.00649825，epsilon+mii约1.430751e-6，var约4.292015e-6；完整逐级范围见收据。系数宽仍约5.2，不算数值吻合。

**12像素仍首次在selective413 unknown，未生成writer集合；未选highlight/bright内部仍24个unknown。** `selective-unknown-s16a.json`记录第一处`converted.pow(gamma)`：从Lab逆变换后的底数范围含负数，例如R约[-293.5,293.5]，gamma约[.994589,1.005411]。这些独立端点未证明联合可达，不能反称原宿主产生了负底数；仍须保留后续颜色/混合的依赖。没有给pow任意界、整数指数捷径或中心兜底。

## 点差异：先测指令，再限定调用域

总共6次原AIR完整主入口宿主调用，只覆盖2个保存像素与3组既有探针：(0,0)、(1,1)、(0,0)的encode细探；3次初轮观察，3次同布局memory合同审查复验。诊断使用保存的原guided输出，**不计作新增完整producer链验证**。原helper/主入口只插独立store，相关memory摘要保守扩成readwrite；原算术、谓词、FP属性不变。helper定义#7/#20已保守放宽；调用点#29经核实本来没有memory限制，并不存在漏改。memory审查只重放3组原布局，全部探针及bright400、tonal468、haze493、600终值均与旧收据逐位相同。`internal-memory-s16b.json`保留实际执行IR哈希与对照。纯构建的函数/探针元数据也与执行版本相同；执行收据当时的attribute组发射次序来自Python set；现已按ID稳定排序并编译检查。旧执行IR文本哈希与当前重建可不同，函数/探针元数据一致，不冒称旧IR逐字节重建。没有重跑102次完整链或增加输入案例。

- bright首先在SSA72分歧，SSA70/71及上游相同；原值等于一次half FMA，原逐步模型的乘后加在3通道各差1ulp。之后独立参考encode的SSA105/107/108相同，首次在SSA109分歧，同样由其half乘加收缩解释。不是先归因libm或套用guided的f32顺序。
- tonal在另一个像素首次于SSA440线性乘加分歧；haze首次于SSA33、并核FG63。同一组保存操作数各自的half FMA候选均逐位匹配原观察。分别接入已有算子，没有推断所有相似表达式都收缩。
- **调用域负例**：把bright encode收缩全局套给输出transfer code3，会新增18个600/writer位差。`encode-scope-regression-s16b.json`保留失败计数；现将`host_fma=True`仅固定在bright调用内，输出transfer保持原合同。191项回归含该反例，不能仅凭同形方程合并精度合同。

当前完整保存上下文1938个half观察：S15的34个内部差异降为8个bright400差异，max绝对误差.0006103515625；tonal7→0、haze3→0。335/392/477/567/600、最终120目标half仍逐位一致。`point-residuals-s16b.json`保留8个分量位置与位型；它们位于尚未作内部原指令探针的像素，未猜测首次内部原因。三个已观察探针的全部保存检查值经纯模型重放已一致，见`internal-replay-s16b.json`。这不扩成所有参数或GPU下逐位一致。

## BG：只检查原8个失败子域

使用S15-C已保存输入盒，未再均匀细分。每盒按min/mid/max通道身份的6种排序建立保守多面体外盒；原严格门限、else分支与商后乘顺序保留。实际输入来自half：非零通道差有局部half格点下界。该下界再施加原减法的**2u+tiny** allowance、向下取half，最后与原严格分支相交；没有直接用理想格点步长取代舍入预算。还保留max下界M与span的关联：选二进制边界P<M；若名义span D≥M−P，已有远离零下界；否则min>P，全部通道处在该正半轴格点，非零D至少为quantum(P)。合并得到D≥min(M−P,quantum(P))，再施加原减法预算。原正分支不可能由D=0的tiny误差越过原门限；else保留。该逻辑覆盖没有均匀细分输入。

`bg-orders-budget-s16c.json`：48个正分支排序域中42个有界、6个仍unknown；48个else外界均可界定。原8个失败盒中7个现在可完整覆盖，仅原cell0仍unknown。因此64个旧分域由56已知/8未知变成63已知/1未知，**整例依然unknown**，未接成BG完整通过。新增正分支已知外界最大宽6642.955，else最大宽1.6353；新增有界不等于精度足够。

剩余最小失败仍为原half `newspan / span`。原正分支不含零，较高幅值的half格点排除了不可能的小span；低幅值的剩余1个盒仍容许接近原门限的span，独立newspan端点可把商推过65504预算。收据逐排序记录分子/分母、输入边界和未证的联合端点可达性；灰色/近灰色else没有删掉。不知道这些极端端点是否在实际同一表达式下联合可达，故不宣称真实硬件溢出，也不作为硬件阻塞。不重排half除法或删除mask。

## 复验与未完项

191项测试通过；新增共享整盒乘积/倒数与跨零拒绝、同变量与独立等范围负例、完整保存链覆盖与未知保留、输出transfer不得继承bright合同、排序/格点预算与else回归。`compileall`和`git diff --check`通过。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/replay_shared_sets.py research/styles-firmware-20261022/evidence/complete-context-s15a.json research/styles-firmware-20261022/evidence/native-complete-s15a.json research/styles-firmware-20261022/evidence/complete-replay-s15c.json research/styles-firmware-20261022/evidence/guided-first-divergence-s15b.json /tmp/psr-s16-replay.json
python3 research/styles-firmware-20261022/contrast_order_domains.py research/styles-firmware-20261022/evidence/bg-dependency-s15c.json /tmp/psr-s16-bg.json
```

后两条原调用0。6次诊断的IR、原函数和输入身份哈希随收据保存；原固件/AIR/临时库未上传。保留8个bright残差、12个selective集合unknown、1个BG盒unknown；历史24组合/8叶域收据没有重跑或晋级。9个未定位consumer、显式guide/mask/stats/lookup/曲线/34cast/系数输入、原iOS/GPU/同帧与IMG_2810 build缺口保持独立。旧155.125、17941.5513宽包络保留历史范围；本轮不做参数识别或成片逆解，S20多解证书不变。
