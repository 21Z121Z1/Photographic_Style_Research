# SkinSmooth 条件最终混合

`skin_smoothing_final.py` 将已有 SEM-23 的最终混合公式实现为独立模型。
输入是同域、同几何的 half RGB 原图 X、已饱和的重建图 S、模糊采样 B，
以及显式 f32 系数平面 a、b。系数不是 UI slider，也不是恢复出的 Apple 统计。

连续公式为 `Y=(1-a)X+(a+b)S-bB`。实现使用 float64 运算，最后保存为
binary16。它没有按 AIR 的 half 指令顺序执行，不能作为原生位级复现。
S 必须已经处于 [0,1]，不在入口静默截断。a、b 仅要求有限，
现有证据没有证明它们的全局范围。上游 blur、guided reconstruction、
mask 到系数的生成、Apple 采样及完整 Studio 链仍缺实现或原生对齐。

源码依据为 `research/semantic-styles/REPORT.zh-CN.md` 的 SEM-23，
恢复时提交 `4d314bdbfd348b5371f737625c8bacc064930be7`，
描述 AIR0151:207–239。历史 metallib 身份为 SHA256
`16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11`。
本轮没有取得或执行该二进制。历史 S11/S13 原生条件往返结果仍属历史输入和源码。

运行合成回归，不需要照片或私有二进制：

```sh
python3.13 -m unittest discover -s research/styles-firmware-20261022 -p test_skin_smoothing_final.py -v
python3.13 research/styles-firmware-20261022/validate_portable.py /tmp/psr-skin-final-new
```

独立入口保留为条件算子，没有将完整 `SkinSmoothingStandalone` 注册成可用效果。
调用者仍须明确给出它相对于 GTM、LTM 和其他 Texture 效果的位置。
