# Coverage Geometry Diagnostic Report

Status: mechanism diagnostic pilot only. This report does not introduce a new method or stopping certificate.

## Data Used

- Usable states: 38
- Repositories: click, itsdangerous, requests
- Runtime-observable features here are source/item ledger features; oracle recall is used only for offline labels.
- False completion is defined as all inspected G3 agents self-reporting completion while union recall is below theta; confidence is not part of the label.
- Action trajectory embeddings were not built because the inspected online logs do not contain query/action/tool sequences.

## Repository Summary

| repository   |   states |   false_095 |   mean_recall |   mean_erank |   mean_logdet_gain |   mean_source_hhi |
|:-------------|---------:|------------:|--------------:|-------------:|-------------------:|------------------:|
| click        |        9 |           9 |      0.744966 |     0.74585  |            6.17193 |          0.254599 |
| itsdangerous |        9 |           9 |      0.875    |     0.6684   |            5.53839 |          0.392045 |
| requests     |       20 |          20 |      0.728125 |     0.610889 |            6.00344 |          0.350929 |

## False-Completion Label Counts

|   theta |   false_completion |   not_false_completion |
|--------:|-------------------:|-----------------------:|
|    0.9  |                 38 |                      0 |
|    0.95 |                 38 |                      0 |
|    1    |                 38 |                      0 |

## Metric Association With False Completion at theta = 0.95

| metric                                |   n |   spearman_r |   spearman_p |   auroc_abs_direction |   auprc_raw_direction |
|:--------------------------------------|----:|-------------:|-------------:|----------------------:|----------------------:|
| mean_pairwise_item_jaccard_from_score |  38 |          nan |          nan |                   nan |                   nan |
| mean_pairwise_source_jaccard          |  38 |          nan |          nan |                   nan |                   nan |
| source_coverage_count                 |  38 |          nan |          nan |                   nan |                   nan |
| singleton_ratio_from_score            |  38 |          nan |          nan |                   nan |                   nan |
| source_pairwise_cosine                |  38 |          nan |          nan |                   nan |                   nan |
| source_normalized_effective_rank      |  38 |          nan |          nan |                   nan |                   nan |

Interpretation note: AUROC is reported with direction flipped to the better of metric or negative metric, so it is descriptive and optimistic for screening. It is not a trained classifier result.

At theta = 0.95, the inspected historical states contain no safe-completion negative class. Metric screening is therefore undefined for this data slice; the table is retained only to show that the current logs are not sufficient for a discriminative geometry test.

## RQ Answers

### RQ1

The existing logs support a source-path coverage version of the question, not full action-trajectory geometry. All inspected states are false completions even at theta = 0.90, so this pilot cannot compare false completions against safe completions. It can only describe the coverage geometry of failure states.

### RQ2

Not answered from the current data. Because the label has no negative class, effective rank, logdet volume, marginal volume gain, overlap, source coverage, no-new-item rounds, and confidence cannot be compared as predictors of false completion. A new diagnostic run must include both intentionally stopped states and safe or near-safe states.

### RQ3

Not answered. Current scout/holdout logs expose discovered items and some true-positive gains, but they do not expose enough route vectors to compute low-projection residual-direction scout metrics.

### RQ4

Partially assessable across Requests, Click, and itsdangerous score summaries. Stability remains unresolved because the feature representation is path-prefix based and not a true action trajectory.

## Go / No-Go

No-Go for making geometry the main line now.

Reasons:

- Current logs are sufficient for source/item coverage diagnostics but insufficient for action-trajectory geometry.
- The cleaned false-completion definition marks every inspected state as false completion at theta 0.90, 0.95, and 1.00, leaving no safe-completion comparison group.
- Residual-direction scout claims cannot be tested without query/action/tool route logs.
- Any metric separation here is descriptive and not yet shown to dominate simple source coverage or singleton/evidence-ledger baselines under leave-one-repo validation.

Recommended fallback for the paper line: simple source coverage + evidence ledger + lightweight audit controller.

Minimum next re-run: for one seed each on Requests and Click, log per-round query/action/tool/source events for G3 plus one scout policy, and include at least one deliberately extended high-recall/audited run to create a safe or near-safe comparison state. Then repeat this script with true visit/action matrices.
