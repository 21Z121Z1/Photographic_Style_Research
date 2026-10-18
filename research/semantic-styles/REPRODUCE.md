<!-- SEMANTIC-20261018 -->

## 人物语义阶段复现入口（2026-10-19，不默认重跑完成项）

本节资源要求覆盖前文历史命令：VM任何Python必须用`./scripts/local-python-scope.sh`，MemoryHigh300M/Max400M；图像计算、完整逆解、AIR导出全部在macOS runner。不要本地执行旧separate.py/emulate_ios_ccm_v2.py。本轮100MB写入许可、保持剩余>=4GB，下载>1GB先问；不再沿用此前未经本轮许可的92%暂停条件。原件、旧归档不覆盖。

```bash
cd ~/work/styles-gtm-ltm
git -C repo status --short --branch
df -B1 .
# 小型文本/manifest审核，同一scope中执行；不解码照片。
./scripts/local-python-scope.sh semantic-20261018/scripts/audit_semantic_evidence.py
```

新源码在repo/research/semantic-styles。S5=1fc5b6e、S6=4f7435d、S7=76b8352、S8=346634b、S9=5a8d093；原生运行、artifact及ZIP/manifestSHA均见runs.md。源脚本保持历史失败可复现，不将已归档版本自动替换。semantic_skin_model.py是独立连续模型，semantic_exposure.py是显式预算候选，studio_under_eye.py是已知E/w条件逆；均不接入/替换冻结consumer/scene模型。

原有secret/release/私密分支使用后已删除，不能直接dispatch已清理的workflow。若另获安排做新试验：新建research/vm-native-<date>-private-*分支、随机临时输入口令（仅文件/stdin送gh secret），GPG加密原件/所需捕获再传临时draft release。对旧archive可只在本地私钥解出该单个archive的session key，以临时secret送runner；绝不上传私钥。首次workflow以仅限定新分支的push触发；xcode-27，先核对build26A434及Metal。人工上下文与原相机统计分开标注。参数中和之外所有上下文要SHA相同。

runner入口示例（只能在上述私密传输上下文准备完成后）：

```bash
# GitHub macOS runner；W为其临时目录，不是VM。
python3 research/semantic-styles/run_semantic_s8.py  # 已完成，勿默认重跑
python3 research/semantic-styles/run_semantic_s9.py  # 保存数组诊断，无新逆解搜索
```

输出全部tar→GPG加密到archive-public.asc，指纹28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA；upload-artifact@v4 retention-days1。人物图、mattes、像素NPZ及完整ImageIO元数据不得明文artifact/git/log。workflow success另需检查status、原生inferior退出码、pixel结果/manifest。失败先读log-failed再改，禁止盲重试。

归档使用新的目录：先API查询size/空间，再流式下载密文ZIP；本地bounded archive工具仅GPG流→tar逐文件hash，原始f16/f32缓冲不展开。只在新的归档目录执行`archive_semantic_bounded.py <run-id> --materialize-limit <bytes>`，已有decrypt.log/archive-audit存在就拒绝。保留原包、记录cipher与manifest SHA，并核对manifest所有文件。完成后删除本次临时secret/release/tag/branch、复核API不在，再删除自己生成的本次口令文件。不能删除其他分支、历史输出或旧归档。

固定显示：OCIO2.6 cg-config-v2.2.0_aces-v1.3_ocio-v2.4，Linear P3-D65→sRGB-Display /ACES1.0 SDR Video，0EV；np.array(copy=True)后才调用OCIO，每次前后输入SHA必须相同。S5污染的人脸/人身metrics/NPZ作废，数值引用S6，皮肤新估计引用S8/S9。PREVIEWS.md只留本地；公开分支无人物预览。

<!-- SEMANTIC-TEXTURE-S10-S13 -->

S10–S13扩展入口：texture_units_s10.m / run_semantic_s10.py；S11 commit994e44b为SkinSmooth正确imageblock分配，S13 commit4aaed77为Mattify UseImageBlocks=true、thumbnail=false并设置SEMANTIC_UNIT_ONLY=Mattify跳过已完成SkinSmooth。S12 mattify_compile_s12.m只编译不处理照片。两个私密run仍使用单archive session临时secret，已清理；不可直接再次dispatch。图像数值仅runner，结果audit仍用本地scope。原生往返与原输入误差分开，不把0有效mask计成功。
