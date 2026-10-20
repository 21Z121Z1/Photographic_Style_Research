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

S73: from styles-gtm-ltm run `scripts/local-python-scope.sh -I -B repo/research/hdr-native/validate_consumer_roi_s73.py hdr-native-20261019/runs/39353695210/artifact-12234397335.zip`. It verifies all original SHA,54 frozen requested-ROI cases and the post-native standalone implementation; no new holdouts/full consumer proof. Native source/workflow: hdr-native-s73.yml,4a34917,26A434 required,retention1; default master untouched.

S67 full original ZIP now retained: `unzip -t hdr-native-20261019/runs/39335997594/artifact-12226746912.zip`; `sha256sum` must equal b1b95a5df2ee252eec41153cdce6f88d521c36490fc5422bbacb734a208509f1. Historical manifest uses `bytes` rather than `size`;29 payload SHA already verified by supplemental receipt. Essential numerical/AIR replay remains the unchanged validate_stats_s67.py selected-tar command; no native experiment repetition.


S75–S80（26A434/image20261012.0260.1，artifact retention-days:1）：6份完整原ZIP合计834255B、294个payload成员及所有recipe源码SHA已校验落地。无人物输入、临时secret/release或Apple可执行binary上传；只用公开合成图案。源分支research/vm-native-20261020-hdr-s75至s80，保留研究分支research/vm-native-20261018。失败均先读gh run view --log-failed，再依原生日志/静态证据修改新版本，未盲目重跑。ZIP路径hdr-native-20261019/runs/<run>/artifact-<artifact>.zip；manifest SHA/source SHA见evidence/s80/bundle-index.json。

|阶段|source commit|run / artifact|结论|原ZIP SHA256|
|---|---|---|---|---|
|S75|0d08bb13bb0f6980674addb33d3bd939333bfd53|39387345347 / 12248270752|failure|44a413d9e9402dabd113cda68036a007d3d828ebeebef3e756c76d17ededf857|
|S76|de39c5fd11685f7ee0f1f333a8811b15e2df98c9|39387725065 / 12247894805|failure|03d611d8c1fd0e059cdc6e7161737fb863ca380881a7f3d6727c8dac7bc50071|
|S77|c2e80eedf3a25fdadbcf2ad08016ec869ddc04b8|39388810043 / 12248522157|success|dc31a1e3b4706521d914e5d41a0930f5dcbe95ffdedb2fc552bafabc7dacfcd1|
|S78|98e67973d745de83aca865d9317034ad5a33743c|39389860461 / 12249385894|failure|ee17bf5a1519b023d3a6a715f56c955649fe311e2864070bed866a8a04f78596|
|S79|b5c9d8e5e163e782c2f65acf67dfe0cc0091dcdf|39390615195 / 12249605976|success|bfacffe4ad6f10aeeb4e4a9d47bcdf35237dccf1c84dc5543d8c3c2677a0b83a|
|S80|efccbe9887b9fec8129394ac8c829b8548b8c727|39391600201 / 12250205961|success|a821de2eab035d2189343c27a9602a42ca5ce9f9a358d92f17046294290cf825|

只读复现完整性及既有数值记录（不重算像素，不执行原生，不改validate.py）：

```sh
cd ~/work/styles-gtm-ltm
scripts/local-python-scope.sh -I -B repo/research/hdr-native/verify_ci_evidence_s75_s80.py hdr-native-20261019/runs
```

原生复现仅macOS runner：源文件run_hdr_s80.py及probe_consumer_ci_s80.m、ci_status_s80.inc、ci_trace_s77.inc、stats_context_s79.inc、analyze_ci_s77.py；workflow hdr-native-s80.yml列出全部参数/源码SHA并限制build26A434。先mkdir "$W/out"，再python3 research/hdr-native/run_hdr_s80.py；只在新问题需要时派发新run。原stats92-float fixture不是相机统计，不把AA gate当模型验收。累计125MB许可有效，根分区至少4GB，完整EXR仍未获单独许可。


