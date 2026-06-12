# T1-Hard Seed 01 Results

Task: `T1_hard_repo`

Oracle size: 35 line-level migration points.

## Individual Runs

| run_id | confidence | found | true_positive | false_positive | recall | precision | false_stop |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T1hard_G1_seed01 | 0.90 | 22 | 22 | 0 | 0.629 | 1.000 | true |
| T1hard_G3_seed01_agent01 | 0.84 | 22 | 22 | 0 | 0.629 | 1.000 | true |
| T1hard_G3_seed01_agent02 | 0.88 | 22 | 22 | 0 | 0.629 | 1.000 | true |
| T1hard_G3_seed01_agent03 | 0.84 | 35 | 35 | 0 | 1.000 | 1.000 | false |
| T1hard_G6_holdout_seed01 | 0.88 | 35 | 35 | 0 | 1.000 | 1.000 | false |

## G3 Metrics

| metric | value |
| --- | ---: |
| mean_confidence | 0.867 |
| pairwise_jaccard_agent01_agent02 | 1.000 |
| pairwise_jaccard_agent01_agent03 | 0.629 |
| pairwise_jaccard_agent02_agent03 | 0.629 |
| mean_pairwise_jaccard | 0.753 |
| consensus_found_by_at_least_2_agents | 22 |
| consensus_recall | 0.629 |
| union_found | 35 |
| union_recall | 1.000 |

## Holdout Gain

Using the G3 consensus set as the main workflow output:

| metric | value |
| --- | ---: |
| main_consensus_true_positive | 22 |
| holdout_true_positive | 35 |
| new_true_items_from_holdout | 13 |
| holdout_gain | 0.371 |

## Bucket-Level Pattern

The main consensus found the explicit config, registry, and first-hop lookup lines. It systematically missed downstream lines where legacy behavior is inherited:

- `build_gateway(entry)` lines.
- `gateway.post(...)` lines.
- `queue.publish(topic, ...)` lines.
- `if entry["processor"] == "acmepay"` route-selection line.
- downstream replay call lines.

## Interpretation

This run provides a candidate False Convergence signal under a consensus-style multi-agent aggregation rule:

- The main G3 consensus has high agreement and self-reported completion.
- The consensus recall is only 0.629.
- The Holdout Scout recovers 13 additional true items.
- The missed items are not random; they are downstream call-site items that inherit legacy behavior through registries.

Important caveat:

- The G3 union reaches 1.000 recall because one homogeneous agent found the downstream items.
- Therefore this is not evidence that all union-based multi-agent workflows fail.
- It is evidence that consensus/summary aggregation can create a false sense of completion when agents overweight shared explicit-entry evidence.

Decision: `Go for phenomenon refinement, not yet stable proof`.

