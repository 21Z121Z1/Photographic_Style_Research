### HDR-NATIVE-20261019 / S29–S32

|阶段|run / branch / source commit|artifact / ZIP SHA|范围与结论|
|---|---|---|---|
|S29-failure|[39232934429](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39232934429) / research/vm-native-20261019-hdr-s29 / 5f437a1e7ef30fdd2e1e5b395ebc49021b42ac2b|12177642753 / 80353200f9c53fb198aff5fde2394d37e1141d597b8f6963df49c748bd58ca39|初次原生缺map异常，证据保留|
|S29|[39234705515](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39234705515) / research/vm-native-20261019-hdr-s29 / 682c8d2dc13dd3f4da52557985cc2f96fc8c3199|12178164564 / 1183b4878cbdf6c8c5aa7c2dac6f4332c2575f959398bd28299fcc87d4f8c81c|35次headroom公式通过；自动writer SDR/HDR目标未过|
|S30|[39235294224](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39235294224) / research/vm-native-20261019-hdr-s30 / d9875187ae6eb017394fbfd253cd9f948e668ef9|12178892208 / be3368a6fc76c005e040925d03fb517f1cbd2b0540ac5c07afc48434f639e383|70次未编码通过；10次writer输出legacy mono8，ISO失败|
|S31-import-failure|[39236730793](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39236730793) / research/vm-native-20261019-hdr-s31 / ac81b29e8a6dbb6a57776f02151f9178539a99b6|12179976358 / 8668fbfba161e17ebe7c56bed65c46d06248a1ab09a59e19458546678b79c5aa|导入次序错误；无像素证据|
|S31|[39236923652](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39236923652) / research/vm-native-20261019-hdr-s31 / 540a26a3cc128ad6143c8641b8a55753f44c4977|12178638557 / f4d90ac39646f813aae1bba6044167e1e2af03a8aab3c4d1575f337f8b918cdd|8/10bit10例SDR max0；map域错误，12bit5例nil|
|S32|[39237510689](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39237510689) / research/vm-native-20261019-hdr-s32 / d93d11fecb9368d912a7e9a0ccccfd488d2b79a1|12180330582 / 907be588e641ba3ec55a6aa5e0cf6ba9eca5bceae9e602c3f3b3010f2b3ed8bb|单RGB合成图matrix/bit/primary/aux诊断，见analysis-s32.json|

均macOS27.0.1 26A434 / xcode-27-arm64 image20261012.0260.1，retention-days1。完整artifact大小/manifest SHA/源码commit在hdr-native-20261019/run-provenance.json。原始ZIP只增不覆盖，逐成员校验，像素数组保留在ZIP未在VM展开。全程只用合成输入；无secret/release或人物上传。workflow绿灯只表示收集完毕，子项失败如实保留。原master与冻结文件在最终audit中核对，临时研究分支先保留源码commit至持久分支、确认PR/refs后再清理。

S29–S32收尾：全部实际执行commit已在研究分支research/vm-native-20261018@f9d7e6de0e67fb31fd55acf1f992428753236fdb远端验证保留；四个本轮临时研究分支在head/base全状态PR和其他refs检查后删除（无PR/引用），本地同名分支亦删除。6个job的always runner临时清理均成功；本阶段无repository secret/release或人物上传，master未变。证据：hdr-native-20261019/transport-cleanup-s29-s32.json。


### HDR-S33–S35 原生证据

- S33: branch `research/vm-native-20261019-hdr-s33`，source `659ddc6281293dd7a2ba0de3c5ddfd555e05a54a`，run 39241066681，artifact 12181247833（11537162 B），ZIP SHA `5d3b13d965e4cf6d498f30b0fbf104b8da607b4dd9c7b846f3c37690ae8a9f34`；26A434 / image 20261012.0260.1，retention1天，全成员SHA校验通过。
- S34: branch `research/vm-native-20261019-hdr-s34`，source `47e03177b8ac43dff8cafac11cdb965b4ebdf42a`，run 39244341548，artifact 12183626142（7757954 B），ZIP SHA `44d5c139665cf9e13cbb851e6a8df6f08d1ff55e69def8ff941cd1e30019c88a`；26A434 / image 20261012.0260.1，retention1天，全成员SHA校验通过。
- S35: branch `research/vm-native-20261019-hdr-s35`，source `42f0b0f878cc4c3809f63824ed1b5b64c1e2e0d6`，run 39245992644，artifact 12182822786（393727 B），ZIP SHA `a086807ce30399620ea85a934f8b6b8e5af63a7cac20f9abad18c2e4ad6109b0`；26A434 / image 20261012.0260.1，retention1天，全成员SHA校验通过。

S33 workflow成功仅为诊断完成；12bit目标失败。S34成功不能替代guided前置条件，small map对照有效、host full oracle不合格。S35因eps预期错误失败，实际捕获RGBeps.001；读失败日志后才准备S36。没有新人物输入或整份Apple二进制上传，没有secret/release；临时分支待源commit保留及引用检查后统一清理。

