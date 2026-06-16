# Blind Code Task Report

This runtime-blind code discovery task asks agents to find compatibility, security, correctness, and resilience risk sites in a bounded generated repository. The oracle is stored separately and used only during scoring.

## Condition Metrics

| task_id              | condition                           |   n_events |   n_agents |   n_exposure_strata |   n_discovery_strata |   source_route_coverage_ratio |   exposure_gini |   discovery_gini |   found_true_items |   oracle_total |   recall | false_stop_at_90   |
|:---------------------|:------------------------------------|-----------:|-----------:|--------------------:|---------------------:|------------------------------:|----------------:|-----------------:|-------------------:|---------------:|---------:|:-------------------|
| T_blind_code_repo_v1 | homogeneous                         |         33 |          3 |                   4 |                    3 |                      0.333333 |        0.75     |         0.805556 |                  6 |             20 |     0.3  | True               |
| T_blind_code_repo_v1 | homogeneous_low_exposure_challenger |         12 |          1 |                   4 |                    4 |                      0.333333 |        0.722222 |         0.722222 |                  6 |             20 |     0.3  | True               |
| T_blind_code_repo_v1 | route_partitioned                   |         36 |          3 |                  12 |                   11 |                      1        |        0.199495 |         0.29386  |                 19 |             20 |     0.95 | False              |

## Challenger Summary

| challenger         |   runs |   mean_new_true_items |   max_new_true_items |   mean_cumulative_recall |
|:-------------------|-------:|----------------------:|---------------------:|-------------------------:|
| low_discovery      |      1 |                  6    |                    6 |                   0.6    |
| low_exposure       |      1 |                  6    |                    6 |                   0.6    |
| random             |     20 |                  4.35 |                    8 |                   0.5175 |
| residual_potential |      1 |                  9    |                    9 |                   0.75   |

## Challenger Metrics

