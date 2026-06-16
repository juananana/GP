# Minimal Variable Generalization Test

Purpose: avoid inventing unnecessary geometry variables. We test whether coverage localization alone generalizes across simulated worlds, and whether adding coverage ratio or effective rank actually helps.

## Global In-Sample AUROC

| feature_set         | scope            | heldout_n_strata   |    n |    auroc |
|:--------------------|:-----------------|:-------------------|-----:|---------:|
| minimal_three       | global_in_sample | none               | 2160 | 0.995619 |
| gini_plus_erank     | global_in_sample | none               | 2160 | 0.995606 |
| gini_plus_coverage  | global_in_sample | none               | 2160 | 0.995232 |
| coverage_gini       | global_in_sample | none               | 2160 | 0.995124 |
| coverage_plus_erank | global_in_sample | none               | 2160 | 0.957247 |
| effective_rank      | global_in_sample | none               | 2160 | 0.897318 |
| coverage_ratio      | global_in_sample | none               | 2160 | 0.830444 |
| stopped_round       | global_in_sample | none               | 2160 | 0.50282  |

## Leave-World-Out AUROC

| feature_set         |   mean_leave_world_auroc |   min_leave_world_auroc |   folds |
|:--------------------|-------------------------:|------------------------:|--------:|
| gini_plus_coverage  |                 0.996299 |                0.993698 |       3 |
| coverage_gini       |                 0.996228 |                0.993553 |       3 |
| gini_plus_erank     |                 0.995991 |                0.9927   |       3 |
| minimal_three       |                 0.995935 |                0.992546 |       3 |
| coverage_plus_erank |                 0.981759 |                0.974265 |       3 |
| effective_rank      |                 0.977761 |                0.965297 |       3 |
| coverage_ratio      |                 0.819401 |                0.659319 |       3 |
| stopped_round       |                 0.497784 |                0.494215 |       3 |

## Interpretation

A variable should only enter the theory if it improves leave-world-out prediction or explains a distinct mechanism. If coverage Gini alone is competitive with richer feature sets, the paper should keep the core theory simple and use other metrics only as diagnostics.
