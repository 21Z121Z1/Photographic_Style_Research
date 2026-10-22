# block290与首批共享叶：先持久化的增量

基于 `d631b0961504b9734bec489a268dc92065079226`，继续同一iPhone17,3 /24A446参考资源。新增下载0B、私人照片0张；本增量没有重跑mids、fallback semantic或更早native批次。该提交后继续Shadows和剩余叶，不把中间进展称完整BG/FG或照片逆解。

## 预计算分支的确切输入和来源

AIR10参数编号不是Metal绑定槽：`%6=inputBgLTMGainMap`对应Metal8，`%7=inputFgLTMGainMap`对应Metal9；`%8/%9` guide对应Metal5/6。这由原kernel metadata直接核验。

新增完整 `_finalRenderRegion:` 936B原指令，逐字节核cache；SHA `27a77fcfa110227c5f1290e559dc725a7f53f53e9905017c61f6e8dbeb01cbc1`。复用已有 `_processLTMGainMap` 和compile/process文本，没有重复提交已导出方法。CPU先在gate self+0x579==1时执行createLTMGainMap，临时texture8/9经guided filter（kernelRadius1、原epsilon输入）分别写self+0x238/+0x240；final-region仅在两者都有时绑定Metal8/9。动态参数→LTM生成→upsampleLightMap→finalRendering的原调用顺序也已定位。

原AIR7的createLTMGainMap先使用曝光/GTC生成按通道的比值（SSA203/205），除数是其工作域reference RGB，带原小值zero guard，再写BG/FG临时纹理。该生产端及guided filter在本增量仅静态定位，**没有重新生成或恢复原帧纹理**。最终显式输入应是guided-filter后的纹理。来源、绑定、函数/方法SHA见 `evidence/precomputed-links.json`。

block290本身采样两张纹理后做BG/FG各自的LTM向1混合、HR向min1混合，乘reference RGB，再按已处理person weight混合。**块内没有新CCM、GTC采样或曝光乘法**；曝光/GTC已经体现在供给的precomputed值中。模型不猜它与fallback等价。

ROI field5/6是byte48/64，名字分别为logicalImageToBg/FgLTMGainMapGridScaleAndOffset。原坐标为f32 `scale*(uint16 grid+.5)+offset`，sampler .3为normalized/clamp-to-edge/linear。`Texture2D`要求有限、命名工作域的half H×W×3输入（每边≤1024、abs≤8），两图工作域须一致；point采样明确采用CPU理想双线性/clamp，集合采样用对应局部texel范围包络，不假设纹理单调。未证明原GPU采样精度、纹理格式或原帧身份。

`PrecomputedInputs`同时要求两个ROI、reference RGB和处理后的person weight。`tone_fragment_sets.forward`在两个绑定都在时使用此输入类型；只给旧fallback输入仍返回 `unknown_precomputed_inputs`。当任一绑定缺失，仍要求独立fallback输入，不拿预计算纹理猜working/GTC。cast2的原caller系数适配继续复用，结果与guide、未决分支一起按集合传入BG/FG。

新原block比较仅把SSA标识双射改名以包装宿主入口，原运算/常数/metadata保持；27组不同纹理尺寸/坐标/边缘/person输入，81分量逐位差异0、集合越界0。第一次测试外壳错把ROI field5/6放在80/96，导致6个越界；按原schema改成48/64后通过。模型/误差界未改，输入未删除，失败收据留私有scratch、公开更正摘要/哈希见 `precomputed-development-erratum.json`。

## 三个独立共享叶

`leaf_numeric.py` 分开point和set后端，并要求显式half/f32转换；混用point/set、给point贴区间、零分母或不证的pow域均拒绝。point逐操作舍入，set保留比较未决两支，并使用普通算术2u、pow/sqrt4u的明确宿主假设。它们不是GPU误差证明。

`pixel_leaves.py` 是独立数学实现：

- whitesCurve：确切half前后矩阵、幂、min-channel、显式供给曲线的pixel采样、>0与>.75分支、BG mode0/FG mode1、外域分量及max0。
- contrastFilter：工作RGB clamp/外域、root/luma/variance、确切f32权重到half的过渡、两套root混合及按原RGB通道范围做的色度保持分支。
- airyFilter：RGB和的倒数归一化、chroma smoothstep、root luma、gamma混合及外域。全黑导致原链含除零/NaN假设，模型明确unknown，不填identity或拿host偶然输出代替定义。

模型adapter直接接RGB/系数区间；域无法证明时保留具体unknown，未实现叶仍fail closed。已有BG/FG controller无需改写。

|新原完整叶宿主对照|非零激活输入|已知point/set域|逐位差异|集合越界|
|---|---|---|---|---|
|whitesCurve，含两mode|30|30|0|0|
|contrastFilter|15|15|0|0|
|airyFilter|10|8；另2个全黑保留unknown|0（仅已知域）|0（仅已知域）|

`leaf_host.py` 保留所选原函数完整正文及依赖，只有显式声明的宿主libm、dot、sampler intrinsic实现；没有identity/aborting占位来冒充这些叶。`native_pixel_leaves_check.py` 在收据中保留所有unknown案例和逐位差异，不把它们算通过。算术后端在比较后仅加point/set类型防混用guard，算术方法AST未变，源码连接为 `leaves-1-source-link.json`，未重跑这55组。

## 验证与范围

当前92项单元测试通过，覆盖ROI/采样中心和边缘、两路径不互猜、系数不重复套用、纹理域错配、point/set精度合同、whites两mode、contrast正负与gray分支、airy黑点unknown和非零BG adapter。原GPU/真实同帧像素、IMG_2810身份依赖保持独立；没有把静态生产链或条件域通过升级成完整相机正向/逆解。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_precomputed_semantic_check.py /path/to/private/0010.ll.txt /tmp/psr-precomputed-new.json
python3 research/styles-firmware-20261022/native_pixel_leaves_check.py /path/to/private/0010.ll.txt /tmp/psr-leaves-new.json --leaf whitesCurve --leaf contrastFilter --leaf airyFilter
```

工作仍在继续：下一组是ShadowsFilter/Negative，再补sat/lighten和local/gammaContrast、underGrass、neck/underTone、smartContrast等。9槽不重扫已覆盖215头范围，也不标unused。未读取私人照片、未触碰其他项目/进程/安全设置、未重试ps，不合并删分支。
