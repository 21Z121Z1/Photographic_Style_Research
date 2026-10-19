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
