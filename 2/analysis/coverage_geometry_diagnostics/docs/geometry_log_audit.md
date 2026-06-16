# Geometry Log Audit

This audit checks what can be computed from existing logs without inventing fields.

## Sources Inspected

- `score_summary.json` files: 38
- agent run JSON files under `runs/`: 117
- incidence log: `liudang1\experiments\false_convergence_pilot\incidence_logs\line_a_incidence_log.csv` with 7606 rows
- states with usable G3 run item logs in this pilot: 38
- missing run files referenced by score summaries: 0

## Field Availability

| field | availability |
|---|---|
| `task_id` | score_summary.json; incidence log |
| `repo_id` | inferred from path/task_id; not a stable explicit field in score summaries |
| `run_id` | score_summary.json and run JSON |
| `agent_id` | parseable from run_id; incidence log has explicit agent_id |
| `round_id` | incidence column exists but is empty in line_a; online run JSON has no rounds |
| `item_id` | run JSON items as file_path:line; incidence log item_id |
| `oracle_label` | incidence log and score summaries after scoring only |
| `source_path` | run JSON items.file_path; incidence source_id |
| `source_family` | incidence source_bin; otherwise derived from source_path prefix and marked proxy |
| `search_route` | query_path column exists but is empty in line_a; not present in online run JSON; v2 offline features have search_strategy/path-overlap aggregates only |
| `query_text` | not present in online run JSON |
| `tool_name` | not present in online run JSON |
| `action_type` | not present in online run JSON |
| `timestamp` | not present in online run JSON |
| `self_reported_completion` | run JSON and incidence log |
| `self_reported_confidence` | run JSON and score summaries |
| `stop_reason` | schema only for run_log; not present in online run JSON inspected |
| `holdout_or_scout_id` | audit_policy_eval paths/runs imply policy; no uniform field |
| `scout_discovered_items` | seed_summary holdout_new_true_items for some runs; verifier run JSON item lists exist |
| `cost_or_token_count` | separate cost JSON files; not joined in this pilot |
| `latency` | schema/v2 aggregates only; not present in online run JSON |

## Existing Incidence Columns

`task_id`, `task_family`, `case_id`, `seed`, `group_id`, `run_id`, `agent_id`, `round_id`, `prompt_variant`, `model_name`, `item_id`, `canonical_item`, `source_id`, `source_bin`, `query_path`, `first_seen_round`, `support_count`, `is_singleton`, `self_reported_completion`, `self_reported_confidence`, `aggregation_status`, `audit_status`, `oracle_label`, `oracle_bucket`, `reportable`, `experimental_status`

## Non-empty Incidence Field Counts

| field | non-empty rows |
|---|---:|
| `round_id` | 0 |
| `query_path` | 0 |
| `source_bin` | 7606 |
| `source_id` | 7606 |
| `oracle_label` | 7606 |
| `self_reported_completion` | 7606 |

## Directly Computable Metrics

- Agent x source-family discovered-item count matrix from run JSON `items.file_path`.
- Agent x item incidence matrix from run JSON `items.file_path:line`.
- Pairwise item Jaccard, pairwise source Jaccard, singleton ratio.
- Source/file coverage counts, source concentration entropy/HHI/Gini.
- Coverage-matrix cosine similarity, singular values, entropy effective rank, logdet volume, marginal logdet gain.
- Offline labels: union recall/precision and false-completion labels at theta 0.90, 0.95, and 1.00 from score summaries.

## Approximate Metrics Only

- `source_family` when absent is approximated by the first two path segments after `repo/`.
- `source_route` is approximated only by source-path/source-family coverage; this is not an action trajectory.
- `scout_gain_vs_residual_projection.png` uses main-agent source cosine as a route-similarity proxy; no true projection onto action trajectories is available.

## Not Computable From Current Logs

- Visit-count and action-count matrices by source-route stratum.
- Query/action/tool sequence embeddings.
- Principal angles over non-degenerate per-agent trajectory subspaces.
- Timestamped no-new-item rounds for online runs.
- Robust residual-direction scout projection metrics.

## Minimal Re-run Fields Needed

- Append one JSONL event per tool/action with `task_id`, `repo_id`, `run_id`, `agent_id`, `round_id`, `query_text`, `tool_name`, `action_type`, `source_path`, `timestamp`, and `new_items`.
- Keep the current item ledger fields, including `oracle_label`, only for offline scoring after blind runs complete.
- Log scout policy id and route/action events so residual-direction scout comparisons are not path-name proxies.
