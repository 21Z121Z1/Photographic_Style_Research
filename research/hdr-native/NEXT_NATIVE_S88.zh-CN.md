# S88：真实独立HDR目标与新载体集成试验（执行前计划）

本轮先复用已有IMG0032母版，接通S44/S47显示意图与S87 matrix6/10-bit封装；不是重复验证压力图，也不重新求key1/guided。此照片是集成开发样本，不计新配方留出。全分辨率语义控制及五路分离效果仍在后续范围。

输入：S42 run39254061338，artifact12187152763，ZIP153946146B，SHA230cd8fcae5c17fec4d3841788b4003e0c016fb3714c674ce1a176a45887dc59；EXR SHA9b392ea7cf996d1cbc70fbf82911b3c04e51562653010e7a78ee4a7a8129b012。只在runner完整SHA/GPG验证，VM不下载大母版。2026-10-20只读API确认尚未expired，expires_at12:51:18Z；若过期，停止该绑定，不伪造可复用状态，另按冻结S42方法重建所需新集成输入。

代码：run_hdr_s88.py沿用derive_display_s51生成的S47前缀，额外只保留旧transport mask字节。主图/母版/显示公式不改；新log Gain Map、offset序列化舍入、10-bit量化、codec/provider和原生headroom1/2/8误差分栏，精确输入/预览SHA前后比较。读取原irot，原始网格编码，原生oriented读回与固定旋转参考比较；不试翻转挑分数。完整ImageIO原整数SDR max0单独核对。

输出：公共汇总≤250KB，密文预览≤300KB，单张完整HEIC加原S42 mask的密文≤20MB；仅传加密像素，临时session secret完成归档后删除，无私钥上传，无新release。worker只读、xcode-27/26A434、retention-days1，一次一个run。VM只做限400MB的哈希/归档，图像计算全在runner。

写入许可尚缺：现125000000B累计上限仅余20779B。申请提高到150000000B，用于本集成源码、汇总、加密预览和单张完整载体归档；完整EXR仍不下载。按实际artifact大小先核账，根分区保持至少4GiB，>1GB下载仍另问。冻结模型、master、旧workflow不改。仅新增研究分支文件，未触发run/创建secret。旧数值门槛和mask保留，工程/scene/A总验收不预判通过。


2026-10-20T13:04Z更新：用户明确批准累计150000000B写入。上述旧artifact已返回404，不能复用；S88改为在runner上只重建IMG0032所需输入。rebuild_master_s88.py从冻结S42中选择原AST语句（原公式、两个原生RGB-map分支和原mask计算不变），记录节点/源码SHA；原EXR写出函数也不变。计算后的EXR SHA单独核对旧值，只有实际相等才能说一致，不以旧值冒充新值。S47仅替换失效ZIP/GPG输入绑定和来源说明，显示数学不改。此路径无需临时secret、release或新照片明文上传。旧留出角色仅为历史，本次一律集成开发。其余250KB/300KB/20MB输出上限及4GiB根空余不变。
