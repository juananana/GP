# T4 AutoDL Summarizer 稳定性验证

日期：2026-06-08

## 一句话结论

T4 的真实仓库实验已经从单 seed 现象推进到三 seed 稳定复现：在 Click real-repo line-level deprecation audit 上，AutoDL standard summarizer 连续 `3/3` 次给出高置信完成，但 recall 都明显低于完成阈值，构成稳定的 aggregation-stage false stop。union-preserving summarizer 连续 `3/3` 次消除了 false stop，但代价是 precision 明显下降。

这一步可以支撑论文里的一个核心说法：

> 在真实仓库发现任务中，最终汇总器可能把多 agent 报告中已经存在的少数派证据删除，并把高精度但不完整的摘要误报为完成。

## 三 seed 结果

Oracle size：`149`。完成阈值：`theta = 0.95`。

| seed | policy | confidence | found | TP | FP | recall | precision | false stop |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed01 | standard | 0.930 | 105 | 104 | 1 | 0.698 | 0.990 | true |
| seed01 | union-preserving | 0.910 | 199 | 148 | 51 | 0.993 | 0.744 | false |
| seed02 | standard | 0.960 | 111 | 111 | 0 | 0.745 | 1.000 | true |
| seed02 | union-preserving | 0.950 | 233 | 149 | 84 | 1.000 | 0.639 | false |
| seed03 | standard | 0.930 | 102 | 102 | 0 | 0.685 | 1.000 | true |
| seed03 | union-preserving | 0.840 | 232 | 149 | 83 | 1.000 | 0.642 | false |

聚合来看：

| policy | mean recall | mean precision | false-stop rate | mean output tokens | mean wall-clock seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| standard | 0.709 | 0.997 | 3/3 | 2180.3 | 18.3 |
| union-preserving | 0.998 | 0.675 | 0/3 | 5139.7 | 37.7 |

## 这些结果说明什么

第一，T4 现在已经能作为真实任务族上的稳定证据。seed01 可能还可以被解释成偶然汇总失误，但 seed02 和 seed03 重复出现同样模式后，结论更稳：standard summarizer 倾向于产出非常干净、非常高 precision 的结果，同时漏掉大量真实项，并且仍然自报完成。

第二，这不是“agent 完全没找到答案”的问题。union-preserving summarizer 只改变汇总策略，就能把 recall 从 `0.698/0.745/0.685` 提到 `0.993/1.000/1.000`。这说明许多缺失项已经存在于 G3 reports 的 union 中，失败发生在 aggregation stage。

第三，union-preserving 不是免费午餐。它稳定恢复 recall，但 precision 从 standard 的约 `0.997` 降到约 `0.675`，输出 tokens 和 wall-clock 也大约翻倍。因此论文里不能简单写“用 union 就解决了”，更准确的写法是：少数派证据需要被保留为 audit queue 或 coverage-risk signal，而不是直接丢弃，也不是无条件并入最终答案。

第四，当前 evidence-preserving protocol 在 T4 上暴露出一个重要边界。seed01 中 protocol 达到 `recall = 0.993, precision = 0.955`，表现很好；但 seed02/03 中 holdout scout 本身召回不足，protocol 只能恢复到 `0.805/0.832` recall，仍然 false stop。因此当前方法更强的是“风险暴露”和“拒绝轻易认证完成”，稳定恢复还需要更强的 audit / holdout 策略。

## 与 completion certificate 的关系

completion certificate v0 对 T4 三个 seed 都输出 `unsafe_to_stop`，触发的主要 flags 是：

- `low_confidence`
- `singleton_missing_mass`
- `chao_unseen_mass`

这正好补上 protocol 的边界：当 holdout 也不够强时，系统至少不应该把当前状态认证为完成。换句话说，T4 的方法结论应当分成两层：

- summarizer policy 证明 aggregation-stage false stop 稳定存在。
- certificate 证明 observable coverage-risk signals 能稳定阻止错误认证完成。

## 论文中建议怎么写

建议把 T4 写成 stronger validation 的核心实验，而不是 strict false convergence 主实验。更稳的定位是：

> Real-repo aggregation-stage false stop under precision-biased summarization.

可以写成：

> Across three blind seeds on a real Click repository audit, a standard high-precision summarizer consistently self-reports completion while retaining only 68.5-74.5% of oracle items. A union-preserving summarizer recovers nearly all oracle items in all three seeds, showing that much of the missing evidence was present in the agent reports but discarded during aggregation. However, this recall recovery incurs a substantial precision cost, motivating a coverage-risk-aware certificate and audited evidence preservation rather than naive union aggregation.

中文理解就是：真实任务里，最终汇总器很容易把“不够多人支持但真实存在”的发现剪掉；剪掉以后结果看起来很干净，甚至会让系统以为已经完成。但如果我们完全不剪，又会混进大量噪声。所以论文的问题不是“要 consensus 还是 union”，而是“如何估计完成性风险，并把少数派证据变成可审计对象”。

## 下一步

优先级最高的下一步不是继续证明 T4 false stop 是否存在，因为 `3/3` 已经足够形成强信号；更该推进的是：

1. 增加第二个真实仓库任务族，验证现象不依赖 Click / deprecation audit。
2. 设计更强 audit policy，让 T4 seed02/03 不只是发现风险，而是更稳定地恢复漏项。
3. 做 prompt-diverse G3 vs homogeneous G3，验证降低 agent 相关性是否能减少 singleton 噪声和共同盲点。
4. 把 T4 三 seed 结果更新进 AAAI 草稿的实验表和方法动机。
