# T4 Aggregation Policy Comparison

日期：2026-06-08

## 一句话结论

T4 已从真实仓库盲评推进到聚合策略对照，并且 AutoDL 的真实 LLM summarizer 给出了一个很强的聚合阶段 false-stop 信号：standard summarizer 高信心自报完成，但只保留 105 个 items，recall 只有 `0.698`；union-preserving summarizer 恢复到 `0.993` recall，但 precision 降到 `0.744`。evidence-preserving protocol 在召回和精度之间取得更稳的折中。

| policy | status | found | TP | FP | recall | precision |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| majority_consensus | complete_by_consensus | 143 | 142 | 1 | 0.953 | 0.993 |
| deterministic_consensus | deterministic_baseline | 143 | 142 | 1 | 0.953 | 0.993 |
| AutoDL standard summarizer | blind_llm_summary | 105 | 104 | 1 | 0.698 | 0.990 |
| raw_union | complete_by_union | 199 | 148 | 51 | 0.993 | 0.744 |
| deterministic_union_preserving | deterministic_baseline | 199 | 148 | 51 | 0.993 | 0.744 |
| AutoDL union-preserving summarizer | blind_llm_summary | 199 | 148 | 51 | 0.993 | 0.744 |
| holdout_scout | independent_audit | 149 | 140 | 9 | 0.940 | 0.940 |
| evidence_preserving_protocol | verified_after_holdout | 155 | 148 | 7 | 0.993 | 0.955 |

## 论文中怎么解释

- T4 不是 strict False Convergence 阳性，因为 consensus recall 是 `0.953`，略高于 `theta = 0.95`。
- 但 T4 的 AutoDL standard summarizer 是很强的 aggregation-stage false stop：它给出 confidence `0.930`，却只有 recall `0.698`。
- 但 T4 是真实任务族上的强 precision-recall tradeoff 证据：raw union 相比 consensus 只多恢复 6 个 TP，却引入 50 个额外 FP。
- evidence-preserving protocol 达到与 union 接近的 recall，同时把 FP 从 51 降到 7。
- 因此 T4 支持我们从“问题存在”推进到“为什么需要 coverage-risk certificate / audit controller”。

## AutoDL 成本记录

| summarizer | model | input tokens | output tokens | wall-clock seconds |
| --- | --- | ---: | ---: | ---: |
| standard | gpt-5.3-codex | 4754 | 2170 | 16.053 |
| union-preserving | gpt-5.3-codex | 4770 | 4476 | 30.305 |

## 对当前阶段的判断

当前已经不是单纯的问题验证阶段，而是进入方法评估与扩量测试阶段：

- T1/T2 已经提供机制验证：aggregation loss 与 common blind spot。
- T4 提供真实任务族验证：precision-recall boundary 与审计控制价值。
- completion certificate v0 提供 stopping/certification 方向：它保守，但没有 false certification。

下一步最该加速的是 T4 seed02/03 和 prompt-diverse G3，而不是继续构造更难的合成任务。
