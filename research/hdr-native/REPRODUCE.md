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