S36：branch research/vm-native-20261019-hdr-s36 source 5364da810b66eb7f71992d4ec9a35360686a1b17，run39246456413，artifact12183985709（3983408B），ZIP SHA 0bee8e0a3a950e98b503cca3ffc805d8927311ade3fc86105870245c2464a2cb，26A434/image20261012.0260.1。原RGBhost oracle三例合格，冻结NumPy half仍false；retention1天，归档全员SHA通过。


### HDR-S37–S41 运行记录

- S37: research/vm-native-20261019-hdr-s37，source d4e9fe76f07d1a5c465496617a60c8ce6049585d，run 39249246604，artifact 12184577945（6167B），ZIP SHA a3edf0ee53573b32872d99759c047664e458595e0028bf20861866dfdd52bc63；26A434/image20261012.0260.1，retention1天，全部manifest成员已校验。
- S38: research/vm-native-20261019-hdr-s38，source 10f7588b821769803f9a684e35815d8b2f1b2973，run 39249843977，artifact 12184589250（9814B），ZIP SHA 938994dede4296ea717bc88b7a1962944a6f332c311a14ce3dfefba64bcdfaa9；26A434/image20261012.0260.1，retention1天，全部manifest成员已校验。
- S39: research/vm-native-20261019-hdr-s39，source 0ace58770f40d3fa7b57b3aad4eaa9873a2d1c5e，run 39251392813，artifact 12185253044（2855B），ZIP SHA 196e3eb360bfc4d9f8fb30f0aa40423ca1676a49fb99096ab472e2d63a366aaa；26A434/image20261012.0260.1，retention1天，全部manifest成员已校验。
- S40: research/vm-native-20261019-hdr-s40，source 90ecd44003fd5e0ad35e5812ee960c9fb5ea6db8，run 39252096517，artifact 12185683191（32438B），ZIP SHA a4648af370c5e99ea5c21010a64bb8a18d39574c9af02b9ebfebb05fe8eacdc3；26A434/image20261012.0260.1，retention1天，全部manifest成员已校验。
- S41: research/vm-native-20261019-hdr-s41，source 4807ebb68bc88d78bd8c9082607d43f1f6b15763，run 39253046695，artifact 12186850154（48910B），ZIP SHA 89dd0e3150c46b39feb949c8883e8374fb1d4a00d6d016f984dddbedcd6e2dbc；26A434/image20261012.0260.1，retention1天，全部manifest成员已校验。

S37/S39为编译失败；S38源准备完成但候选失败，密文预览只含空manifest；S40作业成功只表示诊断完成（大尺寸原host未通过）；S41容量干预全部四例完成且小图四份读回SHA相同，不是五张照片通过。

|S42|research/vm-native-20261019-hdr-s42|5ab81cf3d4b1253455dc4cd6efa1bf7e4cab75bc|39254061338|12187592176 text /12187257542 encrypted preview|26A434 /20261012.0260.1|5 original-size photos,2 new-recipe holdouts;10EXR storage exact,25 unencoded native headrooms pass; anchor/physical/encoded gates remain|

S42 text ZIP `17bc8b897f51d04779f8a6b3543ccbbc980dc247d25e235059895f01ffeef0f9` / manifest `8c378bbce6b411b3ec708ad99fd0b54a707061d173bf75f273c28ef8f3a7fb0a`; preview ZIP `5243842ad5fc34096354b6df4a7d240d39c240b5d5ee7e209832648ffd70d802` verified GPG/all members,5localcontacts. Full ciphertexts not yet locally archived under current quota. Details: run-provenance-s42.json.

|S43|research/vm-native-20261019-hdr-s43|8b0e656fedbf75dc6bcb2a86e846e71bc318def7|39256675682|12187639046|26A434/20261012.0260.1|AV1 provider4/4, mixed-gain aux0/4; failure retained|

ZIP SHA `8884bf17ec4b09323c947962926abb01e13b185217778595ac8275681211478a`; manifest `abfa67ebae914dd923020ab5c03d32b3badb4a4a8c3ef2076a9736f8ad105f8d`; all members verified.

|S44|research/vm-native-20261019-hdr-s44|e6138d042336fdcf2d2bc5ccb4e758455c7339a6|39259341766|12190285705|26A434/20261012.0260.1|GPG/gzip prerequisite failed, zero new images; secret removed, exact cause not inferred|

ZIP `8d9b49f19960bd9b7bb9ed13a95ec4fddb106857a92d498c7b92035da1d90e31` / manifest `44fda22697d45c96f5018c5eace974003c8fcdf6435df11b7214249560597872` verified; immutable driver.log retained.

|S45|research/vm-native-20261019-hdr-s45|24d618dd7467fce33452d9bc012891b8ade40389|39262070080|12190163508|26A434/20261012.0260.1|missing-rg preflight exit127; zero new images; secret removed|

