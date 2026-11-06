# 复跑 IMG_3673 照片与视频缩略图对照

这套实验脚本针对本次 IMG_3673 配对样本，验证照片与视频的相对线性亮度关系。它要求本机 Apple Silicon、可用的 Metal、Xcode command line tools，以及 Python 的 `numpy`、`scipy`、`Pillow` 和 `matplotlib`。照片解码使用本机私有 Core Image filter，系统版本会影响可用性。

1. 保留两个原件在以下路径。

   ```text
   /Users/retriedstormtrooper/Downloads/IMG_3673.HEIC
   /Users/retriedstormtrooper/Downloads/IMG_3673.mov
   ```

2. 执行完整实验，末尾输出目录必须尚不存在。

   ```bash
   python3 /Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/src/run.py \
       /Users/retriedstormtrooper/Downloads/IMG_3673.HEIC \
       /Users/retriedstormtrooper/Downloads/IMG_3673.mov \
       /private/tmp/IMG_3673-thumbnail-pair-recheck
   ```

3. 打开新目录下的 `verification.json`，确认 `technicalPass` 为 `true`。查看 `analysis/results.json` 的 `primary`、`metadataScaleHypothesis` 和 `symmetricLowPassComparisons`，分别读取原生全频结果、元数据尺度以及共同低频带的结果。

4. 打开 `analysis/comparison.png` 查看数值比较图。使用 `analysis/comparison.svg` 导出矢量图。逐步命令和退出码保存在 `steps.json`，各步骤输出保存在对应的 `.log` 文件中。

当前已完成的运行在 [verified-final](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/verified-final)。其完整解释见 [REPORT.zh-CN.md](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/REPORT.zh-CN.md)。

源码入口如下。

| 文件 | 工作 |
| --- | --- |
| [run.py](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/src/run.py) | 编排完整实验，构建原生解码程序，生成技术验证收据 |
| [extract.py](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/src/extract.py) | 从 HEIF 提取缩略图压缩载荷和摄影风格元数据，保留压缩数据重新封装 |
| [decode.m](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/src/decode.m) | 原生照片与视频解码、PTS 和元数据读取、颜色空间转换 |
| [analyze.py](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/src/analyze.py) | SDR 几何配准、曝光留出验证、传递函数与空间带宽对照 |
| [plot.py](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/src/plot.py) | 输出 PNG 与 SVG 科学比较图 |

这些脚本不覆盖原始媒体，也不写入 PVT。检查条件包含本样本的尺寸和 28 帧辅助缩略图事实，不能把脚本直接视为任意实况照片的通用转换器。
