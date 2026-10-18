# bit-exact 研究收尾（用户决定停止继续追逐）

收尾 UTC：2026-10-18T13:35:15.329583+00:00。源码基点 **76f41321f9e92a7400a7ca6274ea8a143814c35c**；macOS **27.0.1 (26A434)**、xcode-27、镜像20261012.0260.1、Apple Paravirtual Metal。未修改冻结V1、原件或未跟踪consumer-goto-v8文件。用户认可当前精度并转向人物/皮肤语义风格与人脸提亮；本方向不再安排新精度实验。**不降低旧门槛，acceptance_complete=false 保留。**

## 最终证据纠正

最后已排队的run [39121521190](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39121521190) 虽然job为failure，但最后artifact比早先状态多两项进展：

- **已验证（数值）**：同一MSL source `positive-f34-canonical-1` 在五图×tone 0/+.35/−.35共15个完整512×384捕获配置，RGB half不同分量均0、max abs=0、PSNR=inf。source SHA `f9d48aa40ae47a533cf8d57fd1f9d5460524139abbf106212e55c7b7a251e407`。ShadowsNegative f33与正tone Shadows f34分别显式half五项和/乘加舍入，lighten f32保持原算法；没有按照片换公式。源在发现IMG_2600通过后冻结，随后4图含两张留出。
- **已验证（数值）**：oracle-replacement control把Capture.expected替换为全零后，4096发现像素的预测对原预测half不同分量0、max abs=0。这是已通过的既有独立性对照，不再写为未执行或失败；不证明全数学域精确。
- **已验证（数值，未过门槛）**：完整NumPy五图共2949120个RGB half分量，仍684个不同（0.02319336%）。最高绝对误差0.0009765625；高PSNR不替代原bit-exact门槛。

|照片|不同half分量|最大绝对差|PSNR peak1 dB|
|---|---:|---:|---:|
|IMG_2600|127|0.0009765625|107.818767|
|IMG_2604|89|0.0009765625|108.467077|
|IMG_2608|95|0.00048828125|111.670104|
|IMG_0032|103|0.0009765625|103.090566|
|IMG_0033|270|0.0009765625|101.321639|

R2原始Apple pipeline往返15配置已通过：独立F64 max relative0.0009995002498750624，最低eligible覆盖89.96073405%。完整原尺寸ImageIO SDR最大差0沿用run39075649293。上述512×384完整consumer捕获不是12/24MP物理相机逆；global/local真实分离、RAW精度没有被这些结果认证。scene_RAW_EV继续待实机（IMG_2679/IMG_2408配对RAW）。

## 已试方案与原因边界

**已验证（数值）**：通用half unary原语表、独立signed atan2 262144输入控制0差、完整float32尾数fast_pow原语表、BG R/G/B FMA叶选择、float32左右融合、结构化CFG、noinline/always_inline/optnone、contract/reassociate pragmas、relaxed/precise math和size优化均有归档。V9给smoothSat内部增加debug导致整幅133分量变化，拒作原始中间oracle；V10只扩大root观察范围，控制整幅逐位0差。Shadows正/负分支通过明确五项舍入解决MSL，但NumPy全图仍有稀疏差。

**假设（未唯一归因）**：NumPy剩余差可能来自编译器fast-math重排/融合、half中间舍入、dot或硬件采样/超越函数在更大输入域的上下文差异。发现前4096可0差，但全帧仍不为0；尚无逐条最终GPU ISA与全部失败像素算子证明，不能把某个嫌疑写成确定原因。此问题按用户决定停止追逐，绝不因此把它改成已通过。

## 运行、artifact与归档

主run39121521190，artifact **12134493495**（vm-native-text，33,192,457 B，retention-days=1）。完整zip本地 `~/work/styles-gtm-ltm/runs/39121521190/artifact.zip`，SHA `775183dffde87a25460cfaa1007ed1b870ca251aba162edd17883fb3120d1ba6`；manifest SHA `597962f94544a29f842263190c2dc56276a10818a5fe163561e03ab7d2e90080`。122个entry全部流式SHA核验0失败。为守92%磁盘线只展开所需文本和5个已有NumPy预测；15个MSL完整输出与V6原生buffer逐文件SHA相同后作内容去重链接，证据`closeout-materialization.json`；没有用oracle代写预测。

关键entry：`precision-v10/{summary.json,selected-freeze.json,numpy.log,numpy/summary.json,numpy/discovery-trials.json,numpy/candidate-selected-freeze.json,msl/<photo>/<tone>/model-comparisons.json}`。本目录复制的final-evidence.json与errors.csv只含授权的旧五图指标，不含IMG_2810或人物像素。

历史对照run：V6 39111905092（原生14/15先过）、V7 39115378104（仅补最后一个）、V8 39118612970（atan2表和CFG）、V9 39120667676（负tone发现配置先过）。各artifact完整归档SHA在本机runs/<id>/archive-audit.json。GitHub artifact1天后过期，公开日志及本机归档仍在。

## 可复现命令（仅记录；不自动重启本方向）

本机只读审核已有输出，所有Python限内存：

```bash
cd ~/work/styles-gtm-ltm
./scripts/local-python-scope.sh validate.py
```

新输出需另命名，禁止覆盖历史；此audit应报告NumPy false、MSL非零true、oracle-replacement true、acceptance_complete=false。源码/primitive manifest与原始冻结SHA均校验。另附acceptance-closeout.json。

若将来另获明确授权作历史重放，**只在GitHub macOS runner** checkout 76f4132，使用run V6的native contexts及V8的math artifact，在新输出目录执行：

```bash
V10_R_FMA=1 V10_GB_FMA=1 V10_F32_FUSION=1 \
AIR_FUSION=1 AIR_NATIVE_LOWERING=1 AIR_TEX_HALF_UP=1 AIR_DOT_EQUAL=0 \
python3 research/vm-native/model-v10/cpu_probe.py \
  --captures <V6>/acceptance-v6/native --math <V8>/precision-v8/math --out <NEW>/numpy
python3 research/vm-native/runner/generate_candidates_v10.py \
  --source research/vm-native/runner/consumer-structured-v8.metal --out <NEW>/msl-sources
clang -fobjc-arc -O2 -framework Foundation -framework Metal \
  research/vm-native/runner/context_precision_v10.m -o /tmp/context-v10
```

用variants.json中唯一positive-f34-canonical-1项生成chosen.json，再对每个捕获调用 `/tmp/context-v10 <capture> chosen.json <NEW-result> ''`。完整调度源码run-precision-v10.py含筛选/冻结/留出顺序。本研究分支旧workflow改为仅manual，文档提交不再触发bit-exact跑次。
