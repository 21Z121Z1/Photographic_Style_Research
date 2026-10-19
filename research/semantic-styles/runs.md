<!-- SEMANTIC-20261018 -->

## 人物/皮肤语义阶段（2026-10-19更新）

持久研究分支research/vm-native-20261018；未动master、不开PR。所有照片/可重建像素仅密文传输，输出公钥指纹28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA。一次一个run，artifact retention1天，均已立即归档。

|run|commit|artifact|结果|归档|
|---|---|---|---|---|
|39133038484|4ec4907|12138727142,62786B|S1无照片预检：Studio默认order与硬件tuning|已归档；ZIP9f7723a98638305ce140b648078ca094f16386bc2c3eca2be5a25dad2098b69f|
|39134556722|73114a82|12139397306,31481607B|j三值×两native路径零像素差；personData0；texture错误NSValue extent中止|已归档全部76文件SHA0失败；ZIPc3f3864eda35a548bf65b6c3f682aeb646869abad23d756a56cf281abbb9a74d|
|39135405637|08b5ee9e|12139274094,10766B|Texture辅助接口查询SIGABRT；61相关AIR模块，无现成LLVM库|已归档13文件SHA0失败；ZIP300313a00b470cf1c6258114f712d1a424f03f2e253682a1bac6e11478b06698|
|[39135794320](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39135794320)|a07f75784931b2c69045dfd44b990680cbd26b4a|12139921306, 6833538B|S4 3个texture效果身份路径；61/61 AIR文本导出|GPG0、177文件SHA0失败；ZIP `d45c70bb33f7bd9c6d8f4ef266f05ae246f00ca413c58d1c5a5983df2c9563d2`|
|[39139035394](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39139035394)|1fc5b6e501efa68e7be7480b92791b9aecccd044|12140624073, 75645295B|S5 隔离theta9/10非零；完整逆未过；人脸/人身metrics与RGB-NPZ因显示alias作废|GPG0、234文件SHA0失败；ZIP `55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc`|
|[39140025554](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39140025554)|4f7435d0c01645a8c4dbdf9f4aae868a30b5f110|12140853109, 604938B|S6 副本重算20个输入SHA不变；64个iOS指令控制0差；UEB只在链接时失败|GPG0、23文件SHA0失败；ZIP `07255af3ed54395840ab906245204a17cbc595cf90ddaff30489f9cd7a5662d9`|
|[39155124218](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39155124218)|76b83524f405eff24b267c0f9194bc47af2cbefd|12146312541, 6290584B|S7 残差法联合613失败；UnderEye条件原生往返max9.5877e-4|GPG0、32文件SHA0失败；ZIP `b2507b583484b367fa551962aa5cc5e0d958b02e0790eeef26d9eb143df5ed2c`|
|[39156000731](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39156000731)|346634b1aae9c36939f52f3543d9dc665fd3162e|12146693880, 35169598B|S8 同上下文0差；皮肤逆91/205/296失败；量化非唯一见证|GPG0、76文件SHA0失败；ZIP `b48ae649e8c491474f8a34a3927b5d354e4920ead46c783794c8aaab8c8c4746`|
|[39156641912](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39156641912)|5a8d093e303541340c3f932430f1ac32c38121e9|12147325821, 21010B|S9 保存数组边缘/阈值审核；联合歧义并集87，失败交集28|GPG0、12文件SHA0失败；ZIP `bbcc782d41a189d081987e1ffdba01d6f09b297f87726437f22ba986250e1237`|

S4–S9每次均为macOS27.0.1/26A434，runner image xcode-27-arm64 20261012.0260.1，Provisioner20261006.597；逐job日志API、branch、cipher/manifest SHA见run-provenance-20261019.json及各archive-audit.json。S4首次下载许可已解决，原先“等待许可”现状作废。S4/S5/S6为历史运行，本轮只下载/审计或续做，不重复原实验。

- S4 branch `research/vm-native-20261018-private-s2`，cipher `a7a8cacf569393719fd51caeb8f777e82aed6c6fc3714ad298851b5053e14a16`，manifest `fbed985abbc7dfefb2974eec82bde8bbb7a0a243e18b2a81c88a0e252c870184`。
- S5 branch `research/vm-native-20261018-private-s5`，cipher `33973c5893518ef15fd7f930b95a3a61f28966e1653593a65161bd2b09790ba7`，manifest `f827fcf0e4e4f07f3280273e6ba892c4803f7d85ddc72a5e63d02bc573001828`。
- S6 branch `research/vm-native-20261018-private-s6`，cipher `c9b3ea58aa166edc380345d7150f2d98627927d373b1cf4eb20d03a3ad8c8d65`，manifest `304e7d173abfcfde4040f81cbf93acd66d3d885439cbf01bad4cc55ff0a57ef4`。
- S7 branch `research/vm-native-20261019-private-s7`，cipher `9b537910d9600f7c03ee5601b99320c2d51769537768b98b9923a202f93a45fd`，manifest `6633b713263d37e4f97d40bfb02dfd6a41845a5ba6d913445238c5f5e3c9b936`。
- S8 branch `research/vm-native-20261019-private-s8`，cipher `51a9e2d89440ec7811d3b88cc397c0cb239d02125dfba0a6f4f3ce8830930e7f`，manifest `037c9bbd70a213692a0454a4175c4251819ebd59d81d1dec71dd6c4d6b24117c`。
- S9 branch `research/vm-native-20261019-private-s9`，cipher `0a17d1cc3e5fe180ac707a1b5866293ceee94e180d2632e3fe4b4e074ee12d98`，manifest `f56c2a77825653fb99b359e96f16ed014188affaf9a4d3a365294f99a17e8428`。

