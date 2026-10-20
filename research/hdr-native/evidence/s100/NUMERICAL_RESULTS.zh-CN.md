# S100 真实 key1 输入域与 Tone0 行为
run 39514608080，source e9a93b09f0c814dce6816e60b0bc2f274db4cb35，26A434 / image 20261012.0260.1。状态：已验证数值，固定探针上下文。
| 输入 / Tone | 与自身输入的RGB max差 | 自身输入对照p99 EV | ACES max码 | 皮肤色彩 / 亮度 / 联合改变像素 |
|---|---:|---:|---:|---:|
| original-tone0 | 0.06893217564 | 0.4176386297 | 23 | 0 / 0 / 0 |
| key1-reverse-tone0 | 0.07080078125 | 0.4263626933 | 23 | 0 / 0 / 0 |
| key1-reverse-tone035 | 0.353515625 | 0.64402771 | 69 | 128324 / 178433 / 306749 |

这些差值是consumer输出与它自己的输入比较，属于处理幅度，不是逆解误差、scene精度或F(R,0)与原片S的往返误差。没有重新跑逆解，也没有新ImageIO/SDR载体测试。

Tone0两case内field9/592与field10/596都已是0，三个参数中和的原生效果全0；但整个consumer明确非恒等，不能把Tone0视为无local或无处理。R+.35时9=0.503125011920929、10=−0.22238825261592865；仅目标字节改动，其他参数/纹理/cd/GTC/guides/统计逐owner保持原SHA。

实际native key1 R来自冻结source_s37/Styles_full_v3，max_edge0，5712×4284；native half后精确widen f32，没有新曝光或tone操作。R捕获数值范围[0,1]，这本身不证明是哪一算子clamp，也不能当scene master。原生反风格配置12×9、8planes、sigma2.5、ColorSplit false，属于本次实际configuration，不扩展成未证的语义分解。

三个case各4个真实CI owner，24470208像素完整覆盖一次；12个原生PSO重放hydrate half差0，native/CI RGB max差0，上下文SHA全不变。每case skin11完整raw R16共869043正texel、23601165零texel；它是原始绑定格，不是内部精确采样matte、语义支持集或背景零变化证明。

setDefaults后useStyleEngine实测false（本次仍显式设false），inputCast保持默认nil，inputColorBias0，不能声称这等价真实Photos UI恢复全部原编辑设置。F(R,0)和原片S的完整像素直接比较尚未测量；不能用各自均值接近代替这个比较。尚不能把S98以B=F(S,+.35)为基底的校正图直接乘S，也不能把本次皮肤反事实解释为拍摄端已烘焙因子。

统一固定ACES1.0 SDR Video / Linear P3-D65 /0EV，819次预览前后输入SHA全部不变；3.75MB预览只在日本密文，未回传人物明文。完整native R/S半精度zlib、12owner参照/中和输出、raw skin/ROI/参数均已在日本GPG206成员认证，非只存哈希。

原ZIP GitHub→日本577462229B，香港只取公开成员549144B（编码开销另计）、32768B密文头和30993B摘要，无整ZIP或大cipher body回传。临时secret/release/tag/private分支在PR零引用/源保留后全部清理。私有ZIP artifact12308091275 SHA6940dfa84d0d3d4dfc9b05eb1318d9c889612dcc997352906012fbf6a2db1655，内cipher SHA816577f7767420cef7679e8d98df1621edd43bc0554444b3dce9d8aed2d3751d，manifest SHA14ce46f85bf834089bd795d606defc2f564428bdf7fba41ff35fef567c3b088f。

下一步仍可runner：直接测F(R,0)与原片S并定位零Tone非恒等的处理域/配置，不能先假定UI顺序；按原条件保留语义反事实。完整母版/载体与global/local的IO保留器已在workspace准备（未运行），不拿代码准备替代文件交付。真实拍摄端语义分量、同帧j四曲线/N/B/T/V/hist/allocateTone/app域、原Studio统计、RAW2679/2408和实屏按原清单待实机。A、工程、旧acceptance仍false，不再追bit-exact/33点。
