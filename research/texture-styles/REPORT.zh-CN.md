# Texture Styles 研究（B）— 2026-10-19

> 工作分支 `research/gpt-styles-20261019`，基线来自 `21Z121Z1/XDRemux@research/texture-style` 和 PSR 的 S2/S10–S13 原生单位研究。所有新增公开结果不含相机图、人像或原厂媒体；此目录从未引入 Lightroom / RAW / 私有照片数据。

## 结论与证据层级

|命题|结论和证据级别|边界|
|---|---|---|
|预设、参数空间|**已验证·静态文件**。随附调校表列出 4 个机型 ID、5 个摄像头 port、LivePhoto/Preview/Still 3 种模式、Filmic/Glowy/Soft/Standard/Studio 5 种预设，共 **285** 个配置记录；EffectOrder 有 **9** 种取值。见 `evidence/source-inventory.json`，各来源 plist SHA 记录在同一文件。|这些是设备配置分支，不等于 285 种独立影像算法或可编辑滑块。|
|滤波器名字和参数|**已验证·静态文件**。存在 `Diffusion`、`Glow`、`Bloom`、`Mattify`、`SkinSmoothingStandalone`、`FilmGrain`、`UnderEyeBrightening`、`Halation`。例如 `Diffusion.gaussianBlurSigma` 在调校表中为 **6.26–62.05**，`SkinSmoothingStandalone.pores` 为 **0.075–1.35**。|key 名不证明具体 Gaussian 核、实际像素半径、边缘处理或 guided filter 的设计，必须跟踪算子源码/原生中间缓冲。|
|同一预设内的处理次序|**已验证·静态配置**：例如 Filmic 分支有 `Diffusion→Glow` 或 `Halation→Diffusion→Bloom→Glow→FilmGrain`；Studio 可能使用 `UnderEyeBrightening→SkinSmoothingStandalone→Mattify→FilmGrain`。|仅确认配置 `EffectOrder`，尚无证据证明全系统 GPU 调度必严格执行该序列。|
|Texture 相对 GTM/LTM 的位置|**未验证／需要同上下文原生管线证据**。没有证据能把 EffectOrder 提升为 `pre-GTM`、`post-LTM` 等全局结论。|原 S2 只运行选定 CI processor；不是完整 Photos 图。|
|Texture 的工作域|**未验证**。S2 受控 CI context 设置 `extended linear Display P3`，这只说明该实验的输出渲染空间；不能据此断言内部所有 Texture 核在 Linear P3、Apple Log 或 gamma 编码域工作。|需要逐中间态同输入对照、显示正确编码及 API 连接关系。|
|两个末端单元的非零行为|**已验证·runner 原生**。在 `26A434` Apple `default.metallib` 中，用固定人工上下文、合成 Float16 RGB/mattes 调用原 `CMITextureStylesSkinSmoothenStandalone::finalBlendingKernelInPlace` 与 `CMITextureStylesMattify::ApplyRegionAddbackAndEditingStrength`，各测 strength 0/.5/1。见下列 S24 结果。|此处「原生」限原 shader 末端单元及模拟绑定；不是 Apple 全纹理管线，也没有说明相机实际润色顺序。|
|原始 Texture 管线可逆性|**尚无法宣称唯一可逆或数学不可逆**。半精度往返中观察到对当前残差候选的量化误差及未达标分量；这只能证明本候选失败，不能单凭失败证明不存在其他前像。|需要相同完整原生条件下的碰撞见证或覆盖全部合法前像的数值证明。|
|与既有 Photographic Styles 的叠加|**已验证·静态元数据关联；数值作用机制待验证**。随附 `SmartStyleToTextureStyleMapping` 为 16 种 cast 指向纹理 preset、intensity 和 grain，`RendererTuningWithTextureStyles` 保留 ColorBias/ToneBias/CastIntensity 的默认偏好。|这些值不是一条可直接应用在 GTM/LTM/LinearThumbnail 上的像素数学公式。|

