# S11-G：selective-color 条件模型与cast集合前缀

同一 iPhone17,3 / 24A446 AIR10。`pixel_selective.py` 覆盖完整renderSelectiveColorAdjustments及selectiveColorFilter；复用原Lab、皮肤transfer和既有2D采样器。模型声明输入是显式4×360 RGBA half texture，严格校验尺寸与工作域，不声称从CPU证明所有实际lookup都采用该尺寸，更不代表原lookup生产器已恢复。

角度→f32度数→half clamp/half+.5→归一化u，四行y=(row+.5)/4，person/skin/sky混合次序、RGBA分别控制hue/saturation/luminance/gamma均按原指令。三组cast颜色按标量9/10/11的非零bool门解码，再转Lab，分成低/中/高亮偏移。输出mix、person的反向混合、gamma、chroma零分母及exterior/clamp均保留，零域不自动补值。

16个新完整原根helper宿主调用，原完整函数体及递归叶不修改。显式RGBA宿主shim由旧S10-A三通道2D采样器仅扩为四通道，归一化linear/clamp、f32插值后half仍是宿主假设。合成纹理四行及四通道均非恒定，公开生成算法和half SHA，不使用原Apple纹理或私人媒体。

- 8个点域已知，24个half分量逐位一致；8个点unknown保留。
- 7个集合可计算且覆盖原结果，最大盒宽`0.9159617216374462`；9个集合unknown保留。宽盒不能支持高精度逆解。
- 灰/黑色等pow或零分母拒绝没有从案例中删除，也没有把人物mask或系数中心替代原输入。

`cast_chain.py` 接真实404→408→409→413，要求完整cast字段、显式统计与texture，并保留原tone边界决策。任何算子首次unknown都返回其输入集合与原因，不经过中心点兜底。它仅是此cast前缀，不称外围混合/BW/整张照片管线通过。

139项回归通过：四行RGBA通道、尺寸拒绝、非单调区间采样、texture本身非零激活、黑色拒绝、未知上游保留。没有重跑旧批次；旧24个组合unknown、8个叶域unknown和S11-B/C/F未知域均不改记通过。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_selective_check.py /path/to/0010.ll.txt /tmp/new-selective.json
```

收据`evidence/native-selective-s11g.json`含全部函数/模型/宿主/输入输出SHA。下一项为主入口外围cast选择与BW混合；AIR7/guided filter生产、原GPU/同帧与IMG_2810精确build仍未验证。没有新下载、私人媒体或照片逆解验收。
