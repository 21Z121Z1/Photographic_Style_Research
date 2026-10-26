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

GitHub runner 仅为标准 macos-15，不触发 xcode-27、自定义、付费或 larger runner。
报告通过 GitHub Checks API 原生文本字段发布。它不是代理访问受阻的 artifact 下载目的地。
只发布本次生成的 JSON、公开源代码哈希及自编探针反汇编；不发布系统库字节或私人媒体。
