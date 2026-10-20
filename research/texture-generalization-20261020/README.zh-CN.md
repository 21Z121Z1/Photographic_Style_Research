# 使用 XDRemux 真实样张泛化 Texture 生成

本轮将已有 SPI 生产流程扩展到多实例、空人物上下文、非正方形图像、输入方向和不同尺寸。输出是新建的 SDR 编辑副本；原 fixture 字节不变，副本不保留 HDR 资源或动态视频。

此前 NASA 候选 `a7ac5d0d…` 已有[用户确认的设备激活](https://github.com/21Z121Z1/Photographic_Style_Research/blob/38f1216a567cc57c993b5e5646f6b0a0d944a18e/DEVICE_ACTIVATION.json)。本轮新文件仍需分别导入测试，云端生成/回读/重放结果与设备反馈分别记录。

## 转换自己的输入

在 Apple Silicon、macOS 27、Xcode 27 环境运行：

```sh
python3 research/texture-generalization-20261020/convert.py \
  /path/to/photo.heic /tmp/texture-photo --max-dimension 1024
```

输出目录必须为空。导入 `texture-candidate.heic`，`control.heic` 是同一编码主图的普通对照。`person-N/final-file-mattify-preview.heic` 是逐人的单效果烘焙预览，不是可编辑候选，也不是全部人物/效果的合成预览。

默认长边 1024；参数另接受 512、1536、2048、4096。实际覆盖尺寸以矩阵为准，不能从参数可接受推断均已验证。原分辨率 HDR 与 Live Photo 保留不属于本轮副本契约。

## 原生数据与泛化行为

ImageIO 统一完成方向变换；后续检测、统计和编码共享同一幅直立图像。Vision 产生几何、分割与独立实例概率图，遮罩明确重采样至工作尺寸。人脸按边界内的概率重叠匹配独立实例；未匹配人脸会列出，不把聚合人物图充当逐人实例。

每个匹配人物调用原始 Mattify、UnderEyeBrighten、SkinSmoothStandalone 生产入口，使用共享几何和该人的实例图，不提供预制拍摄统计。空统计字典会省略并记录原始结果，不填默认值或借用其他图。空人物上下文不构造人物、人脸点或不存在的皮肤/人物群体统计。原生分割也可能检测到模型、展示物等，保留模型结果，不冒称已鉴别人类。

本系统的原生人物 `dictionaryRepresentation` 会把负角度转成巨大正数，也会舍入正角度。序列化保留实际的有符号原生 getter 值，并在证据中保留未修正字典。验收将角度与本图 Vision 弧度比较，验证原生解析器往返和最终文件 getter；没有修改 Apple 实现。此前损坏角度下的空统计或零效果，不作为尺寸限制的证明。

每人有独立 XMP 实例引用键；原生读回必须匹配几何及已有统计。逐人重放只使用最终 HEIC 的主图、原生读回数据和实际解码的遮罩，不重新检测。空上下文没有人物效果可重放，会明确记录。

生命周期以 `finishProcessing` 结束，统计和预览均在此前完成。启用预览后再次 prepare，提交并等待命令；结束前同时等待原生上下文和调用队列完成。验收检查实际记录的顺序及 GPU fence，结束后不再处理。早期全量运行记录过 2048 UnderEye SIGSEGV；独立的 128/256/512 MiB 分配池对照均成功且统计相同，未证明是固定容量不足。首次失败报告在调试器重跑前另存；`stress` 工作流阶段连续执行三轮 2048 写入、回读与重放。

普通 Styles 仍是新建 SDR 中性上下文。原生线性分量的负值记录范围与数量后，在该 SDR 上下文钳制为非负。没有恢复原相机 RAW、ISP 或拍摄参数。鼻唇眉、脸部皮肤、手部区域及耳部/纹身可选保护仍遵循[原生产报告](../texture-producer-20261020/REPORT.zh-CN.md)中的来源和限制。

## 真实样张矩阵

工作流固定 XDRemux `18340989590d451f5676924feb03c70baa503e1a`，按 canonical `fixtures/SHA256SUMS` 核对 28 个媒体条目，其中两份重复，独立原图 26 张。

```sh
python3 research/texture-generalization-20261020/matrix.py \
  /path/to/XDRemux/fixtures /tmp/texture-fixtures --phase generate --selection all
```

补充用例由真实 fixture 派生：两份检测人脸的裁剪拼接、配对反向像素变换的 EXIF 方向 2–8，以及 512/2048 尺寸。双人用例必须原生读回两个独立实例；方向用例必须恢复与直立基线逐字节一致的原生像素。NASA 是单独回归项，另有直接调用 CLI 的测试。派生压力用例与未改动的原始样张分别标识。

逐文件 `acceptance.json` 验证原生返回值、输入/遮罩 SHA、共享几何、实例键和统计回读、主图载荷保留、最终遮罩原生解码及有限的逐人重放输出。效果不适用时可以没有像素变化；实际变化量会列出。实际执行覆盖、失败与省略组以 `matrix.json` 为准。

结果保存到独立 `research/texture-matrix-output-<run-id>` 分支，不合并或改写源码分支。各用例 ZIP 内含逐文件 SHA 与长度 manifest。原生程序没有仓库凭据；只有最后的结果保存步骤获得工作流 token。工作流不改 Apple 实现/系统模型，也不打开 Photos。

英文规范见 [README.en.md](README.en.md)。
