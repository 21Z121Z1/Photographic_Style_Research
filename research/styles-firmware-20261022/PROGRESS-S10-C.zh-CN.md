# lighten与negativeLighten增量

接Shadows提交 `0e2dc30deb95a862be0dc03853d8452099cd4861`。`pixel_lighten.py` 独立保留两个完整原叶的guide重映射、pow/root域、各自luma权重、f32/half转换、两层混合、色度/外域分量；没有把negative叶当作把amount取负的同一函数。

新宿主对照各5 RGB×3 guide(.05/.4/.9)×3非零参数，共45组/135分量。positive参数+.1/+.5/+.9；negative叶的参数是由controller产生的正指数域1.1/1.4/1.8，不能错当负滑杆值。两个完整原叶均**逐位差异0，集合越界0，point/set unknown0**。原函数正文与明确数学shim比较，没有重跑任何已有native批次。

guide=0会使某个pow基底越过当前已证实数域，新增负例明确DomainUnknown，不设经验clamp、不称硬件阻塞。`all_pixel_leaves.models` 汇合已完成叶，集合fragment默认使用这些模型；whites仍必须单独提供其cubic-spline曲线，不能偷偷复用fallback GTC。未有叶或无法证域的叶仍fail closed。

新增3项回归验证guide依赖、集合包含、guide0未知和BG两段lighten确实接上Shadows与Lighten；当前98项单元测试通过。源SHA、非零激活和逐位结果见 `native-pixel-leaves-3.json`。2u/4u与宿主libm假设保持，仍未认证原GPU、完整BG/FG或照片链。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_pixel_leaves_check.py /path/to/private/0010.ll.txt /tmp/psr-lighten-new.json --leaf lightenFilter --leaf negativeLightenFilter
```

工作继续，下一组saturation及其后local/gammaContrast、underGrass、neck/underTone、smartContrast。没有新下载、私人媒体、ps/其他项目操作或分支合并。
