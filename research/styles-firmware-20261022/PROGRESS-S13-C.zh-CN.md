# S13-C：原输出 gain/CCM/transfer

同一iPhone17,3 /24A446 AIR10。`pixel_transfer.py`按真实uint32 enum实现双向CMI transfer，不套用外部ICC名称。code3直接复用已验收的有符号encode/decode，没有重跑其算术批次。新增0/1/2/4/5/6/7/8及default分支，保留各half比较符号、code7负域/等号及本特化code8实际零除。未选中的非法log/sqrt路径按原select条件分域，无法证明的集合继续unknown。

72个新完整原transfer helper调用：输出方向36已知，输入方向34已知/2unknown；70个已知点在210个half分量逐位一致，已知集合越界0。2unknown是输入code8大于half0x1800时原实际零除，原宿主有非有限分量，保留位型。code8小值有限支及未知enum默认零输出未用identity替代。集合最大宽约.18744，不是数值吻合。最新当前模型重放保存输出，不重复宿主调用。

`pixel_output.py`接原568..600：输入enum136==6才走param2选择，ratio577除原half reference gain176；输出CCM转half后按(G乘积+R乘积)+B乘积，再乘ratio，调用输出enum599的transfer，不加RGB clamp。包装独立返回output600、linear597、gain577。

10个新完整输出连接调用：9点/9集合已知，三处共63个half逐位一致，已知集合越界0；1例原gain176=0，点/集合都unknown，原宿主非有限7分量。已知集合最大宽.0124354。`from_post_chain`只接完整上游集合并保留分支决策，接口连接不等于组合宿主或原照片通过。165项回归通过。

收据`native-transfer-s13c.json`、`transfer-replay-s13c.json`、`native-output-s13c.json`含原函数/切片/模型/宿主/输入输出SHA。新增log/log2/powr宿主只用于新分支（powr基数是原正数2）；既有算术未修改。2u/4u及C libm仍为宿主限定。旧unknown、bright位差及field17布局失败与独立tonal468观察仍保留。

```sh
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_*.py' -v
python3 research/styles-firmware-20261022/native_transfer_check.py /path/to/0010.ll.txt /tmp/new-transfer.json
python3 research/styles-firmware-20261022/native_output_check.py /path/to/0010.ll.txt /tmp/new-output.json
```

最终像素打包/ROI写出与原GPU未验证；原RGB、gain、CCM、transfer身份仍是显式输入。继续AIR7早于99的入口和生产→guided连接；没有新下载或私人媒体。
