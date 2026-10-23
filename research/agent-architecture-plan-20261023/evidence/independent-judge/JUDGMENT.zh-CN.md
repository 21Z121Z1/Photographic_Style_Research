# 两种初版架构的独立判定

结论为 **ISSUES：两个初版都不能原样采用**。建议修正 B 的配置身份问题后，把 B 作为阶段 0 的边界实验；A 的简洁调用界面可以借鉴，但当前同进程执行方式应拒选。此判定只针对初版提交 `bc00b741219e7b9bced7dd9cf1d1cf6d38cd918d` 中 A 的 `execution.py`（SHA-256 `de6ca894a0913ceb54b574516443e1426d00935869b3b2f05f44a362e42af4c4`）与 B 的 `coordinator.py`（`f5a469c9e2024927956fe72947644c67f622f1ec2d0f93a8c1d490507d84e268`）。后续修正版必须另行验收。

模型源码来自 `611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079`。实际环境为 Linux x86_64、Python 3.13.5。本次独立 judge 使用继承的可用模型，按固定版本 architect/arena/swarm/no-comments 技能进行评审；**没有跨模型多样性验证**，也没有把 Cursor slash 命令注册为当前执行环境工具。技能版本与完整判定见 [judgment.json](judgment.json)。

| 维度 | A：模块拥有执行 | B：注册表协调现有 CLI |
|---|---|---|
| 证据/能力边界，1/2 | 原普通拒绝检查保留 model/native 边界 | 原普通拒绝检查通过，但缓存策略可绕过新 availability |
| 源码/输入所有权，0/2 | 磁盘摘要不能代表已导入模块 | 新磁盘配置摘要可绑定旧内存策略 |
| 调用工作，2/2、1/2 | 示例 factory + run，2 次调用 | constructor + prepare + run，3 次调用 |
| 首次迁移成本，1/2、2/2 | 要补独立 worker、checkpoint 与 CLI 输出等价性 | 可先包装现有 image_chain_cli，保留算法与输出 |
| 失败可见性，1/2、2/2 | 黑域为 UnresolvedModel；缺文件可能直接异常 | 黑域为 unknown，真实 CLI writer=0 |
| 设计风险，0/2、1/2 | 磁盘与 import cache 分裂 | 磁盘与解析策略分裂；公共 snapshot/source_paths 可收回内部 |

评分是有据可查的评审判断：0 为阻断性不变量失败，1 为有条件满足，2 为本次范围满足。没有汇总成总体完成比例。

## 实际反例

**A：先导入，再改源码，最后 prepare。** 在独占临时 Git 仓库复制 514 个公开基线 Python 文件。先加载模型，再只把临时 `pixel_output.py` 的线性输出乘以 half 0.5，然后 prepare/run；另起新进程在同一修改后磁盘上运行。两次都返回 `RenderedModel`，记录的完整源码快照、helper 摘要、输入摘要一致，实际 writer 的 **36 个 half 分量不同，最大绝对差 0.15966796875**。这是执行身份反例中的人为行为变化，不是 Apple 误差。两次实际 portable 模型执行，原生产源码、作者原型均未修改，native 调用 0。[结果](frozen-replay/candidate-a-cache/result.json)

**B：先建立 Coordinator，再改配置，最后 prepare。** 仅修改独占 registry 副本，把 portable-image 的 availability 从 runnable 改成 prepared-only。旧对象实际运行 2×2 CLI 并返回 `model_only`；同一磁盘配置的新对象返回 `blocked`。两份 request 都绑定修改后 registry 的 SHA-256 `91bf4dec8141ffc23684f7522062afb4593c29d8be3998257d35f4ec2e4565fb`。两次请求、一次实际 CLI 执行，native 调用 0。[结果](frozen-replay/candidate-b-cache/result.json) 独立 root 先前的同类反例也已核对：[原收据](../root-review-registry-cache/result.json)。

**失败状态保留。** 使用冻结初版与公开基线的独占副本，A 的公开 context 中 primary/linear RGB 置零，B 使用合成 zero 2×2，均选 bright16。A 返回 `UnresolvedModel`，B 返回 `unknown`，真实 CLI summary 的 writer 数量为 0。两次实际模型/CLI 运行，native 调用 0。[结果](frozen-unknown/unknown-results.json) 这只验证该黑域负例传播，不涵盖完整 mask、非有限值与参数矩阵。

