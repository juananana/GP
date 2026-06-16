# Controlled Geometry Simulation v2

This version isolates the candidate order parameter:

> lambda = coverage_gini * (1 - source_coverage_ratio)

It asks whether a simple coverage-localization risk quantity is stronger than the individual ingredients.

## Condition Summary

| condition         |   runs |   false_rate |   mean_recall |   mean_risk |   mean_gini |   mean_coverage |   mean_erank |   scout_gain |
|:------------------|-------:|-------------:|--------------:|------------:|------------:|----------------:|-------------:|-------------:|
| extended_audit    |    540 |     0.546296 |      0.870194 |  0.00533403 |    0.227417 |        0.985297 |     0.804132 |     0.116267 |
| homogeneous       |    540 |     1        |      0.750071 |  0.0264083  |    0.334742 |        0.929377 |     0.70031  |   nan        |
| prompt_diverse    |    540 |     1        |      0.749775 |  0.0255916  |    0.341862 |        0.932501 |     0.736634 |   nan        |
| route_partitioned |    540 |     0.637037 |      0.848904 |  0.00785247 |    0.248217 |        0.978228 |     0.826853 |     0.3937   |

## Dependency Summary

|   dependency |   false_rate |   mean_recall |   mean_lambda |   mean_gini |   mean_coverage |
|-------------:|-------------:|--------------:|--------------:|------------:|----------------:|
|         0    |     0.508333 |      0.853131 |     0.0134907 |    0.233323 |        0.964947 |
|         0.25 |     0.616667 |      0.840962 |     0.0139227 |    0.25406  |        0.962773 |
|         0.5  |     0.772222 |      0.821278 |     0.0127063 |    0.280634 |        0.966019 |
|         0.75 |     0.883333 |      0.791022 |     0.0145145 |    0.306736 |        0.960379 |
|         0.9  |     0.994444 |      0.767966 |     0.0191538 |    0.322606 |        0.94843  |
|         0.98 |     1        |      0.754056 |     0.0239915 |    0.330998 |        0.935556 |

## Metric Screening

| metric                           |    n |   spearman_with_false |   spearman_p |   auroc_abs_direction |   auprc_raw_direction |
|:---------------------------------|-----:|----------------------:|-------------:|----------------------:|----------------------:|
| coverage_gini                    | 2160 |              0.691366 | 5.931e-307   |              0.995124 |              0.998736 |
| source_normalized_effective_rank | 2160 |             -0.554795 | 1.26449e-174 |              0.897318 |              0.614627 |
| scout_novelty_per_cost           | 1080 |              0.611516 | 9.3306e-112  |              0.858651 |              0.907985 |
| coverage_risk_lambda             | 2160 |              0.488135 | 1.01202e-129 |              0.830605 |              0.930987 |
| source_coverage_ratio            | 2160 |             -0.488268 | 8.42609e-130 |              0.830444 |              0.669338 |
| coverage_hhi                     | 2160 |              0.109582 | 3.30213e-07  |              0.578477 |              0.858533 |
| coverage_entropy                 | 2160 |             -0.052482 | 0.0147112    |              0.537585 |              0.758606 |
| stopped_round                    | 2160 |              0.047301 | 0.0279271    |              0.50282  |              0.796751 |

## Challenger Ablation

|                                       |   runs |   false_rate |   mean_recall |   mean_gini |   mean_coverage |   scout_new_items |   scout_gain |
|:--------------------------------------|-------:|-------------:|--------------:|------------:|----------------:|------------------:|-------------:|
| ('extended_audit', 'risk_weighted')   |    540 |     0.546296 |      0.870194 |    0.227417 |        0.985297 |           7.24815 |     0.116267 |
| ('homogeneous', 'none')               |    540 |     1        |      0.750071 |    0.334742 |        0.929377 |           0       |   nan        |
| ('prompt_diverse', 'none')            |    540 |     1        |      0.749775 |    0.341862 |        0.932501 |           0       |   nan        |
| ('route_partitioned', 'low_coverage') |    540 |     0.637037 |      0.848904 |    0.248217 |        0.978228 |          22.1389  |     0.3937   |

## Interpretation

The compound lambda risk does not beat plain coverage Gini in this construction. The theory should therefore stay with plain coverage localization first, rather than overfitting a compound formula.

The residual challenger is operationally defined by the same geometry: target source-route strata with low observed coverage under high localization. This turns the geometry into a search policy without claiming an advanced geometric controller.
