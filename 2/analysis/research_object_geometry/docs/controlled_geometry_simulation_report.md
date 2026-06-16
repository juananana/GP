# Controlled Coverage-Geometry Simulation Report

Status: controlled mechanism construction. This is not real-agent evidence and not a method claim.

## Purpose

We test whether a bottom-up closed-world discovery environment can exhibit false stopping controlled by measurable coverage geometry. This answers a necessary precondition: if geometry cannot be made predictive in a clean mechanism model, it is unlikely to be the right research core.

## Construction

- A world contains hidden target items distributed over source-route strata.
- Easy strata are oversampled; hard strata contain valid items but are less likely under correlated exploration.
- Three main agents sample strata over rounds and stop after repeated low novelty.
- Conditions vary exploration dependence and route assignment.
- Oracle recall is available only after the run.

## Label Balance

| false_completion   |   count |
|:-------------------|--------:|
| True               |    2484 |
| False              |    1116 |

## Condition Summary

| condition         |   runs |   false_rate |   mean_recall |   mean_source_coverage |   mean_erank |   mean_hhi |   scout_gain |
|:------------------|-------:|-------------:|--------------:|-----------------------:|-------------:|-----------:|-------------:|
| extended_audit    |    720 |     0.555556 |      0.867158 |               0.983232 |     0.79791  |  0.0442115 |   nan        |
| homogeneous       |    720 |     1        |      0.750917 |               0.931217 |     0.703481 |  0.0506124 |   nan        |
| prompt_diverse    |    720 |     1        |      0.749401 |               0.932641 |     0.733828 |  0.0508182 |   nan        |
| residual_targeted |    720 |     0.245833 |      0.938307 |               0.999967 |     0.72535  |  0.0435822 |     0.635458 |
| route_partitioned |    720 |     0.648611 |      0.851041 |               0.979663 |     0.830405 |  0.045097  |   nan        |

## Metric Screening

| metric                           |    n |   spearman_with_false |   spearman_p |   auroc_abs_direction |   auprc_raw_direction |
|:---------------------------------|-----:|----------------------:|-------------:|----------------------:|----------------------:|
| coverage_gini                    | 3600 |              0.709649 | 0            |              0.942943 |              0.973491 |
| scout_novelty_per_cost           |  720 |             -0.534528 | 1.91911e-54  |              0.857946 |              0.165546 |
| source_coverage_ratio            | 3600 |             -0.542986 | 2.9175e-275  |              0.804662 |              0.552346 |
| source_logdet_volume             | 3600 |             -0.415294 | 3.96745e-150 |              0.759215 |              0.533354 |
| pairwise_route_jaccard           | 3600 |             -0.363027 | 1.41402e-112 |              0.726546 |              0.542842 |
| pairwise_cosine                  | 3600 |              0.248053 | 1.29322e-51  |              0.654827 |              0.7566   |
| source_normalized_effective_rank | 3600 |             -0.244482 | 3.8093e-50   |              0.652598 |              0.572391 |
| visit_entropy                    | 3600 |              0.132305 | 1.57921e-15  |              0.582581 |              0.71944  |
| visit_hhi                        | 3600 |             -0.107286 | 1.09272e-10  |              0.566965 |              0.647613 |
| coverage_hhi                     | 3600 |              0.032196 | 0.0534103    |              0.520096 |              0.763395 |

## Cross-World Stability

| metric                           |   n_strata |   spearman_with_false |   auroc_abs_direction |
|:---------------------------------|-----------:|----------------------:|----------------------:|
| source_coverage_ratio            |         18 |            -0.401135  |              0.652819 |
| source_coverage_ratio            |         30 |            -0.661404  |              0.870002 |
| source_coverage_ratio            |         42 |            -0.44149   |              0.852966 |
| coverage_gini                    |         18 |             0.854546  |              0.997168 |
| coverage_gini                    |         30 |             0.778765  |              0.97159  |
| coverage_gini                    |         42 |             0.552594  |              0.956342 |
| coverage_hhi                     |         18 |             0.858624  |              0.99954  |
| coverage_hhi                     |         30 |             0.778313  |              0.971316 |
| coverage_hhi                     |         42 |             0.552277  |              0.956081 |
| coverage_entropy                 |         18 |            -0.858997  |              0.999757 |
| coverage_entropy                 |         30 |            -0.780798  |              0.972821 |
| coverage_entropy                 |         42 |            -0.555216  |              0.958507 |
| source_normalized_effective_rank |         18 |            -0.473729  |              0.775612 |
| source_normalized_effective_rank |         30 |            -0.311619  |              0.688705 |
| source_normalized_effective_rank |         42 |            -0.355932  |              0.793935 |
| source_logdet_volume             |         18 |            -0.500172  |              0.790996 |
| source_logdet_volume             |         30 |            -0.367407  |              0.722487 |
| source_logdet_volume             |         42 |            -0.402074  |              0.83204  |
| pairwise_route_jaccard           |         18 |            -0.50039   |              0.78959  |
| pairwise_route_jaccard           |         30 |            -0.39686   |              0.740308 |
| pairwise_route_jaccard           |         42 |             0.0641387 |              0.552967 |

## Interpretation

In this controlled construction, a geometry signal does exist, but it is mostly the simple geometry of source-route coverage localization. The strongest candidate control quantity is coverage Gini: discovered evidence becomes concentrated in a small subset of strata while the workflow's novelty signal is exhausted. Source coverage ratio is also useful. Effective rank and log-det are informative but weaker than this localization signal.

This means the current best hypothesis is not yet a Grassmann/subspace theory. It is a coverage-localization or coverage-saturation theory: false stopping emerges when observed novelty is exhausted inside a locally concentrated explored region while global source-route coverage remains incomplete.

## Go / No-Go

Go for a small real-agent diagnostic, not yet for a geometry method paper.

The next real experiment should test whether source-route coverage ratio, coverage concentration, and effective rank retain predictive value when generated by actual agent trajectories. If simple source coverage dominates, the paper should stay with safe stopping and evidence-ledger control rather than advanced geometry.
