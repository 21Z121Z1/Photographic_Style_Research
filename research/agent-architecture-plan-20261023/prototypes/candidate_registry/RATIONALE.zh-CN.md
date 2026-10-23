# 候选 B。能力注册表与单一运行协调者

## 问题与实际约束

调用者需要明确知道一次运行能回答什么问题。当前 `image_chain_cli.py` 可以在 Linux
产生有用的模型图像，但 `output_code3.py` 的旧精度路径要求 Darwin arm64，
`context_color_api.identity` 又绑定了更精确的历史 runtime。原生 pow 收集器缺少
Git 外 sealed dylib 时只能准备，不能执行目标调用。

这些区分已在当前代码中存在。候选 B 试验把能力选择、源码依赖集合、输入冻结、
运行时准入与结果等级交给一个所有者，避免每条新命令重新组合这些规则。
候选没有迁移生产模块，没有改旧模型、旧目录或历史通过记录。

## 调用者先看到的接口

```python
coordinator = Coordinator()
request = coordinator.prepare(
    'portable-image', Intent.PORTABLE_MODEL, Path('input.json'), Path('new-output'))
record = coordinator.run(request)
assert record.evidence_level == 'model_only'

# 相同模型不能因为请求方改了意图就成为原生证据。
request = coordinator.prepare(
    'portable-image', Intent.APPLE_NATIVE, Path('input.json'), Path('new-output-2'))
assert coordinator.run(request).status == 'blocked'

# 原生收集器仍可被发现，但不可假装已有原产物和目标环境。
request = coordinator.prepare(
    'sealed-pow', Intent.APPLE_NATIVE, Path('input.json'), Path('new-output-3'))
assert coordinator.run(request).status == 'blocked'
```

调用者提交声明用途的配置文件，不再手写执行命令、宿主判据和多个 source 列表。
本原型的公开 `source_paths` 和 `snapshot` 是探索用检查口，正式接口应收回为内部实现。
原型输入是现有 CLI 的合成场景配置。它没有伪造真实照片或人物分割。

## 数据与模块

|所有者|数据或接口|隐藏的复杂度|
|---|---|---|
|`registry.json`|能力 ID、意图、运行方式、历史 profile、可用状态|一条命令究竟能运行模型、使用绑定宿主，还是只能准备原生收集器|
|`Coordinator`|`prepare`、`run`|依赖发现、输入与源码 hash、运行时检查、CLI 调用、结果等级和不覆盖输出|
|`Request`|能力、意图、输入 digest、源码快照、独占输出目录|准备与执行之间的身份变化|
|`RunRecord`|blocked、model_only 或 unknown，以及实际工件 hash|记录有用模型与真实原生证据的边界|
|现有图像与 HEIF 模块|原来的算法和命令|本原型不改数值合同、采样或文件格式规则|

组织结构采用 **Model the Domain**。能力是枚举意图与一张声明表，不再由命令名暗示
精度。边界采用 **Boundary Discipline**。原始 JSON 在协调者边界解析，算法留在已有
实现中。输出采用 **Separate Before Serializing Shared State**。每次运行使用新目录，
重复执行不会覆盖已有工件。这些原则的叶技能已读。

接口深度来自集中执行的证据策略，不来自转发更多算法参数。
候选仍有一个关键局限。它保留了算法模块的原始 ABI 数组和 AST 克隆，因此单独采用
注册表不会让错误的肤色字段、颜色域或 mask 类型在算法层自动失效。

## 实际运行与反例

基线提交是 `611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079`。
初版代码与测试 hash 记录在 `artifacts/structural-inventory.json`。
执行命令是从仓库根运行以下两项。

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /usr/bin/python3.13 -m unittest discover \
  -s research/agent-architecture-plan-20261023/prototypes/candidate_registry \
  -p 'test_*.py' -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /usr/bin/python3.13 \
  research/agent-architecture-plan-20261023/prototypes/candidate_registry/run_probes.py \
  research/agent-architecture-plan-20261023/prototypes/candidate_registry/artifacts
