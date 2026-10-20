### HDR-NATIVE-20261019 / S29–S32

所有本地Python使用内存scope；不在VM运行图像分析。归档后的增量验收：

```bash
cd ~/work/styles-gtm-ltm
scripts/local-python-scope.sh -I repo/research/hdr-native/validate_hdr.py \
  --s29 hdr-native-20261019/runs/39234705515/selected/analysis-s29.json \
  --s30 hdr-native-20261019/runs/39235294224/selected/analysis-s30.json \
  --s31 hdr-native-20261019/runs/39236923652/selected/analysis-s31.json \
  --s32 hdr-native-20261019/runs/39237510689/selected/analysis-s32.json \
  --out /tmp/hdr-validation-new-receipt.json
```

输出使用exclusive-create，已有receipt不覆盖。完整重放在macOS runner执行研究分支`.github/workflows/hdr-native-s29.yml`、s30、s31、s32，每次等上一个结束/失败读日志后再派发。S31依赖S29的合成ZIP，S32依赖S31；artifact仅保留1天，过期后先重放上游并用实际新artifact id/SHA通过dispatch参数指定，不能悄悄跳过摘要验证。两条workflow的push限定各自新研究分支，master不改。每个runner先严格核对26A434再进行计算；所有source/artifact SHA在run-provenance及各freeze文件中，不用最后提交SHA冒充实际执行的旧source SHA。

S29已执行source682c8d2，S30 d987518，S31首次ac81b29导入失败、修订540a26a；S32 d93d11f。后来追加文档/参数化的delivery commit不替代这些原始执行commit。ISO splice源自冻结gainmap_carrier.py的direct-item函数，原件不改；只扩展precision allowlist，不支持grid树的新增泛化。


### HDR-S33–S35复现边界

仅在确需新原生实验时使用新研究分支，不改旧workflow：S33入口run_hdr_s33.py，依赖S32 ZIP907be588…/artifact12180330582；S34入口run_hdr_s34.py为三组合成fixture原始冻结；S35入口run_hdr_s35.py依赖S34 ZIP44d5c139…/artifact12183626142。workflow dispatch均可给实际新artifact id/SHA，必须通过完整SHA核对；artifact只保留一天，过期时不得伪称旧id仍可用。完整已执行source/run/SHA在run-provenance-s33-s35.json。

S33源码decode_layers_s33.m把provider、Quartz、CI软件/Metal分开；S34原small map创建可复用，host full因无guided前置条件作废；S35补原prepare后捕获eps.001，因原错误.05期待而失败，不能重用S35返回码当输出通过。S36将执行相同输入并读取真实full输出，不改老记录。

归档（全本地Python受scope限制；已存在目录不能重复运行覆盖）：`scripts/local-python-scope.sh -I hdr-native-20261019/finalization-scripts/archive_hdr_s29.py <new-run-id> <new-artifact-id>`。脚本先核尺寸<40MB及剩余空间，流式ZIP SHA对GitHub digest，再核manifest全部成员；VM只展开文本，不执行图像计算。无人物像素的合成artifact不用临时secret；实际照片结果仍用密文+授权的临时传输资源并清理。

S36入口run_hdr_s36.py / ltm_materialize_s36.m，读取同一S34 ZIP（SHA44d5c139665cf9e13cbb851e6a8df6f08d1ff55e69def8ff941cd1e30019c88a）。workflow hdr-native-s36.yml只运行host，期待实际RGB epsilon.001、两guided/七dispatch；失败时先看日志及checkpoint，不能退回无参与的compile-only host。执行source5364da8；run39246456413，artifact12183985709。


S37–S41复现：完整source/run/artifact/ZIP SHA见hdr-native-20261019/run-provenance-s37-s41.json。S37/S38原workflow保持历史失败；S39/S40入口run_hdr_s39.py/run_hdr_s40.py只用合成尺寸诊断，S41入口run_hdr_s41.py比对默认144MiB和原指定初始化器自供2GiB native pool。每个新实验使用新research/vm-native-<date>-hdr-sNN及push过滤，不改旧workflow。所有图片计算只在xcode-27/26A434 runner；本地只用内存scope审计汇总/密文。

