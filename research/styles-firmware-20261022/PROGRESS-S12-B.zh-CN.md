# S12-B：原外围指令直接调用实际BW，保留三份内部观察

同一 iPhone17,3 / 24A446。`computed_bw_host.py`将原BW477调用接回原414..492指令，链接完整BW原函数及递归叶，拒绝冲突的共享IR定义。BW输出不再由外部向量代替。RGB413、highlight398、原参数0和解析245、tuning17、tone20/65、guide/person及whites curve仍显式供给；未从成片恢复。

18个新增完整连接案例（两种彩色及灰色、参数0/245刻意分离、tuning2/5），观察结果分别报告：

| 观察值 | 已知点 / unknown | 已知集合 / unknown | half位差 | max绝对误差 | 集合越界 |
|---|---:|---:|---:|---:|---:|
| 原outer tonal468 | 18 / 0 | 18 / 0 | 9 | 0.00146484375 | 0 |
| 原BW stark12 | 18 / 0 | 12 / 6 | 0 | 0 | 0 |
| 原BW tonal67 | 18 / 0 | 6 / 12 | 15 | 0.00146484375 | 0 |
| 原最终492 | 18 / 0 | 15 / 3 | 3 | 0.00048828125 | 0 |

不以最终结果掩盖内部域或差异。集合有严重松弛：最终最大盒宽约20630.775，不能用于高精度逆解。最终3组unknown及内部未知域全部保留，旧24组合、8叶域、bright与其他阶段差异不变。2u/4u和宿主sampler仍非GPU证明。

观察包装合同修正：原BW函数声明memory(read)，添加global trace stores后应改为memory(readwrite)。现在只修正该内存摘要，保留全部原FP属性与算术/predicate；合并时原定义仍有哈希。只用S12-A保存的**一个**BW输入回归，stark/tonal/最终三份输出均逐位等于保存值，没有重跑48组。S11-A local+gamma观察包装同样修正内存摘要，用一个保存见证确认原值、SSA157/166与两种fast-flag诊断结果不变。旧收据保留，此补充纠正可用于优化器的观察合同，不把原GPU内存或数学合同混同宿主修改。

147项回归通过。tuning field19失败见证及独立tonal468观察继续保留；没有新下载、私人媒体、ps重试或原GPU运行。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_computed_bw_check.py /path/to/0010.ll.txt /tmp/new-computed-bw.json
python3 research/styles-firmware-20261022/regress_bw_observer.py /path/to/0010.ll.txt research/styles-firmware-20261022/evidence/native-bw-s12a.json /tmp/new-observer-regression.json
```

收据为`native-computed-bw-s12b.json`、`bw-observer-regression-s12b.json`、`local-gamma-observer-s12b.json`，各含精确输入/原函数/模型/宿主哈希。接着推进后续haze/保护/通道混合/输出，以及AIR7与guided filter生产；本阶段不是完整照片处理或逆解验收。
