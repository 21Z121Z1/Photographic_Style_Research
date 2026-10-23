# 待审计划：先统一运行与证据所有权，再收拢现役计算 API

建议先把现有图像 CLI 放进一个有明确能力、输入、执行身份和结果类型的运行边界。以修正后的注册表原型 B 做阶段 0，借鉴 A 的互斥结果类型；A 的同进程执行方案暂不采用。第一步不搬数学文件、不重写冻结 profile，也不重构整个 macOS app。本分支实现了调查工具、两种原型、反例及修复回放、真实 CLI verification skill；正式迁移和合并仍待用户审查。

## 基线与可用证据

历史统计固定在 `611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079`，共 280 个祖先提交、3628 个文件。之后已承接实现基线 `3aae24d96b1807c9d6c48ce09c4760c8350e650d`。该版本已有逐阶段图像 CLI、合成矩阵和 15 个模块干预入口；本计划不把它们重新列为待实现。最初实验的 611 收据保留原身份，最终检出版本另跑 [check_plan.py](tools/check_plan.py)。

|来源|真实覆盖|可以支持的判断|
|---|---|---|
|Git 原始提交、源码及历史收据|固定树、24 个故障源码锚点；[ledger](evidence/history/incident-ledger.json)|仓库发生过的具体失误与边界；提交作者不能证明代理归因|
|PR #1/#2/#3|9 个评论/审查集合均为空；公开 issues 排除 PR 后为 0|没有可用于归纳用户 review 偏好的反馈样本|
|聊天与会议|Slack 连接未完成、原 Cursor corpus 缺失；3 次相关 Pages 查询无相关结果，读取正文 0|归因和偏好学习缺口；不能声称已 recall 全部历史|
|两个隔离原型及独立 judge|真实模型/CLI、相同意图与身份反例、黑域负例|结构方案的局部可行性与已证失效；不代表完整 Python 闭包证明|
|生成的 [verification skill](../../.cursor/skills/verify-photographic-style/SKILL.md)|实际 PTY→CLI→checkpoint→inspect→拒绝伪证据→cleanup|portable 产物与证据合同；没有 Apple 参考比较|
|最新实现 CI|3aae：117 scoped checks 通过；标准 macOS 15 collector 编译/静态检查通过|编译前提已真实运行；collector 执行、原 pow 调用、目标运行时绑定均为 0|

技能流程来自 `cursor/plugins@00d5decc6f05669044fd092dec73da9ef6f7eec0` 的 poteto-mode、correct、architect、recall、create-verification-skill 及依赖。当前运行时没有注册 Cursor slash 命令，原定 Claude/Grok 不可用，各独立代理继承可用模型；没有跨模型多样性验证。用户的计划审查门槛覆盖 playbook 默认的自动迁移/merge。

## 重复问题与结构观察

[原始证据和复现](evidence/history/FINDINGS.zh-CN.md)严格分开受影响路径、实际运行失败数和纠正提交数。8 条记录不能称为 8 次代理失误，也不足以给“代理最常犯的错误”排名。可确认同机制在两条独立引入路径中出现的只有前两组；都不证明修好后再次复发。

|问题组|计数单位与原始事实|已有结构与下一步|
|---|---|---|
|执行输入生命周期|S21/S22 两个 harness 编译临时 `0.ll`，后来精确原件不可用；共同修正提交 1 个|复用现有 `Archive`，禁止新 runner 编译未封存字节；未恢复的旧 IR 保持缺失|
|观测器副作用摘要|两个生成器加入全局 trace store 后保留 LLVM `memory(read)`；独立引入路径 2、共同修正提交 1、原运行数未知|新 instrumenter 由实际 effect 派生属性；真实历史生成器合成 IR 回放为 false/true/false/true，未新编译 LLVM/Apple|
|原生构建边界事件族|S96 argv 混入 `.inc/.json`/旧 TU，S108 ARC 指针转换；两个实际编译失败、不同机制|typed `ProbeBuildSpec` 分开 TU、include/data、SDK、arch、ownership；不能宣称一个类型已证明挡住整个事件族|
|外部表示边界事件族|S29 half `0xca00` 误标 -6，实为 -12；S33 字符串 regex 漏零填充地址；两个不同机制|从 `HalfBits`/整数 `Address` 派生标签，保留编码与域；实际公开 bits 和历史 parser 回放通过，未取得私有表|

