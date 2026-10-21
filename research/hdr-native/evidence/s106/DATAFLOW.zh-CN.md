# S106：沿苹果真实摄影风格生产链追踪

状态：已验证静态，**仅iOS27 24A446/iPhone12,1参考**。不是IMG2810匹配build。共享缓存只读；没有新图片实验或Apple整二进制上传。新解析category后未解码类组0；仍没有在已检查的11个共享缓存模块中找到三个createLinearThumbnail的实现。

1. `follow/3-BWSmartStyleLearningNode.asm.txt` 0x1b05e1410–1418及`loader-helpers/0-capture-helper.asm.txt` 0x1b05e10dc–1134，实际拼出并加载 `/System/Library/VideoProcessors/SmartStyleV1.bundle`。处理器class由同一loader的`CMISmartStyleProcessorV%d`与version1取得。不能把CMImaging内同名旧utilities方法当这个插件实现。
2. `annotated/0-BWSmartStyleLearningNode.asm.txt` 0x1b0639b38/bcc/c4c显示三个真实缩略图生产调用；格式分支及输入存在性决定入口。这里只证明调用输入角色，未证明哪套LTM/WithoutFaceBoost曲线被选中。
3. `follow/7-BWSmartStyleTargetRenderer.asm.txt` 0x1b0936358–63c8复制cast/intensity/tone/color；tone getter结果v13随后原样进setter。0x1b09363d4–646c绑定unstyled主图、另一路linear及metadata、三个matte和crop。0x1b09360f8/6104绑定coded thumbnail及其metadata，64c0/64cc绑定两张small light map，再于64e0调用process。这是真实生产调用链的静态补证，不是仅据字段名推公式。
4. 同函数0x1b09369a8–69ec的两条分支都将sp+c8的coded thumbnail交给SmartStyleStillLinearThumbnail附件；`annotated/2-BWPhotoEncoderController.asm.txt` 0x1b08165c0取同一附件，6774–6788以像素buffer和type10送addAuxImage。辅助图HEIF tag表与inside-plugin具体kernel还需继续绑定，不能将这一段直接等同“确定无face boost”。
5. `follow/9-BWLearnSmartStyleRenderer.asm.txt` 0x1b0b32f78–33038给出独立学习阶段的Tone、unstyled/target两个输入与learned coefficients输出。沿用现有key1整体逆风格结论，不把whole key1叫LTM。

每个完整函数边界来自缓存LC_FUNCTION_STARTS，代码窗口SHA在trace/follow/loader manifests；CMCapture UUID995FC22B-41BD-37B4-812F-2686B81C2694，Mach-O header SHA0678924feef322a69bb19bb45f41992b81a158810ae8746b5f20c54096552a4d。没有完整抽取binary，故不虚构整binary SHA。注释器的字符串/selector注释只是定位器，以reviewed-dataflow.json的寄存器数据流审阅为结论；参考构建不代替样张同帧证据。

下一步先由S108只查询macOS26A434实际插件与producer selector可用性。存在则沿原处理器复刻输入构造、Tone→参数→两个light map/guide→输出像素，固定global/semantic做局部反事实；缺失则静态缺口明确定位在这个插件，不再为了同一事实重复caller或编码精度实验。没有用户层face-boost-off开关，也不要求用户拍UI关闭提亮对照。