合成artifact归档用既有archive_hdr_s29.py，实际照片汇总用新archive_hdr_aggregate.py（仅允许.json/.log/.txt），密文预览用archive_hdr_previews.py流式GPG/manifest核对并限量展开。两份新脚本将保存在本轮finalization-scripts。S38预览858B、ZIP SHA491e7fd2cacef89c94d9b2df503d17599c8d5a87f60c4db61963a4d22cff266b，GPG0/PNG0；不得将空归档说成已出图。S42配方与S37一致，仅补S41资源条件、增强失败诊断及避免重复基础设施失败。


S42复现：source5ab81cf3d4b1253455dc4cd6efa1bf7e4cab75bc，workflow hdr-native-s42.yml、xcode-27/26A434，S41_HEAP_BYTES=2147483648。保持run_hdr_s42.py冻结配方及source_s37.m依赖SHA；不重新拟合。`validate_hdr.py --s29 <analysis-s29> --s30 <analysis-s30> --s31 <analysis-s31> --s32 <analysis-s32> --rgb-host <analysis-s36> --photo-suite <analysis-s42> --out <NEW-output.json>` 只读metadata，本地仍须scripts/local-python-scope.sh。额外operator_progress与原验收门槛分栏，不能从新观察通过推成总通过。完整命令/归档scripts在本阶段finalization目录保留，旧archive不覆盖。

S43复现source8b0e656，workflow hdr-native-s43.yml；输入artifact12178164564、ZIP SHA1183b4878cbdf6c8c5aa7c2dac6f4332c2575f959398bd28299fcc87d4f8c81c，单个固定合成fixture。workflow_dispatch通过inputs传入新的同SHA归档ID；过期后须恢复准确模板，不盲目重试。brew实际版本/header SHA记录，不凭API名称证明native兼容。

S44失败sourcee6138d0；不要直接重试相同导出/解密方式。新S45用同一冻结显示数学、单密文SESSION_KEY（GnuPG官方DETAILS合同），secret仅存在一次run，值不落盘/不进日志，任务后删除。失败前置GPG rc与状态事件名须先持久化到text，再解释图像/数值结果。


S47复现：实际source d657f306cdff1c0652f4538ddb5ed303d46d2d99，workflow hdr-native-s47.yml / xcode-27 /26A434。原S42输入artifact12188060302的ZIP SHA897065d3ea71e3068f2af8ee98ef8745065b923c6692f0366d98cd1b3069d621，内cipher SHAd1c3d9beabec857f972f897a7ef91f0fbee8df8d9ab270c7f97949235ae30c86。会话保留完整algorithm.mode:hex（本案9.2），不能截为2:hex；通过fd传入，值不得写日志/文件。`setup_hdr_s47_session.py`为正确本地有界提取脚本，必须MemoryHigh300M/Max400M wrapper；其它早期setup/probe仅失败取证，不照抄重试。任务后删除secret并核对空列表。

输入artifact只有1天，过期后须使用保存的准确ZIP/密文恢复到新artifact，并在新研究分支的workflow下载层解包到W/S42.zip；保留上述原ZIP/cipher SHA和原mother EXR SHA，切勿把新Zip/新母版当同一输入。当前未获全套本地存储许可，故缺该输入时不能宣称可离线逐像素重放；可按S42固定源/版本重建并先比较EXR SHA，有差异须标新证据。不得直接盲跑已过期ID。

新增只读验证：在旧S29..S32、S36host与S42photo-suite命令上加 `--display-suite <analysis-s47.json> --out <NEW-receipt.json>`，得到display_intent_progress；metadata验证本地仍用scripts/local-python-scope.sh。旧validate.py、原门槛和mask不改，extra observations不翻转总验收。S47完整H/logmap为临时计算产物，不把密文预览称为完整HDR文件。


