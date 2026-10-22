# 匹配SystemOS：实际CPU链与SRL标量原指令

前阶段先完成可复用清单和现有资源分析后，才定向取得**同一iPhone17,3 /24A446** manifest中的最小CPU来源；没有改下载另一机型的整OS或整个IPSW。该参考链用于用户所指Styles2代硬件，内部V1名称继续不当产品代际。IMG_2810/iPhone19,2/Styles16/PeopleData3的精确capture build与运行选择仍未补齐。

## 实际获取与身份

- `Cryptex1,SystemOS`：`043-70113-711.dmg.aea`，2348810240B，ZIP CRC `78747dcb`，完整SHA256 `8bcfae5ca2c434b09b75c8a2412461085cd9e1787ce188c3254e78688223b0e2`。
- 解密DMG：6018826240B，SHA256 `bce06bf973fe4fcce39f5401be42352b96e2e052cf4c182d107ef8fd2d86fe18`。源URL、manifest SHA、精确entry范围、空间预算与公开AEA流程均有独立收据；不称作完整IPSW哈希或签名认证。
- 先用16435B头部请求核公开FCS可用。下载曾DNS失败，HEAD同源恢复后从301989888B完整范围续传；不改源或重复前缀，中断body保守上界67108864B，完成下载body总上界2415919155B，头部前置检查另计。无无限重试。
- 镜像实际包含 `System/Library/Caches/com.apple.dyld`，79个cache文件；主cache UUID `0094EE12-3B41-3892-A043-9459D9C749FE`，iOS/arm64e。私有完整工具JSON未上传，仅精选框架、UUID、映射与所用代码cache SHA。

|实际框架|UUID|版本|
|---|---|---|
|CMCapture|995FC22B-41BD-37B4-812F-2686B81C2694|764.22.14.0.0|
|CMImaging|0A9BC064-A4BC-330E-861A-C70A637B14B3|同上|
|CameraColorProcessing|0A211E15-50CA-373B-AD9A-F9E3283C68F4|同上|
|CMCaptureCore|B24CA414-DFAB-3E2E-89BB-937DD6D91DC5|同上|

CMCapture的UUID与S106参考相同，仍不能据此继承整条拍摄链、配置或像素结果。现已分别取得同机型/build的OS插件与SystemOS框架成员证据。

## 可复验的静态读取

`dyld_bytes.py` 直接解析原cache mapping及Mach-O load commands、LINKEDIT和ULEB `LC_FUNCTION_STARTS`，再与ipsw逐框架输出独立核对。`export_cache_methods.py` 只按已知方法导出，逐条原字节回查后复用S106既有selector/literal注释函数，不运行旧脚本顶层Linux路径。共35个方法、**55680B**，分为 `cache-methods-24A446`、`cache-follow-24A446`、`render-follow-24A446`、`render-compile-24A446` 四份清单；每份保留方法范围、原字节SHA与注释文本SHA。

