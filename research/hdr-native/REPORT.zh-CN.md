## HDR-NATIVE-20261019：独立 HDR 目标与场景恢复持续目标（S29–S32）

**目标已建立并进入实施，active；A阶段及总验收仍未完成。** 新方向分成“独立HDR制作/承载”和“物理场景恢复”两个验收面；global、local、语义/纹理控制和显示渲染分别保留。旧模型、Apple Log、原mask、half/float/1e-3门槛不变；用户已收尾的bit-exact方向不重新启动。新脚本及入口在`repo/research/hdr-native/`，`GOAL.zh-CN.md`/`IMPLEMENTATION.zh-CN.md`和`operator-registry.json`标明证据级别。不是完成场景恢复后就把线性像素直接显示；母版之后保留独立HDR显示渲染。

**已验证（静态，HDR-02）：** `operator_recipe.py`封装26A434已知输入上下文的consumer local620/624→1、皮肤色彩592→0、亮度596→0独立目标。端点沿用S27原PSO证据，参数字节外不动。中间strength是明确的工程withdrawal policy，不是Apple UI tone标定；全局曝光/相机j/Studio未识别字段不猜。仅有最终Y时必须求`{F_target(A):F_applied(A)=Y}`，不能把Y当原输入执行负tone。原33皮肤点紧外包络及C01–C05缺口保持，未以点估计或缩mask过关。

**已验证（数值，HDR-03–05，26A434）：** S29原CoreImage双图writer/reader有5组带map合成输入、7档headroom：35次公式对照maxabs=1.96372652805e-06，最小PSNR=131.739826dB，均过原float门槛。与原`_flexMap`一致的采样后方程为

```
scale=clamp((log2(displayHeadroom)-baseCapacityLog2)/(alternateCapacityLog2-baseCapacityLog2),0,1)
signedPow(g,q)=sign(g)*pow(max(abs(g),1e-6),q)
logG=(maxEV-minEV)*signedPow(code,1/gamma)+minEV
out=exp2(scale*logG)*(linear_P3_SDR+offsetS)-offsetH
```

仅覆盖同尺寸合成网格；不把它当全尺寸低分辨率map采样或逆消费端验证。S30显式供给预定RGB比值，未编码原生应用70次（5组×2上下文×7档），maxabs=8.10341341584e-07、最小PSNR=133.49464dB；完整强度对预设HDR目标maxrelative=2.37367161424e-07。它证实RGB Gain Map能承载空间/通道定向校正，并不提供可信场景H本身。S29分析里`known_pair_saved_f32_log_map`字段实际只做float32 cast，没有落盘再读；该字段不作新存储验收。真正保存后重建的旧S28结论保持独立。

**已验证（静态推导，HDR-12）：** SDR/HDR分量为正且offset为0时，中间headroom为`S^(1-w)*H^w`，即RGB几何插值。它一般不等于重新以Apple某个UI tone运行LTM，也不会自动给global/local/semantic各选独立headroom强度。制作阶段保留各项控制，合成为H之后仍须逐档验证中间显示条件。

**已验证（数值，HDR-04/06，失败也保留）：** S29便捷双图writer重新编码SDR，五个目标HDR重建均未达门槛；rgb-opposing maxabs=.245859146、PSNR21.5723dB。另两个峰值<1的原始合成目标没有返回map，仅作这两个输入的边界观察。S30显式`HDRGainMapImage`虽写出文件，但本次10次均输出legacy Apple单通道8bit，不含ISO metadata；RGBA8/RGBAh成对文件SHA相同。不能从format请求宣称得到12bit RGB map。相关容器解析在`evidence/S30-container-inspection.json`。

**已验证（数值，HDR-07/08）：** S31把独立编码的RGB gain替入ISO tmap，原primary全部coded descendants和颜色/几何property逐项一致。十个8/10bit合成载体原ImageIO解码SDR maxabs=0。新目标编码尚未通过：matrix0 RGB在aux原生读回有大幅代码偏差（flat1会出现约1.886的分量），这远大于量化误差；五个12bit文件均native nil。1e-3与PSNR不放宽；不能把未解码12bit的理想量化理论当原生通过。

**已验证（数值，HDR-09）：** S32只用rgb-opposing合成图，固定其余条件，单独对比matrix1/6和8/10/12bit；另读同一gain文件的原生primary/raw和libheif结果，不用翻转数组选择最佳分数。每项结果如下；nil是该文件/路径的观测，不是所有12bit或真机的普遍结论。

matrix1/6的8/10bit中，primary/raw与aux记录的最大代码误差相同（尚无逐点差分验收），vertical-flip明显更坏；可定位到编码/原生读回RGB转换，不能归因于消费端逆解。matrix6/10bit的HDR目标maxrelative约.00533125、PSNR51.3941dB，仍未过1e-3。12bit的CGImage/CIImage对象均能建立，但primary render代码maxabs约.99829，aux路径nil；缺的不是单纯“文件打不开”，CPU provider/GPU转换须继续隔离。

|matrix|bit|native rc|primary/raw code maxabs|aux code maxabs|HDR target maxrelative|PSNR dB|
|---|---|---|---|---|---|---|
|1|8|0|0.007490220256880176|0.007490220256880176|0.022992088941984706|38.64950512206328|
|1|10|0|0.0019070285273203869|0.0019070285273203869|0.005647225218517165|50.855689974188714|
|1|12|5|0.9982905982905983|None|None|None|
|6|8|0|0.00731475867477116|0.00731475867477116|0.020610088443077365|39.222406247068434|
|6|10|0|0.0017941373883804124|0.0017941373883804124|0.005331253818467697|51.394126018201604|
|6|12|5|0.9982905982905983|None|None|None|

