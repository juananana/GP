# Union-Preserving Counterfactual 结果说明

日期：2026-06-07

## 实验目的

这一步的目的不是继续制造更难的任务，而是验证一个更干净的因果问题：如果最终聚合器不丢弃少数派 agent 独有报告，而是保留所有 unique reported items，那么之前被 standard summarizer 和 majority consensus 丢掉的缺失项是否能够恢复。

本次运行是一个确定性 union-preserving 聚合基线。它只读取已有 G3 itemsets，过滤指定 seed，然后保留所有 G3 agent 报告过的 unique items，并单独记录 singleton items。这个结果不应被表述为“盲评 LLM summarizer 已经通过”，而应表述为“如果聚合策略保留少数派证据，G3 reports 中已经包含完整 oracle”。

## 结果

| 任务 | 聚合策略 | Oracle | Found | TP | FP | Recall | Precision | False-stop | 保留 singleton |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| T1 hard seed01 | standard summarizer | 35 | 22 | 22 | 0 | 0.629 | 1.000 | true | 0 |
| T1 hard seed01 | union-preserving baseline | 35 | 35 | 35 | 0 | 1.000 | 1.000 | false | 13 |
| T2 policy docs seed01 | standard summarizer | 30 | 28 | 28 | 0 | 0.933 | 1.000 | true | 0 |
| T2 policy docs seed01 | union-preserving baseline | 30 | 30 | 30 | 0 | 1.000 | 1.000 | false | 2 |

## 解释

T1 hard seed01 中，standard summarizer 输出 22 个项目，全部正确，但漏掉 13 个 oracle items。union-preserving baseline 保留这 13 个 singleton items 后，recall 从 `0.629` 提升到 `1.000`，precision 没有下降，仍为 `1.000`。

T2 policy docs seed01 中，standard summarizer 输出 28 个项目，漏掉 `CASE-047` 和 `CASE-048`。union-preserving baseline 保留两个 singleton items 后，recall 从 `0.933` 提升到 `1.000`，precision 同样没有下降。

这说明当前两个核心样本里的 missing mass 并不是“所有 agent 都没有找到”，而是“至少一个 agent 找到了，但最终 aggregation policy 没有保留”。这对 Line A 很关键，因为它把问题从 task difficulty 转移到 aggregation-stage evidence loss。

## 对论文的意义

这个结果支持一个更通用、更容易防守的论文主张：在 closed-world discovery 任务中，多 agent workflow 的完成判断依赖聚合策略。高 overlap、高 confidence、以及高 precision 的 final summary 不一定代表完成；如果汇总器默认偏向 consensus 或高精度保守摘要，它可能会把少数派发现的真阳性删除，从而制造 False Convergence。

这个结果也限制了我们不能夸大的部分。它还没有证明 False Convergence 稳定跨 seed 存在，也没有证明所有 summarizer 都会失败。它证明的是：在当前两个样本中，完整答案已经存在于 G3 union 中，而 standard summarizer / consensus 没有把它保留下来。

## 盲评前计划

在确定性 baseline 完成后，原计划是运行真正的盲评 union-preserving summarizer，也就是只给它 G3 aggregation packet 和预注册 prompt，不暴露 oracle、holdout、score summary。若盲评 summarizer 也能恢复这些 singleton true positives，并保持可接受 precision，那么论文的因果链条会更完整。

随后应在更多 seed 上重复同一组聚合策略比较：`majority_consensus`、`standard_summarizer`、`union_preserving_summarizer`、`raw_union`、`holdout_scout`。重点指标应是 `aggregation_loss`、`minority_true_drop_rate`、recall、precision 和 false-stop。

## 进展更新：盲评 union-preserving summarizer 已完成

我们随后运行了真正的盲评 union-preserving summarizer。盲评 summarizer 只接收 G3 aggregation packet 和预注册的 union-preserving 规则，不接收 oracle、holdout、score summary，也不读取任务文件。

结果与确定性 union-preserving baseline 一致：

