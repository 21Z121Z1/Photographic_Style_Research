# S11-D：neutralizing 三个活跃叶

同一 iPhone17,3 / 24A446 AIR10。`pixel_neutral.py` 实现 deRed、deYellow、deRedNeutralOnly，复用旧皮肤 transfer、原颜色矩阵及条件正分母域；未创建独立拟合算法。`pixel_color.py` 将原矩阵表达式原样提取为 to_lab/from_lab，polar仍调用同一表达式，避免为每叶复制矩阵。

每叶16组新增宿主调用（RGB彩色/灰色/黑色，±非零amount，显式有色及零色度reference Lab），各48个half分量逐位一致，点/集合均无unknown，集合越界0。完整原叶函数不修改，无占位。已验证的只是这些输入与声明的宿主契约，没有重跑旧505组。

`direction` 保留原radius的f32阈值，正分支交集后归一，零色度走原zero方向；hue保留half fmod和跨周期集合。宿主bool转换声明为float!=0，fmod声明C fmodf后转half；二者是显式宿主假设，非GPU后端保证。

reference Lab 为调用者供给，不代表统计或相机辅助上下文已恢复。neutralizing根函数还需要实际stats参考值构建、条件分支、skinWarmth及原调用顺序，尚未称根函数或主入口完成。warmth/selective-color与外围cast仍继续，原GPU/同帧、AIR7与guided filter缺口不变。

126项回归通过，含参考色差分、零色度分支、三个叶的集合后传与fmod跨界。旧24个组合集合unknown、旧8个叶域unknown，以及S11-B/C新增unknown和位差均不改记通过。

复验：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_neutral_leaves_check.py /path/to/0010.ll.txt /tmp/new-neutral-leaves.json
```

收据 `evidence/native-neutral-leaves-s11d.json` 保留函数、模型、宿主、输入/输出哈希与全部案例。新下载0B、私人媒体0、GPU运行0；完整照片逆解未完成。