ZIP `50a57237ace2cf0770d8ed43d8c387883ca496ad14f010ea34ee50a42418ec2f` / manifest `4b9b6ba029122012d364f65abb0251e533adf896694fe6b6dbfa24bf2a6d37ef` verified; log-failed archived before fix.

|S46|research/vm-native-20261019-hdr-s46|3f876035d17f6b2fb93fb834d343661492ef949c|39262796015|12192760214|26A434/20261012.0260.1|AEAD identifier truncated; small empty-cipher control locates error;0newimages|

ZIP `618b87b2ceb734829e47f9c32ecd54c5479edd1970de0c1129d75b0eaace60a9` / manifest `117052052970e656140aa16c95b1397fb4312faa95021a01e80318ad53e70cfb` verified; secret removed.

|S47|research/vm-native-20261019-hdr-s47|d657f306cdff1c0652f4538ddb5ed303d46d2d99|39264474802|12192990470 text /12192990472 encrypted previews|26A434/20261012.0260.1|One unchanged24MP master, independent exposure/HDR,10native equations pass;zerooffset scoped pass;common offset relative/h1fail|

Text ZIP `cb50ff395ff71f6b4b52d8d7f5fc7706965993e66734bd398514473bf712bcdb`/manifest `caa31e04df8c3bab2b0c9a93e8129825ec9705b4950604e43ff53dc8b2d471ef`; previewZIP `3fd3f2025b3696a5893318949c71f4ff7f7828840bdb8ca87eb29f46ecc65fb7`/cipher `806135785421f6fa5080e49a4c7a88ee2282666a67d2a4972158f13bc7ead8f8` verified. Source commit is distinct from final documentation commit.


S33–S47收尾审计：所有实际source commit已fast-forward保留在research/vm-native-20261018@c12f2aa。确认15条临时分支无PR head/base或外来ref指向后删除，local16条含最终临时文档分支亦删除；secret/release/活动run均为空。既有PR#1（其它研究head→本研究base）仅记录，未通过API创建/关闭/操作。7份受保护文件、原始171条claims及文档/CSV历史前缀SHA不变；旧workflow没有修改或删除，15个新增workflow所有artifact保留1天。最终A阶段及总验收仍false，目标active。详见final-audit-s33-s47与transport-cleanup-s33-s47。


|S48|research/vm-native-20261019-hdr-s48|7d3918575afb852e3be048f5f54da313db517797|39270202659|12195995208|26A434/20261012.0260.1|draft asset403; no driver; ZIPa3c506339e5bb05d301d875b207ee0fffd6ecdbcd65ebcb0ba49b47357aebbee|
|S49|research/vm-native-20261019-hdr-s49|9ab3060ff6780f0dd0e154f5036a6243503c6659|39275948343|12196823572 /12196673747 encrypted previews|26A434/20261012.0260.1|paired same-half-anchor full-size comparison, old/new outputs unchanged; tradeoff retained, no acceptance pass|

S49 text ZIP eed057a6b471e1f3db1db31c0ee717ea1a59aeaf924df607358e9d50a3529de4, manifest ad64dec9de23cbad3510ef7018baf08f3efc4c8e2322499ce9857a46acb964aa; preview ZIP c042530fe896c90f77130d30adae2056b59256b36b5f40485a3dfa90a55568a3, cipher ba43a2654a764ca9757824e4ea0452f3c8c677c2199e22139360d26152990f6d, 9PNG verified/one localcontact. Secrets/draft/tag cleared; source branches preserved pending final keeper/ref audit. Artifact retention1天。


|S50|research/vm-native-20261019-hdr-s50|4e3c56c829ac09fe17cb1e7fa20bd1cc5e671af2|39280458478|12200760926|26A434/20261012.0260.1|finite common-offset collision certified; native positive controls; original relative gate retained|

ZIP 60c09dafd81a2c9e07f780097d94d05866c4c1dee5e7ab3cc84f885e4c48b5ed, manifest fc9b2758ccc903cc31a4f46382b3e815a7b0f41696b45bfc23eceaac7074147b; native full job log archived. Control-plane queued discrepancy and later completed/success are in evidence/s50/terminal-state.json. No temporary secrets/release.


|S51|research/vm-native-20261020-hdr-s51|ae2f422b8e09878bed18826f83142fb1d2ba983a|39289319764|12205456068 /12204689131 encrypted contacts|26A434/20261012.0260.1|4 new display outputs +S47=5 images,2 formula holdouts,50 unencoded float comparisons pass;three full commonoffset targets fail|

Text ZIP ff88e6f6ab2fc2c6739402e3766560a0a5fe348df9285c340b86ec8fcefdda6a /manifest 41269ca41258e94956b22451f9361a488e8b13bd9f3e6f37d0fd6d654d4afe88; preview ZIP 4c15f1b07fdbc685f4cb40f1048d7ae00d8d4218713b2b12647b3682adeb77e2 /cipher aec13a3f2f5d40976212618f2667f9b0a4907354ab45fe345f49df2f5f95aa01. Full SHA/GPG/member checks done,45 preview-input checks total unchanged. Four temporary sessions deleted, no release/private archive key. One run of this HDR goal at a time; independent other-branch runs only observed, never altered.


