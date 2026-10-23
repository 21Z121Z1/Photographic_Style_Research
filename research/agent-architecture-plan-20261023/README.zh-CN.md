# 面向代理的架构改进规划

此目录只含历史调查、两种隔离结构原型、独立反例和待审迁移计划。现役数学实现未迁移。正式迁移和合并须经过用户审查。

先读 [待审计划](PLAN.zh-CN.md)，来源与原始反例从[证据索引](evidence/README.zh-CN.md)进入。生成的 [verification skill](../../.cursor/skills/verify-photographic-style/SKILL.md)实际驱动研究 CLI。

```sh
python3.13 -m venv /tmp/psr-plan-venv-new
/tmp/psr-plan-venv-new/bin/python -m pip install numpy==2.2.4 Pillow==11.1.0
/tmp/psr-plan-venv-new/bin/python research/agent-architecture-plan-20261023/tools/check_plan.py \
  --output artifacts/architecture-plan-new
```

两个新目录均不得存在。总入口写当前 HEAD、源码前后 hash、命令/日志、真实 CLI 产物与各步状态。预期坏版本退出 1、原生缺件退出 2 分别记录；不把它们算作 Apple 通过。只跑计划范围，不跑全仓测试。

初版原型与生成技能的完整合成输入、NPZ、诊断图和 PTY 日志保留在提交 `bc00b741219e7b9bced7dd9cf1d1cf6d38cd918d`。当前审查树保留摘要、清单和复现工具，避免重复展示相同 context。逐文件 bytes/SHA 与恢复方式见 [raw-artifact-index.json](evidence/raw-artifact-index.json)。例如：

```sh
git show bc00b741219e7b9bced7dd9cf1d1cf6d38cd918d:research/agent-architecture-plan-20261023/evidence/verification-skill/frozen-run/portable-smoke/terminal.log > /tmp/psr-original-terminal.log
```

旧证明仍属于它记录的源码版本，不能套给之后的提交。生成技能从当前 checkout 新建目录重跑，才产生当前 HEAD 的证明。没有原生参考的模型结果不会升级为 Apple 验证。
