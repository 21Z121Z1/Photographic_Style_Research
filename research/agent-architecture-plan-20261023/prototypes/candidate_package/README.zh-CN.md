# 候选 A。由一个领域包拥有实验执行与证据身份

维护者给出原始 context 和研究意图，由一个对象负责运行、材料检查、身份绑定与结果分类。调用者不再同步多份源码列表，也不能把 `Apple_verified=True` 作为运行参数。

这是隔离原型，未迁移生产模块。`evidence/proof.json` 绑定仓库提交 `611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079` 和四份原型源码 SHA。5 项测试及两条 CLI 旅程通过。该证明不涵盖长寿命 Python 进程的 import 缓存，不能据此宣告证据身份已经闭环。

## 调用者使用方式

以下 API 已可从本目录的 `execution.py` 导入。

```python
from execution import Study, Selection, RenderedModel, Rejected

result = Study.portable(repo, context_file, selection=Selection.BRIGHT16).run(new_output)
if isinstance(result, RenderedModel):
    use_diagnostic(result.writer_path)

result = Study.reference(repo, context_file, precision_file, sealed_binary).run(other_output)
if isinstance(result, Rejected):
    retain_material_gap(result.code, result.reasons)
```

用户使用原始 context，不提供生成好的 LTM 图或中间 RGB。`Study.reference` 接受明确的历史精度合同和原封存产物路径。它在此原型里只能返回拒绝结果，没有原生成功的构造类型。

真实 CLI 复验从仓库根运行。输出目录必须不存在。

```sh
python3.13 research/agent-architecture-plan-20261023/prototypes/candidate_package/prove.py \
  --output /tmp/psr-candidate-a-new
```

`demo.py` 也可独立驱动。portable 使用现有完整模型。native 请求使用保存的 S25 精度合同，在本 Linux 环境被拒绝，没有替换成另一个系统的 pow。

## 结构与不变量

公开表面是 `Study`、`Selection` 和三种互斥结果 `RenderedModel`、`UnresolvedModel`、`Rejected`。`Study` 有两个构造入口和一个执行方法。当前原型只有一个执行模块。

|所有者|拥有的知识|调用者可以停止协调的工作|
|---|---|---|
|`Study`|意图、材料、执行边界、来源、结果分类|源码 hash、精度目录选择、后端选择与证据级别不能由不同 caller 各写一套|
|`_Sources`|仓库提交及源码字节身份|不再逐个手写跨目录依赖|
|`_Inputs`|原始 context 或精度文件的精确字节|准备之后改输入即拒绝，不复用旧观察|
|既有计算模块|half、f32、采样、分支和 writer 数学|原型不改已有数值后端及已验收证书|

Model the Domain 将意图与结果做成不同类型，而不是组合一组 success/native/complete 布尔值。Boundary Discipline 把 JSON、磁盘、host profile 检查收在执行边界。Separate Before Serializing Shared State 让每次运行只写自己的新目录。Type System Discipline 在此 Python 原型中表现为类型标注、冻结的数据与有区分的结果对象。静态类型检查尚未运行，不能写成编译器已经证明这些约束。

源码集合采用保守策略。原型枚举本提交跟踪的 `.py`、`.c`、`.m`、`.metal`、`.swift`，另绑定当前候选的四份 Python 源码。初次证明共绑定 698 份文件，含跨目录 `guided_reference_v3.py` 和 `semantic_curve_inverse.py`。这避免了另一份人工依赖表，但会把无关源码变化也视为请求失效。它还不是最小依赖闭包。

`writer_sha256` 是写出 half 数组原始字节的 SHA，不是 `.npy` 文件容器字节 SHA。原型还未把这两个概念做成不同字段，这是正式接口设计前应消除的歧义。

## 当前系统怎样运行

`complete_forward.Context` 校验 10 张纹理及原始 ABI 数组。`complete_forward.forward` 产生 LTM、guided 和主 consumer，最后交给 writer。`image_chain` 在硬 SHA 守卫下克隆 forward，改变显式的 SSA404 选择，并为 Linux 的 portable 实验替换最终 code3 数值模型。原严格 host profile 保留 Darwin arm64 限制。

