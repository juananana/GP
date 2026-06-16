# External Validation v2: urllib3 Completion Audit

## Purpose

This is the second external real-repo task. The `requests` result is frozen and used only as a prior mechanism case. This task tests whether the evidence-condition controller avoids false certification on a different real codebase.

## Task

Repository snapshot: local installed `urllib3`.

Audit routes:

- `timeout_route`
- `retry_route`
- `tls_route`
- `exception_route`
- `cleanup_route`

The task is a bounded completion audit: decide whether the workflow has enough evidence to certify that these route families have been covered across the selected repo files.

## Condition Metrics

| task_id                     | condition         |   n_events |   n_agents |   support_size |   support_ratio |   exposure_gini |   weak_plausible_gap |   found_true_items |   oracle_total |   recall | naive_false_certification   | geometry_eligible   | controller_decision   | controller_false_certification   |
|:----------------------------|:------------------|-----------:|-----------:|---------------:|----------------:|----------------:|---------------------:|-------------------:|---------------:|---------:|:----------------------------|:--------------------|:----------------------|:---------------------------------|
| T_external_urllib3_audit_v2 | extended_audit    |        734 |          5 |             30 |             1   |        0.550206 |                    0 |                699 |            699 | 1        | False                       | True                | SAFE                  | False                            |
| T_external_urllib3_audit_v2 | homogeneous       |        426 |          3 |              6 |             0.2 |        0.91513  |                   24 |                135 |            699 | 0.193133 | True                        | False               | CONTINUE              | False                            |
| T_external_urllib3_audit_v2 | route_partitioned |        612 |          4 |             24 |             0.8 |        0.647149 |                    6 |                584 |            699 | 0.835479 | True                        | True                | CONTINUE              | False                            |

## Controller Challenger Summary

| challenger               |   runs |   mean_support_expansion |   mean_support_gap_reduction |   mean_new_true_items |   mean_new_evidence_per_cost |   mean_cost |   mean_cumulative_recall |   safe_rate |   continue_rate |   abstain_rate |   false_certification_rate |   abstain_precision |
|:-------------------------|-------:|-------------------------:|-----------------------------:|----------------------:|-----------------------------:|------------:|-------------------------:|------------:|----------------:|---------------:|---------------------------:|--------------------:|
| residual_potential       |    200 |                    5     |                        5     |               329     |                    0.0622046 |     5289    |                 0.663805 |           0 |            1    |           0    |                          0 |                 nan |
| low_exposure             |    200 |                    5     |                        5     |               157     |                    0.0282883 |     5550    |                 0.41774  |           0 |            1    |           0    |                          0 |                 nan |
| random                   |    200 |                    4.065 |                        4.065 |                92.525 |                    0.0218125 |     4225.24 |                 0.325501 |           0 |            0.99 |           0.01 |                          0 |                   1 |
| free_search_continuation |    200 |                    4.025 |                        4.025 |               171.41  |                    0.0364861 |     4708.88 |                 0.438355 |           0 |            1    |           0    |                          0 |                 nan |
| high_potential           |    200 |                    4     |                        4     |               275     |                    0.0626995 |     4386    |                 0.586552 |           0 |            1    |           0    |                          0 |                 nan |

## High-Potential vs Residual-Potential Overlap

- identical target sets: 0.000
- mean Jaccard: 0.667

## Interpretation

The controller again avoids accepting the localized homogeneous stop as SAFE. It sends productive repairs to `CONTINUE` and reserves `SAFE` for broad near-complete evidence.

The method claim must remain restrained. If high-potential and residual-potential overlap is high, any residual-potential gain is not clean evidence that `under_exposure` adds independent value on this task.

Here the overlap is partial rather than complete. Residual-potential recovers more new scored evidence than high-potential, but it also spends more cost and shares much of the same target set. The correct claim is therefore:

```text
external v2 gives positive evidence for residual-potential as a repair candidate,
but does not prove it is optimal or generally better than high-potential.
```
