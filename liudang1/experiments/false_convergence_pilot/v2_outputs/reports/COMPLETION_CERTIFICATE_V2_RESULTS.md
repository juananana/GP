# Completion Certificate v2 Results

Generated at: `2026-06-09T11:17:40.495292+00:00`

## Scope

This is a deterministic offline diagnostic experiment. It creates new logged states from task source files. It is not a new online LLM blind run. Oracles are used only for offline scoring, residual missing mass, calibration, and audit-policy evaluation.

## Data

- Runs generated: `2970`
- Candidate/action log rows: `1572201`
- Pre-audit states: `2340`
- Safe states (`recall >= 0.95`): `439`
- Unsafe states: `1901`

## Train/Calibration/Test Split

| split       | repository        | task_family                 |   seed |   states |
|:------------|:------------------|:----------------------------|-------:|---------:|
| calibration | click             | real_repo_click_deprecation |      3 |      156 |
| calibration | local_policy_docs | synthetic_policy_docs       |      3 |      156 |
| calibration | requests          | real_repo_requests_tls      |      3 |      156 |
| test        | click             | real_repo_click_deprecation |      4 |      156 |
| test        | click             | real_repo_click_deprecation |      5 |      156 |
| test        | local_policy_docs | synthetic_policy_docs       |      4 |      156 |
| test        | local_policy_docs | synthetic_policy_docs       |      5 |      156 |
| test        | requests          | real_repo_requests_tls      |      4 |      156 |
| test        | requests          | real_repo_requests_tls      |      5 |      156 |
| train       | click             | real_repo_click_deprecation |      1 |      156 |
| train       | click             | real_repo_click_deprecation |      2 |      156 |
| train       | local_policy_docs | synthetic_policy_docs       |      1 |      156 |
| train       | local_policy_docs | synthetic_policy_docs       |      2 |      156 |
| train       | requests          | real_repo_requests_tls      |      1 |      156 |
| train       | requests          | real_repo_requests_tls      |      2 |      156 |

Split grouping is by `(repository, task_family, seed)`. No derived state from a group crosses splits.

## Feature Correlation With Residual Missing Mass

| feature                          |   pearson_with_residual_missing_mass |   spearman_with_residual_missing_mass |
|:---------------------------------|-------------------------------------:|--------------------------------------:|
| marginal_discovery_gain_mean     |                           -0.0597141 |                             -0.464267 |
| singletons_f1                    |                           -0.104282  |                             -0.423357 |
| marginal_discovery_gain_last     |                           -0.0503591 |                             -0.410756 |
| v1_risk_proxy                    |                            0.320966  |                              0.322536 |
| mean_confidence                  |                           -0.323091  |                             -0.310341 |
| corr_adjusted_chao_missing_ratio |                            0.0581545 |                             -0.277049 |
| chao_missing_ratio               |                            0.0656537 |                             -0.275763 |
| good_turing_missing_mass         |                            0.275664  |                              0.219359 |
| singleton_ratio                  |                            0.284067  |                              0.219301 |
| source_coverage                  |                           -0.114689  |                             -0.196053 |
| doubleton_ratio                  |                           -0.19484   |                             -0.183274 |
| doubletons_f2                    |                           -0.117893  |                             -0.183056 |

## v2 Risk Estimation and Calibration

SAFE thresholds are selected only on the calibration split using a Clopper-Pearson-style FCR upper bound target. This is an empirical calibration rule, not a distribution-free theoretical guarantee.

