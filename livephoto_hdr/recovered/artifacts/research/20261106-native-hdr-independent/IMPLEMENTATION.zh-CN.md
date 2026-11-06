# 摄影风格实况视频的动态 HDR 重建

这份实现独立编写，运行时只读取配对原片、Mac 上的系统框架和本目录源码。没有读取另一版本的实现或报告，也没有采用 subagent 的结果。

本次输出位于 `/Users/retriedstormtrooper/Downloads/IMG_3673_Independent_Dynamic_HLG.pvt`。完整运行记录在 `verified-run/`，入口是 `src/run.py`。

## 本机实测

环境为 Apple M1 Pro，macOS 27.3，build 26C5035r。

| 检查 | 结果 |
| --- | --- |
| 原生摄影风格反向 | 55 帧成功，useCase 2，processingType 0 |
| 原生线性缩略图 | 28 帧，Apple Log，由 Core Image 反变换到线性 Rec.2020，再转换到线性 Display P3 |
| 配对时刻 | 主帧索引 44，从 0 开始，PTS 881/600 秒 |
| 主视频有效区域 | 1744×1308，来自 1920×1440 coded frame 的原生 clean aperture |
| 原生 guided filter | 每帧三个 RGB 参数通道，共 165 次调用成功 |
| 最终视频 | HEVC Main 10，BT.2020，HLG，55 帧，1.911667 秒 |
| macOS HDR 识别 | AVMediaCharacteristicContainsHDRVideo 为 true |
| 非主轨 | 11 条逐包 SHA-256、PTS、DTS、duration 和 size 一致 |
| HEIC | 除新配对 UUID 外逐字节一致 |
| PVT | UTI 为 com.apple.private.live-photo-bundle，Quick Look 成功生成预览 |

原始 HEIC SHA-256 为 `f3f8cd98836b071d85db8f4373ef403edfd995608b9dc7089201d144947ea5de`。原始 MOV SHA-256 为 `9409a811e618bc6c11592b40246b5b6c1ce2dfffdb0aa63bd58741646b4a9b37`。完整流程结束后两者未改变。

## 为什么需要动态参数

CMIGuidedFilter 负责根据主帧的边缘上采样低分辨率参数图。它本身不推断 SDR 已经丢失的高光信息，也不完成摄影风格的逆变换。

样本在前半段与后半段之间出现明显的画面尺度变化。把照片上的增益位置固定到视频坐标，会把树、动物和天空的增益施加到错误位置。只有全局曝光变化也无法描述这种情况。

本实现把风格逆变换、低分辨率场景参考、照片 HDR 目标、运动关系分别保留。照片定义输出 look，原生视频资源决定每帧如何转移这个 look。

## 实际调用链

1. AVAssetReader 解码主轨、Delta Map 和 Apple Log 辅助轨，按原始 PTS 读取 smartstyle-info。
2. `_NUSemanticStyleProperties` 解析每帧元数据。`CMISmartStyleUtilitiesV1` 根据原始反向系数和 Delta Map 恢复 unstyled SDR。
3. `CIAppleLogToLinear` 解码辅助缩略图。缩略图在原始时间戳之间按 log RGB 插值，并映射到主轨 clean aperture。
4. Apple Vision 双向光流将照片 SDR 配准到对应 PTS 的主帧。相同映射用于照片 HDR。正反向一致性、边界和 SDR 光度差共同决定可用区域。
5. 使用 styled、unstyled 和场景参考的亮度关系，拟合三通道 log2 增益响应。全局响应之外的空间残差由照片 HDR 监督。
6. 每帧把照片空间残差沿光流搬到当前画面。正反向光流不一致或新出现的区域回退到动态响应，不强行套用照片局部参数。
7. 对每帧 64×48 的 RGB log2 增益调用原生 CMIGuidedFilter。guide 由全分辨率 unstyled 主图、原生解析的 GTC、baseGain 和 baselineExposure 构造，尺寸为有效主图的一半。
8. 在 extended-linear Display P3 中计算 styled 主帧乘以动态 RGB 增益。Core Image 转换到 HLG，AVAssetWriter 编码 Main 10。
9. 将新主轨样本和 sample table 写入新 MOV。原始音频、辅助图像轨和元数据轨的压缩内容与时间表保留。
10. 为新 HEIC 和 MOV 分配同一新 UUID，生成 PVT，并从封装后的 MOV 重新原生解码验证。