指针只在实际slide-v5链成员位置解码；初始page offset单位为byte，后继next单位为8byte，非链整数不掩码猜指针。此实现依据 [Apple的slide-v5定义](https://github.com/apple-oss-distributions/dyld/blob/main/include/mach-o/dyld_cache_format.h)、[fixupDataPages实现](https://github.com/apple-oss-distributions/dyld/blob/main/common/DyldSharedCache.cpp)，并核本机SDK `mach-o/fixup-chains.h` 的34bit runtimeOffset。只做离线unslid地址定位，没有PAC签名、认证、内存重基址或执行cache。

全局自动符号扫描180秒超时，私有汇编输出0B；改为逐框架符号和按函数quiet导出后成功。没有把工具超时当缺插件/固件结论。一次 `ps -ax -o pid=,command=` 进程表刷新被shell沙箱拒绝（operation not permitted），未换路线重试；这不影响本任务已知会话的退出确认，也没有停止或改动其他项目进程。

## 已补上的具体边

|边|本build证据|限定|
|---|---|---|
|LearningNode→实际插件|learning-loader 0x1b0491410/1414/1418传"SmartStyle"和version1；load-bundle 0x1b04910e0–1134拼VideoProcessors/SmartStyleV1.bundle并load；learning-loader 0x1b0491524–1530拼CMISmartStyleProcessorV1并classNamed|静态入口，不称该设备/该帧实际运行；encoder-loader 0x1b0a22fe8/22ff4从配置取smartStyleRenderingVersion再调用另一通用loader，不能将它也写成固定1|
|样式对象→renderer|metal-input-style检查smartStyleVersion==1才存对象+0x18；render-static 0x1d42f2208–2238分别读castType/castIntensity/toneBias/colorBias|这是内部style版本，与产品Styles2及HEIC16分开|
|tone/color/intensity→prior|prior-wrapper将参数转给direct内部方法并置isStartupPrior=0；prior-main 0x1d42ed848–89c对tone/color作[-1,1]、intensity作[0,1]的clamp并映射网格/分数，随后8角点FMA插值；0x1d42eda3c–70再按priorStrength与基础矩阵混合，prior-conversion重排并处理特定cast的通道平均|表、cast选择、startup与strength独立；不是toneEV，也不是一条曝光增益曲线。实际表未公开上传，完整数值模型尚待独立测试|
|configuration prior→shader输入|engine-tuning-apply 0x1d42e1ef0读linearSystemPriorMatrix，0x1d42e1ef8传builder setPriorMatrix；同方法设置Ext/Tik/EndLambda及三种plane scale；linear-systems-compile有CalculatePrior/AddPriorToLHS/RHS的确切shader名字和pipeline槽；enqueue把48B prior矩阵绑定buffer8、plane scales绑定14，LHS/RHS factors分属6/7|连接前阶段 `style_prior.py` 的显式buffer模型；ISPSMG分支另有门控，不能概括所有执行路径|
|P和S不是任意名字|engine-polynomial-count：order1→10、order2→7、其余→4；engine-system-size还依赖linearSystemType、weight/空间数量|不把合成布局当某帧真实配置|
|用户值与tuning→SSR参数|render-static分别复制cast/tone/color tuning到参数+0x24/+0xac/+0x1b4；条件场景可缩放用户值，之后intensity/tone/color分别写+4/+8/+12；render-setup实际分配params672B、stats10640B|输入参数不能直接当最终像素操作；stats、scene与tuning都参与|
|SSR参数→统计shader→LTM/最终渲染|render-compile将RenderingParamsFromStats存self+0x548；render-dynamic使用该槽并绑定params到buffer1、stats到3；metal-process先统计/动态参数、guide、segmentation、LTM、upsample、final，再按条件encodeLinear|只适用这个renderer内部已核分支。没有据此定义所有拍摄/编辑端全局顺序|

CommonSettings已证：configuration/tuning getter把用例转为NSNumber，在self+8/+16字典查找；loadTuning读取StyleEngineTuning/StyleEngineV1并经常量键映射重建字典。因此"12"候选值与已观察useCase12之间仍保留常量映射逐项核验义务，没有仅因数字相同就关闭它。

`_calculateCubicSplineToneCurve` 使用固定double控制点生成256个R32Float参考值，写self+0x270。本完整方法未读取用户tone字段；不能因方法名把这张固定曲线当滑杆公式。实际tone调整的可定位下一输入是RenderingParamsFromStats；其module11已在同metallib中定向定位，和此前91/92模块比较的历史分母分开。

## 新独立分支：SRL参数而非提亮增益

`srl_parameter.py` 对应 `_getAdjustedSrlCurveParameter` 完整40B leaf：读self+0x598的f32 curve与+0x5a0的uint32 adjustment；仅0<curve<1时返回 `f32(curve+f32(adjustment))`，其余包括NaN返回-1。必须保留uint32→f32转换；这不是face gain或原拍摄SRL重建。

`native_srl_parameter_check.py` 把40B原指令完整置于自有C ABI，两个字段来自合成buffer，没有ObjC/Metal/库调用。84组结构化边界和4096组固定种子raw-f32/uint32，合计**4180组、38组非有限输入，逐位差异0**；subnormal与非有限输入未删mask。FPCR=0、输入/输出/原指令/模型/测试产物SHA均记录。大uint32使不同curve小数部分丢失的反例保留，不能反向唯一恢复。

新增2项解密准入、3项cache映射/slide与2项SRL测试，加之前32项，共**39项通过，0失败/错误**。此前257头/通用头原指令验收没有重复运行。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_srl_parameter_check.py /tmp/psr-srl-new.json
python3 research/styles-firmware-20261022/export_cache_methods.py /path/to/owned-systemos-scratch /tmp/psr-cache-text-new
```

原始固件、FCS、cache和完整私有工具文本仍留仓库外；只读镜像已卸载，见systemos-cleanup收据。没有读取照片库/私人样本、改变锁屏/安全设置、停止他项进程、运行实屏或Photos。匹配iPhone原生GPU调用、原帧统计、完整拍摄逆与真实留出均未新增认证。下一静态/合成工作是RenderingParamsFromStats的tone→前景/语义系数分支，复用既有skin/semantic模型并保持采样、量化与原native证书边界。
