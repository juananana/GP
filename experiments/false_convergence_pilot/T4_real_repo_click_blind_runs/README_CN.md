# T4 Click 真实仓库盲评运行说明

日期：2026-06-08

## 为什么要这样跑

T4 是当前最重要的 stronger validation：它使用真实开源仓库 Click 的固定快照，任务是找出 deprecated API surface audit 的 line-level items。

注意：主线程已经看过 oracle，因此主线程不能产出 blind-agent itemsets。下面四个 run 必须由独立上下文执行，且执行者不能访问 oracle、score summary、smoke itemsets、incidence logs 或其他实验结果。

## 允许访问

只允许访问：

```text
experiments/false_convergence_pilot/T4_real_repo_click/
```

## 禁止访问

禁止访问：

```text
experiments/false_convergence_pilot/results/T4_real_repo_click_deprecation_oracle.json
experiments/false_convergence_pilot/results/T4_real_repo_click_seed01_smoke_itemsets.json
experiments/false_convergence_pilot/results/T4_real_repo_click_seed01_smoke_score_summary.json
experiments/false_convergence_pilot/results/T4_real_repo_click_seed01_smoke_score_summary.md
experiments/false_convergence_pilot/incidence_logs/
experiments/false_convergence_pilot/results/*score_summary*
experiments/false_convergence_pilot/protocol_outputs/completion_certificate_v0_results.json
```

## 需要生成的独立 run 文件

| run_id | prompt file | output |
| --- | --- | --- |
| T4_G3_seed01_agent01 | `prompt_T4_G3_seed01_agent01.md` | `T4_G3_seed01_agent01.json` |
| T4_G3_seed01_agent02 | `prompt_T4_G3_seed01_agent02.md` | `T4_G3_seed01_agent02.json` |
| T4_G3_seed01_agent03 | `prompt_T4_G3_seed01_agent03.md` | `T4_G3_seed01_agent03.json` |
| T4_G6_holdout_seed01 | `prompt_T4_G6_holdout_seed01.md` | `T4_G6_holdout_seed01.json` |

每个输出文件放在本目录：

```text
experiments/false_convergence_pilot/T4_real_repo_click_blind_runs/
```

## 合并和评分命令

四个 JSON 都完成后运行：

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

python experiments\false_convergence_pilot\tools\score_itemsets.py `
  --oracle experiments\false_convergence_pilot\results\T4_real_repo_click_deprecation_oracle.json `
  --runs experiments\false_convergence_pilot\results\T4_real_repo_click_seed01_blind_itemsets.json `
  --out-json experiments\false_convergence_pilot\results\T4_real_repo_click_seed01_blind_score_summary.json `
  --out-md experiments\false_convergence_pilot\results\T4_real_repo_click_seed01_blind_score_summary.md
```

## 成本日志

每个 run 另外保存一个成本日志到：

```text
experiments/false_convergence_pilot/run_cost_logs/
```

如果拿不到 token，则先填 `null`，不要编造。