`image_chain_cli.execute` 还负责自己的源码清单、输入编码、override 请求、NPZ、PNG、报告与参数差分。它有 11 个参数。另有 `image_chain.run`、`validate_portable.sources` 和 `bound_validation.run` 各自维护证据或源码身份的部分规则。这是当前结构观察，不是把四个接口计成四起历史 bug。

`context_color_api.identity` 把目录绑定到具体 context、精度源码和 runtime。`output_code3.runtime_contract` 描述的是原 macOS host powf ABI。当前拒绝 Linux 是一个正确边界，不能把它列为待修 bug。

父代理新增的 `4d314bdbfd348b5371f737625c8bacc064930be7` 已提供独立模块敏感性入口。正式 facade 应让该入口复用相同执行所有者，不重复实现已有 15 种干预或把它们列为尚未完成的功能。

## 已跑的失败探针

|探针|原始依据|实际观察|
|---|---|---|
|保存的 Darwin 精度不能在 Linux 接受|`context_color_api.py` 的 runtime 合同及 `model-precision-v3-s25c6.json`|返回 `reference_runtime_mismatch`，列出 system/release/machine/numpy，不调用原生函数|
|跨目录计算依赖在准备后改变|`guided_conditioned.py` 实际通过 importlib 加载 `hdr-native/guided_reference_v3.py`|临时 Git 仓库跟踪该真实源码，修改后在模型加载之前拒绝|
|精确 context 在准备后改变|当前运行以原始 context 文件 hash 绑定，不能换输入继承输出|只追加换行也返回 `input_identity_changed`|
|不能由 caller 指定证据级别|当前既有结果和清单含多种证据布尔值，这里改为独立结果类型|未知关键字 evidence_level/source_paths 被拒绝，结果字段不能改写|
|portable 仍须产出可用结果|使用保存的合成完整 context 和实际源图模型|实际产生 12 个 writer 像素，保留为 portable_model|

这些探针来自真实代码和保存合同。它们没有自行证明历史上同一失误发生过两次。历史频次由共同的 incident ledger 独立判定。

## 接入整个仓库

正式方案只新增一个支持的实验 API 与一个机器可读 CLI。Swift `StyleDeltaMapCore` 保留命令与进程管理，读取 CLI 的有区分结果，不复制科研验收规则。HEIF 的结构解析和辅助图编码仍由现有 container 工具拥有，不能把 HEIF 结构有效等同摄影风格数值正确。

建议分三次可验收的变更。

1. 先把只读材料检查和当前 portable 入口接到 facade。原冻结源码和历史证据不移动、不换 SHA。
2. 同一次变更迁移现役 CLI caller 的清单与证据标签生成，删除重复的现役路径。保留历史冻结脚本只作带版本的旧证据，不继续增加 caller。
3. 在独立原生后端有真实材料与观测证明后，才增加 `NativeObservation` 结果类型。CPU 单次 helper、GPU、整个 pipeline 和产品验收继续是不同范围。

这里没有提出重写所有数学 helper 或 macOS app。能先隐藏的，是执行条件和证据边界的协调复杂度。

## 取舍、风险与待测修正

我们接受当前全仓源码绑定的保守失效，换取原型不遗漏已跟踪跨目录源码。正式包边界可以缩小该集合，但须通过依赖探针证明。

我们接受当前 Python API 的运行时类型守卫，换取对已有代码的小接入面。正式迁移应另行引入静态类型检查和包边界检查，不能把现在的 dataclass 当作不可绕过的安全边界。

父代理审查指出一个当前原型未覆盖的反例。长寿命进程如果先导入旧 backend，再改磁盘源码，然后准备新请求，importlib 可能复用旧模块，而清单却绑定新磁盘 bytes。当前两个磁盘 snapshot 不证明已加载 bytecode 身份。独立评审应先在自己的临时副本复现，当前 5 项通过不能排除它。

候选 A 的待测修正是把同一直接 API 的执行体放入每次运行独占的新 worker 进程，输入使用已封存字节，代码来自不可变快照。caller 仍只调用一次 `Study.run`。这一修正尚未实施或计量，因此不能声明已经消除了缓存风险，也不能声明它的启动成本已知。

正式迁移之前需要解决该反例，明确数组字节与容器文件 hash 的不同字段，并证明新机器可读结果在 Swift 和 CLI caller 中不会被误作 Apple 通过。是否采用此候选由两个结构原型的共同评审决定。
