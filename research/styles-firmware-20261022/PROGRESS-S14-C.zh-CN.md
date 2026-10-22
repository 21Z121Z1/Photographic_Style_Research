# S14-C：主入口393前工作域、guide与外围饱和度组合

同一iPhone17,3 /24A446。新`main_pre393.py`连接原source/ROI/masks→person/skin hint缩放→SRL version0/1/2→input transfer/HLG/CCM→reference196→linear CCM/base gain working286→cast2 semantic修改→precomputed或fallback semantic347→guide350→原BG352→原FG354→外围RichSat/smoothSat→392。矩阵仍只以原字面数与明确工作域识别，不猜P3/ICC，也不把linear源当成无风格原片。

person hint21<0跳过；非负时除cast.scalar21阈值，clamp/smoothstep并以f32.3为下限，再转half缩放person/skin。SRL version1仅开放(0,1)参数，version2复用完整semantic SRL且用缩放后的person96。code6及gain176完全复用AIR7模型；gain是原本已计算的量，仅新增返回字段。cast2正Tone仅改HR5/6，Tone<=0还改exposure2/3，零点归非正支；不确定符号两支包络，不取中心。

原ROI7/8采样guide211/214，再依post-caller语义LTM0/1和person96产生350。typed BG/FG只复用已有点控制器/叶；集合控制保留完整字段及guide/person/skin盒，无法证明的算子继续拒绝。外围355..392真实参数为half(color3)，负支f32*.8、非负支half平方后+1；仅>0进RichSat并使用colorBoost11.2，否则进smoothSat。随后按原保护量和person混合；独立观察374、389与392，不依最终混合遮错。

新宿主包装链接原main从入口直到392的**全部原指令**及递归原helper，保留算术/比较/FP属性；只改根ABI/名、在392后截断并增加17处观察。5个有针对性的单上下文：两种semantic路径、SRL0/1/2、cast0/2、正/负/零Tone与color、hint缩放与跳过、非零BG/FG叶、black负例。每例参数buffer独立重置，不声明原多线程参数写入或GPU行为。

结果：4个完整点域已知，所有37观察分量逐位一致；black例在FG354模型遇0除并unknown，保留其早期27个已知分量。合计175个已知half观察逐位一致，35个post-semantic f32字段也逐位一致。原宿主五例输出都有限；这不消除black模型的未证明域。最终4×3个392分量逐位一致，也独立报告饱和度374同样一致。

**5个集合域全部unknown**：前4例首个失败为BG352有限运算预算超限，black为FG354预算超限；此前source/CCM/semantic/guide与post-semantic已知集合均覆盖原结果，0越界。未调整阈值、epsilon、mask或输入范围，未把点证据写成集合通过。旧24组合unknown与8叶域unknown继续原样保留，属于局部模型/相关性工作，不是硬件阻塞。

175项回归通过。复用重构有AST证据：`gain_ratios`内曝光/GTC/比值branch与旧函数逐节点相同；preprocess除返回已计算gain外，运算body逐节点相同。native旧批次重跑0。早期合成fixture把同域BG/FG错误标成两个role域，被类型合同拒绝；仅纠正域标签，未改变数值或模型数学。

收据`native-main-pre393-s14c.json`、`ltm-refactor-proof-s14c.json`含原prefix/递归函数/模型/宿主/输入输出SHA、17处位差与每例首个unknown。34值cast、BG17/FG16/semantic7、source/guide/masks/ROI、CCM、GTC/whites与版本控制仍显式供给，不能称从照片恢复。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_main_pre393_check.py /path/to/0010.ll.txt /tmp/new-pre393.json
```

S14-B的真实epsilon.001、内部5位差及17941.5513宽集合仍有效；9个未定位消费者、bright差异、原GPU/同帧和IMG2810精确build均未解除。下一项最终RGBA打包/ROI写出单独验证，不把已验证片段相加为全照片/逆解通过。
