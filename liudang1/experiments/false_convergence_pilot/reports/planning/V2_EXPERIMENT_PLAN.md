# Completion Certificate v2 Experiment Plan

Created: 2026-06-09

## Freeze Status

`completion_certificate_v1` is frozen as an honest diagnostic baseline. Its code,
results, report, and the current paper snapshot are copied to:

`experiments/false_convergence_pilot/frozen/completion_certificate_v1_20260609/`

The v1 interpretation is fixed: no observed false certification in the current
states, low safe coverage, and near-random AUROC. Do not tune v1 thresholds or
overwrite v1 outputs.

## Existing Data Inventory

- Synthetic/document tasks:
  - `T1_hard_repo_oracle.json`
  - `T2_policy_docs_oracle.json`
  - `T2_policy_docs_seed0*_itemsets.json`
- Real repository tasks:
  - Click deprecation audit at commit `8a1b1a33d739be05b7e91251e3c0dde77c5e152f`
  - Requests TLS audit at commit `1190afd14fca74292946d62c4c8169880a47ff67`
- Existing blind itemsets:
  - `T4_real_repo_click_seed0*_blind_itemsets.json`
  - `T5_real_repo_requests_tls_seed0*_blind_itemsets.json`
- Existing cost logs:
  - `run_cost_logs/*.json`
  - T5 token/wall-clock fields are mostly present.
  - T4 older logs have incomplete token/tool-call fields.

## Missing Fields in Older Runs

Older blind runs do not consistently log:

- `round_id`
- `query_or_action`
- `source_file`
- `source_region`
- `candidate_item`
- `first_seen_round`
- `support_count`
- per-candidate token/tool-call/wall-clock accounting
- search path and query history needed for query/path similarity

These fields are required for v2 calibration and are added by the new v2
offline diagnostic collector.

## New v2 Data Collection

The first v2 run uses deterministic offline repository/document scanners. These
are independent replay-style diagnostic runs, not new online LLM blind runs. The
scanner reads task source files and task descriptions only. Oracles are used
only after candidate generation for offline labels, recall, residual missing
mass, and audit-policy scoring.

Logged fields:

```text
run_id, repository, task_family, seed, agent_id, model,
prompt_variant, round_id, query_or_action, source_file,
source_region, candidate_item, first_seen_round, support_count,
confidence, token_input, token_output, tool_calls, wall_clock
```

Coverage targets:

- agent counts `k=1,2,3,5`
- homogeneous, prompt-diverse, and model-heterogeneous agent groups
- free-search and source-partitioned search
- low, medium, and high budgets
- pre-audit and post-audit states
- complete, near-complete, and incomplete states when produced by the scanner

## Split Rule

Train/calibration/test splits are grouped by `(repository, task_family, seed)`.
No derived state from the same group may cross split boundaries.

Initial split:

- train: seeds 1-2
- calibration: seed 3
- test: seeds 4-5

## v2 Features

Export the following features before fitting complex models:

- output Jaccard
- source overlap
- source coverage
- query similarity
- search-path overlap
- marginal discovery gain
- novelty decay
- singleton/doubleton counts
- per-source singleton density
- nominal agent count and effective exploration size
- Good-Turing and Chao missing-mass estimates
- residual missing mass for offline correlation analysis

## v2 Risk Models

Target:

```text
unsafe = recall < 0.95
```

Models/baselines:

- v1 handcrafted rule
- confidence-only
- overlap-only
- no-new-item
- Good-Turing-only
- Chao-only
- logistic regression
- regularized logistic regression
- decision tree
- gradient boosting

Each method outputs a continuous risk score interpreted as
`P(unsafe | pre-audit observable signals)` for learned models and a monotone
risk proxy for non-learned baselines.

Calibration:

- choose SAFE risk threshold only on calibration split
- evaluate once on test split
- report AUROC, AUPRC, Brier, ECE, FCR, FCR confidence upper bound, Safe
  Coverage, Abstention Rate, and risk-coverage curves

No theoretical risk-control guarantee is claimed unless a separate conformal
calibration experiment is implemented and its assumptions are documented.

## Audit Policy Evaluation

Compare:

- no audit
- singleton audit
- random holdout
- boundary-focused holdout
- source-partitioned audit
- always-holdout
- risk-triggered audit

Report:

- pre/post recall
- precision
- recovered true positives
- introduced false positives
- token/tool-call/wall-clock
- cost per recovered true positive
- unnecessary audit rate on already-safe states

## SeekerGym Status

Current status: scaffold only.

`experiments/false_convergence_pilot/benchmark_runs/seekergym/MANIFEST.json`
records that no local SeekerGym checkout was found. No SeekerGym results should
be written into the paper until a fixed subset is actually run and logged.

TODO:

- add or point to a local SeekerGym checkout
- map episodes to closed-world oracle items
- map traces to candidate item logs
- run a fixed small subset with seed/config manifest
- export completeness and uncertainty metrics

## Paper Update Rule

Do not broadly rewrite the paper before stable v2 results exist. After v2
outputs are generated and inspected:

- demote v1 to prototype baseline/ablation
- make v2 calibrated certificate the main method only if test results support it
- add risk-coverage table/curve from real v2 logs
- keep v1 negative result as motivation for calibration
- move detailed configs and extended results to appendix
- compile PDF and check the AAAI 7-page technical-content limit
