# 原始历史与结构证据

测量固定在 `611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079`。祖先提交共280个，提交树3628文件。代码量为 research545个Python、tools14个Python、tests9个Python，以及Sources中的Swift。Python test_函数静态定义为research441个、tests60个；这些不是执行通过数。

`mine_history.py` 枚举精确Git树并读取原始blob，记录每个Python、Swift和workflow的SHA。55个Python文件编辑sys.path，29个调用exec，4个使用AST或FunctionType克隆，19个用glob('*.py')参与源码身份记录。它们是重复维护面的观察，不是55、29、4或19次缺陷。runner声明共105次xcode-27、1次ubuntu-latest。标签不证明付费、免费或当前可用。

|故障组或边界事件族|独立记录下界|原始源码锚点|代理归因|
|---|---:|---|---|
|execution-input-retention|2|[S21-producer-input](https://github.com/21Z121Z1/Photographic_Style_Research/blob/435d2ce4aee880148635ca22b9b9ff34287f4d8e/research/styles-firmware-20261022/native_active_color.py), [S22-producer-input](https://github.com/21Z121Z1/Photographic_Style_Research/blob/b2585a04d5344d147c5b2319557fe01b421caa81/research/styles-firmware-20261022/native_color_boundaries.py)|未知|
|observer-effect-summary|2|[BW-observer-readonly](https://github.com/21Z121Z1/Photographic_Style_Research/blob/fbe4d25a2941862566c23d9aa204153510d26fd6/research/styles-firmware-20261022/bw_host.py), [BG-gamma-observer-readonly](https://github.com/21Z121Z1/Photographic_Style_Research/blob/fbe4d25a2941862566c23d9aa204153510d26fd6/research/styles-firmware-20261022/diagnose_local_gamma.py)|未知|
|native-build-input-contract|2|[S96-translation-inputs](https://github.com/21Z121Z1/Photographic_Style_Research/blob/c735ecbbb000426d676eea20a575718f3fe2f8e0/research/hdr-native/run_semantic_s96.py), [S108-Class-pointer-ownership](https://github.com/21Z121Z1/Photographic_Style_Research/blob/548cf16477d57253fe7003f9b3db9e8d075e8048/research/hdr-native/native_style_inventory_s108.m)|未知|
|foreign-numeric-metadata-decoding|2|[S29-half-ca00](https://github.com/21Z121Z1/Photographic_Style_Research/blob/611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079/research/styles-firmware-20261022/evidence/bright-machine-map-s29e.json), [S33-hex-address-prefix](https://github.com/21Z121Z1/Photographic_Style_Research/blob/611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079/research/styles-firmware-20261022/audit_pow_stub.py)|未知|

8个是本次审阅的事件或受影响路径记录下界，不是8次修正提交、8次代理错误或全仓库故障率。只有retention与observer两组在独立引入的两条路径中显示同一机制。两组各有一次共同的后续修正，不证明改好后又犯。native-build的argv与ARC、numeric-metadata的half误译与hex regex是底层机制不同的边界事件族，归并只是规划推断，不能宣称一个架构动作已证明能阻止全族。没有原始代理会话或明确bot作者证据，所有代理归因均为未知。详细计数分开列affected_paths、recorded_runs、correction_commits，不能据此给“最常犯错误”作全仓库排名。

## 新复现与已有证据

- `historical-replays.json` 用两个实际旧生成器和各自修正版本处理明确标为合成的IR。原版都保留readonly摘要，修正版都改为readwrite，结果为false、true、false、true。此处没有LLVM编译或Apple执行。保存数值在历史修正前后相同，不能宣称已证明像素被优化器破坏。
- 同一工具正确解码真实公开收据中的half `0xca00` 为-12，拒绝旧-6标签。它还重放旧regex与新整数地址parser，验证零填充0x形式的漏匹配。原私有Mach-O表没有取得，pow运行调用0。
- S96和S108原始macOS build.log仍在Git中。两个作业都失败在编译前提，实验没运行。未在Linux重编译它们，也不从编译失败推断私有framework不存在。
- S21/S22原件丢失来自精确源生命周期和历史availability收据。没有恢复旧IR、推断全盘无备份、用新生成件冒充旧原件。

## 保留边界

已有 `baseline_archive.Archive`、producer身份门禁、`tools/__init__.py` 和Swift `CommandSpec`的参数数组是复用基础。`ProcessRunner`把`command.arguments`交给Foundation.Process，没有在这条路径拼shell。保留这些边界，避免另造一套归档格式或把整个研究目录按时间步骤机械搬成一个包。

S16/S25的FMA、f32 pow与half发现保留为数值profile设计约束。被拒科学假设没有自动计作代理错误。`3aae24d`增量已存在模块敏感性入口，不能在新计划中列成尚待实现；611结构统计不混入这个后续提交。

## 已查反馈与缺口

实际查询PR #1、#2、#3的issue comments、inline review comments和review submissions，九个集合均为0。GitHub issues collection排除pull_request后为0。原始结果保存为`public-pr-records.json`和`public-issues.json`。PR正文是提交者自述，不是用户审查反馈。

开始调查时Slack没有可调用工具，父代理已请求安装但未完成。原Cursor transcript corpus不在Cloud，未扫描其他项目会话。原始用户聊天归因、会议上下文和私人原生材料保持缺口。

## 复现

```sh
python3.13 research/agent-architecture-plan-20261023/tools/mine_history.py \
  --ref 611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079 --output /tmp/psr-history-new
```

输出目录必须不存在。`inventory.json`记录测量时local-ref快照，因此all-refs总数可以随别的分支推进而改变；固定611祖先与树计数不变。原错误作者不明确时，架构计划应把它称作可复制陷阱，并单列归因unknown。