S75–S80传输收尾（已验证静态/归档完整性）：六个terminal run的原ZIP均已保存，并在删除前核对所有PR head/base引用为空、源码已在远端保留研究分支。六个临时ref全部返回DELETE204且随后精确查询为空；本批未创建任何secret/release，未修改master或其他分支。一次清理预检的公共API读取返回curl22，发生于任何删除之前；后续同一run读取200/completed，原失败HTTP状态未保留，不能推断根因。改为配置CLI凭据仅在内存/stdin访问api.github.com，重新检查全部前置条件后清理完成，未重复原生实验、未写盘凭据或签名URL。详见research/hdr-native/evidence/s80/closure.json及hdr-native-20261019/cleanup-s75-s80.json。原归档、样张、冻结模型及consumer-goto-v8两个受保护文件均保留。


S81 只记录方向调整，无原生实验可重跑。查看 PRACTICAL_ACCEPTANCE.zh-CN.md、evidence/s81/scope-change.json 和 phase-summary.json。S75–S80 原完整性复现入口保留，不为此政策调整重复执行；旧 validate.py/validate_hdr.py 的严格失败未改成通过。后续真实样张工程报告另列 engineering_accepted，不能用它替代物理 scene-referred 验证或“99%准确率”。


S82/S83（源码在研究分支17fcc3b）：新控制semantic_strength_s82.py；新实用驱动run_hdr_s82.py；输入哈希inputs_s82.json；合成检查check_strength_s83.py。S83复现仅macOS26A434：设私有临时W并mkdir "$W/out"，安装numpy2.3.4，再python3 research/hdr-native/check_strength_s83.py。该命令不含照片/密钥，只复现新控制的结构检查，非旧native逆证明；现有证据足够时不要重复运行。

S82还不能执行：先取得针对公开密文预发布release和两条临时session secret的明确批准；批准记录必须包括release_tag=hdr-private-s82-20261020、input_total_bytes=110814893以及两项approved=true。随后只用现有归档，不复制/解密原照片到VM，不向runner提供私钥；归档完整性和各成员SHA在任何像素处理前检查。workflow hdr-native-s82.yml保留contents:read、retention-days1；初次需push其单独触发分支，不能盲目重试。未获批准前不创建任何传输资源。源码/API/域/预览说明见PRACTICAL_SEMANTIC.zh-CN.md。


### S82–S87 可复现入口（本地仅元数据/哈希）

```sh
cd ~/work/styles-gtm-ltm
scripts/local-python-scope.sh -I -B repo/research/hdr-native/verify_practical_evidence_s82_s86.py hdr-native-20261019/runs
scripts/local-python-scope.sh -I -B repo/research/hdr-native/verify_carrier_s87.py hdr-native-20261019/runs
```

第一条校验S82/S84/S85/S86保留原ZIP/public manifest、原commit源码SHA和已存GPG收据；第二条专门校验S87原ZIP/派生成员清单，明确报告原runner manifest缺失和run封装failure，同时核对五图整数SDR0及实际code/headroom公式。两条均不重做GPG解密、图像计算或Apple原生执行。完整GPG与每个私有成员的流式校验在archive-receipt.json，人物预览在原密文ZIP内；VM未解码/写入人物明文。S82入口run_hdr_s82.py/semantic_strength_s82.py，S85为carrier_readback_s85.m，S86仅选择matrix6/10bit；原生仅xcode-27/26A434。S87入口run_hdr_s87.py，子case carrier_case_s87.py，原生carrier_readback_s87.m/read_sdr_s87.m。workflow列出依赖、只读权限、retention-days1，源码/holdout顺序在evidence/s87/source-freeze.json。原S87会复现末端90KB封装失败，无需为改变run颜色重复像素实验；后续新任务另估容量。数学目标是RGB压力图，不是艺术HDR或生产ISP逆。

本次所有临时触发ref在原ZIP/GPG验证、PR引用为空、源码保留研究分支后删除；S82两条secret及prerelease/tag已删除。需要重新原生执行时先用新研究触发ref按现有串行流程准备，密文传输的临时secret须从既有本地归档以stdin提供，不在命令/日志中记录值；不得修改旧workflow或复用已删除ref。所有原件/冻结模型/历史archive保留，旧validate.py不改。125MB累计许可不重置，根分区≥4GB，>1GB下载先问，完整输出另核预算。


