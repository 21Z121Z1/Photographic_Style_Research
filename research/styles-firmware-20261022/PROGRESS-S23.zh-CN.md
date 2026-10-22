# S23：producer历史执行IR原件可用性与身份门禁

**历史逐字/语义比较目前不能完成，原因是缺少两份实际执行的producer host IR原文本，不是权限拒绝。** 本轮只核身份与文件保留链，没有生成重建IR、编译、执行原kernel、重跑146状态、扩域或添加像素叶案例。

这里的目标是各次提交给LLVM编译器的生成host IR `0.ll`，不能用固件source AIR、已有函数指纹或当前重新生成件替换。

|历史运行|记录的实际producer IR SHA256|实际原文本SHA核验|
|---|---|---|
|S21|`a787d7ada4c12ba8fbc36ad48161f47d5fb63be4fd5a01421731569127b8cf28`|未执行：原件不可用|
|S22|`ba676ebda2421750a32823caa5d664970c78f4fa459650910e65a5269df695da`|未执行：原件不可用|

## 限定定位与保留链

`producer_ir_identity.py`核当前历史harness源文件SHA与**原运行前**清单一致：`native_active_color.py`、`native_color_boundaries.py`均未被后续身份核查改写。两者在`TemporaryDirectory`中把`enumerate(units)`写成`{i}.ll`，producer为`0.ll`，编译后退出上下文即按默认行为清理。原成功post收据均为exit0；成功日志SHA也逐一匹配，只含运行指标，没有保存精确临时路径。

本轮仅查看当前Python user temporary目录及`/tmp`两个已知根下的顶层`psr-active-color-*`、`psr-inverse-boundaries-*`，四个限定模式均0目录项；没有递归全盘查找、进程清单或未知缓存搜索。现有研究目录发现的6个`air-*.ll.txt`只读核hash，均不匹配上述两目标，明确不作为历史执行host IR。全部候选hash、受限定位范围、harness源SHA和原日志SHA见`producer-identity-s23a.json`，没有上传原IR内容。

这只证明**目前在所查已知范围没有可用原件**，不证明用户磁盘上不存在任何未知备份。收据中的SHA不能还原已丢失文本；也不能把source AIR经当前生成器构建的件冒称S21/S22原件。

## 允许的结论与未执行部分

|核查项|证据|状态|
|---|---|---|
|两原件身份及历史逐字diff|只有记录SHA，缺原文本及其保留路径|缺件阻塞|
|名称/排序/metadata差异分类|无已验证实际pair|未执行|
|算术、常量、FP属性、memory摘要、ABI、写出及依赖差异|无已验证实际pair|未执行，不能称无差异|
|规范化规则与规范化hash|没有可证明无关的实际差异|规则为空，hash为null|
|原函数指纹/元数据相同及有限前缀0位差|原S21/S22保存收据|仅旁证，不能补证模块全等|
|146接口状态模型穷尽、6状态有限宿主见证|原S22证据保留|范围不变，本轮未重跑|

身份门禁要求记录SHA匹配和已建立的保留执行输入来源；即使当前重建件字节碰巧匹配SHA，也不能仅凭它自动宣称历史执行来源。只有可接受实际pair才可生成raw diff；工具仍不删除metadata/属性、不自动将差异判为无关、不生成规范化hash，后续必须逐项举证。测试中的小型IR文本只测门禁，不执行shader或验证像素算子。

原S22首次错误的整段IR身份断言及失败pre/post继续逐字保留；没有把其失败改记通过。producer全文差异的原因仍未知，没有推断是排序或metadata，也没有用有限输出一致证明模块语义相同。

## 下一步

若能提供**既有保留原件的精确路径及执行来源证据**，先分别核上述两个SHA，再逐项diff并给差异分类；只对可证无关的具体差异制定有限规范化规则。

若确无原件，该历史pair的逐字与语义比较保持不可完成。下一次经授权的新原宿主运行应在编译前将实际IR输入持久化到本任务私有缓存，记录文件bytes SHA、原run身份、生成器/输入/编译参数及依赖摘要；只把hash与脱敏分类提交Git。任何未来重建或复跑都必须标为**新运行**，不能补写成旧S21/S22原件。本轮未实施新运行或新搜索。

定向测试命令（不运行旧246项、146状态或原kernel）：

6项身份门禁测试通过，实际unittest用时0.003秒；源码和输入在运行前绑定，运行后未变。没有将审计程序exit0误记为历史IR比较通过。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_producer_ir_identity.py' -v
```

实际审计、测试及源码/输入运行前绑定见`identity-binding-s23a.*`、`test-binding-s23b.*`和`verification-s23.json`。9字段缺缓存断点、原GPU/真实同帧、IMG_2810 build和未知源逆解缺口保持原状。
