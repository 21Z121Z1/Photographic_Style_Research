# 封存 CPU shim 的单次 pow 运行时绑定

`pow_runtime_binding.py` 和 `pow_read_call.c` 为下一次**新的当前调用**准备了收集器。本 Cloud 是 Linux x86_64，且没有原私有封存 dylib；原生编译、加载和 pow 调用均为 **0**。新增测试使用程序生成的 Mach-O 形状和报告，不能当作 Apple 运行结果。原 S33 只观测 sqrt 的边界继续保留。

预先核对的候选来自 S31 `square132-proof-s31b.json`，不是历史 pow 调用记录：base 为 **half `0x2b8f` = 1935/32768**，指数为 **half `0x36aa` = 853/2048**。两个 half 精确扩为 f32 时分别是 `0x3d71e000`、`0x3ed54000`。理想实数幂正确量化后的 half 是 `0x34ed`；既有两种 mix 合同都给 square132=`0x3400`，相等选 low。这一候选在真正原生执行前仍只是条件前缀见证。

收集器只接受 SHA256 为 `47185c09c0407d7c96aa9dc55e0581ae4e781836951c8b236d17f2ac6f8efbbe` 的原封存 CPU 重编译研究产物。先按实际 `LC_SYMTAB` 确定 `_psr_pow_scalar` **入口**，再验证该函数内 `0x15904` 的 tail branch、`0x16244` 的 ARM64 stub、stub/GOT 的共同 indirect-symbol index136 和 `_powf` 字符串。`0x15904` 只由旧记录确认是分支地址，不能预先冒充函数入口。未知 stub、指针认证形式、改变的 SHA 和其他架构均拒绝；没有 `dlsym("powf")`、Linux libm 或另一个系统的替代路径。

运行前必须显式提供期望的 Apple OS build。新的私有目录在 Git checkout 外创建，持久保存源码、原封存副本、编译命令、编译器 SHA、`otool` 反汇编及日志；不覆盖已有目录。按真实编译后指令确认两次 `MRS FPCR` 内有两次 half→f32 转换、一次同步 BLR 和一次 f32→half 转换，没有引入 FPCR setter。运行标记在任何会加载原产物的进程启动之前独占写入；异常或不明结果不得自动重试。

当前实际 GOT target 在调用前后读取，记录其加载镜像 UUID、镜像内偏移、basename、符号及是否精确位于该符号入口。若 `dladdr` 仅给近邻符号，明确标 `nearest_symbol_only`。系统 dyld-cache 镜像可能没有独立磁盘文件，因此 target 单文件 SHA 保持 null，不伪造它；加载 UUID、OS build 和实际 target offset 是本次运行身份。这里只能绑定调用前后 FPCR，不能排除系统函数内部临时改模式再恢复。

原生返回结果不需要“预期通过”才能保存。验证器用精确整数幂比较 `c^853` 和 f32 舍入 cell 两个中点的 `2048` 次幂，分别判断**这一个输入**的返回 f32 是否为正确 RN，以及最终 half 是否符合原条件证书。没有调用 Python 浮点 pow。即使两者通过，也不推及其他输入、历史调用、GPU、整个 bright helper 或完整图像链。

Cloud 最小复核：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p test_pow_runtime_binding.py -v
python3 research/styles-firmware-20261022/pow_runtime_binding.py preflight --output /tmp/pow-preflight-new.json
```

仅在已有原私有封存产物的匹配 Apple arm64 主机运行一次（路径和 build 由真实材料指定）：

```sh
python3 research/styles-firmware-20261022/pow_runtime_binding.py run \
  --binary /private/path/to/original-sealed-trace.dylib \
  --expected-os-build ACTUAL_VERIFIED_BUILD \
  --private /private/path/to/new-task-owned-pow-run \
  --output /private/path/to/new-pow-summary.json
```

若任一步失败，保留该目录及日志，人工复核后再决定独立的新实验。不要把私有目录、dylib、系统二进制或私人照片上传。普通免费 GitHub macOS runner 不能凭空恢复这个未上传的封存产物；改用 runner 自身另一个 OS 的 pow 不能沿用原结果身份。现有 `xcode-27` 标签也不是免费标准 runner 的证明，本轮没有提交或启动该标签的任务。
