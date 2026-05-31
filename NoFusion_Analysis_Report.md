# No Fusion 底层架构与摄影风格注入技术分析报告

> [!NOTE]
> 本文档基于对 `No Fusion` 应用程序二进制包及其输出的 HEIC 样片进行的深度静态与结构化逆向分析得出。旨在揭示其“突破系统底层限制，支持任意机型开启摄影风格”的技术原理。

## 1. 调研背景与应用概述

*   **应用名称**: No Fusion-Powerful Pro Cam
*   **版本号**: 2.5.53 (Build 137)
*   **Bundle ID**: `com.grey.swiftcamera`
*   **核心特性**: 宣称能够在任意 iOS 机型上支持原生相册的“摄影风格 (Photographic Styles)”编辑，打破了 Apple 仅限 iPhone 13 及以上机型的硬件限制。同时支持极其拟真的胶片光晕 (Halation) 渲染。

## 2. 二进制包静态分析与阻碍

### 2.1 FairPlay DRM 加密
在尝试直接从可执行文件寻找明文字符串和底层汇编实现时，通过 `otool` 提取 Mach-O 头部信息，发现该文件存在强加密：
```text
cryptoff 16384
cryptsize 11124736
cryptid 1
```
`cryptid 1` 标志表明该应用代码段（`__TEXT`）受 Apple App Store 的 FairPlay DRM 保护，导致无法直接通过反汇编工具读取其原始的 Swift / Objective-C 逻辑指令。

### 2.2 基于明文符号表的侧信道推演
尽管代码被加密，但由于系统动态链接机制的需要，其符号表（`__LINKEDIT`）仍然保持明文。通过导出所有的 `_OBJC_CLASS_$_` 外部依赖类，发现以下关键线索：
*   **缺失的硬件级 API**: 应用**完全没有**链接 `AVSemanticStyle`（Apple 官方用于摄影风格的类）。证实了它不是通过调用原生相机接口来实现该功能的。
*   **高频调用的底层接口**: 核心逻辑严重依赖于 `CIImage`, `CIContext`, `CIFilter`（负责图像处理与计算），以及 `PHAssetCreationRequest` 和 `AVAssetWriterInputMetadataAdaptor`（负责底层文件封装与写入）。

## 3. 核心机制解密：欺骗系统相册的伪装术

通过对其使用前置/后置摄像头实际拍摄输出的 HEIC 样片（如 `NO_FUSION_LIVE_0525_005/IMG_4745.HEIC`）进行 EXIF 和底层数据块的提取，我们找出了它突破硬件限制的真相：**自定义 HEIC 封装与 Metadata 注入 (Metadata Injection)**。

### 3.1 伪造 Apple MakerNote (EXIF 注入)
在生成的 HEIC 文件中，提取到如下私有信息：
```text
[Apple] Maker Note Version  : 16
[Apple] Semantic Style      : {_0=1,_1=0,_2=0}
```
**实现原理**：No Fusion 在内存中手动组装了一段符合 Apple 规范的 MakerNote 二进制字典，并将 `Semantic Style` (语义风格) 相关的数据强行赋值给 `kCGImagePropertyExifMakerNote`。当文件存入系统相册后，iOS 底层的 Photos 框架读取到该字段，便会“误认为”这是由新款 iPhone 拍摄的合法照片。

### 3.2 构造 `styledeltamap` (风格增量图层) 与辅助蒙版 (Auxiliary Masks)
这是技术实现中最难且最关键的一环。通过提取辅助图像属性，发现：
```text
[QuickTime] Auxiliary Image Type : tag:apple.com,2023:photo:aux:styledeltamap
```
**实现原理与深度解析**：
根据行业前沿解析（如 iPhone 16 系列的相关拆解），Apple 的摄影风格之所以能够进行二维维度（如色调与色温）的无损级别调整，是因为它在 HEIC 容器中塞入了多达十余层的辅助图像（Auxiliary Image）。
在这套体系中：
1.  **Semantic Masks (语义蒙版)**：Apple 会生成精细到“天空”、“人像皮肤”、“头发”、“牙齿”甚至“眼镜”的蒙版，用于局部定向渲染，确保改动背景时不影响人物肤色。
2.  **`styledeltamap` (风格增量映射图)**：这张图的核心作用是**“升位” (Bit-depth recovery/upsampling)**。在进行高强度的风格化色彩偏移时，常规的 8-bit 图像极易出现色彩断层（Banding）。`styledeltamap` 记录了原始的高宽容度/高精度数据，用于在后期滑动调整时复原出高质量的图像细节。

