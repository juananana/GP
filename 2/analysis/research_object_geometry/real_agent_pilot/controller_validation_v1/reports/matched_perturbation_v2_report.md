# Matched Perturbation v2 Report

## Purpose

Strengthen the mechanism test: broad exposure should grant completion eligibility, not automatically certify SAFE.

## Results

| state              | note                                                              |   discovered_true_items |   recall |   support_ratio |   exposure_gini |   weak_plausible_gap | geometry_eligible   | evidence_still_appearing   | controller_decision   | false_certification_if_safe   |
|:-------------------|:------------------------------------------------------------------|------------------------:|---------:|----------------:|----------------:|---------------------:|:--------------------|:---------------------------|:----------------------|:------------------------------|
| local_observed_31  | observed homogeneous local evidence                               |                      31 | 0.104027 |            0.25 |        0.888514 |                   15 | False               | False                      | ABSTAIN               | False                         |
| broad_matched_31   | same discovered count as homogeneous, broad source-route searches |                      31 | 0.104027 |            1    |        0.540152 |                    0 | True                | True                       | CONTINUE              | False                         |
| broad_prefix_100   | broad exposure with medium continuing evidence                    |                     100 | 0.33557  |            1    |        0.745296 |                    0 | False               | True                       | CONTINUE              | False                         |
| broad_prefix_200   | broad exposure with high continuing evidence                      |                     200 | 0.671141 |            1    |        0.713914 |                    0 | False               | True                       | CONTINUE              | False                         |
| broad_observed_298 | observed route-partitioned completed audit                        |                     298 | 1        |            1    |        0.607402 |                    0 | True                | False                      | SAFE                  | False                         |

## Interpretation

The matched `31` case is the key control. It has the same discovered count as the local homogeneous stop but broad source-route exposure. The controller still outputs `CONTINUE`, because evidence is still appearing. This supports the refined mechanism:

```text
source-route exposure geometry controls whether completion evidence is eligible;
SAFE additionally requires that repair/audit no longer reveals residual evidence.
```

This prevents the paper from overclaiming that coverage geometry alone proves completion.
