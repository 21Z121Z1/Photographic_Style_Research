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


<!-- SEMANTIC-S14-S18-20261019 -->

### S14–S18 复现与只读审计

本地仅文本/哈希；所有旧归档保持原样，已存在的open('x')证据不覆盖：

```bash
cd ~/work/styles-gtm-ltm
./scripts/local-python-scope.sh -I semantic-20261018/scripts/audit_semantic_evidence.py
sha256sum semantic-20261018/static/producer-j-{bound-s14.md,flow-s14.txt,downstream-s18.json,downstream-s18.txt}
git -C repo log -3 --oneline research/vm-native-20261018
```

S15代码沿用S14名字，正确编译修复在bdb9a16；S14/737ea70的失败归档不能算有效像素。S16/9e172f6只扩大47点的独立集合，S17/fa9ddf6是保存数组审计，S18/bdfa477为格式/短块重放。完整source commit/run/artifact/cipher/manifest SHA见runs和provenance，不靠已删除的临时ref取源。

下面只在macOS runner已解密到全新临时副本后执行；S5/S15/S16/S17变量均指相应归档根目录，W为新临时工作目录。不要在892MB VM运行，也不默认重复已完成实验。

```bash
# GitHub xcode-27 / macOS26A434；S17依赖numpy、Pillow。
mkdir -p "$W/out"
# 仅复现保存数组审计。
python3 research/semantic-styles/audit_semantic_s17.py \
  "$S5/out/consumer-toneP035/semantic" "$S15/out" "$S16/out" "$W/out/diagnostics"
# S18 runner环境：numpy + unicorn==2.1.4，clang使用当前SDK。
clang -O2 -fobjc-arc research/semantic-styles/probe_s18.m \
  -framework Foundation -framework Metal -o "$W/probe_s18"
"$W/probe_s18" > "$W/out/native-format.json"
python3 research/semantic-styles/audit_semantic_s18.py "$S17/out" "$W/out/analysis"
```

S15/S16完整native重放入口为run_semantic_s14.py / run_semantic_s16.py，域与诊断/估计种子分离由semantic_s14.inc固定，不能拿原输入选根。每点packed控制的ROI映射不同于full frame，必须保留basis/四pipeline对照及恢复ROI步骤。S18只读取不可变S17，预览沿用S15/S16已校验结果，不再改像素。

旧临时secret/release/5条分支已清理，不能直接dispatch原workflow期待旧输入有效。需要复现时新建限定push的研究临时分支，轮换单archive session secret、只传GPG密文，核对assetID和源归档SHA，结果retention-days1。终态立即下载到新目录，GPG+全manifest验证后查PR/ref/源码可达性再清理临时资源。归档审计已存在则只读，不覆盖open('x')历史文件。公开聚合provenance不用历史native_precision_valid字段作验收；execution_scope明确S17仅数组审计、S18非iOS原生，acceptance_pass=false。


<!-- SEMANTIC-S19-S20-20261019 -->

### S19–S20 复现入口与信息界

```bash
# 本地仅小型只读审计；任何Python都在该scope内。
cd ~/work/styles-gtm-ltm
./scripts/local-python-scope.sh -I semantic-20261018/scripts/audit_semantic_evidence.py
```

以下只在xcode-27 runner、全新临时目录执行；不默认重跑完成项：

```bash
python3 research/semantic-styles/producer_allocate_s19.py "$W/out/allocation"
clang -O2 -fobjc-arc research/semantic-styles/domain_native_s19.m \
  -framework Foundation -framework Metal -o "$W/domain-s19"
"$W/domain-s19" research/semantic-styles/evidence/scalar-context-s19.json "$W/out/native-domain"
python3 research/semantic-styles/test_semantic_curve_inverse_s20.py "$W/out/curve"
```

S19输入完全合成，无需人物文件；脚本记录外部hooks，不称原生iOS。S20真实整幅证书入口run_semantic_s20.py→semantic_s20.inc→analyze_semantic_s20.py；依赖同一S5/S17不可变归档和原件副本，只改变target参数/指定输入替代。原始传输secret/release已删，不能直接dispatch历史workflow。若复现，创建新限定push的研究分支和新workflow，轮换单archive session secret；原件AES256密文临时release或已授权加密输入，输出GPG到既有公钥。禁止上传私钥/人物明文。先核对build26A434；终态立即下载到新目录，GPG+全manifest校验后查PR/ref/源码可达性再清理。run原分支source commit在runs.md；S19仅注释纠正不改变数值代码。