S88复现（代码固定于caae6869d2824884d36f27c475c4684744f0be37；全部图像计算只在xcode-27/26A434）：
```bash
gh workflow run hdr-native-s88.yml --repo 21Z121Z1/Photographic_Style_Research --ref research/vm-native-20261018
gh run view 39428400454 --repo 21Z121Z1/Photographic_Style_Research
```
精确复现应另取source commit创建新research临时分支并修改新workflow的触发绑定，不能重写历史分支/workflow或盲目重复run。此新版不依赖过期artifact、secret或私钥。原结果ZIP已在hdr-native-20261019/runs/39428400454/，外层ZIP/providerSHA见evidence/s88/run/archive-receipt.json。archive内carrier.tar.gz.gpg包含成品HEIC与旧transport mask，contacts.tar.gz.gpg是固定ACES三联及误差点witness。只在受控本地按现有GPG私钥流式解密/解tar，不把人物明文上传或提交；本阶段VM仅流式SHA/GPG核对，没有解码图片。S88所有原始数值在analysis.json，原生SDR完整行哈希在native.json，门槛逐项结果在phase-summary.json；本次不覆盖旧validate.py或宣称总验收通过。


S89复现固定于b03beb93cfd1b5093fd8bed314ff53a76842febf；.github/workflows/hdr-native-s89.yml/xcode-27/26A434，五case顺序及角色见inputs-s89.json。原workflow会重复最终1.5MB容量失败，历史代码不修写。原始ZIP已在hdr-native-20261019/runs/39430695395/。元数据复核无需图像计算：
```bash
scripts/local-python-scope.sh -I -B repo/research/hdr-native/verify_independent_hdr_s89.py
gh run view 39430695395 --repo 21Z121Z1/Photographic_Style_Research --log-failed
```
归档恢复只为创建已检查的嵌套公共文本目录，并从已保存原ZIP补齐；s89-archival-recovery.json说明，不要覆盖任何原ZIP。六个密文只含contact/数值见证，不含新完整HEIC或EXR；S88的完整HEIC密文保留。每图精确派生源码/替换证明、算子/中间headroom/最大RGB点分类在evidence/s89/run/，原门槛逐项布尔在phase-summary.json。下一新实验应另建文件，不能为了绿灯修改本次冻结容量或数值门槛。


S90复现source0a2a4fe66a63e564504926b30110a95820bb1133，run_hdr_s90.py/.github/workflows/hdr-native-s90.yml，xcode-27/26A434，最差开发IMG2600固定10/12bit；原代码会重现12bit缺gain导致的run failure，不为绿灯改写冻结文件。原ZIP已保存于hdr-native-20261019/runs/39435568710/，元数据验证：
```bash
scripts/local-python-scope.sh -I -B repo/research/hdr-native/verify_display_diagnostic_s90.py
gh run view 39435568710 --repo 21Z121Z1/Photographic_Style_Research --log-failed
```
完整显示、亮度分层与支持边界见evidence/s90/run/analysis.json、native-checkpoint-12.json、codec-versions.json和phase-summary.json。密文previews.tar.gz.gpg含10bit三档ideal/native/difference×8 contact及数值见证；差图放大仅用于诊断。VM没有解码图像；没有完整12bit HEIC或EXR交付，不把SHA等同文件已持久保存。


S91：source c27610d0dd63ca70f6bca4acfe7f9c9068756df5，run_semantic_s91.py/inputs_s91.json/.github/workflows/semantic-native-s91.yml。原源码可复现pixelFormat类型冲突，不修改它。输入只允许新加密包+临时session secret，禁止提交人物明文。原ZIP在私有日本存储runs/39474288686/；连接选择保存在工作目录的storage-jp-20261021.json。公开证据验证入口为evidence/s91/run/archive-receipt.json、manifest.json、build.log和closure.json，精确private成员SHA在receipt；原私钥仅本机GPG使用，未上传。原生失败日志命令：
```bash
gh run view 39474288686 --repo 21Z121Z1/Photographic_Style_Research --log-failed
```
归档通过短期签名URL在日本直接写独占.part，provider长度/SHA通过后原子改名；HK仅接收public小文本，通过SSH读取cipher流做GPG/tar hash。收尾脚本的自动重跑原生选项始终关闭；核验失败保留现场。具体中断保护的首次nohup启动未形成进程，之后由前台scope实际执行归档/清理，完成状态见closure；不宣称先前后台监控成功。