### 数值与证据：S24 原生末端单元

|原生算子|strength|原生前向改变的 RGB 分量|当前逆解候选往返超出 `1e-3` 的分量|最大相对误差|
|---|---:|---:|---:|---:|
|SkinSmooth|0|0|0|0|
|SkinSmooth|0.5|574643|57|0.0010040160643|
|SkinSmooth|1|576893|525|0.0010422094841|
|Mattify|0|0|0|0|
|Mattify|0.5|575406|0|0.001|
|Mattify|1|582518|144|0.0010198878123|

以上以 **512×384、589824 个 RGB half 分量**为口径。来源：[原生 run 39217101424](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39217101424)，job `117943403883`，纯文本 artifact `12169639182`（ZIP `ab9de4856a2f0e3da331447e01e9319a48183cbc28dffe6c50e593ea80cd29f6`），manifest SHA 全部核对一致。旧的单位逆解按原始 `texture_units_s10.m` 固定上下文做最多 24 轮残差迭代，针对图案前向输出估计其一个前像；初始化没有采用真实原始输入做种子。

严格门槛随后接入 `.github/workflows/research-s24-texture-native-units.yml`：在 [run 39217407757](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39217407757) / job `117944406077`，编译/原生执行/数据审计均成功，**`Enforce original 1e-3 all-valid-component roundtrip requirement` step 明确失败并使 job 变红**。这反映数据真实性；不要因为先前一次 green 把逆解指标写成通过。该轮 artifact `12169649400`，带单次 24 小时到期保护。原始阈值、未解数目未被抹除。

### S23：仅为方法学展示的预览，不是 Apple 实拍效果

独立的 [run 39216211111](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39216211111)，job `117940553876`，artifact `12169811617`，执行纯 Python 解析后的清单约束与三个程序生成的 192×128 灰阶预览：源图、**3×3 box blur 替代**、**确定性噪声替代**。ZIP SHA `db5195764bbb4d8fede1564fa8c027f11287724df52228bdbabca3fa11a7d283`，manifest 所有六个文件逐个匹配。**这些图不代表 Apple 的 Diffusion、FilmGrain 核或相机原生滤波结果**。展示源有意无人物、不含设备照片。

### 对 XDRemux 的约束

在 `21Z121Z1/XDRemux` 的 `research/texture-style`，`crates/xdremux-heif/src/texture_styles.rs` 和 `research/texture-style/README.md` 明确写着仍属探针：将一个 2019 `semanticskinmatte` 复制映射为十二个不同的 2026 语义角色，固定 `iPhone19,2`／拍摄属性，以及在缺失 Apple MakerNote 时生成伪造标志。可测试 Photos 的**容器准入**，不能升级为对原始产地、语义或图像处理的产品真值。此 PR 不修改 XDRemux，也不生成正式 Texture Styles 元数据。

工程目标应优先保证滑块正反方向、线性 RGB 色度约束、梯度连续、低频/高频分离和噪声稳定；这些是**未来实现的验收目标**，未由现有 S24 证实。GTM 与 LTM 两套独立结果不得和 Texture 混成一张不可分的预览；LinearThumbnail 保持既有 Apple Log 传递函数常数与码值范围，未改变。

### 下一步

先采集实际调用图：Texture Pipeline 输入、各 EffectOrder 核前后 buffer 的标注色彩空间、LTM 前后对应中间帧，再用**同一 synthetic 输入**在完整原生 pipeline 和单元核中求差。若需要对比真实照片，只能经加密临时 secret 运输并立即清理，不能把带人像的数据送进公开 run／artifact。真实 iOS Photos 的准入、跨设备外观及人物语义仍需实机。操作清单见 `NATIVE_TODO.md`。

**结论状态**：参数清单与受控两个末端内核验证完成；全 Texture 处理链／线性域／Log 域／相对 LTM 顺序／完整可逆性／iOS 端一致性 **均未验证**。