## 拟合公式

令 `S_t` 为线性化 styled SDR，`U_t` 为原生逆变换后的 unstyled SDR，`A_t` 为当前 PTS 的线性场景缩略图，`H_0` 为配准后的照片 HDR。

训练目标是三通道的 `log2(H_0 / S_0)`。特征包括 `log2(Y(A_t)/Y(U_t))`、`log2(Y(S_t))`、`log2(Y(U_t)/Y(S_t))`、亮度分段项和色度项。使用带正则化的稳健回归拟合响应 `f`，再拟合平滑空间残差 `R_0`。

```text
logGain_t = f(S_t, U_t, A_t) + confidence_t × warp(R_0, t → 0)
HDR_t = S_t × 2 ^ nativeGuidedUpsample(logGain_t)
```

这个响应是本实验的估计模型。它没有把未知字段当成完整 Apple ISP 逆函数。原生 guide 也没有被宣称与完整 Photos 图像图逐位等价。

## 对齐结果来自保留区域

照片 HDR 的空间块分为训练、参数选择和最终测试区域。最终测试块不参与回归或空间残差拟合。光流只读取 SDR。

最终 HLG 文件经原生解码后，在 18,350 个有效测试像素上：

| 指标 | 独立构造的固定照片增益对照 | 动态结果 |
| --- | ---: | ---: |
| 亮度平均绝对误差 | 0.528278 EV | 0.254647 EV |
| 亮度 P90 误差 | 0.969436 EV | 0.560183 EV |
| 归一 RGB 色度距离 | 0.070762 | 0.064783 |

平均亮度误差降低 51.8%。这是当前样本配准后共同区域上的对齐结果，不是对未知场景或所有摄影风格版本的保证。

编码再解码相对于送入编码器的线性 HDR，亮度平均误差为 0.02453 EV，最差帧为 0.03900 EV。最终解码的相对线性亮度峰值约 1.797，保留了超过 SDR 白点的高光。整段视频的中位增益最大相邻变化约 0.051 EV。这个统计不能替代真实屏幕上的闪烁和 HDR look 检查。

## HDR 元数据

主轨写入 BT.2020、HLG 和 BT.2020 YCbCr 矩阵。CLLI 为 0、0，明确表示没有绝对亮度母版测量。

观看环境写为名义 314 lux、D65，payload 为 `002fe9a03d134042`。这是依据 [Apple TN3145](https://developer.apple.com/documentation/technotes/tn3145-hdr-video-metadata) 选择的移动设备观看条件，不是拍摄现场的光照测量。字段单位由 [ITU-T H.274](https://www.itu.int/epublications/publication/itu-t-h-274-v3-2023-09-versatile-supplemental-enhancement-information-messages-for-coded-video-bitstreams) 定义。

本机 AVAssetWriter 还生成了 Dolby Vision profile 8、HLG 兼容 ID 4 的信令。独立初次完整运行核对到 55 个 RPU NAL。最终文件的主色彩契约仍是 HLG。消费设备上的 Dolby Vision 显示效果没有单独验收。

## 当前支持范围

已测试输入为 Smart Style 版本 0.16，包含匹配的 HEIC HDR 参考、主轨、Delta Map、线性缩略图、逐帧系数和 still-image-time。

当前不能声称支持任意带有某个风格标签的实况照片。缺少真实 HDR 参考或完整辅助资源时，程序会拒绝处理。低分辨率参考也不能唯一恢复已经裁切的高频高光细节。

原始辅助轨被保留，便于后续研究和消费者测试。替换主轨之后，原始 SDR 反向系数与 HLG 主轨能否继续满足 Apple 编辑器内部契约，仍需通过编辑、保存、重新打开验证。保留元数据本身不证明这一点。

本次没有向 Photos 资料库导入文件，没有进行物理 HDR 显示验收，也没有修改 XDRemux 的产品代码。完整本地验证结果见 `verified-run/validation.json`。
