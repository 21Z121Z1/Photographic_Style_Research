# S98 整幅条件语义逆估计（26A434）

run 39504949862，source 1165f8a074c3b5118cae776c61e0b2f945247687，image 20261012.0260.1。

状态：已验证数值，仅固定上下文consumer效果估计。不是拍摄端已烘焙语义恢复证明。

| 目标算子（0.5） | 作用区像素 / EV有效数 | 作用区 p99 / max EV | ACES 全图max码 | 全图PSNR dB | 真CI接缝max/mean（线性Y残差梯度） |
|---|---:|---:|---:|---:|---:|
| skin-color | 135930 / 135930 | 0.0013876280 / 0.0125287194 | 1 | 96.531448 | 0.0007779315638 / 2.391390806e-06 |
| skin-brightness | 187760 / 146671 | 0.0021920004 / 0.1131939515 | 1 | 111.047280 | 0.000188416132 / 7.808608705e-07 |
| skin-both | 323680 / 282591 | 0.0016765019 / 0.1131939515 | 1 | 96.380678 | 0.0007779315638 / 3.172250755e-06 |

B=F(X)，X是本次原照片解码后送入native filter的输入，Tone固定+0.35。Xhat由B求解；计算D=F_neutral(Xhat)-F(Xhat)，C=B+D；正有限RGB域输出Q=B·exp2(strength·log2(C/B))，其他像素保留B并记录mask。参考是同一上下文下原native输入生成的参数中和效果。原输入/neutral oracle没有作为seed。

交付loggain以B对应的native.f16为baseline，不能直接乘原HEIC SDR并声称去掉了拍摄端语义。latent Xhat也不是scene-linear母版。native_effect_active只是参考中和确实改变像素的集合，不是matte或新逆mask；零效应区实际最大变化非零（≤0.000977278），不可说背景逐位不变。

旧RGB-eligible mask覆盖0.9443835540752249，8327939点超1e-3，max relative0.7113556778389195。215289个原输入分量落在旧box外，该计数不是像素数，也不能解释全部失败；未把未收敛点归为信息丢失。旧失败保留，不继续为bit-exact重跑。

0.5三个实用gate均通过；1.0敏感性也通过预声明实用gate，ACES max3/2/3、作用区p99 EV0.002775589/0.004322484/0.003340014。仍维持预先选定的0.5，不根据结果更改默认。brightness/both的EV尾部max0.11319（全强度0.21814），近黑等排除仍如表/JSON报告，不能用全图p99零掩盖。

half loggain传输与逆估计分开：色彩max gain误差0.0000305065EV、亮度/联合0.0009749993EV；对应RGB绝对误差max≤0.00001347065，ACES量化差max1码。输出本身已含该half传输再与oracle比较；不是只验证未保存数组。

12个完整校正map及12个mask的大小/SHA逐项与已认证私有tar对上；全部native reference、恢复effective half、estimated-neutral、roundtrip/residual/old mask仍在日本密文。3271组预览输入SHA全部不变，私有账本SHA abd402f083db598219f2e8416543075b78c828f026917404b0c037f4084a083e。

776092602B原ZIP直接GitHub→日本，22 public/GPG167 private全验。香港读306197B公开成员（编码开销另计）、32KiB密文头和26584B摘要；无ZIP/大cipher body回传。临时secret/release/tag/分支清理已核对。

继续可runner工作：连接真实revert-image/原照片处理域，验证适用于实际原片的独立语义撤回及全分辨率matte边界；完整五套母版/载体与global/local文件留存、HDR组合。仅本次条件测试通过，不宣布A完成。相机同帧曲线/统计、原Studio、RAW和实屏仍待实机。
