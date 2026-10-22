# S19：排序域接入默认contrast与保存同帧输入的selective域判定

本轮新增原AIR/CPU指令宿主调用0，下载0B，私人媒体0。复用保存64个contrast输入盒、原S14-C case0、S15冻结的3×4合成上下文及其已保存宿主观察；没有新孤立叶批次。身份仍是iPhone17,3 /iOS27.0.1 /24A446、内部SmartStyleV1 /CMISmartStyleProcessorV1，产品Styles2参考另列。IMG_2810的iPhone19,2 /Styles16 /TextureStylePeopleDataVersion3与精确build缺项保持原范围。

## 7盒的原证明已进入默认路径

`contrast_sorted.py`复用S16的`ordered_box`与`lattice_span_lower`。仅half集合RGB、half整盒参数精确为`.029998779296875`，且输入整盒包含于保存的7个失败家族之一，才准入排序域回退。家族为cell1/17/21/22/38/42/43。S18的cell0联合回退保留；点模式和原已知独立域继续走原图，范围/参数不符时保持原unknown。

每个家族覆盖RGB通道的6种顺序，含重合/相等边界。使用S16原half格点与max-lower-bound事实，分别保留原`span.f()>threshold`正支和原else；不移动门限，不重排原half商再乘的指令顺序。将诊断器曾以全局patch表达的min/span事实改为私有算子的显式输入极值/分支参数，**生产路径不修改全局V方法或channel_span**。正支与else最终取并集，全部原舍入预算保持。

默认路径另仅接受**精确保存parent盒**及该精确half参数，用原64盒覆盖它。输入cover文件SHA固定为`31b167989bddf8a93d67a42ed66f7b8daf655810bcc156ee24bb8e263705a59c`；运行时核3轴各5个共同端点、全4×4×4笛卡尔网格与parent边界，拒绝空缺/错配。只读取保存输入坐标，重新执行各模型；未使用保存输出作oracle，也不扩大到任意更大parent盒。

|计数层|历史/当前结果|含义|
|---|---|---|
|S16诊断|8盒、48正支域：42已知/6 unknown；48 else已知|历史诊断收据不改写，不算当时默认准入|
|S18默认64盒|57已知、7 unknown|旧默认收据保留|
|S19默认64盒|56原独立、1 cell0联合、7排序，64有界/0 unknown|64个原输入盒，非64个新宿主案例|
|S19的7排序盒内部|42正支、42 else已知|是7盒的子分支，不能与64盒混加成独立案例|

S19排序子支的最大宽逐项与S16保存结果一致，复用原算术验收，没有重复原宿主批次。7盒中最大包络宽仍约6642.95499。parent并集RGB约为R[-3143.89428,6339.10654]、G[-3321.10463,3321.85036]、B[-1511.39333,4677.96060]，最大宽**9483.00082536**。这些是声明预算下的条件外包络，宽度不代表数值吻合或原GPU精度。

## 完整S14-C case0的下一处实际失败

`contrast-default-s19a.json`沿原默认主入口运行一个保存case0，独立记录叶输入、输出与被内部回退处理的算术失败，避免把已被处理的旧contrast异常误报为完整BG失败。当前顺序为：

`Shadows（已知，宽约1.01540）→ contrast（已知，宽9483.00083）→ whitesCurve（unknown）`。

主入口仍报告BG352 unknown，**完整BG未通过**。新的首个未处理表达式是whitesCurve原`(changed*c)/z`：先乘后除，未改其顺序。z是同一个`min(c)`，正支为原`z>0`；half下界为`2^-24=5.960464477539063e-8`，不是零分母。独立分子盒约[-.04228386,1.04611575]，分母盒约[5.960464e-8,1.00195318]，原商界约[-709405,17550910]超出65504，因此fail closed。

最小未决关系是`z=min(c)`、`target=curve(z)`和`changed=mix(z,target,amount)`的共同来源及其与c的关系。负分子端点和最小分母与最大分子的联合可达性均未证明；不能据此宣称原实现溢出。本轮止于这个准确的软件边界，没有为它补任意界或升级整BG通过。已知主入口前缀仍覆盖原保存宿主值。

## S15同一保存合成上下文：局部可排除，完整上游集合仍未决

冻结context SHA仍为`ffae597ca79f92447a2bdae45bbc007450be27ae9165bef78d0e6b3cb0932b11`。`selective_sameframe_domain.py`同时核context、S15原宿主收据和S17首像素探针的精确SHA；不是只信一个可复制的context标签。使用原保存的warm409 half值、person/skin观察和冻结的uniform sky，lookup/offset/amplitude/output_mix仍为原零控制。

S19在已有neutral selective联合误差证明中，保留局部输入实数参考root的**下界**，再计算Lab矩阵的相消范围；原f32误差、half量化、极坐标、两次幂及指数不完全互逆的预算不减。原完整[0,1]³域下root下界仍0，S17宽包络不因此改变。这不是pow(1)捷径，也没有添加底数clamp。

