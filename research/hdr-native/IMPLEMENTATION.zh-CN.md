# 独立 HDR 制作与场景恢复：实现入口

`GOAL.zh-CN.md` 是持续目标。这里的代码把已验证的消费端控制、给定曲线的条件逆、HDR/SDR 比值和显示 headroom 分开，冻结旧模型不改。

## 按证据使用控制

`operator_recipe.retarget` 只接受 26A434、捕获布局的672字节参数和已知原输入上下文SHA。它分别生成 consumer local、背景/人物local、皮肤色彩、皮肤亮度的目标参数，保证目标字段外字节不变。620/624→1及592/596→0的端点来自S27原PSO隔离干预；中间强度是明确的工程withdrawal policy，不能称为Apple UI tone标定。拒绝把最终Y当成原输入直接重放，也不猜相机j、global曝光或Studio偏移。

已知原输入A时，可直接得到`F_target(A, frozen_context)`。只观察最终Y时，需要完整集合

```
{ F_target(A, context) : F_applied(A, context) = Y }
```

而不是对Y再执行一次负tone。全域集合无法保证1e-3点估计的地方继续输出mask/区间；S20非唯一性证书、33皮肤点紧外包络缺口保持。不能用参数隔离成功替代逆解通过。

`../semantic-styles/spatial_curve_retarget.py` 在已知实际knots、应用域、固定空间权重和配对曲线时提供条件集合逆。先混合前向曲线再求逆。权重依赖待求像素、颜色耦合、半精度/纹理合同未确认时，不能把它接成相机的事实模型。

Global-only、local-only、semantic-only各自保留独立参数和结果收据，组合顺序从实际调用链确定。一般非交换算子不能只凭“反曝光/除c/d”的名字任意换序。旧`Y=G(lX)`分解仍是假设。

## 目标 HDR 与承载

`render_contract.gain_from_pair` 接受同一线性P3中的已定义SDR/HDR有界tile，导出RGB log2增益及无效/负值mask。苹果`_flexMapLinGainRGB`先把负RGB夹至0，这些值不能被悄悄计入精确可逆域。黑位offset明确给定；offset带来的定义与场景标定分开。

`apply_decoded_map` 是原`_flexMap`的数值参考，要求caller已经按原生图坐标完成采样。它不暗中缩放或clip。`iso_scale`用metadata声明的log2 capacity计算headroom强度。S29覆盖同尺寸合成map，不能外推全尺寸低分辨率采样。

```
logG = log2((max(H,0)+offsetH)/(max(S,0)+offsetS))
H_r = exp2(scale * ((maxEV-minEV)*signedPow(code,1/gamma)+minEV))
      * (S + offsetS) - offsetH
scale = clamp((log2(headroom)-baseCapacity)/(alternateCapacity-baseCapacity), 0, 1)
```

这里的H必须带来源：场景恢复候选、已知输入的算子反事实、或创作显示目标；三者不能混称scene真值。场景母版之后还有独立显示渲染步骤。现有固定ACES1.0 SDR Video预览仍只是诊断，不替代HDR屏幕/观看环境测试。

`run_hdr_s29.py`：原CoreImage双图自动writer与35次headroom原生对照。`run_hdr_s30.py`：显式已定义RGB比值，分别测试未编码原生应用、两种HEIF format请求、SDR codec、gain codec/metadata和8/10/12/16bit理想量化。合成输入不计照片验收，bit深只认实际hvcC/pixi，不能从RGBAh请求推定。

实际S30在writer输出的ISO metadata检查处停止，后面的codec/理想量化分栏没有运行，不能把代码存在当成结果。S31改为独立编码+ISO item替换；S32进一步隔离矩阵与原生primary/aux读回。结果在本目录REPORT和证据JSON中，未过的编码门槛保持。

SDR/HDR分量为正且offset为0时，单map在中间headroom生成`S^(1-w)*H^w`。它是RGB几何插值，通常不等于以某个Apple UI tone参数重新运行整条LTM；一个map的单个w也不会自动给global/local/semantic各选独立强度。这些控制在制作阶段分开，组合成H之后，中间headroom仍要逐档验证。

最终保留原SDR要求保留coded descendants及颜色/几何属性并用原ImageIO全分辨率验证max0。CoreImage双图writer会重新编码SDR，不能直接充当最终封装器。旧`gainmap_carrier.replace_map`提供保留SDR的已验证入口，但仅支持原先8bit direct gain item；新map格式和树结构未经验证不能强行套用。独立HDR制作并不自动使传输通过旧1e-3门槛。

## 相机端数据流的证据边界

24A446 iPhone12,1参考代码中，`LTMProcessor.process`在`0x256b64468`判断globalCCM，`0x256b644d8`应用解码后的signed Q12矩阵，`0x256b64598`可选dehaze，随后纹理送到`startCalculateHITHStatistics`（`0x256b64d84`）。`LTMCurvesCompute.compute`（调用点`0x256b64e20`）得到的字典被合并到outMetaData（`0x256b64e50..e5c`）。这证明了统计输入/曲线生产的连接，不能由shader名证明它就是最终全尺寸照片的同一应用操作。

`LTMMetadataWriterV2._addLTMCurvesToMetadata`把output+0x18504/+0x18908的257节点分别clamp[0,1]、乘常量、向下取整、存u16；局部曲线为12×16格、节点数由调用者65/129选择，打包也有clamp/floor和方向重排。已有汇编证据见`evidence/producer-statistics-path.txt`与source receipt。这进一步说明：生产曲线、文件消费端c/d和最终ISP的像素应用必须逐边连接，不能拿结构字段名当c/d是整条LTM可逆增益的证明。没有同帧实际曲线/统计/应用域，j的β=.1953125不能变成样张像素EV界。

每个原生run一次只排一个、artifact保留1天；原件/冻结模型不改，含人物的输入输出继续加密传输。大图计算只在macOS runner，VM上的Python用400MB scope。所有本阶段总验收仍为false。