**已验证（静态，HDR-10，参考build24A446）：** 从已有CameraColorProcessing只读汇编补齐`LTMProcessor.process`的统计生产支路：`0x256b64468`判断globalCCM，`0x256b644d8`以signed Q12矩阵预处理；`0x256b64598`可选dehaze；`0x256b64d84`把结果送到HITH统计，`0x256b64e20`求曲线，`0x256b64e50..e5c`合并输出metadata。它不证明这些shader就是最终照片的同一处理，也不证明文件c/d等于所有拍摄端LTM。source UUID0A211E15-50CA-373B-AD9A-F9E3283C68F4 / SHA974ffb2895cae06e26e63bd77ab4891f5401d4789449f7a0080d377553b2426e；原汇编SHA3c84b9b812f06dccdd8b03b1a2b6f4935c46ed5e084cdd21ab61e170111cd823。它是iPhone12,1/iOS27 24A446参考，不是IMG_2810的匹配同帧证据。

**可交给macOS runner，HDR-11：** 先把native gain读回域/有效精度闭环，再冻结目标配方，测试真实5张原尺寸、2张冻结后留出，以及不同headroom下边缘/色彩/传输和ImageIO全尺寸SDR max0。S29–S32只用合成输入，新阶段真实照片数=0，旧5图的旧算子证明不重复也不冒充新目标验收。消费端目标参数隔离和条件曲线集合逆可接入新HDR制作；完整生产逆、不可逆区间和不确定性仍单列。

**待实机解决：** 匹配iPhone18Pro/iOS27.0.1同帧的j/WithoutFaceBoost配对global/local曲线、N、B/T、人脸hist、allocateTone constraints、真实应用域；原Studio统计/纹理；配对RAW IMG_2679/IMG_2408；实际HDR屏幕和观看环境。β=.1953125仍不是像素EV区间。LinearThumbnail保留Apple Log，无203nit标定。固定ACES1.0 SDR Video预览仅诊断；本阶段无人物预览或明文上传。

六次run（含S29初次缺map失败、S31导入失败）均保存不可变ZIP并stream SHA/full manifest逐成员核验。artifact retention-days=1，均xcode-27/26A434/image20261012.0260.1；详见本阶段`run-provenance.json`。没有上传Apple整binary或人物数据，没有创建secret/release。`validate_hdr.py`独立报告两个验收面，不覆盖冻结validate.py；总acceptance_complete=false。


### HDR-NATIVE-20261019 / S33–S35：区分两类 map，保留失败边界

**已验证数值，HDR-13。** S33 run39241066681 / artifact12181247833 / source659ddc6：四个既有合成文件×两种cache模式，12bit两种矩阵均存在CGImage但provider为nil，Quartz与CI软件/Metal均RGB0；direct expected float32对照两种CI路径maxabs0。首个可观察失败环节在provider解码，不是已证GPU算术故障。8/10bit软件/Metal、URL/CGImage/aux显式pairwise不同分量0，仍有code误差；10bit CI maxabs0.001794159412，Quartz float0.000985130668。编码目标门槛不变，不据两文件推断全部12bit/设备支持情况。

**已验证静态，HDR-14/15。** macOS26A434 `CMISmartStyleMetalRendererV1 _updateRenderPipelineConfigForInputs`0x23336ecd0在linear任一边小于主图时置shouldCreateLTMGainMap；`_processLTMGainMap`0x2334d4fd0生成bg/fg RGB maps（slots8/9），以原inputImageTexture作guide上采样。它们与c/d的标量light maps（slots5/6）是不同资源。AIR0007 lines47–300、625–647给出：输入转work-linear及CCM为A；linear输入CCM并乘linearBaseGain为X；分支k的U=min(half(e_k·X),1)，GTC取样像素坐标float(half(U·half(width−1)))+.5，T=mix(U,GTC(U),half(w))，q_k=half(T/A)，half(A−half(1/255))<0时q_k=0。输出是线性RGB比值，不是log gain。SRL-before-stats和transfer非0分支仍需实际上下文，本次控制仅SRLfalse/transfer0/identity CCM。

最终AIR0010 lines360–438按8/9是否为空选预计算或inline；预计算分支是A·mix(q_k,1,l_k)，再HR限制增益、按person混合，并继续c/d派生参数与BG/FG/色彩算子。忽略half/guided/HR时为(1−l_k)T+l_kA。因此l=1是保持输入A，不能称为撤销A内烘焙local。原S27/recipe620/624→1的已知输入反事实证据保持，不作为scene逆解。此前512主图/1024thumbnail的inline捕获不能单独覆盖原件尺寸下的RGB map分支。原文件及冻结模型均不改。

**已验证数值，HDR-16/18。** S34 run39244341548 / artifact12183626142 / source47e0317：三组合成输入的small RGB maps与原host imageblock结果逐位相同；nonlinear case plain/imageblock最多差0.001953125，后续保留原PSO变体。compile-only host虽返回0，却仅一个create dispatch、无guided调用且full输出为零，不能计oracle。静态原prepareToProcess:2（0x23336a748）经_allocateResources（0x23336a7b0）建立guided实例；S35补此调用，没有改原shader。

**已验证数值，HDR-17；输出认证可交给macOS runner。** S35 run39245992644 / artifact12182822786 / source42f0b0f，三组各捕获两次原CMIGuidedFilter、RGBA16主图guide、r=1、epsilon=0.0010000000474974513。S35因错误沿用scalar light map的.05预期而显式失败，未存full map读回，原始失败归档不改。RGB路径的实际eps是.001；已有c/d scalar路径.05结论不受影响。S36只修正这项预期并强制两次实际guided与七个dispatch，继续原生输出对照；不是调平滑或放宽误差门槛。S34 direct GDirect(.05)保留为不匹配参数的控制，不能冒充RGB原host oracle。

**已验证静态（标签勘误），HDR-19。** S29–S32共用Bin曾把raw gain code sidecar标P3，实际计算比较的是unitless code；旧归档不覆盖，S33已明确编码坐标与色彩空间分开。S29的“float32 saved”亦仍是既存勘误：该段只cast，无真实save/read；实际保存证明是S28，不能混计。

