# 边界集合、真实枚举、九槽追踪及semantic/BG/FG推进

在 `7bfea4669401b34b9c4508562dcb79afa924a988` 的同一独立分支继续，参考仍是已核官方iPhone17,3 /27.0.1 /24A446、CMImaging UUID `0A9BC064-A4BC-330E-861A-C70A637B14B3`。新增下载0B，未访问私人媒体、未执行原iOS/GPU；没有重跑S8的409组、cast/SRL/prior/负Tone或S6两字段大批次。

## 边界合同：集合覆盖不算数值吻合

S8的27组pow边界上下文只能支持两支包络覆盖。FG mids约.15的差异**不能计为数值吻合**；历史收据原样保留，没有用本次小测试替换该差异。

`tone_boundaries.py` 直接对应同一原AIR11的实际比较：

|比较|实际运算符|等号归属|
|---|---|---|
|FG SSA342：post-pow f32 r 与.5|`fcmp fast olt`|false，即 `f32(1.2)*r-.5` 分支|
|BG SSA219：post-pow f32 q 与确切f32 threshold|`fcmp fast ugt`|有限输入时false，即 `.875*q` 分支|
|FG tone与.5|`ole`|true，乘.5路径|
|FG tone与f32(.4)|`olt`|false，另一组shadows/contrast/neck路径|
|负FG SSA303：a302与1|`oge`|true，选a302；false选a294|

非有限输入在模型域外；不据`ugt`的unordered语义接纳NaN。pow后候选范围先收为可能的f32值，再判true/false/undetermined；仍使用S7/S8显式4u宿主pow假设，并非GPU证明。负FG也传递其已存在的条件选择未决状态。

`ConsumerFields` 现在同时带40项下/上界、逐分支决策、`branch_determined`和`value_contract`。命名字段中的点值改称 `approximate_center`，不会称原生等价值。未决时 `ssr_block_f32()` 和中心skin渲染默认拒绝；只能显式 `allow_approximation=True` 请求一个不具原生等价保证的近似。BG/FG和semantic集合API直接接上下界，完全不依赖这个点导出开关。

`native_boundary_check.py` 仅新增12个相邻f32探针、24次group调用，并记录宿主实际post-pow f32值、比较结果、FG mids实值与区间，范围越界0。它没有重跑409组，也不把范围内改称紧密数值匹配。`(-2^-24,0)` 的可表示负Tone仍明确拒绝/unknown；−0走正分支。这是模型缺口，不是硬件阻塞。

## 两套真实枚举与未知值处理

从已取得的只读SystemOS cache补出8个完整短方法，1396B原指令逐条核cache；包括两个resolver、tuning字典初始化/冷路径、Foundation intValue及两个proxy参数方法。正文只存短文本和哈希。`collect_enums.py` 检查精确cache UUID/大小集合、主cache SHA、方法字节、常量整数class及实际ivar offset16，不执行ObjC初始化或错误路径。

|semanticStyleSceneType输入uint32|SSR sceneType /byte32|
|---|---|
|1|3|
|2|7|
|3|10|
|其他（包括0、21、UINT32_MAX）|4|

实际36B完整leaf含减1、unsigned比较、ADRP、三项表读取与fallback；新44组原指令比较差异0，ADRP相对布局保留且没有改原字。**S8 code21缩放只验证那段算术分支；21在此resolver不可达，不能据它声称这条参考调用链实际应用sunset缩放。** 低层 `scale_controls` 仍可做显式反事实研究，实际键入口 `renderer_enums.evaluate_runtime_keys` 使用真实resolver。

|tuning字符串|SSR tuningType /byte652|
|---|---|
|DefaultParameters|1|
|WYSIWYG|2|
|UB|3|
|DF|4|
|DigitalFlash|5|
|SWFR|6|
|Video|7|
|QuadraSFD|8|

字典按原8对key/NSConstantIntegerNumber重建，`intValue`实际从offset16读32位。未知键或保留值9进入0x1d42f3ae4→cold2；冷路径含条件字符串 `type != SSRTuningTypeCount`，没有正常枚举fallback。Python接口抛 `UnknownTuningType`，不运行断言、不把未知设成0/1。0/99等仍可作为既有系数模型的显式反事实分支输入，但不是这套实际字符串映射的产物。

## 九槽的定向拷贝/别名追踪

