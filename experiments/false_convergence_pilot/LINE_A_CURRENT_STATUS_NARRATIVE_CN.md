# Line A 当前状态正文说明

日期：2026-06-07

## 当前判断

Line A 可以继续推进，而且现在已经从“单点机制信号”推进到“两类可复现实验现象”。更准确的判断是：aggregation-stage failure 已经被验证，T2 policy docs 也稳定复现了共同盲点；但如果要写成强论文结论，还需要更多真实任务族，以及更严格的聚合策略对照。

目前最有价值的发现不是“任务被设计得很难，所以模型漏了东西”，而是“多个 agent 的报告中其实已经包含了缺失证据，但最终的 consensus 或 standard summarizer 会把少数派发现丢掉，并且仍然给出高完成信心”。这个发现比继续堆人工约束更适合论文，因为它研究的是现实多 agent workflow 里很常见的最后一步：如何把多个 agent 的输出合成为一个最终答案。

## 现在已经证明了什么

T1 easy repo 是一个有效的阴性对照。它没有产生 False Convergence，G3 union recall 达到 `1.000`，holdout 没有带来额外发现。这说明我们的 pipeline 不是无论什么任务都会报阳性，也能帮助回应“是不是实验设计天然偏向失败”的质疑。

T1 hard repo 的 seed01 给出了严格阳性信号。在这个 seed 中，G3 agent 的平均信心是 `0.853`，平均 pairwise Jaccard 是 `0.752`，consensus recall 只有 `0.629`，但 union recall 和 holdout recall 都是 `1.000`。也就是说，缺失项并不是完全找不到，而是被 consensus-style aggregation 排除在最终输出之外。T1 seed02 和 seed03 则是阴性/权衡样本：consensus 已完整，而 union-preserving 会分别带入 4 个和 5 个误报。因此 T1 证明的是“机制存在且有 precision-recall 权衡”，不是“每个 seed 都稳定阳性”。

T2 policy docs 给出了跨任务族的 near-positive，并且 seed01-03 已经补齐。seed01 的 consensus recall 是 `28/30 = 0.933`，union 和 holdout 都能达到 `30/30 = 1.000`，说明少数派 agent 找到了边界项，但最终 consensus 没有保留。seed02 和 seed03 更像共同盲点：三个 G3 agent 都高度一致地停在 `28/30`，raw union 也无法恢复，但独立 holdout 都能达到 `30/30`。这些结果没有超过预注册的 strict positive 阈值，因为新增缺失项只有两个，低于 `gamma = 0.100`；但它们稳定显示了“高一致不等于完成”。

T2 v2、T3 partitioned、T2 partitioned v3 都是阴性难度探测。它们说明仅仅把文档写得更自然、加更多 case、或者提示“搜索预算有限”，并不稳定制造 False Convergence。这个结论反而很重要：我们不应该继续用越来越定制化的任务约束去追阳性，而应该转向更通用的 aggregation-policy 实验。

最新的 standard summarizer 结果进一步加强了这条线。T1 hard seed01 的 standard summarizer recall 是 `22/35 = 0.629`，precision 是 `1.000`，并且 self-reported confidence 是 `0.860`。T2 policy docs seed01 的 standard summarizer recall 是 `28/30 = 0.933`，precision 是 `1.000`，self-reported confidence 是 `0.900`。这说明 standard summarizer 自然倾向于高精度、保守汇总，行为上接近 majority consensus，而不是 union-preserving audit。

## 现在还没有证明什么

当前结果还不能支持“strict False Convergence 稳定跨 seed 存在”这个强说法。T1 seed01 是严格阳性，但 seed02/03 是阴性或精度权衡样本；T2 seed01-03 都是 near-positive 或共同盲点，但因为缺失量是 `2/30`，没有超过 strict 阈值。因此，如果现在写论文，不能把结论写成“多 agent 系统普遍失败”。

更合适的论文说法是：在 closed-world discovery task 中，completion signal 同时依赖搜索覆盖和聚合策略。agent 之间的高重合和高信心不等于完成；当最终汇总器偏向 consensus 或高精度摘要时，它可能把少数派发现的真阳性当作不确定项丢掉；而当多个 agent 共享同一种搜索盲点时，consensus 会把“共同没看到”误包装成“已经完成”。

## 为什么正文书写是合适的

可以，而且建议用正文书写。实验 memo 可以保留表格和 bullet points 方便核对，但论文草稿和核心论证应该用正文。正文能把机制讲清楚：先说明多 agent workflow 的常见结构，再说明 completion signal 从哪里来，接着展示同一批 reports 在不同 aggregation policy 下产生不同 recall，最后把这个差异解释为 aggregation-stage failure。

正文的写法也能避免给审稿人一种“我们在做 benchmark puzzle”的感觉。我们不是说“我设计了一个特殊任务让模型失败”，而是说“在一个常见系统流程里，最终聚合策略会改变可见证据，并可能把已有的少数派真阳性从最终答案中删除”。

## 是否可以继续推进

可以继续推进，而且应该继续推进。下一步不建议优先改造 T2_partitioned_v3，也不建议继续堆更多人工边界规则。第一优先级应该是做 union-preserving summarizer counterfactual：对同一批 G3 packet，使用一个明确要求保留所有 unique reported items 的 summarizer，然后和 standard summarizer、majority consensus、raw union、holdout scout 对比。

