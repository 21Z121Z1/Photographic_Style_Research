# 正Tone→皮肤系数：实际统计shader与既有算子的连接

本阶段在 `a20f5c9` 已取得的资源上继续，没有新下载、挂载或照片输入。新增 `positive_tone_skin.py`，把实际iPhone17,3 /24A446的参数生成端接到既有 `semantic_skin_model.py`；没有修改该旧模型、S20证书或原验收阈值。

## 入口、参数与方程

上一阶段已核：CPU读取样式castIntensity/toneBias/colorBias，按特定scene的tuning可能先缩放，再分别写入SSRParams的byte4/8/12。672B参数buffer与10640B统计buffer进入 `RenderingParamsFromStats`。因此这里的 `t` 是**已完成该场景缩放的SSRParams tone字段**，不是UI百分数、EV或原曝光。

原资源的module11此前未命中S3关键词筛选；本次用 `air_by_name.py` 按实际函数名定向提取。代码复用已测wrapper解析器，要求源metallib确切SHA，拒绝把私有bitcode/AIR写进Git checkout；只提交函数、payload/canonical SHA和类型改名表。该模块17396B bitcode、canonical SHA `5ca4d2dce19c7e8825f0608b04d3637ddf05f3eb507f33430670617624c02c53`。历史91/92比较的分母不改写。

在thread-group分支1、tone≥0的分支339中，SSA368..374生成并写SSRFGAdjustment字段9/10：

```
s = f32(t*t)
theta9  = f32(f32(2.75*t) - f32(3.75*s))
theta10 = f32(f32(a*s) - f32(b*t))
a = f32 bits 0x3e554c98 = 0.20829999446868896
b = f32 bits 0x3f355326 = 0.708299994468689
```

FG结构从参数byte556开始，两个输出分别为byte592/596；与最终skin helper读取的field9/10相连。当前独立模型声明0≤t≤1，保留每次f32舍入，没有把IR的fast收缩当作逐位同一。**该正分支仅这两个字段不依赖统计；不能扩展为其他FG/BG/semantic参数都不依赖统计，或整个Tone效果只含两项。** 负Tone分支仍另有统计、scene/brightness与tuning依赖。

theta9并不在整个正域单调：t=0时0、t=.4约.5、t=1为-1。theta10在t=1约-.5。不能把Tone滑杆简单解释为正曝光增益或一条固定全局gamma。

## 复用与实际比较

`positive_tone_skin.forward` 只把已算theta9/10传给既有连续skin算子，原RGB、skin weight与guide必须由调用者显式提供。颜色域仍是该kernel工作RGB；没有宣称scene-linear P3。它省略其他前景/背景、语义、GTM/LTM、色彩与纹理项，不是整style正向或逆向。

`native_positive_tone_check.py` 重新核原AIR的canonical SHA，再对原全文作arm64 macOS宿主编译。其他输出所需的pow/min/max/mix/clamp使用明确记录的C shim；**目标theta9/10的SSA依赖链只含f32乘/减，不使用这些shim**。因此只比较这两个系数，不把其他shader输出或Apple GPU fast_pow精度也算作验证。

9组边界/结构化Tone与1024组固定种子留出，共1033组。每组还变化合成stats、cast与无关tone tuning，提取2066个目标系数：

- 733个逐位差异，max绝对误差 `1.1920928955078125e-07`。
- 按未消减绝对项计算float32三步舍入界，越界0。没有以逐位零差异表述宿主fast收缩结果。
- 没有运行iOS library、原GPU kernel或真实照片，也没有用此次宿主比较替换旧native像素门槛。

两个新增测试验证边界、非单调theta9、有限域拒绝，以及复用算子在skin weight0/系数0时的身份和非零受控效果。总回归为 **41项通过、0失败/错误**。原257头、通用头、prior和SRL的既有native验收均未重复运行；本次只新增正Tone系数比较。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/air_by_name.py /path/to/verified/CMImaging.framework/default.metallib RenderingParamsFromStats f6d825a7e5c00d0eec2e4721c51bdb7a6b9554073dc632273dec825ae1bf705f /tmp/psr-air-private-new /tmp/psr-air-receipt.json
python3 research/styles-firmware-20261022/native_positive_tone_check.py /tmp/psr-air-private-new/0011.ll.txt /tmp/psr-air-receipt.json /tmp/psr-positive-tone-new.json
```

## 尚未关闭的验收

|目标|当前证据|状态/最小缺项|
|---|---|---|
|匹配参考固件的插件与CPU静态来源|OS+SystemOS成员、SHA、UUID、35方法原字节、实际shader/绑定|通过；实际帧运行入口仍需同机型iPhone运行捕获|
|已有独立算子与新分支|GTC、prior、SRL参数、正Tone→皮肤系数与已有条件皮肤算子|各自限定域通过；不合并成完整相机正向认证|
|tone/color/intensity完整数值映射|CPU已定位cast表/三线性插值、SSR静态和统计生成入口|部分；表选择/插值独立数值比较、负Tone/其他动态系数尚未完成|
|匹配Apple原生像素与留出|旧Mac原生证书保留；本次无iPhone/GPU/照片新结果|待依赖：同机型/build的可调用运行环境和原同帧stats/maps。当前Mac无法执行iOS框架；未绕过锁屏去跑展示/Photos|
|IMG_2810纹理样张准入|iPhone19,2、Styles16、PeopleData3的既有metadata|待精确capture build与原帧上下文，仍不得充当Styles2参考链|
|仅成片唯一恢复|旧S20同观测不同中和结果证书、归一化/舍入歧义反例|不成立于已证范围；继续输出条件/近似/集合，不承诺丢失细节恢复|

原图+成片参数识别、完整HEIC辅助上下文条件逆、仅成片近似估计继续分开。没有访问图库或私人原样本；没有把重新生成纹理统计当作原拍摄统计。上述静态数值待办仍可在现有缓存继续，但整条Apple原生/原帧验收有明确运行环境与上下文依赖，不能由更多合成测试替代。
