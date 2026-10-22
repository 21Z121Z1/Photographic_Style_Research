# S18：默认contrast接线、负底数域见证与9字段新增追踪

沿用iPhone17,3 /iOS27.0.1 /24A446、内部SmartStyleV1 /CMISmartStyleProcessorV1的同一已取得资源。产品Styles2参考、内部V1、IMG_2810的iPhone19,2 /Styles16 /TextureStylePeopleDataVersion3仍分开；IMG精确build与匹配链未补。本轮没有下载、私人媒体、原GPU执行或其他项目操作。

## cell0已接默认路径，完整BG仍未通过

`pixel_leaves.contrast`先执行原独立集合图，保留点模式和原已知域。仅原图返回DomainUnknown且符合以下**全部**条件时，调用S17联合界：half集合RGB三通道；RGB整盒包含于保存cell0；half参数整盒精确等于`.029998779296875`。其余原unknown继续原样抛出，不给任意输入套新界。

准入外包络是R[0,.23502742808362515]、G[-.014420070058153133,.2394291029825464]、B[0,.1698263112707185]。包含关系接受整盒及其子盒，未把任何实际输入缩到此范围；证明仍是原half商先有限、再界原乘法，原严格门限、2u/4u、tiny与else并集均不变。

`bg-default-replay-s18a.json`只重放原保存64子域和原S14-C case0，没有产生新分区、叶输入或原宿主调用：

|范围|原独立图|当前default|
|---|---|---|
|保存cell0|unknown|已知包络，最大宽1.68080284096|
|保存64子域|56已知、8 unknown|57已知、7 unknown|
|原S14-C case0完整BG|BG352内contrast unknown|仍unknown，整输入盒超出cell0准入|

完整BG第一个已记录失败仍为contrast的原`newspan / originalHalfSpan`。当前整输入盒R[0,.9401097]、G[-.0144201,1.0009766]、B[0,.6793052]，商分子盒[0,26.8175377]、正分支分母盒[1.001358e-5,1.0019542]使独立商界超65504；这些端点未证明联合可达。新准入并不覆盖此整盒。所有已观察的前缀范围继续覆盖保存宿主值，未把local通过升级为完整BG通过。S16另外7个失败盒的有序局部证据保留，本轮没有重跑48个有序域或把它们无条件接入默认路径。

## 完整clamp域确有宿主负底数见证

这轮改为判定原helper的完整clamp域[0,1]³，不继续用同一个中性颜色点调误差。先在8个RGB盒顶点运行点模型，选出一个候选；随后**只作1次原AIR前缀宿主调用**，保留同一函数起点至gamma SSA210的原算术/call文本，返回原converted199与gamma210。后续pow SSA213及其所有指令不在编译前缀中，没有执行负底数pow。

输入为精确half RGB=(1,1,0)，person=.4、skin=.25、sky=.2的half表示，零offset/amplitude/output_mix和显式零lookup。原输入clamp不改变此RGB。原AIR前缀宿主输出：

`converted = (.99951171875, 1, -.00012767314910888672)`，`gamma = 1`。

与点模型converted的half位差0。B是非零负half，因此转half之前的原SSA198也必为负。这里的host采样shim仅用于常量零纹理：全部行、通道与有限坐标均返回零；没有据此声称一般二维lookup sampler已验证。pow、cos、atan等宿主数学合同及fast允许的CPU收缩仍是显式假设，不是原iOS/GPU运行。

`selective-domain-s18b.json`保留全部8个模型候选、单次原前缀结果、原函数与所选前缀SHA、生成宿主IR SHA及精确half bits。这是**该宿主舍入合同下对“完整clamp域底数总非负”的反例**，并未证明原GPU产生相同符号；也不意味着S17宽包络的-.4419等端点可达。此RGB尚未证明由S15同帧完整上游产生，不能用它替代那12个像素的联合可达性问题。

`air.pow.v3f16`负底数语义没有从host powf或gamma=1倒推；模型原负底数限制保留，没有pow(1)代数捷径、额外clamp、缩域或预算变化。S15保存上下文的12个selective集合unknown、24个未选内部unknown、无writer集合继续保留；活跃风格与其他lookup域未认证。原GPU的实际负底数可达性及完整pow合同仍须独立证据。

## 新范围：跨函数参数别名与CPU拷贝岛

`trace_consumer_paths.py`没有重扫215资源头。它从已核CMImaging metallib中**定向取原已知payload13**，核canonical SHA `b56d7f51d4556af99356bf5963d270358b2422425b7ba929f056d1a4c95668ea`，新增分析范围是`generateColorCubes`根到递归helper的参数来源传播、原指针字节跨度、无类型GEP/bitcast/phi/select及拷贝/外调逃逸。AIR文本仍留仓库外。

