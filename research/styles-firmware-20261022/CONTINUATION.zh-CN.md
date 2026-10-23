# Cloud 接续：图像链路、可移植模型与原生边界

恢复基线为 `e5d2bcd8db8b3eb6737237ed88167777b3c920ba`，远端
`research/styles-firmware-local-20261022` 无更新。独立任务分支为
`research/styles-chain-20261023`。默认分支实际名为 `master`，核实时为
`ce25aa34fe3dac8541730971d6957401fca3e1dc`；既有 HDR launcher PR 和其他研究分支未修改。
本仓库/上级工作区没有 `AGENTS.md`，本分支没有 `validate.py` 或
`research/texture-styles/`。实际验证入口是 `verify_*.py`、单测及
`research/semantic-styles/validate_tone_s28.py`；后者依赖特定 macOS/加密历史材料。

## 模块与证据覆盖

|模块|复用入口与已有效证据|本任务重点与仍缺条件|
|---|---|---|
|GTM|`gtc_texture.py`、`semantic_tone.py`；已核原 CPU 曲线循环及条件插值|需显式供给曲线/transfer/CCM；不推断无风格原图或完整拍摄曲线|
|LTM|`full_ltm_chain.py`、`ltm_preprocess.py`、`ltm_gain.py`、guided 三阶段；S13–S15/S30|源图到 producer/guided/consumer 已有条件模型；原 GPU 采样和同帧 stats 未认证|
|肤色/人物|`main_pre393.py`、`pixel_skin.py`、`pixel_bright.py`；S29–S30 有限保存观测|原 `complete_forward` 的 selected404 固定 skin393；新接口须追踪 bright 真正进入 writer 的选择，实验数值不冒充原生|
|人脸/人身提亮|`semantic_curve_inverse.py`、已有 j/曲线分析；预算与幅度分开|合成 mask 验处理逻辑；同帧 N/B/T/曲线/原分割和 RAW 缺失，不能认证 Apple 幅度|
|Texture Styles|`semantic-styles/studio_under_eye.py` 及原生 `texture_units_s10.m`/`under_eye_final_s6.m`|已有最终单位/人工固定上下文实验；原 Studio 完整上游 stats/blur/眼部上下文未接；`texture_numeric.py` 只是纹理存储/采样合同|
|完整写出|`complete_forward.py`、`output_writer.py`，S30 cast0 skin writer|保留严格 v3；新增便携模型显式声明非 Apple 后端、阶段/分支/unknown 与输入来源|
|sqrt|S32 全 2047 half 输入的精确数学证书；S33 仅 9/16→3/4 的一次 CPU FPCR=0|RN-f32→RN-half 假设与输入域保留；不推广至历史线程或 GPU|
|pow|S33 封存 CPU 产物 0x15904→0x16244→_powf/index136 的静态绑定|缺原封存 dylib/运行镜像与真实返回位型；Linux/其他系统 pow 不替代它|

## 基线真实复核

Linux x86_64，`/usr/bin/python3.13` 为 3.13.5、NumPy 2.2.4。
未改基线执行全部 319 项单测，8 errors：Darwin arm64 输出 profile 拒绝、
绑定精度目录与当前 runtime 不同、Git 外 S33 私有封存目录缺失。
默认 `python3` 实际为 3.12.14，另有两个 `math.fma` 环境错误；因此复现命令明确用 Python 3.13。
这些缺测未改成 skip/通过，也没有放宽历史精度合同。

S29/S30/S31/S32、纹理存储和 writer 的公开定向测试共 51 项通过。
S32 全 2047 行证书重建后与保存文件逐字一致；这是数学证书复验，新原生调用 0。
S30 只读审计核对保存的 5814 个分量位差 0；此次没有重新运行三条模型。
其 `new_complete_models=3` 是历史收据的成本，不能当 Cloud 新实验。
S33 的原始 72B 报告/封存二进制缺失，只有公开摘要，完整运行绑定复核仍受阻。

详细基线日志及源码绑定见 `evidence/continuation-20261023/`。

## 原生材料与独立工作

