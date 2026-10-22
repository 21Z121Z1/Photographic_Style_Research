# 条件prior算子：原AIR宿主重编译比较

`style_prior.py` 新增的是iPhone17,3 /24A446 CMImaging的CalculatePrior末段及AddPriorToLHS/RHS，来源为本任务已验证资源的AIR107/108/109。不是tone/color/intensity→CCM生成器，也不是像素GTM、LTM、SRL或完整style逆。没有重写已有S20或纹理条件逆。

## 边界与公式

强类型 `SystemLayout(P,S,W)` 按原参数字段保存polynomialCount、systemSize、weightPlaneCount；模型只支持P∈{4,7,10}、1≤S,W≤1024，边界是本实现预算，不声称Apple做同样拒绝。颜色管理、输入归一化、上游SIMD reduction顺序与prior矩阵方向均为外部上下文。

CalculatePrior在**实际reduced sum已给定**后，`m=f32(sum/f32(P*S))`，三组factor为 `max(2^-23, f32(lambda_group*m))`。P≥4时RHS常数/线性factor与相应LHS一致。没有用任意NumPy sum替代GPU原始归约；P=4时二次组没有下游使用。

对实际ushort网格ID g：

- LHS：`term=g%P`，group为term0→常数、1..3→线性、>3→二次；plane=`(g//P)%W`。只写offset=`(P*S+1)*g`，加 `scale[plane,group]*factor[group]`。没有对整矩阵任意位置加同一lambda。
- RHS：term=`g%12`，block=`g//12`，group为term0..2→常数、3..11→线性；plane=`block%W`。写offset=`3*P*block+term`，加 `factor[group]*scale[plane,group]*priorMatrix[term]`。priorMatrix显式是12个float的flat buffer，不猜它与RGB行列/CCM的方向。

Python模型显式逐次float32乘法/加法，不隐瞒原AIR的fast-math允许收缩；没有最终clamp。调用者提供全部factors、scale、矩阵和原buffer。更新返回偏移/增量，保留非目标元素；有限域、buffer长度与唯一grid ID有显式检查。

## 实际结果

5项新增单元测试验证组别/plane、单参数差分只改对应对角、RHS常数与线性分割、flat方向与布局空隙、quadratic不改变RHS、比例歧义与非法/短buffer拒绝。加原27项回归，共32项通过。比例factor和plane scale可相互抵消的合成反例保留；仅凭该更新不能唯一反推两者。

`native_prior_ir_check.py` 先用已提交的canonical hash重新校验私有AIR108/109，再把**原全文**交给安装的LLVM clang，target override为arm64 macOS。原地址空间、参数布局、常量、算术和fast属性保留。仅这两个kernel没有外部AIR采样/归约调用，可以由宿主ABI运行；不加载iOS库，不称为原iOS CPU机器码或GPU二进制执行。

27个结构化布局加128个固定种子随机布局，共155组、310次kernel；18058次写入，包含非目标元素的1540061个buffer值均比较：

- **4855个逐位差异**，最大绝对误差 **7.62939453125e-06**。没有改阈值追求零逐位误差。
- 宿主编译可见FMA收缩；每个写入用未消减的绝对乘积与原buffer计算保守float32三步舍入界，**越界0**。这是本次有限normal输入域的比较，不覆盖NaN/Inf、subnormal或GPUfast实现。
- 原shaderSIMD归约、像素颜色域和整条style链仍未认证。

收据 `evidence/native-prior-ir.json` 保存原AIR文本/模型/检查程序、宿主编译产物/反汇编SHA、全部分组统计与输入输出SHA。私有AIR与临时dylib未上传；没有访问样本或照片库。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_prior_ir_check.py /path/to/private-air-scratch research/styles-firmware-20261022/evidence/cmi-air-alpha.json /tmp/psr-prior-new.json
```

取得匹配CPU框架后，下一边是确认configuration的priorMatrix到buffer8、实际P/S/W和plane scales的设置，而不是依据字段名把tone映射成曝光。SystemOS定向下载进度/最终结果独立记录，不把下载启动或编译成功当作CPU链拆解完成。
