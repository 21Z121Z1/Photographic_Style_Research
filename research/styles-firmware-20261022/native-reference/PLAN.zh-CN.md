# 新原生参考的执行合同

旧 S25/S33 封存产物不在可见工作区或 GitHub artifact 清单中；不重建旧身份。
新探针只执行 runner 自身的 Apple arm64 CPU 指令和系统 powf，另盘点实际 Metal 库。
CPU 报告的机器码、OS/build、compiler/产物 SHA、UUID、输入位型和 FPCR 均新绑定。
不把新参考作为旧 Mac、iOS 原插件、GPU 或完整摄影链的认证。

1. 阻断前置。先确认实际 Darwin arm64，再记录 Metal/device/framework/functions。
2. 独立工作。当前用户禁止 subagent；CPU 数学与 Metal 可用性由当前会话顺序实现。
3. 共享可变状态。一个专用分支；每个输出目录独占创建，运行前后比较源码 manifest。
4. 最小分解。先运行可用性与新 CPU 参考，再依据实际函数与 ABI 决定 GPU 执行，不猜兼容性。

sqrt 输入严格为 S32 的 0x3401..0x3bff，共 2047 个 half 位型。
新 wrapper 直接执行 FCVT→FSQRT f32→FCVT，每行在同一汇编窗口读取两次 FPCR。
不设置 FPCR，不调用旧 helper。用既有精确有理数 oracle 比较 f32/half 输出。
pow 只执行 half 0x2b8f、0x36aa 精确扩成的两个 f32 输入一次。
目标由当前系统 dlsym(powf) 解析，记录实际 loaded image UUID/offset 与符号精度。
用 c^853 与 f32 中点^2048 的整数比较判断本输入舍入，不调用 Python pow。

首轮使用标准 macos-15。实际只有 smartStyleOverlayPersonMask，无 TextureStyles 函数。
核实 actions/runner-images 官方清单后，第二轮改用标准 macos-26。
macos-26 实测同样没有 TextureStyles 函数。
进一步核实 github/docs 的 supported-github-runners.md，公共仓库标准免费表明确列出 xcode-27。
该仓库已核为 public，因此第三轮使用该标准 preview 标签，不使用 xlarge、自定义或付费 runner。
原先“不触发 xcode-27”的保守计划由这次官方计费身份核验取代，不修改预算/安全设置。
报告通过 GitHub Checks API 原生文本字段发布。它不是代理访问受阻的 artifact 下载目的地。
只发布本次生成的 JSON、公开源代码哈希及自编探针反汇编；不发布系统库字节或私人媒体。

GPU 合同在执行前固定。只有库 SHA 精确匹配 16a8a119... 时才运行已知 FinalMix ABI，
用 Metal reflection 检查 active texture/buffer 索引及尺寸，不兼容即阻断。
两张 8×12 合成图分别为梯度与色彩边界，先实际重算 portable source→writer，
只把写入 ROI 送入原生 FinalMix；不把未写边框当输入。
每图 9 组预声明条件，共 18 次 dispatch，包含零/full/spatial mask、mix 0/.5/1、strength 0/.5/1。
Edited=half(float64(writerRGB)*.95+.035)；八张 mask 与 stats 均为合成外部上下文。
输出先以 -99 填充，完成后检查未写 RGB；逐字核 native 读取的所有输入/params/stats SHA。
保存原生 half 输出、max/RMSE/分位数/分布/失败坐标及参数对输出的影响。
误差阈值固定 1e-3 仅用于列举失败坐标，不用于宣布完整 Apple 复现。

CPU 与 Texture 原始 JSON 分别通过两条 GitHub Check 文本发布，避免文本长度上限。
CPU 收据包含 Texture 报告 SHA；Texture 收据包含共同源码 manifest SHA，二者互相绑定。

发现空间 mask 下连续模型存在 337 个 half 位差后，新增同上下文的 0/1 权重探针。
每个条件多一次 dispatch，仅将 source/edited 改为全 0/1，params/stats/masks 保持原字节。
最终每次运行总计 36 dispatch，其中真实 source-to-writer 输入 18 次、权重诊断 18 次。
实际原生权重只用于误差归因，绝不补入主要独立模型。
额外记录原库选中 AIR 的算术 SSA 摘要、payload SHA 与 llvm-dis 身份，不上传完整 shader 或 bitcode。
