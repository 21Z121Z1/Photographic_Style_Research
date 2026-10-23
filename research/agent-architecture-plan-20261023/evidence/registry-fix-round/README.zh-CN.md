# 注册表身份修正回放

这里只修正候选 B 的已证实缺陷，未修改生产模块、历史证书或初版证据。

- `red-original/result.json`：从 `bc00b741219e7b9bced7dd9cf1d1cf6d38cd918d` 提取原协调者，真实 2×2 portable CLI 重现旧对象执行旧配置、快照绑定新磁盘 bytes。预期退出码 1。
- `green-fixed/result.json`：相同回放在修正版通过，构造后和准备后变更均拒绝；新对象执行新配置的 prepared-only 准入。
- `tests-green.log`：9 个行为测试通过，包括现有真实 2×2 CLI。目标 Apple 调用和原生比较为 0。
- `summary.json`：精确源码、日志 hash、命令、环境和边界。源码副本在各回放目录中冻结，不能把初版或工作树结果改标为未来提交通过。

从仓库根复验，使用一个尚不存在且位于仓库内的输出路径；原有证据目录不会覆盖：

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /usr/bin/python3.13 \
  research/agent-architecture-plan-20261023/evidence/registry-fix-round/replay_registry_drift.py \
  --output research/agent-architecture-plan-20261023/evidence/registry-fix-round/recheck
```

加 `--revision bc00b741219e7b9bced7dd9cf1d1cf6d38cd918d` 可重放红阶段。
这是受限 runner 原型的输入/执行身份修正，不是任意 Python 源闭包或完整产品的证明。
