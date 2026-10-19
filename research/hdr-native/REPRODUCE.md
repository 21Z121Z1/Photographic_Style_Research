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