本轮截至S35仍0张新真实照片、0张新全尺寸验收；合成验证不计五张照片或留出。A_phase_complete=false，acceptance_complete=false，33点原mask/1e-3与half/float门槛不改。全尺寸RGB新路径、独立global/local/semantic目标、编码精度和中间headroom继续runner；同帧j曲线/统计、原Studio统计、RAW2679/2408和实际HDR屏幕仍待实机。LinearThumbnail保持Apple Log，无203nit标定。

证据索引：`hdr-native-20261019/run-provenance-s33-s35.json`及`s34/static-receipt.json`、`s35/static-receipt.json`；所有结果均26A434 / image20261012.0260.1，ZIP及manifest全员SHA已校验。每条数字在analysis-s33/s34/s35.json与errors.csv单独列明。


### HDR-S36：原 RGB guided host 输出闭环（合成算子范围）

**已验证数值，HDR-20。** S36 run39246456413 / artifact12183985709 / source5364da810b66eb7f71992d4ec9a35360686a1b17，26A434 / image20261012.0260.1。ZIP3,983,408B SHA0bee8e0a3a950e98b503cca3ffc805d8927311ade3fc86105870245c2464a2cb，manifest SHAa9985c9b326ad97c013bd87501a532add159d34465744b0a84905272592c30aa，全部成员校验通过。三组原host都实际执行两次CMIGuidedFilter（r1、eps=.001、RGBA16主图guide）、共七dispatch；small map与S34 imageblock原生控制逐位一致，全尺寸合成RGB map已取得有效oracle。

冻结NumPy guided在identity case逐位0，另外两例最大gain abs=0.0009765625，最低PSNR=77.8825417dB，最大局部relative=.00120264582。half_bit_exact=false；不改变half/float/1e-3门槛，也不重新做算术精度拟合。相同small q的bilinear对原host可达maxabs=.152099609375、positive-pair maxEV约1.2525，显示滤波路径不能互换；这些数字不是RAW误差或“光晕减少”的感知证明。

R-RGB-HOST在三组合成上下文范围完成；R-RGB-FULL、独立global/local实际拍摄端分解、33点全域界、原SDR保持的编码目标仍未完成。下一轮S37冻结新配方后使用五张原分辨率样张，0032/0033只作为本新配方留出，注明它们参与过旧研究；不把旧scalar.05 oracle重计为RGB.001验证，不把候选升级成物理scene-referred。


### HDR-S37–S41：原分辨率前置条件与失败证据

**已验证数值，HDR-21/25。** S37（run39249246604/source d4e9fe7）在map探针编译时失败，行注释吞掉闭括号，尚未解码照片。S38（39249843977/source10f7588）修语法后完成五张原尺寸源准备：2600/2604/2608为5712×4284，0032/0033为4032×3024，原Apple Log和GTC正常；但map均返回5。该时点没有保存native.json，实际exception已经随本轮临时目录清理，不能凭记忆补写或把后续合成错误码移植到它。密文预览artifact12184434576经ZIP/GPG/manifest校验，PNG数0，不存在可供展示的伪造预览。S39（39251392813/source0ace587）因诊断变量与原allocation对象重名编译失败，亦未执行图像生成；这些失败如实保留，不计照片验收。

**已验证数值，HDR-22。** S40（run39252096517/source90ecd44/artifact12185683191）补齐stderr、原生状态/allocator/checkpoint。原构造器建立type2、144MiB（150994944B）池：1280×960两次guided/七dispatch正常，输出所有RGB分量均0.111083984375；4032×3024、5712×4284在任何guided调用前返回−73465。此为受控合成条件的真实边界，S38仅有exit5，不能回填同一错误码。macOS静态initWithMetalContext0x233369dd4、prepare0x23336a748和_processLTMGainMap0x2334d4fd0的相关行见s41/allocator-init-excerpt.txt（原行号、SHA/UUID均保留）。

**已验证数值，HDR-23/24。** S41（run39253046695/source4807ebb/artifact12186850154）通过原initWithMetalContext: API供应2GiB的type2池，没有改原host方法、metallib、图像参数或guided的r1/eps.001。4032×3024和5712×4284均完整运行两次guided/七dispatch，全幅非零、无nonfinite；1280×960默认144MiB与2GiB池，两张small/two full读回SHA全相同。原构造器descriptor setter实测：wireMemory=true、allowFallback=false、autoUseSubAllocators=false、resourceOptions=512；共享访问小池46080B。这里的setWireMemory:1不能猜成setAllowFallback:1。测试的capacity及label不同，其余所列descriptor设置相同；真实Photos调用者的内存预算尚未识别，不能冒称production配置相同，更不是整个非有限/fast-math域的证明。

下一步S42保持S37冻结数学配方，使用已验证的原API大池条件继续原尺寸五图，保留每次native.json/checkpoint与来源SHA。原native源准备只是新算子的输入依赖，不重新优化key1或重跑旧30个scalar-guided实验。遇到基础设施失败即保全诊断并停止同类照片重复；不放宽旧门槛。输出global-only仍是supplied-GTC假设、local-only是曲线保留的投影候选、both是相对linear-P3母版候选；人物/皮肤/texture逆向保持独立，物理scene验证仍需RAW/同帧曲线。

五张新候选目前通过数仍0，原SDR编码max0未验收、A_phase_complete=false、acceptance_complete=false。汇总与全部SHA见run-provenance-s37-s41.json；所有像素/预览仅密文，公共artifact只含汇总文本。该时段未创建secret或release，未上传Apple整份二进制；研究临时分支在实际source commit保留并审查引用后清理。

S41用语边界：这里的“原PSO”指使用原框架函数和原host建管线方法，没有重写shader；并未证明不同进程/不同context的PSO对象或底层编译产物字节身份。实际Photos调用者的资源预算仍未识别，三组合成与固定小图SHA对照不代替全域合同。


