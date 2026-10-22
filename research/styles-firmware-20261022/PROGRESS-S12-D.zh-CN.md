# S12-D：主入口保护与 BW 通道混合

同一 iPhone17,3 / 24A446 AIR10。补齐501后的真实502..566分支及完整renderChannelMixForBWCasts。保护原样保留texture10 presence、f32 cast19小于.01跳过（无abs，等号进入）、raw stats2/3/4.field4的Lab角度、cast20平方宽度、protectMaskFilter(true)与color476混合。主入口切片仅重命名SSA/块及移除metadata/call attrs，算术与控制流不变；完整递归helper保留原FP属性。

通道混合使用SSRParams0（不同于解析245）、SSRTone17..19（不同于tuning field17/byte652）、原始stats与person96。cast4用显式三项tone权重，cast15用编码颜色的平方和除通道和；其余code原根函数直通。统计参考先转half再走既有本版Lab矩阵及有符号pow，不擅自encode或clamp。复用已验证的encode/decode、Lab及保护叶。

| 新宿主调用 | 点已知 / unknown | 集合已知 / unknown | half分量位差 | 最大绝对误差 | 已知集合越界 |
|---|---:|---:|---:|---:|---:|
| 502..566保护 | 15 / 0 | 15 / 0 | 0 | 0 | 0 |
| 完整通道混合567 | 22 / 2 | 22 / 2 | 15 | 0.000732421875 | 0 |

保护含.01的相邻f32三点，另含texture缺席、负amount、黑/灰输入。通道混合2例unknown为cast15黑输入的无保护0/0，原宿主输出非有限；保留half位型及非有限计数，JSON显示值为null，不改成0。已知集合最大盒宽分别约.00543与.14346；覆盖不是数值吻合。2u/4u、C libm与sampler仍是宿主假设。

`pixel_post_chain.py`连接computed-BW492→haze501→保护566→通道567，拒绝点中心代替上游集合，保留边界决策、首个unknown和未选中的内部haze unknown。接口测试不等于组合宿主或全照片通过。完整34值cast、stats、tone、curve、lookup和原RGB仍是显式上下文，未从成片恢复。旧24组合unknown、8叶域unknown、bright差异、tuning布局失败见证及独立tonal468观察全部不变。

154项回归通过。数字对照后只增加输入类型断言；当前模型重放全部保存输出，点/集合状态与误差指标相同，未重复宿主调用。收据分别为`native-channel-mix-s12d.json`、`native-postprotect-s12d.json`和对应`*-replay-s12d.json`，含原文/模型/宿主/输入输出SHA及原始half位型。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_channel_mix_check.py /path/to/0010.ll.txt /tmp/new-channel.json
python3 research/styles-firmware-20261022/native_postprotect_check.py /path/to/0010.ll.txt /tmp/new-protect.json
```

继续本版输出变换与AIR7/guided filter生产。无新下载、私人媒体或原GPU运行；本阶段不是完整逆解。
