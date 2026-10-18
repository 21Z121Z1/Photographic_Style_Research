## 2026-10-18 人物/皮肤语义阶段：证据边界

本轮不继续 bit-exact；旧验收仍为 false，详见 closeout-20261018。以下新结果不能替代旧五图验收。

### 已验证数值：IMG_2810 的结构与 j 参数干预

原件 SHA256 `52ea41f0dd16590cef83abfd8093ccf8082994113e0c2cee86f90c42f7ab21c2`，Styles v16。12 张 2026 matte 均为 768×576；另有 3 张旧 matte。该文件没有 hair matte。`j=1.09765625`，`log2(j)=0.1344263202209261 EV` 仅为算术量，不是已识别的人脸提亮逆变换。

run 39134556722（commit 73114a82，macOS 27.0.1 /26A434）固定 primary、Apple Log 原生 thumbnail、c/d/GTC、mattes、统计、tone=0，仅改变 `_NUSemanticStyleProperties.faceBasedGlobalExposureBoostRatio` 的返回值：实际值→1、实际值→1.2，在 PISemanticStyleFilter 的 renderer 与 style-engine 两条路径中，512×384×RGB 各 589824 分量均 0 差，EV MAE/max=0；EV 有效覆盖率 0.9377085367838541。此结果是参数干预，无原始相机去提亮真值。

证据：`semantic-20261018/runs/39134556722/selected/out/{metrics.json,status.json,face-actual/facts.json}`；全部 76 文件、71311908 字节流式 SHA 校验 0 失败，GPG 完整性校验成功。artifact 12139397306，ZIP SHA `c3f3864eda35a548bf65b6c3f682aeb646869abad23d756a56cf281abbb9a74d`。固定 ACES 预览配置 SHA `5aefc668796eabb1902b9593340496231758eceaec18ce290e12901042bd4440`，无逐图曝光拟合。

### 已验证数值：实际 Texture Styles 元数据缺少逐人实例

`texture_styles` 是 214 字节 plist，7 个 key：Preset=Studio，CaptureType=LF，CaptureMode=Still，PortType=PortTypeBack，HardwareModel=iPhone19,2，TextureStylePeopleDataVersion=3，FilmGrainSeed=65。没有 `TextureStylePostProcessedPeopleData` 和 `TextureStyleFaceAttitudeMetadata`。

同一 run 的原生 `_NUTextureStyleProperties textureStylePropertiesFromImageMetadata:auxImageMetadata:error:` 解析成功（aux 字典为空，文件中亦无实例 mask 元数据输入），version=3.0、numberOfPersons=0、personInstances=[]；`PITextureStyleProcessorKernel personInputDataFromStillProperties:` 返回 []。不能从这个结果推断拍摄时没有人物或从未执行过纹理处理。

### 已验证静态 / 原生数值：独立的 Studio 纹理链

run 39133038484 的原生 defaultEffectOrderForPreset: 返回眼下提亮→皮肤平滑→Mattify。硬件匹配 tuning `iPhone19,2/PortTypeBack/Still/Studio/Common` 的 EffectOrder 另含 FilmGrain；默认 grain=0，不能仅凭 tuning 名称断言胶片颗粒被执行。该 tuning 的 UnderEyeBrightening.brightnessMix=.5，Mattify.editingStrength=.3，SkinSmoothingStandalone.degrunge=1、pores=1、gFRadius=.45、gFContrast=.1；通用对象 defaults 不等于选定 tuning。macOS tuning 与 iPhone 拍摄固件的完全等价仍未证明。

### 已验证静态：相机端去人脸提亮会重新求曲线

iOS 27.0 /24A446（iPhone12,1 cache，版本/硬件与样张不一致）的 CameraColorProcessing，UUID `0A211E15-50CA-373B-AD9A-F9E3283C68F4`，SHA `974ffb2895cae06e26e63bd77ab4891f5401d4789449f7a0080d377553b2426e`。`-[LTMCurvesComputeV2 compute]` 中 `0x256b86e30` 写 flag +0x554，`0x256b86e38` 把 driver input +0x24 写为 float 1；随后 `0x256b86e4c` 调 computeLtmComputeInput，`0x256b86e64` 调 computeLTM，`0x256b86e84` 写 curvesType=2 的元数据。另一分支 `0x256b86e98`–`0x256b86eec` 同样重新计算 type3。

