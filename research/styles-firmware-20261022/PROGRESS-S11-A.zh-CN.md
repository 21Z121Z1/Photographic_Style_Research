# S11-A：单见证乘加定位与24个首零分母

基于 e186418；同一 iPhone17,3 / 24A446 原 AIR10。没有重跑505组或原 mids/semantic 批次；只对保存的 local+gamma 单见证运行原完整 BG 的限定诊断。没有新下载、私人媒体或原 GPU。

## 首次差异在 pow 之前

`diagnose_local_gamma.py` 在原完整 BG 中增加 checkpoint stores，原算术不动。插桩输出与未插桩和保存收据逐位一致。local 输出 SSA142、gamma 输入 SSA153、mean154、guide155、乘积156均一致；首次选定差异为 f32 SSA157。该差异在 half 转换158后消失。

真正影响最终2个分量的是指数 SSA166：逐操作模型 `1.00390625`，原宿主 `1.0029296875`。pow170的输入已不同，不能先归因 libm。仅移除原 SSA165/166 两条乘加的 fast 标志后，指数及输出回到逐操作模型；只移除156/157标志改变了157、没有改变最终输出。单次舍入 fma 候选分别精确匹配157和166的宿主值。因此该见证支持宿主 fast 乘加融合的具体解释，不宣称原 GPU 同样融合或无条件全局 bit-exact。保留原2 ULP差异，不改默认点模型、不修改误差预算。

## 条件分母域

`diagnose_set_denominators.py` 只重放已保存24个模型输入，native调用0次；逐行保留首个含零分母、分子/分母区间、原叶与调用栈、叶输入盒。

历史 e186418 模型：24个首零中，16个由原严格正分母门排除（contrast/negative shadows 的 span 门及 neck 的 luma>0）；这是条件区间没有保留门约束造成的假零。其余8个为 airy 的归一化 sum：当前独立输出盒包含黑色，但上游联合可达性仍 unknown，不能宣布真实零已可达或不可达。

`leaf_domains.strictly_positive_branch` 在原 yes 分支内取交集，保留原阈值、严格比较和完整 else 并集。half/f32 使用阈值以上的最小可表示数，不缩输入/人物/肤色 mask。无中心兜底。所有0..1的非负 half 编码回归验证该交集没有排除任何原 yes 分支值；首次开发测试发现 NumPy 标量隐式降精度比较会多前进一格，已通过显式 float 比较修正。

应用后原16个条件假零不再导致零分母拒绝；但区间仍过宽，转为16个有限 half 算术包络超预算 unknown，另8个 airy 首零不变。**24个组合集合仍全为 unknown，没有任何一组改记通过。** 此阶段只排除了特定错误拒绝原因，没有证明全激活联合域紧包络。

114项回归通过。baseline使用 git e186418 的3个像素模型与当前诊断脚本临时重放，未切换或修改工作树；修复后再模型重放。静态/宿主、原 GPU 和同帧端到端分别保留边界。

复验：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/diagnose_local_gamma.py /path/to/0010.ll.txt research/styles-firmware-20261022/evidence/native-bgfg-coupled.json /tmp/new-local-gamma.json
python3 research/styles-firmware-20261022/diagnose_set_denominators.py research/styles-firmware-20261022/evidence/native-bgfg-complete.json /tmp/new-denominators.json
```

收据分别为 `evidence/local-gamma-diagnostic-s11a.json`、`denominators-baseline-s11a.json`、`denominators-guarded-s11a.json`。原指令和变体只保留本地；公开收据含 SHA、SSA值和明确的变体标志修改范围。此提交后继续主入口皮肤/高光/亮度连接，尚无新增完整照片或逆解验收。