S5原始archive保持不动；显示alias污染结果用S6替代。S7存储float残差阈值6点差异详见S9审计，91/205/296新参数中和失败不受该记账差异影响。临时S5/S6遗留和本轮S7/S8/S9 secret/release/tag/branch已按transport-cleanup-20261019.json及private/s5-transport/cleanup-20261019.json清理并远端复核。仅持久研究分支保留源码。

<!-- SEMANTIC-TEXTURE-S10-S13 -->

## 后续纹理单位 S10–S13

|run/phase|commit|artifact|结论|ZIP SHA|
|---|---|---|---|---|
|[39157857745](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39157857745) / S10|edefae3ae228a861321ce8284c72646a8bcd02e9|12146704857, 277121B|failure；SkinSmooth未分配imageblock输出全零；Mattify编译失败，分析空mask异常|`2789f9b97351dcc7270f26cf54a3610b14649489f4382b31eeae56aae16c3432`|
|[39158119190](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39158119190) / S11|994e44b7a9a4f20a8b468c9c26ddb693bcd7173f|12147383684, 1393763B|SkinSmooth非零控制/条件往返2配置通过；Mattify pipeline仍失败|`af869e5bd7f3870526ddcff50ef03edce7bed804570c803a6072b2cce2425d3f`|
|[39158417428](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39158417428) / S12|ba7f90a5f751aa6343149e173dd4f399a2761c1f|12147947104, 5271B|无照片编译矩阵8组：imageblock true4/4成功，false4/4失败|`298bdfc4f825681a3e9eb15946befd1c70cf6fee27e8d1be84865f4d218a1af0`|
|[39158599009](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39158599009) / S13|4aaed774e0b1f09127e47fe6944f4bf201221546|12147748302, 1414247B|只跑Mattify，两个非零配置原生往返恰1e-3通过；非camera undo|`d2bdc995d6f6adbf2df7761456f90d89d6c4d2014c8f26f82668894fa9649bf9`|

每次镜像xcode-27-arm64 20261012.0260.1 /Provisioner20261006.597，实际26A434，retention1天。branch/job日志API/cipher/manifest SHA见texture-run-provenance-20261019.json。S12公开文本无原生manifest，单独记录CRC和entry SHA；其余GPG/manifest SHA0失败。追加临时资源均按transport-cleanup-texture-20261019.json清理，源码保留持久研究分支。


<!-- SEMANTIC-S14-S18-20261019 -->

### S14–S18 原始运行、归档与清理

|phase / run|source commit|临时分支后缀 / artifact / bytes|实际执行和结论|ZIP SHA256|
|---|---|---|---|---|
|S14 / [39161360493](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39161360493)|`737ea70710cd001798503c710f27039db67bfeec`|`20261019-private-s14` / 12148797876 / 10768|Native compile failed; no valid new pixel result, regardless of green workflow|`3a8f06a15b936f8646a89e079264d18a8addd1dca2d8804fd7bdcb463a056351`|
|S15 / [39161546771](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39161546771)|`bdb9a16156a9e6deb9a7c0bfaa5f09438cb646bf`|`20261019-private-s15` / 12149132073 / 19946398|Original native PSO finite local-set enumeration; not global hull or acceptance|`62220cce6b4c7aeddf3d0e5eee4152056d0af8438f28936dc2792f068242a20e`|
|S16 / [39162035138](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39162035138)|`9e172f6555695ea3938738fc694ebc67cd5be578`|`20261019-private-s16` / 12148908479 / 12693355|Original native PSO expanded finite local-set enumeration; not global hull or acceptance|`fcf71036c8d9c3d00cefd417c6a98d9e2ae0525c2c6e26a0fc79c2e08f944ab1`|
|S17 / [39162555357](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39162555357)|`fa9ddf6ae9c7dda5622dae3dd2ed51d148b8e4a4`|`20261019-private-s17` / 12149258316 / 41500|Saved-array audit only; no new native execution/search|`ce03b63fa5d35757f228d95d71fd6b13e8592d0d472eb9add70f9389df002c47`|
|S18 / [39177763111](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39177763111)|`bdfa47739f285e8fbf7a26692179fc20b166e154`|`20261019-private-s18` / 12155061915 / 10768|Native Float16 format enumeration plus synthetic Unicorn ARM block replay; not native iOS pixels|`1d6985fb15d3a4076d173def3383d7feb48d11f89a7599ddad2f7124f63f7b95`|

