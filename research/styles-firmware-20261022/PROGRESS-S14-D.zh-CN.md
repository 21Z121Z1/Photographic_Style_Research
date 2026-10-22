# S14-D：最终 RGBA 打包、ROI 地址与两条写出路径

同一iPhone17,3 /24A446 AIR10。`output_writer.py`连接显式half RGB600到原25..27与601..618：RGBA alpha固定1，不额外clamp；目的地址为ushort2(logical gid+ROI12 outputImageGridOffset)，offset byte160；imageblock leader用ROI2 renderEdge（byte8）减目的地址，按unsigned ushort回绕后与实际group尺寸取min。renderEdge不是另一个源UV偏移，不能改成signed clamp。

host包装只重命名SSA、增添ABI，原算术/比较/FP属性不变。CPU phased scheduler先运行全部nonleader，再运行leader；nonleader在barrier后没有跨线程内存读取，leader copy只有在全部active writer到达barrier后才允许执行。内部tile pitch32，覆盖边长1..32、非uniform active tile；真实GPU imageblock/多线程没有执行。不是用空barrier加最终结果冒充GPU同步。

新7个2×3 tile，目标6×8 RGBA16Float115：direct、完整imageblock、edge裁切、zero extent、renderEdge unsigned下溢、direct地址回绕、imageblock地址回绕。42次原writer调用；7幅完整目标共1344个half分量逐位一致，7个已知集合覆盖，写像素mask/count全部正确，未写区域保持初值，HDR/负RGB保持原值，alpha仅在写区域变为1。

包装诊断会写global counter。已把相关intrinsic memory摘要保守从read/argmem-readwrite扩成readwrite，未改FP flags或原打包逻辑。初轮7-case原输出与收据保留；修正后只重放3个保存见证（direct、裁切、imageblock回绕），输出逐位相同、诊断0错，没有重跑整个7-case批次。另一个leader-first负例被host同步合同拒绝：error1、写0像素、目标不变；该负例验证宿主包装，不能推断原GPU对非法调度的行为。

`from_output_grid`把上游`pixel_output.Result.output600`完整盒直接组成tile，保留分支决策，拒绝点中心代替集合；接口回归不计为额外组合原生通过。180项回归通过。目标以外地址在模型中unknown，不猜硬件OOB语义；其他packed/normalized输出格式尚不支持，未读私人媒体或把显式RGB600说成恢复所得。

收据`native-output-writer-s14d.json`与`writer-memory-regression-s14d.json`含原slice/模型/IR/C/输入输出SHA、全部目标位型、mask/extent/counter结果。最新`pixel-inventory-s14d.json`不再把SSA557、外围saturation或本限定writer标未建模，也保留各自域限制。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_output_writer_check.py /path/to/0010.ll.txt /tmp/new-writer.json
python3 research/styles-firmware-20261022/regress_writer_memory.py /path/to/0010.ll.txt research/styles-firmware-20261022/evidence/native-output-writer-s14d.json /tmp/new-memory.json
```

本增量没有把独立片段相加为全照片/逆解通过。旧24组合unknown、8叶域unknown、S14-C五个集合unknown、S14-B五个位差与17941.5513宽包络、旧155.125包络、bright等差异和9个未定位消费者保留。真正原iOS/GPU/同帧验收与IMG2810 capture build依赖仍单列；没有新下载、ps重试、私人媒体访问、合并、删分支或安全/预算变更。