S47已注册workflow ID为389472623。输入artifact仍有效且正确的临时HDR_S47_S42_SESSION已准备时，命令为 `gh workflow run 389472623 --ref research/vm-native-20261018`。先按100MB写入/4GB剩余/大下载规则复核，并确认无其它在跑任务。正确setup源保存在 `hdr-native-20261019/finalization-scripts-s33-s47/setup_hdr_s47_session.py`；复制到新实验命名空间，替换输出目录常量并先建立父目录，保留原s45完整校验收据路径；不要覆盖已有s47目录/receipt。早期失败版本仅用于审计。用完执行 `gh secret delete HDR_S47_S42_SESSION -R 21Z121Z1/Photographic_Style_Research` 并核对secret为空。过期输入必须按上文恢复，不能仅换ID后忽略SHA。


S48/S49源码与复现（新计算仅runner）：S48失败先读 `gh run view 39270202659 --log-failed`；S49源码固定9ab3060，见run_hdr_s49.py与hdr-native-s49.yml。先SHA/GPG验证S42 IMG2600单一密文和50MB legacy密文，再核对anchor-compatibility.json，运行 `python3 research/hdr-native/run_hdr_s49.py`（仅macOS26A434/Metal，环境W、S49_S42_SESSION、S49_LEGACY_PASS由临时secret提供，不在命令行/日志写值）。同一原legacy曝光，旧baseline_ops_s48.py源码出处见baseline-source-s48.json。S49的临时release/secret已删除，重放须新建自己的密文传输与secret并在终止后清理；不得把已清理的asset id当可用永久输入。已有源文件/归档只读，所有本机Python经scripts/local-python-scope.sh，勿在VM重算图像。


S50（仅合成常量，macOS runner）：固定source4e3c56c，执行 `python3 research/hdr-native/run_hdr_s50.py`；workflow hdr-native-s50.yml。证书为finite-collision-certificate.json，原生对照analysis-s50.json；无需原片/secret/下载输入，所有像素仅在runner临时区，artifact只有文本。新本机验证仅解析证书/校验SHA，必须经scripts/local-python-scope.sh，不在VM执行该native/数值脚本。原1e-3及floor1e-6不改；S50不复现真实照片或33点合同。


S51 native源码ae2f422（workflow hdr-native-s51.yml，driver run_hdr_s51.py，derive_display_s51.py，inputs-s51.json）。只有输入绑定/联系表布局改变，原S47数学前缀可逆还原；依赖SHA写入suite-freeze.json。四份GPG session仅内存提取并临时secret传入，runner逐份完整ZIP/cipher/GPG/EXR SHA验证，结束立即删secret。既有artifact会过期，复现前核对id/expiry，不将已清理secret当永久输入；不要在VM运行图像driver。只读本机复核：`scripts/local-python-scope.sh -I -B repo/research/hdr-native/validate_display_s51.py --s47 hdr-native-20261019/runs/39264474802/selected/analysis-s47.json --s51 hdr-native-20261019/runs/39289319764/selected/analysis-s51.json --library repo/research/hdr-native --out <一个新的json路径>`。相对路径从工作根目录执行，输出exclusive-create，不覆写历史JSON。


S52只在runner执行`python3 research/hdr-native/run_hdr_s52.py`（source1e2924b；workflow hdr-native-s52.yml，复用offset_collision_s50.m）。纯合成常量，无输入照片或secret。原结果analysis-s52.json含每档输出与三种host-offset模型残差；不要将h8通过代替h1或编码检查。

可选精确母版字节落地：`stream_verified_master.py --work-root <工作根> --photo IMG_0032 --output <工作根>/hdr-native-20261019/scene-candidates/IMG_0032/relative_linear_P3.native_S42.exr --receipt <新的receipt.json> --phase-cap-bytes <用户明确许可的字节数> --authorization-note <许可依据>`，外层必须`scripts/local-python-scope.sh -I -B`。默认100MB，当前不会容纳该EXR；没有新许可不提高cap。不保存153MB ZIP/cipher/tar，只流式SHA/GPG并复制一个EXR，最终原子no-clobber，所有原件/历史文件只读；失败只清理本次创建的partial。

本阶段编排/传输/收尾源码已按SHA保留在hdr-native-20261019/finalization-scripts-s48-s52。原数据与历史exclusive-create receipt不覆盖；复现请使用新的命名空间。单个完整EXR仅在收到新的写入额度许可后使用stream_verified_master.py流式复制，100MB默认值仍有效。


### S53–S54复现入口

