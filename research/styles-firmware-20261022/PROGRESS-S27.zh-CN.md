# S27：显式共享raw field3的多已知上下文联合候选API

本轮仅查询已有同v3目录，实现**调用者明确声明共享同一个内部raw f32参数**时的联合候选API。state7示例从第一场景的7/8/9类收缩到7，但联合结果恰好等于更强的第二场景，**没有超越它的额外候选消除**。平台仍多解；不相容目标对返回共同参数候选空，不判任一单张目标非法，不最近值兜底。

新增完整模型前向、原kernel、编译均为**0**。未扩场景/参数域/cast，没有修改v3模型、原单上下文API或已有目录。

## 共享条件与身份合同

`joint_color_api.py`提供`SharedField3`、`Observation`和`solve_joint`，以及JSON请求入口`solve_request`。共享声明没有默认true：调用者必须给`SharedField3(True)`或JSON中的显式布尔声明，字段定义为`post-scene SSRParams.color field3 byte12 raw f32`。相同UI设置、Styles名称或metadata本身不能代替该声明；API不推断这些因素是否使不同帧的场景缩放后raw参数相同。

API只接受既有两个完整冻结context SHA，对2至8个观测至少要求两个不同的已支持context；重复观测不会被计为新场景。每个target必须绑定自己的完整context、目录SHA及精度。两目录的build/内部class/ABI版本、v3精度、字段定义、域及partition须一致，不静默缩域兼容不同合同。当前仅cast0、唯一自由字段3；cast16/多自由参数继续禁止。

两份已验收完整目录的SHA另作来源钉住。partial目录只可省略行或标为unknown；所有保留已知行的代表值、接口键、writer数组和digest必须等于对应原目录。即使新writer及其digest自洽，也不能注入为“既有模型行”。

身份仍为iPhone17,3 /iOS27.0.1 /24A446、SmartStyleV1 /CMISmartStyleProcessorV1。产品代际、内部版本和HEIC编号分开，ABI version0不解释为HEIC版本0。保留的精度SHA为`9358741644914631950a72161b25967ba9c433400d1faf3dbb4267db1fb036da`；域仍为canonical`+0..3/8`，raw闭区间`0x00000000..0x3ec00000`，不含负零或域外值。

## 按raw位型求交，分别报告已知和未决

`raw_f32_sets.py`以含端点uint32范围为主表示，核实对应二进制实数端点的开闭及精确人口。交集取raw最大下界/最小上界；合并、差集和人口计算不引入舍入容差。端点几何随结果保留，邻接区间的合并只表示离散f32集合，不作实数连续域声明。

对每个单目录，记已计算且匹配的集合为K，缺失/unknown所对应的未决区域为U。联合结果为：

- 已确认模型候选：各K的精确交集。
- 可能候选：各`K∪U`的精确交集。
- 尚未决候选：可能候选减去已确认候选。

结果分别导出`confirmed_model_joint_candidates`、`possible_joint_candidates`、`unresolved_joint_candidates`及各自人口。原缺失/unknown state ID和单目录coverage仍保留。某未决区域可以被另一完整观测排除，但这不将原partial目录升级为完整目录。显示的接口state ID是辅助信息，主计算依据raw位型区间。

机器结果区分区间代数、已有条件点模型目录匹配、调用者共享假设及原宿主/GPU证据。所有本轮联合class均标`model_only`，没有联合原宿主实验，不扩大任何单目录的有限见证。

## 三个已有模型目标示例

5份target文件均直接取已存在的v3目录writer行，未新增前向；请求/目标与原目录SHA记录在`joint-example-plan-s27a.json`。API只读取target位型和绑定身份，不使用来源state ID或真实控制作为求解输入。

|示例|各自候选|联合候选与结论|
|---|---|---|
|第一/第二scene各state7的writer|第一7/8/9，2400255个f32；第二7，860159个|联合7，860159个；等于第二单独结果，额外消除数0|
|两scene各state0的writer|两者均0/1平台|仍为0/1，1018499073个f32；没有唯一值|
|第一state7、第二state93的writer|各自都有非空精确模型候选|共同raw参数候选空；不推断哪张目标非法，也不扩大到域外/其他模型|

state7联合范围为开区间`(.073272705078125,.079681396484375)`，raw含端点范围`0x3d961001..0x3da32fff`。相对第一scene消除1540096个f32，相对第二消除0；不能宣传额外超越最强单观测的信息增益。

平台范围保持闭区间`[0,.02210235595703125]`，raw `0x00000000..0x3cb51000`。即使联合多个已知context，有限输出量化和碰撞仍留下大量多解。

## partial目录及边界测试

23项最终定向测试通过，unittest1.361秒。包括精确端点开闭、闭端点单点相交/open端点空交、邻接与重叠去重、差集补集闭合，以及小范围独立整数集合枚举对照；还覆盖未声明/false/UI别名共享、不同版本/域/精度/字段/partition、真实文件的错build/域、错context目标、JSON导出及partial已知writer注入拒绝。

partial测试只在临时目录删除或标记已有行，明确为模拟、前向数0，不把它们写成真实目录新发生了unknown：

- 删除第一scene匹配类7/8/9：已确认交集空，但保留860159个未决可能候选。
- 只把第一scene7标unknown：已知8/9不匹配第二scene7不能排除未决7，可能候选仍860159。
- 删除无关93：联合已知/可能均为7，原目录coverage仍partial。
- 第一scene缺失93、第二target为93：原本完整目录下空交的例子变为未决可能区域，不能仍报确定空。
- 第一scene全部unknown：仍保留第二scene的可能候选，不能把unknown当作负证据。

测试同时拦截完整前向函数和原kernel入口，证明联合查询路径不依赖它们。没有新增叶算子批次或重跑146状态/旧8边界。

初版三例及22项测试已通过；加入原目录行来源校验后，在相同冻结请求上重放三例并运行最终23项测试，数学候选完全相同。初始结果未覆盖，初版实际API/驱动/测试源码原件保留在任务私有`s27-private-source/`，SHA见`source-iteration-s27e.json`；最终带来源校验的结果为`joint-result-*-s27b2.json`。这些重复查询和测试均未增加前向/kernel。

## 复验与保留限制

仓库根执行，输出文件必须不存在；命令只查询目录：

```sh
python3 research/styles-firmware-20261022/joint_color_api.py \
  research/styles-firmware-20261022/evidence/joint-request-state7-s27a.json \
  /tmp/psr-joint-state7-new.json
python3 -m unittest discover -s research/styles-firmware-20261022 -p 'test_joint_color_api.py' -v
```

请求schema为`psr-shared-field3-request-v1`，`shared_parameter`须显式声明`same_raw_f32_across_contexts: true`，并绑定上述field定义；每个observation指向自身context/precision/partition/catalog/target。JSON结果同时包含请求、文件和算法源码SHA，输入文件（含所有chunk）在求解前后复核一致。

实际请求、结果、审计、测试及运行前source/input绑定位于`evidence/*s27*`；最终摘要为`verification-s27.json`。原目录、v3模型/API的SHA保持，现有S25成本162–163限制未改。bright6+18、cast16/多参数禁止、集合unknown、9字段缺缓存、历史IR原因未知、原GPU/UI/真实同帧、IMG_2810 build和未知源逆解继续保留。每场景140类未原宿主穷尽，本轮没有新host联合验收。

没有新下载、挂载、找缓存、私人媒体、被拒ps重试、其他项目或安全预算操作；Git只提交代码、合同、合成目标和脱敏结果。
