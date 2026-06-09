# T5 Requests TLS 真实仓库盲评运行说明

日期：2026-06-08

## 允许访问

盲评 agent 只能访问：

```text
experiments/false_convergence_pilot/T5_real_repo_requests_tls/
```

## 禁止访问

禁止访问：

```text
experiments/false_convergence_pilot/results/T5_real_repo_requests_tls_oracle.json
experiments/false_convergence_pilot/results/T5_real_repo_requests_tls_seed01_smoke_itemsets.json
experiments/false_convergence_pilot/results/*T5*score_summary*
experiments/false_convergence_pilot/incidence_logs/
experiments/false_convergence_pilot/protocol_outputs/
experiments/false_convergence_pilot/summarizer_outputs/
```

## 输出文件

每个 run 输出一个 JSON，放在本目录：

| run_id | prompt file | output |
| --- | --- | --- |
| T5_G3_seed01_agent01 | `prompt_T5_G3_seed01_agent01.md` | `T5_G3_seed01_agent01.json` |
| T5_G3_seed01_agent02 | `prompt_T5_G3_seed01_agent02.md` | `T5_G3_seed01_agent02.json` |
| T5_G3_seed01_agent03 | `prompt_T5_G3_seed01_agent03.md` | `T5_G3_seed01_agent03.json` |
| T5_G6_holdout_seed01 | `prompt_T5_G6_holdout_seed01.md` | `T5_G6_holdout_seed01.json` |

## 后处理

四个 JSON 都完成后运行：

```powershell
python experiments\false_convergence_pilot\tools\run_t5_blind_postprocess.py --seed seed01
```