semantic_curve_inverse.py只收实际已知的单调标量curve pair与knots，返回输入/中和输出区间、plateau、endpoint、近黑与保证mask；完整含混点以NaN候选+区间交付。研究用minimax_estimate不是认证像素。2^-22只对应本次归一化二进制knots的原ARM插值误差合同，不能随意套到完整half消费端/相机空间。实际相机曲线未知时拒绝用S19合成曲线替换。GTM/LTM/人物语义分开，Apple Log与冻结模型不改。


<!-- SEMANTIC-S21-20261019 -->

### S21 复现（文本审查与无照片native探针）

本轮结果已完成，下列命令用于复核，不默认重复运行。规范最小事实见msl-spec-check-s21.json；URL内容若变化，脚本按预期SHA拒绝自动采用新版本。

```bash
cd ~/work/styles-gtm-ltm
# 新建临时目录；14,564,497B官方PDF，加小型pypdf包，无人物数据。
styles_s21_tmp=$(mktemp -d /tmp/styles-s21-reproduce.XXXXXX)
systemd-run --user --scope -p MemoryHigh=300M -p MemoryMax=400M \
  uv pip install --target "$styles_s21_tmp/parser" --no-cache pypdf==6.21.1
curl --fail --location --max-filesize 15000000 \
  https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf \
  -o "$styles_s21_tmp/spec.pdf"
./scripts/local-python-scope.sh -I repo/research/semantic-styles/read_msl_contract_s21.py \
  "$styles_s21_tmp/spec.pdf" "$styles_s21_tmp/spec-facts.json" \
  --parser-dir "$styles_s21_tmp/parser"
./scripts/local-python-scope.sh -I repo/research/semantic-styles/audit_consumer_contract_s21.py \
  repo/research/vm-native/model-v10/0010.ll "$styles_s21_tmp/spec-facts.json" \
  semantic-20261018/runs/39202621951/text/capabilities.json "$styles_s21_tmp/contract-audit.json"
```

审计输出REFUSED_MISSING_CONTRACT_AND_COVERAGE是当前正确结果。它不是interval solver，不能因脚本退出0就称global认证通过。full-domain/全consumer门槛独立保留false。

native部分只在xcode-27/26A434 runner的新输出目录执行：

```bash
clang -O2 -fobjc-arc research/semantic-styles/semantic_contract_s21.m \
  -framework Foundation -framework Metal -o "$RUNNER_TEMP/semantic-contract-s21"
"$RUNNER_TEMP/semantic-contract-s21" "$RUNNER_TEMP/s21-new-output"
```

历史临时分支已删除，源码在持久研究分支。若重新排队，使用新研究分支/新限定push workflow，一次一个run，upload-artifact保留1天并立即下载校验。此probe没有照片/secret/release需求；不需要解密旧人物档。完整consumer区间若后续实现，必须保留原PSO和固定上下文，不以safe重编译、helper逐值对照或局部查询替代原生全域证书。


<!-- SEMANTIC-S22-S26-20261019 -->

### S22–S26 复现入口（默认只审计已有文本）

本地仅低内存文本/JSON/流式哈希，所有Python包scope；大图/原生一律runner。现有归档不覆盖，输出选新目录：

```bash
cd ~/work/styles-gtm-ltm
./scripts/local-python-scope.sh -I repo/research/semantic-styles/audit_original_pso_s24.py   "$PWD" 39217875904 "$PWD/semantic-20261018/replay-s24-new"
./scripts/local-python-scope.sh -I repo/research/semantic-styles/audit_pso_evidence_s26.py "$PWD"
```

第一条期望输出certified_tight_points=0、uncertified_points=33、A=false；它是前提审计，不是全域solver。指向S24是因为该run包含全部8个声明控制及捕获解析；S26实际variant/UUID附加证据在s22-s26。第二条合并审计会调用未改动的原只读审计，不必再单独重复运行原脚本。脚本成功不代表1e-3逆解通过。

如必须重新执行原生：新建research/vm-native-<date>-private-sNN分支，复制本轮相应workflow并把push过滤改为该新分支，retention-days=1，一次一个run。`run_semantic_s22.py`记录原创建；S24补capture、samplers、原对象反汇编；S25补非capture原构造；S26限长读取_inputInfo和primitive/UUID。它们会调用原FrozenFilterMain路径，未开启SEMANTIC_RUN_INVERSE，不用于选根。

