# S15：单一条件前向整图链与保存误差诊断

版本仍限定 iPhone17,3 / iOS27.0.1 /24A446，产品 Styles2 参考、内部 SmartStyleV1 / CMISmartStyleProcessorV1。IMG_2810 的 iPhone19,2 / Styles16 / TextureStylePeopleDataVersion3 及未知 capture build 保持分离。本轮没有下载、私人媒体、原GPU或照片测试。

## S15-A：连续链，不供给中间输出

冻结 S14-B fixture0 的3×4 primary/original guide、2×3 linear/matte、CCM、semantic7、SRL、producer形状、ROI5/6；补入 S14-C case0 的辅助guide8/9与mask值，首次明确其余主入口参数。完整原始半精度位型、672B参数、320B色彩管理、10640B stats、176B ROI 和版本存于 `evidence/complete-context-s15a.json`，**在运行前写定并哈希**。补充字段不冒称旧局部上下文原本已有定义。

`complete_forward.Context`冻结原始输入并校验形状/精度/版本；复用 `full_ltm_chain.generate`、已有主入口前缀与后续算子，组成 source→producer→guided→precomputed block290→完整主入口→600→writer。API不接受BG/FG图、reference196、person96、335、392、BW477、567或600等中间结果。producer/guided图进入主入口；主入口自行从原纹理/参数求reference和mask。颜色管理传入/输出code3、BG/FG基础调整为中性、cast0、tuning2、非零外围mix4=.25/mix5=.65；并非所有非零分支的联合激活验收。

`main_full_host.py`保留完整原AIR10及40个递归helper、原writer，只增加ABI与独立观察store；PHI观察置于整组PHI之后。原算术/谓词/FP属性不变。AIR7、90/91/92 guided 和完整主入口在同一宿主库连续执行，原主入口直接写5×6 RGBA16目标，ROI12=(1,1)。source UV没有混入output offset。主入口原图块路径未在本组合选择，direct writer真实运行；旧S14-D imageblock验证独立保留。

一个上下文共102次原kernel调用：producer6，guided72，带writer主入口12，无观察主入口12。后者验证观察store没有改变最终写出，120个目标half逐位一致、原宿主全部观察值有限。原始收据 `native-complete-s15a.json`保留producer、原始map、guided五级、335、392、393/394/398/400/404、408/409/413、468/472/476/477/492/493/501/566/567/597/600及目标图的位型。全链没有由外供中间输出跳过算子。

初轮点模型guided有2值差异；S15-B修正后仅重放已保存输出，新增原调用0。当前 `complete-replay-s15c.json`比较1938个half观察分量，34个内部差异：bright400为24值、max .0009765625；tonal468为7值、max .00048828125；haze493为3值、max .00048828125。335、392、477、567、600、最终120目标分量逐位相同。内部差异仍独立可见，不能被cast选择或最终混合掩去。

整图集合12像素均在selective413的pow域首次unknown，另有24个未选择highlight/bright内部unknown；**没有writer集合结果**。此前已知范围均覆盖保存的宿主值，最大宽度15824.084179562526（warm409），335为1429.7648972561542，392为5035.5182289262775。覆盖和巨大宽度不计作数值吻合；旧155.125、S14-B的17941.5513包络均未删除或替换。

仍需外供的确切接口：guide8/9与上游生成；人物/肤色/天空mask与上游生成；GTC/whites；34cast、完整系数/控制；原stats字段；4×360 lookup与上游生成；CCM/transfer/SRL/ROI/格式及帧身份。本例lookup为显式常量零，仍执行selective算法，只覆盖该纹理条件下的采样；非恒定lookup的旧ideal sampler与v3采样差异没有由此解决。相同原始输入的条件链已连接，不等同从成片恢复这些输入。

## S15-B：guided 首次f32分歧与修正

`guided-first-divergence-s15b.json`：fixture0使用完整链保存的FG_a差异位置(3,0)；S14-B fixture1旧收据仅有聚合值，故只恢复该20像素系数pass，不重复producer、mean/apply或ROI批次。总21次系数调用，定位fixture1的(0,1)。两见证从sample累计到mean/cov均逐位相同；首次差异在SSA56，不是libm。实际ARM64宿主为：