工作区起始为空，没有原 Mac 私有框架、sealed dylib、系统缓存或照片。
原生现有 workflow 使用 `xcode-27`，不能默认它是免费标准 runner。
标准 macOS runner 也不会自然包含 SHA256
`47185c09c0407d7c96aa9dc55e0581ae4e781836951c8b236d17f2ac6f8efbbe`
的原封存 CPU 重编译产物；换系统 libm 不闭合这个目标。
本任务不触发付费/自定义 runner，不改变预算/安全设置，不上传私人媒体或系统二进制。

候选 `0x2b8f` 和 `0x36aa` 都是 **half**：分别为 1935/32768 和 853/2048；
精确扩成 f32 后位型为 `0x3d71e000`/`0x3ed54000`。它们来自 S31
SSA104–112 encode→127–132 square 条件见证，不是已执行 pow 的观测。
原地址只在上述封存二进制身份下使用。

## 新增实现与最小复现

`image_chain.py` 提供强类型 `BranchSelection`、`Numerics`、`SemanticMasks`、
逐阶段 `Checkpoint` 和 `BranchDecision`。复用并核 SHA 的旧前向实现，
只在独立函数副本中接入真实 SSA404 选择及明确的输出数值后端。
显式 cast16 使用调用者提供的系数，不声称原 renderer 已生产了 cast16 的正确参数。
默认 `STRICT_HOST_POINT` 仍保留 Darwin/arm64 门槛；Linux 必须显式选
`EXPERIMENTAL_PORTABLE_POINT`，它的 NumPy 幂是独立模型，不能替代目标 Apple pow。
选中 bright 未知会阻断 writer，未选中的内部错误仍可在诊断里保留。

`image_chain_cli.py` 保存原始 ABI context、override 请求、实际输入 hash、
逐阶段 NPZ、分支与 unknown。PNG 只是截断 code 值的诊断图，不是 ICC/ACES 预览。
RGB 差分只比较共同实际写入像素，含 max/RMSE、分位数、分布、half 位差和失败坐标；
参数变化的差值不是 Apple 精度误差。默认四种场景各为 8×12，模型仍有明确的 ≤32 tile 限制，
没有把低分辨率实验称作完整相机分辨率产品验收。

```sh
# 依赖 Python 3.13、NumPy 2.2.4、Pillow 11.1.0；从仓库根执行。
python3.13 research/styles-firmware-20261022/validate_portable.py /tmp/psr-checks-new
python3.13 research/styles-firmware-20261022/image_chain_cli.py \
  --numerics experimental-portable --output /tmp/psr-context-new
python3.13 research/styles-firmware-20261022/image_chain_cli.py \
  --numerics experimental-portable --selection experimental-bright16 \
  --output /tmp/psr-bright-new
python3.13 research/styles-firmware-20261022/benchmark_image_chain.py /tmp/psr-cost-new.json
```

所有输出必须不存在。CLI exit2 表示保留了 blocked/unknown，exit3 表示运行期间源码变化，
不能宣称绑定通过；默认参数集包含 raw field3=1 等会失败的端点，不删除失败来报绿。
field3 是内部 ABI 字段，不是已经核对的 Apple UI 控件。
另可用 `--patterns zero`、`--mask-pattern zero` 或
`--missing-masks person skin sky` 复核零输入与明确的合成零 mask 回退。
此回退不等于所有原生 nil-texture 分支。

`texture_style_adapter.py` 复用 UnderEye 连续 float64 公式并显式存 half，
要求调用者声明 primaries/transfer/reference、edited RGB、八种 mask 与 f32 参数。
`run_conditional_texture` 只执行明确请求的顺序；缺 mask 默认拒绝，显式 identity 回退留记录。
请求 SkinSmooth/Mattify 时保留前段检查点并返回 `output=None` 与 gap，
不把 identity 伪装成已实现效果，也不猜它们相对 GTM/LTM 的拍摄顺序。
历史原生单位与其他分支成果见 `evidence/conditional-texture-adapter-index.json`。

`module_sensitivity.py` 在同一源梯度上隔离 15 种干预：GTC identity/权重0/1、
BG/FG LTM neutral、skin theta9/10、bright exposure0/1、person/skin零 mask、
UnderEye 强度0/.5/1。每例逐字检查仅声明的 raw 字段/曲线/mask 改变，
从 source 重算全部阶段并保存差分。UnderEye 三例只采用**本调用者明确指定的 writer 后顺序**，
不声称 Apple 拍摄顺序；输入是实际 writer 有效 ROI，edited 和八张 mask 是解析合成字段。
各参数是 raw ABI 系数或已供给曲线，不是已经还原的 UI/原统计参数。

