# S11-C：brightAndContrast 与主入口分叉的集合接口

同一 iPhone17,3 / 24A446 AIR10。`pixel_bright.py` 完整条件模型覆盖 renderBrightAndContrast 的顺序、half/f32、零分母、clamp、分段及采样前工作域；复用 transfer、polar、contrast、RichSat。统计必须以 `BrightStats` 五个显式 f32 标量供给：SSRGlobalStats `[2][4]、[3][4]、[5][0]、[6][6]、[6][4]`，没有估算或重新生成原帧统计。名称保留原索引，不猜字段业务含义。

原完整 helper 及递归叶未经改动，宿主 wrapper 按原 LLVM struct GEP 填五个统计位置，未猜内存 byte layout。新增 `air.fast_saturate.f32` 显式 shim；无 identity/abort 占位。

18次新宿主调用（16组两类统计/曝光与人物/肤色、彩色/灰色/黑色，另2个零曝光及非法pow域负例）：

- 点模型12组已知、6组 unknown；已知域30个 half 位差，最大绝对误差 `0.00244140625`，没有计作数值吻合。
- 集合仅2组已知，覆盖原结果，最大盒宽 `1.000976622104645`；另16组仍 unknown（含零分母与有限算术包络超预算）。这些结果不支持高精度逆解。
- 对全部案例保留输出与具体拒绝原因，没有缩输入或mask；没有重跑505组或更早已验收批次。2u/4u仍是宿主假设，不能借宿主结果承诺原GPU精度。

`post_skin_branches.py` 接受显式 half **集合**和五个 f32 stats集合，拒绝点/中心输入，系数直接取完整 tone 接口上下界及边界决策。严格照本版主入口：

1. skin393 ← RGB392、肤色95、guide350、FGθ9/θ10。
2. highlight394 ← skin393；398仅在原始shader cast code245==2时选half.5混合结果，否则选393。它在后续SSA476另被消费。
3. bright400 ← **skin393** 与工作RGB286、人物96、肤色95、曝光399、stats18；它不读取highlight398。
4. neutralizing输入404在raw cast code245==16时为400，否则为393；按真正依赖保留各分支 unknown。raw code必须显式uint32，不由产品/UI风格名猜。

122项回归通过，包括统计类型、激活差分、宽包络诚实性、分叉中bright输入独立于highlight选择、原边界集合后传及拒绝中心输入。此接口没有宣称原入口整体数值通过。

接下来继续neutralizing408→warmth409→selective-color413与外围cast选择。现有24个全激活组合集合 unknown 和旧8个叶域 unknown不变；AIR7生产与guided filter仍未建模。原GPU/同帧及IMG_2810精确build依赖仍单列。

复验：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_bright_check.py /path/to/0010.ll.txt /tmp/new-bright.json
```

收据 `evidence/native-bright-s11c.json` 包含原完整函数/递归叶、宿主、模型、输入/输出 SHA。没有新增下载、私人媒体或GPU运行；完整照片处理和逆解未完成。