```
epsilon_plus_mii = fma(sum_ii, float32(1/9), epsilon)
var = fma(-mean_i, mean_i, epsilon_plus_mii)
```

旧v3先舍入mean_ii，再在减mean_i²后加epsilon；仅更改括号也不足够。新 `guided_precision.py`保留原v3 sampler/apply，显式建模上述宿主fast收缩。两个见证各52个f32检查点共104分量全部逐位一致。fixture0带观察half与已保存无观察输出相同；fixture1补1次原无观察系数调用，同样一致。

`guided-refinement-s15b.json`：fixture0的FG_a、mean_a用完整保存图重放均bit0；fixture1的系数差异修正，并对两个受影响mean_a位置额外执行原AIR91，两处旧值各差1分量、新值bit0。这两个mean探针输入是同上下文计算a/b数组，范围仅为该pass，未冒称新的完整guided原图运行。补充共3次调用；本轮诊断24次，完整组合102次，合计126次。旧S14-B五个具体差异的定位/见证修正均有证据，但不把它扩成任意输入或iOS/GPU的统一求值次序。epsilon、mask、sampler及2u/4u预算未改。

## S15-C：BG首超限，保留unknown

只重放保存S14-C case0，无原kernel调用。首失败在BG352的contrast preserve：`newspan / strictly_positive_branch(span, 原阈值)`。分母下界half0x00a8=1.0013580322265625e-5，严格原分支不含零；这不是可达零分母或硬件阻塞。旧独立范围丢失同RGB min/max关联，newspan为[-18.9222,26.8334]。

`leaf_correlations.channel_span`保留同一向量关系和原一次减法预算，使newspan变为[0,26.8175]，span上界由1.01639降至1.00195；整例仍在原half65504预算拒绝。分4×4×4共64个覆盖原contrast输入盒的子域，56个有界、8个unknown；已知子域最大宽201.1525，不能当整例包络。整例unknown数量前后均1，整例宽度/覆盖仍unknown。最小失败表达式、输入盒、全部分域与原因保存在 `bg-dependency-s15c.json`。

没有把 `(rgb-low)*(newspan/span)` 换成 `((rgb-low)/span)*newspan`：该改写会改变原half除法溢出和舍入，不能仅因连续代数等价就宣告修复。当前缺口仍是可继续改进的软件相关性建模，不缩mask、不调阈值、不用中心结果兜底。

## 复验和范围

185项单元测试通过，包括完整保存输出重放、内部错误不被终值覆盖、集合unknown禁止writer、冻结上下文/版本/ABI负例、共享span角点覆盖、全部104个guided f32见证。tuning field17/byte652错误负例保持；S12原tonal独立观察保持。本轮没有重复既有大批次或增加孤立叶批次。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
# 以下纯模型重放，原AIR调用0：
PYTHONPATH=research/styles-firmware-20261022 python3 -c 'from pathlib import Path; from native_complete_check import replay; p=Path("research/styles-firmware-20261022/evidence"); replay(p/"complete-context-s15a.json",p/"native-complete-s15a.json",Path("/tmp/psr-complete-replay.json"))'
python3 research/styles-firmware-20261022/diagnose_bg_dependency.py /tmp/psr-bg-dependency.json research/styles-firmware-20261022/evidence/native-main-pre393-s14c.json
# 需要已保存AIR、仅重建该组合时：
python3 research/styles-firmware-20261022/native_complete_check.py /path/to/ios-air /tmp/psr-complete-native.json /tmp/psr-complete-context.json
```

旧24组合unknown、8叶域unknown、S14-C其他集合unknown、既有bright/皮肤等差异、9未定位消费者及原GPU/真实同帧上下文依赖均保留。未做参数识别或完整HEIC条件逆/仅成片逆解，既有S20多解证书继续有效。最新清单 `pixel-inventory-s15.json`区分条件组合与原GPU/照片验收。
