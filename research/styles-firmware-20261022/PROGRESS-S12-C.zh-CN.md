# S12-C：真实 video haze 与主入口选择

同一 iPhone17,3 / 24A446 AIR10。`pixel_haze.py`实现完整renderVideoHazeCorrection：八个显式f32 SSRHaze字段1..8，双分母/half增益、luma正分支、chroma混合、两支mids、BG contrast/local与最终person混合。复用既有mids、contrast/local，未重写已验收算子。

原主入口493传的是原guide211，不是mixed guide350。501仅在tuning field17==7且haze field0 byte非零时选493，否则选492；即使最后未选中，结果对象仍记录内部haze unknown，不用最终输出遮错。

18个新完整原helper宿主调用：16组点域与16组集合域已知，6个half分量差异、最大绝对误差0.0009765625，已知集合越界0。另2组为显式零分母/增益分母退化负例，点/集合都拒绝，未删案例或缩mask。FP/sampler/2u/4u仍为宿主限定，不能作GPU或逆解精度证书。

150项回归通过，包括guide依赖、tuning/byte gate、未选内部unknown保留、原field类型和集合后传。旧24组合unknown、8叶域unknown、bright及S11/S12其他未知域与差异不变。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_haze_check.py /path/to/0010.ll.txt /tmp/new-haze.json
```

收据`evidence/native-haze-s12c.json`含原完整函数/模型/宿主/输入输出SHA。下一步仍为501后的保护/通道混合和输出，再到AIR7/guided filter上游。原帧RGB、haze参数、统计、curve与lookup未从成片恢复；无新下载、私人媒体、原GPU或完整照片逆解验收。