输入需重新在本地把原IMG_2810加密，创建临时secret和草稿release，更新workflow中的asset ID与cipher SHA；旧release/secret已删除，不能直接拿旧ID派发。archive output公钥仍为28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA，私钥绝不上runner。S5 ZIP应保持SHA55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc；如果artifact12140624073已过期，使用本地runs/39139035394/artifact.zip中的同一密文ZIP上传为新的临时release asset，仅把driver的download URI改为该asset并保留ZIP SHA检查，临时session secret从本地GPG流式取得。不要上传展开的S5/person原图或整份Apple程序二进制。

每次完成立刻下载到新的runs/<id>/artifact.zip，并用已有`semantic-20261018/scripts/archive_semantic_bounded.py <id> --materialize-limit 12000000`（外层scope）流式检查GPG/manifest。所有结果包括失败都不可覆盖。workflow的W/out只允许文本后再GPG；capture/程序blob必须留W/backend并由always清理。对新private分支检查PR head/base全状态、其他refs、源码已达持久研究分支后，删除新secret/release/分支。本轮准备/归档/清理实际脚本另存在s22-s26/finalization-scripts供审阅。


<!-- SEMANTIC-S27-S28-20261019 -->

### S27–S28 曲线/局部tone复现

本地只做轻量精确标量及只读证据审计；输出必须选不存在目录。原生/照片数值一律runner：

```bash
cd ~/work/styles-gtm-ltm
./scripts/local-python-scope.sh -I repo/research/semantic-styles/test_spatial_curve_retarget_s27.py "$PWD/semantic-20261018/scalar-replay-new"
./scripts/local-python-scope.sh -I repo/research/semantic-styles/audit_tone_s27_s28.py "$PWD"
```

标量检查期望11组通过，包含“先合成再反解”反例与plateau。审计通过只表示证据一致，原A/acceptance仍false。原先S26审计是该时点快照，有固定claims行数；新审计验证本轮增量及旧claims/文件前缀，不重复旧图像计算。

仅在确有新实验时重跑：使用新research/vm-native-<date>-private-sNN和新的workflow push过滤，不碰旧分支/workflow、不force-push，artifact retention-days1。S27入口`run_tone_s27.py`/`tone_retarget_s27.inc`，只改allowed params字段；它调用旧FrozenFilterMain保持Apple Log。S28入口`validate_tone_s28.py`，只读取S27密文副本，不重新抓native。脚本内run/artifact ID和SHA均是当次来源，不能不更新就复用已清理资源。

S27照片输入须用新AES256密文、新临时secret/草稿release，更新asset ID/cipher SHA。S5原ZIP SHA55f845778415b22276bc92e166416e60a29df6ce559df8f3fd71f6f5911d12fc；S27 ZIP SHA92dc95ce0a1193c72a55f149d8dd4bda3dd9c1ce202cfb32bc7ae83b209fedaf。若artifact已过期，从本地不可变artifact.zip上传**同一密文ZIP**到新临时asset，改下载URI但保留ZIP SHA。session-key仅由本地GPG流式导出并经stdin设新secret，不写argv/log、不传输出私钥。S27 out中只放批准的像素/预览和文本再整体GPG；完整Apple二进制/capture不准加入。

runner数值命令在授权W/临时输入准备后运行：`python3 research/semantic-styles/run_tone_s27.py`；S28须W和S27_ARCHIVE_SESSION，`python3 research/semantic-styles/validate_tone_s28.py`。单独科学图（无人物像素）可在runner运行`python3 research/semantic-styles/plot_brightening_s27.py "$W/figure-new"`，使用已经提交的S19合成allocator曲线，不重跑ARM实验。

下载到新的runs/<id>/artifact.zip后，外层scope运行`semantic-20261018/scripts/archive_semantic_bounded.py <id> --materialize-limit 18000000`验证GPG/SHA/manifest。run完成、归档通过、源commit保留到持久研究分支，核对PR head/base全状态和全部refs后删新secret/release/private分支。完整本轮实际准备、断点续跑、归档、清理脚本保存在本地semantic-20261018/s27/finalization-scripts，旧原件/归档不覆盖。真人ACES预览本地索引见s27/PREVIEWS.md，不在公开仓库放图。
