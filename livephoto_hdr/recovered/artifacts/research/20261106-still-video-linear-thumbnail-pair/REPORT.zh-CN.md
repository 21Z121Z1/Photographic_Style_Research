# IMG_3673 照片与视频 LinearThumbnail 的场景参考对照

本次实测支持把视频 LinearThumbnail 作为经过尺度归一化的低频相对场景参考。在同一 PTS、同一线性颜色空间、固定几何配准和共同空间带宽下，视频与照片的亮度关系接近斜率 1。照片与视频并不直接使用相同的数值尺度。原生私有反变换与完整分段 Apple Log 反变换在暗部也有可测差异。

最有说明力的结果来自元数据给出的尺度，而非像素拟合。照片的 `smartstyle-info.h` 为 `2.0376346111297607`，锚点视频帧的 `h` 为 `0.5091552734375`。两者之比为 `0.24987565025468442`，对应 `−2.0007177735683332 EV`。将完整分段 Apple Log 解码的视频线性值乘以这个比例，并对两路施加相同的固定低通后，留出区域平均绝对亮度误差为 `0.07110056 EV`，诊断 log 斜率为 `0.98816635`，log 亮度相关系数为 `0.99506838`。

这项低频结果没有拟合曝光、曲线或局部增益。直接比较原生解码的 128×96 像素时，单一曝光拟合后的误差仍为 `0.24224705 EV`。两项结果共同限定本次结论，低频一致性不能替代逐像素一致性。

所有分析代码均为本次独立实现。实验没有使用另一个模型的 v2 实现或报告，也没有使用 subagent。原始媒体保持不变。本次只完成这对样本的数值对照，没有重编码视频或改写 PVT。

输入身份如下。

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| `/Users/retriedstormtrooper/Downloads/IMG_3673.HEIC` | 3,284,712 | `f3f8cd98836b071d85db8f4373ef403edfd995608b9dc7089201d144947ea5de` |
| `/Users/retriedstormtrooper/Downloads/IMG_3673.mov` | 3,727,953 | `9409a811e618bc6c11592b40246b5b6c1ce2dfffdb0aa63bd58741646b4a9b37` |

运行环境为 Apple M1 Pro、macOS 27.3、build 26C5035r。最终完整复跑目录是 `verified-final`。机器可读数据见 [results.json](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/verified-final/analysis/results.json)，原生解码事实见 [decoded.json](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/verified-final/decoded-isolated/decoded.json)。

照片的 LinearThumbnail 是 HEIF item 94，压缩图像为 1024×768、10-bit，辅助类型为 `tag:apple.com,2023:photo:aux:linearthumbnail`。`src/extract.py` 从原文件复制其压缩数据，重新封装成单图 HEIF，再由本机 ImageIO 和 Core Image 解码。压缩数据的 SHA-256 为 `daa7302e218d3e3c2441968c63546c6f8cd953809c736dd1dad017f7affe015f`。最终验证程序确认封装后的 mdat 与原图压缩载荷相同。

只修改 `pitm` 不能可靠地让原生解码器输出隐藏的辅助图。早期尝试中，ImageIO 返回的是 5712×4284 主图。最终实现移除辅助图的角色关系，以独立单图封装解决这个问题，并把原生解码的 1024×768 尺寸作为必要验证条件。失败尝试保留在本目录早期子目录中，最终结果不使用这些数据。

照片按照已知的静态摄影风格原生顺序解码。

```text
原始 RGB code values
→ CIAppleLogToLinear
→ 除以 i.Gain = 8.150538444519043
→ clamp 到 [−0.00811004638671875, 0.9892578125]
→ 解释为 extended-linear Display P3
```

视频辅助轨通过 `LogTransferFunction` 识别，本样本为 track 3，尺寸 128×96，共 28 帧。缓冲区给出 Rec.2020 原色和 `com.apple.rec2020.apple-log`。视频使用 AVAssetReader 解码为未施加颜色管理的 RGBAHalf code values，再执行反变换。线性 Rec.2020 到 extended-linear Display P3 的变换由本机 Core Image 和 ColorSync 执行，Python 对照使用从同一原生变换测得的基向量矩阵。

主视频的 `still-image-time` 是 `881/600 s`，即 `1.4683333333333333 s`。主视频第 44 帧、LinearThumbnail 第 22 帧具有完全相同的 PTS，帧号从零开始。本次没有对时间插值。主视频编码画布为 1920×1440，clean aperture 为 `(88, 66, 1744, 1308)`。最终比较使用完整编码画布的对应关系。把主视频 clean aperture 的几何变换直接套到未裁切的辅助缩略图上，会使本次误差升至约 `0.806 EV`。

几何变换只在照片 SDR 主图与锚点视频 SDR 主帧之间求解。结构相关系数从 `0.86502907` 提高至 `0.98957218`，然后冻结同一个仿射变换，用于全部线性解码对照。LinearThumbnail 的数值不参与几何拟合。照片线性缩略图先在原生 1024×768 上变换，再按面积降采样到 128×96。

最终比较扣除 5 像素边界，只保留有限、正亮度样本，再按照片参考亮度排除最低 2% 和最高 0.5%。共同评分区域共 9,894 像素。8×8 交替空间块中，4,958 像素用于拟合单一曝光，另 4,936 像素用于评分。所有表中误差均来自后一组。固定元数据尺度的结果使用同一评分区域，但曝光不由前一组拟合。