| method                          |    auroc |    auprc |     brier |        ece |        fcr |   fcr_upper |   safe_coverage |   abstention |   threshold |
|:--------------------------------|---------:|---------:|----------:|-----------:|-----------:|------------:|----------------:|-------------:|------------:|
| gradient_boosting               | 0.999361 | 0.999812 | 0.0179727 | 0.0756869  |   0.017341 |   0.0442064 |        0.965909 |     0.815171 |    0.378619 |
| decision_tree                   | 0.979822 | 0.992335 | 0.0416734 | 0.00582077 | nan        | nan         |        0        |     1        |  nan        |
| logistic_regression             | 0.944247 | 0.988754 | 0.0638937 | 0.0791526  | nan        | nan         |        0        |     1        |  nan        |
| regularized_logistic_regression | 0.90289  | 0.97787  | 0.103517  | 0.0826705  | nan        | nan         |        0        |     1        |  nan        |
| confidence_only                 | 0.641029 | 0.877342 | 0.54275   | 0.629214   | nan        | nan         |        0        |     1        |  nan        |
| good_turing_only                | 0.54674  | 0.826397 | 0.176807  | 0.18206    | nan        | nan         |        0        |     1        |  nan        |
| v1_handcrafted_rule             | 0.504755 | 0.837552 | 0.153312  | 0.163012   | nan        | nan         |        0        |     1        |  nan        |
| chao_only                       | 0.4855   | 0.855531 | 0.195501  | 0.212688   | nan        | nan         |        0        |     1        |  nan        |
| overlap_only                    | 0.483422 | 0.817819 | 0.74502   | 0.741472   | nan        | nan         |        0        |     1        |  nan        |
| no_new_item                     | 0.459282 | 0.84772  | 0.68605   | 0.722066   | nan        | nan         |        0        |     1        |  nan        |

## Audit Policy Test-Split Summary

| policy                   |   states |   pre_recall |   post_recall |   post_precision |   recovered_true_positives |   introduced_false_positives |   token_cost |   tool_calls |   wall_clock |   unnecessary_audit_rate |   cost_per_recovered_true_positive |
|:-------------------------|---------:|-------------:|--------------:|-----------------:|---------------------------:|-----------------------------:|-------------:|-------------:|-------------:|-------------------------:|-----------------------------------:|
| always_holdout           |      936 |     0.266988 |      1        |         0.540134 |                     121869 |                            0 |      2193642 |         5238 |     877.457  |               0.0042735  |                                 18 |
| boundary_focused_holdout |      936 |     0.266988 |      0.28282  |         0.204323 |                       2596 |                            0 |        46728 |          269 |      18.6912 |               0          |                                 18 |
| no_audit                 |      936 |     0.266988 |      0.266988 |         0.163077 |                          0 |                            0 |            0 |            0 |       0      |               0          |                                nan |
| random_holdout           |      936 |     0.266988 |      0.305725 |         0.264356 |                       7026 |                            0 |       126468 |          814 |      50.5872 |               0.0042735  |                                 18 |
| risk_triggered_audit     |      936 |     0.266988 |      0.535223 |         0.407145 |                      51548 |                            0 |       927864 |         2425 |     371.146  |               0.00106838 |                                 18 |
| singleton_audit          |      936 |     0.266988 |      0.266988 |         0.163077 |                          0 |                            0 |      4778352 |         1511 |    1911.34   |               0.134615   |                                nan |
| source_partitioned_audit |      936 |     0.266988 |      0.535366 |         0.407208 |                      51552 |                            0 |       927936 |         2426 |     371.174  |               0.00106838 |                                 18 |

## Output Files

- `run_logs/v2_candidate_logs.csv`
- `run_logs/v2_runs.json`
- `state_logs/v2_states.json`
- `features/v2_state_features.csv`
- `features/v2_feature_correlations.csv`
- `models/v2_model_metrics.json`
- `models/v2_risk_coverage_curve.csv`
- `models/v2_audit_policy_eval.csv`
- `figures/v2_feature_residual_correlation.png`
- `figures/v2_risk_coverage_curve.png`
- `figures/v2_calibration_curve_v1_proxy.png`

## TODO

- Run online LLM agents with the same logging schema when API/runtime budget is available.
- Replace deterministic holdout simulations with real post-audit agent traces.
- Run SeekerGym once a local checkout/schema is available.
- Inspect learned-model stability before promoting v2 to the paper's main method.
