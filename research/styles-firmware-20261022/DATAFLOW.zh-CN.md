# 官方 iPhone17,3 / 24A446 插件：已核验的静态边

这份文件只描述实际提取的 SmartStyleV1 插件。源固件组件与镜像 SystemVersion 在 `evidence/plugin-iphone17-3-24A446/extraction.json`，完整插件身份和 ivar 偏移在其 `SmartStyleV1.bundle/inventory.json`。它不是 IMG_2810 的同硬件、同拍摄 build 证明，也不是 iPhone17,3 实际相机运行捕获。

实际可执行文件 SHA256 `04dbdad52b959f848ba1d8de07f4fc81c85d1595c8843637a1dc905039112216`，UUID `5A365596-1ACE-39C8-93D5-EF893EA81BAC`，CFBundleVersion=1、DTSDKBuild=24A442。官方镜像 OS build=24A446，与 bundle/SDK 编号分别记录。

## 输入风格对象、两个下游处理器

原始文本：`evidence/plugin-iphone17-3-24A446/SmartStyleV1.bundle/processor-process.asm.txt`。函数入口0x188c，完整指令SHA `dd32185e2a981a1f2bc31721fb9295fe264ef2deeb4ffb370d5165684d074d16`。不是只凭属性名字认定数据流：

|边|指令及寄存器证据|可支持的范围|
|---|---|---|
|inputOutput → 当前风格|0x18c0将self留在x22；+0x128取inputOutput；0x18c8调用inputSmartStyle，0x18d0结果存x19|ivar元数据独立确认+0x128确为_inputOutput|
|当前风格 → pixel renderer|0x2244取self+0x28，0x2248把x19放入x2，0x224c setInputStyle:|+0x28确为_smartStylePixelBufferRenderer，不是style engine|
|两个small light map输出 → renderer|0x1a10/1a1c分别取outputSmallLightMapPixelBuffer/outputSmallLinearLightMapPixelBuffer，保存在sp+0x110/+0x108；0x2360/236c绑定到self+0x28|只绑定实际buffer角色，不据命名认定它们等于最终文件c/d|
|renderer process|0x2404–241c读_shouldGenerateTarget(+0xc0)和_shouldEncodeLinear(+0xc2)；0x2444/2448在这条分支对self+0x28调用process|配置决定是否触发；本轮没有运行这些接口或捕获其像素|
|当前tone/color/intensity → CCM prior|0x26f4取CMISmartStyleCCMPriorGenerator类；x19的toneBias在0x270c进v8，colorBias在0x2718进v11，castIntensity在0x2724进v2；0x2734/2738恢复s0/s1，0x2740调用calculatePriorCCMforCast:tone:color:intensity:priorStrength:|这里没有把tone直接换算成曝光EV；完整prior函数在外部框架，尚未补其匹配实现|
|prior矩阵 → style engine配置|0x2744/2748保存返回q0/q1/q2；0x274c取self+0x30并取configuration，0x275c/2760恢复矩阵，0x2764 setLinearSystemPriorMatrix:|ivar元数据确认+0x30为_styleEngineProcessor，与renderer是两个对象|
|style engine process|0x2c90/2c94对self+0x30调用process|不能把前面的renderer target生成和此学习/应用配置概括成通用拍摄端顺序|

0x18e8另取inputLinearMetadataDict；0x1928另取inputLinearPixelBuffer；0x2264把前者传给renderer；0x23d4–23fc绑定coded linear输出与metadata。仅凭这些边不能证明LinearThumbnail未经历人脸提亮、SRL、颜色变换或完整相机处理。SRL分支也真实存在，0x20e8调用runSRLForLivePhotos...，不能忽略为始终无操作。

## 与旧缓存的关系

整份新插件与历史24A435缓存**不同SHA、不同UUID/SDK build**。重新提取后，五个已选utility方法的完整指令SHA相同，processor.process指令SHA也相同；default.metallib完整SHA相同，均为 `675b74d04efa5727e1e8b71cf39b0541618667d13dbd15d548d105bfba603446`。因此旧缓存的三个已解析AIR单位和新插件的这些具体指令可作同代码复用，不能推广为两个固件完整相同。

257头GTC归一化的132B循环在新插件中再核SHA `136b3854b385fff4f7695d960808262eb814119d85bbba8ae55481287d7b2b9e`，与本机135组/34560个half零差异的原指令测试一致。这个链接只覆盖该算术分支，不覆盖iOS库/API、Metal原生运行、零除数或完整GTM/LTM。见 `evidence/target-static-native-link.json`。

## 仍缺失的边

- 新插件的官方镜像成员身份已验证；本硬件/build的CMCapture loader选择分支尚未重新取得。S106仅是iPhone12,1 /24A446参考，继续分开。
- 外部CMImaging/CameraColorProcessing内的完整renderer、prior、真实统计和GTM/LTM/人物提亮连接还需匹配SystemOS共享缓存或同帧捕获；不将Mac26A434手工配置替代它。
- IMG_2810属于iPhone19,2 metadata链，精确拍摄build、原Studio人物统计、配对RAW和新真实留出仍缺；当前版本准入依然失败，见 `evidence/img2810-version-admission-after-extraction.json`。

这轮没有新增原图+成片的Apple slider识别结果，没有完整HEIC的全相机条件逆，也没有仅成片唯一恢复的证明。已有S20原生同观测/不同中和结果证书和原误差门槛保持。
