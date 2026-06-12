# Line A 当前证据总结

日期：2026-06-07

## 当前结论

Line A 的机制链条已经基本打通。现在更准确的判断是：aggregation-stage failure 已经被验证，T2 的共同盲点也开始呈现跨 seed 稳定性；但如果要写成强论文结论，还需要避免过度声称“strict false convergence 稳定出现”。

更通俗地说：我们已经证明了“最后汇总这一步可能出问题”。有些情况下，少数派 agent 找到的东西其实是真的，但 standard summarizer 或 majority consensus 会把它丢掉；换成 union-preserving 汇总规则后，这些漏项能回来。与此同时，我们也看到 union-preserving 不是万能药：在另一些 seed 中，少数派 singleton 是误报，保留它们会降低 precision。

所以当前最稳的论文主张不是“multi-agent 一定失败”，也不是“union 一定更好”，而是：

> 多 agent workflow 的 completion signal 依赖搜索覆盖和聚合策略。少数派发现既可能是 missing mass，也可能是 noise；多个 agent 的高一致也可能只是共同漏掉同一个边界区域。如果最终系统只看 consensus 和 confidence，就可能把真实缺失项误当成已经完成，从而产生 False Convergence。

## 已完成的关键实验

### T1 hard repo：三 seed 已补齐

T1 hard repo 现在已经有 seed01、seed02、seed03 的完整 G3 aggregate，并完成 standard summarizer 与 union-preserving summarizer 对照。

seed01 是阳性机制样本。majority consensus 和 standard summarizer 都只保留 `22/35` 个真项，recall 为 `0.629`，但 raw union、holdout scout、blind union-preserving summarizer 都能达到 `35/35`，precision 仍为 `1.000`。这说明缺失项已经在 G3 reports 里，只是被最终聚合策略丢掉了。

seed02 是阴性/权衡样本。majority consensus 和 standard summarizer 都达到 `35/35`，precision 为 `1.000`。blind union-preserving summarizer 也达到 `35/35` recall，但保留了 4 个 singleton 误报，precision 降到 `0.897`。

seed03 也是阴性/权衡样本。majority consensus 和 standard summarizer 都达到 `35/35`，precision 为 `1.000`。blind union-preserving summarizer 达到 `35/35` recall，但保留了 5 个 singleton 误报，precision 降到 `0.875`。

T1 的结论是：False Convergence 机制存在，但不是稳定跨 seed 自动出现。更准确地说，T1 展示了少数派 evidence handling 的两面：seed01 中 singleton 是真漏项，seed02/03 中 singleton 是噪声。

### T2 policy docs：三 seed 已补齐，稳定复现共同盲点

T2 policy docs seed01 是第二任务族中的 near-positive。majority consensus 和 standard summarizer 都是 `28/30`，precision 为 `1.000`，漏掉 `CASE-047` 和 `CASE-048`。raw union、holdout scout、blind union-preserving summarizer 都达到 `30/30`，precision 为 `1.000`。这说明在 seed01 中，缺失项已经存在于少数派 G3 reports 里，只是被 consensus / standard summarizer 丢掉了。

T2 policy docs seed02 和 seed03 呈现另一种稳定形状。三个 G3 agent 都自报完成，precision 都是 `1.000`，但全部停在 `28/30`，并且三者的 pairwise Jaccard 都是 `1.000`。换句话说，它们不是互相补漏，而是高度一致地漏掉同两个边界项：`CASE-047` 和 `CASE-048`。raw union 也只能得到 `28/30`，因为缺失项根本没有出现在 G3 reports 中；独立 holdout scout 则能恢复到 `30/30`，precision 仍为 `1.000`。

这个结果很重要，因为它把论文机制从单纯的“聚合丢少数派真项”扩展为“completion signal 的双重风险”。T2 seed01 证明聚合可能丢掉已经被发现的真项；T2 seed02/03 证明即使 agent 之间完全一致，也可能只是共同漏掉同一个边界区域。

## 当前证据能支持什么

当前可以支持机制级主张：

- Consensus 和 standard summarizer 可以丢掉少数派真阳性。
- High confidence 和 high overlap 不能直接当作完成证明。
- 共同盲点可以跨 seed 稳定复现：T2 seed02/03 中，三个 G3 完全一致地漏掉同两个边界项。
- Union-preserving 聚合可以恢复 missing mass，但可能带来 false positives。
- False Convergence 更适合被表述为 aggregation-stage risk，而不是 task difficulty 或 universal multi-agent failure。
- 阴性 seed 对论文有价值，因为它们显示这个现象不是自动发生，也帮助我们估计 precision-recall tradeoff。

## 当前证据还不能支持什么

当前还不能支持过强的稳定性主张：

- 不能说 strict aggregation-stage False Convergence 已经稳定跨 seed 出现。
- 不能说两个任务族都已经达到 strict positive。
- 不能说 union-preserving 是总是更好的生产策略。
- 不能说所有 multi-agent workflows 都会失败。

## A 线还差什么

如果目标是“机制论文”，A 线已经接近可写：我们有一个严格阳性代码 seed，一个 near-positive 文档 seed，两个 T1 阴性/权衡 seed，两个 T2 稳定共同盲点 seed，以及清楚的 aggregation-policy 对照。

如果目标是“论文级稳定证明”，还需要继续补：

- 新增一个更真实的第二任务族，例如真实 repo/doc snapshot，并独立构建 oracle。
- 或者扩大 T2 风格任务的 oracle 规模，让 `2/30` 这种边界漏项不会因为 `gamma = 0.100` 被判成非 strict。
- 对每个新增 seed 固定比较 `majority_consensus`、`standard_summarizer`、`blind_union_preserving_summarizer`、`raw_union` 和 `holdout_scout`。
- 报告 `aggregation_loss`、`minority_true_drop_rate`、recall、precision、false-stop，而不是只报阳性案例。

## 建议论文定位

建议把论文定位为：

> Consensus is not completion.

更完整的表述是：

> In closed-world agent-completion tasks, aggregation policy determines whether minority-discovered evidence is treated as missing mass or noise. Consensus-style and summary-style workflows can create false completion signals by discarding minority true positives, while union-preserving workflows expose a recall-precision tradeoff.

这条主张比“模型会漏东西”更强，也比“union 解决问题”更稳。它把论文从单纯 benchmark 失败，提升成多 agent 系统设计中的 completion-signal 问题。
