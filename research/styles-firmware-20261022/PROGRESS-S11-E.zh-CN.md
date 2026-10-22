# S11-E：完整 neutralizing 根与真实 cast/stats 合同

同一 iPhone17,3 / 24A446 AIR10。`pixel_neutral_root.py` 接通 renderNeutralizingAdjustments：原presence gate、三项raw stats→half reference→working Lab及curved reference、deRed或deRedNeutralOnly的分支与更新reference、deYellow、skinWarmth顺序不变。

`CastValues` 要求完整34个f32的136B SSRCastAdjustments；6个scalar、3×3数组等索引显式，和已验证12值cast prior分开。neutralizing使用原struct字段15..18（flat27..30），不由风格名猜数值。`NeutralStats` 要求SSRGlobalStats `[2][4]、[3][4]、[4][4]`；未重新生成照片统计。enabled/use_skin必须是实际布尔presence输入；disabled按原根分支不读stats。

补齐 actual caller 的 skinWarmth **mode>0** 条件模型：本根调用固定half1。mode<=0独立替代分支明确拒绝；不把它算完整无条件叶。复用原颜色变换/方向、半精度fmod及新三叶。16个新独立完整原helper调用均为mode1、非零±amount，48个half分量逐位一致，点/集合unknown0、越界0。

25个新完整原neutralizing根调用（四种RGB、red-only/red-neutral/all-four活跃、use_skin双态，另一个disabled控制）：点/集合unknown均0，原结果均在包络内；2个half分量有差异、最大绝对误差`0.00048828125`，不改记逐位吻合。所有递归原函数体不修改，未用占位叶。集合覆盖也不等于紧逆解或原GPU证明。

系数跨原gate时同时保留像素和reference两条分支的并集，未取中心；测试包括完整字段与prior混淆拒绝、disabled不需stats、阈值相邻域联合后传及mode0拒绝。130项回归通过。旧24个组合集合unknown、8个叶域unknown以及S11-B/C未决项不变。

收据`native-neutral-root-s11e.json`和`native-skin-warmth-s11e.json`记录函数/输入/输出/模型SHA。后者生成后host builder只新增未参与该独立调用的root ABI分支；`s11e-source-links.json`提供精确删除规则及重建SHA，不重复16个宿主调用。继续warmth409、selective413和外围cast，不称主入口整体通过。AIR7生产/滤波、原GPU/同帧与IMG_2810精确build依赖仍单列。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_neutral_leaves_check.py /path/to/0010.ll.txt /tmp/new-skin-warmth.json --leaf skinWarmthFilter
python3 research/styles-firmware-20261022/native_neutral_root_check.py /path/to/0010.ll.txt /tmp/new-neutral-root.json
```

没有重跑旧叶批次、新下载、私人媒体、原GPU运行或照片逆解验收。
