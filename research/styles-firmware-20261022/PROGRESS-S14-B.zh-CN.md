# S14-B：源二维采样、真实格式/epsilon 与 producer→guided→ROI 组合宿主对照

同一iPhone17,3 /24A446。S14-A先纠正SSA557保护的过期标签，关联S12-D的502..566保护收据，native重跑0。此处继续源纹理→完整AIR7→guided三核→AIR10 block290；没有把S13-D的native_calls=0接口见证改成原生证书。

只读挂载本任务已取得的SystemOS镜像，定向导出4个方法共2068B，每字与cache映射独立核对；随后正常解除本次挂载。两分配包装0x1d4340530/0x1d42ccaf8把format参数w2置0x73，已核本机Metal SDK为RGBA16Float115。small BG/FG尺寸取self+0x30，最终图尺寸取原input self+0x20；原AIR7写RGBA并固定alpha1。原guided coefficients/means网格取guide，最终apply取输出网格。源/guide实际帧格式仍须外供，本有界组合只接受明确R16/RGBA16存储。

真实调用epsilon现在核为常量：0x1d44e3d78原4B `6f12833a`，f32=0.0010000000474974513；radius1。旧.05/.03样例继续仅为外供参数条件对照。未改旧收据或用更大epsilon消除退化。

坐标按原指令实现：AIR7为f32(uint16 gid+.5)/destination6尺寸，三个源共享同一normalized/clamp-edge/linear坐标；GTC使用原half宽度/索引后f32+.5的pixel坐标。consumer ROI5/6为byte48/64，分别scale*f32(logical gid+.5)+offset。ROI12只影响uint16输出地址27，不额外加进源UV29。producer primary选self28非空否则self20，guided guide始终self20；第二新样例刻意分离两者。CCM和producer/post-caller semantic分别显式供给，当前组合cast0，未偷含cast2参数修改。

`air7_full_host.py`链接完整原createLTMGainMap及SRL/transfer，保留FP属性/比较/原常量load和两种原写出路径；只增加7处独立观察store。guideds沿用原三核，consumer复用原block290切片并独立观察305/308/332/320。所有buffer/纹理均为新合成输入。

两个新小图上下文，producer各2×3，guide分别3×4及4×5，consumer各3个logical ROI点（含边缘clamp），共210次原kernel/块宿主调用。按独立上下文去重，避免把同一producer在3个ROI重复计数：

| 观察范围 | half分量 | 位差 | max绝对误差 |
|---|---:|---:|---:|
| producer七处：source24/SRL34/linear37/reference96/working121/BG203/FG205 | 252 | 0 | 0 |
| 原RGBA写出（含alpha） | 96 | 0 | 0 |
| guided的a/b/mean_a/mean_b/output，BG+FG | 1280 | 5 | .0009765625 |
| 最终consumer335，6调用 | 18 | 0 | 0 |

内部5位差在FG a与mean_a，最终guided/consumer恰好没有显现；原因尚未单点隔离，不先归因libm或GPU。保留每处误差和原输出hash，绝不以最终逐位一致遮住内部差异。

点/集合均6个consumer上下文已知，已知集合越界0。但纹理局部texel凸包与独立区间丢失相关性，真实.001下最大条件盒宽**17941.551250823606**。这是有限覆盖，不是数值吻合或可用逆解精度；旧155.125包络、24组合unknown、8叶域unknown、bright与其他差异、9个未定位消费者全保留。集合直接沿完整V纹理传递，未取中心、改阈值、改epsilon或缩输入mask。

171项回归通过。新ROI单测同时保留half mix在weight1仍可能不等于b的舍入次序；只修正了测试的identity假设，未修改模型/原算术。没有重跑此前27例block290、505叶、旧guided批次或旧SRL/transfer批次。

收据：`ltm-contracts-s14b.json`、`native-ltm-roi-chain-s14b.json`、`ltm-roi-chain-summary-s14b.json`和`ltm-format-s14/manifest.json`，含源/模型/IR/输入输出哈希。`pixel-inventory-s14b.json`区分新组合域与未验证项。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_ltm_roi_chain.py /path/to/ios-air-directory /tmp/new-chain.json
python3 research/styles-firmware-20261022/summarize_ltm_roi_chain.py research/styles-firmware-20261022/evidence/native-ltm-roi-chain-s14b.json /tmp/new-summary.json
```

这是原指令的CPU宿主组合比较，sampler仍为明确v3量化线性/half tie-up假设、GTC为既有理想pixel-linear假设，单线程imageblock不同于原多线程GPU。原source/guide格式与同帧身份、CCM/统计/masks/ROI、34值cast与lookup均未从成片恢复。继续393前组合、外围RichSat/smoothSat及最终ROI打包；没有新下载、私人媒体、ps重试或原GPU执行。
