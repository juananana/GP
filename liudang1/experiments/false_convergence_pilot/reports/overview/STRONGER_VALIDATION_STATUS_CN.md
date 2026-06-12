# Stronger Validation 当前状态

日期：2026-06-08

## 一句话结论

README 里列的 stronger validation 已经推进了三项：

1. `protocol ablation` 已完成并生成结果表。
2. `cost analysis` 已完成 proxy 版本，并已开始记录 AutoDL blind-agent / summarizer 的 token 与 wall-clock 日志。
3. `真实任务族` 已完成 T4 Click 和 T5 Requests 两个 real-repo audit family 的三 seed blind runs，可作为论文实验结果使用。

## 1. Protocol Ablation

输出文件：

- `PROTOCOL_ABLATION_RESULTS.md`
- `protocol_ablation_cost_results.json`

核心结论：

- 去掉 singleton audit，T1 seed01 / T2 seed01 的 aggregation-loss 真项恢复不了。
- 去掉 common-blindspot trigger，T2 seed02/03 会继续停在 `28/30`。
- 去掉 holdout，系统能发现风险并拒绝认证完成，但不能恢复漏项。
- full protocol 是当前唯一同时覆盖 aggregation loss 和 common blind spot 的变体。

这部分可以直接写进论文方法验证小节。

## 2. Cost Proxy Analysis

输出文件：

- `PROTOCOL_COST_PROXY_RESULTS.md`
- `PROTOCOL_ABLATION_COST_RESULTS_CN.md`

当前成本指标是 proxy，不是真实 API 成本：

```text
audit_actions_proxy = audit_queue_size + holdout_run_units
```

主要结果：

- T1 seed01：14 个 proxy audit actions 恢复 13 个 TP。
- T2 seed01：3 个 proxy audit actions 恢复 2 个 TP。
- T2 seed02/03：每个 seed 1 个 holdout unit 恢复 2 个 TP。
- T1 seed02/03：protocol 避免 raw union 的 4/5 个 FP，但输出 `requires_audit`，不假装已经完成。

论文里应诚实写成 proxy cost，并说明下一步需要记录真实 token、wall-clock、holdout 触发频率。

## 3. 真实任务族 T4 / T5

任务目录：

- `T4_real_repo_click/`

oracle：

- `T4_real_repo_click_deprecation_oracle.json`

任务说明：

- `T4_real_repo_click/TASK.md`

T4 使用真实开源项目 Click：

- upstream: `https://github.com/pallets/click`
- commit: `8a1b1a33d739be05b7e91251e3c0dde77c5e152f`
- oracle size: `149`

任务是 real-repo deprecation surface audit：找源码、测试、文档、changelog 中所有属于当前 deprecated API surface 的 line-level locations。

oracle bucket 分布：

- test coverage: 67
- implementation: 35
- documentation: 13
- warning emission: 12
- parameter behavior: 9
- message formatting: 8
- command behavior: 5

T4 已经完成：

- 固定真实 repo snapshot。
- 生成 `TASK.md`。
- 构建 line-level oracle。
- 生成 smoke itemsets。
- 用现有 scorer 跑通 T4 oracle 格式。
- 完成 `seed01/02/03` blind G3。
- 完成 standard / union-preserving summarizer。
- 完成 protocol scoring、completion certificate、source-aware audit v2。

T4 关键结果：

- standard summarizer 在 `3/3` seeds 中 false stop，recall 为 `0.685-0.745`。
- union-preserving summarizer 将 recall 恢复到 `0.993-1.000`，但 precision 降到约 `0.675`。
- completion certificate v0 对三 seed 都输出 `unsafe_to_stop`。

T5 使用真实开源项目 Requests：

- upstream: `https://github.com/psf/requests`
- commit: `1190afd14fca74292946d62c4c8169880a47ff67`
- oracle size: `304`
- task: TLS certificate verification / CA bundle / client certificate / SSL error handling / tests / docs line-level audit

T5 已经完成：

- 完成 `seed01/02/03` blind G3。
- 完成 standard / union-preserving summarizer。
- 完成 protocol scoring、completion certificate、source-aware audit v2。

T5 关键结果：

- consensus recall 均值 `0.685`。
- standard summarizer recall 均值 `0.546`，并在 `3/3` seeds 中 false stop。
- raw union recall 均值 `0.844`，比 consensus 更好但仍低于完成阈值。
- completion certificate v0 对三 seed 都输出 `unsafe_to_stop`。

重要提醒：

`T4_real_repo_click_seed01_smoke_*` 是 scorer compatibility smoke test，由 oracle 生成，不能作为论文实验结果。

## 下一步

现在不需要重复跑 T4/T5 blind seeds。更自然的下一步是：

1. 把 T4/T5 的结果整理进 AAAI 论文主实验叙事。
2. 将 source-aware audit v2 从 deterministic upper bound 推进到 blind source-partitioned / bucket-targeted audit。
3. 补 prompt-diverse / model-heterogeneous 对照，验证降低 agent 相关性是否减少共同盲点。
4. 扩展更多真实仓库和任务类型，检验 false stop 率是否跨任务稳定。