**No Fusion 的突破之处（与 Apple 官方原生实现的对比）**：
为了深刻理解 No Fusion 的技术含量，我们将其与 **iPhone 17 原生拍摄的带 styledeltamap 样片**进行了系统级对比提取，发现了极具戏剧性的差异：

1.  **容器架构：优雅 vs 暴力**
    *   **Apple 官方**：HEIC 容器内只有 **1 张主图 (`ImageCount = 1`)**。系统依赖硬件 ISP 级别的 `FlexRange` 管道和 HDR Gain Map 动态生成高宽容度数据。
    *   **No Fusion**：由于旧机型无法调用底层 `FlexRange` 管道，No Fusion 采用了“暴力重组”策略，它在一个 HEIC 内强行塞入了 **3 张图 (`ImageCount = 3`)**，其中包含一张高达 90MB+ 的独立 10-bit PQ HDR 图层（Image 1），以此作为 `styledeltamap` 的数据母版！
2.  **`styledeltamap` 规格：克制 vs 堆料**
    *   **Apple 官方**：原生 Delta Map 的尺寸被精简压缩至 `2880 x 2160` (约 600万像素)，并采用极端高效的 `xf20` (4:2:0) 像素格式，极大地控制了文件体积。
    *   **No Fusion**：由于软件算法难以实现硬件级的无损超高压，它的 Delta Map 尺寸高达 `4096 x 3072`，甚至超越了主图尺寸 (经过 64 像素对齐 Padding)，并采用了无损级别的 `xf44` (4:4:4) 格式。
3.  **语义蒙版集成**
    *   **Apple 官方**：原生携带规范的 `kCGImageAuxiliaryDataTypeSemanticSegmentationSkyMatte`（天空蒙版）以及 `ISOGainMap` 等多种标准通道。
    *   **No Fusion**：通过自己的软件算法（如 CoreImage / GPU 着色器），在后台强行计算出这些必要的黑白语义掩码（Mask），并在写入时利用 ImageIO 的 `CGImageDestinationAddAuxiliaryDataInfo` 接口，将这些庞大的图层一并打包进了 HEIC 容器。

这等于**用纯软件暴力复刻了 Apple ISP 芯片的工作流**。为了让旧机型实现 iPhone 16+ 的摄影风格无损色彩调节，No Fusion 不惜以极其庞大的文件体积（动辄数十甚至上百兆）为代价，在内存中手工拼接了一个包含 10-bit 高频数据与全精度 4:4:4 Delta Map 的复合怪物。

## 4. 总结与技术复现可行性

No Fusion 的技术本质并非破解了 iOS 系统内核，而是**精通了 Apple 的 HEIC 图像封装协议**。它通过纯软件的算法生成所需的依赖数据，并利用系统底层的 ImageIO API 进行了严丝合缝的伪装封装。

**复现此技术的伪代码思路 (Swift)**：
1. 使用 `CGImageDestinationCreateWithURL` 创建 `.heic` 容器。
2. 构造包含伪造 `Semantic Style` Tag 的 MakerNote 字典。
3. 调用 `CGImageDestinationAddImage` 写入主图像和伪造的 EXIF。
4. 调用 `CGImageDestinationAddAuxiliaryDataInfo`，传入 URN `tag:apple.com,2023:photo:aux:styledeltamap` 以及软件计算得到的黑白掩码 Mask。
5. 封包并利用 `PHAssetCreationRequest` 存入相册。

> [!IMPORTANT]
> 如果需要针对此机制进行进一步的汇编级代码分析，必须先在越狱设备或关闭 SIP 的 Mac 上使用 Frida/Clutch 等工具对原始 IPA 进行砸壳（Decryption）处理。
