# 下一批实验 Run Manifest

日期：2026-06-08

## 原则

- 盲评 agent 只能访问对应任务目录，不能访问 oracle、score summary、itemsets、summarizer outputs、incidence logs。
- 每个 run 必须输出统一 JSON：`run_id`、`self_reported_completion`、`self_reported_confidence`、`items`。
- 新增 run 必须记录真实成本：开始时间、结束时间、模型名、输入 token、输出 token、工具调用次数。
- 评分只在 run 完成后由 scorer 离线执行，oracle 不参与 agent 决策。

## 第一优先级：T4 Click real-repo blind validation

任务目录：

```text
experiments/false_convergence_pilot/T4_real_repo_click/
```

禁止访问：

```text
experiments/false_convergence_pilot/results/T4_real_repo_click_deprecation_oracle.json
experiments/false_convergence_pilot/results/T4_real_repo_click_seed01_smoke_itemsets.json
experiments/false_convergence_pilot/results/T4_real_repo_click_seed01_smoke_score_summary.*
experiments/false_convergence_pilot/incidence_logs/
experiments/false_convergence_pilot/results/*score_summary*
```

需要跑：

| run_id | group | role | output path |
| --- | --- | --- | --- |
| T4_G3_seed01_agent01 | G3 | blind scout | `T4_real_repo_click_seed01_blind_itemsets.json` |
| T4_G3_seed01_agent02 | G3 | blind scout | `T4_real_repo_click_seed01_blind_itemsets.json` |
| T4_G3_seed01_agent03 | G3 | blind scout | `T4_real_repo_click_seed01_blind_itemsets.json` |
| T4_G6_holdout_seed01 | G6 | independent holdout | `T4_real_repo_click_seed01_blind_itemsets.json` |

完成后优先运行一键后处理脚本：

```powershell
python experiments\false_convergence_pilot\tools\run_t4_blind_postprocess.py
```

这个脚本会自动合并四个独立 JSON、评分、重建 incidence log、重跑 completion certificate v0，并刷新 dashboard。

如果需要手工执行，则先合并：

```powershell
python experiments\false_convergence_pilot\tools\merge_blind_itemsets.py `
  --task-id T4_real_repo_click_deprecation `
  --oracle-size 149 `
  --inputs `
    experiments\false_convergence_pilot\T4_real_repo_click_blind_runs\T4_G3_seed01_agent01.json `
    experiments\false_convergence_pilot\T4_real_repo_click_blind_runs\T4_G3_seed01_agent02.json `
    experiments\false_convergence_pilot\T4_real_repo_click_blind_runs\T4_G3_seed01_agent03.json `
    experiments\false_convergence_pilot\T4_real_repo_click_blind_runs\T4_G6_holdout_seed01.json `
  --out experiments\false_convergence_pilot\results\T4_real_repo_click_seed01_blind_itemsets.json
```

再评分：

```powershell
python experiments\false_convergence_pilot\tools\score_itemsets.py `
  --oracle experiments\false_convergence_pilot\results\T4_real_repo_click_deprecation_oracle.json `
  --runs experiments\false_convergence_pilot\results\T4_real_repo_click_seed01_blind_itemsets.json `
  --out-json experiments\false_convergence_pilot\results\T4_real_repo_click_seed01_blind_score_summary.json `
  --out-md experiments\false_convergence_pilot\results\T4_real_repo_click_seed01_blind_score_summary.md
```

然后把 T4 blind case 加入：

- `build_incidence_logs.py`：已接入。
- `run_completion_certificate_v0.py`：已接入。
- `run_evidence_preserving_protocol.py`：待 T4 blind 出结果后接入 protocol comparison。
- `run_protocol_ablation_and_cost.py`：待 T4 blind 出结果后接入 ablation/cost comparison。

## 第二优先级：T4 aggregation policy comparison

输入：

```text
T4_real_repo_click_seed01_blind_itemsets.json
```

需要两个 summarizer：

- standard summarizer：偏自然最终报告，不强调保留所有 minority items。
- union-preserving summarizer：明确保留所有 unique reported items，并标注 singleton evidence。

输出建议：

```text
summarizer_outputs/T4_real_repo_click_seed01_sum_standard_blind_itemsets.json
summarizer_outputs/T4_real_repo_click_seed01_sum_union_preserving_blind_itemsets.json
```

评价重点：

- standard 是否丢 minority true items。
- union-preserving 是否带入 singleton false positives。
- protocol/certificate 是否能把 singleton 从“最终答案”转成“审计队列”。

## 第三优先级：T1/T2 seed 扩量

目标：

- T1 hard：补 `seed04`、`seed05`。
- T2 policy docs：补 `seed04`、`seed05`。

每个 seed：

| run | 数量 |
| --- | ---: |
| homogeneous G3 | 3 |
| holdout G6 | 1 |
| standard summarizer | 1 |
| union-preserving summarizer | 1 |

新增命名：

```text
T1hard_G3_seed04_agent01
T1hard_G3_seed04_agent02
T1hard_G3_seed04_agent03
T1hard_G6_holdout_seed04

T2_G3_seed04_agent01
T2_G3_seed04_agent02
T2_G3_seed04_agent03
T2_G6_holdout_seed04
```

## 第四优先级：prompt-diverse G3

先每个任务族跑一个 seed，验证“多样化是否减少相关盲点”。

prompt variants：

- `source_sweep`：按文件/文档源系统扫。
- `boundary_case`：专门寻找边界项、别名、间接依赖。
- `skeptical_audit`：假设已有结果不完整，主动找反例。

命名：

```text
T2_G3div_seed01_source_sweep
T2_G3div_seed01_boundary_case
T2_G3div_seed01_skeptical_audit
```

评价：

- 与 homogeneous G3 比较 union recall。
- 与 homogeneous G3 比较 pairwise Jaccard。
- 看 common blind spot 是否减少。

## 成本日志格式

每个 run 额外保存：

```json
{
  "run_id": "T4_G3_seed01_agent01",
  "task_id": "T4_real_repo_click_deprecation",
  "started_at": "2026-06-08T00:00:00+08:00",
  "ended_at": "2026-06-08T00:00:00+08:00",
  "model_name": "unknown",
  "prompt_variant": "homogeneous",
  "input_tokens": null,
  "output_tokens": null,
  "tool_calls": null,
  "wall_clock_seconds": null,
  "stop_reason": "self_stop"
}
```

建议路径：

```text
experiments/false_convergence_pilot/run_cost_logs/
```

## 完成标准

这一批实验完成后，我们应该能更新论文中的三张核心表：

- real-repo validation 表。
- stopping/certificate baseline 表。
- cost-benefit 表。

如果 T4 seed01 明显太慢，先完成 G3 三个 agent 和 scorer；G6/summary 可以第二轮补。
