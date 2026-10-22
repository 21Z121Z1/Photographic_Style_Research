# S10-D：saturation 两叶，保留黑色定义域缺口

范围仍为 iPhone17,3 / 27.0.1 / 24A446，已取得 CMImaging AIR10；产品 Styles 2、内部 V1 与样张 metadata 编号不互换。没有下载、私人媒体或 GPU 运行。

`pixel_color.py` 独立实现 `smoothSatFilter`（AIR10:4508–4587）与 `RichSat`（4079–4261）：输入先 clamp，f32 三列矩阵、带符号幂、half 色相角与半径，再逆矩阵与输出 clamp，按原顺序补回 HDR/负值 exterior。矩阵只命名为本 build 的工作颜色变换，不推定其 ICC/相机颜色空间。RichSat 还包括归一化色度距离、强度门、色相 exp 权重及均值保持。

控制器给 RichSat 的 strength 固定 3；独立叶对照额外用 4 激活 `gain > .75 && strength > 3`，不宣称该分支在当前控制器可达。smoothSat 的低增益门在 gain 扩为 f32 后严格 `< 0x3F947AE140000000`；相邻 half 回归覆盖该门。

`leaf_numeric.py` 新增显式 atan2、sin/cos 内部极值、exp、平方和布尔集合。负 x 轴切口/原点的角度集合保留全角包络；不将边界集合喂成中心。2u 算术、4u 超越函数仍是宿主比较假设，不是 GPU 误差保证。

新增原完整叶宿主对照（未重复已验收批次）：

| 原 helper | 非零组 | 点模型 unknown | 集合 unknown | 已知域 half 位差 | 集合越界 |
|---|---:|---:|---:|---:|---:|
| smoothSatFilter | 15 | 0 | 0 | 0 / 45 | 0 |
| RichSat | 30 | 6 | 6 | 0 / 72 | 0 |

6 组为黑色输入，归一化分母为零。宿主 shim 的 min/max 有有限结果，不足以确定原 GPU 的 NaN/fast-math 行为；模型和控制器适配器均 fail closed。这是明确数值定义域缺口，不称硬件阻塞。所有案例（含 unknown）都保留在收据；没有将 unknown 计为通过。新增 C libm 与向量转换/dot/sign shim 的完整哈希也在收据中。旧已验收算子的算术未改动，只新增能力，未重复宿主批次。

103 项单元回归通过。复验：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_pixel_leaves_check.py /path/to/0010.ll.txt /tmp/new-saturation-receipt.json --leaf smoothSatFilter --leaf RichSat
```

原 helper 原文 SHA、输入/输出 SHA、模型/宿主源码 SHA 见 `evidence/native-pixel-leaves-4.json`。原 AIR 不入库。此阶段补齐独立叶与接口；尚无完整 helper 数值、原 iOS/GPU 或照片逆解验收。local/gamma、underGrass、neck/underTone、smartContrast 等接着独立推进。
