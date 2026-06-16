# Controller Validation v1 on External Requests

## Purpose

This is not a new method search. It tests whether the existing residual-potential challenger behaves like evidence-condition repair rather than only item recovery.

## Controller Rule

Runtime-only stop decision:

- accept `SAFE` only if source-route support ratio is at least `0.75`, exposure Gini is at most `0.7`, and repair/audit produces no new residual evidence;
- otherwise run a challenger;
- after repair, output `SAFE` only if the evidence condition passes the same support/Gini check and no residual evidence appears;
- output `CONTINUE` if repair finds new scored evidence;
- output `ABSTAIN` if the certificate remains too narrow.

The thresholds are operational test points, not a claimed theory law.

## Base State

| condition         |   base_recall | base_false_certificate_if_stop_accepted   |   base_support_size |   base_support_ratio |   base_exposure_gini |   base_weak_plausible_gap | base_safe_by_condition   |   safe_coverage_min |   safe_gini_max |
|:------------------|--------------:|:------------------------------------------|--------------------:|---------------------:|---------------------:|--------------------------:|:-------------------------|--------------------:|----------------:|
| homogeneous       |      0.104027 | True                                      |                   6 |                 0.25 |             0.888514 |                        15 | False                    |                0.75 |             0.7 |
| route_partitioned |      1        | False                                     |                  24 |                 1    |             0.607402 |                         0 | True                     |                0.75 |             0.7 |

The same kind of blind stop signal appears in both conditions, but the evidence
condition differs sharply. The homogeneous condition has localized support and is
not eligible for a global completion certificate. The route-partitioned condition
has broad source-route support and, in the observed full run, passes the operational SAFE check.

## Matched Evidence Perturbation

| state                               | note                                                          |   discovered_true_items |   recall |   support_size |   support_ratio |   exposure_gini |   weak_plausible_gap | same_stop_signal   | naive_accepts_stop   | naive_false_certification   | controller_decision   | controller_false_certification   |
|:------------------------------------|:--------------------------------------------------------------|------------------------:|---------:|---------------:|----------------:|----------------:|---------------------:|:-------------------|:---------------------|:----------------------------|:----------------------|:---------------------------------|
| homogeneous_observed_stop           | observed local stop evidence                                  |                      31 | 0.104027 |              6 |            0.25 |        0.888514 |                   15 | True               | True                 | True                        | ABSTAIN               | False                            |
| route_partitioned_matched_discovery | same discovered-count ledger with broad source-route exposure |                      31 | 0.104027 |             24 |            1    |        0.540152 |                    0 | True               | True                 | True                        | CONTINUE              | False                            |
| route_partitioned_observed_stop     | observed broad stop evidence                                  |                     298 | 1        |             24 |            1    |        0.607402 |                    0 | True               | True                 | False                       | SAFE                  | False                            |

This table is the mechanism check. The matched-discovery counterfactual holds
the scored discovery count at the homogeneous level but broadens the evidence
condition using only route-partitioned runtime traces. Under a naive stop rule,
both low-recall states would be accepted. Under the evidence-condition controller,
the localized state is rejected. The broad matched-count state is not accepted as
SAFE because evidence is still appearing. This is the key boundary: broad exposure
is necessary for a global certificate, but it is not sufficient by itself.

## Challenger Controller Summary

| challenger               |   runs |   mean_support_expansion |   mean_support_gap_reduction |   mean_after_support_ratio |   mean_after_exposure_gini |   mean_new_true_items |   mean_cumulative_recall |   safe_rate |   continue_rate |   abstain_rate |   false_certification_rate |   false_stop_reduction_rate |   abstain_correct_rate |
|:-------------------------|-------:|-------------------------:|-----------------------------:|---------------------------:|---------------------------:|----------------------:|-------------------------:|------------:|----------------:|---------------:|---------------------------:|----------------------------:|-----------------------:|
| high_potential           |    200 |                    4     |                        4     |                   0.416667 |                   0.869203 |               177     |                 0.697987 |           0 |           1     |          0     |                          0 |                           1 |                  0     |
| residual_potential       |    200 |                    4     |                        4     |                   0.416667 |                   0.869203 |               177     |                 0.697987 |           0 |           1     |          0     |                          0 |                           1 |                  0     |
| free_search_continuation |    200 |                    3.61  |                        3.61  |                   0.400417 |                   0.87158  |               126.415 |                 0.528238 |           0 |           1     |          0     |                          0 |                           1 |                  0     |
| low_discovery            |    200 |                    4     |                        3     |                   0.416667 |                   0.869203 |               106     |                 0.459732 |           0 |           1     |          0     |                          0 |                           1 |                  0     |
| low_exposure             |    200 |                    4     |                        3     |                   0.416667 |                   0.869203 |               106     |                 0.459732 |           0 |           1     |          0     |                          0 |                           1 |                  0     |
| random                   |    200 |                    3.055 |                        2.535 |                   0.377292 |                   0.873822 |                45.535 |                 0.256829 |           0 |           0.995 |          0.005 |                          0 |                           1 |                  0.005 |

## Interpretation

The external `requests` task still supports the diagnostic: the base homogeneous stop has very narrow source-route support and would be a false certification if accepted. The route-partitioned condition has the same stop-command structure but broad source-route exposure and reaches full bounded-oracle recall.

For intervention, the result is mixed. Residual-potential repairs weak source-route support and reduces false certification by forcing `CONTINUE`, but high-potential-only ties it on this external task. Therefore the current honest claim is:

```text
source-route exposure localization is a strong completion-certificate diagnostic;
residual-potential is a mechanism-aligned repair candidate;
the product rule is not yet proven uniquely better than high-potential repair.
```
