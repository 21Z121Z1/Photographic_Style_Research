# ShadowsFilter与ShadowsNegativeFilter增量

接S10-A提交 `2cc8e18d91819ab30c9b84606f3d8a42d3bcf827`，没有新下载、照片或原GPU输入。本增量只激活这两个新叶，不重跑mids、semantic、block290及前三个叶。

`pixel_tonal.py` 用已提交的half/f32双后端独立实现两个完整函数。guide、amount与工作RGB均显式给定，保留guide影响的q符号分支、blue mask、dark boost、root混合、外域分量；负路径还含按原RGB跨度保持色度的分支。positive路径的部分shape/权重继续在f32算，negative路径相应部分在half算，未为了共享代码合并成同一精度顺序。外域相加顺序也按这两个原函数保留。

原完整函数新宿主对照，每叶5种RGB×3个guide(.05/.4/.9)×3个非零amount，共45组；Shadows取+.1/+.5/+.9，Negative取−.1/−.5/−.9。两叶各135分量，**逐位差异0，集合越界0，point/set unknown均0**。黑点、gray和超出[0,1]的输入也保留在这些合成案例中。

原函数正文/依赖未改，没有未实现占位；只补宿主fast_fmax等intrinsic解析。源SHA、原函数SHA、输入输出SHA和逐案例结果在 `native-pixel-leaves-2.json`。常规2u、pow/sqrt4u仍是显式宿主假设，非Apple GPU精度证明。测试框架只是按新叶选择guide/amount，不重新执行已有叶批次。

新增三项回归验证guide依赖、黑点、gray/HDR外域、集合覆盖与非零BG adapter；总95项单元测试通过。接口继续接区间并在域不明时fail closed，没把这两个叶或counterfactual renderer值当完整照片链通过。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_pixel_leaves_check.py /path/to/private/0010.ll.txt /tmp/psr-shadows-new.json --leaf ShadowsFilter --leaf ShadowsNegativeFilter
```

继续下一组saturation/lighten，再处理local/gammaContrast、underGrass、neck/underTone、smartContrast。9槽不重扫旧范围；原GPU/原帧/IMG_2810身份依赖独立保留。
