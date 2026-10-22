# S11-F：完整 warmth 根与共享保护/白平衡

同一 iPhone17,3 / 24A446 AIR10，继续真实neutralizing408→warmth409接口。`pixel_warmth.py` 实现完整renderWarmthCastAdjustments，包括protectMaskFilter、warmthFilter、whiteBalanceFilterAdjustments和whiteBalanceFilter；复用原Lab及算子，不重新拟合颜色。

完整34值cast块显式供给。原数组6/7/8分别按源指令取值，array7在f32中平方并缩放后才转half作高斯宽度；原最小half宽度保护保留。hue周期Gaussian的半/f32分工、quarter-power/YIQ变换、tint旋转、half映射后的gate、输入/输出clamp与人物混合均保留。

调用顺序不是三段串联：第一warmth从原RGB计算；whiteBalance也从原RGB计算；最后warmth从whiteBalance结果计算。人物权重最后混合第一与最后分支。没有把第一个warmth输出误送入白平衡。

新增32个原完整根helper宿主调用，全部递归原函数体不修改，llvm lifetime/memset用原声明，AIR数学用显式宿主shim，无占位。四种RGB、两个人物权重、first/whiteBalance/last/combined四个活跃profile：

- 点模型32组、96个half分量逐位一致，point unknown0。
- 集合26组可计算且覆盖原结果；另6组因独立区间包含负pow底数而拒绝，未缩输入或mask，未将点结果用于集合兜底。
- 没有重跑旧505组、neutralizing叶/根或旧mids/semantic批次。声明2u/4u仍是宿主包络假设，不是原GPU误差保证。

134项回归通过。新增测试核验人物极端权重的分叉、first分支不串入second、非零f32控制在原half映射后门内跳过、活跃集合后传。旧24个组合unknown、8个叶域unknown及S11-B/C未决项不变。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_warmth_root_check.py /path/to/0010.ll.txt /tmp/new-warmth-root.json
```

`evidence/native-warmth-root-s11f.json`保存版本、全部原函数/模型/宿主/输入输出SHA和全部失败域。下一项selective-color413仍需显式四行RGBA纹理与wrapper参数映射；它和外围cast、AIR7生产/guided filter仍未完成。无新下载、私人媒体或GPU运行；原GPU/同帧验收与照片逆解继续独立未验收。