S92复现source13780b9b6bca8bf5a5ac6dcb846696664055f6bc，run_semantic_s92.py/inputs_s92.json/semantic-native-s92.yml。wrapper对原S91驱动仅作精确类型/传输绑定替换，S92-binding.json与S92-derived-driver.txt可反向核对。输入仍须使用加密+临时session secret，清理后的旧asset不能假定永久可取；创建新传输绑定时保留旧输入SHA，不修改原源码。完整原始ZIP在私有日本存储runs/39477063576，receipt列provider/private成员SHA；HK只保存public证据。
本地小型参数核对没有解码图像：从已核验cipher流读取bytes-5.bin、copy-control和18点空间扰动JSON，见evidence/s92/context-metadata.json；source0/skin11 affines是原生参数，不是由图像对齐拟合。原尺寸图像重放和统计均在runner；源图尺寸5712×4284，已测试的每块ROI仅512×384，不能把原生inverse JSON full_frame标志用于整幅验收。


S93复现source e8b6d0c0cbca2be151d995295851cca3f04f6910，run_semantic_s93.py/inputs_s93.json/semantic-native-s93.yml；run39480275514，retention-days1。必须加密输入+临时归档专用session secret；原输入SHA52ea41f0dd16590cef83abfd8093ccf8082994113e0c2cee86f90c42f7ab21c2，旧临时asset已清理。S93-binding.json逐项替换/派生源码，S93-seed-binding.json与include文本给出8种子方案和旧include不变证据。所有图像重放/统计在runner，HK本地仅300/400MB scope内处理文本与GPG头；不重跑冻结S5–S92。
原ZIP仅日本runs/39480275514，hash及145成员见archive-receipt.json；像素/params/masks/contact只在GPG内。不要重跑S93传输测试：已有transfer-local-verification.json；32KiB头缓存完成后清理，诊断记录仅保存元数据。新run采用storage/verify_remote_private_v2.py的verify_private(plan)，plan必须给run_id/source_commit/os_build/relative_path/ZIP_bytes/ZIP_sha256/cipher_member/cipher_bytes/cipher_sha256，不含预存session；连接从私有O/storage-jp-20261021.json选择。install_helper()只在缺少工具时传源码，已装SHA相同则复用。fetch/inspect可沿用日本v1，禁止再用其stream把整cipher回HK。未来archiver应保存独立receipt后按旧终态/PR零引用/源代码保留规则清理临时传输资源。
GPG头只用于取session：完整PKESK保持，partial body的长度标记去掉并重封截断加密包。该短包认证状态无效；最终证据必须来自日本对原始cipher全流的returncode0与manifest/member SHA一致。session只过SSH stdin与匿名fd，私钥不出HK、session不进argv/文件/日志。新格式无法解析时停止，不自动取大文件。日本hash/GPG仅流式、不解码图片，计算/预览继续runner。所有跨区小型payload计数不含SSH协议开销，不能当作云账单的精确计费字节。


S94 sourcebf117dccb793e2ceaaff85b5e2ee9a368cd54353/run39486436418；run_semantic_s94.py、semantic_fullframe_s94.m、inputs_s94.json与semantic-native-s94.yml。失败日志已读（gh run view39486436418 --log-failed，副本native-failed.log）；原生具体异常在evidence/s94/run/native.log，驱动缺少calls_path的断言是后果。后续新版本先建日志父目录并记录不匹配dispatch；不编辑S94已有源码/产物。归档器使用storage v2在日本完整认证；这份密文仅8465B，头部即全小文件，流量纠正附加记录，原receipt SHA不改。