|S52|research/vm-native-20261020-hdr-s52|1e2924bd17cc47e45b1c8a6753be77e288cbd004|39293130622|12207396048|26A434/20261012.0260.1|4x5 finite offset contract, h8allpass/h1allfail; no photo rerun|

ZIP b34024a807f1d71516a2861de6c0e2badb7414d6c4925ab501499c5713c69d31/manifest 5a37390e3a25d3a214a0cd1ebb94b6a7cada724ef1bc69856b0d210a1c03755a; every member verified, no secret/release. Overall success means the probe completed, not a complete target/inverse pass.


S48–S52 科学检查完成：五张原尺寸/两张显示配方留出/50次原生float公式通过；原scene/语义逆解与完整HDR目标/编码仍未通过，A阶段与acceptance_complete仍false。原33点mask及C01-C05、旧NumPy/half失败不改，不继续旧bit-exact拟合。完整EXR的125MB小归档许可待显式答复，当前100MB累计上限不重置；本地只保留证据和密文预览，未假称完整母版落地。源码将保存在research/vm-native-20261018，随后仅清理本阶段自建临时分支，master/原件/旧工作流不动。


S48–S52收尾完成：5条自建临时远端/本地分支在远端源码保留、PR及全部ref审查后清理；8项本阶段secret与2个draft/tag均不存在，5个自有run均终止。既有PR#1和其他研究任务未操作。原件/冻结7文件SHA与原始171claims/文档历史前缀保留；5个新增workflow的8次upload均retention1天。125MB单EXR许可仍待显式答复，当前100MB累计上限有效，未写完整EXR。A阶段和总验收false，goal active。


### HDR-S53–S54：相机记录量化与归一化审计

- research/vm-native-20261020-hdr-s53 / source `d54796021c2155bb329140e0e44f63287ac7e211` / [run39300758676](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39300758676) / artifact12211821267 (1176B), failure。26A434/image20261012.0260.1；参考源码24A446，非原生iOS执行。ZIP SHA `d1563d63c48a5f8c9c2183bb1b126f25be4d72988b76d048912d384767621db1`，manifest SHA `4ead090292745f5d255d6f8e28accb7dc558f170fd7eaebe09900f5d3cf75881`，所有成员验证，retention1。
- research/vm-native-20261020-hdr-s54 / source `e7b1edf81675fd4b1bda93f20b25a5dfa949ec9e` / [run39301402089](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39301402089) / artifact12211902213 (5196B), success。26A434/image20261012.0260.1；参考源码24A446，非原生iOS执行。ZIP SHA `ff3c502e3f150088cb87e4530cfd634b6211f09cf0ab843cd654d5b2be35662e`，manifest SHA `ec26338865f2b663f812982f0b1c0991a8eff9dbd500fb18e876085e461eded9`，所有成员验证，retention1。
S53失败于sNaN/qNaN合并预期，未记为成功；S54用checkpoint和原生ARM asm区分两路，131070个边界探针差0、12特殊例匹配。无照片/secret/release，原模型/mask/门槛未变。源码保留到研究keeper，完成引用核查后仅删除两条自建临时源分支。A与总验收false，目标active；125MB许可仍待答复。

S53–S54收尾完成：两个源commit已保存在推送的research/vm-native-20261018@98d8cd675f3bcc89c663728b4ebaccaf41115620；全部PR/远端ref核查后仅删除两条自建临时分支，本轮无secret/release。原master与旧208条claims/7个原件冻结SHA保持，自己的临时脚本校验归档后清理。保守累计写入上界96,843,500B（含500KB后续审计清理预留），仍受100MB总额约束，根剩余>4GB；125MB许可待答复，未写完整EXR。A与acceptance_complete继续false，目标active。详见transport-cleanup-s53-s54和integrity-review-s53-s54。


### S55–S59（2026-10-20，全部source已保存在keeper）

均xcode-27 / macOS26A434 / image20261012.0260.1，retention-days:1；全ZIP、manifest及所有成员SHA已验证并落地。运行分支为research/vm-native-20261020-hdr-sNN，已清理；原source commit仍可达。

|阶段|source commit|run / artifact|结论|
|---|---|---|---|
|S55|8444b7230277b3b41c9f5ab6a4d60753566e0a74|[39307765465](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39307765465) / 12214666602|失败：prepare2无statsPSO，0行；AIR0/1导出成功|
|S56|7b7b4725b26187e16ac0b8809a67d311e0ce681b|[39308719398](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39308719398) / 12214318554|失败：269组原生tail全部逐位一致，随后密钥解析失败；无真实图数值|
|S57|a32e06cd88e11e904cbb865a4c78c2eb82e428b9|[39310642611](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39310642611) / 12215755870|成功：修正传输，global7有效/5诊断；3 consumer生成stats为0|
|S58|f79823d63c260057a50e9d72dbadf0f4f873d902|[39311415530](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39311415530) / 12215329062|成功：六图各一个有序参考尺度；不是native全域证书|
|S59|1c2b41bbaea560241bb986e52477b8c342467add|[39312021801](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39312021801) / 12215314906|成功：768新原生控制，六组256桶；6144真实辅助码均唯一兼容|

