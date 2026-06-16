# Cross-Task Synthesis Report

## Scope

This synthesis freezes the current evidence without changing the paper mainline. It aggregates four task families: `policy_docset_v1`, `code_repo_v1`, `requests`, and `urllib3`.

## Unified Result Table

| task             |   base_support_ratio |   base_exposure_gini |   base_recall | base_false_certification_if_stop   | base_controller_decision   |   broad_support_ratio |   broad_exposure_gini |   broad_recall | broad_controller_decision   |   residual_repair_gain |   high_potential_repair_gain |   residual_cost_normalized_evidence |   high_potential_cost_normalized_evidence |   residual_high_overlap_jaccard |
|:-----------------|---------------------:|---------------------:|--------------:|:-----------------------------------|:---------------------------|----------------------:|----------------------:|---------------:|:----------------------------|-----------------------:|-----------------------------:|------------------------------------:|------------------------------------------:|--------------------------------:|
| policy_docset_v1 |             0.25     |             0.770833 |      0.708333 | True                               | CONTINUE                   |                  0.75 |              0.385417 |       1        | SAFE                        |                      4 |                            0 |                           0.125     |                                 0         |                      nan        |
| code_repo_v1     |             0.333333 |             0.75     |      0.3      | True                               | CONTINUE                   |                  1    |              0.199495 |       0.95     | SAFE                        |                      9 |                            5 |                           0.136364  |                                 0.0757576 |                      nan        |
| requests         |             0.25     |             0.888514 |      0.104027 | True                               | CONTINUE                   |                  1    |              0.607402 |       1        | SAFE                        |                    177 |                          177 |                           0.0542612 |                                 0.0542612 |                        1        |
| urllib3          |             0.2      |             0.91513  |      0.193133 | True                               | CONTINUE                   |                  0.8  |              0.647149 |       0.835479 | CONTINUE                    |                    329 |                          275 |                           0.0622046 |                                 0.0626995 |                        0.666667 |

## Evidence Chain

Across all four tasks, homogeneous route reuse produces localized evidence conditions and would be unsafe if accepted as a global completion certificate. Broader source-route evidence improves completion eligibility, but the `urllib3` route-partitioned case shows that broad exposure alone is not sufficient: it is geometry-eligible but still below the 0.90 oracle threshold, so the controller outputs `CONTINUE`.

The strongest supported contribution is therefore:

```text
evidence-condition diagnostic/controller prevents locally conditioned evidence from being accepted as global completion proof.
```

## Repair Evidence

Residual-potential is positive but bounded. It beats random and simple low-exposure in several source-route settings, ties high-potential exactly on `requests`, and improves total repair gain on `urllib3` while having similar or slightly worse cost efficiency than high-potential.

## Boundary

The current evidence does not prove residual-potential optimality. It supports residual-potential as a mechanism-aligned repair instance.
