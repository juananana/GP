# Geometry-Control Question Validation

Question:

> Is multi-agent workflow false stopping controlled by a stable coverage-geometry quantity?

This report uses existing historical logs only as read-only observations. It does not use the archived `liudang1/` direction as the new research line, and it does not claim a method or phase transition.

## Identification Checks

|   theta |   false_completion |   not_false_completion | label_has_two_classes   |
|--------:|-------------------:|-----------------------:|:------------------------|
|    0.9  |                 38 |                      0 | False                   |
|    0.95 |                 38 |                      0 | False                   |
|    1    |                 38 |                      0 | False                   |

- Safe/false discriminative test available: `False`.
- Action-trajectory geometry available: `False`.
- Current logs contain source/item ledger geometry, but not query/action/tool trajectories.

## Continuous Recall Association

Because all inspected states are false completions at high-recall thresholds, we cannot test safe-vs-false separation. As a weaker diagnostic, we ask whether geometry variables correlate with the degree of union recall.

| scope   | repository   | metric                       |   n |   spearman_with_recall |     p_value |
|:--------|:-------------|:-----------------------------|----:|-----------------------:|------------:|
| global  | all          | source_coverage_count        |  38 |              -0.515269 | 0.000931396 |
| global  | all          | file_coverage_count          |  38 |              -0.514988 | 0.000938458 |
| global  | all          | mean_confidence              |  38 |               0.428368 | 0.0072934   |
| global  | all          | source_concentration_hhi     |  38 |               0.423874 | 0.00800198  |
| global  | all          | source_concentration_entropy |  38 |              -0.421901 | 0.00833125  |
| global  | all          | source_concentration_gini    |  38 |               0.412255 | 0.0101132   |
| global  | all          | source_marginal_logdet_gain  |  38 |              -0.251453 | 0.127792    |
| global  | all          | singleton_ratio_from_score   |  38 |              -0.238557 | 0.149201    |

Caution: the strongest global association is `source_coverage_count`, but it has no usable within-repository signal in this slice. That makes it likely to be a repository/task-size confound rather than a stable control variable.

## Cross-Repository Sign Stability

| metric                                |   repos_with_signal |   positive_repos |   negative_repos | sign_consistent   |
|:--------------------------------------|--------------------:|-----------------:|-----------------:|:------------------|
| file_entropy_effective_rank           |                   3 |                0 |                3 | True              |
| mean_pairwise_item_jaccard_from_score |                   3 |                3 |                0 | True              |
| mean_pairwise_source_jaccard          |                   3 |                3 |                0 | True              |
| singleton_ratio_from_score            |                   3 |                0 |                3 | True              |
| source_normalized_effective_rank      |                   3 |                0 |                3 | True              |
| file_coverage_count                   |                   1 |                0 |                1 | True              |
| mean_confidence                       |                   3 |                1 |                2 | False             |
| source_concentration_entropy          |                   3 |                1 |                2 | False             |

## Condition-Level Observation

The condition table is saved as CSV because it is wide. It should be read as descriptive only, not as causal evidence.

## Verdict

**Current answer: not verified.**

The existing data show that false completion is real in these historical runs, but they do not verify that a stable coverage-geometry quantity controls it.

Reasons:

- There is no safe-completion comparison class at theta 0.90, 0.95, or 1.00.
- The logs lack action trajectory fields, so source-path geometry is only a proxy.
- Continuous correlations with recall are exploratory and cannot establish safe-stopping control.
- The strongest global association is confounded by repository/task differences; within-repository variation is the relevant test.
- A geometry quantity must beat simple source coverage/overlap baselines across repositories before it can become the research core.

## Minimum Next Validation

To verify the question rather than only motivate it, run a small new diagnostic with:

- at least two repositories or task types;
- both false-completion states and safe or near-safe states;
- per-round query/action/tool/source-route logs;
- homogeneous, route-partitioned, and extended/audited conditions;
- a challenger aimed at weak or residual coverage regions;
- oracle labels used only after the blind runs finish.

The geometry line becomes credible only if one runtime-computable coverage variable predicts unsafe stopping better than source coverage, overlap, no-new-item rounds, and confidence, and the pattern repeats across tasks.