输入 metadata 的 FaceBasedGlobalExposureBoostRatio 在 `0x256b65b14`–`0x256b65b44` 读入 +0x24；LTMDriverV2::Process 的 `0x256bab880`–`0x256bab884` 再把它放入 compute input 的标量位置。仅有最终 j/c/d/GTC，尚不能假定可以用一个 skin matte ×固定 EV 撤销此生产过程。

### 原有 key1 结论的复用

已验证静态 C08/C09：8 个平面是输入亮度 Gaussian 分区，10 个二次 RGB 基函数，不是语义类别。该 blob 不提供“哪组系数属于皮肤/人物”的标签；单个复合映射的因子分解需要额外观测。不能把整套 key1 逆风格后再套 person matte 的候选标成原生皮肤逆算子。

### 尚待原生结果

Texture kernel 第一次因 extents 使用 NSValue 而非原生 CIVector 中止，run39134556722；修正后 run39135405637 又在辅助接口遍历阶段 SIGABRT、未产生像素结果；不能把 workflow success 等同于算子成功。后续用逐项 checkpoint、原生堆栈及隔离 getter 检查。AIR 提取已定位 61 个相关模块，但 runner 没有现成 LLVM C API；后续使用单一 llvmlite binary wheel，仅导出文本，不上传 Apple 二进制。


### global、local 与人物语义逆向的独立性

本阶段没有修改 GTM/LTM 公式、Apple Log decoder、冻结模型或已有 scene 输出。人物 mask 在 consumer 中也参与 LTM 的前景/背景混合，所以“把 person matte 清零”不能用来认证独立的皮肤/人物色彩逆向。应只干预目标算子的参数，保留 c/d、GTC、guides、统计、颜色管理和其他 matte。

若人物算子位于 GTM/LTM 之前，最终图上的独立去除需要对下游变换作共轭：`D ◦ S^-1 ◦ D^-1`；不能无证据在最终空间直接除一个 gain。最终两张已知、同域且为正的图可以形成 RGB gain map，但这个载体不能补足未知的无风格真值。

key1 是一个已学习的复合 RGB 映射。对任意可逆 S，`A◦B=(A◦S^-1)◦(S◦B)`，仅凭复合输出不能唯一拆成人物项/非人物项。这是因子可识别性的限制，不是新的实测去风格结果。平坦段、clamp 或未知人脸统计造成的缺信息区域，当前不给有限误差上界；不能用一个低往返残差替代唯一性证书。

### 预览与隐私

原生 j 中和的 ACES 预览在本地 `semantic-20261018/runs/39134556722/selected/out/face-j1-renderer-ACES.png`；对应基准为 `face-actual-renderer-ACES.png`，当前像素对照数值为 0。它们只是参数干预预览，不是已完成的相机去人脸提亮。统一使用 OCIO2.6 / ACES1.0 SDR Video / Linear P3-D65 → sRGB Display，0EV，无逐图拟合。原始 artifact 的 orientation 文字有误，实际代码 np.rot90(k=3) 是270°逆时针=90°顺时针，符合 HEIF irot3；见 errata.json，原 artifact 未修改。

所有人像、matte、可重建像素缓冲区与私密日志均以 GPG 加密传入/传出 runner，未明文提交或上传。输入用临时 secret；输出加密到只保存在 VM 的私钥对应的公钥。临时 secret、release、分支已删除，远端复核均为空；永久研究分支保留源代码。artifact retention-days=1。S4 run39135794320 的 artifact12139921306（6833538字节）下载被自动审批按92%磁盘阈值阻止，等待新许可；本轮已获准的S2归档没有被替换或删除。
