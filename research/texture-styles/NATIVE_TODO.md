# Texture Styles（B）待验证事项与直接执行方案

## 已完成的本轮入口

- `research/texture-styles/evidence/source-inventory.json`：无需照片的参数、预设、符号文件摘要。源来自用户本地附带资料包的 plist 与符号**静态文本**，仅记录原文件 SHA 与复核值，没有重新公开 Apple 二进制或媒体。
- `research/texture-styles/validate.py`：仅在 macOS runner 执行，审计参数清单，生成基于合成数学图的 PNG。记录见 [S23 run39216211111](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39216211111)。
- `research/texture-styles/native_units_s24.py`：先在 runner 临时目录生成十个无照片 half 合成纹理和假 mask，再用现有原 `research/semantic-styles/texture_units_s10.m` 执行 `SkinSmooth`、`Mattify` 的原始末端 shader。原生输入、输出的二进制仅在 `RUNNER_TEMP`，审计数值与 SHA 留在 `s24/native-summary.json`；runner 结束删临时目录。[S24 原生成功 run39217101424](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39217101424)；[S24 严格逆解门槛失败 run39217407757](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39217407757)。

## Runner 可做的项目：优先按顺序

1. **核映射和闭合输入图**：在当前 `26A434` Apple `default.metallib` 以及实际 PSO context 下，对 `CMITextureStylesFilter::Guided/SelfGuided/WeightedGuided`、`GaussianGuidedFilterV3` 的 `guided_lr_2d`、`upsample_apply_to_mr`，以及 `FastGaussian::gaussian_h/v` 逐项记录参数含义、生成中间纹理的 shape、pixel format、sampling mode、边缘延拓和坐标变换。符号表中的存在性仅是搜索入口；对没有运行证据的核不得写“已使用”。为测试生成单脉冲、阶跃边缘、线性斜坡、双色细线和中性灰合成图，不引入真实人物数据。
2. **域与混合顺序**：拿同一幅合成输入，分别构造“先原生 Texture 单元后 GTM/LTM”与“先 GTM/LTM 后 Texture 单元”的实验，再与系统真实整条 pipeline 的中间状态对照。每步必须保留输入空间标识（linear P3、设备编码域、Apple Log）与转换公式；先分别完成 GTM、LTM，禁止合并成单一补偿。仅在中间缓冲和 native 调用图匹配后才能确定真实顺序；不能以两个 proxy 的 PSNR 最优排序代替。
3. **B 逆的数学边界**：固定所有纹理、强度、统计、matte、函数常量和 ROI，枚举相邻 half 输入（包括一个像素扰动和多像素邻域扰动），在原 native 输出上找 `F(x1)==F(x2)` 的严格逐字节碰撞；若找到且 `x1 != x2`，留出可公开的小型**纯合成**根对输入值、输出哈希及必要的上下文哈希，形成无法唯一逆的存在证书。若未找到，不得推断单射；若尝试上界，必须覆盖明确声明的全部可行域及 sampler 邻域。
4. **修正 S24 逆候选**：当前 SkinSmooth .5/1 有 57/525 个 RGB 分量未满足 `1e-3`，Mattify 1 有 144 个，绝不屏蔽。可以对已经收敛到半精度邻域的候选做受控局部半精度格点搜索并实际 native reapply；任何改善都需要保留原始 589824 分量 mask，不得缩减有效像素、调大阈值或用原输入作种子。运行 CI 的 `Enforce original 1e-3...` 只有零失败才变绿。
5. **参数连续性**：使用强度 0、.25、.5、.75、1 的固定合成图序列，对每帧保存可复算的强度-亮度曲线、Lab/OKLab 色度偏移、ROI 边缘一阶/二阶差、alias/banding 计数与确定性噪声 seed；该项直接面向 XDRemux 的滑块方向、平滑与色带目标，但不自动证明 Apple 语义等价。

## 只能匹配真机/原相机上下文才能完成

- 从同一次拍摄保留所有目标角色对应的真实 semantic mattes（nose、face/nonface skin、person、lips、glasses、hands 等），确认数量、维度、方向、alpha 边缘和成像坐标；缺某个 role 时必须缺失或拒绝，不能默默把单一 2019 skin matte 扩充成 12 种语义。
- 在同设备系统版本下 capture `PITextureStylePipelineProcessor` 完整 still/video 处理图与每个 `EffectOrder` 的实际核 launch、上下游颜色空间、LTM/GTM 与效果函数的边界。分别覆盖 Standard、Soft、Studio、Filmic、Glowy 和非零强度、颗粒分支；不用 S2 的假 mask 自动补零通过来代替真实上下文。
- 在 iPhone Photos 做真实 2026 Texture Style 编辑入口的正负对照：真实来源纹理文件、纯结构仿制文件、缺角色/缺 metadata 的文件。记录准入、可选择的 preset、强度、grain、编辑后输出和关闭-再开启的稳定性；iOS 上的 UI 准入与真实语义相符必须两个独立验证。
- 如需相机样张、预览、RAW/LinearThumbnail 或人物区域 mask：必须在新的**用户明确批准的 GPG 加密 + 临时 secret** 方案下处理，绝不在公开 Git、PR、Actions artifact 中留下明文人像。任何超 1 GB 下载先征得同意，artifact 一律 `retention-days:1`，任务完按次核对 secret、临时 tag/release/分支删除。此前没有为 B 创建过任何 secret/release。

## 合格判定

B 只有在处理域、相对 GTM/LTM 的真实次序、关键核及其参数、组合和真机语义可编辑性均有对应的日志/run/数值及可复核隐私合规证据，并对可逆性给出数学上有依据的判断时才可以标为 `B_phase_complete=true`。当前为 `false`，S24 严格验证失败是有效信息，不能被绿灯的静态预览工作流掩盖。
