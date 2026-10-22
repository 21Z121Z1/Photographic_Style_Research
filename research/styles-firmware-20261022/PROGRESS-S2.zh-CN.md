# 继续阶段：外部依赖定位、目标输入分支、通用头GTC构建

本阶段基于已验收 `a5318a0`，**新增网络下载0B**。只读重用已校验的iPhone17,3 /24A446 OS镜像和现有缓存，没有读取照片库、样张或重新运行既有257头原指令验收。原15项回归加8项新测试共23项通过；新增算子结果与原35k输出的257头测试分别记录。

## 可复用组件和最小缺项

机器清单为 `evidence/component-inventory.json` 与 `component-reuse-and-minimum-gap.json`。检查逐段lstat，遇symlink即停止，不允许挂载镜像中的绝对链接误落到Mac宿主路径。该OS镜像：

- 已有真实SmartStyleV1插件；约0.4MB必要文件复制到本任务scratch，完整可执行文件SHA仍为 `04dbdad5…`。没有把二进制提交。
- CMImaging、CMCapture、CameraColorProcessing、PhotoImaging的资源和metallib确实可读，SDK/Info和每文件SHA已记录。例如CMImaging default.metallib为2847752B、SHA `f6d825a7e5c00d0eec2e4721c51bdb7a6b9554073dc632273dec825ae1bf705f`，不能把它当作Mac整个metallib或插件自身的metallib。
- 上述框架的CPU可执行文件在该OS组件确实缺失，`System/Library/dyld`也缺失；`System/Cryptexes/OS`是指向Preboot的symlink，未跟随。这不是iPhone没有这些实现的结论。
- 现有24A435资料可作参考，现有S20曲线集合逆、S54记录解码等继续复用。没有以这些旧构建资料替换24A446的实现身份。

目前能明确列出的最小候选缺项是**同一iPhone17,3 /24A446的Cryptex1,SystemOS组件**：`043-70113-711.dmg.aea`，2348810240B，已核中央目录CRC `78747dcb` 与偏移9692339875。内部cache文件及解密后大小尚未验证。本阶段没有下载它，更没有再下另一整OS镜像。取得匹配CPU模块后才可继续定位loader与外部方法体；现有OS资源仍可用于独立shader/配置研究。

## 外部类到底来自哪里

`component_inventory.imports`解析实际Mach-O的LC_LOAD_DYLIB与nlist64的library ordinal。CCM prior、pixel renderer、style engine、coefficients processor、common settings及SRL的9个实际未定义类符号都绑定到**库序号2：CMImaging.framework/CMImaging**。这比看到同名类更具体，但依然不是动态派发方法体或运行加载证明。

新导出的6个方法共5160B指令均回查实际插件字节，清单为 `evidence/bindings-24A446/manifest.json`：

|已核静态边|原指令证据|范围|
|---|---|---|
|创建style engine|setup 0x4900–4918：取CMIStyleEngineProcessor类、initWithOptionalMetalCommandQueue:withCoefficientSynchronization:，结果存self+0x30|该导入类归属CMImaging；不补外部构造器实现|
|创建pixel renderer|prepare 0x5838–5850：取CMISmartStylePixelBufferRendererV1类，initWithOptionalMetalCommandQueue:allocator:，结果存self+0x28|把前阶段process中+0x28接收者与确切类连接起来|
|stills reversibility配置|0x6ce0 useCase=3获取renderer thumbnail size；0x6cf8/6d28 useCase=12分别取style engine configuration/tuning，再copy并设置|3/12是内部用例编号，不是Styles产品代际；外部配置函数体仍缺|
|生成target与外供target分开|target-input 0x7a78读_shouldGenerateTarget；生成路径取self+0x60的styled输出，经必要下采样后在0x7c84送style engine；非生成路径优先用调用者x3 supplied target，缺时处理x2输入|不能把学习target当作无风格原图，也不能把这些分支概括成固定相机顺序|
|GTC helper确实被使用|unstyled-gtc 0x9354调用_createGlobalToneCurveTextureFromMetadataDict:，结果保存在x24；0x9424/9428/942c把它绑定texture slot1|对应已导出的_extractThumbnail管线；此前linear入口slot1=nil的事实保持，两个入口不混同|

tone/color/intensity→CCM prior矩阵→style engine configuration的前阶段寄存器边保持，详见 `DATAFLOW.zh-CN.md`；现在其外部类归属有实际导入表支持。如何从tone经外部renderer变成曲线、人物/SRL/纹理像素，仍需要匹配方法体或运行捕获，没有用字段名称补公式。

## 新独立算子：非257头的GTC表构建

`gtc_texture.py`扩展既有S54比例模型，新增实际helper 0x8f64–8ffc的分支；保留颜色域为metadata曲线坐标，**不是像素GTM或场景线性RGB**。

H为首个uint16。原helper对H≤64返回nil；H=257走原已验收分支。H≠257且H>64时：

1. 读words[1..H−1]，以words[H−1]归一化；每节点先double除法，再round-to-nearest float32，得到H−1个节点。
2. 对k=0..255，`u=f32(f32((H−2)*k)/255)`，`i=clamp(floor(u),0,H−3)`。
3. `d=f32(v[i+1]−v[i])`、`a=f32(u−i)`，结果为 `half(fma_f32(d,a,v[i]))`。不能用两次独立float32乘加替代FMA。

模型用精确有理数和相邻float32的距离/偶数规则实现单次f32舍入，含能击穿f64→f32双重舍入的测试。输入span按插件实际读取范围校验；后续trailing words不参与。零除数保留为未认证的原生nonfinite义务，不伪称Apple主动拒绝。当前可测试实现/宿主缓冲范围H=65..4097，不扩展成完整uint16头域认证。

`native_gtc_generic_check.py`将该分支的两个原算术循环共156B置于独立macOS ABI外壳，排除原ObjC/动态栈/Metal调用，没有加载iOS库。11个非257头（65、66、129、130、255、256、258、259、513、1025、4097），ramp/step/alternating/random四种结构与除数1/257/65535，另加1组有限输入溢出half探针，共133组新纯合成记录：

- 84568个中间float32节点：逐位差异0。
- 34048个half输出：逐位差异0。
- 251个Inf half输出保留并按实际码字比较，不通过删mask求零误差；零除数的NaN/Inf路径仍未认证。

收据 `evidence/native-gtc-generic.json` 含原指令SHA、输入/输出/测试可执行文件SHA与全部分组结果。没有重复旧257头物理验收。记录整体按相同比例缩放可产生完全相同的纹理；新测试保留这种归一化不可识别性，不把该模型变成原相机参数的唯一恢复器。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_gtc_generic_check.py /tmp/psr-generic-new.json
```

下一可推进项是实际OS资源中CMImaging的目标shader与已知Mac参考的逐模块对比，并读取确切tuning键。CPU方法体、实际loader选择和同帧原始统计暂时属于明确的组件依赖缺口，不因此停掉可独立完成的资源与算子工作。