### HDR-S42：五图原尺寸 RGB 投影、独立 HDR 与承载分离验收

**已验证数值，HDR-26/27/29。** run39254061338 / source5ab81cf3d4b1253455dc4cd6efa1bf7e4cab75bc / xcode-27 / macOS27.0.1 26A434 / image20261012.0260.1。S37数学配方不改，仅接入S41验证的大池前置条件与完整诊断。原host对5照片的2个变体各执行2次guided/7dispatch，RGB eps.001/r1/全分辨率RGBA guide，参数和源纹理SHA不变。0032/0033在本新RGB配方冻结后才用于验证；它们参与过更旧scalar研究，不称完全未见照片。

十份EXR实际保存并读回，存储分量差0；float32 unitless log2 RGB map的正比值mask内重建maxrelative≤6.60515477177e-07。原CI五档headroom1/1.25/2/4/8共25比较，公式maxabs≤5.60320626897e-07，PSNR≥148.357935dB，无nonfinite。h1与所供float32 SDR分母max0，仅证未编码调用，**新编码HEIF、原ImageIO全尺寸SDR max0仍未验收**。原SDR coded数据本轮未改。

**已验证数值（失败边界），HDR-28。** Apple Log锚点面积诊断如下。正比值coverage是承载mask，不是皮肤33点或原消费端逆mask，绝不拿它替换原验收mask。

|照片|原件画布|锚点均值绝对EV|p99 EV|max EV|正比值承载coverage|
|---|---|---|---|---|---|
|IMG_2600|5712×4284|0.330882|3.402471|14.715423|97.7627%|
|IMG_2604|5712×4284|0.137667|1.074551|13.555624|98.0662%|
|IMG_2608|5712×4284|0.204337|1.748978|12.872202|97.3047%|
|IMG_0032|4032×3024|0.009532|0.046146|3.561942|99.9361%|
|IMG_0033|4032×3024|0.020795|0.059394|27.147115|99.7618%|

误差在近黑和极值区仍大，尚未分清原create-kernel的1/255阈值、采样和half各自贡献。不能因为调用Apple算子就把投影当完整scene恢复。gain梯度/Laplacian极值已入errors.csv，但不足以证明无光晕/振铃；当前对照是相同Apple small q的双线性，**尚未完成旧2048双线性+2x2面积约束的逐项比较**。不改变原门槛或旧mask。

**假设，HDR-30。** 六路输出继续分开：原SDR、逆key1、给定GTC的global-only条件逆、保留给定GTC的local-only投影、both相对linear-P3母版候选、其后的独立HDR渲染。给定GTC不等于已经识别真实拍摄端全局曲线；本试验未自动撤销人物/皮肤/texture。母版的相对曝光尺度与最终显示曝光是两个不同量。S42渲染保持冻结的H=M·8/(8+Y_M)、曝光1，没有为改善图像而事后调参；在统一ACES0EV下明显偏暗，故它是可复现的第一版显示意图，**不是最终HDR效果验收**。下一版可单独定义全局显示曝光，不能回写/重标原场景母版或冒称物理曝光标定。

全部30个显示变换前后输入SHA及各源main/float32 SDR/thumbnail文件SHA一致。35张PNG只以密文artifact12187257542传输，GPG和manifest每个成员均验证，本地只展开5张contact。固定预览：OCIO cg-config-v2.2.0_aces-v1.3_ocio-v2.4（SHA5aefc668796eabb1902b9593340496231758eceaec18ce290e12901042bd4440），LinearP3-D65 → sRGB Display / ACES1.0 SDR Video /0EV；无203nit标定，Apple Log未改。实际HDR屏幕与观看环境仍需实机。

文本artifact12187592176 ZIP SHA 17bc8b897f51d04779f8a6b3543ccbbc980dc247d25e235059895f01ffeef0f9，manifest SHA 8c378bbce6b411b3ec708ad99fd0b54a707061d173bf75f273c28ef8f3a7fb0a；密文预览ZIP SHA 5243842ad5fc34096354b6df4a7d240d39c240b5d5ee7e209832648ffd70d802。完整5图密文约1.25GB，当前100MB写入上限与4GB剩余底线下尚未下载，具体每份ID/大小/SHA见s42-encrypted-inventory与GitHub artifact metadata；已提具体额外存储许可，不把远端短期产物说成本地归档。A_phase_complete=false，总acceptance_complete=false。33皮肤点全域tight hull和同帧拍摄曲线/原Studio统计/配对RAW边界均保留。


### HDR-S43：AV1 编码候选的原生边界

**已验证数值，HDR-31/32。** run39256675682 / source8b0e656fedbf75dc6bcb2a86e846e71bc318def7 / artifact12187639046 /26A434。沿用S31固定rgb-opposing目标和3.5EV范围，改用libavif1.4.2/AOM lossless 4:4:4，matrix0/6各10/12bit。四文件独立ImageIO provider均成功；matrix0 libavif整数回读差0，CI URL/CG读回仍有约.00173–.00191代码误差，CPU Quartz再包装更近。原native浮点通路对照仍通过，不能把此误差归因于消费端逆解或所有12bit不支持。

原HEVC primary coded bytes/颜色几何props/ftyp保持，实验性av01增益item/av1C替换的四组合均ISO aux和CI gain为nil、compare返回5（ISO native input nil）。未证明此mixed-codec容器格式合规，亦不能推广成所有AV1 gain map不支持；本路径不计自动HDR封装通过。libavif实际header SHA43ec2563fcc739a4d5ca18e22f74bc15e76a11f8c9a82bd7e1ee572bff7afc04、上游模板ZIP/SHA、每个编码文件SHA和原生对照均在s43 evidence。

