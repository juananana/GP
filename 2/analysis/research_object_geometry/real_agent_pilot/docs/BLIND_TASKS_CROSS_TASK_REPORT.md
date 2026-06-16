# Blind Tasks Cross-Task Report

## Cross-Task Diagnostic Pattern

| task_dir         | task_id                  |   exposure_gini_homogeneous |   exposure_gini_route_partitioned |   recall_homogeneous |   recall_route_partitioned |   source_route_coverage_ratio_homogeneous |   source_route_coverage_ratio_route_partitioned |   delta_exposure_gini_homogeneous_minus_partitioned |   delta_recall_partitioned_minus_homogeneous | pattern_replicated   |
|:-----------------|:-------------------------|----------------------------:|----------------------------------:|---------------------:|---------------------------:|------------------------------------------:|------------------------------------------------:|----------------------------------------------------:|---------------------------------------------:|:---------------------|
| code_repo_v1     | T_blind_code_repo_v1     |                    0.75     |                          0.199495 |             0.3      |                       0.95 |                                  0.333333 |                                            1    |                                            0.550505 |                                     0.65     | True                 |
| policy_docset_v1 | T_blind_policy_docset_v1 |                    0.770833 |                          0.385417 |             0.708333 |                       1    |                                  0.25     |                                            0.75 |                                            0.385417 |                                     0.291667 | True                 |

## Condition Summary

| task_dir         | task_id                  | condition                           |   n_events |   n_agents |   n_exposure_strata |   n_discovery_strata |   source_route_coverage_ratio |   exposure_gini |   discovery_gini |   found_true_items |   oracle_total |    recall | false_stop_at_90   |
|:-----------------|:-------------------------|:------------------------------------|-----------:|-----------:|--------------------:|---------------------:|------------------------------:|----------------:|-----------------:|-------------------:|---------------:|----------:|:-------------------|
| code_repo_v1     | T_blind_code_repo_v1     | homogeneous                         |         33 |          3 |                   4 |                    3 |                      0.333333 |        0.75     |         0.805556 |                  6 |             20 | 0.3       | True               |
| code_repo_v1     | T_blind_code_repo_v1     | homogeneous_low_exposure_challenger |         12 |          1 |                   4 |                    4 |                      0.333333 |        0.722222 |         0.722222 |                  6 |             20 | 0.3       | True               |
| code_repo_v1     | T_blind_code_repo_v1     | route_partitioned                   |         36 |          3 |                  12 |                   11 |                      1        |        0.199495 |         0.29386  |                 19 |             20 | 0.95      | False              |
| policy_docset_v1 | T_blind_policy_docset_v1 | homogeneous                         |         66 |          3 |                   4 |                    4 |                      0.25     |        0.770833 |         0.775735 |                 17 |             24 | 0.708333  | True               |
| policy_docset_v1 | T_blind_policy_docset_v1 | homogeneous_low_exposure_challenger |         13 |          1 |                   4 |                    1 |                      0.25     |        0.793269 |         0.9375   |                  2 |             24 | 0.0833333 | True               |
| policy_docset_v1 | T_blind_policy_docset_v1 | route_partitioned                   |         51 |          3 |                  12 |                    8 |                      0.75     |        0.385417 |         0.640625 |                 24 |             24 | 1         | False              |

## Challenger Summary

| task_dir         | challenger         |   runs |   mean_new_true_items |   max_new_true_items |   mean_cumulative_recall |
|:-----------------|:-------------------|-------:|----------------------:|---------------------:|-------------------------:|
| code_repo_v1     | low_discovery      |      1 |                  6    |                    6 |                 0.6      |
| code_repo_v1     | low_exposure       |      1 |                  6    |                    6 |                 0.6      |
| code_repo_v1     | random             |     20 |                  4.35 |                    8 |                 0.5175   |
| code_repo_v1     | residual_potential |      1 |                  9    |                    9 |                 0.75     |
| policy_docset_v1 | low_discovery      |      1 |                  2    |                    2 |                 0.791667 |
| policy_docset_v1 | low_exposure       |      1 |                  2    |                    2 |                 0.791667 |
| policy_docset_v1 | random             |     20 |                  2.15 |                    5 |                 0.797917 |
| policy_docset_v1 | residual_potential |      1 |                  4    |                    4 |                 0.875    |

## Decision

The diagnostic pattern is replicated when homogeneous route reuse has higher exposure localization and lower recall than route-partitioned search. Challenger results remain secondary: they can confirm residual missing mass, but the method should not be finalized until challenger selection beats random across more tasks and seeds.