作者原始证据中 A 的 5 项测试与 12 像素模型运行通过；B 的 7 项测试与 4 像素真实 CLI/四种拒绝请求通过。独立复核添加的上述反例说明原测试集合不足。A 原来捕获 698 个源码文件，B 静态闭包为 70 个；A 只保存 writer.npy 和 receipt，B 保存现有 CLI 的 NPZ、PNG、分支与来源报告，二者工作量不同，**不能比较速度或据此宣称优化收益**。

晚于冻结反例的共享工作区单测另记为诊断：[A 日志](a-unittest.log) 为 5 项中 3 项通过、2 项 ERROR，原因是别的代理清理了 tracked evidence `frozen-helper-source.py`，A 的广域源码收集直接读到缺失路径；[B 日志](b-unittest.log) 为 7 项通过。这两次没有捕获运行前后完整源码清单，且存在并行改动，不能替代冻结源码验收，也不能把 A 的 dirty-worktree 错误写成原初版干净检出的结果。

## 阶段 0 的必要边界

1. 配置 bytes 只读一次，同一不可变拥有者保存解析结果和 digest。prepare 前变更应拒绝，或原子重载；prepare 后变更应在 CLI 前拒绝。新对象读到 prepared-only 必须直接 blocked。保留旧失败证据，在新 SHA 回放同一反例。
2. 实际模型执行使用每请求新进程或受控不可变 loader，并绑定源文件与输入载荷。单靠执行前后磁盘 hash 无法证明已加载代码身份。B 的新进程 CLI 能避开 A 的已观测缓存问题，但仍不能把可写磁盘当数学意义的不可变快照。
3. 保留现有 CLI 的逐阶段 NPZ、分支原因、PNG、raw-domain 参数和 unknown；不能为减少调用次数丢失这些产物。公开 Python dataclass、类型注解或 `__all__` 不能独自承担编译期不变量证明。
4. 70 文件闭包覆盖当前普通 import 和字面 `.py` 载入线索。对未声明的计算式 import 应拒绝或要求 capability extension；它不是通用 Python 依赖闭包证明。无关证据脚本也不应自动成为算法源码依赖。
5. 缺失源码/输入应成为明确 typed blocked 结果；保留历史科学 manifest，新运行身份另建记录。CPU/GPU 原生成功类型仍不能开放，直到实际二进制身份、运行时绑定、输入/返回位型、精度和舍入环境具备相应原生证据。

第一迁移单元只需新增协调边界、配置 schema 和回归入口，包装现有 `image_chain_cli.py`；算法、历史 profile/manifest 可保持冻结。后续把 doctor/CI/文档的手写当前能力信息逐步改为该同一来源的派生结果，并收回原型的 source_paths/snapshot 公共界面。A 若将来复用 facade，还需独立 worker 和与现 CLI 产物等价性；本次不估算未经测量的工期。正式迁移、合并仍须计划审查。

在本次已检查范围，没有另外独立复现的关键阻断；这不构成穷尽正确性、安全或完整产品证明。未测试 Apple 输出准确度、原生 pow/sqrt 全域、GPU、产品摄影质量、同条件 main 性能收益。

## 精确复现

在仓库根执行；输出目录必须是不存在的新路径。脚本用 `git show` 固定初版候选及公开模型源码，不会回退工作区或读取正在修改的 B。

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  /usr/bin/python3.13 research/agent-architecture-plan-20261023/evidence/independent-judge/reproduce_boundaries.py \
  research/agent-architecture-plan-20261023/evidence/independent-judge/replay-new

PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  /usr/bin/python3.13 research/agent-architecture-plan-20261023/evidence/independent-judge/probe_unknowns.py \
  research/agent-architecture-plan-20261023/evidence/independent-judge/unknown-new
```

默认候选 commit 为 `bc00b741219e7b9bced7dd9cf1d1cf6d38cd918d`；模型基线为 `611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079`。命令、日志摘要、源文件与输入摘要见对应 result/manifest，关键交付摘要见 [artifact-manifest.json](artifact-manifest.json)。
