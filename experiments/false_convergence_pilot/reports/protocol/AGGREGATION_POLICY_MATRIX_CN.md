# A 线聚合策略对照矩阵

日期：2026-06-07

## 一句话状态

当前 A 线已经从“发现一个阳性案例”推进到“看清楚聚合策略的作用”。同一批 G3 报告，在不同汇总规则下会给出不同结果：standard summarizer / majority consensus 更保守，可能漏掉少数派真阳性；union-preserving summarizer 更保留证据，可能恢复漏项，但在某些 seed 中也会带入 singleton 误报。

## 当前已评分矩阵

| 任务/seed | 聚合策略 | Found | TP | FP | Recall | Precision | False-stop | 解释 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| T1 hard seed01 | majority consensus | 22 | 22 | 0 | 0.629 | 1.000 | true | 严格阳性，漏掉 13 个真 singleton |
| T1 hard seed01 | standard summarizer | 22 | 22 | 0 | 0.629 | 1.000 | true | 复现 consensus 丢失 |
| T1 hard seed01 | blind union-preserving | 35 | 35 | 0 | 1.000 | 1.000 | false | 恢复 13 个 singleton，且无误报 |
| T1 hard seed01 | raw union | 35 | 35 | 0 | 1.000 | 1.000 | false | 说明完整答案已在 G3 reports 中 |
| T1 hard seed01 | holdout scout | 35 | 35 | 0 | 1.000 | 1.000 | false | 独立 scout 也能恢复缺失项 |
| T1 hard seed02 | majority consensus | 35 | 35 | 0 | 1.000 | 1.000 | false | 阴性 seed，consensus 已完整 |
| T1 hard seed02 | standard summarizer | 35 | 35 | 0 | 1.000 | 1.000 | false | 高精度汇总正确丢弃 4 个 singleton |
| T1 hard seed02 | blind union-preserving | 39 | 35 | 4 | 1.000 | 0.897 | false | 保留 singleton 带来 4 个误报 |
| T1 hard seed02 | raw union | 39 | 35 | 4 | 1.000 | 0.897 | false | union-preserving 的 precision cost 被量化 |
| T1 hard seed03 | majority consensus | 35 | 35 | 0 | 1.000 | 1.000 | false | 阴性 seed，consensus 已完整 |
| T1 hard seed03 | standard summarizer | 35 | 35 | 0 | 1.000 | 1.000 | false | 高精度汇总正确丢弃 5 个 singleton |
| T1 hard seed03 | blind union-preserving | 40 | 35 | 5 | 1.000 | 0.875 | false | 保留 singleton 带来 5 个误报 |
| T1 hard seed03 | raw union | 40 | 35 | 5 | 1.000 | 0.875 | false | union-preserving 的 precision cost 再次出现 |
| T2 policy docs seed01 | majority consensus | 28 | 28 | 0 | 0.933 | 1.000 | true | near-positive，漏掉 2 个真 singleton |
| T2 policy docs seed01 | standard summarizer | 28 | 28 | 0 | 0.933 | 1.000 | true | 复现 consensus 丢失 |
| T2 policy docs seed01 | blind union-preserving | 30 | 30 | 0 | 1.000 | 1.000 | false | 恢复 2 个 singleton，且无误报 |
| T2 policy docs seed01 | raw union | 30 | 30 | 0 | 1.000 | 1.000 | false | 完整答案已在 G3 reports 中 |
| T2 policy docs seed01 | holdout scout | 30 | 30 | 0 | 1.000 | 1.000 | false | 独立 scout 也能恢复缺失项 |
| T2 policy docs seed02 | majority consensus | 28 | 28 | 0 | 0.933 | 1.000 | true | 三个 G3 完全一致地漏掉 `CASE-047/048` |
| T2 policy docs seed02 | raw union | 28 | 28 | 0 | 0.933 | 1.000 | true | union 也无法恢复，说明漏项不在 G3 reports 中 |
| T2 policy docs seed02 | holdout scout | 30 | 30 | 0 | 1.000 | 1.000 | false | 独立复查恢复同两个边界项 |
| T2 policy docs seed03 | majority consensus | 28 | 28 | 0 | 0.933 | 1.000 | true | 三个 G3 再次完全一致地漏掉 `CASE-047/048` |
| T2 policy docs seed03 | raw union | 28 | 28 | 0 | 0.933 | 1.000 | true | union 也无法恢复，复现共同盲点 |
| T2 policy docs seed03 | holdout scout | 30 | 30 | 0 | 1.000 | 1.000 | false | 独立复查再次恢复同两个边界项 |

## 目前能说什么

现在可以比较稳地说：False Convergence 至少有两类机制。一类是 aggregation loss：答案已经出现在少数派 G3 reports 里，但 standard summarizer 和 consensus 会把它丢掉，例如 T1 seed01 和 T2 seed01。另一类是 common blind spot：多个 G3 agent 彼此高度一致，也都自信完成，但它们一起漏掉同一批边界项，例如 T2 seed02 和 seed03。

这让论文主张更成熟：我们不是说 union-preserving 永远更好，而是说 completion 不能只看 consensus 和 confidence。真正应该研究的是 aggregation policy 的 recall-precision tradeoff，以及什么时候 singleton 是 missing mass，什么时候 singleton 是 noise。

## 目前还缺什么

T1 的 seed01-03 已经形成完整 G3 aggregate，并完成 standard / union-preserving summarizer 对照。T1 目前不是“稳定阳性”任务族，而是一个机制任务族：seed01 展示 aggregation-stage false convergence，seed02 和 seed03 展示 union-preserving 的 precision cost。

T2 的 seed01-03 现在已经补齐 G3/G6 对照。它没有达到 strict positive 阈值，因为 holdout gain 都是 `2/30 = 0.067`，低于预设 `gamma = 0.100`；但它稳定复现了高一致、高信心下的共同盲点。要进一步提高论文级说服力，下一步更应该补一个更真实的第二任务族，或者扩大 oracle 规模，让类似 2 个边界漏项不会被阈值过度压低。

## 下一步判断标准

T1 的当前结论是“聚合机制存在，但不稳定”：seed01 阳性，seed02 和 seed03 是阴性或精度权衡样本。T2 的当前结论是“共同盲点稳定存在”：seed01 有少数派真项可被 union 恢复，seed02/03 则是所有 G3 都漏同两个边界项，只有独立 holdout 能恢复。

无论哪种结果，都有论文价值。阳性 seed 证明风险存在，阴性 seed 说明风险不是自动发生；两者合起来可以支撑更诚实的系统论文。