全部临时分支全名以 `research/vm-native-` 开头。macOS27.0.1(26A434)、xcode-27-arm6420261012.0260.1、Provisioner20261006.597、retention1天。S18 ARM代码来源24A446，与样张固件/硬件不一致；Unicorn不是iOS原生。S14 workflow success不等于probe成功，S17不调用新native。各cipher/manifest/job-log SHA及逐项执行范围见 `skin-bounds-run-provenance-20261019.json`；原始本地 `skin-interval-run-provenance-20261019.json` 与 `bounds-run-provenance-s18-20261019.json` 不覆盖。

S15联合46失败，S16/S17联合33失败/PSNR99.97383dB；6/27/33各残余都有非唯一性见证，原门槛仍未通过。S18没有新pixel solver，仅格式外包络和90组合成ARM循环重放。所有ZIP/GPG/manifest完整，公开证据仅文本/聚合数字，人物图/matte/逐点RGB留密文和本地。

S14–17 preflight确认PR全状态0、其他advertised ref0、源码可达持久分支；5个旧secret、release416667456及4分支清理。release已删除而tag本来不存在导致初次CLI退出1；API确认404/空refs后恢复清理，不复删归档。S18的单archive secret与第5条private分支也已清理，无新增release/原件上传。准确结果见两份transport-cleanup与preflight JSON；本轮原始archive文件未删除/替换。

- S14：cipher `c6e59389698b0770c0aca4c9fd7266cd2076606f9e945d5ccf5e43c2891b2511`；manifest `c48f88d983cb2f8a79c4c00a82c35ad1ceec91acb3937ddd1a95fc86b6e78ef1`；14文件/9004B完整流式验证。
- S15：cipher `28f19411932046a89b7b7cb0b4472349c5d6633ec6fbc732352fa8995ec02f64`；manifest `356911d529d401dcf8e78c782b070e7d40a36fb63e9882693a07173d80f10dc6`；54文件/80799467B完整流式验证。
- S16：cipher `054329e24b9ba811c8d543db59762eb24be1ea3c0f6324abc2e560f0de8025e2`；manifest `54b6affe6ab73b19961082d1507495522bf824f5708037710e33c0c797498f11`；51文件/16664434B完整流式验证。
- S17：cipher `ade750958abca1ad9f2db4c23e091aadebc479c703d915ee18649d947f999e26`；manifest `5c2b5ed208673214330f821e7abb597c164bc2ba03aa97ecf6f9a81f862b82b5`；16文件/619210B完整流式验证。
- S18：cipher `449b6e1d6a4e84c33524c9cd441da50e7a0f317e16a877bda4279bef3e70e247`；manifest `de36035de24791b4b9edbbc3f555c19d2d0dde16e347e13e7700899edbd8c3f6`；12文件/62457B完整流式验证。


<!-- SEMANTIC-S19-S20-20261019 -->

### S19–S20

|phase/run|branch / commit|artifact|实际执行|结论|
|---|---|---|---|---|
|S19 / [39183348891](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39183348891)|research/vm-native-20261019-s19 / a5c6f65a682b4130c4e489d01099a1922765edb1|12157286597，38046B|原consumer合成域72配置；allocateTone+3helper原ARM重放36组|全部正常内部控制有限，灰阶大范围有限输入有808异常/配置；24组曲线非零。无照片/secret/release。|
|S20 / [39184820567](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39184820567)|research/vm-native-20261019-private-s20 / 100ad285a571634c62e5d15b7e2c5c5617f5a609|12157941077，18778529B|原512×384 retained PSO整幅见证；精确有理数审计；条件曲线逆|整幅同Y/异F0，70/70证书；非零tone j控制0差；23148条件曲线观测区间0漏包。原A/点门槛仍false。|

两次均26A434，xcode-27-arm64镜像20261012.0260.1，Provisioner20261006.597，retention-days1。S19是公开合成文本，未伪称GPG；S20全密文，55文件28401260B验证、仅89708B小型证据展开。精确branch/commit/ZIP/cipher/manifest/log SHA见s19-run-provenance、s20-run-provenance和cleanup-s20。S19分支已清理；S20三个secret、release416811688及private分支已清理。草稿release按tag读取404后经认证list定位到原有唯一草稿，没有重复创建或上传。

- S19 ZIP：`db5a00222bf017798bf45cf064b854ad1655f5f0ce2103d37763f8c92a3c8dc5`。
- S20 ZIP：`d7bd0a79aad12a7a17899df87a9ffc86690811cfe2e12fbcac4472eba87805d7`；cipher：`5ad6308e5c01456fa24481211d49ab64eb9025c79f99ab7ca466c384ddafde5a`；manifest：`a011597ccc7ea1db05f72c0f4c562dfc441b346c4e2fe33e625c21c75fa38602`。

原生iOS未执行；S19外部powf与PAC/stack hooks有清单。S20“完整”只指整个已捕获512×384 dispatch，不是原件24MP。所有源码已保留research/vm-native-20261018，master/PR未动。
