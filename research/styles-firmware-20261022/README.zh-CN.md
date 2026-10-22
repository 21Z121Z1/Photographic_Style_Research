# 摄影风格产品代际、实际插件与条件算子：本机阶段

当前为**静态和连续条件算子阶段**，没有完成匹配样张的固件处理、完整拍摄端复现或逆解。独立分支 `research/styles-firmware-local-20261022` 基于 `2132e1fcb6505e601d006b5ca1afde04e36ae649`。没有修改 master、既有研究分支、其他项目、记忆或原媒体。

## 版本映射

|证据|实际核验|尚未证明|
|---|---|---|
|[Apple iPhone 16 规格](https://support.apple.com/en-us/121029)|官方标为 Photographic Styles 2，2026-10-22 查询|不能从它推出内部 bundle 为 V2|
|[Apple iPhone 18 Pro 规格](https://www.apple.com/iphone-18-pro/specs/)|官方标为 Photographic Styles 3，同日查询|不能把纹理样张当第二代产品样张|
|`evidence/iphone17-3-manifest.json`|官方 IPSW 包内 BuildManifest：iPhone17,3，27.0.1，24A446，d47ap；读取 133051B|该机的实际插件及运行加载路径|
|`evidence/iphone19-2-manifest.json`|官方 BuildManifest：iPhone19,2，27.0.1，24A446，v63ap；读取 161388B|IMG_2810 的精确拍摄 build；该机的实际插件|
|`evidence/iphone18-1-manifest.json`|官方 BuildManifest：iPhone18,1，27.0，24A435；读取 123375B|缓存插件在该官方镜像中的成员身份，尚未重新提取证明|
|本机缓存实际文件|SmartStyleV1.bundle / CMISmartStyleProcessorUtilitiesV1，CFBundleVersion=1，SDK build=24A418，MinimumOSVersion=27.0|SDK build 不是安装 OS build；V1 不是产品代际|
|既有 IMG_2810 清单|Styles v16，HardwareModel=iPhone19,2，TextureStylePeopleDataVersion=3，来源 `../semantic-styles/evidence/metadata-inventory.json`|这些 metadata 编号不等于产品代际；精确拍摄 build 未核验|
|S106 真实 loader|24A446 / iPhone12,1，version1 → SmartStyleV1.bundle / CMISmartStyleProcessorV1|不是 IMG_2810 匹配硬件链；不能接到本次 24A435 插件当作同 build|

三次元数据读取均只收精确 HTTP206，核对 ZIP CRC，保存原始 manifest 的 SHA256 和中央目录 SHA256；没有下载 DMG 或整 IPSW，整 IPSW SHA 留空。CRC 是传输一致性检查，不能替代固件签名验证。缓存七个 bundle 文件的 SHA 全部符合历史清单，但历史清单不能代替官方镜像成员证明。

## 新的静态证据

插件可执行文件 288176B，SHA256 `34c7ecc0c6355159edea3e0515571760a230911104eb042907f921c70eca919f`，UUID `305C2ACD-593F-3B87-98A8-736D9362820D`。metallib SHA256 `675b74d04efa5727e1e8b71cf39b0541618667d13dbd15d548d105bfba603446`。`inspect_cached_plugin.py` 从只读缓存重新导出五个完整方法、逐条回查 6940B 指令与 Mach-O 文件映射一致；9 个 AIR 模块可解析，保留三个相关模块文本。没有执行 iOS library 或上传 Apple 二进制。

- `evidence/plugin-24A435/linear-3.asm.txt`：`_compileShaders` 0x601c–6030 将 `smartStyleCreateLinearThumbnail` 管线存到对象+0x30，0x6048–605c 将 `smartStyleCreateLinearThumbnailFromPreLTMBounds` 存到+0x40；GDC 变体分别为+0x38/+0x48。不是仅用名称猜关联。
- `linear-2.asm.txt`：post-LTM 入口始于 0x9e08；0xa2ec–a420 按 crop/GDC 条件取上述管线，绑定输入、输出及16B bounds、4B size、112B GDC参数。入口还从 LTMThumbnail metadata 0x30/32/34 读三个分量偏移，0x3e 起读数据；不是凭 HEIC auxiliary 名称认定无风格输入。
- `air-2.ll.txt`：先处理坐标/GDC和采样；严格在 pre bounds 内选重采样的 pre-LTM RGB。边界分支为 `post(output) * min(preLuma / postLumaAtBounds, 1)`；分母不大于 half `0x1419` 时比例取1。dot 的每通道权重是 half `0x34cd`，不是精确的1/3；原实现含 fast half 运算及 imageblock。GDC 和 sampler 量化尚未独立建模，不能用本模型认证边缘像素精度。
- `air-0.ll.txt`：packed ushort 先转 float、乘 float32 `1.5259021893143654e-05`，再转 half；有可选GTC纹理。`linear-0.asm.txt` 的 0x9abc 明确把该 GTC slot1 设 nil，故此入口不能据可选 shader 路径声称实际应用了GTC。
- `linear-4.asm.txt`：本插件 `_createGlobalToneCurveTextureFromMetadataDict:` 在257头分支读 words[1..256]，用 words[256] 作除数，存256个half。它本身没有同名框架帮助函数中的额外transfer调用；不能把不同类的实现合并。

## 模型和复用范围

`thumbnail_model.py` 新增上述采样之后的连续分支模型、显式先验下的条件集合逆，复用 `semantic_curve_inverse.inverse_curve_pair`，没有重写 S20 求解器。内部区域输出不观察 post-at-output；零比例同样丢失该输入。因此条件逆保留整个调用者先验区间，不伪造唯一值。该证书只属本连续单位模型，与既有原 Apple PSO 的 S20 同观测/不同中和结果证书分开保留。

GTM、LTM、人物/人脸提亮、肤色、纹理仍分别使用既有证据和模型。没有把 global→local→semantic→texture 猜作通用拍摄顺序。`inverse_supplied_curve` 必须显式传实际坐标、曲线、存储精度和实现误差；缺曲线不填经验值。肤色沿用 `semantic_skin_model.py`；纹理沿用已验证的 UnderEye→SkinSmoothStandalone→Mattify consumer 链及其原生单位实验。另一分支 `2bc4e3d16fc2c6028cdf708f06d79cf3be42a6d5` 的纹理统计生成/最终文件重放已读取核验，未复制重写；新统计不等于原拍摄统计。

三种逆问题继续分开：原图+成片的参数识别仍需配对模型和可识别性测试；完整 HEIC 是辅助上下文条件逆，不能把 LinearThumbnail 当无风格原图；仅成片目前只能给带先验的近似/集合，不承诺恢复丢失纹理。

## 复验

依赖 Python3、NumPy；静态导出另需本机 ipsw 与 llvm-dis。工作目录为仓库根。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/inspect_cached_plugin.py /path/to/SmartStyleV1.bundle /tmp/psr-new-text
python3 research/styles-firmware-20261022/firmware_probe.py '<evidence JSON 中的 source_url>' iPhone17,3 24A446 /tmp/psr-new-manifest.json
```

本机 macOS27.0.1 /26A434，15项测试通过：HTTP200拒绝且不读body、元数据预算/来源、ZIP64偏移、CRC损坏、机型/build错配、精确普通/Recovery OS变体选择、断点字节复用/完整CRC、组件未完成/身份变化时禁止解密挂载、单变量分支、1000个固定种子合成留出样本条件往返、歧义和 S20 plateau 集合保留，以及四项产品/内部/metadata版本不混同的反例。没有新真实照片测试，没有原生 GPU 精度验收；合成留出不计作真实照片留出。

`version_gate.py` 对硬件/build、官方镜像成员身份、实际loader分支和插件类分别校验。V1 bundle配产品第二代与metadata16可以通过合成的完整身份链；单改V2名称不能修复缺失build/来源；相同OS build但硬件不同、产品三代样张充当二代均拒绝。当前真实证据运行结果 `evidence/img2810-version-admission.json` 仍未准入：IMG_2810精确build和独立产品代际证据缺失，缓存与loader硬件/build不匹配。这个检查不把静态准入升级成运行加载、图像精度或唯一逆证明。

`compare_texture_tuning.py` 可复验缓存iOS配置和本机macOS配置的精确Studio子表：`iPhone19,2/PortTypeBack/Still/Studio/Common` 的canonical JSON SHA同为 `398fa58e64ca1a9d37008a02179afaf5e10651682661fa6a5abda5ca33c129b0`，包括 UnderEye亮度混合.5和Mattify强度.3；整份plist SHA不同。配置的顺序还含 FilmGrain，grain0时可能不执行。缺iPhone17,3精确键不作为该机功能不存在的证据。配置子表相等不补原始人物统计或实际拍摄选择，见 `evidence/texture-tuning-comparison.json`。

### 原 CPU 算术循环比较

```sh
python3 research/styles-firmware-20261022/native_gtc_check.py /tmp/psr-native-gtc-new.json
```

在本机 Apple Silicon 上，将已核对的 `_createGlobalToneCurveTextureFromMetadataDict:` 0x8eb0–8f30 的132B原指令放入独立 macOS 测试函数，外壳只提供合成记录、输出指针及ABI保存；原循环不含系统调用或跳转回iOS。输入为6组结构化、128组固定种子随机记录与1组末尾word257干预，总135组、34560个half输出。与复用的 `producer_curve_record_s54.ios_gtc_input_ratios` 后正确half转换逐位比较，**差异0**；word257单变量控制通过。完整iOS库没有加载，未运行Metal、没有照片输入；不覆盖其他记录头、零除数、纹理创建或完整capture调用。收据为 `evidence/native-gtc-loop.json`，含原指令、源码、临时可执行文件和输入/输出SHA；临时可执行文件未提交。

### 有界获取目标参考插件

`evidence/iphone17-3-components.json` 在同一原始manifest SHA下补齐ZIP entry。普通 `Customer Erase Install (IPSW)` 的 OS 是 `043-69462-662.dmg.aea`，8858370048B；Recovery的OS是另一251658240B组件，不混选。`download_component.py` 要求精确变体、stored entry、10GiB组件上限、精确HTTP206、最终CRC/SHA和至少三倍组件加4GiB预留空间，无整包回退、自动重试或删除。可显式复用本任务完整16MiB范围断点，至多4个范围请求/64MiB缓冲；中断丢弃的网络body另记上界，不伪称精确累计网络字节。`extract_downloaded.py` 只接受已完成校验的收据，重新核SHA后用公开AEA流程解密、只读挂载、核镜像SystemVersion，导出实际插件文本并卸载本任务挂载点。当前下载只在本任务仓库外scratch进行，下载准备或进度不算插件提取完成。

## S110 失败和下一步

`evidence/s110-failure.json` 记录作业119004152190：提取 exit1；当时实际上传10个文本文件、3588B artifact12316810885，当前 API 列表为空。异常只存在被重定向的 driver.log 中，作业日志没有它。清理时 disk5 被卸载，不足以推断具体失败原因；本轮不补写根因，也不把准备好或挂载过当提取完成。

下一步优先用现有缓存对已定位 CPU 归一化循环做合成原指令比较，再判断是否需要从经核验的 iPhone17,3/iPhone19,2 OS entry 有界提取真实插件。尚缺匹配硬件/build的实际插件身份、同帧人脸提亮/曲线/统计、原纹理统计、原生半精度误差及真实照片留出。没有读取照片库或私人原媒体，没有绕过锁屏；完整目标仍未完成。