```sh
python3.13 research/styles-firmware-20261022/module_sensitivity.py \
  --numerics experimental-portable --selection experimental-bright16 \
  --output /tmp/psr-module-effects-new
```

对应测试还证明 inactive BG 分支/未选 bright 参数可不影响 writer，
以及 person=0 后同一 BG 编辑才影响输出；不把“参数变了”自动解释成“图像必须变”。

`pow_runtime_binding.py` 的 preflight 在 Linux 可执行，run 只接受原封存 dylib、
明确匹配的 Apple OS build 和 Git 外新私有目录。先核 SHA/Mach-O UUID/真实符号入口、
tail/stub/GOT/import，再收集一次调用前后 GOT 目标、loaded image UUID/偏移、
符号是否精确起点、参数/返回位型和 FPCR。失败不自动重试，不设置 FPCR。
新 C 收集器在 Apple 尚未编译/执行，不能把合成 metadata 测试当原生通过。
详见 [NATIVE_POW_BINDING.zh-CN.md](NATIVE_POW_BINDING.zh-CN.md)。
标准 GitHub `macos-15` job 另做收集器 arm64 编译及机器码窗口检查，
先记录实际 OS/host architecture/SDK/compiler；它从不运行收集器或调用原 pow。
编译通过也不能升级目标原生绑定。

## 运行结果与成本

本页后续记录最终稳定源码的运行收据。`master` 和原研究基线均无新增图像链路模块，
同命令工作负载不存在；性能脚本核实精确 ref 与缺失模块，明确标对照不可用。
这里只能报当前同机重复成本/波动，不声称相对 master 优化收益，不比较不同机器的时长。

稳定图像实验的精确源码提交为 `611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079`。
107 项定向回归通过，before/after source 和 evidence hash 均未改变。
全量 361 项仍为 8 errors，与基线的环境/私有材料错误一致，不能报全测绿。
原生 CPU/GPU 调用均 0。后续新增代码和最终 HEAD 的 CI 分别核验，不给旧 SHA 通过结果换标签。

|稳定合成运行|实际 writer / 案例|结果与失败边界|
|---|---|---|
|context cast0，四场景 × field3=0/.125/.375/1|14/16|colors=1 的 11 像素与 edges=1 的 2 像素在 selective413 未证 pow 域；exit2|
|显式 bright16，同输入/参数|13/16|gradient=1 在 selected404 未知；colors=.375/1 在 selective413 未知；exit2|
|全黑，bright16，4×6|0/1|24 像素 selected404 零分母/非有限域未知；没有 epsilon 修补；exit2|
|缺 person/skin/sky 的显式零回退，4×6，两控制|2/2|保留 1 个案例的未选内部异常；回退行为仅是模型合同|

两套主运行用同一原始 context 对齐后，有 12 对共同 writer 可比较。
例如 gradient、field3=0，只改显式 raw cast 选择，96 像素/288 RGB 分量的输出差为
max `0.02587890625`、RMSE `0.010544956055611347`，287 个 half 分量位型改变。
这证明 bright 在模型中实际影响 writer；不是 Apple 误差，也不证明 cast16 原系数生产正确。
阶段数组、分布、失败坐标、输入 SHA、命令和检查点文件 hash 见
`evidence/continuation-20261023/model-trials.json`。

同 Cloud 机器、同一 8×12 梯度、每分支 3 次完整模型，context 中位耗时
4.3675s、样本标准差 .1854s，bright16 中位 4.3935s、标准差 .2448s。
每分支三次 writer hash 各自一致；进程峰值 RSS 为 30976KiB，包含导入及全部重复，
不是单个算子的独占内存。没有相对 master 收益结论。
完整成本与原始样本见 `costs-611ac4f.json`。

首次并行开发期间的源码变动运行、初次未绑定测试及域标签修正前中断的运行
另记 `initial-attempts.json`，未计作稳定验证。
工作区 `styles-synthetic-611ac4f.zip` 包含合成 context、逐阶段 NPZ、诊断 PNG 与完整 summary；
其 SHA/大小见 `synthetic-artifact.json`，不含原照片或二进制。
