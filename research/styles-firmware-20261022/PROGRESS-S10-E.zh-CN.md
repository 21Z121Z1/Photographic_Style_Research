# S10-E：剩余七叶与真实调用参数

同一 iPhone17,3 / iOS27.0.1 / 24A446 AIR10。`pixel_remaining.py` 补齐 `underGrassFilter`、`underToneFilter`、`tonalContrastFilter`（neck）、`smartContrast`、`highlightNeg` 以及 BG 的 local/gammaContrast 内联段。沿用强类型 half/f32、逐操作舍入、集合包络及无法证明定义域时的 unknown，未添加恒等或 abort 占位。

| 算子 | AIR10 原范围 | 非零对照组 | half 分量 | 位差 / 集合越界 |
|---|---|---:|---:|---:|
| underGrassFilter | 5876–5973 | 30 | 90 | 0 / 0 |
| underToneFilter | 5435–5534 | 30 | 90 | 0 / 0 |
| tonalContrastFilter | 5537–5586 | 30 | 90 | 0 / 0 |
| smartContrast | 4816–4886 | 30 | 90 | 0 / 0 |
| highlightNeg | 4889–4970 | 45 | 135 | 0 / 0 |
| BG.localContrast_inline | renderBG SSA90..142 | 30 | 90 | 0 / 0 |
| BG.gammaContrast_inline | renderBG SSA151..174 | 30 | 90 | 0 / 0 |

共 225 组 / 675 分量，点与集合均无 unknown。5 类 RGB 包括彩色、灰色、HDR/负分量、小值和黑色，3 个显式权重/guide，正负系数（highlightNeg 用实际负号路径）。这是有限输入集的原 AIR 宿主对照；2u/4u 误差假设没有被提升为硬件定理。

完整独立叶原文不变。local/gamma 不是独立原函数：截取父函数原直线算术段，仅将 SSA 双射重命名并加宿主 ABI，门限及 f32→half 输入转换在截取段之外。收据分别记录父函数 SHA、原指令段 SHA、输入 SSA 映射与新 wrapper SHA，不能称完整原 helper 通过。

接口参数由实际调用证据锁定：主入口 SSA352 向 BG 的 underGrass 传人物 SSA96；SSA354 向 FG 传人物 SSA96、肤色 SSA95、混合 guide SSA350。BG underGrass 使用 person（在输出混回原色），FG neck/underTone 使用 skin（两者混合方向不同）；其余新叶使用 guide。`models()` 按参数身份取上下文，不共用 guide。

`from_polar` 新增显式 `clamp_output=False`：underGrass/underTone 的原实现先逆变换、按权重混色，再 clamp，不能提前 clamp。已有 saturation 的默认 clamp 路径保持原算术及顺序，未重复已验收 saturation 宿主批次。

107 项回归通过，包括各叶非零、黑色 neck 零分母门、负 guide/负均值拒绝、人物/肤色与 guide 不混用、7 叶输入包络及控制器字段接线。每个结果仍 `full_helper_numeric_verified=False`，外围采样/皮肤/风格等主入口与原 GPU 未验收。

复验（原 AIR 只保留本地，不入 Git）：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_pixel_leaves_check.py /path/to/0010.ll.txt /tmp/new-remaining-receipt.json --leaf underGrassFilter --leaf underToneFilter --leaf tonalContrastFilter --leaf smartContrast --leaf highlightNeg --leaf BG.localContrast_inline --leaf BG.gammaContrast_inline
```

精确哈希及逐案例收据见 `evidence/native-pixel-leaves-5.json`。9 个未连读槽依然未决，未重扫215头，也未标 unused。没有新下载、私人媒体、原 GPU、原照片或完整逆解验收。