S95入口run_semantic_s95.py、semantic_fullframe_s95.m、inputs_s95.json、semantic-native-s95.yml、s95_observer_binding.json；source475e050dc0a4fd7fc30528c9bf9a65d875129596。绑定可从S94原生源逐项精确替换恢复并检查SHA；预览只改stride10，不改S82算子。已触发run39488329547，不再push或dispatch同一验证；先看其status/jobs，原生失败先取--log-failed。新归档协调器storage/verify_remote_private_v3.py，后台仍用v2日本GPG helper，差别为小cipher字节计数和要求显式新receipt，不默认重跑S93。


S95终态39488329547，先读已落地native-failed.log与evidence/s95/run/native.log、native-calls.json、native-execution.json：原native program rc0不能替代四次renderer process rc−12786。恢复入口无需再等旧queued状态。资源假设静态来源已保存allocator-and-guided-error-source.txt，原文本SHA/UUID/binary SHA及行范围在static-provenance.json；只复用已有文本，没有下载Apple binary。未来容量对照前记录实际请求与guided返回，再据真实PI output.region建全帧参照；不重跑旧S41合成组/旧30个scalar-guided实验，不做半码格点精度追逐。


S96复现失败：在commit c735ecb检查research/hdr-native/run_semantic_s96.py:56与evidence/s96/run/build.log（无需下载密文）。clang输入误含旧S95 unit，缺generated native_filter_probe_s95.m；应只编译semantic_fullframe_s96.m，由它include已冻结S96派生native/observer/capture。修正版应单独冻结driver SHA和精确替换表，不改S96 source或把本run称为像素验证。原ZIP留日本，不重复回传。


S97 source5f8646d/run39499003223：读取run_semantic_s97.py、s97_driver_binding.json和冻结S96 native/observer/include；driver精确修复clang单一translation unit，native代码不变。输入仍仅2.56MB原始HEIC密文，非旧320MB结果包。复现先检查26A434/loaded UUID/容量命中、所有原返回0，再检查owner-coverage.json与native-CI-fullframe.json；analysis.json的practical patch gate是分块误差，不是inverse认证。private原件留日本runs/39499003223/artifact-12300720827.zip，已做GPG/70成员SHA核验；无需为补文档再次下载或回传。临时release/secret已清，未来新run用新临时凭据，不恢复历史值。


S98复现源码1165f8a：run_semantic_s98.py、semantic_fullframe_s98.m、fullframe_analysis_s98.py、s98_binding.json。原S93 include保持SHA23fff931a0914e5956ccee79bc715ee60ecaff936658ea2f9e2fdf1a218f92e0；prefix/native精确替换和单一clang translation unit已冻结。小型4×6合成几何只检查10条实际owner接缝、mean0.5及稀疏预览位置覆盖，不冒充照片验证。新run只取2.56MB原HEIC密文，旧S97约320MB结果包不重传。当前结果待run39504949862，先看其日志/终态；不要重跑旧S89数值或12bit，仅当补交完整文件必须重建时复用原S42/S88 AST。


S98实际结果入口：evidence/s98/NUMERICAL_RESULTS.zh-CN.md、run/analysis.json、inverse-roundtrip.json、review-checks.json。下载无需重复：原ZIP在日本runs/39504949862/artifact-12304682191.zip。每个owner的native.f16是本次校正baseline，使用operator-strength0.5-loggain.f16按metadata重建B_RGB*exp2(loggain)；mask false保持B。不要把它当原HEIC SDR的直接gain，也不要把recovered-effective.f16当scene master。F_neutral-estimate、native-inverse-roundtrip与native reference均留档，semantic_strength_s82.apply可重建0/0.5/1政策。3271预览ledger在私有tar，public SHA与GPG167成员清单一致。无需重新传旧S5/S8/S97大包。


S99失败复现：3936cb99的run_semantic_s99.py只extract(photo,RES)后，直接source photo PRIVATE/native-key1-source；冻结Decode要求该dir已有styles.plist/linear.heic/delta.heic。run39513947146 source-native.log记录最终catch写目录也失败。新实验必须先extract(photo,SRC)，保持source_s37原字节；原失败日志与密文归档不覆盖。