| base_condition   | challenger         |   seed | targeted_strata                                                                                         |   challenger_events |   base_true_items |   new_true_items |   cumulative_true_items |   cumulative_recall | new_true_item_ids                   |
|:-----------------|:-------------------|-------:|:--------------------------------------------------------------------------------------------------------|--------------------:|------------------:|-----------------:|------------------------:|--------------------:|:------------------------------------|
| homogeneous      | low_exposure       |      0 | api_client::resilience_route;api_client::security_route;auth::resilience_route;auth::security_route     |                  12 |                 6 |                6 |                      12 |                0.6  | C02;C03;C04;C16;C18;C19             |
| homogeneous      | low_discovery      |      0 | api_client::resilience_route;api_client::security_route;auth::resilience_route;auth::security_route     |                  12 |                 6 |                6 |                      12 |                0.6  | C02;C03;C04;C16;C18;C19             |
| homogeneous      | residual_potential |      0 | api_client::resilience_route;storage::security_route;auth::security_route;payments::resilience_route    |                  15 |                 6 |                9 |                      15 |                0.75 | C02;C03;C10;C11;C12;C13;C14;C18;C19 |
| homogeneous      | random             |      0 | storage::compat_route;api_client::resilience_route;auth::compat_route;payments::security_route          |                  11 |                 6 |                3 |                       9 |                0.45 | C08;C18;C19                         |
| homogeneous      | random             |      1 | auth::resilience_route;api_client::compat_route;auth::security_route;payments::security_route           |                  11 |                 6 |                4 |                      10 |                0.5  | C02;C03;C04;C08                     |
| homogeneous      | random             |      2 | auth::compat_route;auth::security_route;api_client::security_route;payments::resilience_route           |                  13 |                 6 |                5 |                      11 |                0.55 | C02;C03;C10;C11;C16                 |
| homogeneous      | random             |      3 | payments::compat_route;api_client::compat_route;storage::resilience_route;auth::resilience_route        |                   9 |                 6 |                2 |                       8 |                0.4  | C04;C15                             |
| homogeneous      | random             |      4 | payments::compat_route;payments::security_route;auth::security_route;storage::compat_route              |                   9 |                 6 |                3 |                       9 |                0.45 | C02;C03;C08                         |
| homogeneous      | random             |      5 | api_client::compat_route;payments::security_route;payments::resilience_route;storage::resilience_route  |                  10 |                 6 |                4 |                      10 |                0.5  | C08;C10;C11;C15                     |
| homogeneous      | random             |      6 | api_client::compat_route;auth::security_route;storage::security_route;payments::security_route          |                  13 |                 6 |                6 |                      12 |                0.6  | C02;C03;C08;C12;C13;C14             |
| homogeneous      | random             |      7 | payments::resilience_route;auth::resilience_route;storage::compat_route;auth::compat_route              |                  10 |                 6 |                3 |                       9 |                0.45 | C04;C10;C11                         |
| homogeneous      | random             |      8 | payments::compat_route;payments::resilience_route;storage::compat_route;auth::resilience_route          |                   8 |                 6 |                3 |                       9 |                0.45 | C04;C10;C11                         |
| homogeneous      | random             |      9 | storage::security_route;api_client::compat_route;payments::resilience_route;payments::security_route    |                  12 |                 6 |                6 |                      12 |                0.6  | C08;C10;C11;C12;C13;C14             |
| homogeneous      | random             |     10 | api_client::compat_route;auth::compat_route;storage::compat_route;storage::security_route               |                  12 |                 6 |                3 |                       9 |                0.45 | C12;C13;C14                         |
| homogeneous      | random             |     11 | storage::security_route;storage::resilience_route;api_client::resilience_route;api_client::compat_route |                  13 |                 6 |                6 |                      12 |                0.6  | C12;C13;C14;C15;C18;C19             |
| homogeneous      | random             |     12 | storage::security_route;payments::security_route;storage::resilience_route;payments::resilience_route   |                  11 |                 6 |                7 |                      13 |                0.65 | C08;C10;C11;C12;C13;C14;C15         |
| homogeneous      | random             |     13 | payments::security_route;api_client::resilience_route;auth::resilience_route;payments::compat_route     |                  10 |                 6 |                4 |                      10 |                0.5  | C04;C08;C18;C19                     |
| homogeneous      | random             |     14 | auth::security_route;api_client::compat_route;storage::resilience_route;payments::compat_route          |                  11 |                 6 |                3 |                       9 |                0.45 | C02;C03;C15                         |
| homogeneous      | random             |     15 | payments::compat_route;auth::compat_route;storage::resilience_route;api_client::security_route          |                  10 |                 6 |                2 |                       8 |                0.4  | C15;C16                             |
| homogeneous      | random             |     16 | payments::resilience_route;storage::security_route;api_client::security_route;payments::security_route  |                  11 |                 6 |                7 |                      13 |                0.65 | C08;C10;C11;C12;C13;C14;C16         |
| homogeneous      | random             |     17 | storage::resilience_route;storage::compat_route;payments::security_route;payments::resilience_route     |                   8 |                 6 |                4 |                      10 |                0.5  | C08;C10;C11;C15                     |
| homogeneous      | random             |     18 | auth::resilience_route;auth::security_route;storage::security_route;payments::resilience_route          |                  13 |                 6 |                8 |                      14 |                0.7  | C02;C03;C04;C10;C11;C12;C13;C14     |
| homogeneous      | random             |     19 | api_client::security_route;auth::compat_route;storage::resilience_route;auth::security_route            |                  12 |                 6 |                4 |                      10 |                0.5  | C02;C03;C15;C16                     |

## Interpretation

This second task reproduces the main diagnostic pattern if homogeneous route reuse has higher exposure localization and lower recall than route-partitioned search. Challenger results should be treated as intervention diagnostics, not final method evidence, unless they beat random baselines.
