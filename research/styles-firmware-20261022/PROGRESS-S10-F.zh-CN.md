# S10-F：完整 BG/FG 的限定接线检查与剩余边界

参考资源仍为 iPhone17,3 / iOS27.0.1 / 24A446 的内部 SmartStyleV1 / CMISmartStyleProcessorV1。与产品代际 Styles 2、IMG_2810 的 iPhone19,2 / Styles v16 / PeopleData 3 分开；后者精确 capture build 未核实。没有新下载、私人媒体或原 GPU 运行。

## 本轮已经减少的 unknown

S10-A 的 block290 显式输入 post-guided-filter BG/FG 纹理，已经定位坐标、颜色域、混合和来源；没有假定与 fallback 等价。S10-A..E 补齐 whites、contrast、airy、Shadows/Negative、lighten/Negative、smoothSat/RichSat、underGrass、neck、underTone、smartContrast、highlightNeg 以及 local/gamma。mids 与 fallback semantic 复用已验收模型，未重复其宿主批次。各叶精确激活数量、原函数/指令段 SHA 与运行收据见各阶段报告。

本阶段进一步使用 **完整原 renderBGAdjustments / renderFGAdjustments 及所有递归叶原文** 进行组合检查。没有 abort/identity 占位；`leaf_host.py` 只新增 ABI wrapper，原完整函数体不改。编译为 arm64 macOS 宿主执行，AIR 内部 sampler/dot/libm 使用显式 shim，不能称原 iOS/GPU 运行。

## 固定点输入与不确定集合分开

`bgfg_fixed.py` 要求 `ExactHelperFields`：显式 f32、BG17/FG16、有限 abs≤8、来源说明、只读副本。RGB/semantic 与 guide/person/skin 必须为显式 half 点。它拒绝 `ConsumerFields` 和任何区间输入，未添加 producer 中心值适配器。该模型仅检查已知固定 helper 参数的运算顺序与接线。

原 `bgfg_tone.run` 集合路径保持不变，继续传完整区间和边界决策；未知分母域仍返回 unknown，绝不自动调用固定点模型兜底。

| 新完整 helper 检查 | 原调用数 | 已知点分量 | half 位差 | 集合已知 / unknown | 已知集合越界 |
|---|---:|---:|---:|---:|---:|
| BG 多叶同时激活 | 12 | 36 | 0 | 0 / 12 | 无已知集 |
| FG 多叶同时激活 | 12 | 36 | 0 | 0 / 12 | 无已知集 |
| BG 双叶组合 | 4 | 12 | 2 | 4 / 0 | 0 |
| FG 双叶组合 | 4 | 12 | 0 | 4 / 0 | 0 |

双叶组合为 BG local+gamma、whites+underGrass；FG neck+underTone、lighten+smart（后者包含 highlightNeg 前置叶）。24 个多叶激活点对照逐位一致，**其24个集合结果仍全为 unknown**，不能用点对照抹掉。首次无点模型检查的24组开发收据留在本地；之后加入固定点比较重新执行同一开发组，不属于重复已验收旧批次。

两个位差都在 BG local+gamma 的同一个调用，最大绝对误差 `0.00048828125`，各为相应 half **2 ULP**。早期进度文字误称一个 ULP，现以编码差值审计更正。`audit_bgfg_ulp.py` 从已提交合成输入重放模型、比较保留的原宿主输出，不重跑 native 批次；审计见 `evidence/bgfg-coupled-ULP-audit.json`。未调整模型或误差预算来消除差异；具体来源尚未隔离（宿主 C float libm 与 Python 双精度中间运算是待检验因素），不可断言原 GPU 更吻合任何一侧。原结果均落入集合。

集合也不等于紧误差：双叶组的最大 box 宽度 BG `1.000976622104645`、FG `5.249569190930268`，明显不能支持高精度逆解。多叶集合在 contrast/airy/negative shadows/neck 处因累计包络包括零分母而 fail closed。这是数值建模缺口，**不是硬件阻塞**。RichSat 黑色归一化的 6 组 unknown 与 airy 黑色域缺口也仍保留。

111 项单元回归通过，新增固定字段只读/类型约束、禁止区间中心替代、多叶 unknown 保留及双叶集合后传。各结果仍 `full_helper_numeric_verified=False` / `full_camera_pipeline_verified=False`；只支持表中明确的固定域、宿主及集合假设。

## 可复用资源与最小剩余工作

`pixel_coverage_inventory.py` 对同一 AIR10 身份先校验，再生成主入口20处直接像素调用的符号、SSA、原函数 SHA 与当前覆盖状态，输出 `evidence/pixel-coverage-s10f.json`。它不重复9槽/215头扫描，也不声称未发现的消费者 unused。

可直接复用本地 AIR7/AIR10/AIR11、CPU 原方法文本、GTC/cast/prior/正负系数与本轮叶模型，无需新机型镜像。具体可继续的静态/合成工作：

1. 收紧 contrast 等条件分母与颜色区间的相关性、隔离 local+gamma 两个 ULP 差异；尚不可将全激活集合当已解决。
2. `renderSkinAdjustments`（主入口 SSA393）：已得 FG θ9/θ10 系数，不代表皮肤像素变换已建模。接着是 `highlightRecover` SSA394、`renderBrightAndContrast` SSA400。
3. neutralizing/warmth/selective-color（SSA408/409/413）、BW、video haze、protectMask、通道混合、输入/输出 transfer function 与外围 inline 运算尚未接成数值模型。已完成的 saturation/airy/contrast 算法应复用；其外围参数与混合仍需逐段核对。
4. AIR7 createLTMGainMap 与 guided filter 仍是已定位的生产链，尚未数值重建；block290 条件模型要求显式供给最终纹理。

真正依赖外部材料的验收另列：匹配 iPhone17,3 / 24A446 原 iOS/GPU 运行、同一帧的工作 RGB/ROI/masks/曲线及 post-guided-filter 纹理；IMG_2810 还缺独立精确 capture build 与匹配资源。未尝试读取照片库/私人样本。仅成片多解证书 S20 及条件逆范围不变，未承诺丢失细节唯一恢复。

没有新增授权拒绝或待批准动作；此前被拒绝的 `ps -ax -o pid=,command=` 不重试、不替代绕过，且不妨碍以上静态工作。未触碰 Metal/XD、安全设置，未合并或删分支。

## 复验

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_bgfg_complete_check.py /path/to/0010.ll.txt /tmp/new-bgfg-complete.json
python3 research/styles-firmware-20261022/native_bgfg_coupled_check.py /path/to/0010.ll.txt /tmp/new-bgfg-coupled.json
python3 research/styles-firmware-20261022/pixel_coverage_inventory.py /path/to/0010.ll.txt /tmp/new-pixel-coverage.json
python3 research/styles-firmware-20261022/audit_bgfg_ulp.py research/styles-firmware-20261022/evidence/native-bgfg-coupled.json /tmp/new-ULP-audit.json
```

完整函数、宿主、输入/输出与模型源码 SHA 在 `evidence/native-bgfg-complete.json` / `native-bgfg-coupled.json`；原 AIR/专有二进制不入 Git。静态调用链、宿主运行、原 GPU 与真实照片验收各自分开。本阶段交付代码与证据，完整照片处理/逆解未完成。