亮度误差定义为 `abs(log2(k × Y_video) − log2(Y_photo))`。平均值和分位数的单位是 EV。诊断斜率来自 `log2(Y_photo) = a × log2(Y_video) + b`，只用于检查线性关系，未将这条拟合曲线应用到评分像素。

| 解码与空间处理 | 视频到照片尺度 k | 诊断斜率 a | 平均绝对误差 EV | 中位绝对误差 EV | P90 EV |
| --- | ---: | ---: | ---: | ---: | ---: |
| 原生私有反变换，128×96，拟合一个曝光 | 0.23702026 | 1.08950587 | 0.24224705 | 0.16780094 | 0.54241051 |
| 完整分段 Apple Log，128×96，拟合一个曝光 | 0.24587209 | 0.95605528 | 0.22913956 | 0.15317202 | 0.51313508 |
| 原生私有反变换，两路固定 σ=2 低通，元数据尺度 | 0.24987565 | 1.13369256 | 0.09211800 | 0.02553301 | 0.30464607 |
| 完整分段 Apple Log，两路固定 σ=2 低通，元数据尺度 | 0.24987565 | 0.98816635 | 0.07110056 | 0.02396220 | 0.23775262 |

σ 的单位是 128×96 网格中的像素。低通分别测试了固定的 σ=1 与 σ=2，没有搜索最佳 σ。低通分析是在发现原始比较中的差异后加入的诊断。σ=1 的完整分段解码、固定元数据尺度结果为 `0.08176076 EV`，斜率 `0.97714475`。最终报告保留未经额外低通的原生结果，以免低通遮蔽真实的边缘和采样差异。

在 σ=2 的完整分段解码对照中，训练块独立拟合的尺度为 `0.24992762673357363`，与元数据比例只差约 `0.0208%`。因此，本样本的约 2 EV 差异有独立元数据解释。当前支持的归一化假设为：

```text
L_photo ≈ (h_video / h_photo) × L_video

等价地：h_photo × L_photo ≈ h_video × L_video
```

这个关系在本对样本的低频亮度上得到支持。仅凭一个配对场景，还不能把它宣布为所有设备和所有视频的生产端契约。这里也没有获得绝对光度单位。

原生私有 `CIAppleLogToLinear` 在本样本测得的输入范围内，与下列指数式相符。

```text
F(c) = 2 ** ((c − 0.69336945) / 0.08550479) − 0.00964052
```

照片原生解码与 Python 镜像的最大分量差为 `1.0036773344657135e-6`。视频原生解码加颜色空间变换与镜像的最大差为 `1.458533473996937e-7`。本次实现另外测试完整分段反变换：

```text
R0 = −0.05641088
Rt = 0.01
C = 47.28711236
Pt = C × (Rt − R0) ** 2

F_piecewise(c) = F(c)                          if c >= Pt
                 sqrt(max(c, 0) / C) + R0     otherwise
```

两种视频解码的差异出现在暗部 toe。即使低通降低采样误差，原生指数式的斜率仍约为 `1.13`，完整分段对照接近 `0.99`。因此，把静态照片使用的私有反变换直接当成视频 Apple Log 的完整反函数，会留下亮度相关的系统误差。完整分段对照更符合这对样本的低频照片参考，但本次实测不证明它是全部视频场景的唯一正确解码方法。

同一冻结几何和同一曝光拟合规则下，把 code values 直接当线性值，误差为 `0.78698269 EV`；使用 sRGB 反变换则为 `0.51774575 EV`。二者都明显差于 Apple Log 对照。锚点附近的视频缩略图中，完全相同 PTS 的第 22 帧误差最小。前后 1 个辅助帧的误差分别约为 `0.29665` 和 `0.28380 EV`，使用同一冻结几何。

此前阶段报告的约 `0.143 EV` 来自先降采样再变换。这会在低分辨率上增加插值平滑。最终实现先在原生照片缩略图上变换再降采样，主结果更新为 `0.24224705 EV`。旧操作顺序仍保留为 `downsample_then_warp` 对照，结果为 `0.14401098 EV`。不能把这项较小误差解释为更好的辐射恢复。

对视频 HDR 重建而言，本次结果支持让 LinearThumbnail 提供随帧变化的低频场景约束，而不只估计一个全局曝光。以对应静态 HDR 画面建立场景到显示的映射时，需要先统一照片与视频的 `h` 尺度，并解决视频暗部反变换，再区分低频亮度约束与高频边缘恢复。摄影风格后的 HDR look 仍需要静态 HDR 目标来约束。仅有场景参考不会自动给出最终显示亮度或风格。

本次亮度比较没有证明完整 RGB、局部风格、高频细节或 HDR look 的一致性。全部结果均来自这一对输入；本次也没有形成 Apple Photos 交互编辑或设备播放验收结论。

最终复跑的 [verification.json](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/verified-final/verification.json) 中，全部 13 项技术检查为真，`technicalPass` 为真。检查包括原件哈希、压缩载荷、精确 PTS、原生尺寸、帧数、数值镜像、独立几何和产物完整性。该收据记录运行源码和结果的 SHA-256，属于这项独立实验的技术收据。它不表示逐像素辐射等价，也不表示产品完成验收。

科学比较图如下。左上是原生解码后未经额外低通的比较，右上使用完整分段视频解码、共同低频带和固定元数据尺度。下方保留错误传递函数对照及原生解码的空间残差。

![IMG_3673 照片与视频线性缩略图对照](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/verified-final/analysis/comparison.png)

复跑步骤见 [REPRODUCE.zh-CN.md](/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-still-video-linear-thumbnail-pair/REPRODUCE.zh-CN.md)。