同一目标量化：10bit理想maxrelative.001183817/PSNR59.0586dB，12bit.000293977/71.1156dB。前者即使不计原生误差也未过1e-3/60dB；不得缩窄目标EV范围或改mask后宣布通过。12bit理想可达标不等于当前原生载体支持。这里量化指标中的linear maxabs另列，编码目标仍沿原maxrelative/PSNR门槛，不把其`gate`字段（采用线性算子1e-5）误作同一个验收。


### HDR-S44：显示试验前置失败，不冒充新图像结果

**已验证数值（失败边界），HDR-33。** run39259341766 / sourcee6138d042336fdcf2d2bc5ccb4e758455c7339a6 / artifact12190285705。显示曝光/common offset配方已经冻结，但第一次tarfile读取收到“not a gzip file”，没有执行新显示/原生像素对照，亦无新预览。原GPG私有stderr和返回码未入档，故具体失败原因仍未完全定位；先前“没有加密子钥”的推测已撤回，本地实际有ECDH子钥。该artifact的photos_used=true仅描述计划输入，不代表实际完成照片。

本地随后以400MB scope流式校验同一327MB密文，完整ZIP/cipher SHA和GPG DECRYPTION_OKAY/GOODMDC均成功；只丢弃解密输出，不保存大文件，不做图像计算，子进程最大RSS35MB。第一次取session的解析仍误用了面向人的格式；GnuPG官方DETAILS规定machine-status为SESSION_KEY <algo>:<hexdigits>，修正解析后才继续，不把parser错误说成密文/GPG失败。原失败和收据均不覆盖。

S44临时secret HDR_S44_ARCHIVE_SUBKEY已删除、列表核对为空，无release。S45仅用单密文session，通过fd传给GPG，不再把归档私钥交给runner；先验证完整SHA/GPG/文件头再读tar，增加仅含状态事件名的脱敏诊断。render_intent_s44/read_sdr_s44/unencoded_s44数学依赖不改。原精度、场景/语义mask与SDR门槛不变。


**S45失败边界（已验证数值，HDR-34）：** run39262070080/source24d618dd7467fce33452d9bc012891b8ade40389/artifact12190163508。runner没有rg，GPG选项检查exit127，未到下载/图像计算。失败日志先读后归档，S46改用Python membership，无需为该检查安装新工具。S45临时session secret已删除并核对空列表；没有新图像可计入验收。会话提取应按机器status捕获完整payload再规范化algo:hex，不能用人读格式或误截token；完整密文SHA/GPG校验与会话格式解析分别保留收据。


**S46失败与小型对照（已验证数值，HDR-35）：** run39262796015/source3f876035d17f6b2fb93fb834d343661492ef949c/artifact12192760214。脱敏GPG返回2/DECRYPTION_FAILED，未做图像计算。706B空密文对照确证会话字段为带AEAD模式的9.2:hex；原regex截成2:hex，fd解密失败，而保留完整payload返回0、明文逐字节相同。S47仅修该传输格式与标签，不改S44显示数学。临时HDR_S46_S42_SESSION删除后空列表已核对，无release。既存S44解密失败的私有stderr仍缺，不回填成相同原因。


### HDR-S47：独立显示渲染完成一张原尺寸实拍；offset 失败照实保留

**已验证静态，HDR-36；显示意图自身为工程选择。** `render_intent_s44.py`定义母版之后的全局显示尺度：在固定中心采样网格的正亮度域计算`k=2^median(log2(Y_SDR/Y_M))`，再以`H=kM*8/(8+max(Y(kM),0))`作独立HDR目标。正亮度域`dY_H/dY_M=64k/(8+kY_M)^2>0`，共享RGB标量保持色度；没有新空间邻域操作，不能据此证明母版无原有光晕或已逆相机local。8为相对亮度滚降参数，不是全RGB硬上限，也不是203nit。Apple Log和相对母版不改；这一步是显示曝光/意图，不是GTM物理逆解或相机j幅度。

**已验证数值，HDR-37。** run39264474802/sourced657f306cdff1c0652f4538ddb5ed303d46d2d99/xcode-27/26A434/image20261012.0260.1。重用S42 IMG2600的5712×4284 half-P3母版，输入EXR SHA69c553e49f3c70ffbebc6e85d32ad6933fe3582535088dd24f60f59c398c4634；没有重算既有key1、Apple Log或guided。显示曝光3.718534360EV（k=13.164076042，统计677174点），原件/原SDR/母版EXR及pixels前后SHA相同。正Y域float32 RGB/Y色度差最大3.13367019444e-07，只是数值诊断，不借此认证scene。该新显示配方仅1张开发照片，不能把旧S42五图/2留出重复计为本新显示目标验证。

两个offset变体各5档headroom1/1.25/2/4/8，共10个原生未编码公式对照，maxabs≤4.7088888806e-06、PSNR≥132.827091506dB，原float门槛通过。各自的目标承载结果须另外验收：

|变体|可表示比值覆盖率|保存f32 logmap maxrelative|原生h8对目标maxrelative|原生h8 PSNR|原生h1对原SDR maxdiff|
|---|---|---|---|---|---|
|offset0|97.762716%|3.30480318222e-07|1.56001707439e-06|129.734769|0|
|公共offset 0.0307447053492|100%|0.00252261043998|0.0253673864137|134.842219|5.96046447754e-08|

**已验证数值，HDR-38/39。** offset0在原已定义比值区内通过，full目标maxabs7.62939453125e-06；承载mask与全部原逆解/33点mask分离。公共offset令`S+o,H+o>0`后可保留signed RGB，全图数学比值可定义，但float32存储及原生近零分量相对误差未过1e-3，h1也非像素0差，故不能拿覆盖率100%或高PSNR代替通过。最坏relative点参考RGB分量`abs(H)≤maxabs/maxrel=0.000263161529768`；这定位到近零分量，**不是整像素亮度或所有失败点的逐类归因**，坐标未捕获。误差与offset加减及log/exp的消减敏感性相容，进一步数值定位可交runner；不缩目标、不改旧mask、不放宽门槛。

