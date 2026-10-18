
## 人物语义阶段：待实机与 runner 的界限（bit-exact 已收尾）

旧 R1 精度继续项是历史记录，用户已明确停止追逐；不再重启。以下新项目不把失败归因于 RAW 缺失。

**可交给 macOS runner：Texture 原生单位算子。** 输入 IMG_2810（仅加密传输）、实际15张mattes、原生Apple Log thumbnail、styles/texture_styles plist，build26A434。源码 research/semantic-styles/semantic_texture_s2.m。检查每次查询checkpoint、lldb原生堆栈和算子returncode；NSValue→CIVector修正对应原生vectorWithCGRect调用。固定所有其他上下文，分别记录UnderEye/SkinSmooth/Mattify输入/输出、descriptor、mask缺失和personData；每步结果与GTM/LTM分开。若缺personData导致跳过，身份输出不算成功去风格。S4已执行但待获准下载6.8MB密文；不是待实机事项。

**可交给 macOS runner：独立 consumer 皮肤色彩。** 从同一原生renderFinalAdjustments dispatch保存SSRParams、SSRColorManagement、ROI、guides、c/d和全部mattes；只把SSRParams.field14的field9/10分别设0作对照。不可清空person matte，因为它还改变LTM。完整原生重放与旧pipeline的基准先比对，再提取皮肤算子输入/输出；内部工作RGB→线性P3须使用原矩阵。新semantic_skin_model.py仅为连续float候选，先和AIR/原生单位算子比较，再验证反解残差、near-black/clamp/singular mask、mask覆盖率。旧门槛不放宽，也不宣称float候选通过half逐位门槛。

**待实机：原始 Texture 人脸上下文与真值。** 需要同一iPhone18Pro/iOS27.0.1原始捕获上下文（记录精确build、框架UUID与SHA），包含TextureStylePostProcessedPeopleData、instance mask引用、faceROI/landmarks/pose和imageStats；当前IMG_2810的214B plist缺这些字段。用同一已冻结主图/thumbnail/语义mattes运行Studio各效果的开/关，再抓每一步前后half/float及shader参数。不要重新拍两张变曝光照片作单算子真值。真实去效果候选必须在原始上下文上原生forward回放；区分残差通过与唯一可逆，clamp/平滑零频段只给信息区间。Vision新估计的人脸只能作为假设上下文，不能冒充原拍摄统计。

**待实机：相机人脸曝光 counterfactual。** 当前CameraColorProcessing静态证据来自24A446/iPhone12,1，和样张不一致。需同版本同硬件、同一帧统计/driverInput的副本，在原生计算中分别保留j与启用WithoutFaceBoost（参照新版本确证地址，不把旧offset写进未知build）。保存原j、face权重/ROI、global LUT、GTC、local LUT、c/d打包前后、thumbnail统计及最终像素。判据：用原分支能重建基准；只改变该开关，分别量化global/local曲线变化、人物内外EV和边缘误差。然后按已确定顺序撤销，不能把最终图除j当作测试本身。需要能调用相机内部处理的诊断环境；普通macOS consumer不能生产这些相机统计。

**待实机：RAW EV。** 继续要求Mac上的IMG_2679/IMG_2408配对组；分开报告GTM、LTM、人物/皮肤色彩、纹理各阶段的RAW EV，不用目前无RAW的IMG_2810宣称场景精度。Photos UI等价性仍需真实图库测试。runner若实际支持Metal则不把普通原生接口失败归类为“缺GPU”。
