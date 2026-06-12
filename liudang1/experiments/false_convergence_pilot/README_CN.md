# False Convergence Pilot 实验目录

日期：2026-06-08

## 当前一句话结论

我们现在已经把问题从“可能存在”推进到“有稳定证据”：在 T4 Click 真实仓库 line-level deprecation audit 上，AutoDL standard summarizer 连续 3 个 blind seed 都给出高置信完成，但 recall 只有 `0.685-0.745`；union-preserving summarizer 连续 3 个 seed 把 recall 恢复到 `0.993-1.000`，说明大量漏项其实已经在 agent reports 的 union 里，只是在最终汇总时被剪掉。

同时，第二真实仓库任务族 T5：Requests TLS/certificate audit 已完成 `seed01/02/03` 三个真实 blind seeds。T5 的模式比 T4 更难：raw union 能从 consensus 的平均 recall `0.685` 提升到 `0.844`，但仍低于完成阈值；standard summarizer 平均 recall 只有 `0.546`，并在 `3/3` seeds 中 false stop。

## 我们已经证明了什么

- `问题存在`：consensus / high-precision summarization 不能当作 closed-world discovery 的完成证书。
- `机制存在`：已经看到 aggregation loss、common blind spot、aggregation-stage false stop 三类机制。
- `真实仓库稳定性`：T4 的 standard summarizer false stop 是 `3/3` 稳定出现；T5 在第二真实仓库上也出现 `3/3` false stop，但机制更偏“搜索覆盖不足 + 汇总压缩”的混合风险。
- `union 不是最终解`：union-preserving 能恢复 recall，但 precision 从约 `0.997` 降到约 `0.675`，所以应该保留少数派证据进入 audit queue，而不是直接全收。
- `更强 audit 有希望`：source-aware candidate filter v2 在 T4 三 seed 上把候选池从低 precision 恢复到接近或达到 `1.000` recall / `1.000` precision，但这是 audit-policy 原型，不是 blind LLM 结果。

## 目录结构

| path | 内容 |
| --- | --- |
| `results/` | oracle、blind itemsets、score summary。 |
| `protocol_outputs/` | protocol / certificate / ablation / audit JSON 输出。 |
| `reports/overview/` | 当前阶段、dashboard、总览报告。 |
| `reports/task_summaries/` | T1/T2/T4 单任务或任务族总结。 |
| `reports/protocol/` | aggregation policy、protocol、certificate、ablation、source-aware audit 报告。 |
| `reports/planning/` | 后续实验计划和 run manifest。 |
| `summarizer_inputs/` | standard / union-preserving summarizer 聚合输入包。 |
| `summarizer_outputs/` | summarizer 输出、raw response、summarizer score summary。 |
| `run_cost_logs/` | AutoDL summarizer / blind-agent token 与 wall-clock 成本日志。 |
| `incidence_logs/` | item-level incidence log。 |
| `T4_real_repo_click/` | T4 Click 真实仓库任务目录。 |
| `T4_real_repo_click_blind_runs/` | T4 blind prompt 与 independent run 输出。 |
| `T5_real_repo_requests_tls/` | T5 Requests TLS/certificate 真实仓库任务目录。 |
| `T5_real_repo_requests_tls_blind_runs/` | T5 blind prompt 与 independent run 输出。 |
| `tools/` | 构建、评分、协议、证书、audit、pipeline 脚本。 |

## 常用入口

- 总览 dashboard：`reports/overview/EXPERIMENT_DASHBOARD_CN.md`
- 论文可用结果表：`reports/overview/PAPER_READY_EXPERIMENT_RESULTS_CN.md`
- 论文表格 CSV：`reports/paper_tables/`
- T4 三 seed 稳定性：`reports/task_summaries/T4_AUTODL_SUMMARIZER_STABILITY_CN.md`
- T5 Requests TLS 管线状态：`reports/task_summaries/T5_REQUESTS_TLS_PIPELINE_STATUS_CN.md`
- source-aware audit v2：`reports/protocol/SOURCE_AWARE_AUDIT_V2_RESULTS.md`
- evidence-preserving protocol：`reports/protocol/EVIDENCE_PRESERVING_PROTOCOL_RESULTS.md`
- completion certificate v0：`reports/protocol/COMPLETION_CERTIFICATE_V0_RESULTS_CN.md`
- AAAI 草稿：`../../papers/aaai_false_convergence/main.tex`

## 关键命令

从仓库根目录运行：

```powershell
python experiments\false_convergence_pilot\tools\run_evidence_preserving_protocol.py
python experiments\false_convergence_pilot\tools\run_protocol_ablation_and_cost.py
python experiments\false_convergence_pilot\tools\build_incidence_logs.py
python experiments\false_convergence_pilot\tools\run_completion_certificate_v0.py
python experiments\false_convergence_pilot\tools\run_source_aware_audit_v2.py
python experiments\false_convergence_pilot\tools\build_experiment_dashboard.py
python experiments\false_convergence_pilot\tools\build_paper_tables.py
```

T5 AutoDL 盲跑管线：

```powershell
$env:AUTODL_ART_API_KEY="你的 key，只放当前 shell，不写文件"
python experiments\false_convergence_pilot\tools\run_t5_autodl_pipeline.py --seed seed01
```

如果只想检查命令不调用 API：

```powershell
python experiments\false_convergence_pilot\tools\run_t5_autodl_pipeline.py --dry-run --skip-agents --skip-summarizers
```

## 论文里的稳妥表述

建议写：

> We show that consensus and high-confidence summarization are insufficient completion certificates for closed-world multi-agent discovery. The failure appears through aggregation loss, common blind spots, and real-repo aggregation-stage false stops.

不建议写：

> We fully solve false convergence.

更准确的中文理解是：我们已经证明问题稳定存在，并证明简单 consensus / summarizer 会把“高 precision 但不完整”的答案误报为完成；目前解决方案应定位为 coverage-risk certificate + audited evidence preservation，还不是最终闭环。

## 下一步

1. 把 T4/T5 的实验结果和限制同步进 AAAI `main.tex`，形成可读的实验主线。
2. 将 source-aware audit v2 从 deterministic upper bound 推进到 blind source-partitioned / bucket-targeted audit。
3. 补 prompt-diverse G3 vs homogeneous G3，验证降低 agent 相关性是否减少共同盲点。
4. 扩展更多真实仓库和任务类型，检验 false stop 率是否跨任务稳定。
