# T1 Seed 01 Preliminary Results

Task: `T1_acmepay_repo`

Oracle size: 50 line-level migration points.

## Runs

| run_id | confidence | found | true_positive | false_positive | recall | precision | false_stop |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T1_G1_seed01 | 0.93 | 49 | 49 | 0 | 0.98 | 1.00 | false |
| T1_G3_seed01_agent01 | 0.92 | 50 | 50 | 0 | 1.00 | 1.00 | false |
| T1_G3_seed01_agent02 | 0.93 | 49 | 49 | 0 | 0.98 | 1.00 | false |
| T1_G3_seed01_agent03 | 0.88 | 51 | 49 | 2 | 0.98 | 0.96 | false |
| T1_G6_holdout_seed01 | 0.86 | 51 | 49 | 2 | 0.98 | 0.96 | false |

## G3 Aggregate

| metric | value |
| --- | ---: |
| union_found | 52 |
| union_true_positive | 50 |
| union_false_positive | 2 |
| union_recall | 1.00 |
| union_precision | 0.96 |
| mean_pairwise_jaccard | 0.961 |
| mean_confidence | 0.91 |

## Holdout Scout

| metric | value |
| --- | ---: |
| holdout_found | 51 |
| holdout_true_positive | 49 |
| holdout_false_positive | 2 |
| holdout_recall | 0.98 |
| new_true_items_beyond_G3_union | 0 |
| holdout_gain_beyond_G3_union | 0.00 |

## Interpretation

This task produced high agreement, but not low recall. The Holdout Scout also found no new true positives beyond the G3 union. Therefore it does not demonstrate False Convergence.

This is still useful as a smoke test:

- The blind task protocol worked.
- The JSON output format was usable.
- The first code scan task is too easy for the current model and prompt.
- The next task must contain harder long-tail targets, hidden source partitions, or stricter budget constraints.

Decision for this task version: `No-Go for False Convergence evidence, Go for pipeline validation`.
