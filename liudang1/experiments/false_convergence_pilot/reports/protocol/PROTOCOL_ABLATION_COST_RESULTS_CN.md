# Protocol Ablation 与成本代理分析

日期：2026-06-08

## 一句话结论

ablation 结果支持当前方法设计：singleton audit 负责恢复 aggregation loss，common-blindspot trigger 负责发现高一致下的共同盲点，holdout 负责把风险从“待审计”推进到“已验证”。

## Ablation 结论

- 去掉 singleton audit：T1 seed01 / T2 seed01 的少数派真项无法恢复。
- 去掉 common-blindspot trigger：T2 seed02/03 仍会停在 `28/30`。
- 去掉 holdout：系统能发现风险并输出 `requires_audit`，但不能恢复漏项。
- full protocol：在已有 holdout 的 case 中同时覆盖 aggregation loss 和 common blind spot；在 raw union 会带来误报的 case 中保持更保守。

## 成本说明

当前日志已有 T4 summarizer 的 token / wall-clock 记录；协议级别仍先报告 proxy cost：

```text
audit_actions_proxy = audit_queue_size + holdout_run_units
```

| case | full protocol status | audit queue | holdout used | recovered TP | avoided FP vs raw union |
| --- | --- | ---: | --- | ---: | ---: |
| T1_hard_seed01 | verified_after_holdout | 13 | true | 13 | 0 |
| T1_hard_seed02 | requires_audit_holdout_missing | 4 | false | 0 | 4 |
| T1_hard_seed03 | requires_audit_holdout_missing | 5 | false | 0 | 5 |
| T2_policy_docs_seed01 | verified_after_holdout | 2 | true | 2 | 0 |
| T2_policy_docs_seed02 | verified_after_holdout | 0 | true | 2 | 0 |
| T2_policy_docs_seed03 | verified_after_holdout | 0 | true | 2 | 0 |
| T4_real_repo_click_seed01_blind | verified_after_holdout | 56 | true | 6 | 44 |
| T4_real_repo_click_seed02_blind | verified_after_holdout | 98 | true | 7 | 55 |
| T4_real_repo_click_seed03_blind | verified_after_holdout | 102 | true | 8 | 44 |
| T5_real_repo_requests_tls_seed01_blind | verified_after_holdout | 97 | true | 30 | 33 |
| T5_real_repo_requests_tls_seed02_blind | verified_after_holdout | 97 | true | 22 | 37 |
| T5_real_repo_requests_tls_seed03_blind | verified_after_holdout | 95 | true | 31 | 27 |

## 论文里怎么写

这部分可以作为方法有效性的 stronger validation：不是只展示 full protocol 有效，而是证明每个组件分别对应一种失败机制。需要诚实说明，T4 seed02/03 中当前 holdout 召回仍不足，所以 protocol 更强的是风险暴露与保守停止，稳定恢复还需要更强审计策略。