如果 union-preserving summarizer 能恢复 T1 的 13 个 singleton true positives 和 T2 的 2 个 singleton true positives，同时 precision 没有明显崩掉，那么论文的因果故事会非常干净：失败不是因为 agent 完全没找到证据，而是因为最终 aggregation policy 把证据丢掉了。之后再扩展 seed 和任务族，目标就不是“制造更多阳性”，而是估计这种 aggregation loss 在不同场景下何时出现、出现多大、由什么因素预测。

## 下一步最小可执行计划

第一步，固定并预注册两个 summarizer prompt：standard summarizer 和 union-preserving summarizer。这个已经写入 `AGGREGATION_POLICY_PROMPTS.md`。

第二步，在不暴露 oracle、holdout、score summary 的情况下，对 `T1_hard_seed01` 和 `T2_policy_docs_seed01` 的 G3 packet 运行 union-preserving summarizer。

第三步，用同一个 scorer 计算 recall、precision、false-stop、bucket recall，并新增两个 effect size：`aggregation_loss = recall(raw_union) - recall(aggregate)`，以及 `minority_true_drop_rate`。

第四步，如果 counterfactual 成立，就把 Line A 的主实验定义为 aggregation-policy comparison，而不是 task-hardness escalation。随后再补 seed 和现实任务族。

## 进展更新：union-preserving 基线已经成立

我们已经完成了一个确定性的 union-preserving 聚合基线。它只读取已有 G3 itemsets，保留所有 unique reported items，并标出 singleton items；它不是盲评 LLM summarizer，但可以作为一个可复现的因果上限，用来回答“缺失项是否已经存在于 G3 reports 中”。

结果很干净。T1 hard seed01 的 union-preserving baseline 找到 `35/35` 个 oracle items，precision 是 `1.000`，false-stop 为 `false`，并且保留了 standard summarizer 丢掉的 `13` 个 singleton items。T2 policy docs seed01 的 union-preserving baseline 找到 `30/30` 个 oracle items，precision 也是 `1.000`，false-stop 为 `false`，并且保留了 `2` 个 singleton items。

这一步把 Line A 的机制说得更清楚：当前两个关键样本中，完整答案已经存在于 G3 union 里，失败发生在 aggregation stage，而不是因为所有 agent 都没有看到证据。下一步应运行真正的盲评 union-preserving summarizer，并在更多 seed 上重复同一组聚合策略比较。

## 进展更新：盲评 summarizer 也恢复了缺失项

真正的盲评 union-preserving summarizer 已经完成。它只看 G3 aggregation packet，不看 oracle、holdout 或评分结果。T1 hard seed01 的盲评输出找到 `35/35` 个 oracle items，precision 为 `1.000`，false-stop 为 `false`，保留 `13` 个 singleton items。T2 policy docs seed01 的盲评输出找到 `30/30` 个 oracle items，precision 为 `1.000`，false-stop 为 `false`，保留 `2` 个 singleton items。

这说明当前论文机制又前进了一步：不是只有程序化 union baseline 能恢复缺失项，一个按 union-preserving 规则盲评的 summarizer 也能恢复。更通俗地说，之前的失败不是“没人发现答案”，而是“最后负责汇总的人把少数派发现扔掉了”；当我们明确告诉汇总员不要扔少数派发现时，缺失项就回来了。

接下来最重要的不是继续改难任务，而是在更多 seed 和任务族里重复这个对照，观察 union-preserving 是否一直能减少漏报，以及它在更复杂场景下会不会带来误报。

## 进展更新：T1 三个 seed 已形成完整图景

我们已经补齐 T1 hard seed03 的 G3 aggregate，并完成 seed02、seed03 的 blind standard summarizer 与 blind union-preserving summarizer 对照。T1 现在不再只是一个单点阳性案例，而是一个更完整的机制任务族。

T1 seed01 是阳性机制样本：standard summarizer 和 consensus 漏掉真 singleton，union-preserving 恢复它们且没有误报。T1 seed02 和 seed03 是阴性/权衡样本：standard summarizer 完整且无误报，union-preserving 也完整，但分别带入 4 个和 5 个误报。

这个结果让论文论证更诚实：问题不是“union 一定好、consensus 一定坏”，而是“少数派证据需要被显式建模”。有时候 singleton 是漏掉的真阳性，有时候 singleton 是噪声。False Convergence 的风险来自把少数派证据直接丢掉；union-preserving 的风险来自把噪声也一起保留。论文下一步应当研究这个权衡，而不是只追求更多阳性样本。

## 进展更新：T2 三个 seed 已补齐

我们已经补齐 T2 policy docs 的 seed02 和 seed03。两个新 seed 都呈现同一个模式：三个 G3 agent 自报完成、彼此输出完全一致、precision 为 `1.000`，但都漏掉 `CASE-047` 和 `CASE-048`，停在 `28/30`。独立 holdout scout 在 seed02 和 seed03 都恢复到 `30/30`，precision 仍为 `1.000`。

这一步把 A 线稳定性往前推了一格。T2 不是严格阳性，因为 holdout gain 是 `2/30 = 0.067`，低于预设 `gamma = 0.100`；但它稳定证明了“共同盲点”存在：多个 agent 的高度一致和高信心，可能只是说明它们用相似方式漏掉了同一个边界区域。