根argument4是Metal buffer1、声明672B；跟踪12个参数相关函数、13条指针调用边、87处参数访问。根分别两次传原params到`renderAdjustmentsForCube` argument9；后者把params+488传BG argument4、params+556传FG argument6和skin argument1，也向BW/channel/haze等helper传整params。每条边保留源行、指令SHA、formal索引、基址和声明跨度。cast子数组三个动态GEP由原phi0、无溢出单位增量、next=3退出的循环证出index=0..2，实际访问分别在params[60..72)、[72..84)、[84..96)，未把动态索引默认为0。

本次闭合的参数指针遍历中未找到9字段的字节读取。局部`memset`是24B栈矩阵，未建立到9字段的别名；参数源的memcpy/memmove或未知外调没有出现。词法/调用图是may-reach范围，不是全模块、全调用者或运行路径证明。

|字段|SSRParams byte|已知写入与新增传递端点|当前断点|
|---|---:|---|---|
|BG airy|512|AIR11 RenderingParamsFromStats store；AIR13 BG子引用+24|BG相关闭包未找到读|
|BG warmthMatchI/Q|536/540|同一producer store；BG子引用+48/+52|同上|
|BG warmthMatchSkyI/Q|544/548|同一producer store；BG子引用+56/+60|同上|
|BG bgGlobalMix|552|同一producer store；BG子引用+64|同上|
|FG airy|560|同一producer store；FG/skin子引用+4|FG/skin相关闭包未找到读|
|FG faceI/Q|604/608|同一producer store；FG/skin子引用+48/+52|同上|

这里没有把AIR11 producer与AIR13根的CPU buffer桥接当成已证明。新增CPU范围是已有字节核验的`CMIStyleEngineProcessor process`两处此前未作9槽来源分析的blit窗口：0x1d42c67f0把来源x21（未解）复制到self+0x148 buffer，长度为目标length；0x1d42c69c8把该buffer复制到[sp+0x460]对象的bufferView，长度为来源length；两侧offset均0。这两岛尚未桥接到SSRParams，未因为指令出现copy就认作9字段拷贝。

已有proxy静态代码可定位self+0x1b0 contents、672B数组stride；新的Proxy dynamic/cube dispatch字节核验仍缺输入。准确目标`../firmware-iphone17-3-systemos/decrypted/043-70113-711.dmg`及其dyld文件当前不在本任务缓存，旧收据SHA为`bce06bf973fe4fcce39f5401be42352b96e2e052cf4c182d107ef8fd2d86fe18`。symbols/objc和已导出文本仍在，但不足以补新的原字节核验；因此未尝试新disassembly、挂载或下载。状态是**缺输入而未执行，非权限拒绝**。最小可恢复材料是同SHA缓存镜像，或已字节核验的Proxy `_calculateDynamicRenderParameters` 0x1d437335c与`_generateColorCubes` 0x1d4373474完整方法及binding证据。

`consumer-paths-s18c.json`给每字段独立writer、可达指针边、读取结果和断点；9字段继续归为未完成软件追踪，不称unused，也不说只能等硬件。CPU缓存缺项、未追踪的其他软件调用者、原GPU/同帧验收分别列出。

## 验证与剩余范围

205项测试通过，新增cell0默认接线/范围外拒绝、原64与完整BG状态分离、真实负底数前缀见证、无类型调用参数跨边读取、动态/存储指针逃逸与未知指针合流负例。保留S17/S16原失败收据、tuning field17/byte652、18个全局encode反例、旧24/8 unknown及S20非唯一逆证书。S17的1938保存half零差异只属cast0/tuning2/中性BGFG/零lookup的原宿主上下文；它不是活跃风格、原GPU、真实同帧或照片逆解验收。

仓库根复验命令；输出文件须不存在。前两条仅纯模型/保存证据，不调用原AIR：

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/replay_bg_cell0.py \
  research/styles-firmware-20261022/evidence/bg-dependency-s15c.json \
  research/styles-firmware-20261022/evidence/native-main-pre393-s14c.json \
  /tmp/psr-bg-default-s18-new.json
python3 research/styles-firmware-20261022/trace_consumer_paths.py \
  ../tone-alias-s18-private/0013.ll.txt /tmp/psr-consumers-s18-new.json
```

单次宿主前缀复验入口是`native_selective_domain.py ../air-cmi-compare/ios/0010.ll.txt /tmp/psr-selective-domain-s18-new.json`，需要本机ARM64 clang及已有私有AIR；会执行1次原前缀、不会执行SSA213。源码、测试日志和收据精确SHA见`evidence/verification-s18.json`，最新覆盖清单为`evidence/pixel-inventory-s18.json`。