| 任务 | 聚合策略 | Oracle | Found | TP | FP | Recall | Precision | False-stop | 保留 singleton |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| T1 hard seed01 | blind union-preserving summarizer | 35 | 35 | 35 | 0 | 1.000 | 1.000 | false | 13 |
| T2 policy docs seed01 | blind union-preserving summarizer | 30 | 30 | 30 | 0 | 1.000 | 1.000 | false | 2 |

这一步比确定性 baseline 更强。确定性 baseline 证明“如果保留所有 unique reported items，完整答案在 G3 union 里”；盲评 summarizer 进一步证明“在不看 oracle 的情况下，只要明确要求保留少数派报告，summarizer 也会保留这些缺失项”。因此，当前机制链条更完整：

standard summarizer 和 majority consensus 会把 singleton true positives 当作不确定项丢掉；union-preserving summarizer 会保留它们，并且在这两个样本中没有带来 precision 损失。

这不意味着 union-preserving 策略永远没有代价。当前两个样本的 singleton items 恰好都是真阳性，所以 precision 没有下降。后续必须加入更多 seed 和更多任务族，观察 union-preserving 策略在不同场景下是否会引入 false positives，以及 precision-recall tradeoff 到底有多大。

## 进展更新：T1 seed02 显示 precision cost

我们又在 T1 hard seed02 上运行了 blind standard summarizer 和 blind union-preserving summarizer。这个 seed 是一个有用的阴性/权衡样本：G3 majority consensus 本来已经达到完整 recall，且有一个 agent 报告了 4 个 singleton 额外项。

评分结果如下：

| 任务 | 聚合策略 | Oracle | Found | TP | FP | Recall | Precision | False-stop | singleton 处理 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| T1 hard seed02 | blind standard summarizer | 35 | 35 | 35 | 0 | 1.000 | 1.000 | false | 丢弃 4 个 singleton |
| T1 hard seed02 | blind union-preserving summarizer | 35 | 39 | 35 | 4 | 1.000 | 0.897 | false | 保留 4 个 singleton |

这个结果很重要，因为它说明 union-preserving 不是无条件更好。在 seed01 中，singleton 是 missing true positives；在 seed02 中，singleton 是 false positives。论文因此不应该写成“用 union 就解决问题”，而应该写成“completion 判断需要显式处理少数派证据，并度量 recall-precision tradeoff”。

## 后续下一步

现在盲评 counterfactual 已经完成，下一步应从“单个样本机制验证”进入“跨 seed 稳定性验证”。优先顺序是：先整理已有 seed 中所有 G3 report diversity 非零的样本，再补运行缺失的 G3/G6 seeds；每个 seed 都固定比较 `standard_summarizer`、`majority_consensus`、`blind_union_preserving_summarizer`、`raw_union` 和 `holdout_scout`。这样可以估计这个问题出现的频率，而不是只展示两个漂亮案例。

## 进展更新：T1 seed03 已补齐

T1 hard seed03 已补齐两个新的盲评 G3 agent，并完成 G3 aggregate、standard summarizer 和 union-preserving summarizer 评分。

结果如下：

| 任务 | 聚合策略 | Oracle | Found | TP | FP | Recall | Precision | False-stop | singleton 处理 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| T1 hard seed03 | majority consensus | 35 | 35 | 35 | 0 | 1.000 | 1.000 | false | 丢弃 5 个 singleton |
| T1 hard seed03 | blind standard summarizer | 35 | 35 | 35 | 0 | 1.000 | 1.000 | false | 丢弃 5 个 singleton |
| T1 hard seed03 | blind union-preserving summarizer | 35 | 40 | 35 | 5 | 1.000 | 0.875 | false | 保留 5 个 singleton |

seed03 与 seed02 一样，是 precision-cost 样本。它说明 union-preserving 可以保留更多少数派证据，但当 singleton 是噪声时会带来误报。到这里，T1 的三 seed 图景已经比较清楚：seed01 显示 aggregation-stage false convergence；seed02 和 seed03 显示保留少数派证据的代价。
