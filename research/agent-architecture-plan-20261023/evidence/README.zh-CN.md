# 证据索引

历史账本与初版判定、修复红绿及独立复核各自绑定源码 commit 或 working-bytes SHA。旧结果没有重写为新版本。

- [历史与反馈覆盖](history/FINDINGS.zh-CN.md)及 [结构统计](history/inventory.json)。
- [两初版独立判定](independent-judge/JUDGMENT.zh-CN.md)，冻结初版反例和黑域结果仍按原路径保留。
- [B 修复红/绿](registry-fix-round/summary.json)与[新独立复核](final-registry-review/review.json)。
- [单次诊断 profile](profile/profile-summary.json)，不作性能收益比较。
- [生成技能原始证明](verification-skill/index.json)，原完整字节按[旧索引](raw-artifact-index.json)从 bc00b741 恢复。

重复的合成 context、NPZ、PNG、临时源码副本及终端日志压缩为各证据目录内 `raw-synthetic-evidence.zip`；[成员路径/hash索引](synthetic-archive-index.json)可逐个核对。压缩不修改原 result/manifest；需要检查旧 manifest 全部文件时，将相应 archive 解压到新目录，合并保留的摘要文件，保持相对路径。部分旧摘要中的绝对路径只是当时执行位置。不要把解压后的旧文件覆盖作者源码或新运行证据。

最终 HEAD 的 scoped 自动回归输出在 GitHub Actions artifact 中，使用 README 中的一条命令可在新目录重建。artifact 中包含真实 CLI 原始产物和完整 before/after 源码清单；native preflight 的预期 blocked 与通过 portable 检查分别记录。
