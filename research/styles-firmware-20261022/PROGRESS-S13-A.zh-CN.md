# S13-A：AIR7 增益生产核心

补齐同一iPhone17,3 /24A446 createLTMGainMap的SSA99..205。`ltm_gain.py`用强类型f32 CCM列、scale6与semantic7，在half工作域按原G+R再B顺序生成linear121，分别执行FG/BG曝光、上限min1、原GTC像素坐标采样、GTC混合，再除reference96，保留逐通道half门限。只复用现有Curve1D/curve_sample和算术，不重新拟合曲线。semantic0/1/5/6不进入该生产核心，留给下游LTM/HR。

10个新增原指令宿主调用，分别观察BG203、FG205、内部linear121，共90个half分量逐位一致，10点域/10集合域已知，集合越界0。包含原EPS=half0x1c04的相邻half、等号和零参考。集合最大盒宽5.23927；两支区间包络与2u/4u及理想像素线性clamp sampler是宿主限定，不能扩成GPU精度。

只在输出zero guard的非零支条件下交reference>=EPS，再做比值；不缩输入mask，不改变比较符号，也不取中心。保留原指令切片SHA8504ab1e5508692dbf4d027d62225d6cf4da9f5222fd6ee7a7ce9cd73120f009、原完整kernel SHA及动态宿主IR/输入输出/模型SHA；未上传AIR或二进制。

157项回归通过。此处reference96、sampled linear98、CCM、scale、semantic和曲线仍显式供给，早于99的SRL/transfer/CCM0/二维采样尚未接入；guided filter也未在此处应用。只称生产核心完成。旧unknown、位差与同帧/GPU/IMG2810身份缺口不变。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_ltm_gain_check.py /path/to/0007.ll.txt /tmp/new-ltm.json
```

下一步复用已有guided_reference_v3，先核同版三核与宿主对照，再推进生产入口和主输出变换。纹理生成的条件重放不等于原拍摄纹理恢复。