源码source：S53 d54796021c2155bb329140e0e44f63287ac7e211（失败归档保留）；S54 e7b1edf81675fd4b1bda93f20b25a5dfa949ec9e。macOS26A434/image20261012.0260.1上运行；不在VM执行ARM枚举。

```bash
# research分支，单个任务，artifact保留1天；先看前一run结果再启动。
gh workflow run hdr-native-s54.yml --ref research/vm-native-20261018
gh run view <run-id> --log-failed
# 先查artifact大小、digest，再下载本次小型文本并校验manifest全部成员。
gh api repos/21Z121Z1/Photographic_Style_Research/actions/runs/<run-id>/artifacts
gh run download <run-id> -n hdr-s54-producer-record-evidence -D <new-private-evidence-dir>
```

已有归档无需重跑：`hdr-native-20261019/runs/39300758676/`与`39301402089/`。两ZIP已验SHA与逐项manifest。实际driver入口为`research/hdr-native/run_hdr_s54.py`；依赖unicorn2.1.4，clang只编译标量原生指令探针。原iOS量化指令仅128B文本fixture，完整Apple二进制没有上传。

拿到设备实际516B global记录后，使用`producer_curve_record_s54.decode_global_record(raw)`取得各节点条件前像；不要把局部grid或文件key3直接塞入这个接口。它不估计GTM/LTM像素EV。配对捕获步骤见NATIVE_TODO与producer-paired-capture-plan.json。VM只解析小文本并始终用`scripts/local-python-scope.sh -I -B ...`；冻结原validate.py不变，S54成功不修改总验收。


### S55–S59 增量复现（不重跑旧图像实验）

在~/work/styles-gtm-ltm执行，仅做归档字节/JSON检查，必须使用内存scope；输出换成不存在的新路径：

```bash
scripts/local-python-scope.sh -I -B repo/research/hdr-native/validate_scalar_metadata.py \
  --root "$PWD" --out /tmp/scalar-metadata-new-receipt.json
```

索引为hdr-native-20261019/archive-provenance-s55-s59.json；完整SHA见同名public evidence。S55/S56失败及source按runs.md保留。S56原269组仅复用、未在S57–59重跑。新validate只验证已声明的子算子和归档，输出A/acceptance_complete=false。

需要重新执行时只在macOS runner上按S57→S58→S59单个run派发；已有归档先验证，不因artifact过期重复所有上游。S57将从仓库已验证纯合成JSON的39,083B ZIP复用旧S56。成功workflow新增input_asset_id，历史执行source不因此改写。先确认没有自有run在执行、临时secret名不存在，再将private-transport-s55/scalar-maps-input.json.gpg的**完全相同11863字节密文**上传新draft；SHA必须9cd2baa4b339afe35ef19bf1784597a7a0cc7d5b4ed0ea0aac2df4ad0a265ee0，不上传照片、解密明文或archive私钥。

提取临时会话密钥的本地步骤也通过scope；gpg输出必须进subprocess.PIPE，完整正则为rb"session key:.*?([0-9]+(?:\.[0-9]+)?:[0-9A-Fa-f]{32,})"，取整段9.2:HEX，只经stdin给`gh secret set HDR_S55_INPUT_SESSION -R 21Z121Z1/Photographic_Style_Research`，不写磁盘、不打印。先用私有keyring解密核对transport-input-s56.json的明文SHA/size，再以空keyring和override-session-key-fd复验；返回码0+DECRYPTION_OKAY+精确SHA同时要求。完整已执行代码在本轮finalization-scripts归档中的fix_s55_session.py，原open('x')保护不可盲目原地重跑。

```bash
gh release create "$SCALAR_OWN_TAG" \
  hdr-native-20261019/private-transport-s55/scalar-maps-input.json.gpg \
  --draft --target research/vm-native-20261018 \
  --title 'Temporary encrypted scalar metadata replay' --notes 'Encrypted input only; remove after verification'
# 用 gh api repos/21Z121Z1/Photographic_Style_Research/releases 列表找到自己的draft ID，再查其assets取得新ID。
# 不用draft的releases/tags查询404来断定不存在。
gh workflow run hdr-native-s59.yml -R 21Z121Z1/Photographic_Style_Research \
  --ref research/vm-native-20261018 -f input_asset_id="$SCALAR_OWN_ASSET_ID"
# 先等待本run终止，失败先 gh run view <id> --log-failed。
gh run download <id> -R 21Z121Z1/Photographic_Style_Research -D <new-empty-directory>
```

