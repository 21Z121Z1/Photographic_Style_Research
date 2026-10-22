# S11-B：复用皮肤算法的精度适配与 highlightRecover

同一 iPhone17,3 / 24A446 AIR10。`skin_contract.py` 核验旧 `semantic_skin_model.py` 指向的 AIR 文件 SHA `9ce57a…`，其完整 renderSkinAdjustments 与本版仅有常量文本表示和属性/metadata编号差异；按 typed half/f32 编码归一后完全相等。不是凭 V1 名称判断版本。归一及两个原函数 SHA 保留收据，未复制原 AIR。

旧连续模型不改动；`pixel_skin.py` 是该算法的 half/f32 精度适配，保留原门及指令次序。皮肤亮度复用 `local_contrast`：静态逐指令双射证明该分支与 BG local 只差最后保护混合权重（BG0，skin1）。颜色继续旧 luminance/chroma/tint 方程，按原 AIR 拆出 half 运算及 f32 权重转换。没有重新拟合皮肤模型或创建新逆解。

新增 highlightRecover 完整条件模型，复用 whites 的前/逆矩阵和算子原语，保留 pow、正分母门、half/f32、颜色域与零点拒绝。其主入口 strength 固定 half2，两个 undef 参数确实没有被原 helper 消费；未将它们当辅助图已恢复。

新增完整原 helper 宿主小批次：

| helper | 调用 | 点/集合 unknown | 已知域 half 位差 | 最大绝对误差 | 已知集合越界 |
|---|---:|---:|---:|---:|---:|
| renderSkinAdjustments | 24 | 4 / 4 | 2 | 0.000244140625 | 0 |
| highlightRecover | 8 | 1 / 1 | 0 | 0 | 0 |

4个 skin unknown 是黑色且颜色系数活跃，归一化分母为零；highlighter 的黑色/guide≈.7样例在 half 中间转换出现非有限值。未缩 mask、未排除失败案例，宿主有限输出也不替代模型定义域证明。颜色系数还覆盖±非零及严格门内控制，黑色、灰色和不同颜色输入全部保留。位差没有修成“通过”；2u/4u 宿主包络为假设，不能视作 GPU 精度保证。

主入口实际是分叉，不能误串成 skin→highlight→bright：

- skin393 输入392、肤色95、guide350；highlight394 输入skin393，395以half.5混合，398按castType==2选中。
- bright400 **也直接输入skin393**，另收工作RGB286、人物96、肤色95、曝光399和stats18；404仅在castType==16时选400，否则选393，再进neutralizing408。
- highlight的398另在SSA476的cast分支继续消费；它没有被喂给bright400。

本阶段仅完成前两项条件模型；bright、neutralizing/warmth/selective-color及外围混合仍在继续，AIR7生产/滤波与原GPU/同帧依赖不变。24个全激活组合集合 unknown、早先8个叶域 unknown 均不改记通过。

118项回归通过。收据 `evidence/skin-contract-s11b.json` / `native-skin-highlight-s11b.json` 含版本/输入/原函数/模型/宿主哈希。复验：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/skin_contract.py research/vm-native/model-v10/0010.ll /path/to/0010.ll.txt /tmp/new-skin-contract.json
python3 research/styles-firmware-20261022/native_skin_highlight_check.py /path/to/0010.ll.txt /tmp/new-skin-highlight.json
```

无新下载、私人媒体或GPU运行；未重跑旧批次。照片逆解未完成。
