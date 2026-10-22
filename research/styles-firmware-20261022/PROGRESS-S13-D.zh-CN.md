# S13-D：AIR7 SRL/transfer/CCM 入口与 guided 集合接口

同一iPhone17,3 /24A446。补齐AIR7 sampled primary24→SRL34→linear37→reference96，独立观察三处；复用刚验收的transfer、矩阵和typed算术。真实SRL保留f32参数分段、matte混合、严格(0,1)门限、half luma小值跳过与f32比值；code6保留原两种gain方法及byte mode选择。没有把LinearThumbnail或inputLinearImage认定为无风格原图。

原25..96切片仅将函数常量load25变为显式bool、将28..30 matte纹理采样变为显式half输入，其他算术/比较不改；完整原SRL与transfer函数随原属性编译。15个新增组合调用：13点域/13集合域已知，三处共117个已知half分量中1个位差、最大绝对误差.0001220703125，已知集合越界0。2unknown为黑输入code6 HDR gain的未证明pow域，原宿主非有限；不归因硬件、不调黑值或阈值。已知集合最大宽.0225401。

定向核同版AIR7/AIR10的applySemanticSRL与linearFromCurved：只去掉attribute组编号后完整函数文本相同，保存两端原SHA。没有据此声称各caller/纹理/拍摄链相同，也没有再扫215头或重跑旧算术批次。

`ltm_guided.py`以已采样的整图primary24/linear98/matte30集合为输入，逐点连接AIR7入口→BG203/FG205，再把完整V图像集合直接交给guided三阶段，保留输入分支决策及每支unknown。新API允许纯集合与明确几何，不需要中心图或占位点图。curve、CCM、SRL、semantic、guide、epsilon与工作域仍显式供给。

两个2×3合成接口见证（RGB/scalar guide）生成3×4输出，均为已知有限集合；这是独立模型连接见证，新增native/GPU调用0，不是组合原生对照。依赖损失严重：raw BG/FG盒宽约1.41465/1.56419，guided最大宽达155.125（scalar guide约52.7656），不具备高精度逆解用途。保留这些真实宽度，不缩semantic范围、不改epsilon、不使用中心。producer→block290 ROI采样仍未做完整集合组合验收。

168项回归通过。收据`native-ltm-pre-s13d.json`、`ltm-guided-sets-s13d.json`、`ltm-helper-equality-s13d.json`与更新后的`pixel-inventory-s13d.json`列明函数/偏移/输入依赖和局部剩余工作。S12 BW实际分支、主输出600、guided生产各有独立覆盖；不能把这些孤立收据相加为全照片通过。旧24组合unknown、8叶域unknown、bright及其他位差、tuning field17/byte652布局失败见证与独立tonal468观察均保留。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_ltm_pre_check.py /path/to/0007.ll.txt /tmp/new-pre.json
python3 research/styles-firmware-20261022/verify_ltm_guided.py /tmp/new-connection.json
python3 research/styles-firmware-20261022/audit_ltm_helpers.py /path/to/0007.ll.txt /path/to/0010.ll.txt /tmp/new-links.json
```

局部模型剩余项：原source二维采样/纹理格式与完整ROI集合连接；主入口393之前RichSat/smoothSat等外围选择及完整工作域/guide组合；旧unknown的相关性分析、尚未定位的9字段消费者；最终打包写出。它们不是统一的硬件阻塞。真正外部验收另缺匹配iPhone17,3/24A446原iOS/GPU与同帧上下文，IMG2810另缺精确capture build/匹配资源。没有读取私人媒体、下载或绕过被拒ps。