**显示与物理逆解分开。** 中间headroom（给定公共o）是`(S+o)^(1-w)*(H+o)^w-o`，并不自动等于Apple UI某个tone；各global/local/semantic控制仍在制作阶段独立。给定GTC的global-only、保留曲线的local-only和语义反事实依旧沿既有边界，不把这次全局显示曝光称为相机GTM恢复，也不把母版残留semantic/纹理清除视为完成。

10张PNG全部只加密上传，GPG/manifest逐项验证；本地仅展开contact。所有显示均固定OCIO cg-config-v2.2.0_aces-v1.3_ocio-v2.4 / LinearP3-D65 → sRGB Display / ACES1.0 SDR Video /0EV，9次预览前后输入SHA相同。native中间headroom预览从全图结果固定中心采样，不是实际HDR屏幕照片。指标artifact12192990470 ZIP SHAcb50ff395ff71f6b4b52d8d7f5fc7706965993e66734bd398514473bf712bcdb，manifest SHAcaa31e04df8c3bab2b0c9a93e8129825ec9705b4950604e43ff53dc8b2d471ef；预览artifact12192990472 ZIP SHA3fd3f2025b3696a5893318949c71f4ff7f7828840bdb8ca87eb29f46ecc65fb7，cipher SHA806135785421f6fa5080e49a4c7a88ee2282666a67d2a4972158f13bc7ead8f8。输入大密文在runner完整SHA/GPG/GOODMDC/gzip1f8b先验证，GPG2.5.24，只有一次性session，无归档私钥。HDR_S47_S42_SESSION已删除并核对空列表，无release；临时分支待exact source保留后清理。

本次原尺寸H和logmap只用于计算与原生对照，**没有另行归档完整新像素文件**；保留配方、原母版引用、摘要和密文预览。原S42全套EXR/GainMap密文约1.25GB仍受100MB写入/4GB底线约束，仅2600密文做过流式SHA/GPG验证而未保留；不能称全套本地归档。原SDR未重新编码，但尚未生成新HEIF，**新编码ImageIO全尺寸SDR max0、编码目标和5图独立HDR渲染验收仍未闭环**。A_phase_complete=false，acceptance_complete=false。


S33–S47收尾审计：所有实际source commit已fast-forward保留在research/vm-native-20261018@c12f2aa。确认15条临时分支无PR head/base或外来ref指向后删除，local16条含最终临时文档分支亦删除；secret/release/活动run均为空。既有PR#1（其它研究head→本研究base）仅记录，未通过API创建/关闭/操作。7份受保护文件、原始171条claims及文档/CSV历史前缀SHA不变；旧workflow没有修改或删除，15个新增workflow所有artifact保留1天。最终A阶段及总验收仍false，目标active。详见final-audit-s33-s47与transport-cleanup-s33-s47。


### HDR-S48/S49：旧面积约束与原生 RGB guided 投影的配对比较

