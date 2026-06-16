# Exposure Localization Simulation v3

This version tests the user's key refinement: distinguish search exposure localization from discovered-evidence localization.

## Core Question

> Is false stopping better explained by localized exposure than by localized discoveries?

## Metric Screening

| metric                   |    n |   spearman_with_false |   spearman_p |   auroc_abs_direction |   auprc_raw_direction |
|:-------------------------|-----:|----------------------:|-------------:|----------------------:|----------------------:|
| discovery_gini           | 2700 |             0.595236  | 1.37198e-258 |              0.84534  |              0.856013 |
| exposure_gini            | 2700 |             0.595027  | 2.30693e-258 |              0.845218 |              0.860971 |
| effective_rank_discovery | 2700 |            -0.477943  | 3.76572e-154 |              0.77729  |              0.391692 |
| exposure_coverage_ratio  | 2700 |            -0.500559  | 3.21186e-171 |              0.770693 |              0.415751 |
| discovery_coverage_ratio | 2700 |            -0.500559  | 3.21186e-171 |              0.770693 |              0.415751 |
| scout_novelty_per_cost   | 1080 |             0.205412  | 9.39215e-12  |              0.767386 |              0.107849 |
| effective_rank_exposure  | 2700 |            -0.459198  | 6.05731e-141 |              0.766414 |              0.394831 |
| discovery_per_exposure   | 2700 |             0.215655  | 8.88689e-30  |              0.625075 |              0.591501 |
| discovery_hhi            | 2700 |             0.18215   | 1.42359e-21  |              0.605679 |              0.675675 |
| exposure_hhi             | 2700 |             0.176375  | 2.63251e-20  |              0.602328 |              0.675215 |
| exposure_max_mass        | 2700 |             0.145538  | 2.97617e-14  |              0.58432  |              0.635221 |
| exposure_entropy         | 2700 |            -0.143322  | 7.29624e-14  |              0.583151 |              0.477865 |
| discovery_entropy        | 2700 |            -0.135026  | 1.85237e-12  |              0.578338 |              0.480876 |
| discovery_max_mass       | 2700 |             0.0944169 | 8.88931e-07  |              0.554777 |              0.593011 |

## Cross-World Stability

| metric                   |   n_strata |   spearman_with_false |   auroc_abs_direction |
|:-------------------------|-----------:|----------------------:|----------------------:|
| exposure_gini            |         18 |              0.698633 |              0.903416 |
| exposure_gini            |         30 |              0.669464 |              0.887211 |
| exposure_gini            |         42 |              0.685729 |              0.909255 |
| discovery_gini           |         18 |              0.716293 |              0.913617 |
| discovery_gini           |         30 |              0.672504 |              0.888971 |
| discovery_gini           |         42 |              0.680507 |              0.906139 |
| exposure_coverage_ratio  |         18 |             -0.320701 |              0.624133 |
| exposure_coverage_ratio  |         30 |             -0.544984 |              0.799099 |
| exposure_coverage_ratio  |         42 |             -0.60999  |              0.858969 |
| discovery_coverage_ratio |         18 |             -0.320701 |              0.624133 |
| discovery_coverage_ratio |         30 |             -0.544984 |              0.799099 |
| discovery_coverage_ratio |         42 |             -0.60999  |              0.858969 |
| effective_rank_exposure  |         18 |             -0.540888 |              0.812331 |
| effective_rank_exposure  |         30 |             -0.474835 |              0.774641 |
| effective_rank_exposure  |         42 |             -0.507155 |              0.80268  |
| effective_rank_discovery |         18 |             -0.591694 |              0.841668 |
| effective_rank_discovery |         30 |             -0.527438 |              0.805066 |
| effective_rank_discovery |         42 |             -0.574052 |              0.842605 |

## Condition and Challenger Summary

|                                             |   runs |   false_rate |   mean_recall |   exposure_gini |   discovery_gini |   exposure_coverage |   discovery_coverage |   scout_new_items |   scout_gain |
|:--------------------------------------------|-------:|-------------:|--------------:|----------------:|-----------------:|--------------------:|---------------------:|------------------:|-------------:|
| ('extended_audit', 'low_discovery')         |    540 |    0.0425926 |      0.970287 |        0.260283 |         0.228346 |            0.982537 |             0.982537 |           18.6796 |     0.327503 |
| ('homogeneous', 'none')                     |    540 |    0.998148  |      0.75011  |        0.364586 |         0.334641 |            0.931223 |             0.931223 |            0      |   nan        |
| ('low_exposure_challenger', 'low_exposure') |    540 |    0.0611111 |      0.970054 |        0.292589 |         0.246205 |            0.978839 |             0.978839 |           21.763  |     0.385529 |
| ('prompt_diverse', 'none')                  |    540 |    1         |      0.749361 |        0.383856 |         0.341133 |            0.932216 |             0.932216 |            0      |   nan        |
| ('route_partitioned', 'none')               |    540 |    0.644444  |      0.851445 |        0.294361 |         0.247038 |            0.979436 |             0.979436 |            0      |   nan        |

## Interpretation

Exposure Gini measures where the workflow searched, including failed searches. Discovery Gini measures where it found items. If exposure Gini is stronger, the theory should be local exhaustion under localized search. If discovery Gini is stronger, the theory should remain evidence localization.

The low-exposure challenger is the natural implementation: when no-new stopping is triggered under high exposure localization, audit the least-exposed strata rather than dispatching another free-search agent.