```

7 个测试通过。脚本实际调用了当前图像 CLI，一张 2×2 合成色块写出了 4 个像素。
它执行的是 portable 模型，目标 Apple 调用和原生参考比较均为 0。
另外四个 probe 按预期拒绝了以下请求。

|probe|输入来源或已有约束|初版实际结果|
|---|---|---|
|模型请求被改成 Apple 原生意图|`image_chain.py`、CLI 的明确 model_only 合同|blocked|
|Linux 使用历史 Darwin profile|`output_code3.py` 与 `context_color_api.py` 的实际 gate，基线日志包含对应错误|blocked|
|准备好的收集器被当作已可执行原生能力|`pow-runtime-preflight-cloud.json` 的实际缺件状态|blocked|
|源码快照删掉实际跨目录 guided 文件|`guided_conditioned.py` 的 importlib 文件加载|blocked|

这些是当前真实边界与对抗性输入的回放，不是四个已经发生过的历史 bug。
重复失误的次数应以项目的独立历史事件账本为准。

原型的静态依赖闭包包含 70 个文件，其中包括
`hdr-native/guided_reference_v3.py`、`semantic-styles/spatial_curve_retarget.py`
和 `semantic-styles/semantic_curve_inverse.py`。它递归处理普通 import 和当前代码里的
Python 文件路径字面量。它不是任意 Python 动态导入的完整证明，未解析的计算导入
仍需要额外拒绝规则或明确声明，不能把 70 当成通用完整性证书。

## 独立审查发现的未决反例

初版在构造 `Coordinator` 时缓存了解析后的注册表，但 `prepare` 的快照读取磁盘文件。
审查者指出，如果构造后、准备前更改注册表，快照可能绑定新 bytes，执行却仍使用旧
配置。原先五个 probe 没有覆盖这个时序，不能据其通过声称所有身份都已完备。

此处按父协调者要求冻结初版，没有悄悄修正实现。独立反例与修正版应分别保留。
若继续该方案，注册表应作为 `ParsedRegistry(bytes_digest, entries)` 不可变值读取一次，
并在准备时拒绝磁盘 hash 与已解析 hash 不同的状态。这样 bytes 与解析值才由同一
对象拥有。该修正是候选的待验假设，尚未在本版本执行。

## 接受的代价与替代方向

采用这条路线，可以先保护新运行的证据准入，暂时不移动几百个历史文件。
代价是历史模块依然可直接导入。它们的 ABI、`sys.path` 和精度边界尚未由注册表隐藏。
正式迁移仍需限制新调用者绕过协调者，否则只是在正确路径旁边增加了另一条路径。

完整包化会更直接地约束算法类型与内部导入，但一次移动大量旧文件会影响源码 hash
证书。这是需要另一个候选实测的结构取舍。本候选不读取或模仿另一候选的代码。
只增加文档是另一个替代方向，不能强制阻止能力与精度的错误组合，因此没有作为原型。

## 小步迁移草案

1. 先修复并验证注册表 bytes 与解析对象的身份问题，再让一个新合成命令使用协调者。
   历史证据只读，旧通过记录不换新源码标签。
2. 从一个注册表派生新命令的 doctor、依赖清单与 CI 目标。禁止新调用者另写 source 列表，
   并以当前五处源清单实现为观察基线，避免把不同用途的历史记录误删。
3. 通过同样的能力协议接入 HEIF 结构检查和 macOS 原生探测。各适配器继续拥有格式或
   framework 细节。不能因注册一项能力就把 prepared 改成 native-validated。
4. 如果原型证明算法内部类型错误仍是主要重复类，再对活跃模块包化。被冻结的历史
   实现留在只读 legacy 适配器后方。正式迁移与合并仍等待用户审查计划。

没有测量优化收益。70 是本次静态闭包文件数，190 是协调者初版行数，3 是能力项数。
这些结构成本可以重算，不等同于运行性能改善。