**已验证数值，HDR-40。** S48 source7d3918575afb852e3be048f5f54da313db517797/run39270202659在draft密文asset元数据读取HTTP403，尚未执行driver。S49 source9ab3060ff6780f0dd0e154f5036a6243503c6659/run39275948343只修正传输权限与自有draft清理，图像计算公式未改，26A434/image20261012.0260.1。GitHub官方草稿可见性说明见[REST releases](https://docs.github.com/en/rest/releases/releases?apiVersion=latest#list-releases)；“403→成功”是本次具体原生作业事实，非全部token的合同。临时两secret/draft/tag均空；S48失败记录和659B artifact原样保留。

**已验证数值，HDR-41/42。** 重用既有IMG2600 1536×2048冻结scene，按旧版本实际RGB双线性投到4284×5712；另一侧重用S42完整half-P3母版EXR SHA69c553e49f3c70ffbebc6e85d32ad6933fe3582535088dd24f60f59c398c4634，未重算key1或guided。旧float32 LinearThumbnail转half的SHA与S42 GPU锚点2d8ee1596d8f2d1f79a870a288ca398a445883f8499ef9bb9bee8d0fcca6f0a0相同。原legacy曝光4.979845792404184EV/因子31.55607338026331只统一单位，没有重新拟合曝光。仍保留Apple Log，不修改旧scene/冻结模型。

|共同诊断|旧2048双线性+2×2面积约束|原生RGB guided投影|
|---|---:|---:|
|锚点MAE EV|0.03587141095|0.34960619562|
|锚点p99 EV|0.35601522277|3.63355426623|
|锚点max EV|4.01517453362|15.19038894089|
|边缘梯度保留中位比|0.2060544730|0.8136424440|
|边缘gain曲率均值 EV|1.1677671931|0.4286922099|
|边缘gain斜率反转比例|0.1624855017|0.2038192917|
|负RGB分量 / 非有限分量|0 / 0|44 / 0|

同一原SDR全分辨率参考、共同有限正亮度诊断区24317242像素，其中边缘800096、固定抽样梯度50067点。该选择仅用于新诊断，**不修改逆解/33点/承载mask**。更清楚的纹理与更大的锚点误差并存；曲率降低但反转比例增加，不能宣布全部边缘伪像改善或直接替换已冻结基线。原RGB map的中心采样/乘法比值+guided不具有旧2×2面积约束（原AIR/调用链见HDR-14/15），面积守恒是旧工程约束；两种结果也都没有RAW真值。此处只证明GPU half锚点相同，未证明历史float32参考相同，且诊断参考/算术与S42原表不同，新表不覆写历史表。

9张PNG采用同一固定OCIO cg-config-v2.2.0_aces-v1.3_ocio-v2.4 / LinearP3-D65→sRGB Display / ACES1.0 SDR Video，显示尺度13.164076042436493沿用S47，不标定nit。8份预览输入和原件/SDR/legacy/master前后SHA全部相同；密文逐项GPG/SHA验证，本地仅展开contact。它们不是实际HDR屏幕证据。指标artifact12196823572 ZIP SHAeed057a6b471e1f3db1db31c0ee717ea1a59aeaf924df607358e9d50a3529de4、manifest SHAad64dec9de23cbad3510ef7018baf08f3efc4c8e2322499ce9857a46acb964aa；密文预览artifact12196673747 ZIP SHAc042530fe896c90f77130d30adae2056b59256b36b5f40485a3dfa90a55568a3、cipher SHAba43a2654a764ca9757824e4ea0452f3c8c677c2199e22139360d26152990f6d。文件与行号见claims HDR-40～42及repo/research/hdr-native/evidence/s48-s49。仅1张开发照片，未增加5图/2留出验收，A与总验收仍false。


### HDR-S50：公共 offset 的信息损失与原生算术分开

**已验证数值，HDR-43。** source4e3c56c829ac09fe17cb1e7fa20bd1cc5e671af2/run39280458478/26A434/image20261012.0260.1。合成S=0.125、o=0.03125、log范围[-8,8]，目标H1=1.0000000116860974e-7（bits33d6bf95）与H2=1.0219999779792488e-7（bits33db790b）写成相同float32 log=-2.3219234943389893（bitsc0149a65）和归一化纹理0.35487979650497437（bits3eb5b2ce）。源/metadata相同，两个原1e-3目标允许区间不相交；使用精确有理数证书，任意单值重建均有：

`max(error1/d1,error2/d2) >= (H2-H1)/(d1+d2) = 0.0010999983146575687 > 0.001`，其中`di=max(abs(Hi),1e-6)`沿用原定义。

这是**有限输入碰撞**，无需假定fast pow精度或编译重结合行为，信息在float32记录里已经合并；不据此宣布33皮肤点完整consumer域或所有实际照片的全域区间证明。目标网格/分组/首个不交区间的选择规则在取得原生输出前冻结，不拟合硬件结果，不改门槛或mask。

**已验证数值，HDR-44。** 原生CI五档headroom1/1.25/2/4/8的两份公共offset输入纹理与metadata SHA相同，全部输出SHA也相同；h8输出1.0291114449501038e-7。对H1/H2的maxrelative分别0.0029111433264/0.00071114669709，前者失败，尽管maxabs2.9111433264e-9、PSNR170.718728dB。对已存code的double公式，原生h8另有1.90516565718e-9绝对误差；这与记录碰撞是两层不同问题。零offset控制H1/H2使用不同gain code，原生目标maxrelative2.13162820728e-8/1.42108547152e-8，均通过这两个有限输入。此实验**没有图像codec**，不把它归为8-bit Gain Map传输误差；也不把o=.03125例子冒充S47真实o=.0307447053492全部失败点的归因。

证据artifact12200760926 ZIP SHA60c09dafd81a2c9e07f780097d94d05866c4c1dee5e7ab3cc84f885e4c48b5ed，manifest SHAfc9b2758ccc903cc31a4f46382b3e815a7b0f41696b45bfc23eceaac7074147b，所有成员已校验，完整原生日志SHA8e3dc5882dfc2c286d39aa6f040df2e3ba5bf081e81c1675f2e9f8ae67663f96。接口此前持续queued而日志/结果已结束，取消命令返回“已完成”，随后裸run端点已确认completed/success（updated_at=2026-10-19T16:14:48Z）；不猜服务状态矛盾的原因。无secret/release或含人物输入。既有总验收与A阶段仍false。


### HDR-S51：独立显示配方五张原尺寸、两张配方留出闭环；完整目标仍未通过

**已验证数值，HDR-45。** sourceae2f422b8e09878bed18826f83142fb1d2ba983a/run39289319764，26A434/image20261012.0260.1。只在runner依次读取既存S42四份密文（总922251766B），每份完整ZIP/cipher SHA、GPG和EXR成员验证后才处理像素；没有重算key1、Apple Log、guided或任何旧scene。与S47合成3张5712×4284、2张4032×3024。两张留出限于冻结S44/S47独立显示配方，旧scalar/RGB研究曾看过它们，不宣称从未见过的照片。逐项源绑定与联系表布局的逆替换恢复原数学前缀，5份依赖SHA完全相同。

50次原生未编码CI公式对照（5图×2offset×5headroom），maxabs4.7088888806001705e-6、PSNR最低132.82709150641782dB，通过原float maxabs1e-5/PSNR60门槛。45份预览输入、原件/SDR/master前后SHA相同；全5图曝光来自同一固定网格中位数规则，无逐照片手调。

**已验证数值，HDR-46。** 各照片的已定义承载域与全图目标分开：

|照片 / 角色|显示曝光 EV|zero覆盖率|zero原生端点relative|公共offset原生端点relative|公共offset已存logmap relative|
|---|---:|---:|---:|---:|---:|
|IMG_2600 / development|3.718534360|97.7627162%|1.560017074e-06|0.02536738641|0.00252261044|
|IMG_2604 / development|4.353422260|98.0662404%|1.33693813e-06|0.004436711443|0.001148625054|
|IMG_2608 / development|3.676197399|97.3047307%|1.363259322e-06|0.00510207343|0.001221411423|
|IMG_0032 / display-formula-holdout|1.199509741|99.9361097%|1.154897184e-06|6.716883126e-06|5.013617085e-06|
|IMG_0033 / display-formula-holdout|1.475500357|99.7617686%|1.184494621e-06|6.364852222e-06|4.853326042e-06|

zerooffset全部在自己的承载定义域通过，未编码h1全图max0；没有用承载mask替换逆解/33点mask。公共offset全图coverage100%，前三张目标仍未过1e-3，后两张留出端点通过；全部公共offset的未编码h1 maxabs在2.98023223877e-8～5.96046447754e-8之间，仍非0。**没有新HEIF/ISO编码载体**，源文件未动不代替“新载体完整ImageIO SDR max0”。未编码公式通过也不代替新编码Gain Map的目标误差通过。

**假设/工程选择，HDR-47。** 独立显示渲染仍是`H=kM*8/(8+max(Y(kM),0))`，M为原母版候选；显示k与8不标定场景曝光/nit，不把它们当j提亮EV。全5图正Y域RGB/Y色度差最大3.34155283e-7只是float32诊断。GTM、LTM、人物/皮肤及纹理逆向原有边界继续独立保留：五图验证的是此显示/未编码公式，**不是对拍摄端未知生产曲线或scene-referred母版的五图物理认证**。33点C01-C05未认证、同帧j/Studio统计、RAW2679/2408与真实HDR屏幕项目不因本轮通过而改变。

预览固定OCIO cg-config-v2.2.0_aces-v1.3_ocio-v2.4 / LinearP3-D65→sRGB Display / ACES1.0 SDR Video /0EV；使用原始像素网格，未按EXIF旋转，全部面板方向相同。只加密上传4张联系表（每张含SDR/M/独立H及5档原生headroom），不是实际HDR屏幕照片。指标artifact12205456068 ZIP SHAff88e6f6ab2fc2c6739402e3766560a0a5fe348df9285c340b86ec8fcefdda6a、manifest SHA41269ca41258e94956b22451f9361a488e8b13bd9f3e6f37d0fd6d654d4afe88；预览artifact12204689131 ZIP SHA4c15f1b07fdbc685f4cb40f1048d7ae00d8d4218713b2b12647b3682adeb77e2、cipher SHAaec13a3f2f5d40976212618f2667f9b0a4907354ab45fe345f49df2f5f95aa01，GPG与全部成员SHA已验证。四项session secret已删除；未创建release、未传归档私钥、未改其他研究任务的分支/run。串行限制按本HDR任务执行，前文全仓库等待要求是本代理过严的调度解释，此处更正，科学门槛无变化。

只读验证器`repo/research/hdr-native/validate_display_s51.py`输出五图协议完成与原float公式通过；`acceptance_complete=false`、`A_phase_complete=false`。旧root validate.py、冻结模型、原件与历史证据未改；只有HDR显示公式的五图/2留出子项闭环。


### HDR-S52：分别设置两端 offset 能改善 HDR 端点，未保持 h1 身份

**已验证数值，HDR-48/49。** source1e2924bd17cc47e45b1c8a6753be77e288cbd004/run39293130622/26A434/image20261012.0260.1。只做四组合成常量×五档headroom，复用原生CI测试入口，没有重算任何真实照片。固定两端offset模型的最大abs5.756476469109817e-9，两个假定随headroom混合offset的候选差约0.0312。所测行为符合`(S+B)*2^(wL)-A`。这也与[Android Ultra HDR参考显示公式](https://developer.android.com/media/platform/hdr-image-format#use-the-gain-map-to-create-the-adapted-hdr-rendition)中的独立输入/输出offset结构相容；Android文档不作为Apple API实现或ISO容器合规证明。

令w=0，实数模型为`S+B-A`，故B=A是这一模型保持h1身份的必要条件；有限精度下仍可能有加减消减误差（S47/S51）。S52降低A后，全部h8端点通过原门槛，全部h1身份失败：

|合成案例|h1原SDR差|h8目标relative|h8目标通过|
|---|---:|---:|---|
|positive-alt0|0.03125|3.5527136788e-08|是|
|positive-small-alt|0.0312347412109375|1.44240175359e-06|是|
|negative-source|0.0312347412109375|5.58793557259e-07|是|
|negative-target|0.031219482421875|1.72803997702e-06|是|

因此不把不等offset当完整解决方案，不改五图目标或mask，不继续对既有照片作无目的精度拟合。本实验的未编码CI h1身份与“新容器primary decoded SDR max0”是不同检查；没有生成新容器，后者仍未认证。全部结论只覆盖有限合成输入，不充当33点完整consumer域的证明。原GTM/LTM/语义逆向边界不因承载层参数检查而改变。

artifact12207396048 ZIP SHAb34024a807f1d71516a2861de6c0e2badb7414d6c4925ab501499c5713c69d31、manifest SHA5a37390e3a25d3a214a0cd1ebb94b6a7cada724ef1bc69856b0d210a1c03755a，全部成员已验证；无secret/release/真实照片输入，retention1天。A阶段与总验收仍false。

**存储交付待许可。** 五张完整S42母版密文尚未全部本地归档。当前提出更小方案：流式读取IMG0032既存153946146B密文ZIP，仅落地27791119B的原母版EXR（SHA9b392ea7cf996d1cbc70fbf82911b3c04e51562653010e7a78ee4a7a8129b012），不保存整包。写入预计使本阶段累计约124MB，已询问将用户100MB上限改125MB，尚未把未答复当许可；旧300MB整包方案由此更小选项替代。准备好的`stream_verified_master.py`默认仍按100MB检查，只有显式新许可才能提高cap。候选原字节在runner已完整GPG/EXR SHA验证；本机脚本仅字节流校验/复制，不解码图像。该EXR仍是相对线性P3候选，物理RAW及未认证global/local/semantic边界继续保留。


S48–S52 科学检查完成：五张原尺寸/两张显示配方留出/50次原生float公式通过；原scene/语义逆解与完整HDR目标/编码仍未通过，A阶段与acceptance_complete仍false。原33点mask及C01-C05、旧NumPy/half失败不改，不继续旧bit-exact拟合。完整EXR的125MB小归档许可待显式答复，当前100MB累计上限不重置；本地只保留证据和密文预览，未假称完整母版落地。源码将保存在research/vm-native-20261018，随后仅清理本阶段自建临时分支，master/原件/旧工作流不动。