立即流式SHA并按manifest核对所有成员；只接收文本/密文、小包，并继续检查100MB累计和根4GB/>1GB许可。然后删除自己的专用secret、草稿release及可能生成的tag，先查PR/ref引用；dispatch在keeper无需新临时分支。原归档/历史输出不替换；只清理自己临时数据。不要复用本轮已经删除的asset id。完整相机绑定/33点/场景/编码验收按NATIVE_TODO，不能用本子算子receipt宣布全绿。


### S60–S64 复现与只读归档验证

本机仅小型证据审查（强制内存scope，无图像计算）：

```bash
cd ~/work/styles-gtm-ltm/repo
../scripts/local-python-scope.sh -I -B research/hdr-native/validate_stats_s64.py --archive-root ../hdr-native-20261019
```

输出应为5个host/45 dispatch、9279不同码、file_map_half_gate_passed=false、A/acceptance=false。源码入口为run_hdr_s63.py（从冻结S60派生的改动逐一断言，原native reverse-key1/AppleLog和原PSO）及analyze_stats_s64.py（只读取S63捕获；原source SHA/公式freeze在ZIP中）。不要本机执行这两个重型脚本。

需要重新采集时，创建新的research/vm-native-<date>临时分支，checkout对应source并复制相应workflow为新文件、修改push分支过滤；push触发，每次只一个run，xcode-27且硬核对26A434。S63 workflow本身含显式public-key homedir、照片前加密preflight、retention1与私有临时目录清理。先读日志再处理失败；不重复S60–62已知故障。

S64重放须从本地完整S63 ZIP验证后临时提供到runner（旧artifact过期不得假设仍可下载），核对ZIP SHA77d121caf0eb5a095107fc412a215c6da5946ac0ab94b008a55575da7a4ae153；仅用该密文的临时session secret，不能传archive私钥。脚本里的artifact ID是历史来源，重放须显式更新已核验的传输入口，不能把旧ID新跑失败误作科学失败。空间数据始终加密，立即下载文本/密文并核对manifest及GPG/明文成员SHA，再按PR/引用审查清理自建secret/分支/release。没有新的样张明文上传。各run完整source/artifact/SHA见evidence/s64/archive-provenance.json。


S69复现：在新增日期研究分支复制s69 workflow并更新push filter，xcode-27硬核对26A434；export W=$RUNNER_TEMP/新的私有目录，mkdir -p "$W/out"；python3 research/hdr-native/run_hdr_s69.py。只做CPU绑定/原PSO属性，不调用process，不依赖Photos图库。retention1天、马上下载校验；失败先读日志。原始归档见hdr-native-20261019/runs/39338027870、39338223690、39339778014、39341678257。整数几何模块stats_geometry_s69.full_frame(w,h,32,1024)有明示前提，不作为图像验收。


S70–S71: run `scripts/local-python-scope.sh -I -B repo/research/hdr-native/validate_matte_roi_s70.py hdr-native-20261019/runs/39346448714/artifact-12231437053.zip` from styles-gtm-ltm (VM 400MB cap). This verifies all original manifest members and finite step counts, never a global sampler certificate. Original failed parent:39345177157/artifact-12230252826.zip. Native reproduction: workflow hdr-native-s71.yml on an authorized new research branch/ref; no parallel run,26A434/retention1; source derivation SHA in original derivation-s71.json. Use mask1 per existing S56 static proof; do not edit archived S70.

S72: workflow hdr-native-s72.yml on an authorized research ref, source a5ea4e2; pure CPU framework bindings. Check evidence/s72/run/native.json and receipt, compile/run source with matching26A434 UUIDs; do not infer pixel/scene gates from job success. S71 same validation command now additionally reports post-native CPU UV56-component replay (not new holdouts); helper/source SHA in evidence/s70-s71/uv-model-validation.json.
