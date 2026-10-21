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


S48–S52收尾完成：5条自建临时远端/本地分支在远端源码保留、PR及全部ref审查后清理；8项本阶段secret与2个draft/tag均不存在，5个自有run均终止。既有PR#1和其他研究任务未操作。原件/冻结7文件SHA与原始171claims/文档历史前缀保留；5个新增workflow的8次upload均retention1天。125MB单EXR许可仍待显式答复，当前100MB累计上限有效，未写完整EXR。A阶段和总验收false，goal active。


### HDR-S53–S54：相机曲线分组、记录逆区间和 GTC 的信息边界

**已验证静态（HDR-50）。** 本节仅追 24A446 / iPhone12,1 参考代码，未把它当成 IMG_2810 的匹配生产实现。CameraColorProcessing UUID `0A211E15-50CA-373B-AD9A-F9E3283C68F4` / SHA `974ffb2895cae06e26e63bd77ab4891f5401d4789449f7a0080d377553b2426e`；CMImaging UUID `0A9BC064-A4BC-330E-861A-C70A637B14B3` / SHA `b8f3c04f3f9ee000c328357156b38aecc3ca06d5292e47421966094a58fa1832`。510条摘录指令逐条与只读cache核对，16条literal引用及3条global-tone GOT绑定另行核对；缓存只读，size/mtime未变，不声称对整份cache重做内容SHA。证据为 `evidence/s53/source-audit.json`、`curve-record-fixture.json`、`producer-curve-export-static.txt`（保留原行号/地址）。

`LTMCurvesComputeV2.compute` 的三处 writer 调用 `0x256b86e1c/e84/eec` 选择 type1/2/3；`LTMMetadataWriterV2.create...` 在 `0x256b8c9e8` 选择 type0。writer `0x256b8ce70–cf80` 的控制流与实际CFString/GOT指针给出：

|type|局部表键|global LTM键|global tone键|
|---:|---|---|---|
|0|LTMLookUpTables|GlobalLTMLookUpTable|GlobalToneCurveLookUpTable|
|1|LTMLookUpTables_HLG|GlobalLTMLookUpTable_HLG|GlobalToneCurveLookUpTable_HLG|
|2|LTMLookUpTablesWithoutFaceBoost|GlobalLTMLookUpTableWithoutFaceBoost|GlobalToneCurveLookUpTableWithoutFaceBoost|
|3|LTMLookUpTables_HLGWithoutFaceBoost|GlobalLTMLookUpTable_HLGWithoutFaceBoost|GlobalToneCurveLookUpTable_HLGWithoutFaceBoost|

两类global数据分别来自computeOutput+0x18504 / +0x18908，均是header=257、257个u16节点、总516B；局部grid另有格式，本次decoder不接受它。原WithoutFaceBoost分支不仅写j=1（driver+0x24），还写+0x554和+0x558（`0x256b86e30–e3c/e98–ea4`），故不能把整个API分支叫作“仅j干预”，更不能叫“只逆local”。全局/局部的实际应用角色仍须沿绑定判定，不能依据GlobalLTM字段名分类。

**已验证数值（HDR-51/52），条件为binary32、RN-even、FPCR=0。** 新 `producer_curve_record_s54.py` 对记录节点保留前像区间，依据原标量链：

```
Q(x) = floor(RN32(FMAXNM(FMINNM(x,1),0) * 65535))
```

正数float32位序、正数乘法的单调性、floor和clamp给出每个u16码的离散前像；用整数位序二分定位边界。S54对全部65,535个跳变的前驱/首点，共131,070个探针（510份记录，含两类global输出）执行未改的 `0x256b8cc68–cce4` ARM指令，u16差异0。不是穷举完整consumer输入，也没有把此子算子证明升级为33点紧外包络。示例：code32767对应 `[0.49999237060546875,0.50000762939453125)` 的有限float32值；code0和65535分别包含clamp端的整个有限域尾部，不能返回唯一恢复值，更不能给出物理像素EV界。

