# 摄影风格盲重建与最终文件 Texture 回放

[English](README.md) | 简体中文

实验、候选代码和数值证据放在这个研究仓库。XDRemux PR85 只接收验证后的产品修复。
直方图候选在三张对照图的负向 Tone 上都有退步，暂不迁入产品。

脚本从原片隔离出编码的 SDR/HDR 基图，再调用 XDRemux 的同一个 Rust 生成器重建资源。
生成结束后，评估器才读取原片摄影风格资源。候选对照不替换任何原片资源；资源归因模式
则明确标记它所替换的资源组。

## 已保留的原生结果

[原始数值报告](evidence/20261029-histogram/native-report.json) 与
[来源记录](evidence/20261029-histogram/provenance.json) 对应迁移前实际测量的生成器、
渲染器与产物，报告原样保留。

| 对照图 | 分组 | 默认平均 RMSE | 直方图候选 | 降幅 |
| --- | --- | ---: | ---: | ---: |
| IMG_2600 | 校准 | 0.0330819025 | 0.0308088261 | 6.87% |
| IMG_2604 | 校准 | 0.0287555617 | 0.0252179764 | 12.30% |
| IMG_2608 | 留出 | 0.0352662714 | 0.0326951252 | 7.29% |

指标取 Tone -0.5 与 +0.5 的平均值，两张校准图合计降低 9.40%。三图负向 Tone 的
RMSE 分别增加 0.39%、6.09%、2.65%。中性 Tone 和 Color -0.5/+0.5 与参考误差为零。
三份隔离输入与六份重建文件的全分辨率原生 SDR/HDR 基图误差也为零。这些公开对照图
以前参与过研究，留出只是固定场景分组，不代表新收集的未知数据集。

候选采用局部量化直方图中位数，以及 `research/hdr-native/lightmap_model_s55.py`
保留的 half 编码步骤；d 图使用经过 GTC 处理的 RGB。s56 的 269 例原生合成对照是
历史条件编码尾部的证据，不证明完整相机颜色、统计和 ROI 流程。图像最大值归一化、
算术 RGB 引导图和整数分块仍是近似。

原生测量范围是 macOS 26A434 上的 `PISemanticStyleFilter useStyleEngine=NO`。
完整引擎、原生反向处理、key-1/Delta 与 Photos 保存重开均未由此证明。此前原生反向
处理出现 `desc != nil` 断言。公开 Texture 对照图是商店模特，尚未验证用户提供真人
样张上的肤质效果。

## 运行

在 XDRemux 的一次性检出中使用 `cf1e790e33e04202745bc34e52f1e414c02e290d`，按英文说明应用
[`xdremux-research.patch`](xdremux-research.patch)，构建研究入口和 Apple adapter。
补丁对共享 Rust 生成器增加候选参数，不复制另一个生成器，也不留在 PR85 中。

Python 从本研究仓库运行，`PYTHONPATH` 指向外部 XDRemux 检出，复用它的 HEIF 检查器
和解析兼容工具。渲染器与公开对照图另行检出固定版本
`37dd551a949047ed14580efa0c0a2556922791b5`。完整命令见英文说明。

```bash
PYTHONPATH=/absolute/path/XDRemux python3 -m unittest discover -s research/styles_fidelity/tests -t . -v
```

需要 NumPy、Pillow；原生步骤还需要 macOS、Apple adapter 和 HEVC 提供器。迁移后的
检查由现有 `styles-native-reference.yml` 工作流承接，来源 JSON 区分产品提交与实验补丁。

`corpus`、`isolate`、`split` 用于压缩包目录、基图隔离和固定场景分组；`blind` 保留联合
曝光与增益实验。`texture` 从最终编码资源回放存储或重算的统计，其 `--research-root`
需指向另行检出的 `2bc4e3d16fc2c6028cdf708f06d79cf3be42a6d5`。
各模块提供 `--help`。用户提供的人像保留在公开 Git 和 Actions 产物之外，只上传数值、
哈希和日志。

## 迁入产品的条件

先消除负向 Tone 退步，在更多场景组上重新测量 Tone/Color 联动，再把候选迁入 PR85。
原生反向处理、真人样张的最终 HDR Texture 需要分别验证。PR85 保留的 HDR 容器修复
由其产品回归单独覆盖。