结构测量另有 55 个 Python 文件编辑 `sys.path`、29 个调用 `exec`、4 个 AST/FunctionType 克隆点、19 个 `glob('*.py')` 源码身份所有者。这些是维护面，不能换算成缺陷数。优先减少现役入口的重复所有权，冻结研究脚本留在原位。Swift `CommandSpec` 参数数组、`ProcessRunner`、现有 `tools` 包和 Archive 均予保留。

## 用原型解决的选择

|方案|实际接口与初版结果|独立反例与决定|
|---|---|---|
|A：单一领域包直接执行|factory + run 两次调用；5 个原测试、12 像素 writer；初始保守绑定 698 份源码|临时副本先 import、编辑 helper、再 prepare：相同完整磁盘/输入快照的两次执行仍被接受，36 个 half 分量不同，max abs 0.15966796875；拒绝同进程执行方案|
|B：能力注册表协调真实 CLI|constructor + prepare + run 三次调用；7 个原测试、4 像素 writer；当前静态闭包初次 70 文件|旧对象使用旧内存策略却绑定新 registry hash；两个初版均拒绝原样采用。B 同 bytes 解析/hash 修正后 9 项测试与同一漂移反例通过，独立复核保留 model_only|

[初版独立判定](evidence/independent-judge/JUDGMENT.zh-CN.md)、[修复红/绿](evidence/registry-fix-round/summary.json)、[独立修复复核](evidence/final-registry-review/review.json)分别绑定源码 SHA。B 修正版 `coordinator.py` 为 `8e13fffc142cbafe30bc04321006c3f53ffe4d6075b27f348f75563d546683a5`，没有把旧反例改写为新通过。原版坏配置准入真实运行一次 2×2 CLI；修正版漂移在执行前拒绝。A/B 均保留不支持黑域：A 为 UnresolvedModel，B 为 unknown 且真实 writer=0。

选择 B 是因为它能保留现有 CLI 的 NPZ、PNG、checkpoint、分支与报告，首个迁移单元不用修改数值实现。A 直接模型+NPY 与 B CLI+全产物工作量不同，时长不能比较。将 A 的 `RenderedModel | UnresolvedModel | Rejected` 思路移入 B 的正式结果合同，收回 `snapshot/source_paths` 公共方法；不把 registry 变成另一个需要 caller 同步的清单。

修正版 B 仍是原型：输入准备后被删除会抛异常并留下无收据目录；静态 import/字面路径分析不覆盖任意 computed imports。A 的 tracked-file 集合也不覆盖 untracked imports，且曾因 tracked-deleted 的证据脚本连带失效。以上限制已由实际复核或接口机制确定，不能靠 5–9 个测试宣称通用闭包认证。

## 迁移次序、成本和验收

成本以下用具体接入面和必要验证表达，不估未经测量的工时或收益。一次只合入一个可回退的现役单元；任何科学数值变化单独审查。

|顺序|一个可审单元与成本|必须通过的验收/回退|
|---|---|---|
|0：运行所有权|新增一个支持 API、registry schema、worker、结果 schema；先包装 `image_chain_cli`，随后接 `module_sensitivity`。保持算法/profile 文件不动|同 bytes 配置与 hash；输入封存；漂移 before/after 拒绝；缺件/异常产生 typed blocked/error 与部分日志。原 CLI 输出合同相等。失败时停止新入口调用、保留旧 CLI 和失败收据|
|1：身份与能力派生|doctor、当前 CI、现役验证入口读取同一能力描述；接入 `image_chain_cli`、`module_sensitivity`、`validate_portable`、`bound_validation` 的现役身份生成规则，各自科学范围仍独立|native 请求不能降级 portable；编译与运行分状态；实际导入模块及运行环境可追踪。迁移 caller 与删除其重复现役规则同一变更完成，历史 catalogs 不动|
|2：观测与外部格式|抽出一个 instrumenter effect owner 和两个窄类型边界 `HalfBits`、`Address/Section`；先迁移两条已证生成器的现役后继|实际旧生成器 red、修正版 green；编码标签一致；不改变历史数值/profile。构造无 store 负例，防止无条件乱改属性。旧版本仍按原 SHA 可恢复|
|3：构建前提|把新 probe 接到 typed `ProbeBuildSpec`；先覆盖一个 collector 与一个 Objective-C probe，不批量改 100 多个历史 workflows|TU 不含数据/include；编译-only 标准 runner 先跑，ARC/SDK/arch 明示；保留真实原生缺件状态。3aae 的 macOS15 编译成功可作现状，不能套到原 S33 目标运行|
|4：现役计算 API|只把 supported facade 的 context、buffer、domain、precision、selection 做强类型；复用现有 validated Context。迁移当前 image/module caller 后才收拢内部 imports|新静态类型检查与依赖边界检查只覆盖该包；raw 参数不是产品滑杆；half/f32、线性/非线性域、范围和未知原因明确。AST clone 替换要新数值版本及逐阶段相等性证据，不能仅更新 SHA gate|

