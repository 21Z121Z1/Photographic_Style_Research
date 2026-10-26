# 2026-10-26 接续

承接远端 `research/styles-chain-validation-20261023` 的 `3ebb5d7ec3041963a06f6b48c525d71deec4aad6`。
默认分支 `master` 仍为 `ce25aa34fe3dac8541730971d6957401fca3e1dc`。
S33 历史分支仍为 `e5d2bcd8db8b3eb6737237ed88167777b3c920ba`。
未修改上述分支、其他 PR 或原媒体。工作区没有 AGENTS.md，实际验证入口仍为 validate_portable.py。
pstack 来源为 cursor/plugins 的 `99b609a72323b70204eab407c622f436e858e112`，采用 Session pickup 和小步验证流程。
遵从用户指令，本轮不调用 subagent。

## 实现

`TextureEffect.SKIN_SMOOTH_FINAL` 明确表示最终混合，不表示完整 SkinSmooth。
`run_conditional_texture(..., skin_smooth_final=SkinSmoothingContext(...))`
复用既有公式和颜色域合同，消费前一阶段的实际 binary16 输出。
调用者必须供给饱和重建 S、blur B 和 f32 权重 a/b。
运算仍为 float64 连续公式再存 binary16，不宣称原生 half 运算或采样。
UnderEye 与最终混合按 effects 顺序执行，最终混合检查点带阶段索引。
缺上下文返回 output=None 和 gap；请求完整 SkinSmooth 或 Mattify 继续阻断。
顺序测试中 UnderEye→final 的输出为 .5，反序为 .75，说明指定顺序确实改变输出。
这只是合成模型检验，不是 Apple 拍摄顺序证据。

`validate_portable.py` 原来只绑定 evidence 顶层文件，且不能检测新增输入。
现在递归绑定文件路径和内容，并比较运行前后的完整 manifest。
新增、删除或修改嵌套证据均令身份变化。输出目录不得放入证据输入树。
源码绑定补全 semantic-styles 下全部 Python 文件。
新增回归用临时合成文件验证这些失效情形，不触碰既有证书。

## 复现与证据

从仓库根目录执行。输出目录必须不存在。

```sh
python3.13 research/styles-firmware-20261022/validate_portable.py /tmp/styles-check-20261026
cd research/styles-firmware-20261022
python3.13 -m unittest -v test_skin_smoothing_final test_texture_style_adapter test_validation_binding
```

收据 before.json 包含实际 HEAD、dirty 状态、源码与输入 SHA 和 OS/架构/Python/NumPy。
result.json 和 tests.log 记录命令、测试状态与日志 SHA。
本地干净提交 `26a4e0ac6ca9aa5363ec8f8b81b63d1709ddff90` 的 130 项定向回归通过。
耗时 10.8496 秒是一次回归成本，不是性能优化测量。
收据与日志在 `evidence/continuation-20261026/`，输入和源码运行前后不变。
最终提交的 CI 使用相同入口并上传收据。旧 SHA 的通过不转记给新提交。
未测新性能优化；旧同机成本与 master 缺少同工作负载的边界仍适用，不能报告优化收益。

## 原生缺口

当前为 Linux x86_64，没有原 Mac 封存 dylib、S33 原始 72B 报告、私有框架或原帧上下文。
pow 运行绑定仍需要 SHA256 `47185c09c0407d7c96aa9dc55e0581ae4e781836951c8b236d17f2ac6f8efbbe`
的原封存产物、匹配 OS、UUID/GOT 与 FPCR/返回位型实测。
标准 macOS runner 只编译和静态检查 collector，不能替代该目标运行。
S32 的 2047 输入域与 RN 运算假设、S33 单次 9/16→3/4 的范围不变。
完整 Texture 的上游 stats/reconstruction、真实语义分割、原 GPU 和完整摄影产品链仍未验收。
没有上传私人照片、原系统二进制，也没有触发付费 runner、购买额度或合并 PR。
