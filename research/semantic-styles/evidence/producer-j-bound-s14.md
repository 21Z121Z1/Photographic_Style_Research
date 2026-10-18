# j 的内部权重界；不能换算成相机 EV

状态：**已验证静态**（数据流与实数代数）；**假设**（把它移植到 IMG_2810 的匹配相机生产链、空间 matte 或像素曝光幅度）。

来源：CameraColorProcessing，iPhone12,1 / iOS27.0 /24A446 来源记录；UUID `0A211E15-50CA-373B-AD9A-F9E3283C68F4`，拆出文件 SHA256 `974ffb2895cae06e26e63bd77ab4891f5401d4789449f7a0080d377553b2426e`。和 IMG_2810 的 iPhone18Pro/iOS27.0.1 不同，不能宣称是样张原生产代码。

逐行摘录见 producer-j-flow-s14.txt（含原反汇编行号和地址）；原 annotated.asm SHA `3c84b9b812f06dccdd8b03b1a2b6f4935c46ed5e084cdd21ab61e170111cd823`。原 cache 和历史产物只读。

## 明确的数据流

- LTMDriverV2::Process，`0x256bab574–578`：x27=computeInput+0xa910。`0x256bab880–884`：driverInput+0x24 的 j 写入该块+0x1c，即 computeInput+0xa92c（后者沿用 S6 摘录）。
- 此函数一个明确分支在 `0x256bab6b0–6dc` 把两个 ushort 的乘积（也作为 computeGlobalHistogram 的尺寸参数）写入 computeInput+0xa910，`0x256bab908–924` 再除以 HITHStat 首个 packed u32 的两个 ushort 的乘积。它不是凭字段名得到的平均像素亮度。尚未证明全部调用/别名写入，也没有样张的原始 HITHStat，所以不把该比值强行命名为已知物理量、不赋予样张数值。
- LTCGridCalcAlgo `0x256ba9bfc–c00` 定位 computeInput+0xa910；`0x256ba9e64–e74` 的 meta+0xc==1 分支在 `0x256ba9edc` 读取 N，`0x256ba9f18` 从同块+0x1c读取 j。
- `0x256ba9f20` 用 FMADD 更新 cap；`0x256ba9f34–50` 把一组权重逐项取 min(cap)。此前这组输入乘0.2（`0x256ba9e80–eb4`）。它是局部曲线计算内的权重限制，尚未证明等于最终图上的 gain。
- computeFaceWeight `0x256babdb8` 的 `0x256babf84–fa8` 和 `0x256babfe4–c01c`，分别由 ROI/faceRect 的位置和尺寸生成两个一维非负衰减，包含 `max(distance−halfExtent,0)`、`pow(1+aspectScale*distance,4)` 及归一化尺寸开根号；`0x256bac04c–58` 对两个方向乘积累加。上述拍摄端 ROI 统计权重与文件 faceSkinMatte 不是同一绑定证据。这里只描述指令形状，不补写尚未识别的坐标单位。

## 收窄到内部 cap 的范围

沿用 S6 已重放的指令解释，有限非负 N 时：

```
a = clamp(1 - 1/(kappa*sqrt(N)), 0, 1)
cap(j) = clamp(a + 2*(1-a)*(j-1), 0, 1)
kappa = 0.22360679507255554
```

N=0 的分支得到 a=0；N=-inf 的显式 sentinel 选 a=1（`0x256ba9f08–0c`）。本次不重复 S6 的64组ARM指令重放。

IMG_2810 的 j=281/256，故 β=2(j−1)=25/128=0.1953125。在实数解释下，对任意 a∈[0,1]，

```
cap(1) = a
cap(j) = a + beta*(1-a)
0 <= cap(j)-cap(1) <= 0.1953125
```

对固定原始权重 w，`min(w,cap(j))−min(w,cap(1))` 也在此范围。若 w≤a，这一处 j 干预完全不改变该权重。该结论只限此分支的内部算子，不证明最终像素必然变亮，更不是“相机最多提亮0.1953125EV”。

若按 round-to-nearest 的 float32 运行，`RN(1−a)` 在[0,1]内的误差≤2^-25，翻倍精确，FMADD 的绝对舍入误差保守界≤2^-24。上式对内部 cap 增量的保守上界可加 2^-23，即 `0.19531261920928955`。这是假定 RN 的条件界；未捕获真实 iOS 调用的 FPCR。它不是对原有像素验收门槛的修改。

## 对去提亮估计的限制

已验证的仅是 j 在生产曲线重算中的位置，以及这条 cap 子路径的内部界。把 cap 转成像素 EV，还缺同帧直方图、局部/face 权重、曲线及应用域，以及 WithoutFaceBoost 对照；尤其不能拿 log2(j) 当作物理增益或上界。人脸/人身预览的0.25/0.5/0.75/1倍 log2(j) 都是显式预算敏感性，不是估计出的 Apple 幅度，人身幅度也未由 j 识别。

只用已编码主图/增益图做正 RGB 标量分解时，任意预算 alpha 都能写成 `observed=(observed*2^(-alpha*m))*2^(alpha*m)`。S15 的不同 alpha 重建观察值至浮点精度，是这个宽模型类里的不可识别性示例；没有验证这些分解都符合真正的 Apple 相机生产模型，不能据此声称已证明其完整物理不可识别域。

真正的幅度收窄测试保持 NATIVE_TODO 的实机方案：同帧、同统计、同原始上下文，只切换 j/WithoutFaceBoost，分别捕获 global/local 曲线和实际像素。不能以另做 Vision 检测、合成统计或文件中的另一张 matte 代替。