完整ZIP字节/SHA和manifest SHA：repo/research/hdr-native/evidence/s59/archive-provenance.json。S59首次下载0字节失败，收据保留；只重试下载，没有重跑计算。实际执行source SHA不以最终文档commit替换。源码keeper在清理时为1c2b41bbaea560241bb986e52477b8c342467add；五分支/专用secret HDR_S55_INPUT_SESSION/draft417638134及tag均核实清理，PR1/其他任务/master保持。


### S60–S64：原host统计与捕获复用（26A434 / image20261012.0260.1）

- S60: branch `research/vm-native-20261020-hdr-s60` / source `c55b2f516b5652eef4250bf79b779381f9fc9769` / run 39320900991 / artifact 12220345855 / failure / ZIP 5007B SHA `f29a20659b0eb9a0a3e36b36a2bc225bfa5252d1e2f2bcc4fbef959fa675c01a` / manifest `013c0881aa287e92a12a931265cc465ba69b17aca07dd5d2a6fc0c42444dbbce`。
- S61: branch `research/vm-native-20261020-hdr-s61` / source `7a7d2f04e3c29b0d0a4ed306aad343ea1e25a995` / run 39322265009 / artifact 12220567156 / failure / ZIP 4182B SHA `bd4a9bed42b53a2a607ee1fc096eb45c200f5cb8da81884e03564236bdebb047` / manifest `9c76190222449bd1284ba4b362ba28d56efde9b8c73bdcfe28acabfc8a03712c`。
- S62: branch `research/vm-native-20261020-hdr-s62` / source `2496f73203dd3a9ccfde51f7a2062592cb90dbee` / run 39323282982 / artifact 12219998681 / failure / ZIP 11111B SHA `76e9285d18c74a0d63afcef54010c1212593d19de0c91be86bd7bb9463a74fc1` / manifest `8390ee7210a9cb1ab9b1e85ccd57a369dd86a21abeabd74aaa73fabccf217262`。
- S63: branch `research/vm-native-20261020-hdr-s63` / source `be2f2605c7a14ff0366adef87738c8c3122c0f3b` / run 39324317293 / artifact 12221727679 / success / ZIP 83390B SHA `77d121caf0eb5a095107fc412a215c6da5946ac0ab94b008a55575da7a4ae153` / manifest `529983ee50e96ea4bc56ec7aa5116b8dfaed5d117aba879dda2bb8fbc171f30e`。
- S64: branch `research/vm-native-20261020-hdr-s64` / source `857e664d412ec947f88211041f354629f55886fb` / run 39326316262 / artifact 12222715223 / success / ZIP 6376B SHA `80046a73b095e4ac0480be96566f67e7c5bac06d7ccbd4f48995bc10d26491be` / manifest `38a472b4f939d6704537365b15ff275bd722e1581e208dc1920fd4c365e5c8b6`。

S60输出keyring失败且私有失败原始数据未保存；S61照片前编译失败；S62首图populateStatic −12780/style nil；S63五图45 dispatch成功但文件map half门槛失败；S64只复用密文/无原生图像重算。全部artifact retention1天且ZIP逐成员已校验归档，S62/S63 GPG验证；不修改历史失败记录。源码保存在研究keeper后再核查PR/ref并清理本轮临时分支和HDR_S64_S63_SESSION；清理结果以最终receipt为准。A与总验收false。


S60–S64收尾：源码/指标先普通push至research/vm-native-20261018@689034a284bc9fa714667872d9473baf161ad523，再经全部PR/ref与run终态核查，删除本轮5条临时分支和HDR_S64_S63_SESSION；无release增删，原master/现有PR/8份原件冻结SHA不变。见evidence/s64/closure.json及本地transport-cleanup-s60-s64.json。累计100MB许可不重置；旧Git预算按未压缩对象上界记账，本轮以可核对的最终loose对象实存字节调账，原账/全部历史归档保留，未扩大许可。A与总验收仍false。


