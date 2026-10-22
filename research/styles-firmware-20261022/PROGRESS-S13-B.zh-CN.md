# S13-B：本版 guided 三核、复用点模型与集合后传

本版iPhone17,3 /24A446中CMIGuidedFilter三核是AIR90/91/92，不能沿用Mac模块号。它们与旧Mac AIR142/143/144整模块alpha相同，限于明确排除的target triple和llvm.ident；常量、sampler、代码、metadata和FP flags相同。复用已存在的`research/hdr-native/guided_reference_v3.py`点算法，不从零写通用guided filter；不把代码同一性扩成GPU/拍摄链同一性。

新增完整原三核宿主重编译，保留原函数/metadata/属性和五处独立输出。CPU包装明确每个imageblock只有1线程：barrier为该单线程同步，imageblock存储与纹理写回都实际执行；不宣称原多线程imageblock运行。宿主sampler复用v3的1/256权重、half tie-up假设，R16缺失lane=[r,0,0,1]。实际系数在guide网格生成，过滤仍在guide网格，最终按output网格采样。scalar guide只在系数阶段广播；单次RGB调用不得偷换成三次R16调用。

5个新合成fixture：不同输入/guide/output尺寸、RGB guide、scalar guide、常量、零epsilon+零guide。4个有限点域在a/b/mean_a/mean_b/output全部逐位一致（最大绝对误差0）；负例在全部五处均非有限，模型明确unknown，不改epsilon。161项回归通过。

集合模式单独实现三阶段有界传播，可接受上游完整half gain/guide盒及f32 epsilon盒；固定网格与所声明CPU sampler权重不取中心。共享mi的平方使用相关square，分母穿零仍拒绝。对保存宿主输出重放：4个已知集合全部覆盖、0越界，最大盒宽分别.0021973/.0234375/.0078125/.000019073；零epsilon域仍unknown。更宽gain盒的回归确认输出宽度随输入传播。此为误差假设下的集合覆盖，不是GPU数值吻合或逆解精度证明。

开发失败收据保留：初版集合mean采样多加半texel，造成3组后续集合越界。修正texel-index坐标；b明确使用half转换前的f32 a。未改误差界、阈值、mask或案例，仅重放保存输出，未重跑宿主五fixture。原点模型不变，最新补充收据逐位复核当前点模型及域状态。

收据：`native-guided-s13b.json`、`guided-sets-s13b.json`、`guided-sets-development-failure-s13b.json`，保存版本/原完整kernel/模型/包装/五处输出half位型及输入SHA。原LTM完整入口早于SSA99仍未接入，actual guide与后续ROI/纹理格式、原帧统计不从成片恢复。旧24组合unknown、8叶域unknown、bright与其他差异、tuning失败和独立tonal观察均保留。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_guided_check.py /path/to/ios-air-directory /tmp/new-guided.json
python3 research/styles-firmware-20261022/check_guided_sets.py research/styles-firmware-20261022/evidence/native-guided-s13b.json /tmp/new-guided-sets.json
```

无下载/私人媒体/原GPU执行。本阶段数值工作以显式输入为条件，不等于同帧纹理恢复或完整照片逆解。