正式 worker 的验收不能止于“新进程”。长寿命 import cache 的已证反例必须重放；新进程仍可读 timestamp/size 旧 `.pyc`，应使用每 run 新 pycache/source-only 加载或不可变源码快照，并核模块 `__file__`、扩展库/NumPy/解释器身份。对未声明或越界导入拒绝运行，覆盖集合只能叫“受支持执行源码集合”。本轮未实现不可变 Python worker，也没有数学全程序证明；原型的静态闭包只为界定第一单元成本提供数据。

第一迁移验收矩阵复用现有梯度、曝光、色块、边缘、程序 mask、参数端点、分支边界、half/f32、零/非有限值、缺失 mask 与负例。保留全部 unknown、失败样例和非零退出码，不要求每个参数在所有图案上改变 writer。Skin theta 在一张梯度无最终差异与另一个激活用例有差异可以同时成立。合成 mask 只验证处理逻辑。

## 执行性约束优先于规则文档

|容易复制的错误|优先强制方式|保留的人类审查|
|---|---|---|
|模型/编译结果冒充原生或产品验收|互斥结果 schema、能力意图不可降级、序列化负例；当前 skill 已拒绝伪 Apple 标签|新增证据类别及其真实作用域|
|新磁盘身份套旧配置/执行|单一 owner 捕获字节、受控 worker、同输入/源码漂移回放；旧清单不可改写|支持源码集合与运行材料来源|
|观测器修改了 effect 却留旧属性|由 effect 派生属性、真实历史红/绿回放|新 instrumentation 语义与编译条件|
|手写 bits/数值标签相互矛盾|解析类型派生标签，property tests/精确域枚举|新输入域与舍入前提|
|缺测变绿|CI 区分 scoped portable、compile-only、native blocked；最终 HEAD receipt|验收门槛和例外范围|

新增文档限于支持入口、精度与证据域，以及实际执行过的 verification skill。对能由代码/类型/CI 表达的内容不再堆 AGENTS.md。TLA+ 暂不引入：目前高价值缺陷是具体字节/loader 所有权，尚无需建模的并发状态协议。

## 性能与材料边界

单次 Linux x86_64、Python3.13 cProfile 对 4×6 合成 CLI 的诊断中，`leaf_numeric.V.__post_init__` 调用 75,082 次（[profile](evidence/profile/profile-summary.json)）。这支持把后续性能问题定位到数值对象/舍入工作量，而不是假定搬包能加速。仪器化时长不是产品延迟；没有本分支对 main 的同条件优化收益，A/B 产物不同也不可比。主实现与 main 缺同等模型入口的比较保持 n/a。

未来优化单独实验：同机、同解释器/依赖、同精度/输入/产物、交替执行 main/候选至少 5 轮，记录 wall/CPU/RSS、原始每轮值和波动；基线无相同能力时明确 n/a。禁止从不同机器数据推出收益。优化须通过原阶段数值合同和未知传播后才能合入。

原 Apple pow 的目标二进制、UUID/GOT/实际绑定、参数/返回位型及实际舍入环境仍缺。Linux libm 不补此证据。S30 有限 source-context、S32 的 2047 输入假设和 S33 的单次 sqrt/FPCR 作用域均保留；cast0 的 skin writer 不能成为 bright writer 证明。macOS15.7.9/arm64 编译 collector 不能替代历史 Mac27/26A434 私有实现调用。新计划没有私人媒体/聊天明文/系统 binary，也没有外发消息、付费 runner、预算或安全设置更改。

## 最小复验与审查决定

```sh
python3.13 -m pip install numpy==2.2.4 Pillow==11.1.0
python3.13 research/agent-architecture-plan-20261023/tools/check_plan.py \
  --output artifacts/architecture-plan-new
```

首次安装依赖应在一次性 venv，输出目录须不存在且位于检出目录。总入口执行 5 个 A 测试、9 个修正 B 测试、历史 replay、冻结初版反例、B red/green、真实黑域、verification skill 与 expected-blocked native preflight；每步命令/日志/hash、运行前后源码和当前 HEAD 写入新 receipt。标准 Ubuntu scoped workflow 执行同一命令。它不运行全仓测试，也不认证 Apple。

需要审查的是阶段 0 的支持入口与能力/结果合同，以及上述迁移顺序。计划审查通过后才实施正式重构；本 Draft PR 不自动合并。
