# 现有OS资源：可复用算子与明确差异

基于 `56fe5ac`，本阶段网络新增下载 **0B**。从已校验的iPhone17,3 /24A446 OS只读复制9个资源、4761920B，每个SHA与上一阶段镜像清单一致，随后卸载本任务挂载点。原始metallib和AIR全文留仓库外；只提交比较程序、哈希、符号与精选配置上下文。没有读取照片库或私人样本。

## AIR比较的证据层

`air_compare.py` 对LLVM wrapper做范围和bitcode magic检查，使用已安装llvm-dis，私有文本总量限64MiB。实际iOS CMImaging metallib SHA `f6d825a7…` 有215个模块，92个选中模块；Mac参考SHA `16a8a119…` 有203个模块，同样选中92个。159个函数名共有，**没有任何共有函数的原始bitcode payload相同**。模块名和该哈希结果均不证明方程相同或不同。

`air_alpha.py` 进一步进行狭义全文比较：按声明顺序对identified type与internal global进行一对一重命名，单独记录target triple、llvm.ident编译器字符串，移除llvm-dis临时路径注释。其余文本全部保留，包括类型定义/布局、常量、global initializer、函数、fast-math属性、sampler、binding、function constant与所有metadata。不会重命名metadata中的字符串，也不会删除属性或归一化数值。重名/保留名冲突拒绝比较。

92对模块中 **91对在上述限定下全文相等**，对应143个一对一共有函数中的136个。不能比较的多重函数对应不计入这个分母。收据 `evidence/cmi-air-alpha.json` 保留每对哈希、平台/编译器和全量改名表；不是交叉平台GPU或完整拍摄链等价证明。

|可复用静态算子|iOS模块 / Mac参考模块|已有模型与适用范围|
|---|---|---|
|UnderEye FinalMix|151 /138|继续复用 `../semantic-styles/studio_under_eye.py` 的显式editedTex、weight上下文连续正向/条件逆；原half指令与sampler误差仍按旧边界处理|
|SkinSmooth最终混合、in-place分支|99 /151；98 /150|复用既有条件单位模型和原生实验分析；不补原始blur/stats或把平滑丢失纹理当作已恢复|
|Mattify region/addback/editingStrength|41 /67|保留HSL编辑、mask归一化blur、addback与clamp的非仿射区别；不能套UnderEye的一次线性逆|
|StyleEngine PolyExpandInput/Target|102 /17；103 /18|确切shader方程可复用；颜色域仍由缺失的输入CPU调度和颜色管理上下文限定|
|StyleEngine prior、加至LHS/RHS|107 /22；108 /23；109 /24|仅shader计算相等；tone/color/intensity→CCM prior的外部CPU公式仍未取得|

这里把iPhone参考资源与已有模型接上了**静态算子**一层，没有继承Mac原生像素精度证书，也没有证明这些shader在该机该帧必然启用。整体texture配置的EffectOrder亦不等于相机实际执行顺序。

## 保留的差异：StyleEngine::Apply

唯一未相等模块为iOS157 /Mac170。实际kernel和相关noise函数中的20处调用，在Mac为 `air.fast_fract.v2f32`，iOS为内部 `___metal_fract_v2float`，并多出fract实现辅助函数与相应属性。没有删掉这些差异来强行做等价；不把噪声、纹理或整Apply模块继承为同一实现。具体输入域/非finite/精度下是否有数值差异仍需独立实验。

## 配置上下文

`resource_context.py` 只读取已校验资源，收据 `evidence/resource-context.json`：

- SmartStyle/V1/Default含SRLParameters、LearningRate=2、SRLCurrentValueWeight=.1等。MaxBoost_I..VI=2.1是配置数值，不据名字称为2.1倍实际人脸增益或EV。
- StyleEngineV1键"12"的TikLambdaConstant/Linear/Quadratic均.01、ExtLambda=.2、LearningModulationStrength=2。插件上一阶段确实调用useCase12，但CommonSettings方法体未取得，所以**useCase12→plist键12尚未认证**。
- 本次实际OS的TextureStyleTuning全文件SHA `9a0963e5…` 与已知Mac资源一致；其iPhone19,2/back/still/Studio/Common子表SHA `398fa58e…`，UnderEye亮度mix=.5、Mattify强度=.3，顺序含FilmGrain。该跨机型资源没有iPhone17,3精确键；这不证明该机缺功能，也不证明iPhone19,2样张选了此表。

IMG_2810仍只有iPhone19,2、Styles16、PeopleDataVersion3的既有清单，精确capture build未核。它与本参考链继续分开；这不阻止当前资源与合成算子的研究。

## 复验与下一组件

新增4项有意义的比较器测试：wrapper截断/边界、允许的alpha改名、常量/布局/fast flag/绑定/sampler/global值/数据布局改变必不相等、保留名碰撞。原23项回归加4项，共 **27项通过，0失败/错误**。本阶段没有重新执行既有257头或通用头原指令验收。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/air_compare.py /path/to/ios/default.metallib /path/to/host/default.metallib /tmp/psr-air-new /tmp/psr-air-inventory.json
python3 research/styles-firmware-20261022/air_alpha.py /tmp/psr-air-new /tmp/psr-air-inventory.json /tmp/psr-air-alpha.json
python3 research/styles-firmware-20261022/resource_context.py /path/to/verified/CMImaging.framework /tmp/psr-resource-context.json
```

当前资源分析没有补出缺失的CPU方法体。最小可定位的下一来源仍是**同一已核manifest中的2348810240B Cryptex1,SystemOS组件**；无需改为另一机型或再下载完整OS。先前缺项清单、CRC与范围见 `evidence/component-reuse-and-minimum-gap.json`。取得并核验其内部cache后，才可继续本build的loader、外部renderer、CommonSettings、CCM prior、SRL和统计调用链。这个依赖与锁屏、图库访问、IMG_2810 build缺失分别处理。
