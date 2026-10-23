# 面向代理的架构改进规划

此目录只含历史调查、两种隔离结构原型、独立反例和待审迁移计划。现役数学实现未迁移。正式迁移和合并须经过用户审查。

初版原型与生成技能的完整合成输入、NPZ、诊断图和 PTY 日志保留在提交 `bc00b741219e7b9bced7dd9cf1d1cf6d38cd918d`。当前审查树保留摘要、清单和复现工具，避免重复展示相同 context。逐文件 bytes/SHA 与恢复方式见 [raw-artifact-index.json](evidence/raw-artifact-index.json)。例如：

```sh
git show bc00b741219e7b9bced7dd9cf1d1cf6d38cd918d:research/agent-architecture-plan-20261023/evidence/verification-skill/frozen-run/portable-smoke/terminal.log > /tmp/psr-original-terminal.log
```

旧证明仍属于它记录的源码版本，不能套给之后的提交。生成技能从当前 checkout 新建目录重跑，才产生当前 HEAD 的证明。没有原生参考的模型结果不会升级为 Apple 验证。
