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
