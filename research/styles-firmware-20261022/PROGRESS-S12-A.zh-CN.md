# S12-A：实际 BW477 根、内部观察与 tuning 失败回归

基于80388ef，同一 iPhone17,3 / iOS27.0.1 / 24A446 AIR10。产品代际、内部SmartStyleV1和样张metadata仍分开，IMG_2810精确capture build未知。无下载、私人媒体或原GPU运行。

`pixel_bw.py`覆盖renderBWAdjustmentsByCastType与starkBWAdjustment，复用已证whites、root修正和tonal核心。参数包含实际SSRParams0、field17/byte652、parameter2、SSRTone20/65、guide350、person96及显式whites curve。SSRParams0与主入口解析cast245不同，不能共用猜测值。原参数0==4选stark，否则保留输入；参数0==15选BW tonal，否则保留前一步。

`computed_bw_outer.py`从真实472输入计算BW477，再按原483/489/492混合，不接受外部BW输出参数。旧conditional接口留作历史对照；新接口`BW_output_supplied_externally=False`。这消除了**显式BW输出**依赖，但曲线/参数/工作RGB/上游统计与lookup仍显式供给，未从成片恢复，也没有升级全域/GPU证明。

BW tonal与旧outer tonal共享同一算术核心；提取后的AST逐操作完全一致（哈希见source-links），没有改原舍入、阈值或mask。

48个新增完整原BW根宿主调用，算术/predicate不改，仅添加stark12/tonal67观察stores。四种RGB、参数0=0/4/15、tuning2/5、正负parameter2和两组guide/person；原曲线显式提供，未重跑旧批次：

| 原观察值 | 已知点 / unknown | 已知集合 / unknown | 已知域half位差 | 最大绝对误差 | 已知集合越界 |
|---|---:|---:|---:|---:|---:|
| stark12 | 48 / 0 | 48 / 0 | 0 | 0 | 0 |
| BW tonal67 | 36 / 12 | 24 / 24 | 41 | 0.00146484375 | 0 |
| 实际输出477 | 44 / 4 | 44 / 4 | 15 | 0.00146484375 | 0 |

内部unknown没有被最终分支掩盖。最终477的4个unknown是黑色且参数0==15选中的tonal域；其他未选中的内部unknown仍在结果中可见。已知集合最大盒宽约16708.326，明显不能支持高精度逆解。宿主2u/4u与sampler仍是假设，不把集合覆盖称数值吻合或原GPU精度证明。

`regress_tuning_layout.py`只重放保存的一个S11-H失败见证：正确field17匹配保存的内部tonal，错误field19匹配旧失败值，内部观察明确拒绝错包装，而最终492两者相同，确认最终混合会遮错。未重跑旧16组或505组。失败见证来自既有synthetic收据，原错误摘要与SHA保留。

147项回归通过。新增原参数0与245分离、未选内部unknown保留、选中黑色域拒绝、真实BW计算后集合及边界决策后传，以及禁止外供BW输出。旧24组合unknown、8叶域unknown、bright差异、S11新增未知域与原GPU/同帧缺口不变。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_bw_check.py /path/to/0010.ll.txt /tmp/new-bw.json
python3 research/styles-firmware-20261022/regress_tuning_layout.py /path/to/0010.ll.txt research/styles-firmware-20261022/evidence/tuning-failure-witness-s12a.json /tmp/new-tuning-regression.json
```

继续原调用图的video haze、后保护、通道混合和输出处理，再推进AIR7及guided filter上游。原GPU/同帧实际验收另列依赖；本阶段没有完整照片处理/逆解验收。
