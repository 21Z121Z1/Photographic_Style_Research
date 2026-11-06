# Live Photo HDR 进展（baseline + IMG_8148 时域）

日期：2026-11-06。分支 `cursor/livephoto-hdr-baseline-temporal-aa8c`。没有改 `master`，没有合并。

并行分支 `research/livephoto-scene-grading-pilot-20261106` 由另一路 Codex 做场景引导调色试点。本分支没有检出、没有提交、也没有改那条分支。调色试点的补丁（`WORK.md`、`color_model.py`、`pilot.py`）只记在恢复清单里，没有落成源码。两边以后按目录合并：这里是 `livephoto_hdr/`，调色不要写进这个目录。

## 做了什么

1. 从 `source-patches.jsonl`（SHA-256 `33b50f8ccdc08513282c48f40f9f5f1613967f6ae0789a5d879f237e272ce64f`）恢复独立基线和 S12 独立副本。细节在 `livephoto_hdr/PROVENANCE.md`。S12 的 `cp` 本身不在补丁记录里；`validate.py` 和 `extract.py` 按 S12 raw L44 声明的来源做了拷贝种子，不是磁盘字节见证。
2. 便携合同：分段 Apple Log 反变换（常数未改）、full/legal 码值分开、有理数 PTS、`bypassed` / `native-delta-coefficients` / `styled-scene-fallback`、缺省标志不叫做 bypass、新目录输出且拒绝覆盖。
3. 用三组原始样本做了时域测量。样本在 gitignore 的 `input/`，没有提交媒体、帧或 GPS。Linux 上 Core Image / Metal / Vision / CMImaging 记为 blocked，不是成功。

单元测试：`PYTHONPATH=livephoto_hdr/src python3 -m unittest discover -s livephoto_hdr/tests`，9 项通过。

## 输入哈希

| 文件 | SHA-256 |
|---|---|
| IMG_8148.HEIC | `3cc28577d332b7a9d29a418b6f390b426d0ec1c8360a3dbb7aec4e4b5f04728c` |
| IMG_8148.MOV | `b095c9461fa4876e1e4fdcdae79d0e9a9753dbf62ad40b8a7ea6f7263e7e9ed5` |
| IMG_8147.HEIC | `40d2758b6b1b2462a2e4ff09a3a3f6de2f4a377530340702845a3339594fedac` |
| IMG_8147.MOV | `32c30f5283cc794f124813bb2e85eb1b708e580adeb454fdf06f7f72a94be4da` |
| IMG_8043.HEIC | `3b54aeaecd67416be2c971fb4e8bc1996d99292e32d6c029d3410eb29af7a8d1` |
| IMG_8043.MOV | `a4f4160d27728d05e85db0f6fb33cbf91340cb20969da7ac7dbe1ad63627ffa1` |

三组都是显式 `smartstyle.bypassed=1`，没有与主视频同尺寸的 linear Delta 轨。分类都是 `bypassed`。没有跑原生 inverse。

## IMG_8148 时域（本机实测，连跑两次结果一致）

报告：`livephoto_hdr/results/IMG_8148-temporal.json`。

- 主视频 56 帧，Apple Log 缩略图 28 帧（`logs` = `com.apple.rec2020.apple-log`）。解析出的显示 PTS 与 ffprobe 的帧 PTS 一致。
- 长空档在缩略图 11 与 12 之间：`11/15`（0.733… s）到 `13/10`（1.3 s），时长 `17/30` s。中间有 8 个主帧。
- 静帧时间是编辑列表空编辑 `373/300` = `746/600` s，落在这个空档内。
- 码值范围：亮度码 166..654，同时落在 legal 10-bit 窗口里。nclc 没有 range 位。本次 ffprobe `color_range=pc`，因此按 full range（`code/1023`）解包，没有改成 legal。`color_transfer=bt709` 不是场景 EOTF。
- 逐帧 `h`：56 个都对上主帧 PTS。最小 0.51611328125，最大 0.51904296875。照片 `h` = 2.0609331130981445。最近主帧的 `h_video/h_photo` = 0.25042699249668565。

留出缩略图（去掉一张真实缩略图，间隔被加倍；没有曝光拟合；Rec.2020 亮度，没有 P3 矩阵）：