|判定对象|结果|
|---|---|
|12个保存精确宿主warm输入，各自局部selective误差图|12个converted包络下界均正；最小通道下界约.16784668|
|这12个实际观察的RGB包络，保留整个包络而非中心|输入R约[.21228,.28003]、G[.18762,.22290]、B[.16882,.22058]；converted下界(.19848633,.18273926,.16516113)，均正|
|S17首像素原converted探针|仍被新局部解析界覆盖，未新增原宿主调用|
|完整原上游舍入误差集合|仍12个selective unknown、24个未选内部unknown、无writer集合|

因此，在声明的selective2u/4u和转换假设下，可以排除**这些保存宿主warm输入及其观测包络**在该局部图产生负底数。输入来自已核原宿主观察，未取不确定盒中心；但这个观测包络不是完整上游所有舍入选择的传播界，代码从未把它喂回complete_forward替换warm集合。原12个传播warm盒中，没有一个已证明包含于这个观测包络。

S18的完整clamp域RGB110负底数见证保留，没有重跑它或再追求全clamp非负证明。RGB110不在本次12个观测warm输入包络内；这仅排除它是**保存宿主实现的这些实际warm输入**，不把一个全clamp域见证当成同帧可达见证。

当前集合图第一次在**saturated374**的外包络允许clamp后的RGB110（12像素），此前FG354盒不允许；saturated宽约1.08016，output392及warm409宽约1.73493。准确待保留关系为：同一FG354 RGB经原color3=0的neutral-gain smoothSat极坐标/Lab往返生成saturated374，再与该FG RGB按同一person权重混合到392。共同LMS/root/角度/半精度往返残差及`saturated−FG`不能当成独立盒。只是外包络包含RGB110，既不能证明它可达，也不能证明所有负域都不可达。

完整同帧误差集合的最小保留问题是：是否存在该冻结raw上下文的**共同上游舍入实现**，使warm409与后续selective共享变量图产生负converted。当前结果是unknown，所缺是上述相关关系，而非额外照片、更多中性点或GPU才能开展的软件分析。本轮原pow213未新增执行，没有由gamma1或局部正界推断其完整语义及原GPU行为。

## 9字段桥接暂停与恢复材料

沿用S18 `consumer-paths-s18c.json`的9个writer/指针路径和CPU断点，分类继续是未完成软件追踪。本轮没有新追踪、查找缺件、下载或挂载。缺件是任务缓存中的`../firmware-iphone17-3-systemos/decrypted/043-70113-711.dmg`及对应dyld，旧收据SHA `bce06bf973fe4fcce39f5401be42352b96e2e052cf4c182d107ef8fd2d86fe18`；状态沿用S18“缺输入而未执行”，非权限拒绝。

后续最小恢复清单保持：同SHA镜像，或iPhone17,3 /24A446 /CMImaging UUID `0A9BC064-A4BC-330E-861A-C70A637B14B3`下、已核原字节的Proxy `_calculateDynamicRenderParameters` @0x1d437335c与`_generateColorCubes` @0x1d4373474完整方法；核params数组672B stride、实际offset、Metal buffer1/stats3及cube pipeline的binding。没有把这些预期核查点写成已证明的运行连接。缺缓存不阻止本轮contrast与同帧条件域软件工作。

## 复验与限制

211项测试通过；包括原64覆盖几何、参数/外域拒绝、排序分支与S16逐项相等、默认路径不patch全局方法、whites新失败、局部域正界与完整上游unknown分离、收据内容篡改拒绝。旧24/8 unknown、tuning field17/byte652、18个全局encode负例及S20非唯一证书均保留。1938保存half零差异仍仅是既有cast0/tuning2/中性BGFG/零lookup宿主上下文的回归，未扩成活跃风格、原GPU、真实同帧或成片逆解验收。

仓库根目录，Python3/NumPy；以下均为纯模型和已保存证据，输出须不存在：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/replay_sorted_contrast.py \
  research/styles-firmware-20261022/evidence/bg-dependency-s15c.json \
  research/styles-firmware-20261022/evidence/native-main-pre393-s14c.json \
  /tmp/psr-contrast-default-s19-new.json
python3 research/styles-firmware-20261022/selective_sameframe_domain.py \
  research/styles-firmware-20261022/evidence/complete-context-s15a.json \
  research/styles-firmware-20261022/evidence/native-complete-s15a.json \
  research/styles-firmware-20261022/evidence/selective-one-pixel-s17a.json \
  /tmp/psr-selective-sameframe-s19-new.json
```

收据为`contrast-default-s19a.json`、`selective-sameframe-s19b.json`；精确源码/收据/测试日志SHA见`evidence/verification-s19.json`，覆盖清单为`evidence/pixel-inventory-s19.json`。
