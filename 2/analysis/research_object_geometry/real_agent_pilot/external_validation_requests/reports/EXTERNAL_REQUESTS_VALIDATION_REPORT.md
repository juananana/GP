# External Validation: Requests Repo

This experiment uses a real local snapshot of the open-source `requests` package from the Python environment. It is a bounded discovery task over six source files: `adapters.py, api.py, auth.py, models.py, sessions.py, utils.py`.

## Purpose

Test whether the frozen source-route exposure localization story survives outside generated tasks.

## Leakage Control

Oracle labels are created by a fixed offline route-pattern scan and used only for scoring. Challenger selection uses only runtime-visible exposure, discovery ledger state, source text, and route match counts. It does not use oracle missing mass or undiscovered true item counts.

## Condition Metrics

| task_id                     | condition         |   n_events |   n_agents |   n_exposure_strata |   n_discovery_strata |   source_route_coverage_ratio |   exposure_gini |   discovery_gini |   found_true_items |   oracle_total |   recall | false_stop_at_90   |
|:----------------------------|:------------------|-----------:|-----------:|--------------------:|---------------------:|------------------------------:|----------------:|-----------------:|-------------------:|---------------:|---------:|:-------------------|
| T_external_requests_repo_v1 | homogeneous       |        114 |          3 |                   6 |                    3 |                          0.25 |        0.888514 |         0.915323 |                 31 |            298 | 0.104027 | True               |
| T_external_requests_repo_v1 | route_partitioned |        326 |          4 |                  24 |                   18 |                          1    |        0.607402 |         0.65632  |                298 |            298 | 1        | False              |

## Challenger Summary

| granularity         | challenger               |   runs |   mean_new_true_items |   std_new_true_items |   new_true_ci95_low |   new_true_ci95_high |   mean_novelty_per_cost |   mean_cumulative_recall |   mean_false_stop_reduction |   delta_vs_random |   percentile_vs_random_normal_approx |
|:--------------------|:-------------------------|-------:|----------------------:|---------------------:|--------------------:|---------------------:|------------------------:|-------------------------:|----------------------------:|------------------:|-------------------------------------:|
| source_only         | free_search_continuation |    200 |               241.96  |              24.8185 |            238.455  |             245.226  |               0.0177841 |                 0.915973 |                        0.68 |            61.755 |                            0.928772  |
| source_only         | high_potential           |    200 |               257     |               0      |            257      |             257      |               0.0175931 |                 0.966443 |                        1    |            76.795 |                            0.965917  |
| source_only         | low_discovery            |    200 |               112     |               0      |            112      |             112      |               0.0107858 |                 0.479866 |                        0    |           -68.205 |                            0.0526275 |
| source_only         | low_exposure             |    200 |               112     |               0      |            112      |             112      |               0.0107858 |                 0.479866 |                        0    |           -68.205 |                            0.0526275 |
| source_only         | random                   |    200 |               180.205 |              42.1046 |            174.43   |             186.03   |               0.0166439 |                 0.708742 |                        0.06 |             0     |                            0.5       |
| source_only         | residual_potential       |    200 |               158     |               0      |            158      |             158      |               0.0120795 |                 0.634228 |                        0    |           -22.205 |                            0.298966  |
| source_route        | free_search_continuation |    200 |               126.415 |              32.5907 |            122.134  |             130.83   |               0.0378204 |                 0.528238 |                        0    |            80.88  |                            0.995833  |
| source_route        | high_potential           |    200 |               177     |               0      |            177      |             177      |               0.0542612 |                 0.697987 |                        0    |           131.465 |                            0.999991  |
| source_route        | low_discovery            |    200 |               106     |               0      |            106      |             106      |               0.047216  |                 0.459732 |                        0    |            60.465 |                            0.975714  |
| source_route        | low_exposure             |    200 |               106     |               0      |            106      |             106      |               0.047216  |                 0.459732 |                        0    |            60.465 |                            0.975714  |
| source_route        | random                   |    200 |                45.535 |              30.6566 |             41.3619 |              49.6404 |               0.0166784 |                 0.256829 |                        0    |             0     |                            0.5       |
| source_route        | residual_potential       |    200 |               177     |               0      |            177      |             177      |               0.0542612 |                 0.697987 |                        0    |           131.465 |                            0.999991  |
| source_route_action | free_search_continuation |    200 |               126.415 |              32.5907 |            122.134  |             130.83   |               0.0378204 |                 0.528238 |                        0    |            80.88  |                            0.995833  |
| source_route_action | high_potential           |    200 |               177     |               0      |            177      |             177      |               0.0542612 |                 0.697987 |                        0    |           131.465 |                            0.999991  |
| source_route_action | low_discovery            |    200 |               106     |               0      |            106      |             106      |               0.047216  |                 0.459732 |                        0    |            60.465 |                            0.975714  |
| source_route_action | low_exposure             |    200 |               106     |               0      |            106      |             106      |               0.047216  |                 0.459732 |                        0    |            60.465 |                            0.975714  |
| source_route_action | random                   |    200 |                45.535 |              30.6566 |             41.3619 |              49.6404 |               0.0166784 |                 0.256829 |                        0    |             0     |                            0.5       |
| source_route_action | residual_potential       |    200 |               177     |               0      |            177      |             177      |               0.0542612 |                 0.697987 |                        0    |           131.465 |                            0.999991  |

## Mean New True Items by Granularity

| granularity         |   free_search_continuation |   high_potential |   low_discovery |   low_exposure |   random |   residual_potential |
|:--------------------|---------------------------:|-----------------:|----------------:|---------------:|---------:|---------------------:|
| source_only         |                    241.96  |              257 |             112 |            112 |  180.205 |                  158 |
| source_route        |                    126.415 |              177 |             106 |            106 |   45.535 |                  177 |
| source_route_action |                    126.415 |              177 |             106 |            106 |   45.535 |                  177 |

## Interpretation

This is a real external-source validation, but it is still pattern-defined rather than human-annotated. Treat it as stronger than generated toy tasks and weaker than a fully manual external benchmark.
