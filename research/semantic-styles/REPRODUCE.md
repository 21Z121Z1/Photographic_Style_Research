
## 人物语义阶段复现入口（不自动重跑已完成项）

本地Python均包 `./scripts/local-python-scope.sh`。ROOT目录为~/work/styles-gtm-ltm。

1. 小型元数据读取：`./scripts/local-python-scope.sh semantic-20261018/scripts/semantic_inventory_local.py`。
2. 既有密文归档审计：`./scripts/local-python-scope.sh semantic-20261018/scripts/archive_semantic_private.py 39134556722`，只展开小文件；需本地private/gnupg私钥。
3. 静态切片与selector注释：`./scripts/local-python-scope.sh semantic-20261018/scripts/semantic_static_slice.py`；仅文本、无图像解码。
4. macOS原生脚本：repo/research/semantic-styles/run_semantic_s1.py（已完成无照片预检），run_semantic_s2.py（真实照片、仅runner）。SEMANTIC_PHASE=texture-fix会跳过已完成j对照。semantic_texture_s2.m在固定上下文运行单位算子和残差迭代，不保证相机真值。
5. 已清理的私密工作流不能直接再次dispatch：原asset/secret/临时分支均不存在。重跑必须新建临时随机口令（只用文件/stdin传入gh secret set），GPG AES256加密只读原件，建临时draft release仅上传.gpg；把新asset ID及cipher SHA写入专用临时分支workflow，push触发。输出使用archive-public.asc对应本地私钥加密，上传retention-days1；完成立即下载、校验每文件SHA和GPG完整性，清理临时secret/release/tag/branch。不得把私钥、口令或明文人像放进git或log。磁盘越过92%或下载>1GB先获得许可。
6. 新连续皮肤候选semantic_skin_model.py限制单块<=65536像素，仅待验证草案，不接入冻结forward/inverse/scene。native/macOS重放负责重型计算。RAW验证继续待配对组。
