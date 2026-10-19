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
