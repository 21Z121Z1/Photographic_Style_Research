# S24：持久保存实际编译输入的新宿主基线

本轮建立**明确标为新运行**的基线 `s24-20261022-a9c712f6`，修复未来验证的输入可追溯性。先持久保存实际5段host IR、plain主入口及C shim，之后编译器只读取这些文件。既有8个边界控制全部通过旧边界输出、两个目标及独立点模型比较；没有重跑146状态搜索、扩大控制域或改候选预算。

**S21/S22历史producer IR全文差异的原因仍未知。** 新件不是历史原件，也不补证历史模块逐字或语义等同。S23缺件结论、S22失败收据及原证据保持不变。

## 实际输入、编译与保留链

私有原件位于任务目录下的 `psr-private-baselines/s24-20261022-a9c712f6/`，在Git checkout外。目录为0700，封存输入0400，编译日志0600；没有改现有文件权限。新目录上限64 MiB，预留至少2 GiB磁盘，审计时实际4862288 B。没有自动清理或覆盖失败运行的路径。

私有manifest SHA256为 `2871f78fd971a01b11204433549d1e6462d2615b130b05b502678c6542e87dd4`。其中280份封存输入包括实际编译输入、5份现有source AIR、全部249份本研究Python源码、固定上下文/原目录快照、field3合同及编译器版本输出。Git只提交哈希、合同、合成结果和脱敏收据，未上传这些专有IR、AIR或编译产物。

|实际持久编译输入|SHA256|
|---|---|
|producer|`685fd8da9c85a39b520928165810f80920c750e7ec2b78e902e9fa3615d37289`|
|guided coeff|`6bde4e5adfcc9593c89769e0344b6054cce04f5dd8c0ddb78f617ce6e279e4d0`|
|guided filter|`d4aefab6820e1674c1c4451cb392602dbbde7250be660b4a6d471f2181038de5`|
|guided apply|`e400b0197691fb83848ad2e94114e620bfd16ff0da5ff572845eea05198c1b54`|
|observed main|`786cd858ca4a8241a29feda4e81df6b9764cafc2b71cfd316f7bcd7d8dbb9800`|
|plain main|`321987269f6748b0fae93985911ed75e46d66351682cd46f9503efb94a73eec3`|
|C shim|`105e0ff7a9fc7a25eb2ceafa8c0ad9b3155bcc76863810d7b020e2eab3d62d51`|

编译使用Homebrew clang22.1.6，二进制SHA `9a3ebf66e99cded4cee3f6efe79103994ed155694be5abcfdbb0bdf1910007cf`；参数为 `-target arm64-apple-macos27.0 -Wno-override-module -v -dynamiclib`，后接manifest内封存路径和新产物路径。实际argv、stdout/stderr、`otool -L`依赖日志及两个dylib均保留在该私有目录。公开收据只把运行目录替换为 `<private_run>`。宿主为arm64 /macOS27.0.1 /Darwin27.0.0；数学与纹理shim沿用现有合同，不是iOS/GPU执行。

生成前绑定source AIR、编译器和工具SHA；生成后封存并复读实际bytes。编译前后、加载前后、前缀后、每控制前后及运行结束均核输入SHA，编译产物在加载前和后续运行阶段另核SHA，共26份证明。只读审计再次核所有原件、命令、日志和产物，并从保存文件重算field3静态合同，全部一致。进程局部固定 `PYTHONHASHSEED=0`，只用于新运行的生成记录；没有由此推断历史差异原因。

## 新文件上的field3依赖合同

版本限定仍为已核iPhone17,3 /iOS27.0.1 /24A446的实际SmartStyleV1 /CMISmartStyleProcessorV1链路。产品代际Styles2、内部V1、HEIC metadata编号分别处理，不继承IMG_2810精确build或纹理链路身份。

`baseline_field3.py`读取**已保存的新IR**，不比较或继承历史整模块身份。producer的原SSRParams指针仅有field6和field15的分量4/3/2四个标量读取，各成员指针只流向自己的float load；没有field3读取或未跟踪的原buffer转交。三个guided包装入口不绑定SSRParams。

observed/plain main各检查5个原buffer作用域：主入口、BW、haze、BW channel mix及其stats helper。field3唯一读取在主入口SSRParams byte12：SSA355→float356→half357→float358。由此进入既有branch/gain364/protect384合同；额外观察转换只允许隔离写入观察buffer。未知原指针别名/逃逸、额外控制消费者、观察指针额外读取均拒绝。函数、关键指令及整文件SHA记录在新合同中；不据此宣称其他参数、主模块所有行为或GPU舍入均已等价。