S68–S69（26A434/image20261012.0260.1，0照片/0图像dispatch）：
- run39338027870/artifact12228355105；source643d5119cfaace229f2cfdda0177a68fc1aee682；failure；ZIP SHA d201b6cacef83c5bbc7ba922f82fba84008e06f94d5e5c801630ecfa95109ce5
- run39338223690/artifact12227756202；source01d543703d57252f04f9f62cefbfa88b5975a8b7；failure；ZIP SHA 13d421b280eebe5970e1ecf1dcbd2662655768a6b89b66852d2d1763424de3ae
- run39339778014/artifact12227399531；source1792940f83b6fe3c9f54085d184db47615f170a0；success-diagnostics-ROI-failed；ZIP SHA 1d0fd2e653d1369e9cd34b10b6abedf8bbada488f918ed2a13208afaa85ccd4c
- run39341678257/artifact12228712359；source93c0b4adda0d86e02572d79a578c569854d42d52；success-CPU-ROI-0；ZIP SHA f8f458dd7842a06d8eff1c672498e324a460dfcd9973be08442c198eb89af236
所有ZIP/成员SHA已验，3份派生C程序从各commit精确重建。S68/S69自建临时分支在确认无PR/他用ref且源已保存后清理，无secret/release；master与他人PR保持。细节evidence/s68-s69/provenance.json。


S70–S71 (2026-10-20): no photos/secrets/releases, xcode-27 26A434/image20261012.0260.1, retention-days1.
- source 07f5943a3cd0168c04aaf097f46d181818b4b885, research/vm-native-20261020-hdr-s70, run39345177157, artifact12230252826, ZIP2487B SHA256 23972244a31f790ae3edaf0b8868e4ff14fab667f4f29f2014ed6cdc35bf241a, manifest SHA256 a3af60772237b9620c145fbf925350e50f79bd0ab24f7bc3c433c9ea2a20837c; all members verified. Known mask2 initialization failure retained.
- source 8cd1b82c44ddd681c4f936a04cf6ceccd6cd7696, research/vm-native-20261020-hdr-s71, run39346448714, artifact12231437053, ZIP6095B SHA256 0cf5bc0e6ffba46c7354e5bfccae3feb32bafd5772152888be2ede6e251114db, manifest SHA256 52fa016dd9535154804c918af3019c0efe4b5134779df9ddde997b282d1a694f; all members verified. 7 finite synthetic ROI/count cases,14336 cells max abs0; no full scene/inverse certificate.

S72 research/vm-native-20261020-hdr-s72/sourcea5ea4e2fa3be49ed87ab074c9e4a8b01c37a71d9, run39350205726, artifact12232168720, ZIP3657B SHA256 f8b4dba6e3fddc344ebeff071a8f480d9777aeea2134db8c444fdc04261dff98, manifest SHA256 64905d7e3b501da59b3c3aa4c33171acde3aecedc5936229dbb62a9c9bfcfc95; xcode-27 26A434/image20261012.0260.1,retention-days1, success CPU bindings only,0photos/0image dispatches; all members archived/verified. No secret/release used.

S70–S72收尾：源码/全部证据已普通push至研究分支@dea598522448a1224beb0693e43d63f2bf1eee2c；PR/release引用、run终态及归档逐项核对后，3条本轮临时分支已删除并复核远端缺席；未创建secret/release，master及原件/历史归档不动。见evidence/s72/closure-s70-s72.json。125MB累计上限下，S73前含1MB预留保守上界102019344B；全部旧门槛及A/acceptance=false保持。

S73 research/vm-native-20261020-hdr-s73, source4a349173547b96e9b0994c57c98192d774b6b474, run39353695210, artifact12234397335, ZIP5360B SHA256 f23f633a0b760d8cac37a7b4a746f5eec71d2e3b5583f7bdeaa828d3b01889b7, manifest SHA256 10f73c5dfbbd4e97048bf06cdefa4eca4f8c382d01e13f555cc875e7788b602e; xcode-27 26A434/image20261012.0260.1,retention-days1,54 finite original CPU ROI cases maxabs1.7763568394002505e-15, no photos/image dispatch; all archive members verified. No pixel/full-domain gate inferred.

S67 archive supplement2026-10-20: source4df92c6f1dcab7c6b57e5783d22438ee05bab609,run39335997594,artifact12226746912,26A434/image20261012.0260.1,ZIP210521B SHA b1b95a5df2ee252eec41153cdce6f88d521c36490fc5422bbacb734a208509f1;29 payload SHA verified,30 ZIP members including manifest; original selectionxz unchanged; native reruns0, no new branch/run/secret/release.

S73收尾：源码与全部证据已普通push至research/vm-native-20261018@1cca0fb4dca4168d0618ba62f753166b08f5812b。head/base PR为空、release为空、临时ref为原source且完整ZIP已校验后，仅删除本轮S73分支；DELETE成功并以公开REST matching-ref=[]复核。S70–S73四条本轮临时分支均已清，无临时secret/release创建，未改master、原件、历史归档或既有分支。核查自动审批超时后采用拆分只读查询完成；无待审批动作。见evidence/s73/closure.json。A与acceptance=false；下一步整数取整/实际CI buffer及未认证的C01–C05。


