# S11-H：外围cast选择与条件BW混合，单独观测内部tonal

同一 iPhone17,3 / 24A446 AIR10。`outer_cast.py` 覆盖主入口414..492的tonal/airy/contrast、cast选择与两个BW混合权重；复用原叶，保留half/f32、原luma正分母门和tuning条件。tuning为原SSRParams **field17 / byte652**，不是float field19。raw cast245及tuning415均需明确shader数值，不从UI名称推测。

真实数据流：tonal468只在cast245==3进入BW输入472；否则472为selective413。color476只在cast245==4取472，否则取highlight398。BW477原调用读取472，但本阶段其像素算法未建模；最终483/489分别用SSRParams4/5，492再用person混合489→483。

条件接口要求显式同调用上下文的BW477 half结果。缺失时返回unknown，即使blend权重是0也不以占位兜底。给定BW结果不代表BW算法通过，`BW_algorithm_verified=False`。`outer_cast_chain.py`串接已有集合前缀并保留producer边界决策，拒绝中心输入，未称整张照片管线通过。

原指令摘录414..492仅作SSA双射，BW477调用改为显式输入，去除metadata/call属性，其他算术和predicate不改。记录父函数/原摘录/BW调用行SHA与外部SSA映射。额外导出tonal468，防止显式BW输入遮掉未验证内部算术。

16个新增开发案例，独立观测结果：

| 对象 | 已知点/集合组 | half位差 | 最大绝对误差 | 已知集合越界 |
|---|---:|---:|---:|---:|
| 条件最终混合492 | 16 / 16 | 0 | 0 | 0 |
| 内部tonal468 | 16 / 16 | 4 | 0.0009765625 | 0 |

不能因第一行通过称tonal逐位吻合。宽包络及2u/4u仍是宿主假设，原GPU未运行。

开发勘误：首次宿主wrapper把tuning写入field19，最终BW条件输出没有暴露该错误；增加tonal468观测后发现24个分量差异、max0.021484375。按原AIR改为field17后，仅重跑这16个新增开发案例，模型方程、阈值、输入与误差预算均未改。失败开发收据保留本地，哈希与摘要见`s11h-development-erratum.json`。没有重复505组、原mids/semantic或已验收叶批次。

143项回归通过：cast3/4双输出身份、无BW时严格unknown、未选highlight缺失不污染cast4、原边界决策与未知上游保留。旧24个全激活集合unknown、旧8个叶域unknown及S11-B/C/F/G新增unknown没有改记通过。

当前新增链已覆盖skin、高光与亮度分叉、neutralizing、warmth、selective和该外围条件混合；未完成BW477像素算法、后续video haze/保护/通道混合/transfer、AIR7 createLTMGainMap与guided filter生产及lookup来源。已有资源可继续建模这些项，不能称其全是硬件阻塞。原GPU/同帧真实照片验收另缺匹配运行与原帧上下文，IMG_2810仍缺精确capture build。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_outer_cast_check.py /path/to/0010.ll.txt /tmp/new-outer-cast.json
```

收据`evidence/native-outer-cast-s11h.json`含内部与最终两份观察，函数/模型/宿主/输入输出哈希。没有新下载、私人媒体或GPU运行；完整照片处理与逆解仍未完成。
