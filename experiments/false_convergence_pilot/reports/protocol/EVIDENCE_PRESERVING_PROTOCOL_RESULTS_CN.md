# Evidence-Preserving Completion Protocol 结果总结

日期：2026-06-08

## 一句话结论

我们完成了一个“最漂亮的实验”：在同一批 T1/T2 证据上，对比 `majority consensus`、`standard summarizer`、`raw union`、`union-preserving summarizer`、`holdout scout` 和新的 `evidence-preserving completion protocol`。

结果很干净：新 protocol 在 aggregation loss 样本中恢复漏项，在 common blind spot 样本中触发独立复查，并且在 singleton 是误报的 T1 seed02/03 中没有把误报直接放进最终答案。

## 方法定义

这个 protocol 不把“多数一致”直接当完成，也不把“所有 singleton”直接当最终答案。它采用三步：

1. 保守最终集先采用 consensus items。
2. 所有 singleton items 进入 audit queue，而不是被 summarizer 直接删除。
3. 如果出现高一致、高信心并且任务有边界解析风险，则触发 boundary-focused holdout，专门检查共同盲点。

重要的是：protocol 决策阶段不使用 oracle。oracle 只用于最后评分。

## 关键结果

| case | 机制类型 | consensus | raw union | holdout | protocol | protocol 状态 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| T1 hard seed01 | aggregation loss | 22/35, FP 0 | 35/35, FP 0 | 35/35, FP 0 | 35/35, FP 0 | verified_after_holdout |
| T1 hard seed02 | precision-cost control | 35/35, FP 0 | 35/35, FP 4 | n/a | 35/35, FP 0 | requires_audit |
| T1 hard seed03 | precision-cost control | 35/35, FP 0 | 35/35, FP 5 | n/a | 35/35, FP 0 | requires_audit |
| T2 policy docs seed01 | aggregation loss | 28/30, FP 0 | 30/30, FP 0 | 30/30, FP 0 | 30/30, FP 0 | verified_after_holdout |
| T2 policy docs seed02 | common blind spot | 28/30, FP 0 | 28/30, FP 0 | 30/30, FP 0 | 30/30, FP 0 | verified_after_holdout |
| T2 policy docs seed03 | common blind spot | 28/30, FP 0 | 28/30, FP 0 | 30/30, FP 0 | 30/30, FP 0 | verified_after_holdout |

## 这说明什么

第一，`majority consensus` 和 `standard summarizer` 的问题很清楚：它们偏保守，precision 高，但会漏掉少数派真项。T1 seed01 和 T2 seed01 都是这个形状。

第二，`raw union` 和 `union-preserving summarizer` 不是万能解。它们能恢复 T1 seed01/T2 seed01 的少数派真项，但在 T1 seed02/03 中会带入误报；在 T2 seed02/03 中也救不了共同盲点，因为漏项根本没有出现在 G3 reports 里。

第三，`evidence-preserving protocol` 更像一个论文里的缓解方法。它不是简单地“多保留”，而是把证据分层：

- consensus items 可以进入保守 final set。
- singleton items 不能直接丢，也不能直接信，而是进入 audit queue。
- 高一致高信心时，如果任务有 alias、registry、边界解析等风险，要触发独立 holdout。

## 对两类机制的解决效果

### 对 aggregation loss

在 T1 seed01 和 T2 seed01 中，漏项已经出现在某个 G3 agent 的输出里。protocol 通过 singleton audit 把这些项恢复回来：

- T1 seed01：恢复 13 个 singleton true positives。
- T2 seed01：恢复 2 个 singleton true positives。

这解决的是“证据已经存在，但最终汇总丢掉了”的问题。

### 对 common blind spot

在 T2 seed02/03 中，三个 G3 agent 完全一致地漏掉 `CASE-047/048`，raw union 也只有 `28/30`。protocol 在高一致、高信心、边界解析任务中触发 holdout：

- T2 seed02：holdout 新增 2 个真项。
- T2 seed03：holdout 新增 2 个真项。

这解决的是“大家一起没看到，所以 consensus 看起来很稳”的问题。

### 对 singleton noise

在 T1 seed02/03 中，raw union 和 union-preserving summarizer 都完整覆盖 oracle，但分别带入 4 个和 5 个误报。protocol 没有直接采纳这些 singleton，而是标记为 `requires_audit`：

- T1 seed02：最终保守集仍是 `35/35, FP 0`，4 个 singleton 留待审计。
- T1 seed03：最终保守集仍是 `35/35, FP 0`，5 个 singleton 留待审计。

这说明 protocol 不是盲目提高 recall，而是在 recall 和 precision 之间加了一个审计层。

## 论文里的方法表述

可以把方法命名为：

> Evidence-Preserving Completion Protocol

中文可以叫：

> 证据保留式完成协议

论文表述建议：

> Instead of treating consensus as completion, the protocol separates finalization from evidence preservation. Consensus-supported items form a conservative final set, singleton evidence is retained for audit, and high-agreement/high-confidence states trigger boundary-focused holdout when the task contains latent resolution risks.

更通俗地说：

> 不要让系统直接说“大家差不多都这么说，所以完成了”。应该先问：有没有少数派证据被丢掉？有没有大家一起漏掉的边界区域？

## 当前局限

这个实验是一个强力 proof-of-concept，但还不是最终论文结论：

- 当前 protocol 使用已有 holdout 作为审计器，下一步需要把 holdout 触发和执行写成更标准化的实验流程。
- T1 seed02/03 没有真实 holdout，因此 protocol 正确地输出 `requires_audit`，而不是假装已经彻底解决。
- 目前 case 数量还少，适合作为机制和方法展示；如果要增强论文说服力，仍建议补一个更真实的第二任务族。

## 结论

这一步让论文从“我们发现了一个问题”推进到“我们能提出一个有针对性的缓解框架”。

最稳的论文贡献可以写成三点：

1. 定义 False Convergence：高一致、高信心、多 agent 完成信号可能掩盖漏项。
2. 区分两类机制：aggregation loss 和 common blind spot。
3. 提出 Evidence-Preserving Completion Protocol：保留少数派证据、触发边界复查，并避免 raw union 的误报问题。
