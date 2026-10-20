# 研究归档的传输规则（2026-10-21）

用户明确指出日本与香港之间的跨区流量会计费。默认将计算、归档和核验分开：图像计算在 GitHub macOS runner；大归档从 GitHub 直接下载到日本；完整 GPG 验证、tar 成员 SHA 与 manifest 对照在日本本地执行。香港只读取小型公开指标和 hash 摘要，以及提取 archive session key 所需的至多 32 KiB 密文头。不会为查看结果或补文档把完整 ZIP、大密文或照片在日本与香港间反复传输。

私钥留在香港。临时 archive session key 只经 SSH stdin 和匿名文件描述符交给日本端 GPG；不写入日志、命令行或文件。日本端不保留解密出的照片或 tar 成员。含人物的预览与结果仍只作为密文上传。

新 run 下载前核对 artifact ID、大小、GitHub digest，落地后核验 ZIP SHA 与全部成员。已存在且 SHA 一致的归档只复用，不重复下载。超过 1 GB 的下载停止并按用户规则确认。完整校验与研究源保留后，才清理本 run 的临时 secret、release、tag 和分支；不删除原件、历史输出或其他分支。

流量记录区分 GitHub→日本下载量、日本→香港密文头、hash 摘要和小型公开文本；应用 payload 计数不包含 SSH/TLS 开销。小密文若整个落在 32 KiB 头内，按完整小密文实际字节计入，不能写成“零密文回传”。完整 ZIP/大密文 body 的跨区回传另列为零。每次对照保留 receipt，不把“未回传大文件”说成“没有网络流量”。

使用入口为 storage/verify_remote_private_v3.py 和各 run 的 archive_remote.py。早期 v1 的完整密文 stream 属于历史实现，不用于之后的大归档。调试先读现有小型日志与 receipt；需要新数据时只提取最小的文本证据，不重复搬运旧大归档。