| 方法 | 平均 MAE |
|---|---:|
| hold_nearest | 0.0688 EV |
| fixed_log | 0.0420 EV |
| motion_gated | 0.0477 EV |
| motion_ungated | 0.0484 EV |

在这组平均上，固定坐标的 log 插值优于运动补偿。运动补偿不是普遍更好的插值器。

第 46–55 帧空间跟随（分析网格 384×288，1 像素 = 5 个编码像素；相位相关，不是历史 gain 图）：

- 第 46 帧是精确缩略图 `407/200`。第 55 帧在最后一张缩略图 `1381/600` 之后，是单边片尾。
- 主视频结构从 46 到 55 的水平位移 **+70.38** 编码像素（垂直 +12.14）。
- `fixed_log` 与 `hold_nearest` 在这两个端点都不做形变，位移 **+57.15**，落后主视频 **13.23** 编码像素。
- `motion_gated` 位移 **+72.42**，相对主视频超前 **2.04** 编码像素。

这只说明：片尾单边时，把最后一张场景缩略图按主视频亮度光流扭到当前帧，结构位移更接近主视频。它不是历史那次约 118 编码像素、gain 落后 6–9 像素的复测。历史上的 gain 图不在这批输入里。GTM 和 LTM 没有做逆变换。

静帧线性缩略图已用分段 Log、照片自己的 Gain 和 OriginalRange 解开。与视频观测的未配准亮度 MAE 是 0.288 EV（11923 个有限像素）。静帧是 Display P3，视频是 Rec.2020，矩阵用的是 BT.709 系数假设，不是当时 Core Image 测到的基。这个数不是验收指标。

## 另外两组（独立检查，不是调色试点）

`IMG_8147`：36 主帧 / 23 场景帧，与容器 `nb_frames` 一致。静帧 `383/300` s。没有超过 2 倍中位间隔的长空档。留出 MAE：hold 0.116 EV，fixed_log 0.074 EV，motion_gated 0.144 EV，motion_ungated 0.175 EV。运动补偿在这组平均上更差。没有做 46–55 窗口。竖向显示矩阵没有单独旋转，测量在编码栅格上。

`IMG_8043`：解出的帧是 74 主帧 / 37 场景帧，并与 ffprobe 帧 PTS 一致。容器 `nb_frames` 仍写着 78 / 44，那是头字段，不是这次解出的帧数。静帧 `833/600` s。有一处较长间隔 `1/15` 到 `67/300`（0.1567 s，中间 1 个主帧）。留出 MAE：hold 0.082 EV，fixed_log 0.078 EV，motion_gated 0.342 EV，motion_ungated 0.370 EV。运动补偿在这里明显更差。

## 堵住的事

- 原生 inverse、Vision 光流、`CIAppleLogToLinear`、HLG/Main10 编码、PVT 封装：这台 Linux 没有这些框架。托管 macOS 上 SPI 构造函数曾经是 false。绿的可用性检查不能当成原生执行。
- `IMG_3673` 不在样本里。有真实 Delta 的 `native-delta-coefficients` 路径没有实样。
- 照片与视频的跨色彩空间配准、以及历史 gain 图的 6–9 像素复测，都还没有。

## 下一代理（Linux 上的 Codex CLI）

从本分支继续，不要切到调色分支上去改同一批文件。

1. 先读 `livephoto_hdr/results/IMG_8148-temporal.json` 和本文件。运动补偿只在 IMG_8148 片尾跟随上更接近主视频结构；留出平均和 IMG_8147 / IMG_8043 上它更差。不要把它写成已经胜过固定 log 插值的默认算法。先查小运动和竖屏编码栅格上光流为何拉高误差。门限 0.05 和 1.5 像素（按 384 宽度换算）来自恢复的 `fit.py`，这次没有按测试集再拟合。
2. 有 Apple GPU 的 Mac 才能做：useCase 2 inverse、把本机分段 Log 和 `CIAppleLogToLinear` 再对一次、用 Vision 光流替换这里的搜索、按 TN3145 写出新文件名的 Main10 HLG，并核对 PTS、光圈、方向、辅助轨和 content identifier。不要覆盖原始文件。
3. 拿到 `IMG_3673` 后再测 Delta 路径。不要用这三组 bypass 样本宣称 inverse 已经验证。
4. 调色试点继续留在它自己的分支。合并时只接目录，不要把 GTM/LTM、场景参考和显示 look 揉成一步。