S53 run39300758676/source d54796021c2155bb329140e0e44f63287ac7e211 失败于非有限断言：初稿把sNaN/qNaN混为同一路；原失败源码/日志保留，不计完整通过。S54 run39301402089/source e7b1edf81675fd4b1bda93f20b25a5dfa949ec9e 增加逐指令检查点及原生ARM asm对照，12例全部一致。qNaN经FMINNM选择1→Q=65535；sNaN先quiet，再由FMAXNM选择0→Q=0，IOC=1。原生测试开始/强制FPCR均0，退出恢复浮点状态。这与[Arm官方FMINNM合同](https://documentation-service.arm.com/static/67e40f3398aa3c3b6eea6a85)一致。这里只认证这个CPU指令链，不推断Metal clamp/fast math或实际相机FPCR；全consumer的非有限路径义务保持。

**已验证静态与数值（HDR-53），仅GTC读取子路径。** iOS `CMISmartStylePixelBufferRendererV1._createGlobalToneCurveTexture` 在 `0x1d476c2d4–2f4` 从输入字典取固定 `GlobalToneCurveLookUpTable`；header257分支在 `0x1d476c31c/370–3f4` 读取u16 words1..256，除以word256，再按输入CV transfer/primaries选择解码并存half。writer最后一个节点word257未被这一分支读取，读取端也未在该函数里自动选HLG/WithoutFaceBoost键；外围调用者是否换绑generic键仍缺证据。S54构造两份整数幅度相差2倍的记录，比值阶段完全相同；只改word257亦不改变此阶段。它说明“只拿归一化GTC纹理”不足以恢复记录幅度/被省略节点；完整元数据是否另存尺度必须继续查。这里没有捕获原生iOS纹理，没有证明文件key3的序列化绑定，也没有改变已冻结的key3 `inverse_sRGB(u16[1..256]/65535)` 样张结论。

**local/语义边界（假设 / 待实机，HDR-54）。** 四组相机曲线与Styles文件c/d、key3及最终ISP应用的同帧连接尚未证明；对c/d作除法、把UI tone改负、或者把WithoutFaceBoost当纯local逆，均不能升级为物理反演。新 `evidence/s54/producer-paired-capture-plan.json` 给出参考writer入口/三处NSData复制/GTC读取拦截点、原float节点与打包记录、FPCR/FPSR和四组键的捕获要求。先匹配真实设备build/UUID并重新核对布局；**不把参考绝对地址移植到IMG_2810**。随后只j反事实与API WithoutFaceBoost分开，重放G_A/L_A、G_B/L_A、G_A/L_B、G_B/L_B，检查交互和每步原门槛。j的β=.1953125仍仅是内部权重界；没有同帧N、B/T/V、直方图、allocateTone约束/knots及应用域，不能变成样张EV。RAW、Studio原统计和实际HDR观看按原待实机清单保留。

两个run均在26A434/image20261012.0260.1执行；主要是iOS原指令的静态重放，原生部分仅为macOS ARM标量指令，不是相机运行。S53 artifact12211821267（1176B）ZIP SHA `d1563d63c48a5f8c9c2183bb1b126f25be4d72988b76d048912d384767621db1`；S54 artifact12211902213（5196B）ZIP SHA `ff3c502e3f150088cb87e4530cfd634b6211f09cf0ab843cd654d5b2be35662e`，manifest SHA `ec26338865f2b663f812982f0b1c0991a8eff9dbd500fb18e876085e461eded9`。全部成员校验且只含文本；0张新照片、无secret/release，retention1天。独立HDR渲染/承载与scene物理恢复继续分别验收，旧NumPy/half不追拟合，1e-3/原mask不变；**A_phase_complete=false，acceptance_complete=false，goal active**。100MB累计上限不重置，125MB单EXR许可仍待答复，未写完整EXR。

S54受体补证（已验证静态）：`0x256b86dac–db4`读取GOT槽0x271529a50；只读解码到class0x27994a090、class_ro0x27f060558及name="LTMMetadataWriterV2"。见`evidence/s54/writer-class-binding.json`，从而补上selector调用的具体静态receiver；没有声称捕获真实运行时对象或IMG_2810同帧路径。

S53–S54收尾完成：两个源commit已保存在推送的research/vm-native-20261018@98d8cd675f3bcc89c663728b4ebaccaf41115620；全部PR/远端ref核查后仅删除两条自建临时分支，本轮无secret/release。原master与旧208条claims/7个原件冻结SHA保持，自己的临时脚本校验归档后清理。保守累计写入上界96,843,500B（含500KB后续审计清理预留），仍受100MB总额约束，根剩余>4GB；125MB许可待答复，未写完整EXR。A与acceptance_complete继续false，目标active。详见transport-cleanup-s53-s54和integrity-review-s53-s54。


### SEMANTIC-20261018 / HDR-S55–S59：标量 c/d 的生成约束与 global 归一化

**已验证静态（HDR-55/57，macOS 26A434）。** 新证据来自 CMImaging UUID `3CCD434E-B1E0-3F14-8EF6-E29D58379BE8`、metallib SHA `16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11`。`evidence/s55/local-histogram-source.ll` SHA `e5b8b8d09dd04ca5f27c9f1a3a32d485cc26c690c4e28f365d574190cb003cac`；新增 AIR0/1 文本由 S55 导出，分别对应 `imageReduction` / `updateBaseGainWithStats`，不是新的相机执行。**此处拆的是 macOS 重建/编辑端能生成的标量 light maps；文件 c/d 的拍摄端序列化与最终 ISP 应用尚未同帧绑定。** iOS 24A446 / iPhone12,1 仍只是参考，不能代替 IMG_2810 的匹配实现。

在 SRL-before-stats=false 的已测分支中，令 A 为主图 transfer 解码、可选 VE 和 half CCM 后的 RGB；X 为线性缩略图 half CCM 后乘 half(baseGain)；E 为 half(baselineExposure)。T 是每通道 `GTC(min(half(E·X),1))`。统计量 M_A 为 ltmBasic.max；M_T 为 `linBasic.max·baseGain` 经 float→half、乘 half(E)、clamp1、同一 GTC 取样后的 half 标量。这里的 min/max 是 RGB 通道极值，avg 源于每像素 half RGB 等权均值和 ROI/计数的层级 half 归约，**不是 nits，也不能把它直接当场景亮度**（`evidence/s57/imageReduction.ll:100`、`:242`）。

`calculateLocalHistogramStats_all` 对 A/M_A、X/half(linMax·baseGain)、T/M_T 分别构造 histogram0、5、7。每个样本先 half 等权 dot，再 half×256、round、转整型和 clamp[0,255]（AIR:352–382）；选累计计数严格越过 floor(0.5N) 的桶。写槽17 lightMapTexture 使用 hist0 的 p50；写槽18 linearLightMapTexture 使用 **hist7** 的 p50，**不是 hist5 或 person 的 hist1**（AIR:693–731、:1117）。所以第二张图的生成已经包含 GTC，不能先反 GTC 后把原 c/d 当作无关的局部增益。SRL=false 时这两个未加权直方图的原子加数为1，person/skin 另有加权桶；不能把这一结论外推 SRL=true 或整个 consumer 的语义不变性。

两个标量编码尾部的冻结顺序参考为：

```
p = RN32(k * float32_bits(0x3b808081)), k in 0..255
t = half(RN32(RN32(RN32(M * a) * p) + b))
code = half(RN32(RN32(float32(t) + 1.2f) * 0.29412f))
a = float32_bits(0x401c3d8f), b = float32_bits(0xbf87ede0)
```

它保留 half 中间量与源常数，不是拟合的 log Gain Map。在正常非空 ROI、正有限 M 的 k=0 情况，输出为 `0.040740966796875`（halfbits10551）。`lightmap_model_s55.py:16` 实现条件编码和全部256桶逆集合；它输入的 p50 来自原生或声明的桶，不独立预测完整图像的统计。空 ROI 的 sentinel、非有限/负输入及完整 fast-math 合同未认证。

**已验证数值（HDR-56）。** S55 因 prepare mask2 没有原 stats PSO 而失败：原编译支路 `0x23336dc78` 检查 bit0，CFString `0x27b947a88` 绑定该 histogram kernel，保存到 self+0x4d8（`evidence/s56/prepare-mask-source.txt`）。S56 改为有静态依据的 mask1，直接取原 host-retained PSO；269个合成控制的 c/d 编码尾部全部 half 逐位一致，max abs0、非有限0，输入/外部上下文 SHA 均不变。它仍是 transfer0/identity CCM/SRLfalse 的手工 dispatch，不是完整原 host 或相机。S56 后续失败于临时会话密钥解析：完整 `9.2:HEX` 被旧正则截成 `2:HEX`，未得到真实图数值结论。S57 以完整前缀修正；空 keyring 正确解密、SHA/size 均匹配，篡改副本非零退出。始终同时检查返回码、状态和明文 SHA，不能仅凭 DECRYPTION_OKAY；未上传私有 archive key。

**global 单列（HDR-57/58）。** `updateBaseGainWithStats` 原 AIR:20–33、buffer indices1/3、params+24/+28 和 stats+10636/+10624 给出：`g = fast_float(avg_main / (E * avg_linear))`，只写 g。它是两路已处理图的统计对齐，不能自动解释为物理曝光逆。S57 的原 host PSO 对7个正有限控制，与有序 float32 参考 max abs=`1.9073486328125e-6`、max relative=`1.0596380170569932e-7`；除 g 四字节外参数与 stats 未变。另5个边界/非正诊断含当前 VM 的 NaN/Inf 观测，不构成非有限合同；这里只通过标量控制的 abs 子门槛，没有图像 PSNR 或全管线通过结论。

**真实 c/d 与缺失尺度（已验证数值，HDR-59/60/61）。** S57 解密读取 IMG_2600/2604/2608 的旧 consumer 捕获：六张32×32 half 图存在，但两项生成统计 max 都是0。不能拿这份零缓冲冒充拍摄时统计。S58 转而在冻结有序参考中完整枚举31,743个正有限 half 尺度 M、每个256桶；六张图分别只有一个 M 能同时解释全部1,024码。每组的3968B位集及摘要保留于 `evidence/s58/conditional-normalizers.json`，不是对原生所有 fast 输入的认证。

|样张|c 的条件候选 M|d 的条件候选 M|各图兼容码|
|---|---:|---:|---:|
|IMG_2600|1.0078125|1|1024/1024|
|IMG_2604|0.94677734375|0.7666015625|1024/1024|
|IMG_2608|0.97998046875|0.927734375|1024/1024|

S59 随后在这六个候选尺度上用**原 PSO**运行768个新的合成控制，逐图实测全部256桶；参考尾部1,536个 half 分量差异0，原图、线性图、GTC、person/skin、params/stats SHA 不变。六个原生代码本对真实6,144个辅助图样本码全部兼容，并各自只有一个桶，未覆盖0、桶歧义0（`evidence/s59/native-compatibility.json`）。尺度由同一批码推断，**不是留出验证**；原生只确认这六个尺度的兼容性，未把其余全部尺度都执行，所以“尺度唯一”仍限有序参考域。没有把候选尺度回填零 stats 并称为实测。

**信息界与分离策略（runner / 待实机，HDR-62）。** 唯一桶不是唯一场景像素：256桶、局部中位数、GTC clamp、half 和空间汇总会丢失分布/空间/RGB 信息；guided filter 也不能恢复被汇总掉的 RAW 细节。当前没有从代码本推出逐像素 scene EV 界。global 曲线/曝光/全局色彩的逆、local 的 c/d/guides/局部分支的逆、人物皮肤与 Studio 处理继续分别保存上下文、mask、区间和结果。改变 GTC 后重新求统计/guide 会同时改变 local；把 UI tone 改负、直接 d/c 或简单抵消 baseGain 不能充当物理 local 逆。

runner 还能推进：同一原图上捕获真正计算 stats 的 host 分支、ROI/grid/CCM/SRL 与 scalar17/18全图，核对候选 M、文件字段与原生输出的实际绑定；继续审计33皮肤点 C01–C05 的原 PSO 全域合同。实机仍需匹配 IMG_2810 build/UUID 的同帧 j-only 与实际 WithoutFaceBoost 曲线、N、B/T/V、人脸直方图、allocateTone 约束和应用域，以及 IMG_2679/IMG_2408 RAW/Studio 原统计/实际 HDR 屏幕。β=.1953125 仍不是像素 EV。

本轮0张新照片像素渲染，仅3组真实辅助元数据；没有替代 ≥5张完整前向/两张冻结后留出、完整原生往返或编码后 SDR max0 验收。LinearThumbnail 保持 Apple Log，原件/冻结模型和33点 mask不改，旧 NumPy/half 拟合不恢复，原1e-3门槛不放宽。**A_phase_complete=false，acceptance_complete=false，goal active。** 新记录加到根 errors.csv 和 `evidence/s59/errors-delta.csv`；旧公开 errors.csv 保持历史原样。

五次 run 的 source commit、artifact、完整 SHA 和 image 见 `evidence/s59/archive-provenance.json` / runs.md，均26A434/image20261012.0260.1，artifact retention1天且全已落地。S55/S56 的失败归档保留，S59首个0字节下载失败也保留收据，未重跑计算。临时 secret、draft/tag、五条临时分支在源码推送 keeper 后经 PR/ref 审查清理；所有源码 commit 仍可达，master 未动。100MB累计预算不重置，125MB完整EXR许可仍待显式答复，未写完整EXR。


### SEMANTIC-20261018 / HDR-S60–S64：完整统计 host、global 分支条件与 c/d 不匹配

**已验证静态，HDR-63（26A434）。** CMImaging UUID `3CCD434E-B1E0-3F14-8EF6-E29D58379BE8`，沿用S55–S59源SHA。`process`在0x23336aa8c/aa98读取variant与常量、0x23336abbc–abc8比较指针并把bool传给优化stub0x23804cdf0；原生ADRP+ADD解码确认selector为`_runImageReductionAndUpdateBaseGain:`（ABI i20@0:8B16）。0x23336bd9c在false时跳过update PSO。metadata:28444把0x270933900列为`(__DATA_CONST,__const) external _CMISmartStyleTuningParameterVariant_DigitalFlash`，不是GOT；旧evidence/s60/source-provenance.json的reference_GOT误名保留，新analysis.json勘误。S57均值对齐公式因此有分支条件，不是通用曝光逆，更不是物理EV标定。

**已验证数值，HDR-64/65。** S62实际失败于`_populateStaticRenderParametersFromTuning:inputStatisticsByStatsKey:`（0x23336e8ec）返回−12780，inputStyle=nil、0 dispatch。S63调用原void helper `_checkAndCreateInputStyle`先创建默认CMISmartStyleV1；没有拟合tone/color/gain。statsComputationRect使用0x23336c224–c24c给出的归一化全幅(0,0,1,1)，各输入mapped rect仍按各纹理尺寸。未按猜测CGRect调用私有SSRRenderROI*参数。observer仅按运行时ABI记录，原PSO未替换；VM原有residency-set兼容开关继续显式记录。

S63在五张原始像素网格（含两张本新stats算子的冻结后留出0032/33；它们曾参加其他研究）执行完整原host，每张9 dispatch：5×imageReduction、localHistogram、globalHistogram、sumPersonAndSkinCounts、globalStats。全部输入SHA不变，actual/supplied queue一致，SRL=0；DefaultParameters分支bool=false，没有updateBaseGain PSO，gain/曝光逐值等于输入元数据。捕获10640B stats、672B params、320B颜色转换、176B ROI及两张32×32 half图，空间数据仅加密保存。**这是逆key1/P3/Apple Log重建域的默认style上下文，不是匹配原相机style或拍摄生产路径。**

**已验证数值，HDR-66；local原门槛失败。** 生成c/d与文件原图共10240个half码中9279不同，最大绝对差0.707275390625：

|样张|c不同码/1024|c max abs|d不同码/1024|d max abs|
|---|---:|---:|---:|---:|
|IMG_0032|1020|0.51385498046875|984|0.61376953125|
|IMG_0033|1016|0.56219482421875|1016|0.6783447265625|
|IMG_2600|977|0.5936279296875|718|0.707275390625|
|IMG_2604|1014|0.311279296875|914|0.19732666015625|
|IMG_2608|994|0.49993896484375|626|0.501861572265625|

不能把这次“host成功运行”当作完整前向/拍摄端local逆已通过。S58条件M和S59桶兼容性仍保留原条件；不得回填候选M来掩盖这里的实测差异。

**已验证数值，HDR-67。** S64复用S63小型密文捕获，0次照片/统计原生重算。三张与39055408205历史consumer的颜色管理320B逐字节相同（transfer原枚举0/0/3/0、CCM identity、VE byte0，语义枚举名未据字段猜定）。固定8种旋转/翻转诊断，开发3图的联合MAE之和identity=0.12457743287086487、次小flip_x=0.5381505787372589；先冻结identity再评估0032/33，仍非half一致。权威坐标、原mask和门槛完全不变。这只排除了所测D4候选改善开发集总体误差、及所比三图320B颜色载荷差异；不能排除采样/ROI或真正相机输入域差异，不能升级成相机绑定证明。

**失败与归档边界。** S60原host −12780/0 dispatch之后输出GPG失败：同一setup步骤只写GITHUB_ENV，公钥导入了另一个homedir；其私有原始失败捕获未保住，只有公开摘要/日志，不能伪称完整落地。S61先修显式keyring并做传输preflight，但在照片前因嵌套main宏重定义编译失败。S62修入口/归一化ROI、保持原失败源码，按checkpoint确定nil style；S63补原helper后通过上述host执行。S62/S63密文、解密返回码/状态/压缩明文及全部成员SHA均验证；S64只发布聚合文本。五个run source/branch/artifact/ZIP/manifest SHA见evidence/s64/archive-provenance.json，均26A434/image20261012.0260.1、retention1天，完整ZIP已落地。S63 ZIP83390B、S64 ZIP6376B，ZIP内密文不重复解包落盘。

**可交给macOS runner，HDR-68。** 下一步沿实际生产/编辑调用者查输入域和文件c/d序列化绑定，固定已有统计/guide/GTC/matte，先解释实测差异，再分别验证global与local反事实。已有三图颜色载荷或八种D4结果不再无理由重复；33皮肤点全域C01–C05、完整原生往返与编码后ImageIO SDR max0继续未认证。人物/皮肤、Studio与GTM/LTM继续分别输出；旧NumPy/BG/atan2 half拟合不恢复。

**待实机解决。** 匹配IMG_2810 build/UUID的同帧j-only和WithoutFaceBoost、N、B/T/V、人脸直方图、allocateTone约束/knots与应用域仍按s54捕获计划；β=0.1953125不是像素EV。RAW2679/2408、Studio原统计和真实HDR headroom观看仍待实机。原33点mask、half/float/PSNR/1e-3门槛不改，LinearThumbnail仍Apple Log；这轮无新预览，旧固定ACES预览不变。**A_phase_complete=false，acceptance_complete=false，goal active。** 原100MB累计限制不重置，125MB完整EXR许可未收到，不写完整EXR。


S60–S64收尾：源码/指标先普通push至research/vm-native-20261018@689034a284bc9fa714667872d9473baf161ad523，再经全部PR/ref与run终态核查，删除本轮5条临时分支和HDR_S64_S63_SESSION；无release增删，原master/现有PR/8份原件冻结SHA不变。见evidence/s64/closure.json及本地transport-cleanup-s60-s64.json。累计100MB许可不重置；旧Git预算按未压缩对象上界记账，本轮以可核对的最终loose对象实存字节调账，原账/全部历史归档保留，未扩大许可。A与总验收仍false。


### SEMANTIC-20261018 / HDR-S65–S66：统计桶差异与独立 headroom 逆换算

**已验证数值，HDR-69/70（26A434）。** S65复用S63的五张小型捕获与S56/S59原生码表，只对新实测尺度M=.9912109375补256个合成原PSO控制；参考编码尾部half差0。五张c图共5120码在各自实测M的256桶码表中都有唯一桶前像，无遗漏/歧义。这只是编码桶，不是唯一RGB、场景值或33点全域证书，照片像素/统计重算0次。

在前三张文件M仍限S58有序参考唯一、S59原生兼容的条件下，分别解码文件桶k_f与重算桶k_n。令C_M(k)为观测原生码表：

```
C_Mn(kn)-C_Mf(kf)
 = [C_Mn(kn)-C_Mf(kn)] + [C_Mf(kn)-C_Mf(kf)]
 = [C_Mn(kn)-C_Mn(kf)] + [C_Mn(kf)-C_Mf(kf)]
```

两种顺序的加法恒等式残差均0；它们的项有交互，不能唯一归因到物理GTM/LTM。只把M改为文件条件候选、保留重算桶，仍有如下差异：

|样张|不同桶/1024|桶差MAE|桶差最大值|仅改M后的码max abs|
|---|---:|---:|---:|---:|
|IMG_2600|914|14.62011719|211|0.5989990234375|
|IMG_2604|977|9.00683594|109|0.29052734375|
|IMG_2608|883|7.83105469|179|0.49407958984375|

交互max abs分别.00494384765625/.016357421875/.0054931640625（map码单位，不是EV）。这排除了“该条件下只差一个normalizer”的解释；不能据此断定差异全由某一个物理局部算子造成。0032/33只查重算c码前像，未为它们另拟合文件M、未假称新留出逆解通过；d的桶分解没有执行。所有原c/d、GTC、guide和逆模型未改，诊断反事实未安装进scene路径。

**已验证静态/数值，HDR-71/72。** 原CPU helper在0x2333c8994/0x2333c89fc调用castType（优化stub0x23804d660），比较外部LongGray常量槽0x270933880；仅命中该指针时处理HDR headroom比值r：

```
forward(r) = RN32(pow(double(RN32(r)), 0.644))
inverse(r) = RN32(pow(double(RN32(r)), 1.5527950310559007))
```

原double常数分别位于0x233559bf8/c00，bits3fe49ba5e353f7cf/3ff8d83f9a3c6c20；其他cast分支identity。S66核对原IMP和f28@0:8@16f24 ABI，在Standard/LongGray、tone−1/0/+1与r=0,.25,.5,1,1.25,2,4,8,16,64共60例中，正/逆模型abs0，native往返max abs4.76837158203125e-7、正r max relative5.960464477539063e-8；所测tone不改变这两个helper输出，四个style字段不变。这里是CPU标量控制，没有图像PSNR、Metal像素或完整HDR/scene门槛通过的含义。isHDRGainMapHeadroomAdjusted:在0x2333c8a64只返回0，不能充当可靠的应用状态识别器。

新global_headroom_s66.py按原常数/float→double→float顺序实现这对标量函数；实际还原入口要求显式已识别的applied_branch，未知状态拒绝执行。**它不逆GTC、RGB曝光、local、语义或j；不能因函数名而把它用于所有照片。** iOS24A446/iPhone12,1参考CMI UUID0A9BC064-A4BC-330E-861A-C70A637B14B3的同两入口0x1d476e878/e8e0及flag0x1d473bacc，54条指令与现存Mach-O、只读cache逐条一致，常数相同；这是参考版本，不是IMG2810匹配相机实现。

LC_SYMTAB→常量槽→CFString字节核对了参考短键c/d、b=SubjectRelightingCurveParameter、j=FaceBasedGlobalExposureBoostRatio、k=HDRGainMapHeadRoomAdjustmentEnabled、l=OriginalInsteadOfReversibility。IMG2810原plist记录k=false；该观测不证明原生helper曾/未被调用，不能据此自动施加上述逆。j的β=.1953125仍仅内部权重界，仍没有新的像素EV界。常量键的命名绑定也不等于c/d生产或写文件调用链已绑定。

**已验证静态，输入角色。** S66运行时ivars证实主图/普通主图thumbnail/LinearThumbnail纹理分别在self+20/+28/+30（十六进制）。process0x23336abd0–abe0把+20/+30传给原histogram selector；reduction也用这两路。另一个_processLTMGainMap分支0x2334d50d8–50fc可选+28、缺失回退+20，绑定texture0，+30绑定texture1。普通thumbnail和线性锚点不是同一输入；这段绑定不能证明相机实际选择及c/d序列化来源。原source、运行时selector字节、地址与全部SHA见evidence/s66下审计文件。

**可交给runner，HDR-73。** 继续追生产输入域/ROI/统计到c/d的写文件调用者，以及headroom helper实际调用者与k字段合同；先证明实际分支再应用分离逆换算。33点C01–C05全域边界、完整native往返、编码后ImageIO SDR max0保持未认证。**待实机：** 匹配IMG2810同帧j/WithoutFaceBoost/N/B/T/V/face hist/allocateTone/应用域、Studio原统计、RAW2679/2408与真实HDR屏幕，沿用s54捕获清单。

S65 run39329429383/source8053c0baa5aebf95afa80c168c0ba3677c9ca928/artifact12222729900；S66 run39330883147/source5b7131f9e0d5b0528bcd2375cc6370e7282d9f65/artifact12223619922，均26A434/image20261012.0260.1、retention1天，全部ZIP已逐成员校验落地。完整SHA见archive-provenance.json。S65复用输入密文且临时secret已清；S66无人物输入/secret/release。无新预览，旧固定ACES不变；Apple Log、原件/冻结文件、33点mask与half/float/1e-3门槛不改。**A_phase_complete=false，acceptance_complete=false，goal active。** 根REPORT/claims/errors/NATIVE_TODO/runs/REPRODUCE全部追加；公开aux文档增量见evidence/s66/reproduce-and-todo.md，历史CSV及aux文档保留。


### SEMANTIC-20261018：S67–S69 统计域与原封装绑定

**已验证静态/数值**：S67原globalHistogram使用固定32×32数组，globalStats以ROI面积归一化。恒灰1024×768的计数守恒、P50=.25；5712×4284与4032×3024的累计质量仅.221202/.323003，P50=0。冻结的1024-samples/cell模型仍只有2/3通过；按实际32×24/32×32线程组修正的模型三例吻合，仍为有条件数值模型。不能据S63异常全局分位数拟合拍摄端逆曲线；S65固定normalizer/桶码表的条件事实保留。S67必要原始AIR/统计已存选取tar.xz（非完整原ZIP），全部29原成员在内存校验。详见research/hdr-native/S67.json与归档内selection-provenance。

S68–S69原生CPU检查：prepareToProcess:的实际ABI为i20@0:8I16；原PSO maxThreads=1024、threadExecutionWidth=32，设备Apple Paravirtual device/Family4。第一次因signed参数ABI检查失败；随后两次漏绑输出，ROI检查5，已由原cold2断言“输入/输出交集非空”定位；补独立同尺寸输出后，两个尺寸原检查均0（run39341678257/artifact12228712359，26A434/image20261012.0260.1）。成功job仅代表诊断完成，前面失败均保留。

**已验证数值，仅CPU绑定**：封装保留原主图5712×4284、普通thumb512×384、linear1024×768，没有自动降统计输入尺寸。zero-crop默认matte比例为RN32(1/matteWidth)、RN32(1/matteHeight)；主图/linear采用RN32(1/mainWidth)、RN32(1/mainHeight)。实际matte配准须再验证crop/ROI，不能把默认比例当相机合同。style-engine中间尺寸usecase0–9为256×192、1024×768、256×192、1024×768、768×1024、768×1024、192×256、256²、256×192、256²；与LTM统计源等同仍属假设，未采用。

**已验证静态**：原线程组公式Tx=min(ceil(renderW/32),TEW)，Ty=min(ceil(renderH/32),floor(maxThreads/Tx))；组数固定32×32。新stats_geometry_s69.py只核对这一整数几何，原始调用者/采样域及像素误差分别待证，未改冻结模型、mask或阈值。源地址、原AIR行号、4次run/artifact/SHA及原始JSON见research/hdr-native/evidence/s68-s69/。

**可交给macOS runner**：下一步以阶跃person/skin matte只干预目标crop，抓原_encodeRenderRegionForStats和localHistogram计数；继续原调用者统计源与尺寸绑定，及33点全域区间/完整原生往返/编码SDR max0。**待实机**：匹配IMG2810的同帧j/WithoutFaceBoost四组曲线、N/B/T/V、face hist、allocateTone及应用域；RAW2679/2408、原Studio统计与实际HDR观看沿用原方案。没有新增物理EV或照片预览结论；GTM/LTM/语义独立，LinearThumbnail仍Apple Log，A与acceptance_complete继续false。

资源许可：用户于2026-10-20明确批准125MB累计写入上限（文本/小型密文），旧100MB账不改写、根分区仍至少4GB空闲；完整EXR许可另列，>1GB下载仍需询问。


### SEMANTIC-20261018：S70–S71 原 matte crop 与统计配准

**已验证静态（HDR-79）**：26A434原 `_calculateROIShift`（0x2333bcf98–bff0）对每轴计算 `RN32((cropExtent/mainExtent)/maskExtent)`，mapped origin为负cropOrigin；原 `_encodeRenderRegionForStats:`（0x23336c654）在零原点全画布时给出 `bias=RN32(cropOrigin/maskExtent)`。零crop由原ROI检查补 `RN32(1/maskExtent)`。因此“默认零crop”和“显式完整matte crop”不等价，S60手工 `1/mainExtent` 与后者相容，尚未绑定实际相机/PI consumer。原AIR以主图像素中心生成坐标，person/skin取ROI112/128B的float4，half matte阈值为≥.25（evidence/s55/local-histogram-source.ll:75–99、255–273）。不得据字段名或默认wrapper比例替换冻结上下文。

**已验证数值（HDR-80）**：S71 run39346448714/artifact12231437053，26A434/image20261012.0260.1；1024×768恒灰、32×24横向person/纵向skin阶跃，identity GTC、base/exposure1、SRL0。原CPU生成176B ROI，手工dispatch原host-retained localHistogram PSO（mask1，32×24线程、32×32组）。7组控制的14,336个计数单元与运行前冻结预测全部相同，max abs0；主图/linear/两matte/GTC/params/stats SHA与目标外ROI字节不变。

|仅改变的crop|person总计数|skin总计数|每格max abs|
|---|---:|---:|---:|
|default|774144|774144|0|
|person_full_matte_crop|399360|774144|0|
|skin_full_matte_crop|774144|401408|0|
|person_shifted_matte_crop|595968|774144|0|
|skin_shifted_matte_crop|774144|598016|0|
|person_logical_size_crop|774144|774144|0|
|skin_logical_size_crop|774144|774144|0|

**失败与范围**：S70误带历史mask2而未创建统计PSO，run39345177157/artifact12230252826返回3；这是S55/S56已解决的初始化问题，本轮保留失败归档，S71只依已有静态证据修为mask1。未新拟合曲线、未重做旧269例。两份ZIP共8582B全部成员SHA已校验，S71 ZIP SHA `0cf5bc0e6ffba46c7354e5bfccae3feb32bafd5772152888be2ede6e251114db`；manifest/source/完整原始JSON与复现见research/hdr-native/evidence/s70-s71/及validate_matte_roi_s70.py。只验证有限合成阶跃，不是全纹理/fast数学/非有限路径的C04合同，也不是新增7张照片或完整host/相机执行。没有新照片预览或物理EV结论，旧ACES预览保留。

**可交给macOS runner（HDR-81）**：读原PhotoImaging消费端优化selector、参数常量及ABI，继续绑定真实consumer ROI和统计源；33皮肤点C01–C05紧外包络、完整原生往返、封装后全图ImageIO SDR max0保持未认证。**待实机**：匹配IMG2810同帧j/WithoutFaceBoost曲线、N/B/T/V、face hist、allocateTone与应用域，原Studio统计、2679/2408 RAW及实际HDR观看沿用原清单；β=.1953125仍不是像素EV。GTM/LTM/语义分开，Apple Log、原件、冻结文件、原mask及阈值均不改。**A_phase_complete=false，acceptance_complete=false。** 累计写入许可125MB，根分区至少4GB；无人物明文上传，无完整EXR写入。

S71坐标编码补充（已验证数值，HDR-82）：matte_roi_s71.py独立实现原CPU舍入/除法顺序；复用原7组捕获的56个UV float32分量全部逐位相同。实现后补，不计新增留出；证据uv-model-validation.json含代码SHA。validate_matte_roi_s70.py同一复现入口同时报告原计数和此CPU坐标检查；未接入冻结路径、未认证实际调用者或C04全域。


### SEMANTIC-20261018：S72 原 PhotoImaging 消费端调用绑定

**已验证静态（HDR-83，原生符号绑定佐证）**：run39350205726/artifact12232168720，26A434/image20261012.0260.1。匹配PhotoImaging UUID5F17E1DB-A15E-38C7-9BEC-E081688B62E5、CMI UUID3CCD434E-B1E0-3F14-8EF6-E29D58379BE8；26个优化selector、15个CFString常量、4个方法ABI均读取成功。纯CPU只读，无图像/PSO dispatch。PISemanticStyleProcessor方法IMP0x1cbeef754、ROI IMP0x1cbef066c，Filter outputImage0x1cbef1c78。

原process block在0x1cbeefd84–d88把block+0x90的两个double交给setLogicalImageSize:；0x1cbeefe4c–e60用同一尺寸的double倒数交给实际selector **setLogicalImageToInputLinearImageScale:**。这明确是linear输入比例，不能凭邻近setter猜成LTM map或matte比例。person/skin/sky分别设置纹理及mapped region；它们的实际CI ROI仍需下一步验证。

|arguments实测常量|原调用|实际CMI接口|
|---|---|---|
|baseGain，0x1ee262218|0x1cbef001c|setInputLinearBaseGain:|
|faceBasedGlobalExposureBoostRatio，0x1ee262238|0x1cbef0048|setFaceBasedGlobalExposureBoostRatio:|
|stats，0x1ee2621d8|0x1cbef0154|setInputStatisticsByStatsType:|
|xstats，0x1ee262258|0x1cbef0180|setInputStatisticsByStatsKey:|

stats/xstats两个setter受block+0xc0==1分支保护（0x1cbef0128–0130）；本节尚未独立绑定该标志的来源，不把这两步当作无条件执行。这里只证明字典取值→实际setter的数据流。常量名不证明应用域、相机来源、j是RGB乘数或影调逆已完成；既有j干预consumer零差与相机β界仍按原范围解释。S72完整ZIP3657B，SHA `f8b4dba6e3fddc344ebeff071a8f480d9777aeea2134db8c444fdc04261dff98`，manifest及每成员SHA全部校验；原JSON、源码SHA、ABI、反汇编行与归档receipt见research/hdr-native/evidence/s72/。

**可交给macOS runner（HDR-84）**：以显式extents和全帧/分块输出区域调用原ROI方法，进一步绑定实际consumer的matte采样；继续原统计源、33点C01–C05、完整往返与编码SDRmax0。**待实机**仍为匹配IMG2810的同帧j/WithoutFaceBoost四曲线及N/B/T/V、face hist、allocateTone/应用域，原Studio统计、2679/2408 RAW与HDR实屏。没有新增照片结果或预览；GTM/LTM/语义分离、Apple Log、冻结上下文和全部门槛保持。**A_phase_complete=false，acceptance_complete=false，goal active。**


### SEMANTIC-20261018：S73 原 CI 请求 ROI 与实际 mapped-region 的分界

**已验证静态（HDR-85）**：原PISemanticStyleProcessor ROI方法0x1cbef066c在index0返回outputRect、index6/7/8返回各自完整extent，其他有效索引调用NeutrinoCore的NUCGRectConvertFromRectToRect(...,false)。GOT/跳板地址0x1d01aa9b0实际目标0x1c5ba7884；另外4个导入精确绑定为NUPixelRectFromCGRect/Scale/ToCGRect和NURectFlipYOrigin。原生dladdr exact-address全为true，NeutrinoCore UUID5E0B3F6B-554E-3373-A411-4A4D1CF0A057与原提取binary SHA b42a15eab428fb24f355d19b00efc0e8599d37e7c672516f97c21ea76cb24419对应；PI仍为5F17E1DB-A15E-38C7-9BEC-E081688B62E5、26A434。

**已验证数值（HDR-86）**：S73 run39353695210/artifact12234397335，source4a349173547b96e9b0994c57c98192d774b6b474，image20261012.0260.1。运行前冻结三种几何（整图、小数分块、带原点偏移）×9索引×useLightMap false/true，共54次原CPU调用/216个double分量：

```
index0: R0 = outputRect
index6/7/8: Ri = full extent_i
other supported i:
Ri = (xi+(X-x0)*Wi/W0, yi+(Y-y0)*Hi/H0, Wout*Wi/W0, Hout*Hi/H0)
```

最大误差1.7763568394002505e-15（源坐标单位），通过此CPU几何控制预设1e-12门槛。consumer_roi_s73.py的后补独立实现重放同误差，非新增留出。所有原manifest成员SHA已验，完整ZIP5360B SHA `f23f633a0b760d8cac37a7b4a746f5eec71d2e3b5583f7bdeaa828d3b01889b7`；原始JSON、ABI、导入目标、汇编行/文件SHA、源代码SHA与复现输出在evidence/s73/。这54次均无照片/图像或PSO dispatch，不计入五张照片验收。

**已验证静态，证据边界**：实际process callback(0x1cbeefc58)还将输入对象CGRect getter(0x1d0088a70，selector尚未在此探针解码)返回值依次交给PixelRectFromCGRect(policy0)、PixelRectScale(policy0)、ToCGRect、FlipYOrigin。PixelRect为四个signed-int64分量（RectT<long>、ToCGRect的scvtf）；policy0使用floor(min+C_a)/ceil(max+C_b)，常量槽0x1c5cf52a8/0x1c5cf5450尚未读数值。实际CI分配/取整和采样未在S73捕获；不能以请求ROI公式通过替代这些算子或C04全域。未把此实现覆盖冻结输入，也未凭函数名猜getter或常量。

**可交给macOS runner（HDR-87）**：读原getter/常量，逐项复现整数取整/缩放及实际CI buffer的尺寸、mapped region、scale，再做完整像素对照。33皮肤点C01–C05紧外包络、完整原生往返、ImageIO封装SDRmax0继续未通过。**待实机**同帧j/WithoutFaceBoost、N/B/T/V、face hist/allocateTone/应用域、原Studio统计、2679/2408 RAW及真实HDR观看仍按既有计划。没有新HDR预览或物理EV；GTM/LTM/语义仍分离、LinearThumbnail为Apple Log，原件、mask、half/float/PSNR/1e-3门槛不改。**A_phase_complete=false，acceptance_complete=false，goal active。**

125MB许可下的S67补档（已验证数值，仅完整性，HDR-88）：原run39335997594/artifact12226746912仍未过期，完整ZIP210521B现已追加落地，SHA b1b95a5df2ee252eec41153cdce6f88d521c36490fc5422bbacb734a208509f1，原manifest SHA 8efb2a7166222ef8054df2a569d4bd5b0fdbb5a5e67d5af2cd0754851417141c，29个payload成员SHA均验证。与原选取包记录为同一份原ZIP，旧selected-original-members.tar.xz保留且SHA不变；未重跑任何原生实验，也未改变S67冻结2/3或后补条件模型的结论。第一次补档读取器把历史bytes字段误当size，在写ZIP前报错；核对旧原manifest后修正，最终完整验证。见evidence/s72/full-s67-archive-supplement.json；此后补记录不改写早先“只保留必要成员”的历史事实。


### SEMANTIC-20261018：S74 原整数 ROI、容差与 region getter

**已验证静态（HDR-89）**：26A434原callback的getter0x1d0088a70现已解析为`region`。原NC UUID5E0B3F6B-554E-3373-A411-4A4D1CF0A057（binary SHA b42a15eab428fb24f355d19b00efc0e8599d37e7c672516f97c21ea76cb24419）中，policy0的double槽0x1c5cf52a8和0x1c5cf5450分别为+1e-6与-1e-6（bits `0x3eb0c6f7a0b5ed8d` / `0xbeb0c6f7a0b5ed8d`）。四个CoreGraphics极值导入均dladdr精确绑定，因而有限正尺寸路径可写为：

```text
lo = floor(min + 1e-6); hi = ceil(max - 1e-6)
PixelRect = (lo_x, lo_y, hi_x-lo_x, hi_y-lo_y)   # 四个 signed int64
正scale：先分别乘整数origin与size，再将两者相加得到max，重复policy0。
FlipYOrigin(r,b) = (minX(r)-minX(b), maxY(b)-maxY(r), width(r), height(r))
```

来源：FromCGRect0x1c59b581c、setXYMinMax policy0的0x1c59b5a0c–5a44、Scale0x1c5ba4b0c、Flip0x1c5ba65d4；原disasm行40547、40600、40727、554398、556159及本节evidence/s74/source-notes.txt。这里的x平移也依赖bounds原点，不能仅翻转y。

**已验证数值（HDR-90）**：S74 run39368595307/artifact12240755401，source07353ab0a6d16096a3883da960fa8613da91d243，image20261012.0260.1。运行前写入公式/控制规则，metadata进程只读常量（测试primitive调用数0），在oracle前冻结54个控制：5类整数/小数/负原点矩形×6种正scale，加24个原常量边界的nextafter邻点；比例含5712/1024与4032/1024。270次原CPU函数调用的432个整数分量完全一致、648个CGRect分量max abs0，输入JSON/整数输入与FPCR0均不变。独立CPU几何预设gate1e-12通过，原RGB half/float1e-5+PSNR60及可逆mask内1e-3保持原样。

不带±1e-6容差的数值重放会改变16/54个控制、48个整数分量（epsilon-ablation.json）；这证明几何边界会改变，不是照片光晕/像素误差测量。consumer_pixelrect_s74.py与validate_consumer_pixelrect_s74.py提供独立重放，不覆盖冻结路径，不计额外留出或五图验收。本轮没有照片/PSO dispatch或新预览；旧固定ACES预览与Apple Log缩略图保留。

原始ZIP9973B SHA `64af6fe10403d51a66950970f3f0b286c3194a05f9ef993c8743d758086289a4`，manifest SHA `e18804df3412f92eb533c1df8ad30d9c292af4cb4ba53957c0e527d6482ea28e`，10个payload成员及所有recipe源码SHA均校验，原ZIP在hdr-native-20261019/runs/39368595307/。两次传输在写入前超时；改用curl后取得同一run/attempt1，未重跑原生实验，凭据/签名URL未写盘或日志。原JSON、冻结值、逐项误差和复现在research/hdr-native/evidence/s74/。

**可交给macOS runner（HDR-91）**：实际CI分配的region/format/texture尺寸、mapped region与sampler尚未捕获；本轮只补正尺寸/正scale的有限CPU链。33点C01-C05完整声明域（纹理、fast math、非有限路径）紧外包络、完整原生往返和封装SDR ImageIO max0继续未认证。**待实机**：匹配IMG2810同帧j-only/WithoutFaceBoost四曲线、N/B/T/V、face hist、allocateTone/应用域，Studio原统计、RAW2679/2408与真实HDR屏幕；β=.1953125仍不换算像素EV。GTM/LTM/人物语义分开，全部原mask/门槛保持。**A_phase_complete=false，acceptance_complete=false，goal active。**


### SEMANTIC-20261018：S75–S80 原 CI consumer、无效成功返回与有限空间 oracle

**已验证静态（HDR-92）：** 26A434/PhotoImaging UUID5F17E1DB-A15E-38C7-9BEC-E081688B62E5、CMI UUID3CCD434E-B1E0-3F14-8EF6-E29D58379BE8。原格式表0x1e1fcb0b8与getter逐项相同：输入0/4及输出是RGBAh(2056)，其余是Rh(2053)，实际MTL纹理为RGBA16Float(115)/R16Float(25)。slot4是linear输入；slot5只绑定setInputGainMapTexture:，不靠命名断定HDR容器域。slot6的0x1d00b8a70为setInputGlobalToneCurveTexture:；7/8的0x1d00b8cc0/8cd0为setInputSmallLightMapTexture:/setInputSmallLinearLightMapTexture:。baselineExposure的CF0x1ee262158→setBaselineExposure:0x1d00b7bd0。完整useLightMap数据流见evidence/s75/source-flow.json：block+c0保护stats/xstats与两图setter；stats参数缺失选processingType3、存在选2。

**已验证数值（HDR-93，纠错）：** S75 run39387345347在编译时报NSValue valueWithCGRect:未声明，尚无原processor调用；S76仅用valueWithBytes/getValue存取observer的CGRect。S76六个useLightMap=true callback虽然YES、A/A相同，却全部读回零。S77 run39388810043用原方法返回码与PSO创建/dispatch观测定位：有small maps却无stats，原process0x23336a8d8在0x23336aa20–aa3c命中一致性assert（cold3，0x2334d5d14；字面量“Input statistics/small light maps are incorrectly set”），跳到0x23336aa18置status0返回，外层PI据status0返回YES。实际只有每次157次hueSatLumLUTCalculation初始化，没有renderFinalAdjustments。false/missing-stats独立控制的原统计ROI返回5。故这些零差不计有效图像oracle；S76的512条trace上限也已明确记录。S78无完成case时all(empty)产生的true不作为不变性证据，未改写原始JSON。

**已验证静态/数值（HDR-94）：** 原SSRDictionaryFromStats0x2333d7b40、SSRExtendedDictionaryFromStats0x2333d7e14、Populate0x2333d81a8/81b4均精确dladdr绑定到同UUID。SSRStats0x2990B，0x2800起10×9个float32，0x2970另两float；S78构造正值合成输入，经原序列化/解析92个float逐位往返，原输入SHA不变。原函数返回的字典提供字段绑定，不把字段名当成相机应用域证明。S79另设仅将10个record的raw field7由.9改.005的独立合成profile，两组结果在这个控制内相同；不能推广为该字段全域无作用。它们都不是实际照片或同帧相机统计。

**已验证数值（HDR-95）：** S78 run39389860461已走RenderingParamsFromStats、两次createGuide、五组三阶段guided filter及createLTMGainMap，随后_applyFinalRendering/_checkROISpecification返回5，停止后续case。原_processSegmentationMasks0x23336d9e0仅对person条件上采样，skin/sky保留输入纹理（0x23336db54–db68）。S79保持原stats，只把skin/sky按原逻辑边界4×最近复制为64×48，person仍16×12，原检查通过；两个独立profile各A/A、共4次真实renderFinalAdjustments，RGBA有限、全部RGB分量非零，half字节相同/float max0。只证明本组CI映射条件，不证明真实调用者的所有matte必须全尺寸。S79 observer未识别含引号字段名的ivar编码，未取得完整CGRect；源码/历史记录保留，S80单独修正。

**已验证数值（HDR-96）：** S80 run39391600201/artifact12250205961，source efccbe9887b9fec8129394ac8c829b8548b8c727，26A434/image20261012.0260.1。固定S79 ordered合成stats、tone+.35/baseGain1/j1、其他原参数/GTC/maps/源图；实际CI apply/process与原BOOL、PSO参数、shader、residency均保留。规范化ivar类型中的字段名，并先核对大小/对齐，24次快照各读到22个几何项。whole/tile/translated各A/A共6个成功callback、1062 dispatch（含6次final），9路输入/输出half全部读回，source与stats SHA不变；三组AA half逐字节相同，CI float max0/PSNR∞，符合原来的AA数值门槛。whole对translated也half/float精确。这些是有限原生重复/分配控制，不是NumPy前向、逆解、五图或场景恢复通过。

空间对照单列：计划预先声明storage row8与20两种crop。仅row20与实际输入0的half字节完全匹配，独立于输出误差；row8不匹配，不拿输出误差挑方向。在输入匹配的row20，tile与whole裁剪的原生RGB仍有max abs **0.000244140625**、PSNR **84.44812904567885dB**；超过原float max1e-5，不能当空间逐位一致或整体验收通过。差异尚未定位到guide、map、ROI归一化、采样或具体half算子，不猜成某个原因。row8对照max.0830078125/PSNR25.9062只作为错误存储行假设记录。API字段与CPU/GPU内存合同参见[Apple CIImageProcessorInput](https://developer.apple.com/documentation/coreimage/ciimageprocessorinput)与[render toBitmap](https://developer.apple.com/documentation/coreimage/cicontext/render(_:tobitmap:rowbytes:bounds:format:colorspace:))；未把CPU stride当GPU纹理布局。

**可交给macOS runner（HDR-97）：** 固定已合格上下文，逐项捕获最终PSO使用的guides、上采样maps、mattes、ROI/params和输出；仅替换一项做oracle-replacement，区分tile残差来自哪一步。继续PI上游真实matte resize/crop、C01原half-pow合同、C02实际backend重写、C03非有限路径、C04全部允许采样组合与C05全域覆盖。PSO名称/对象/有限像素已绑定，仍没有最终ISA或原编译器mathMode合同；33点全域紧外包络、原1e-3/mask、完整native往返和全图编码后ImageIO SDR max0均未通过。停止旧bit-exact拟合的决定保持。

**待实机：** IMG2810匹配设备/OS的同帧j-only/WithoutFaceBoost四曲线、N、B/T/V、face hist、allocateTone与应用域，原Studio统计、RAW2679/2408及真实HDR headroom显示继续按NATIVE_TODO清单；参考机型β=.1953125未换算最终像素EV。GTM/LTM/语义逆仍分开；LinearThumbnail保持Apple Log；本轮没有照片、EXR或新预览，旧固定ACES预览与SDR保持路径未改。**A_phase_complete=false，acceptance_complete=false，goal active。**


S75–S80传输收尾（已验证静态/归档完整性）：六个terminal run的原ZIP均已保存，并在删除前核对所有PR head/base引用为空、源码已在远端保留研究分支。六个临时ref全部返回DELETE204且随后精确查询为空；本批未创建任何secret/release，未修改master或其他分支。一次清理预检的公共API读取返回curl22，发生于任何删除之前；后续同一run读取200/completed，原失败HTTP状态未保留，不能推断根因。改为配置CLI凭据仅在内存/stdin访问api.github.com，重新检查全部前置条件后清理完成，未重复原生实验、未写盘凭据或签名URL。详见research/hdr-native/evidence/s80/closure.json及hdr-native-20261019/cleanup-s75-s80.json。原归档、样张、冻结模型及consumer-goto-v8两个受保护文件均保留。


### SEMANTIC-20261018：S81 实用效果优先，停止微小精度追查

**工程方向调整，非新增实验结论：** 2026-10-20 用户明确允许“99%效果”，不再要求像素级还原与完整可逆。按接近目标的实用效果理解，不声明已取得 99% 数值准确率。原 bit-exact、33 点全域紧外包络、C01–C05 全覆盖和逐像素唯一逆解从当前实用交付的阻塞项中移出，历史未通过记录、原门槛及冻结模型保留。S81 原 PSO 单绑定微小残差归因探针在创建源码/workflow/分支/run之前暂缓；没有新增照片、预览、原生运行或 errors.csv 测量行。

**可交给 macOS runner（HDR-98，计划）：** 改为真实照片的 global-only、local-only、semantic-only 与联合 HDR 五种对照（含原 SDR），统一此前固定 ACES/曝光，报告 EV 分位数/最大值和 coverage、边缘光晕/振铃/接缝、肤色/背景误改、亮度连续性及低/中/高 headroom；至少五张全尺寸、两张冻结后留出。数值门槛按新配方提前声明，不把旧 PSNR 或 p99 冒充“99%效果”。保持原 SDR、预览输入 SHA 不变、不可恢复 mask/区间及目标/传输误差分开。真实可见缺陷需要时再重开精度定位。S80 的有限合成 max 0.000244140625、PSNR84.4481 dB 仅作为既有记录，不改称实用通过。

**待实机：** 同帧 j/WithoutFaceBoost 曲线和 N/B/T/V/人脸统计/allocateTone/应用域、Studio 原统计、RAW2679/2408 及真实 HDR 屏幕仍按原方案。自然度和物理场景精度分别报告，相对场景母版仍标候选。新状态 engineering_accepted=false；A_phase_complete=false、原 acceptance_complete=false、goal active。完整政策与用户原文见 research/hdr-native/evidence/s81/scope-change.json；实用清单见 research/hdr-native/PRACTICAL_ACCEPTANCE.zh-CN.md。125MB 为累计许可，其他资源/隐私约束、Apple Log 与 global/local/语义分离保持。


### SEMANTIC-20261018：S82 条件皮肤校正准备 / S83 实用控制代码验证

**已验证静态（HDR-99，新增自有实现，非苹果全域逆证明）：** semantic_strength_s82.py 采用 C=y+F0(xhat)-F(xhat)，在有限且RGB严格为正的比值域做 output=exp2(log2(y)+alpha*(log2(C)-log2(y)))。F0仅关闭目标皮肤参数，外部c/d、GTC、guides、统计和其他matte固定；不加入平滑/曝光或GTM/LTM逆换。alpha是输出效果插值，不是苹果参数；默认.5未用oracle选强度。域外保持y并返回mask；0强度保留源、源只读、每块≤262144像素、dtype溢出拒绝。它是可复用的条件估计，既不保证一般非线性误差抵消，也不声称拍摄端皮肤恢复。

**已验证数值（HDR-100，仅合成控制）：** S83 run39399353600/artifact12254506268，source17fcc3bd029da1d252515660e70e8ffa30123e36，26A434/image20261012.0260.1。5档强度×5种分块布局，同一24576像素合成张量块间max abs0；有效比值像素24273，域外原值保留。只读源SHA不变，7类无效输入/输出溢出被拒绝；已知加性目标的残差抵消max1.1102230246251565e-16，自选变换往返max1.191113041532077e-7。后者不是native consumer往返。chunk guard预先设1e-6，仅验证新代码结构，不替代旧门槛；没有照片、新Apple像素执行、预览或scene结论。原ZIP2337B，SHA3d180ba38ea787438fd6911ce5b6dab0bcdf1293570a137797606c5c28c6c356；5个成员和源码SHA均校验，临时S83分支经全状态PR head/base0引用检查后删除，源码留研究分支，master未变。

**可交给macOS runner（HDR-101，S82待批准传输）：** 复用现有S5/S8两份密文原ZIP共110814893B，无本地大文件复制；不采用S15/S16按既有oracle误差挑点的补丁。计划在同一真实384x512捕获上输出0/.25/.5/.75/1强度，分开报告皮肤色彩、皮肤亮度和两者联合，固定ACES；整幅、matte footprint、实际受影响区域分别统计误差/边缘/色偏，避免背景稀释指标，正比值域外的原生端点差异另列。它不计全分辨率、五图或新留出，也不与global/local混合。源代码与workflow已冻结，但没有S82 run、secret、release、临时分支或新照片指标。

自动审批先拒绝contents:read→write权限提升，再拒绝未得到目的地明确许可前将人物密文上传公开预发布release。两项均未执行；workflow保留read。已提出公开密文目的地确认，传输脚本额外要求明确批准记录；当前不改用其他方式上传同一人物数据。证据见evidence/s82/permission-decision.json与pending.json。S83无需人物/secret/release，已独立完成；不能用其成功冒充S82验证。

**待实机清单不变：** 匹配同帧j/WithoutFaceBoost曲线与N/B/T/V/face histogram/allocateTone/应用域、原Studio统计、RAW2679/2408、真实HDR屏幕。j权重增量仍未标定为像素EV；Apple Log、原件/冻结模型和33点未认证记录不改。实用五图/两张冻结后留出、分离global/local/semantic预览和最终封装SDR max0尚未完成；engineering_accepted=false，A_phase_complete=false，原acceptance_complete=false，goal active。新实用控制说明见PRACTICAL_SEMANTIC.zh-CN.md。


### SEMANTIC-20261018：S82 实用皮肤强度控制已运行，原生反事实与场景真值分开

**已验证数值（S82，26A434）。** run39407894040 / source45e02e86d1ced0c375b6c9ebed8cae3bc3681090 / xcode-27 / image20261012.0260.1，复用原S5/S8已保存原生数组；本轮没有重复原生前像搜索，也没有采用S15/S16按oracle误差挑选的点补丁。输入为IMG2810既存384×512、tone=+.35的consumer捕获，不是5712×4284原片、五图或配对无风格场景真值。GTM、LTM、j、人脸/人身和Studio纹理不在这次校正中改变；LinearThumbnail保持Apple Log。

自有控制公式为 C=y+[F0(xhat)−F(xhat)]，有限且y、C各RGB分量严格正的域内 Hα=exp2(log2(y)+α·[log2(C)−log2(y)])。0/.25/.5/.75/1五档、默认.5在查看本轮照片指标前已固定。它控制已求出的输出反事实差值，不是Apple tone或theta的线性插值，也没有把j=1.098当RGB倍数。F与F0使用同一恢复输入和外部上下文，原S5干预只改变目标theta9/10；其他参数字节、c/d、GTC、guides、统计和matte保持。oracle只用于对照，没有参与挑选强度或局部补丁。

**已验证数值（按真实受影响区域报告）。** 半强度与相同输出强度的原生反事实比较：

|单独去除项|实际受影响且非近黑像素|亮度误差p99 EV|最大EV|最大归一化RGB色度误差|该区域PSNR dB|
|---|---:|---:|---:|---:|---:|
|皮肤色彩|887|0.00126700|0.00167631|0.000328422|77.8183|
|皮肤亮度|1512|0.00134784|0.00173077|0.000403702|88.5630|
|联合|2399|0.00129445|0.00173077|0.000403702|81.5566|

全强度联合在同一2399像素中的p99/最大EV为0.00258883/0.00346258，PSNR75.5271dB。整幅196608像素全部有限；187224个matte采样足迹外背景在15个变体中变化均0。原非近黑诊断保持RGB>1/255，共186949像素；这不是删改旧mask。整图正比值域196607像素、域外1像素保留base并输出mask，这一覆盖率不是场景准确率或唯一逆置信度。全图近黑的半/全强度联合最大EV仍0.0422613/0.0838671，不能只引用背景稀释后的整图p99=0。原生全强度端点未改写；域外1个原生变化5.960464477539063e−8也独立报告。

**已验证数值（有限自洽性）。** 21次固定ACES预览的前后输入SHA相同，所有所选原输入文件SHA也相同。选定自有增益的浮点往返maxabs≤5.960464477539063e−8，只证明这条控制的自洽性，不证明Apple完整逆解或物理场景恢复。半强度联合的matte边缘加权log-RGB梯度p99/最大为0.0266308/0.0862873EV；它是所选校正的空间变化代理，并非相对原生的梯度误差，也不是无光晕证明。未在VM解码人物预览，不能据此下无色偏、无光晕或主观效果已通过的结论。

证据：`repo/research/hdr-native/evidence/s82/practical-summary.json`、`run/analysis.json`（15变体全部区域与原生端点）、`run/input-verification.json`、`run/freeze.json`及源`run_hdr_s82.py:96`、`:109`、`:138`。固定显示仍为cg-config-v2.2.0_aces-v1.3_ocio-v2.4，LinearP3-D65 → sRGB Display / ACES1.0 SDR Video，0EV，config SHA5aefc668796eabb1902b9593340496231758eceaec18ce290e12901042bd4440。三行三列密文contact对应色彩/亮度/联合×0/50/100%，另有联合matte边界ROI和比值域mask。

**已验证静态/归档完整性（用户本轮明确授权后执行）。** S5/S8现有密文原ZIP合计110814893B临时上传公开prerelease，不产生本地归档副本；runner权限contents:read，未上传照片明文或私钥。S82结果ZIP已立即落地：汇总artifact12257239736，15425B、SHA3955094e7a72baaf16f643167ee3f7e828ccc080d14c9d6f87d3a49cca345474；密文预览artifact12257579499，270052B、SHA622ed242cfcc9e0a45696bd4ed35a02ab8f5604b24763c3388aaea67de7f301c。11个汇总成员和4个私有manifest成员SHA均核对，GPG returncode0、GOODMDC，私有manifest SHAfd2e7c2d4a6ce1ec1a2d73863455fb4c0200006527918c50d0dac0d5f493c4b3。归档后核对所有PR head/base引用为空、源码保留研究分支，再删除两条临时secret、release、tag和触发分支，五次DELETE均204，精确查询确认不存在。证据见`evidence/s82/user-transport-approval.json`、`closure.json`和`run/archive-receipt.json`。历史HDR-101“待授权/未运行”记录不覆盖；由这次新记录更新当前状态。原预检gh只读release列表失败发生于任何远端写入前，改用配置凭据仅在内存/stdin的curl GET重新核对全部条件后成功；未提升workflow权限。

### HDR-S84：原尺寸SDR零差有效，旧混合坐标HDR指标不作结论

**已验证数值（26A434）。** run39403808066 / source45e02e8，只用已公开IMG2600，5712×4284；固定旧S31 RGB压力图EV=[3u,−.5+2v,2(1−u)]，它是承载测试，不是scene母版或艺术HDR目标。8/10bit各自保留46个原primary后代的coded payload及所有属性、142个非gain/tmap原item payload；完整ImageIO显式DecodeToSDR整数光栅的4284行×22848有效字节变化0，格式/ICC相同，原/新有效字节SHA均45db8a8a774044df6ff51c81a06c4e098ed6cb3e0bef9030adb98347157fe797。此SDR max0结论独立于后续CI浮点读回坐标错误。

**已验证静态（对照资格边界）。** S84新blocked reader把递增CI-y块直接拼成存储顺序，和S44整幅参考及先前S80的H48/CIy8/h20→存储row20约定不一致。原HDR/gain/CI误差表和native预览panel原样保留，但在同源坐标控制通过前均不具解释资格；不能把其中的约2EV误差归因于codec、颜色管理或场景逆解。参考源的独立量化数学诊断仍有效：8/10bit亮度EV中位数0.00217695/0.000540652，p99为0.00604822/0.00149291。RGB逐通道理论半LSB为3.5/(2·(2^bits−1)) EV；带符号RGB相消及近黑时亮度相对误差不受这个逐通道界约束。完整载体未下载或持久归档，不能把文件SHA当成已交付HEIC。

S84原ZIP：汇总artifact12257525181，15772B、SHAafac971ddd9156a8f4499c77c86286b7e6fd6165a68cca7249e83991f11e9735；密文contact artifact12257480250，413188B、SHAd139f160e80ff938cc4f7bc20c2cc30f4177fd47600a94452bc434fef9557d8b。20个汇总成员及2个密文成员、GPG和源码SHA已验。触发分支在PR引用为空、源码保留后已清理。证据：`evidence/s84/run/archive-receipt.json`、`comparison-status.json`、`closure.json`；S85只修读回并增加颜色/坐标控制，不改变冻结目标、原件或旧模型。

**已验证静态（五图容器，不计新像素验证）。** 五份既有HEIC均有ISO tmap/base/gain绑定，维度、属性原字节SHA及offset记录于`evidence/s84/source-container-bindings.json`。2600/2604/2608的primary存储画布5712×4284；0032/0033的primary4032×3024、irot270，而tmap3024×4032、irot0。因此后续两张验证必须原生核对坐标，不能用改变全局画布方向的隐式resize掩盖。


### HDR-S85–S86：坐标、原生应用公式与编码误差分开

**已验证数值（S85，26A434）。** run39408560663/source42dc055458bf9e5ddb8346ba80851c0751587f83；同一5712×4284源，共24470208像素。固定规则CI_y=H−storage_top−block_height，块内行序不变，整幅/分块和S44参考的差均0，SHA均1f8cd21a4278d466042cefb6c1adf35fb4ed0f3acfbfd425153d8bd32a4f2a66。旧递增CI-y拼接在这同源对照中maxabs1.123616136610508、PSNR5.29064dB。S84坐标错误因此有原生数值证据，原始归档不覆盖。

原坐标修正后，matrix0的HDR目标仍失败：8/10bit中位EV0.277590841/0.277219802、p99为1.02657294/1.02635997，gain code maxabs0.783003279/0.777308541；两端完整SDR仍0差。原生headroom1/2/8与“实际解码gain”的方程比较，maxabs≤2.707780742738919e−6、PSNR≥145.090dB。说明应用公式对实际code正确，不代表实际code等于原上传整数。gain的CI颜色空间nil，HDR为DisplayP3_PQ，原/新SDR均同一DisplayP3 ICC；本轮未从字段名推断provider内部转换。matrix0问题与旧S31观测相容；没有重新追pow/half误差来解释它。

**已验证数值（S86，26A434）。** run39409968844/sourcef0ccf95cea77e3359eca78e2a2e9506c3c392eb7，保持S31目标和S85读回，仅改为旧S32已观测更可靠的matrix6/10bit；实际colr为nclx、matrix6、primaries1、transfer13、full_range=true，hvcC为10bit/4:4:4，不只依靠调用参数。原片、float源和预览输入SHA不变，完整ImageIO及CI SDR均0差。目标maxrelative(floor1e−6)=0.00564012579、maxabs0.0305681229、PSNR(peak1)53.4487dB；EV中位0.00095417272、p990.00339722466，最大3.38626207416EV。最大EV点尚未由S86定位，不能直接把所有大值判为近黑或宣称无可见缺陷；S87新增逐点见证。原1e−3/1e−5/60dB目标门槛仍false，未改为通过。

S86量化数学与codec/provider分开：理想10bit量化EV中位0.000540651468、p990.00149291405；相对该量化参考的额外原生EV中位0.000889274001、p990.00298003936。后者包含codec/provider路径，不是新逆处理误差。gain code maxabs0.00187288812。原生headroom1/2/8实际code方程maxabs≤1.0593947745718424e−6、PSNR≥142.688dB；这些有限承载自洽性不能替代场景恢复。

S85证据在evidence/s85/run（22汇总成员、2私有成员），S86在evidence/s86/run（19汇总、2私有），原ZIP/GPG/manifest/源码SHA均验、临时触发分支已清理。S85汇总artifact12258786314 ZIP SHAae9baf8afeb058d9c094e23e4dba0252de23cb3c355755cb93391b82aa1bcc9f，密文12258456624 SHA4fe189474408a0943d704846cf83eaecaaa6e78e67c15e2c55a3f6273470a7b1；S86汇总12259445696 SHA86afef59b3d884d573349c15e2d5235284602a870fc021115b31c5d798c953ca，密文12259245854 SHAc795344500c684b3bea789c1c40d4e1cec01a03579b4b78e4ee2ef6559053700。原件/冻结模型/consumer-goto-v8不变，未下载完整载体。

### HDR-S87：五图原尺寸、显式旋转和最大EV点审计

**已验证数值（有限实际结果，26A434）。** run39411684190 / sourcecc3a20ad2149b64f84793f56102eee9273389075 / image20261012.0260.1，已完成5/5张，其中本配方留出2/2。源代码、顺序及坐标约定在执行前冻结（evidence/s87/source-freeze.json）；0032/0033曾参与旧研究，只称本次oriented carrier配方留出，不称全新场景。

处理画布显式应用原primary irot；新gain编码前做反向irot，保留原primary和旋转属性。不是试翻转挑最低误差，也没有resize。ImageIO SDR零差逐项使用原整数光栅自身尺寸；它不与旋转后的浮点处理画布混为一谈。三个24MP源为5712×4284；两个12MP源原存储4032×3024/irot270，预期处理3024×4032。

|照片/角色|处理shape(H,W,3)|完整SDR max0|目标EV中位/p99/最大|最大RGB相对误差(floor1e−6)|最大EV点：负RGB/相消条件数|
|---|---|---|---|---|---|
|IMG_2600 / development|[4284, 5712, 3]|True|0.00095417272 / 0.00339722466 / 3.38626207|0.00564012579|True / 756.901904|
|IMG_2604 / development|[4284, 5712, 3]|True|0.000947487017 / 0.003227255 / 3.12501914|0.00564005289|True / 468.417859|
|IMG_2608 / development|[4284, 5712, 3]|True|0.000950467715 / 0.00328339719 / 6.46228291|0.00564009556|True / 575.449466|
|IMG_0032 / recipe-holdout|[4032, 3024, 3]|True|0.000938542653 / 0.00317216608 / 0.00607058792|0.00567894339|False / 1|
|IMG_0033 / recipe-holdout|[4032, 3024, 3]|True|0.000940910366 / 0.00319136469 / 0.00609545802|0.00567897795|False / 1|

最大EV的相消条件数定义为sum(|Yc·RGBc|)/|sum(Yc·RGBc)|；它描述该参考像素的亮度条件数，不能转换成全图准确率或无可见伪像结论。公开只存符号/近零分类和条件数，准确坐标、实际/参考RGB均在密文witness中。近零阈值、正亮度覆盖/排除数、所有headroom、量化和额外codec/provider误差均在每图analysis；不缩旧mask，也不删最大值。

**已验证数值（实际边界）。** 三张24MP图的最大EV点均含负RGB、参考Y≤1e−4，相消条件数分别756.9019、468.4179、575.4495，最大EV为3.386262、3.125019、6.462283；这是实际捕获的点分类。两张留出无该点相消（条件数1、RGB非负），最大EV0.00607059/0.00609546。五图目标EV中位0.000938543–0.000954173、p990.00317217–0.00339722，RGB最大相对误差(floor1e−6)≤0.005678978；逐点分类并不保证显示后无可见问题。全部5图完整ImageIO及CI SDR均0差。

**已验证静态（封装失败与归档恢复）。** S87 run结论为failure，五个child均returncode0、all_completed=true；主步骤和seal步骤失败于汇总101900B>预设90000B，缺少runner public manifest。原ZIP不改：汇总artifact12259413845/45106B/SHA5fc2a91d84ca682790e8e092bf127e6cab7bf8d7ba46300aea1b73b16f6a5f9b，密文12259249040/118227B/SHA1e6763fd0e823d69ba8a55446b716240a81d9fa3a07f19108421ab32f9d44a1e，均与API digest一致。另建derived-archive-inventory.json核对33个公开原成员；它不是runner manifest，未伪造或覆盖缺失文件。37个私有manifest成员经GPG returncode0/GOODMDC和逐成员SHA核对，包含JPEG contact及准确最大EV点witness。未重算像素或重跑workflow去改变run结论。evidence/s87/run/archive-receipt.json保留全部边界；原冻结workflow会重现这项封装失败，后续新任务应另估汇总容量。

**实用验收边界：** 本轮五图是固定RGB压力目标的表示/承载验证，不是原生摄影风格global/local/semantic五路结果，也不是HDR艺术效果或场景真值。S82只覆盖一张384×512语义捕获；五路独立结果、肤色/边缘/断层质量、最大误差点显示影响及真实HDR屏幕尚未组成新工程验收。因此engineering_accepted=false、A_phase_complete=false、原acceptance_complete=false。遵守用户“接近效果即可”的新优先级，停止旧bit-exact/33点全域紧界追查；历史失败、旧模型与mask保持。人物j实际EV、原Studio统计和配对RAW仍待实机，不把假设升级为已验证。


### SEMANTIC-20261018 / HDR-S88：独立HDR目标已封装，单图原生回读

**已验证静态（输入和公式边界）。** 用户“怎么样了，允许写入”批准此前明确申请的累计150000000B，保留根空余4GiB和所有原件/旧产物。旧S42 artifact12187152763在2026-10-20T13:04Z已404，未继续下载失效输入、未等待Mac文件。新rebuild_master_s88.py直接选择冻结run_hdr_s42.py的原AST语句（preamble行1–93、native master95–122、旧transport mask123–126），仅选IMG0032进行必要的集成输入重建。S42/S47及旧模型未改，S47的完整显示计算块除照片标签外字节相同；额外替换ZIP/GPG绑定和来源文字。该图这次是集成开发样本，不计新留出。证据evidence/s88/expired-input-fallback.json、user-write-approval-150MB.json和run/integration-freeze.json。

**已验证数值（输入重建）。** run39428400454 / sourcecaae6869d2824884d36f27c475c4684744f0be37 / macOS27.0.1(26A434) / image20261012.0260.1 / Apple Paravirtual device成功。实际重建EXR为27791119B，SHA9b392ea7cf996d1cbc70fbf82911b3c04e51562653010e7a78ee4a7a8129b012，与旧记录完全相同，EXR存储读回差0；这项相等来自实际新文件，不是以旧SHA代填。它依然是原生RGB guided thumbnail投影的相对场景线性P3候选，并非真实相机局部处理已经完全逆掉；其锚点面积误差p99仍0.0461462EV、最大3.56194EV，不能用transport通过替代母版精度。LinearThumbnail保持Apple Log。

**已验证数值（真正独立HDR目标，不是S31压力图）。** 冻结S44/S47显示步骤：固定网格中位亮度比定义单一显示scale k，H=kM·8/(8+max(Y(kM),0))；不改M、不添加语义操作、不做nit标定。直接对原4032×3024存储画布编码matrix6/10bit/4:4:4 RGB gain，保留primary irot270，原生oriented处理shape4032×3024(H×W)。Gain范围[-8.125,2.9375]EV，共同正offset在ISO有理数中序列化为0.000015，gamma1/headroom8。不同误差分栏，不把量化或codec损失记到场景反演。

|算子对照|亮度误差p99 EV|最大EV|线性maxabs|PSNR peak1 dB|
|---|---:|---:|---:|---:|
|float32 log存储|3.66465776e-08|1.20379089e-07|3.1997704e-08|174.578|
|offset有理数舍入额外|2.10970871e-05|0.000131612268|1.67138811e-06|137.756|
|实际编码输入的10bit量化额外|0.00463634541|0.00543600138|0.00581895779|61.5967|
|codec/provider额外|0.00600027846|0.02281758|0.0141467395|56.9188|
|最终原生HDR对独立目标|0.00873854818|0.0269484147|0.0191915035|55.6757|
|原生HDR对实际解码gain方程|4.48956342e-07|6.7630479e-07|6.1598254e-07|142.991|

完整12192768像素、36578304个RGB分量均有限，所有像素亮度满足该EV诊断域，没有排除亮度像素。最终亮度p99约0.61%，最大0.0269484EV；它是本图传输误差分布，不称“99%场景准确率”。RGB最大相对误差(floor1e−6)仍0.417625415、线性max0.0191915/PSNR55.6757，原1e−3/1e−5/60dB目标门槛保持false。offset舍入单项RGB maxrel0.2578478/线性max1.67139e−6也保留；尚未单独抓取最大RGB相对误差分量，不能仅凭大比值宣称可见色偏或完全无害。最大亮度EV见证为非负RGB、相消条件数1，准确坐标和RGB只在密文。

**已验证数值（SDR和有限headroom自洽性）。** 完整ImageIO显式DecodeToSDR整数光栅、格式和ICC相同，变化有效字节0，SHA8a74ebc858f021c9e839f645a4494a22acc3b135d998033bde1be3eb7512ca24；CI SDR max0。原生实际gain方程及headroom1/2/8均满足原float门槛，maxabs≤6.1598254e−7、PSNR≥142.991dB、RGB maxrel≤6.09498e−6。此处比较使用实际解码gain，还没有证明中间headroom相对创作目标的自然度。固定ACES1.0 SDR Video / LinearP3-D65→sRGB /0EV三联图仅作中性预览，三个输入样本SHA及完整源数组SHA前后相同，母版和原HEIC SHA不变。

**已验证静态（交付和归档）。** 成品HEIC5742091B，SHAdb24e56e81ee1080f5bf93dd8623c4ad47e0bf99c6ea84d8b737cf98340b8869；已保存在密文carrier.tar.gz.gpg内，附原S42零offset transport mask（未旋转存储画布，非场景逆置信mask或新HDR域）。原始ZIP：汇总artifact12266424270/28674B/SHAf598d9f1619796353d456fa56e79d5b5a99971a902be18dfa4917c7c4f15e2c9；密文artifact12267380960/5814301B/SHAa33b1420f2569452edfcfddf4689e5dd55a6519297264ced5c42f0c0ff164d22。28个public成员、两个密文archive所有manifest成员、GPG、源码和派生AST SHA均已验证，VM未解码或写出照片明文，完整输入EXR未下载。artifact retention1天，但原ZIP已本地留存。evidence/s88/run/archive-receipt.json和closure.json记录PR引用检查、原始归档及临时分支清理；本次无需secret/release。

**可交给macOS runner：** 将完全相同的独立目标/载体数学推广到其余原尺寸照片，独立报告理想headroom目标和实际输出，保持开发/配方留出边界；再推进全尺寸global-only/local-only/semantic-only分离与肤色/边缘实际质量。**待实机：** 同帧j/WithoutFaceBoost曲线与N/B/T/V/histogram/allocateTone/应用域、Studio原统计、RAW2679/2408、真实HDR屏幕。β=.1953125不换算像素EV。本图封装衔接成功，A_phase_complete=false、engineering_accepted=false、旧acceptance_complete=false；按用户新优先级停止bit-exact和33点全域紧界追查。


### SEMANTIC-20261018 / HDR-S89：五图独立目标、中间headroom与暗部传输边界

**已验证静态：** sourceb03beb93cfd1b5093fd8bed314ff53a76842febf只对冻结S88做输入/助手路径/小型归档绑定，逆替换后与原模板字节相同；实际生成的driver/rebuild源码逐图作为公共文本归档。S42原AST、S44/S47显示与S88编码数学不变。顺序2600/2604/0032为开发，2608/0033在S88 encoded independent-HDR数学冻结后才运行，计本配方留出；这些照片参与过旧投影/显示/压力图，绝不称全新场景或物理逆解留出。五个重建EXR实际SHA都与旧记录相同，无旧失效ZIP下载或新secret/release。

**已验证数值：** run39430695395，xcode-27/macOS27.0.1(26A434)/image20261012.0260.1；5/5完整计算，五个child returncode0，2/2上述配方留出，全部源数组与预览前后SHA相同。三张24MP和两张12MP的ImageIO完整整数SDR/格式/ICC均0差，CI SDR也0差。此处使用真正独立S44/S47目标，不能用S87较小的压力图误差替代：

|照片|原生HDR对目标p99/最大EV|EV排除数|理想headroom2对原生p99/最大EV|RGB最大相对误差(floor1e−6)|
|---|---:|---:|---:|---:|
|IMG_2600|0.229329278 / 16.8903019|95323|0.0715222056 / 8.08451913|698.120683|
|IMG_2604|0.0125815105 / 7.17179532|1609|0.00453058794 / 9.15462763|231.942831|
|IMG_0032|0.00873854818 / 0.0269484147|0|0.00291300153 / 0.0065224234|0.417625415|
|IMG_2608|0.0260136114 / 8.74552914|29373|0.0111151128 / 11.3448359|271.283643|
|IMG_0033|0.00910381973 / 0.385104994|8023|0.00302886086 / 0.00657193691|0.452112886|

原EV诊断域保持有限RGB、参考Y>1e−6且实际Y>0，以上排除数不能省略；新增headroom比较也逐项保留coverage/非正亮度数。理想端点过渡预先定义为I(h)=(S+o)·exp2(log2(h)/3·log2((H+o)/(S+o)))−o，h=1/2/8，使用原未舍入共同offset，与“按实际解码gain再代方程”分开。中间headroom不是显示环境自适应已通过，也不是当前像素达到scene-referred真值。

**已验证数值（实际暗部问题，不以大比值直接判观感）：** IMG2600完整目标p99为0.229329EV，不能从单图0.00874EV外推五图都接近。分解p99：float log6.27588e−8、offset舍入1.74180e−5、10bit量化0.150238、额外codec/provider0.189437EV；两项分位数不作可加误差预算。当前共同offset0.030745、gain范围[-14.125,4.125]EV。公式对gain扰动的导数为dH/dg=ln2·(H+o)，因而小H相对误差可被共同offset放大；这是数学条件分析，尚未据此证明p99全部落在哪个亮度段或显示后无伪像。三个24MP源的实际gain方程线性maxabs≤3.91955e−6，但近零分量RGB maxrel达到0.0134913/0.00332611/0.00386282，原1e−3 gate仍false；两12MP该方程通过原float gates。完整各算子门槛在phase-summary.json，未放宽或隐藏。

**已验证数值（最大RGB点分类）：** 五图的最大RGB相对误差分量，参考绝对值都≤1e−6，所以分母使用既定floor；它们的绝对分量误差依次6.98121e−4、2.31943e−4、4.17625e−7、2.71284e−4、4.52113e−7。前三个24MP部分点有符号变化，不能只称“相对误差大所以一定无害”。公开仅保存阈值/符号/绝对误差，准确坐标/RGB及log/offset/量化/codec各项贡献只在密文；亮度最大EV点的非正/相消分类也保留。五图×六张理想/原生headroom固定ACES图均先copy再变换，30次新增输入SHA相同；不是实机HDR观感通过。

**已验证静态（run失败如实保留）：** 五图计算均完成，但最终密文容量断言失败：1554198B>预先声明1500000B，导致run结论failure。公开manifest在容量核对前生成并存在，实际产物均上传，未改变原run或重跑像素。原ZIP：汇总artifact12268852452/202175B/SHAe9a37804c934b8d072a4e5d39235738ba67270c2e8b6e09114deebd484587c29；密文artifact12267719347/1555094B/SHAf425d482bb813e13de03718c97e6a0164e207375e34a34bf5b0138cd60492576。138个public成员、全部源码/派生输入替换、六份密文GPG/manifest均验证。本地归档第一次漏建嵌套目录，在原ZIP落地后停止；仅修复目录创建并复用原ZIP补齐，不覆盖历史归档、不重算。原容量失败与本地归档恢复分别记录；未来新实验需计入5份contact及新增对照的总大小。

**可交给macOS runner：** 下一步用预声明的相对亮度分层和固定ACES完整显示误差，判断暗部大EV的显示影响，再对最差IMG2600做10/12bit同目标配对；若12bit不被实际编码/原生解码支持则如实停止该分支。只研究可见/可用的编码损失，不恢复bit-exact/33点全域紧界工作。原M/旧渲染/SDR、Apple Log、原阈值和mask不改。原尺寸语义/独立global-local五路质量仍可runner推进；同帧j/WithoutFaceBoost曲线与N/B/T/V/人脸统计/allocateTone/应用域、Studio原统计、RAW2679/2408及真实HDR显示仍待实机。A_phase_complete=false、engineering_accepted=false、旧acceptance_complete=false。


### SEMANTIC-20261018 / HDR-S90：实用显示误差、亮度分层和12bit原生边界

**已验证静态：** source0a2a4fe66a63e564504926b30110a95820bb1133，预先选择S89最差IMG2600开发样本，不是新留出。只执行S89绑定的冻结S88前缀至编码前，共用完全相同S/M/H、共同offset和gain范围；新测量域是固定中性显示及相对Y分层，另试10/12bit。S/M/H三个完整文件SHA均等于S89，没有更改逆模型、Apple Log、HDR显示公式或原mask/门槛。理论gain步长分别18.25/1023、18.25/4095EV，12bit的实际质量需要原生读取，不能只凭位深宣称改善。

**已验证数值（完整固定显示，而非场景精度）。** run39435568710/xcode-27/macOS27.0.1(26A434)/image20261012.0260.1/Apple Paravirtual device。10bit原生部分完成；所有24470208像素都经原固定ACES1.0 SDR Video（cg-config-v2.2.0_aces-v1.3_ocio-v2.4、LinearP3-D65→sRGB、0EV）独立显示，再clip该显示结果到[0,1]并四舍五入到8bit，原浮点图不clip。每像素误差取三个通道绝对差的最大值，所有原误差和非正亮度计数保持。

|headroom|像素误差p99/最大（8bit码值）|差>1码像素|差>2码像素|参考边缘梯度误差p99/最大|Laplacian误差p99/最大|
|---|---:|---:|---:|---:|---:|
|1|0 / 1|0|0|0 / 1|0 / 4|
|2|1 / 2|385|0|2 / 3|5 / 12|
|8|1 / 8|222301|267|2 / 9|7 / 33|

headroom8有99.0915443%像素差≤1码，差>2码267个（0.00109112%），差>4码23个，最大8码。它支持在本固定中性预览中先按实用效果推进；不是“99%场景恢复”、真正HDR显示或无光晕的证明。边缘阈值按参考梯度≥4码在执行前固定，梯度/Laplacian是数值代理，准确最差显示位置未额外捕获。这里只报预先声明的0/1/2/4/8/16码诊断cuts，不把它们追加成放宽后的旧验收门槛。

headroom1显示对照有43个像素差1码，来自应用gain/有理数offset的浮点路径和最后显示量化比较；不能称SDR文件发生43像素变化。完整ImageIO显式SDR及CI原片/载体SDR仍逐像素0差，这与将gain权重设0后再做加减法的浮点结果是两项不同测试。三档合计804次显示输入copy/SHA检查全部相同，完整S/M/H与原生headroom输入文件SHA前后相同。

**已验证数值（相对亮度分层）。** Y来自相同P3线性目标，未作nit标定；9个固定区间覆盖全24470208像素。Y≤0有55332像素，EV无定义，保留计数/原数据，不强猜或改mask。亮度区间及正亮度有效样本的EV如下，完整中位/p95/p99/最大及实际非正数见原JSON：

|目标Y区间|像素|实际Y≤0|正亮度样本p99 EV|最大EV|
|---|---:|---:|---:|---:|
|(-inf, 0]|55332|28220|None|None|
|(0, 1e-06]|3170|1376|10.751354703903191|11.920708147898315|
|(1e-06, 1e-05]|16515|6605|6.75269896030426|7.903636657100331|
|(1e-05, 0.0001]|70892|21249|5.756123895645153|9.246730833790346|
|(0.0001, 0.001]|281456|8967|3.205891904830931|16.89030186812199|
|(0.001, 0.01]|1184087|0|0.2694609135389327|0.691433953248258|
|(0.01, 0.1]|11858899|0|0.037308493405580484|0.07641454542785496|
|(0.1, 1]|5612286|0|0.017393241822719577|0.027786682601076876|
|(1, inf]|5387571|0|0.014657451771199703|0.022057862018277613|

因此不能把全图p990.229329EV笼统当可见影调差，也不能一概免除暗部问题。Y在(.001,.01]的p99仍0.269461EV，Y>.01的三个区间p99约0.0373085/0.0173932/0.0146575EV；极大EV和符号变化主要见于更暗区。固定显示的clip/肩部会改变可见程度，实际HDR屏幕仍需独立查看。场景母版的锚点误差与相机处理未知，不能由本传输测量得出物理精度。

**已验证数值（12bit只到编码/SDR）。** pillow-heif1.3.0/libheif1.21.2/x2654.1实际写出12bit/4:4:4/matrix6，hvcC已核对；ImageIO完整原SDR仍0差。但相同原生reader的CI_present.gain=0、base/HDR/original=1，异常“Native carrier/gain image missing”，退出5，故没有12bit HDR误差或显示指标，不得宣称改善。Family4/MTL设备存在，日志一条AppleM2ScalerParavirtDriver匹配失败不能单独解释根因。范围仅限这一26A434原生路径；尚不能判为所有Mac/iPhone都不支持12bit。可另用独立12bit item原生解码与aux/tmap getter控制区分codec、辅助图选择或元数据合同，当前不是实用交付阻塞，不追half/pow末位。

**已验证静态（归档与清理）。** run结论failure因12bit原生缺gain，10bit子结果不作整run成功。原ZIP：汇总artifact12273330314/36903B/SHA09682fe2281f192e5a22e889414986cbfb3a25d737ab6314ebe6f96b504825b9；密文artifact12272895685/222155B/SHAa3d9b7b2786d5ae3affefbacec94b382132c8d2ff924c184b25f1797b5e13362。31个public成员及源/前缀绑定、GPG/私有manifest全部核验；完整12bit载体与EXR未上传或下载，只有可复现源码、文件SHA和加密contact/见证。原静态模型/原件/consumer-goto-v8保留。临时分支经全状态PR head/base无引用与源保留检查后清理，无新secret/release。

**分类边界：** 固定ACES与码值指标为已验证数值；真正HDR屏幕、同帧相机j/WithoutFaceBoost曲线及N/B/T/V/人脸统计/allocateTone/应用域、Studio原统计、RAW2679/2408仍待实机。全尺寸语义与独立GTM/LTM/semantic五路实用质量、必要时12bit直接解码控制仍可交runner。A_phase_complete=false、engineering_accepted=false、旧acceptance_complete=false；按用户新优先级停止bit-exact/33点全域紧界追查。


### SEMANTIC-20261018 / S91：日本存储闭环与原尺寸语义探针编译边界

**已验证数值（存储完整性）。** 新授权解除此前任务累计写入/下载和本机剩余空间限制，旧预算记录保留；本地Python仍用300/400MB scope，重型图像计算仍在macOS runner。已在用户日本VM的独立私有目录复制62文件/125133909B，逐文件长度和SHA全部相等；manifest SHA256为7b70c0428c2095510b408d6a222ee8d6b51e15e36c9baf5d68c4754414ba61b0。包括S5/S8和S88–S90原始密文/汇总ZIP及研究文本，不含明文人物照片或私钥。本机原件、冻结文件、历史ZIP均保留；没有为恢复空间删除历史数据。私有连接选择见工作目录hdr-native-20261019/storage-jp-20261021.json，不提交公开仓库。

**已验证静态（新探针失败，不能算逆解完成）。** source c27610d0dd63ca70f6bca4acfe7f9c9068756df5，run39474288686，xcode-27/macOS27.0.1(26A434)/image20261012.0260.1。目标是保持5712×4284主图、原c/d/GTC/guides/统计/其他matte不变，在预先由原skin matte选定的两个512×384 CI请求区域上只归零SSRFG9/10，复用一输出种子/24LM而不追格点。输入密文完整SHA和GPG已过；原尺寸consumer探针编译失败：新guard对未指定类型的id发送pixelFormat，IOSurface的OSType和Metal的MTLPixelFormat返回类型冲突（run/build.log:8–9，生成代码第39行）。这是新增诊断代码的类型错误，consumer/逆解没有执行，不得把预声明ROI或旧S82指标当成全分辨率新验证。下一版仅补显式id<MTLTexture>并换传输绑定，保留S91源码与失败。

**已验证数值（坐标预检）。** 同一原生no-orientation/unmanaged路径读取legacy skin matte为2016×1512。独立CILinearGradient坐标标尺render得到row0=0.75、row1=0.25，说明该bitmap第一行对应较高CI y；ROI选择因此在看输出/误差之前固定转换。这个结果只覆盖该原生bitmap路径，不推成所有纹理的通用朝向合同；具体人物选区坐标和matte像素只在密文里。

**已验证静态（新存储路径实际用通）。** 两份原ZIP直接保存在日本存储runs/39474288686/，HK没有复制完整ZIP或解码人物图。aggregate artifact12288922498/7033B/SHA d2531412e88bcaeb33f1f1a516b0fbbcd4b76928ea063307168792be3040d4d3；encrypted artifact12289660799/85861B/SHA f10dd43012ac55c5f33b725a0092aba7bbcab4c44bc6995e02246c58b430b2eb。provider digest、12个public成员、7份source SHA和私有GPG/2成员manifest均核验。原ZIP保留，signed URL/凭据不落盘；通过SSH流式GPG/tar SHA核验不等于在VM运行图像处理。终态+归档+PR head/base全状态零引用+源码在研究分支保留均确认后，已删除本次secret、预发布release、tag和临时分支；见closure.json。

**分类边界。** 原尺寸语义参数干预/逆解/预览仍可交macOS runner，S91没有新增这些结果。相机j最终像素EV、同帧WithoutFaceBoost/N/B/T/V/人脸直方图/allocateTone和应用域、Studio原统计、配对RAW及真实HDR显示继续待实机。GTM/LTM/semantic保持分开，Apple Log不变，旧门槛与mask不改；A_phase_complete=false、engineering_accepted=false、旧acceptance_complete=false。用户已要求按实用效果推进，停止bit-exact和33点全域紧界追逐。


### SEMANTIC-20261018 / S92：原尺寸坐标的皮肤反事实与逆解初始化边界

**已验证静态（修复范围）。** source13780b9b6bca8bf5a5ac6dcb846696664055f6bc，run39477063576 success，xcode-27/26A434/image20261012.0260.1。原S91驱动字节SHA58d3f1f6480a5ec44e37d0837c5e944b5c771f6f6b516cb8e2dbf07e6b9670f1保持；S92只替换输入计划/临时secret名称及三个id→MTLTexture显式属性类型。派生全文、逐项替换和反向还原校验见S92-binding.json、S92-derived-driver.txt，原S5/V7求解器与所有冻结模型未修改。

**已验证数值（原生控制，非整幅验收）。** 主图CI extent实际为5712×4284，未缩小；两个512×384请求区域在读输出之前由原skin matte确定。两次完整原生retained-PSO重放均half零差；texture0/11实际为512×384，guide5/6为256×192，thumbnail1分别93×70/92×70。每次只归零672B参数中offset592/596（SSRFG9/10），目标外字节差0，前后所有可读取绑定/缓冲SHA不变；GTM/LTM、其他matte、GTC和统计保持同一捕获上下文。原生色彩/亮度/联合干预分别改变half分量数如下，改变不等于真值已恢复：

|ROI|去皮肤色彩|去皮肤亮度|联合|
|---|---:|---:|---:|
|0|32729|13510|46239|
|1|57287|122625|179912|

**已验证数值（实用半强度，比较对象为同上下文的原生参数反事实）。** 复用S82定义C=y+[F0(xhat)-F(xhat)]，正RGB域内做0/.5/1的log-RGB效果强度插值，不插值Apple参数；域外原像素保留并计数。下面p99只在预声明旧eligible且原生目标算子确实改变的像素上统计，不用大面积背景稀释。0.5是预先默认值，不根据本run结果改选：

|ROI/算子|受影响eligible像素|p99 EV|最大EV|RGB相对误差>1e-3像素|选择的校正往返max abs|
|---|---:|---:|---:|---:|---:|
|0/skin-color|15010|0.0014707142731030102|0.0025865601884204757|1424|2.9802322387695312e-08|
|0/skin-brightness|5400|0.0015563610751662298|0.0020012257959694797|510|1.4901161193847656e-08|
|0/skin-both|20410|0.0014948864422152039|0.0025865601884204757|1934|2.9802322387695312e-08|
|1/skin-color|24270|0.0014733758234209732|0.006701870193684061|2420|2.9802322387695312e-08|
|1/skin-brightness|31833|0.0013903940090703765|0.002573702205791232|1761|7.450580596923828e-09|
|1/skin-both|56103|0.0014340663812284482|0.006701870193684061|4181|2.9802322387695312e-08|

联合0.5的p99约0.001495/0.001434EV，最大0.002587/0.006702EV，是有用的实用误差结果；不能称99%场景恢复或旧RGB门槛通过。全部6路0.5选择校正的往返max≤2.98023224e-8，是自选gain控制的自洽，不是完整consumer逆往返。18次固定ACES1.0 SDR Video/LinearP3-D65→sRGB/0EV预览前后输入SHA全部相同；原生输出与CI P3渲染对比均满足旧1e-5颜色域检查。预览、原始像素/参数和mask只在密文中。

**已验证数值（大残差明确保留）。** 旧一输出种子/24LM在ROI0/1的完整consumer eligible内仍有82905/75984点超过1e-3，最大相对误差1.141197443/2.465857267，覆盖率0.9631093343/0.8174591064。native-inverse.json里的full_frame=1只指512×384捕获区域，绝非整张24MP通过。上述实用效果差小不能豁免这些失败。原生反事实“恰好没变化”的像素也不保证输出完全不变：0.5最大变化在ROI0/1联合达0.0009752810/0.0014621913；这个集合含matte正值但half舍入未变的像素，不能当作严格matte外背景来宣称串色或背景零差。严格采样支持/边缘分层与完整原帧仍需runner测量。

**已验证静态+数值（排除粗坐标错位，不是全域证明）。** AIR对应source consumer-structured-v8.metal:608–619、653–660、1342：buffer5+16/+128给source0/skin11归一化affine，输出写到buffer5+160 ushort2+gid。本次两ROI实参均[1/512,float32(1/384),0,0]、输出origin[0,0]；原texture0复制重放half零差，18个预定义输入点/通道扰动都只影响同位置的一个输出，未见翻转/平移。证据不支持把大失败归咎于粗坐标错误，但这不是整个有限域、所有纹理或fast数学的全域证明。下一步检查固定旧求解器的初始化/搜索域/导数平台，属于实用鲁棒性；不重启half格点搜索，也不把“初始化落在clamp”这个尚未检验的解释写成已证原因。

**已验证静态（日本归档与清理）。** aggregate artifact12290035513/31339B/SHA b189692f3fc9a511d8515d79d6d418271b95074cb2c1da17fc98c62121b40d3c；private artifact12289627351/50786968B/SHA6cbc5de765bd6546aeb9723b4540def21fa56e2c3b674345e4f97e5d436d0c8b。两份原ZIP直接日本runs/39477063576保存，provider digest、19个public成员、原/派生源码绑定及GPG/143个private成员全部核验，HK未下载完整ZIP或解码图像。终态、PR全状态head/base零引用和代码在研究分支保留确认后，本次secret/release/tag/临时branch均清理，见closure.json。

**分类边界。** 两块原尺寸坐标ROI已验证数值；整幅、严格matte支持、求解器冷启动和更多真实样张仍可交runner。相机实际j/WithoutFaceBoost/N/B/T/V/人脸统计/allocateTone/应用域、Studio原统计、RAW和HDR屏幕仍待实机。Apple Log不变，GTM/LTM/semantic保持分开；A_phase_complete=false、engineering_accepted=false、旧acceptance_complete=false。


### SEMANTIC-20261018 / S93：原尺寸语义效果的背景/边缘验证与冷启动反证

**已验证静态（冻结与范围）。** source e8b6d0c0cbca2be151d995295851cca3f04f6910；run39480275514 success，xcode-27/26A434/image20261012.0260.1。S93只新生成一份8个预声明输出缩放种子的include，选原生前向残差最小的初值后运行原24LM；旧S5/S91/S92、LM方程、[2^-20,1.25]边界、eligible与1e-3均不改，无half格点搜索，原输入/原生neutral oracle均未充当种子。S93-binding.json、S93-seed-binding.json和派生全文给出源码SHA与精确改写。仍是同一IMG_2810、tone=+0.35的两个预选512×384区域，主图5712×4284未缩小；不是整幅24MP验证，也不是相机已烘焙语义的无风格真值。

**已验证数值（原生控制一致）。** 两ROI所有fixed_texture_bindings（含source、c/d guides、GTC、thumbnail、其他matte）与S92逐项SHA/shape/format完全相同。原生retained-PSO hydration依旧half零差；色彩/亮度试验仅改SSRFG9/10 offset592/596，目标外字节差0，前后可读纹理和缓冲SHA不变。GTM/LTM及纹理链不与语义逆变换混算，LinearThumbnail保持Apple Log。

**已验证数值（冷启动未解决完整逆解）。**

|ROI|S92→S93 eligible内>1e-3点|最大相对误差 S92→S93|mask覆盖率|真实输入eligible中超出旧搜索域|
|---|---:|---:|---:|---:|
|0|82905→83960|1.1411974430084229→0.48511019349098206|0.9631093343098959|0|
|1|75984→76477|2.4658572673797607→0.7072815299034119|0.8174591064453125|447|

最大残差下降，失败点数反而增加；不能把S93宣称为优于S92的全面修复，更不能宣布完整consumer往返通过。原texture0 copy-control仍half零差，说明这些捕获目标确有真实原生前像；ROI0真实eligible前像全在旧搜索域内，大失败不能被归为“信息已不可逆丢失”。ROI1有447个真实eligible像素含越界分量（最小负RGB），也不能用它解释其余大量失败。已排除“仅多几个曝光初值即可解决”的简单假设；尚有求解器/模型数值鲁棒性问题，具体成因未证，不伪称是matte边界或half舍入。按用户停止精度追逐的决定，保留这些失败作诊断，不继续穷举求解，也不修改旧验收。

**已验证数值（实用半强度的独立效果）。** 仍用预先冻结的0/.5/1输出效果控制及固定ACES 1.0 SDR Video、Linear P3-D65→sRGB、0EV。误差比较对象是同上下文、仅关目标参数的原生反事实；99%分位不等于99%场景恢复。以下统计不以未受影响背景稀释：

|ROI/算子|受影响eligible像素|p99 EV|最大EV|PSNR(peak=1) dB|matte边界p99 EV|
|---|---:|---:|---:|---:|---:|
|0/skin-color|15010|0.0014753247150475891|0.002422202784728692|84.15352192349263|0.0014763380239624475|
|0/skin-brightness|5400|0.0015501930141540513|0.0020012257959694797|107.24039524023881|0.0015760669701343458|
|0/skin-both|20410|0.0014948864422152039|0.002422202784728692|84.13223894549076|0.0015056128800189203|
|1/skin-color|24270|0.0014725369735496133|0.0030263999911341226|82.47399008739414|0.0014740327201307017|
|1/skin-brightness|31833|0.0013855655919181558|0.002573702205791232|101.16912026796548|0.0015548328322789174|
|1/skin-both|56103|0.0014310738019606658|0.0030263999911341226|82.41573214524817|0.0015062683870646519|

联合0.5的p99为0.001495/0.001431EV，最大0.002422/0.003026EV，PSNR84.13/82.42dB。3×3保守skin texture11支持集之外分别122846/46986像素；全部18个算子/强度组合中，估计校正和原生oracle在这些区域的最大变化均为0。这个支持集只作诊断，未用来门控输出、筛掉失败或改旧mask；结论仅适用于本次identity normalized affine上下文。边界联合p99约0.001506EV，梯度/Laplacian代理与色度差详见analysis.json和errors.csv，不能凭代理数值宣称已消除全部视觉光晕。18次预览前后输入SHA相同，两ROI原生输出与CI P3颜色域检查均合格。自选效果gain往返max≤2.98023224e-8仍只证明该控制的自洽；完整consumer逆解失败另行保留。

**已验证静态（归档与隐私）。** public artifact12291323072/42557B/SHA 3bf0872a51df44b0b259d78ccc782b4db4a7cbeeb6bb935fc197d4ff6c258934；private artifact12290718438/50777786B/SHA bf68605a1cf80ea6165cec649e57aee0b9b805e88c4d06251e31f7a17157b556。原ZIP日本runs/39480275514保留，provider digest、21个public成员、派生/种子源码绑定及GPG/145个private成员全验。私有manifest SHA144fe10263e4f8cbc6d9fb860c0851432395e489dd139076d8542f60ba1345aa。PR全状态head/base零引用、终态及代码研究分支保留确认后，S93临时secret/release/tag/branch全清理，见closure.json。

**已验证数值（用户要求减少跨区计费后的原地校验）。** 历史v1的完整cipher SSH回HK方式停止用于新run，旧receipt不改。storage/remote_artifact_store_v2.py在日本现存S93 ZIP上重做完整GPG/tar/hash认证，145成员SHA与旧receipt全同；无新artifact下载、无整包回传。HK仅收32KiB加密头，私钥留HK，归档专用session经SSH stdin/匿名fd到日本，回传19190B hash摘要、请求491B。初始头部直送GPG失败；诊断确认1KiB OpenPGP partial lengths后，只在本机缓存上去除分包长度并重封短包来取session。截断头无论GPG输出什么状态均不当作认证；完整认证只认日本端实际全cipher的GPG returncode0、DECRYPTION_OKAY/GOODMDC及全部manifest。初始排错合计约102081B数据payload（不含SSH命令/开销和其他API元数据），正常已安装工具的本例约52543B。日本helper/GPG峰值RSS34304/17488KiB，未解码图片或落地明文成员，临时GNUPGHOME已清理。工具不自动回退整包传输，遇未知头格式先诊断。证据transfer-local-verification.json、transfer-policy.json；此为传输验证，不增加图像样本数或场景精度证据。

**分类与下一步。** 两个ROI的语义效果/支持集/固定预览已验证数值；整幅流式实用校正、更多照片与独立保留样本仍可交macOS runner。相机j权重上限β=0..0.1953125仍不能换成实际像素EV；相机同帧曲线/统计、Studio原统计、RAW配对和真实HDR屏幕只能待实机，预览幅度继续标“假设”。A_phase_complete=false、engineering_accepted=false、legacy acceptance_complete=false；本轮未重启bit-exact/33点全域紧区间追逐。


### SEMANTIC-20261018 / S94：整幅语义原生基准的观测入口失败（不冒充像素验证）

**已验证静态/数值（运行边界）。** source bf117dccb793e2ceaaff85b5e2ee9a368cd54353，run39486436418 failure，xcode-27/26A434/image20261012.0260.1。Objective-C编译成功，CI原图解码确为5712×4284、24470208像素、RGB非有限0，LinearThumbnail保持原Apple Log入口；但没有捕获目标final dispatch、没有整幅语义或whole/patch像素指标。native.log只证明输入可解码，不证明前向通过。

**已验证静态（失败定位）。** semantic_fullframe_s94.m的Process94仅在找到满足texture13/11/buffer1的dispatch时才创建子目录；随后的native-calls.json写入却无条件执行。首个内部调用没有该匹配项，父目录未建立，写日志异常被原PISemanticStyleFilter记录在trial.exception，中断后续实际处理。driver.log随后因没有native-calls.json失败。不能把这个探针自身的异常归咎于半精度、matte、不可识别性或苹果不支持大图。后续新版本应在process入口建立本次capture目录，记录所有内部dispatch/绑定的census，再据真实final allocation决定分块比较，不改原PSO或数学。

**已验证静态（运行前定义的门槛与另一个未执行缺陷）。** inputs_s94.json/source commit预先定义新的工程whole/patch判据：maxabs≤1/256、PSNR≥70dB、固定ACES的99%像素各通道差≤1码、最坏≤4码、非有限0；旧half逐位、float1e-5/PSNR60和逆1e-3仍独立保留。S94没有到达这些判据，不得记通过。另在静态复查发现预览stride8给536×714=382704像素，超过冻结S82 apply的262144像素上限；该分支本run未执行，不能把它写成观察到的失败。新派生版本改成stride10（429×572=245388），原S94与S82文件保持。

**已验证静态（低流量归档与清理）。** public artifact12294260940/11387B/SHA e07678bd850e277f22d7dd7ec0030960156df3da0d6bd63ccbbe4c554ed6fdab；private artifact12293452567/8615B/SHA3bb63fdf731b2d088d392358cb8c2ec6c510d0e1ef1332258bc105444b03cf16。原ZIP日本保留、10 public与GPG/11 private成员全验；本次secret/release/tag/临时分支已按PR零引用/终态/源保留规则清理。首次实际新run已使用日本原地完整GPG/member核验，HK未接收完整ZIP或大密文。注意这份cipher仅8465B，小于32KiB头部上限，所以“头部”包含整份小cipher；旧v2 receipt的whole_cipher_or_ZIP_backhaul_bytes=0不能按字面当作它的字节数。原receipt不改，精确解释/计数见traffic-accounting-correction.json；后续协调器分开计完整小cipher与大cipher流，不隐去这8465B。

**分类。** 探针编译/原图CI解码/错误定位/归档已验证；整幅native final allocation与语义控制仍可交runner，尚无新图像结论。只修证实的观测入口与预览分块上限，不重开bit-exact。实机j曲线/统计、Studio/RAW/实屏清单不变；A_phase_complete=false、engineering_accepted=false、acceptance_complete=false。


### SEMANTIC-20261018 / S95 准备与 S94 推断边界更正（排队观察）

**已验证静态（更正HDR-141的局部推断）。** S94日志实证是native-calls.json父目录不存在导致写入异常。原源码把mkdir放在匹配dispatch的分支内，但原catch也可能先吞掉目录创建失败，随后触发相同的JSON写入错误；所以“首个内部调用零匹配”还不是有直接计数支持的事实。此前S94段落/HDR-141中的这处更强解释收回，以本补充为准；已证的观测目录错误、无final像素结果、原尺寸CI解码和归档清理结论不变。源码分支与未排除路径见evidence/s95/static-assumption-audit.json，原日志与receipt字节均保留。

**已验证静态（新源冻结）。** S95 source475e050dc0a4fd7fc30528c9bf9a65d875129596只派生修复：先建观测目录；记录所有内部调用的原返回/真实dispatch数/绑定state数，明确state fallback不是dispatch；预览stride10满足冻结S82的262144像素上限；最多分配一套整幅基准，额外上下文仅记census。精确全文改写与SHA见s95_observer_binding.json。原S94/S82、数学/采样器/PSO与旧门槛不改。仍先要求全原件5712×4284实际分配与原生对照，不用两个ROI冒充整幅。

**可交给macOS runner（正在排队）。** run39488329547/job118854512641、xcode-27；queued-observation.json的时间点job未分配runner，尚无该run实际OS镜像或像素结果。不要拿API started_at字段当成已开始计算。独立监看进程已启动，只观察这个run，终态后在日本保存原ZIP并做完整GPG/member核验，再清理本次secret/release/tag/分支。v3把≤32KiB小cipher整包落在头部内的字节显式计入，保留无大包回传策略。排队不是新的原生失败，不重复派发或退到不同build制造结果。

当前A、engineering与legacy验收均false。整幅语义实用逆估计/跨照片验证仍是runner工作；本次只准备其原生参照，不声称已逆掉原拍摄语义。相机同帧j/WithoutFaceBoost、N/B/T/V/face hist/allocateTone/应用域、Studio原统计、RAW与真实HDR屏幕继续待实机，沿用既有可执行清单。


### SEMANTIC-20261018 / S95 结果：大图在 final 之前返回−12786；黑输出不能算成功

**已验证数值。** run39488329547/source475e050dc0a4fd7fc30528c9bf9a65d875129596，26A434/image20261012.0260.1，failure；前一“排队观察”只记当时时点，此处为终态。目录修复生效，真实记录到4个CMISmartStyleMetalRendererV1 process调用，每次4个actual dispatch，共16个，均非bound-state fallback；4次原process都返回−12786，目标final dispatch为0。main纹理依序为2856×2144、2856×2140、2856×2144、2856×2140，guide为1428×1072/1070，thumbnail为512×385/384。尚未抓CI output.region，不能把四次调用直接证明为无重叠2×2覆盖；它们也不支持强求一个5712×4284物理纹理的前置假设。下一版必须按真实CI owner region组装同一整幅照片，不缩小原像素覆盖要求。

原命令行程序最后返回0，但CI renderer.f32的min/max/mean全为0，实际原CMI方法已返回错误。这是**无效黑输出**，不是前向通过、SDR身份、完整native往返或可用预览。原图CI解码仍非黑且非有限0；native child峰值RSS1236320256B，并无本run被系统OOM终止的证据。错误位置已从探针写目录推进到原生final之前，仍不能凭数值−12786直接给原因命名。S94当时的零匹配计数未记录，S95新计数不回填S94历史。

**已验证静态（资源错误路径，尚非runtime归因）。** 本机既有26A434 CMImaging文本、UUID3CCD434E-B1E0-3F14-8EF6-E29D58379BE8、binary SHA40868a2bc375526c2de6f378c2012420e91830bdb9e16e4cbb20662822b11c3e已绑定。constructor initWithMetalContext在context未提供allocator的分支于0x233369ef8请求0x9000000=150994944B主池，调用点0x233369efc/返回0x233369f00。CMIGuidedFilter encode在0x233363bf4/0x233363c10以−12786返回，相关分支含nil临时coefficient纹理或encoder；cold字符串明确包含coefficientAMeanTexture/coefficientBMeanTexture。原文行号与完整SHA见allocator-and-guided-error-source.txt、static-provenance.json。这只支持资源假设，不能证明S95恰好走这个callee或同一pool。S41先前通过2GiB caller-supplied池运行全尺寸原host，是可复用的原生前置经验，不是S95当前状态。

**假设/可交runner（下一实际对照）。** 先绑定CMIGuidedFilter实际返回/radius/epsilon及allocator descriptor/原请求，复核loaded UUID与构造器callsite。若只改变已证主池容量，保留资源类型/flags、所有图像参数、PSO、采样器、c/d、GTC、guides及统计；记录每项实际值，不凭感觉改eps。四个并发CI上下文须核内存，不能盲目各给2GiB超7GiB runner。捕获外层PI output.region、原点与实际输出纹理/ROI，禁止上传未知padding；再将各合法owner region的native RGB与CI整幅缓冲比对，并做同一上下文内的512×384子块对照。采样仿射移位有AIR依据，浮点差异仍数值报告；旧门槛不改。原来单物理全帧假设不再作为fake gate，实际验收仍覆盖5712×4284全部像素。该工作仍是原生前向参照，尚未构成全尺寸语义逆变换。

**已验证数值（归档/清理与准确流量）。** public artifact12294729886/14380B/SHA d437a6675d1f375d24484b8e1e5d8bf697b1663e6f591921ca7f7c56f8c30811；private artifact12294879502/9536B/SHA9e0af37ad65d53db290e216fd6a16c24cbecea94f76b19b33112b43d9b673491。原ZIP直接日本，13 public及GPG/13 private成员和源码精确改写全验，私有manifest SHA0d20b893a54f58d3d4c872af67755f56d9c12bad88be8c0e2163b09c2eec354b。本次v3明确计入9386B完整小cipher（处于≤32KiB头内），请求483B、hash摘要2671B；完整ZIP回传0、大cipher body回传0，未重传旧大归档。终态/PR零引用/研究源保留后，secret/release/tag/临时分支已清理，见closure.json。旧S95-active/queued观察是历史时点，terminal记录已另增，不覆盖。

A_phase_complete=false、engineering_accepted=false、旧acceptance_complete=false。整幅实用语义逆估计、与global/local分开组合和跨照片仍可runner推进；相机同帧j四曲线/N/B/T/V/face histogram/allocateTone/application域、原Studio统计、配对RAW和实屏继续待实机。这里没有新的HDR效果或物理场景精度结论。


### SEMANTIC-20261018 / S96：探针编译输入错误，尚未执行像素算子

**已验证静态/数值。** run39496980234/sourcec735ecbbb000426d676eea20a575718f3fe2f8e0，macOS27.0.1/26A434、image20261012.0260.1，终态failure。run_semantic_s96.py:56误把observer/capture include、binding JSON及旧semantic_fullframe_s95.m一起传给clang；旧translation unit要求native_filter_probe_s95.m，而本run只生成S96 include，build.log:1–4报fatal include missing。driver在编译assert处停止，没有native-calls或像素结果。不能据此判断512MiB资源前提、PI owner矩形、整幅参照或语义效果通过/失败。下一版只改driver的构建输入及传输标识；复用冻结S96 native/TLS/observer源码，像素/采样/阈值不变，并在提交前用AST断言编译列表仅有一个.m translation unit。

**已验证数值（归档/清理）。** public artifact12297668691/15258B/SHA a0ccf1c83bcd0155ab8d04031777bfaf74b296e92c6d14a3cc839f504b742ad3；private artifact12297814046/816B/SHA531c7d09ce75dc04a0653d5d5adc75f5cb90eb558d0ad2e418b18c0117f1a7d3。原ZIP直接GitHub→日本，10 public成员及GPG/1 private成员校验通过，private manifest SHA4dc2e7808aac750ec11d3f1c329d95d410eba16a096052b5ab6bae16d746da25。香港仅收到666B密文头（此次包含完整小cipher）、481B验证请求对应的1221B hash摘要；完整ZIP/大cipher body跨区回传0。终态、PR head/base零引用、研究源保留后，该run的secret/release/tag/private分支已清理。不得为补文档再下载旧大归档。

**指标解释边界（静态审阅，尚无新像素值）。** S96继承的regular_tile_boundary_gradient统计的是全图512×384规则网格，实际subpatch从各CI owner内部重新起格，故不能把它称为所有实际接缝的平均误差。覆盖全部相邻像素的gradient_error_max在有限路径下仍是任意接缝子集最大误差的上界。后续逆估计应先由owner矩形和各局部网格声明真实接缝mask，再看输出；不修改冻结S96定义或借此改变门槛。详见metric-scope-notes.json。

A_phase_complete=false、engineering_accepted=false、legacy acceptance_complete=false。没有新增99%场景恢复或完整语义逆解结论。既有global/local/semantic分离、Apple Log、mask及实机清单不变。


### SEMANTIC-20261018 / S97：整幅24MP原生参照闭合，分块达到预声明实用门槛

**已验证数值（原生前提）。** run39499003223/source5f8646db52be89d09563f922a369900aee056081，26A434/image20261012.0260.1，success。S97仅修正driver构建输入和run标识，native、observer、TLS、采样和像素算法与S96完全相同，精确替换表/源SHA见S97-driver-binding.json和S96-observer-binding.json。loaded CMI UUID3CCD434E-B1E0-3F14-8EF6-E29D58379BE8；allocator setter ABI v24@0:8Q16、guided ABI i60@0:8@16@24@32@40Q48f56、PI ABI B48@0:8@16@24@32^@40均实际核验。

只在已证constructor返回点IMP+0x12c命中一次144MiB→512MiB容量请求，另一个46080B请求保持原值；4次process在同一renderer/线程顺序执行，实际allocatorType=2、memSize=536870912。4次原process均返回0，每次17个actual dispatch，共68；16次guided均返回0，r=1，其中8次RGB投影eps=0.0010000000474974513、8次scalar c/d eps=0.05000000074505806，不能把二者混成同一个eps。native child峰值RSS1553530880B。此配置证明原生前提可运行，不能把512MiB称为Apple生产默认值；与S95间还有观测实现差异，未做同版单因素A/B，不把S95历史错误反填成已证耗尽根因。

**已验证数值（完整原生参照）。** CI output.region依次为(0,0,2856,2144)、(0,2144,2856,2140)、(2856,0,2856,2144)、(2856,2144,2856,2140)，4块严格覆盖5712×4284=24470208像素一次，空洞/重叠均0。按预先冻结的CI-y→bitmap行规则组装，捕获原native与完整CI P3缓冲RGB max abs=0、非有限0；4块原PSO hydration RGB half差分量均0、所有原纹理/参数SHA前后相同。已摆脱“单个物理全图纹理”的错误前提，同时完整原像素覆盖要求不变。

**已验证数值（目标参数反事实，非拍摄端已烘焙逆解）。** Tone=+0.35固定上下文，仅清零field9/offset592（0.503125011920929）或field10/offset596（−0.22238825261592865），其余参数字节差0，c/d、GTC、guides、统计和其他matte所处绑定保持不变。整幅skin-color、skin-brightness、skin-both分别改变276785、499250、776015个half RGB分量；最大绝对变化分别0.0771484375、0.0079345703125、0.0771484375。它们是参数中和的真实原生效果，不是像素误差，也不是证明Apple拍摄端实际幅度已识别。保留4种全分辨率half输出和统一ACES的50% oracle效果预览；preview输入SHA共280次均不变。

**已验证数值（整幅分块的实用效果）。** 每种operator都比较同一owner原native参照与512×384分块，4种输出均覆盖24470208像素。original/skin-color分别83个、skin-brightness/skin-both分别82个half RGB分量不同；max abs均0.00390625，PSNR分别122.3956733912/122.3952955796dB。固定ACES1.0 SDR Video、Linear P3-D65→sRGB、0EV、config SHA5aefc668796eabb1902b9593340496231758eceaec18ce290e12901042bd4440：p99码差0、最大1码、大于1码像素0。Yref>1/255且正有限的EV域n=23288907/23288750，排除1181301/1181458像素，p50/p95/p99均0，max=0.0040851543EV。非有限0，全部相邻像素亮度梯度残差max=0.0019464351，它是实际接缝子集最大值的上界。规则全图网格统计为0仍不能当作实际CI/局部patch接缝均值，见S96 metric-scope-notes。新实用patch门槛全部通过；旧float与half门槛仍false，不追这82/83个残差的bit-exact。此处比较的是重放几何误差，不能改称完整语义逆解或99%场景恢复。

**已验证数值（日本归档与流量）。** private artifact12300720827/319567324B/SHA684f8a43a4946fdb5d0ae323509cbba1cc30d067cfa9f9f64125623749fad92d；public artifact12299419596/57240B/SHA3c9760c3c405f59553991e390c6232d4c13840806f03277e52e567c6767dde92。319624564B原ZIP直接GitHub→日本，19 public与GPG/70 private成员校验通过，private manifest SHA275336113ded61a47a4047060b97079a91c0245527ace4505ec37e74c6c09cb5。香港收到708170B未压缩公开成员文本（Base64/manifest/SSH开销另计）、32768B密文头与10944B私有hash摘要，验证请求493B。完整ZIP/大cipher body跨区回传0；头部GPG rc2只用于提取session key，真正认证为日本端完整GPG rc0及所有成员SHA。不能把私有verification子项“new_download=0”误读成整次没有GitHub下载。没有人物明文回传/上传，没有移动旧S5/S8等大归档。PR零引用、研究源保留和校验后，S97临时secret/release/tag/分支已清理。永久传输规则见storage/TRANSFER_POLICY.zh-CN.md。

**可交runner（下一步）。** 现在可在已闭合的整幅原生参照上推进保守语义逆估计，按真实owner/局部patch建立实际接缝mask，单独报告估计对原生中和效果的EV/ACES/色偏/边缘误差、旧往返失败及不可识别mask；不得把已知原输入当作反演seed，也不能把旧参数反事实当成去掉已烘焙语义的真值。原global/local分开输出、Apple Log、固定ACES与原SDR max0要求继续保留。新整幅native参照通过不等于整幅inverse通过，S97没有执行inverse，A_phase_complete=false、engineering_accepted=false、旧acceptance_complete=false。

同帧相机j/WithoutFaceBoost曲线、N/B/T/V/face histogram/allocateTone约束与应用域、原Studio统计、IMG2679/2408配对RAW、真实HDR屏幕/Photos UI继续待实机；不以Gain Map承载自洽替代scene-referred物理精度。


### SEMANTIC-20261018 / S98 测试前状态：整幅条件逆估计已冻结，尚无结果

**可交给macOS runner（已触发，非通过结论）。** source1165f8a074c3b5118cae776c61e0b2f945247687，run39504949862，branch research/vm-native-20261021-semantic-s98；2026-10-20T22:17:47.302750+00:00从GitHub观察为queued。OS目标26A434/xcode-27，实际镜像版本尚未观察，不能沿用S97值当作已证。此条是带时间的历史观察，后续看本run终态/归档，不把旧queued marker当持续运行或失败证据。监测入口无自动native重试，终态后先读失败日志、在日本校验原ZIP与完整GPG/成员SHA，再按PR零引用/源保留检查清理本次临时secret/release/tag/分支。

原S93求解器SHA23fff931a0914e5956ccee79bc715ee60ecaff936658ea2f9e2fdf1a218f92e0保持不变：8个仅由观测输出导出的尺度seed、24LM、旧[2^-20,1.25]范围、原RGB-eligible mask和1e-3；不进行半码格点或全域紧包络追查。按S97实际CI owner运行全部像素，每块输入/输出形状必须相等且不超过7M像素，最终全24470208像素覆盖一次。无新512×384采样变换，不重做S97分块benchmark。原输入只用于复制对照和事后域检查；运行记录还须核对own_previous_recovery_seed。潜变量输入不称scene-linear母版。只中和皮肤592/596，其他c/d、GTC、guides、统计、参数/matte绑定保持同一上下文并SHA。

测试前独立实用门槛：整图及“native neutral != native original”目标作用区域的p99EV≤0.01、固定ACES的p99像素RGB最大码差≤1；整图max≤4码、非有限0，strength0身份差0。0.5为选定保守效果，1为幅度敏感性。目标作用区域只是诊断/验收区域，不是matte、旧逆mask或输出门控；旧1e-3失败独立保留，不把p99改称99%物理恢复。输出分别为色彩、亮度、联合的全分辨率half RGB log2校正Gain Map和ratio-valid mask，量化与逆估计误差分开报告；实际CI owner接缝全量测量，不再用规则网格proxy代表接缝均值。完整预览SHA账本留日本密文，香港只取count/通过状态/SHA。统一ACES配置/曝光和Apple Log不变。当前无新ImageIO载体，因此不新增SDR max0通过声称。

**已验证静态/数值（现有交付边界审阅，无重跑）。** S89 run39430695395确有5张、2张encoded-integration留出、全部原生SDR max0，但其phase-summary明确new_full_carrier_master_archived=false；S90也明确full_carrier_or_master_archival=false。S88的full目录只拷一份carrier、旧mask和meaning JSON，记录master hash并不等于该目录交付了master EXR。S42写出both/master，local-only虽原生运行/预览、global-only虽全图计算mask/预览，当前selected writer没有各自独立的完整结果文件。原假设状态不变，不能把这些边界解释为物理恢复成功或算子失败。后续还须保存完整的五套载体/母版与分离结果，不拿已有hash替代实际文件。S88/S89本来就用1023级10bit444/matrix6；不得误写成S89仍是8bit或新10bit配置只测一张。S90的12bit provider nil无须再追。留出IMG2608/0033只针对冻结后encoded integration，曾用于旧研究，不冒称从未看过的或RAW物理留出。

仍可runner推进：本次整幅语义逆估计的真实结果、原生参考下误差/色偏/接缝/域mask评估，以及冻结配方完整文件留存/分离输出和HDR组合。只能实机的同帧j/WithoutFaceBoost四曲线、N/B/T/V/hist/allocateTone/app域、原Studio统计、RAW2679/2408和实屏按原可执行清单。A_phase_complete=false、engineering_accepted=false、旧acceptance_complete=false；尚未得新像素结果，不给errors.csv填占位零值。

S98 strength是输出log-RGB差分插值，不等同Apple UI Tone。Tone固定+0.35用于本次条件语义测试；本轮不改变GTM/LTM上下文，也不把恢复潜变量命名为场景母版。


### SEMANTIC-20261018 / S98 终态：整幅条件皮肤效果达到实用门槛，实际拍摄端语义仍有边界

**已验证数值。** run39504949862/source1165f8a074c3b5118cae776c61e0b2f945247687，26A434/image20261012.0260.1，success。四个真实CI owner覆盖24470208像素一次，native/完整CI RGB max0；每块完整执行原S93逆估计，effective half重放差0、原纹理/参数SHA不变，实际own_previous_recovery_seed均0。native child峰值RSS2141175808B，重计算全部在macOS，香港只做受限内存的元数据核验。原S93 solver/bounds/旧mask/1e-3不变。


run 39504949862，source 1165f8a074c3b5118cae776c61e0b2f945247687，image 20261012.0260.1。

状态：已验证数值，仅固定上下文consumer效果估计。不是拍摄端已烘焙语义恢复证明。

| 目标算子（0.5） | 作用区像素 / EV有效数 | 作用区 p99 / max EV | ACES 全图max码 | 全图PSNR dB | 真CI接缝max/mean（线性Y残差梯度） |
|---|---:|---:|---:|---:|---:|
| skin-color | 135930 / 135930 | 0.0013876280 / 0.0125287194 | 1 | 96.531448 | 0.0007779315638 / 2.391390806e-06 |
| skin-brightness | 187760 / 146671 | 0.0021920004 / 0.1131939515 | 1 | 111.047280 | 0.000188416132 / 7.808608705e-07 |
| skin-both | 323680 / 282591 | 0.0016765019 / 0.1131939515 | 1 | 96.380678 | 0.0007779315638 / 3.172250755e-06 |

B=F(X)，X是本次原照片解码后送入native filter的输入，Tone固定+0.35。Xhat由B求解；计算D=F_neutral(Xhat)-F(Xhat)，C=B+D；正有限RGB域输出Q=B·exp2(strength·log2(C/B))，其他像素保留B并记录mask。参考是同一上下文下原native输入生成的参数中和效果。原输入/neutral oracle没有作为seed。

交付loggain以B对应的native.f16为baseline，不能直接乘原HEIC SDR并声称去掉了拍摄端语义。latent Xhat也不是scene-linear母版。native_effect_active只是参考中和确实改变像素的集合，不是matte或新逆mask；零效应区实际最大变化非零（≤0.000977278），不可说背景逐位不变。

旧RGB-eligible mask覆盖0.9443835540752249，8327939点超1e-3，max relative0.7113556778389195。215289个原输入分量落在旧box外，该计数不是像素数，也不能解释全部失败；未把未收敛点归为信息丢失。旧失败保留，不继续为bit-exact重跑。

0.5三个实用gate均通过；1.0敏感性也通过预声明实用gate，ACES max3/2/3、作用区p99 EV0.002775589/0.004322484/0.003340014。仍维持预先选定的0.5，不根据结果更改默认。brightness/both的EV尾部max0.11319（全强度0.21814），近黑等排除仍如表/JSON报告，不能用全图p99零掩盖。

half loggain传输与逆估计分开：色彩max gain误差0.0000305065EV、亮度/联合0.0009749993EV；对应RGB绝对误差max≤0.00001347065，ACES量化差max1码。输出本身已含该half传输再与oracle比较；不是只验证未保存数组。

12个完整校正map及12个mask的大小/SHA逐项与已认证私有tar对上；全部native reference、恢复effective half、estimated-neutral、roundtrip/residual/old mask仍在日本密文。3271组预览输入SHA全部不变，私有账本SHA abd402f083db598219f2e8416543075b78c828f026917404b0c037f4084a083e。

776092602B原ZIP直接GitHub→日本，22 public/GPG167 private全验。香港读306197B公开成员（编码开销另计）、32KiB密文头和26584B摘要；无ZIP/大cipher body回传。临时secret/release/tag/分支清理已核对。

继续可runner工作：连接真实revert-image/原照片处理域，验证适用于实际原片的独立语义撤回及全分辨率matte边界；完整五套母版/载体与global/local文件留存、HDR组合。仅本次条件测试通过，不宣布A完成。相机同帧曲线/统计、原Studio、RAW和实屏仍待实机。

**已验证数值（归档身份）。** private artifact12304682191/776048869B/SHA af4026a8401bdf63eb2886c8ad0da0ad18ceb55fed4a8d5e8014c68fca90646f；public12303818883/43733B/SHA cb95c0b9ca1af80857c9de49fa0c2656791a41c87a32d9f952095d2dc5b26f2a。cipher SHA dc3f8e0619c1e30bb013cbfbe9d966145caf6abfdeb09eab4a64c470e6ab6980；private manifest SHA46236cfde047e9bf343e44237d24bd4df766222524589ca270b86c90f3f7c4f6。完整GPG rc0及所有成员核验在日本，截断头GPG rc2只用于取session key，不能冒充认证；SHA原件保留。旧queued观察不覆盖，新增terminal记录为后续依据。A_phase_complete=false、engineering_accepted=false、legacy acceptance_complete=false。


### SEMANTIC-20261018 / S99 终态：调用前提失败，未产生新像素结论

**已验证静态（调用错误定位）/可交给macOS runner（修正后验证）。** run 39513947146，source 3936cb99f172df2a7a5f47645cf7e2b3df92cba3，26A434/image 20261012.0260.1。两个clang编译均成功；driver只在RES提取metadata/linear/delta，却把尚不存在的SRC传给冻结source_s37。Styles_full_v3.m:146起从该dir读styles.plist、linear.heic、delta.heic；缺资源触发失败，外层catch再向不存在目录写source-exception，最终日志只呈现“Cannot write S37 source facts”。这是探针调用前提错误，不能解释为Apple算法不可用或任何像素门槛未过。实际三个图像case均未执行，没有新图像误差，errors.csv不填占位零。

失败日志已先读：evidence/s99/run/source-native.log、driver.log、source-build.log、native-build.log；修正只在新driver中向新SRC执行extract(photo,SRC)，按已有S42/S89显式设置VM_DISABLE_RESIDENCY_SETS=1兼容前提，不动冻结源或pixel算法。后续另开有证据的单run，保留本次归档与分支中的源，不盲目重试。

原ZIP直接GitHub→日本共19904B。public13、GPG private1成员全部认证：private artifact12307091071 ZIP SHA44e56bbfa3a796c66d9fdfba9fd44016e967de4e477a6ea09d2c4069e725cf74；public12306776240 SHA3209294d61596a1509650bfb237e006e4811903f6fbe2a34b23014be07576d7d。671B小cipher全部落在bounded header里，准确计作671B小密文回传；无ZIP或大cipher body跨区回传。PR head/base引用0、源保留后，本次secret/release/tag/private branch全部清理。A/工程/旧acceptance仍false。


### SEMANTIC-20261018 / S100 真实 key1 输入域衔接：测试已启动，结果待审阅

**可交给macOS runner。** run 39514608080，source e9a93b09f0c814dce6816e60b0bc2f274db4cb35，branch research/vm-native-20261021-semantic-s100，2026-10-20T23:25:06.555873+00:00 观察为 queued。这是带时间的历史状态，实际结果以终态归档为准；尚未观察的主机build不能当作已验证26A434。

本次先修正已归档S99的SRC资源前提错误：先extract(photo,SRC)并比对styles/linear/delta的SHA，冻结source入口沿用S42/S89 VM_DISABLE_RESIDENCY_SETS=1兼容前提，源文件和S99 native/analysis字节均不改。S99失败run39513947146已先读日志、日本认证归档并清理；这不是盲目重试。随后解决S98的使用边界：S98以B=F(S;Tone+.35)为baseline，不能直接把校正map乘到原HEIC S并宣称撤回拍摄端处理。S100调用冻结source_s37.m/Styles_full_v3.m，max_edge0获得苹果实际key1逆风格图R，native half存储再精确widen为f32，分别观察F(S;Tone0)、F(R;Tone0)、F(R;Tone+.35)。三个case的native guides可随主输入重算；每个case内部中和field9/592、field10/596时，其他纹理、c/d、GTC、guides、统计和参数保持同一绑定并SHA核验。没有新的求解器、格点搜索或分块benchmark。只测这条显式构造链路，不能据此宣称Photos UI实际顺序，R也不是scene母版或已隔离的皮肤逆变换。

即使Tone0完全跳过CMI最终dispatch，也写census并比较实际完整CI输出与输入；无调用本身不证明恒等。有dispatch时需完整owner覆盖和native/CI误差检查；只保存已知初始化范围的texture11 R16与176B ROI。原始texel格不能冒充内部实际采样的matte，更不能据此虚报背景零变化。全部预览使用同一固定ACES1.0 SDR Video/Linear P3-D65/0EV，并核验预览前后输入SHA。

传输只复用原2.56MB密文；无旧S5/S8/S98大包重传。新原ZIP直接GitHub→日本，完整GPG/所有成员校验留在日本，香港只取小型cipher头、hash及公开汇总。人物像素只加密上传，artifact保留1天，完成归档后核PR零引用/源保留再清本次临时资源。A、工程、旧acceptance均false，尚无新照片指标，不填errors占位值。


### SEMANTIC-20261018 / S100 终态：真实key1输入链路、Tone0与皮肤新编辑的边界

# S100 真实 key1 输入域与 Tone0 行为
run 39514608080，source e9a93b09f0c814dce6816e60b0bc2f274db4cb35，26A434 / image 20261012.0260.1。状态：已验证数值，固定探针上下文。
| 输入 / Tone | 与自身输入的RGB max差 | 自身输入对照p99 EV | ACES max码 | 皮肤色彩 / 亮度 / 联合改变像素 |
|---|---:|---:|---:|---:|
| original-tone0 | 0.06893217564 | 0.4176386297 | 23 | 0 / 0 / 0 |
| key1-reverse-tone0 | 0.07080078125 | 0.4263626933 | 23 | 0 / 0 / 0 |
| key1-reverse-tone035 | 0.353515625 | 0.64402771 | 69 | 128324 / 178433 / 306749 |

这些差值是consumer输出与它自己的输入比较，属于处理幅度，不是逆解误差、scene精度或F(R,0)与原片S的往返误差。没有重新跑逆解，也没有新ImageIO/SDR载体测试。

Tone0两case内field9/592与field10/596都已是0，三个参数中和的原生效果全0；但整个consumer明确非恒等，不能把Tone0视为无local或无处理。R+.35时9=0.503125011920929、10=−0.22238825261592865；仅目标字节改动，其他参数/纹理/cd/GTC/guides/统计逐owner保持原SHA。

实际native key1 R来自冻结source_s37/Styles_full_v3，max_edge0，5712×4284；native half后精确widen f32，没有新曝光或tone操作。R捕获数值范围[0,1]，这本身不证明是哪一算子clamp，也不能当scene master。原生反风格配置12×9、8planes、sigma2.5、ColorSplit false，属于本次实际configuration，不扩展成未证的语义分解。

三个case各4个真实CI owner，24470208像素完整覆盖一次；12个原生PSO重放hydrate half差0，native/CI RGB max差0，上下文SHA全不变。每case skin11完整raw R16共869043正texel、23601165零texel；它是原始绑定格，不是内部精确采样matte、语义支持集或背景零变化证明。

setDefaults后useStyleEngine实测false（本次仍显式设false），inputCast保持默认nil，inputColorBias0，不能声称这等价真实Photos UI恢复全部原编辑设置。F(R,0)和原片S的完整像素直接比较尚未测量；不能用各自均值接近代替这个比较。尚不能把S98以B=F(S,+.35)为基底的校正图直接乘S，也不能把本次皮肤反事实解释为拍摄端已烘焙因子。

统一固定ACES1.0 SDR Video / Linear P3-D65 /0EV，819次预览前后输入SHA全部不变；3.75MB预览只在日本密文，未回传人物明文。完整native R/S半精度zlib、12owner参照/中和输出、raw skin/ROI/参数均已在日本GPG206成员认证，非只存哈希。

原ZIP GitHub→日本577462229B，香港只取公开成员549144B（编码开销另计）、32768B密文头和30993B摘要，无整ZIP或大cipher body回传。临时secret/release/tag/private分支在PR零引用/源保留后全部清理。私有ZIP artifact12308091275 SHA6940dfa84d0d3d4dfc9b05eb1318d9c889612dcc997352906012fbf6a2db1655，内cipher SHA816577f7767420cef7679e8d98df1621edd43bc0554444b3dce9d8aed2d3751d，manifest SHA14ce46f85bf834089bd795d606defc2f564428bdf7fba41ff35fef567c3b088f。

下一步仍可runner：直接测F(R,0)与原片S并定位零Tone非恒等的处理域/配置，不能先假定UI顺序；按原条件保留语义反事实。完整母版/载体与global/local的IO保留器已在workspace准备（未运行），不拿代码准备替代文件交付。真实拍摄端语义分量、同帧j四曲线/N/B/T/V/hist/allocateTone/app域、原Studio统计、RAW2679/2408和实屏按原清单待实机。A、工程、旧acceptance仍false，不再追bit-exact/33点。


S100补充（已验证数值，汇总下界推导，未重跑）：同一raw线性P3画布中，原片S的RGB全局max=1.2321066856384277，显式consumer F(R,Tone0)的全局max=1.037109375。因此max|S−F(R,0)|≥|max(S)−max(F(R,0))|=0.19499731063842773。这是严格必要下界，不是实测最大误差；当前显式配置（inputCast默认nil等）无法满足旧float maxabs1e-5，无须为了判定这一点再抓像素/追bit-exact。它没有定位见证像素是否落入旧RGB-eligible mask，也不能推导p99、99%实用效果、亮度EV或实际Photos UI是否等价；这些结论仍未测。均值接近不能代替实际往返。见evidence/s100/tone0-bridge-bounds.json。


### SEMANTIC-20261018 / S101 交付补齐：完整文件保留已冻结并执行，尚无终态结论

**可交给macOS runner。** run39518274902，source90d565c7686cd45f55e1d1e4e5fd9b0f6af31ef7，branch research/vm-native-20261021-hdr-s101；2026-10-21T00:04:55.444596+00:00观察为in_progress。这是带时间的观察，实际build/image须终态归档复核，不从runner标签直接推定。一次API轮询失败只停止了旧监测器；已重新确认同一run实际in_progress，恢复观察，没有重启native或排第二个job。

补的是先前selected S89/S90只留contacts/hash造成的完整文件缺口。原S42计算插入一条local v保存调用，移除它后AST完全恢复；原master EXR必须匹配旧SHA。global-only沿用原GTC逆假设，clamp/plateau/nonfinite flags与NaN保留，不猜缺失值；local-only沿用native RGB thumbnail projection候选。二者均在共同native key1逆风格R后计算，不能改称原片S上的纯GTM/LTM生产端逆解。原S44/S47显示意图及S88/S89 10bit444/matrix6编码不变，原S89实际载体headroom1/2/8的验证AST原样复用到本次新保存文件；这不是新留出集或物理精度提升。

每张实际保存R、global假设、local候选、相对scene候选四份HALF P3 EXR，以及独立HDR显示目标FLOAT P3 EXR、完整保留原SDR的HEIC、mask/flags、统一ACES预览与meaning。HDR目标EXR需与源HDR.f32存储分量逐位相同；不能只留它的hash或把carrier自洽当scene准确。五张沿用既有IMG2600/2604/0032/2608/0033，后两张只是旧encoded-integration冻结留出，不声称本轮新留出。所有新图像输出按照片加密，失败的剩余新文件也尝试加密保留；只上传独立staging中通过类型检查的小型text，人物明文不进入公开artifact。

按用户后续“解除所有限制并可存在日本”的明确资源授权，本次新归档采用日本直存3GB总量预检guard；不修改历史脚本的1GB规则，不拆包规避guard，实际总量超3GB时先停下复核。原100MB/4GB限制已在storage-jp-receipt-20261021记录为被后续授权替代。唯一大路径为GitHub→日本一次，完整GPG/所有成员在那里验证；香港只取小型公开证据、每cipher至多32KiB密文头和hash摘要，不回拉整包，不重传旧S5/S8/S98/S100大结果。输入已在仓库，无新增原片上传/secret/release；artifact retention1day。归档后还须逐文件核对认证tar中实际EXR/HEIC存在且size/SHA对应，不以文件清单代替交付。

当前没有新像素结果，不给errors.csv填零占位。A/工程/旧acceptance仍false；原S100已证显式Tone0桥接的RGB max必要下界0.1949973，不为此重跑bit-exact。真实拍摄端语义、j同帧曲线/统计、原Studio、RAW与实屏仍按原测试方案，不能用完整文件保存替代。