S74（26A434，源码07353ab0a6d16096a3883da960fa8613da91d243）：branch research/vm-native-20261020-hdr-s74，push run39368595307，artifact12240755401，原ZIP9973B/SHA 64af6fe10403d51a66950970f3f0b286c3194a05f9ef993c8743d758086289a4；image20261012.0260.1，54有限CPU控制/432int64完全一致/648CGRect max0、FPCR0。原JSON与recipe/source SHA见evidence/s74/run。只调用270次CPU几何函数，无照片/PSO dispatch；C01-C05/A/acceptance仍未通过。传输两次超时均先于写盘，最终curl同一run/attempt1成功并完整校验。复现（只读原归档，不重跑）：

```sh
cd ~/work/styles-gtm-ltm
scripts/local-python-scope.sh -I -B repo/research/hdr-native/validate_consumer_pixelrect_s74.py hdr-native-20261019/runs/39368595307/artifact-12240755401.zip
```

runner原生复现入口：W=<private-temp> 且先mkdir W/out后，`python3 research/hdr-native/run_hdr_s74.py`；依赖probe_consumer_pixelrect_s74.m、S73/S72/S66 helper，实际命令见workflow hdr-native-s74.yml。新重复原生run仅在新问题需要时派发；artifact retention-days:1，完整小ZIP已落地。许可累计125MB与根分区至少4GB继续有效。

S74临时资源清理：run39368595307已完成，完整原ZIP/10个payload与源码SHA已落地验证；源07353ab为远端研究主线祖先。清理前所有head/base PR引用为空，仅删除本轮research/vm-native-20261020-hdr-s74，随后精确ref查询为空；未创建临时secret/release，未改master或其他分支。组合清理命令自动审批超时且未启动，拆分只读预检/单独DELETE/只读复核后完成。证据evidence/s74/closure.json。A/acceptance仍false。


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


S81（2026-10-20）为用户授权的优先级调整，无新增 run/artifact/照片/预览。原 PSO 微小残差归因探针仅有本地准备基线，未创建 S81 workflow/源码/临时分支，按新指令暂缓。完整政策、原话和 S80 记录引用在 evidence/s81/scope-change.json 与 phase-summary.json；原实验 archives 全部保留。没有新增 errors.csv 测量行。


|阶段|分支/源commit|run / artifact|OS/image|结果|
|---|---|---|---|---|
|S82|预备源码3fbded3；控制修正17fcc3b|未运行|计划26A434|真实捕获传输待目的地明确批准；无secret/release/触发分支|
|S83|research/vm-native-20261020-hdr-s83 / 17fcc3bd029da1d252515660e70e8ffa30123e36|39399353600 / 12254506268|26A434 / 20261012.0260.1|合成结构检查通过；原ZIP2337B已验证；触发分支已清理|

S83 ZIP SHA3d180ba38ea787438fd6911ce5b6dab0bcdf1293570a137797606c5c28c6c356，manifest SHA9f10c46b49086375c18a9768197079e75c6f8b5610dd47a310a21bc5e48d6a88，5个成员和两份源码SHA全部对应原commit。原ZIP保存在hdr-native-20261019/runs/39399353600/；文本、freeze和closure见research/hdr-native/evidence/s83。retention-days1，已立即落地；无人物输入/secret/release。S82拒绝记录见evidence/s82，未发生明文或密文上传。未重跑旧原生精度实验。


S84 原型已提交：research/vm-native-20261020-hdr-s84，source45e02e86d1ced0c375b6c9ebed8cae3bc3681090，run39403808066。首次观测queued，实际OS/image与结果待原run完成后的artifact确认；workflow限定xcode-27/26A434、只读权限、retention1天。只用已有公开样张IMG2600，新的RGB测试增益非scene目标；无S82数据、secret或release。不能把排队/运行当通过，不重复派发。五个原容器的tmap/base/gain绑定及属性原字节SHA/offset见repo/research/hdr-native/evidence/s84/source-container-bindings.json。


|阶段|临时触发分支 / source|run|OS / image|归档与结果|
|---|---|---|---|---|
|S82|research/vm-native-20261020-hdr-s82 / 45e02e86d1ced0c375b6c9ebed8cae3bc3681090|39407894040 success|26A434 / 20261012.0260.1|12257579499 (270052B, SHA 622ed242cfcc9e0a45696bd4ed35a02ab8f5604b24763c3388aaea67de7f301c); 12257239736 (15425B, SHA 3955094e7a72baaf16f643167ee3f7e828ccc080d14c9d6f87d3a49cca345474)|
|S84|research/vm-native-20261020-hdr-s84 / 45e02e86d1ced0c375b6c9ebed8cae3bc3681090|39403808066 success|26A434 / 20261012.0260.1|12257525181 (15772B, SHA afac971ddd9156a8f4499c77c86286b7e6fd6165a68cca7249e83991f11e9735); 12257480250 (413188B, SHA d139f160e80ff938cc4f7bc20c2cc30f4177fd47600a94452bc434fef9557d8b)|
|S85|research/vm-native-20261020-hdr-s85 / 42dc055458bf9e5ddb8346ba80851c0751587f83|39408560663 success|26A434 / 20261012.0260.1|12258786314 (17694B, SHA ae9baf8afeb058d9c094e23e4dba0252de23cb3c355755cb93391b82aa1bcc9f); 12258456624 (411215B, SHA 4fe189474408a0943d704846cf83eaecaaa6e78e67c15e2c55a3f6273470a7b1)|
|S86|research/vm-native-20261020-hdr-s86 / f0ccf95cea77e3359eca78e2a2e9506c3c392eb7|39409968844 success|26A434 / 20261012.0260.1|12259445696 (13566B, SHA 86afef59b3d884d573349c15e2d5235284602a870fc021115b31c5d798c953ca); 12259245854 (90100B, SHA c795344500c684b3bea789c1c40d4e1cec01a03579b4b78e4ee2ef6559053700)|
|S87|research/vm-native-20261020-hdr-s87 / cc3a20ad2149b64f84793f56102eee9273389075|39411684190 failure|26A434 / 20261012.0260.1|12259413845 (45106B, SHA 5fc2a91d84ca682790e8e092bf127e6cab7bf8d7ba46300aea1b73b16f6a5f9b); 12259249040 (118227B, SHA 1e6763fd0e823d69ba8a55446b716240a81d9fa3a07f19108421ab32f9d44a1e)|