`trace_tone_slots.py` 对精确同一metallib的全部215 payload头筛类型/字段标记，只解码命中的8模块（1/2/5/6/7/10/11/13）；处理命名结构GEP、常量byte GEP、bitcast/addrspacecast、同偏移phi/select别名、标量/向量读写跨度和相关memcpy/memmove逃逸。只提交位置/哈希/统计，原AIR仍在Git外。

目标是BG byte512、536/540/544/548、552和FG byte560、604/608。每槽找到1个AIR11写入，在该有界扫描中读取为0，未发现相关copy intrinsic；**全部仍为unresolved consumer，不能标unused**。没有声称覆盖任意无类型shader指针或整个CPU框架。

CPU侧同时检查Metal renderer及新proxy参数方法：cast/tone/color `getValue:size:` 的确切目的区间分别[36,172)、[172,436)、[436,452)，都停在九个输出槽之前；proxy遍历参数的stride是672B。新导出保留实际指令及SHA，literal offset命中只列候选，未将其他对象的相同偏移误认成SSR字段。收据 `tone-slot-alias-trace.json` 明确记录该扫描范围和未闭合的无类型/CPU别名边界。

## 完整semantic helper与实际调用域

`semantic_tone.py` 独立实现AIR10:5976..6093完整helper，而非只套一个曝光gain或一条曲线逆。输入为调用点已经处理的working RGB、reference RGB、已对齐person weight、七个semantic系数及显式GTC red节点；没有把working/reference认作原始无风格图、LinearThumbnail或scene-linear P3。

原调用的working是SSA286（texture2的矩阵变换后再乘half linearBaseGain.field6），reference为SSA196（texture1经缩放与矩阵变换）；person为SSA96，已经经过可能的personMasksValidHint/skinRatioThreshold调制，不等于任意原始人像mask。

每个BG/FG分支依次：half曝光乘working→仅上限min1→像素GTC采样→按GTC系数mix→除reference→严格低于reference阈值则置0→LTM向1混合→HR向min(...,1)混合→乘reference；最后按person weight混合两分支。阈值是half `0x1c04 = 0.0039215087890625`，原比较 `half(reference + half(0x9c04)) < 0`；等号不置零。

采样坐标为 `float(half(scaled*half(half(width)-1)))+.5`，三个通道各读同一texture的red。显式供给的2..1024个half节点复用 `spatial_curve_retarget._evaluate` 的分段线性/clamp数学：pixel sampler的index是u−.5，故该节点/坐标接口在声明的理想宿主采样合同下等价。没有据此证明实际GPU插值量化、所有MTLPixelFormat或原拍摄GTC相同。

point模式逐步half舍入。集合模式接40项系数下/上界，按每个half算术步骤2u（u=2^-11）的显式宿主允许量传播，采样范围还检查区间内所有节点，不能只看端点或假设曲线单调。域为working RGB[0,1]、reference[2^-10,2]、person[0,1]、七系数abs≤8、节点abs≤8且指定坐标。非有限half中间结果或跨零区间除法返回拒绝/unknown，不归因于设备。

`native_semantic_tone_check.py` 保留完整原helper正文和可达metadata，数学/纹理intrinsic有公开明确的宿主shim：CPU float-linear/clamp采样及half mix/min等。136组（72结构化+64固定种子留出）、408分量逐位差异0，集合允许量越界0。**这是原helper加宿主shim比较，不是原GPU或原texture执行。** 比较后只加了非有限中间值拒绝guard，算术AST未变；`s9-source-links.json` 保留比较时/当前完整源SHA和AST连接，没有重跑136组。

调用域有两项不能省略：

- castType2会先修改semantic系数：tone≤0时将曝光字段2/3按 `1-.5*scaledIntensity` 向baselineExposure.field7混合；所有tone都将HR字段5/6向1混合。`semantic_caller.py` 在集合上做这些变换。
- **只有texture6或texture7缺失时才调用该helper。** 两者都存在时，原kernel走block290的预计算RGB纹理路径，本模型尚未覆盖。`tone_fragment_sets.forward` 要求显式两个presence bool；两者都true返回 `unknown_precomputed_semantic_path`，不会误走fallback helper。

`semantic-helper-contract.json` 保存实际SSA、字段、sampler编码、函数SHA和这些调用条件。guideTexture8/9还按BG/FG LTM及person混合成SSA350；新接口把guide区间一起传入BG/FG，未取其中点。

## BG和FG分别推进

`bgfg_tone.py` 分别实现两个helper的字段门控、顺序、初始/最终混合及完整共享inline mids算子。绝对值门控为原f32常数，strict `<`跳过，等号执行。系数、RGB、guide和未决状态按集合传递；可选分支计算并集包络。

