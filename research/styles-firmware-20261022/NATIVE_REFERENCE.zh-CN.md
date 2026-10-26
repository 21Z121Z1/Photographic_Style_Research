# 当前原生参考与条件 UnderEye half 后端

当前原生执行条件已经打通。旧封存 dylib 没有被恢复或重建成相同身份。
新增 CPU 与 Metal 观测绑定各自的源码、运行系统和实际二进制身份，不回填历史 S33。
任务分支 `research/styles-native-reference-20261026` 承接 `076ef48`。
采用 pstack 的小步验证、Build the Lever 和 Type System Discipline，落实为可复跑 harness、证据读回工具及显式数值枚举；全程未调用 subagent。

## 环境与证据传输

官方 [公共仓库标准 runner 表](https://github.com/github/docs/blob/main/data/reusables/actions/supported-github-runners.md)
明确将 `xcode-27` 列为免费标准标签，且该仓库已核实为 public。
没有使用 xlarge、自定义或付费 runner，没有修改预算或安全设置。
官方来源 blob SHA 和仓库身份见 `evidence/native-reference-20261026/runner-policy.json`。

|实际预检提交|实际系统/架构|原生结果|
|---|---|---|
|`c949e4132c5f47c40c7ac426c39de4a56890a897`|15.7.9 / 24G830 / arm64|CPU 2047 sqrt + 1 pow；没有 TextureStyles 函数|
|`1aa3357c60274a0df7ab13bf64043e29bc98b01e`|26.6.2 / 25G83 / arm64|同域新 CPU 参考；没有 TextureStyles 函数|
|`0b371efabf85728b917374ced3bd6a5a1f91d180`|27.0.1 / 26A434 / arm64|找到 UnderEye/SkinSmooth/Mattify；Metal 为 Apple Paravirtual device|

每一行分别是新的当前调用，不继承其他系统的 libm 或 FPCR。
Cloud 代理拒绝连接 artifact 的 blob 域，未绕过该目的地。
新报告直接生成到 GitHub Checks 原生文本字段，由 API 读回。
CPU 报告绑定 Texture 报告 SHA，Texture 报告绑定共同 source manifest SHA。
`read_native_reference.py` 核对 Check 的 app、HEAD、payload SHA、Git 源文件、汇编窗口与全部数值比较。
上传内容为文本和合成数组编码；没有原照片、系统库、bitcode 或完整 shader。

## 原生 CPU 与 GPU 观测

以下稳定结果来自代码提交 `d68bf3abfc6c5ac97f9335458f052d74c1ac87fd`。
读回并重算时核对该提交的 392 份源码，未将旧 SHA 的通过记到新提交。

CPU wrapper 新执行 2047 次 f32 FSQRT，输入域严格为 half `0x3401..0x3bff`。
逐项 f32 和 half 输出与既有精确有理数 oracle 一致，差异为 0。
每次运算窗口前后 FPCR 实测均为 0，不设置 FPCR。
系统 `powf` 只对 half `0x2b8f`、`0x36aa` 精确扩成的 f32 输入调用一次。
实测返回 f32 `0x3e9da2ca`、half `0x34ed`；整数中点幂比较确认本输入正确 RN-f32。
实际 target UUID、offset、符号入口精度、compiler/产物 SHA 和自编探针反汇编均在 CPU 报告中。
它不是旧封存 shim 的 GOT 绑定，也不认证其他 pow 输入或历史调用。

Metal 库 SHA 为 `16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11`。
当前 UnderEye AIR payload SHA 为 `733e009ff75e519e644e4c6e9345ad8a57fdd3e3420094eb07f24f1c0714075b`，与已存 payload 身份一致。
记录了当前 llvm-dis 身份和算术 SSA 摘要；没有把不同 LLVM 文本 canonical hash 当作相同原文本。
FinalMix 使用 function constant 16=false，先检查 Metal reflection 的 active ABI，库 SHA 改变则拒绝运行。

两张 8×12 合成图分别为梯度与色彩边界。
从源图实际重算 portable GTM/LTM/人物/bright/writer 后，仅取实际写入 ROI。
9 组 mask/mix/strength 条件在两图上各执行一次，共 18 次图像 dispatch。
另 18 次 dispatch 将 source/edited 改为 0/1，保持 params/stats/masks，用于测量权重。
所以每个稳定任务共 36 次 GPU dispatch，而不是 36 张独立照片。
Edited、八张 matte、stats 均为明确的合成上下文；不代表真实人像分割或完整眼部上游。
原生输入、params、stats 的逐字 SHA 和输出哨兵检查均通过。

## 从连续残差到精确 half 条件后端

保留的连续 float64 模型在 12 组条件中逐位一致，空间 mask 的 6 组共有 337 个 RGB half 分量不同。
最大绝对误差 `0.00048828125`；每组 RMSE、分位数、分布和位差样例保存在报告中。
旧连续结果未删除，也未把误差低于 1e-3 改写为位级一致。

权重诊断显示，按所读 AIR 的 half 运算顺序计算权重可以解释该批原生权重。
新 `under_eye_half.py` 复用既有 `square132_contract` 的精确 Fraction/RN-half add/sub/mul/fma。
两次 FMA 分别计算 `fma(-w,X,X)` 与 `fma(w,E,previous)`，每次只舍入一次。
这比用 float64 近似 half FMA 更明确，但它仍是从有限原生观测中选出的 lowering 假设。
AIR fast mix 本身不唯一决定所有编译器、采样条件和输入的最终指令。

在新提交的当前原生运行中，新后端重算的 18 组图像共 5184 个 RGB half 分量逐位一致，1728 个权重逐位一致。
模型只使用原始输入，没有注入原生权重或其他中间数组。
这是一批有限 GPU 观测，不是任意图像、iPhone GPU 或完整摄影产品链证明。

后端要求显式 `HalfArithmetic.RN_GRADUAL_TWO_FMA`、全八张对齐 half mask、RGB 样本盒 [-2,2]。
颜色 primaries/transfer/reference 仍由调用者声明；本实验是未知 primaries、非线性 AIR output enum3。
它可通过 `run_conditional_texture(..., under_eye_arithmetic=...)` 与 SkinSmooth 最终混合组合。
默认 UnderEye 连续后端、旧 v3 和历史证书均未改成该新精度合同。
SkinSmooth 完整上游与 Mattify 仍不可冒充已经实现。

## 最小复现

从仓库根执行，输出目录必须不存在。Cloud 需要 Python 3.13、NumPy 2.2.4、Pillow 11.1.0 和 gh 的现有授权。

```sh
python3.13 research/styles-firmware-20261022/validate_portable.py /tmp/styles-native-check-new
python3.13 research/styles-firmware-20261022/read_native_reference.py \
  --head d68bf3abfc6c5ac97f9335458f052d74c1ac87fd --output /tmp/styles-native-readback-new
```

已有 Apple arm64 主机也可以直接执行；不发布 Check 是默认行为。

```sh
python3.13 research/styles-firmware-20261022/native_reference.py /tmp/styles-native-run-new
```

真实 CPU/GPU 收据、合成原始输入/输出和独立复验见 `evidence/native-reference-20261026/`。
`texture-report-d68bf3a.json` 同时包含连续模型残差、新 half 后端比较、权重诊断和算术来源。
`verification-d68bf3a.json` 证明 API 读回与 Git 源码、原生数值比较可重算。
最终 HEAD 的 CI 状态在 Draft PR 中单独核对，前述历史代码结果不转标。

没有测量或宣称性能优化收益。旧 master 缺少相同图像链路工作负载的对照边界仍保留。
报告中的命令耗时是本次采集成本，不能跨 runner 与 Linux 比成优化收益。
剩余产品缺口是完整 Texture 上游、拍摄端同帧 stats/真实语义上下文，以及全摄影链的原生参考；当前原生执行与文本证据回收不再依赖原 Mac 封存目录。

稳定代码的 152 项定向回归通过。Linux 全量 discover 实际运行 406 项，保留 8 个既有环境/私有材料 errors，未改 skip 或放宽阈值。
精确命令、运行时、日志 SHA、源码复验和文件索引见 `evidence/native-reference-20261026/index.json`。
最终交接与 CI 位于 [Draft PR #7](https://github.com/21Z121Z1/Photographic_Style_Research/pull/7)，以 PR 当前 HEAD 为准，不自动合并。
