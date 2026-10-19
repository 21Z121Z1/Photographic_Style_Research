# 独立 HDR 渲染与场景恢复持续目标

目标已由用户明确授权并建立为 active。利用苹果 Styles/c/d/GTC/LinearThumbnail/语义数据，分别逆可识别的global、local、语义/纹理处理，保留不可逆区间；以相对scene-linear P3母版候选独立制作HDR，原SDR像素保持，最后生成RGB Gain Map，测试低/中/高headroom。

两个验收面独立：

- HDR制作/显示/承载：算子干预、HDR目标、Gain Map表达/量化/编码、原生不同headroom、全分辨率SDR像素max0；视觉/边缘/色彩指标与物理反演分开报告。
- 场景物理恢复：真实相机生产数据流、原生逆/往返、全域可行区间、RAW曝光误差。旧half/float/1e-3、5图且2张冻结后留出门槛不变，当前33皮肤点紧外包络仍未认证。

不以Gain Map表示自洽、减局部后的观感或消费端参数中和证明已经还原scene。全局、局部、语义分别输出，再通过真实顺序组合。LinearThumbnail保留Apple Log，无203nit标定，固定ACES SDR预览只作诊断。

实施顺序：

1. S29：原Core Image双图writer、ISO Gain Map metadata与headroom reader契约；5组合成输入，先分离codec误差，不计入5张照片验收。
2. 在冻结公式后扩展原片5张、至少2张后加入，SDR codestream/property不变；原生ImageIO全尺寸max0。头部/中间headroom原生输出及公式对照，必要时提高map精度，不放宽1e-3。
3. 把已识别Apple local/semantic控制接入独立HDR制作；field/曝光/曲线有证据才归到物理逆，否则保留假设与区间。guided锚点候选不冒充纯scene。
4. 追相机c/d/曲线/CCM与j生成链，以及Studio/锐化/去雾覆盖；缺同帧原统计的按可执行实机TODO维护。真显示器headroom感知测试与配对RAW待实机，不能用runner数值代替。

约束继承：只研究分支、不master/PR/force；每次一个run，retention-days1并立即归档SHA。人物照片/可重建输出只加密+临时secret，完成清理secret/release/branch。整Apple二进制上传先问。重型计算只macOS runner；本地Python400MBscope；本轮100MB写入、根剩余>=4GB、>1GB下载先问；不动冻结文件/原件/旧归档及consumer-goto-v8。

当前总状态：active / acceptance_complete=false / scene_accuracy_verified=false。S29的合成成功只验证传输接口，不能改总状态。