S82输入2份既存密文ZIP共110814893B，用户本轮明确允许公开prerelease+2条secret；验证结果后全部删除。S84旧坐标HDR指标不具资格，SDR max0独立有效；S85只修读回并确认matrix0偏差；S86选旧S32 matrix6/10bit；S87完成五图显式旋转/最大EV审计，但run失败于101900B>90000B汇总封装，runner public manifest缺失。其原ZIP通过API digest，33成员使用明确标为派生的本地清单核对；S82/S84/S85/S86使用原runner manifest。全部阶段源码SHA/私有GPG成员已核，retention1天后仍有本地原归档。所有相关临时ref已清理，master不动；证据见各evidence/{stage}/closure.json。旧S82待授权是历史状态，由本次记录更新。


S88：`research/vm-native-20261020-hdr-s88`，source`caae6869d2824884d36f27c475c4684744f0be37`，run[39428400454](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39428400454)，success，xcode-27/26A434/image20261012.0260.1。失效S42输入改为冻结AST重建，实际EXR SHA等于旧记录；真实独立HDR目标经matrix6/10bit封装和原生读回，单图完整SDR0，实际gain公式通过，目标p99EV0.00873855/max0.0269484，原目标阈值仍false。原ZIP、两密文GPG和所有SHA已本地归档，见evidence/s88/run/archive-receipt.json；临时分支经PR引用空和源码保留检查后清理，无secret/release。成品HEIC仅加密保留，不计五图/RAW/全尺寸语义通过。


S89：[39430695395](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39430695395)，sourceb03beb93cfd1b5093fd8bed314ff53a76842febf，research/vm-native-20261020-hdr-s89，26A434/image20261012.0260.1；5/5计算、2/2本配方留出、五图SDR0。run=failure，仅最终1554198B>1.5MB密文容量断言；原manifest及全部产物已校验归档，未重跑改状态。独立目标p99EV0.00873855–0.229329；最差需要亮度/显示域审查，原严格门槛保留false。六份GPG均验，未下载新完整载体/EXR，closure核对PR引用/保留源后只删临时分支，无secret/release。


S90：[39435568710](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39435568710)，source0a2a4fe66a63e564504926b30110a95820bb1133，research/vm-native-20261020-hdr-s90，26A434/image20261012.0260.1；run=failure，10bit完整诊断完成，12bit实际编码/SDR0但原生gain=nil退出5。h8完整ACES像素p99=1码，99.09154%≤1码，267像素>2码，最大8码；亮度分层保留所有非正数/极值。31汇总成员和1份GPG已验，原始ZIP已归档，临时分支按引用检查清理，无secret/release。未归档新完整载体/EXR，不能宣称12bit HDR有效或A/scene通过。


S91：[39474288686](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39474288686)，source c27610d0dd63ca70f6bca4acfe7f9c9068756df5，research/vm-native-20261021-semantic-s91，26A434/image20261012.0260.1。failure=生成ObjC guard的pixelFormat未指定MTLTexture类型；consumer/逆解未执行。原生2016×1512 matte/bitmap行标尺完成；两份原ZIP直接日本落盘，12 public成员、7源码、GPG/2 private成员均验。本次secret/release/tag/临时branch已按引用检查清理。


S92：[39477063576](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39477063576)，source13780b9b6bca8bf5a5ac6dcb846696664055f6bc，research/vm-native-20261021-semantic-s92，26A434/image20261012.0260.1，success。两个原尺寸ROI控制完成、目标外参数差0/纹理SHA不变/18次预览SHA不变。半强度联合p99约0.001495/0.001434EV；完整consumer仍82905/75984失败，旧门槛未过。原ZIP日本落盘，19 public及GPG/143 private成员已验，派生源码绑定已验；本次secret/release/tag/branch已清理。
