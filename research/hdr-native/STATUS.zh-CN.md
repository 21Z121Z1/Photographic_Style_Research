# 当前目标状态

持续目标active，A阶段及总acceptance_complete=false。HDR制作/承载与scene物理恢复两栏独立；GTM、LTM、人物/皮肤/纹理控制分开。

本轮S29–S32：35次原生headroom公式、70次未编码RGB比值应用通过；十个8/10bit合成ISO载体保留原codedSDR及原ImageIO像素max0。编码后目标仍未过1e-3/PSNR；S32已把大偏差定位到编码矩阵/原生RGB读回，12bit原生primary对象存在但render错误、auxnil。合成输入不计5照片，新的真实照片验收数0。

下一步：runner隔离12bit CPU provider/CGContext与CI软件/Metal转换，确认可用map精度和RGB读回；再冻结目标配方，真实五图含两张留出、全分辨率及多headroom验证。33皮肤点全域tight hull、实际生产端GTM/LTM联系仍未闭环。匹配同帧j/WithoutFaceBoost曲线、原Studio统计、RAW与屏幕观看测试维持实机清单。Apple Log、原件、冻结模型和原门槛不改，不重启bit-exact拟合。

详见REPORT、NATIVE_TODO、runs和evidence/validation-s29-s32.json；具体执行commit与artifact SHA用run-provenance，不用最后文档commit替代。