该新合同支持在固定其余输入时共享producer/guided前缀。完整source/guide/ROI/参数/纹理仍由冻结合成上下文供给，cast0、tuning2、中性BG/FG及零lookup限定不变；只改变场景缩放后的内部field3 raw f32。

## 8个既有边界与两个目标

先检查原146状态模型目录的242份计算源码及16份上下文/目录输入SHA未变；`bound_validation.py`唯一旧源码变化是把S24证据加入运行前绑定。搜索证据直接复用，新增146状态搜索调用为0。没有重跑13825单元、55298端点检查或旧大批次。

本轮只执行S22已有8个控制。producer/guided共享前缀78次，8控制各观察/plain主入口24次，共**270次原AIR宿主重编译kernel调用**；不是270个独立案例。重新计算前缀，没有外供保存的中间RGB/map替代它。每控制另执行一次独立完整点模型，共8次、8×1938=15504个half观察比较，含重复比较的共享前缀。

|raw f32位型|状态|平台目标匹配|.3目标匹配|
|---|---:|---|---|
|`0x33000000`|0|是|否|
|`0x33000001`|1|是|否|
|`0x3cb51000`|1|是|否|
|`0x3cb51001`|2|否|否|
|`0x3e991000`|92|否|否|
|`0x3e991001`|93|否|是|
|`0x3e99efff`|93|否|是|
|`0x3e99f000`|94|否|否|

所有输出有限；原half357/gain364/protect384与逻辑键一致。新前缀及每个观察与S22保存输出逐half位差均0，writer与146状态目录预测位差0；两目标的包含/相邻排除和端点判断全部符合原预期。观察/plain writer位差0，独立点模型15504分量位差0、点域unknown0。没有因最终writer相同而跳过内部比较。

新增运行墙钟9.919724秒，包括编译、哈希、8次点模型等；它不是kernel净时间或性能测量。新基线只增加同6个状态0/1/2/92/93/94的可追溯有限见证，**其余140状态仍未宿主穷尽**。

S22候选范围保持：平台目标 `[0,.02210235595703125]`，1018499073个f32；.3目标 `(.2989501953125,.3006591796875)`，57343个f32。它们是canonical非负有限域 `[+0,3/8]` 中的完整模型候选；本轮没有将6状态宿主见证扩大成146状态全宿主证明、原GPU证明或未知源照片逆解。

## 复验及未完成项

12项定向测试通过，unittest实际0.039秒。测试覆盖输入/产物篡改、编译前封存、持久文件读取、日志保留、路径及原指针/观察sink负例、新合同和8控制成本；mock编译用小型合成字节，不新增原kernel。没有重跑旧246项或增加叶算子案例。原运行及新测试均先绑定源码/输入，再执行，运行后未变。

仓库根定向测试：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_traceable_baseline.py' -v
```

新基线可复验入口如下；必须使用**全新目录和全新输出文件**，实际运行的完整绑定参数见`prepare-binding-s24a.pre.json`、`native-binding-s24b.pre.json`，不是在旧目录中重编译覆盖：

```sh
PYTHONHASHSEED=0 python3 research/styles-firmware-20261022/traceable_color_baseline.py prepare \
  ../air-cmi-compare/ios ../psr-private-baselines/s24-new-unique-run /tmp/psr-new-prepared.json
PYTHONHASHSEED=0 python3 research/styles-firmware-20261022/traceable_color_baseline.py run \
  ../psr-private-baselines/s24-new-unique-run /tmp/psr-new-prepared.json /tmp/psr-new-baseline.json
```

公开证据为`prepared-baseline-s24a.json`、`traceable-baseline-s24b.json`、`baseline-audit-s24c.json`及`verification-s24.json`；编译器实际读取的原件只留本机私有目录。仅克隆公开repo不能重建被禁止上传的Apple输入。

下一可考虑的软件工作是保留相同证据链，为现有未宿主覆盖的状态选择必要新见证；需另定范围，不能把本轮8个控制计作全部146。历史S21/S22差异仍缺实际原文本，未补写历史身份。RichSat集合均值含零、旧12+24 unknown、旧24/8域、9未定位字段的缺缓存软件断点、S19恢复审计限制、原GPU/真实同帧、UI映射、IMG_2810 build及未知源逆解全部保留。没有新下载/挂载/找缓存、私人媒体、进程清单重试或其他项目/安全预算操作。
