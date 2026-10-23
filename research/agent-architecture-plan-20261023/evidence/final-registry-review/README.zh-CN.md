# B 修复独立复核

修复的有限目标通过独立复核：已载入配置与收据中的 registry 身份来自同一份 bytes；在 `prepare` 前和后修改独占配置副本，均未执行 CLI。9 项测试通过；另一次真实 2×2 色块 CLI 写入 4 像素，结果仍为 `model_only`，Apple 原生调用为 0。源码前后哈希一致。

本轮收据记录的仓库 HEAD 是 `357a82cab5404f47d15ca1ff4b4ed25f06f0b8ec`，修复仍是工作区 bytes。被测 `coordinator.py` SHA256 是 `8e13fffc142cbafe30bc04321006c3f53ffe4d6075b27f348f75563d546683a5`。这份记录绑定具体源码 bytes，不是该 HEAD 的完整验收，也不能套给未来提交。命令、环境、源码身份、结果和异常检查见 [review.json](review.json)，原始日志和合成输入/输出见 `run/`，哈希见 [manifest.json](manifest.json)。原版反例未改动。若原始 `run/` 以 ZIP 交付，解包后须保持原相对路径；manifest 仍对应这些解包文件。

独立异常探针补充了一个非阻断原型限制：`prepare` 后删除输入文件，`run` 抛出 `FileNotFoundError`，已建立输出目录但未写收据，也未执行 CLI。构造时 registry 缺失、JSON 损坏、必填字段缺失，同样以异常拒绝；`prepare` 后删除 registry 则返回 `blocked` 并保留收据。正式迁移应把这些运行故障统一为保留部分证据的强类型结果，不能把当前原型当作所有错误路径已产品化。

原型仍没有任意 computed import 闭包证明、并发修改原子性证明、pycache/source-only 执行身份保证或 Apple CPU/GPU 数值验证。子进程只避开了已证实的长进程内存模块缓存问题。这些是正式 worker 的验收条件。

复验命令使用新的输出目录，保留本轮证据：

```sh
/usr/bin/python3.13 -m unittest discover \
  -s research/agent-architecture-plan-20261023/prototypes/candidate_registry \
  -p test_coordinator.py -v
/usr/bin/python3.13 research/agent-architecture-plan-20261023/evidence/registry-fix-round/replay_registry_drift.py \
  --output research/agent-architecture-plan-20261023/evidence/final-registry-review/new-drift-run
```

`review.py` 是本轮单次审查驱动源码；它拒绝覆盖已有 `run/`。评审只写本独占证据目录，未修改作者实现、生产模块、旧收据或任何安全/预算设置。