BG顺序覆盖shadows→contrast→whites(mode0)→airyGamma→mids→sat→localContrast→gammaContrast→两段lighten→underGrass→richSat。FG从personMix初混开始，覆盖whites(mode1)→shadows→neck/tonalContrast→contrast→sat→airyGamma→mids→underTone→两段lighten→smartContrast，最后按person再混合。原FG9/10的skin helper是另一个消费点，不能把它冒充此FG helper全体。

目前只有共享mids和基本混合有独立数值实现；其他叶函数没有实现时返回 `unknown_operator`，携带具体名字、已完成trace、当前RGB输入集合与原未决状态，**output为None**，不会静默作identity。`tone_fragment_sets.py` 按实际semantic→BG→FG顺序接这三段；它遇缺叶、未建模预计算路径或guide域越界会保留unknown，永远不声称完整相机管线通过。

新增受控native比较保留原BG/FG两个helper完整正文，只令neutral/mids路径活动。20个其他叶/非活动intrinsic用会终止本任务checker的stub，防止误把未建模数学算通过。48组、144分量逐位差异0、集合越界0；这只支持该受控路径，不能当完整BG/FG通过。之后仅扩展PixelContext以接guide区间，mids及controller算术AST未变，源连接单列。

## 验收矩阵与剩余项

|目标|所需证据|本阶段结果|状态|
|---|---|---|---|
|边界合同|实际f32比较/等号、集合接口与相邻输入|12组记录真实值与范围，范围越界0；未决中心默认拒绝|集合覆盖；非数值吻合|
|真实枚举|同cache表/字典/getter/未知分支|8方法1396B；scene44组原完整leaf差异0|通过限定静态/CPU域；未执行ObjC/错误路径|
|九槽连接|明确范围的读写、拷贝和别名|215头/8模块+相关CPU；每槽1写0读|仍unresolved，非unused|
|semantic helper|独立全部方程+原正文宿主比较|136组/408分量逐位差异0，显式采样/精度假设|通过限定helper域|
|BG/FG推进|各自controller及活动叶比较|48组/144分量逐位差异0；其他叶fail closed|部分；完整数值模型未完成|
|回归|边界/未知/错误输入/集合后传|81项单元测试通过，0失败/错误|通过|
|原iOS/GPU和真实帧|匹配环境、真实bindings、同帧上下文|本阶段没有这些输入或运行|待依赖，未验收|

可继续实现而非环境阻塞的具体项：BG/FG的whitesCurve、ShadowsFilter/Negative、contrast、airy、sat、local/gammaContrast、lighten/negativeLighten、underGrass、neck/underTone、smartContrast等叶模型；block290预计算semantic路径；九槽未闭合consumer/无类型别名；负小幅Tone域。现有曲线集合逆与皮肤模型继续复用，但尚未证明它们替代上述全体。

真正待依赖的验收仍是iPhone17,3 /24A446原运行环境、实际loader/function constants/bindings和授权同帧params/stats/tuning、mattes/guides、曲线、颜色与存储域、配对图像。IMG_2810的精确capture build和iPhone19,2资源仍缺；不混机型，不承诺仅成片唯一逆，不改S20证书。

## 复验命令

Python3+NumPy；新宿主检查需Apple Silicon、xcrun/本机LLVM。输出路径应尚不存在，原AIR/资源继续保留在Git外。本轮仅新上述小批次，不必重跑旧验收。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_boundary_check.py /path/to/private/0011.ll.txt /tmp/psr-boundaries-new.json
python3 research/styles-firmware-20261022/collect_enums.py /path/to/verified/cache /tmp/psr-enums-new.json
python3 research/styles-firmware-20261022/native_scene_enum_check.py /tmp/psr-scene-enum-new.json
python3 research/styles-firmware-20261022/trace_tone_slots.py /path/to/verified/default.metallib /tmp/psr-slot-trace-new.json
python3 research/styles-firmware-20261022/native_semantic_tone_check.py /path/to/private/0010.ll.txt /tmp/psr-semantic-new.json
python3 research/styles-firmware-20261022/native_bgfg_mids_check.py /path/to/private/0010.ll.txt /tmp/psr-bgfg-mids-new.json
```

不合并、不删分支、不force push；没有操作其他项目、进程/caffeinate、锁屏或安全设置。既有ps拒绝未重试/绕过。只卸载本任务的只读镜像，固件/私有AIR/表/照片均未提交。
