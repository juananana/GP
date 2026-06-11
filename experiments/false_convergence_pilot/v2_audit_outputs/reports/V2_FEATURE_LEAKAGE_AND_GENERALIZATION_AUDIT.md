# v2 Feature Leakage and Generalization Audit

## Scope

This audit reads the frozen v2 offline diagnostic feature table and writes new audit outputs. It does not modify v2_outputs and does not tune the frozen v2 test set.

## Leakage Check

- Feature columns missing from table: `[]`
- Forbidden oracle/label columns used as features: `[]`
- ID/task/repository shortcut columns used as features: `[]`
- Post-audit/cost columns used as features: `[]`
- Stage values: `['pre_audit']`
- Collection modes: `['deterministic_offline_scanner']`

Important table columns such as `recall`, `true_positive`, `residual_missing_mass`, and `unsafe` are present for offline scoring, but they are not in the declared v2 feature set.

## Metadata Shortcut Probe

| experiment              | model                           | train_groups                                                                                                                                                                                                                          | calibration_groups                                                                                                 | test_groups                                                                                                                                                                                                                           | features                                                                                             |   n_train |   n_calibration |   n_test |   unsafe_rate_test |    auroc |    auprc |     brier | threshold   |   certified |   false_certifications | false_certification_rate   | fcr_upper   |   safe_coverage |   abstention |
|:------------------------|:--------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------|----------:|----------------:|---------:|-------------------:|---------:|---------:|----------:|:------------|------------:|-----------------------:|:---------------------------|:------------|----------------:|-------------:|
| metadata_shortcut_probe | gradient_boosting_metadata_only | local_policy_docs/synthetic_policy_docs/s1;local_policy_docs/synthetic_policy_docs/s2;click/real_repo_click_deprecation/s1;click/real_repo_click_deprecation/s2;requests/real_repo_requests_tls/s1;requests/real_repo_requests_tls/s2 | local_policy_docs/synthetic_policy_docs/s3;click/real_repo_click_deprecation/s3;requests/real_repo_requests_tls/s3 | local_policy_docs/synthetic_policy_docs/s4;local_policy_docs/synthetic_policy_docs/s5;click/real_repo_click_deprecation/s4;click/real_repo_click_deprecation/s5;requests/real_repo_requests_tls/s4;requests/real_repo_requests_tls/s5 | task_id,repository,task_family,agent_condition,search_strategy,budget_level,nominal_agent_count,seed |       936 |             468 |      936 |           0.811966 | 0.988083 | 0.996786 | 0.0358196 |             |           0 |                      0 |                            |             |               0 |            1 |

This probe intentionally uses task/repository/search/budget metadata to measure shortcut risk. It is not a valid proposed method.

## Feature Ablation

| experiment                                 | model                |   n_train |   n_calibration |   n_test |    auroc |    auprc |     brier |   certified |   false_certifications |   false_certification_rate |   fcr_upper |   safe_coverage |   abstention |
|:-------------------------------------------|:---------------------|----------:|----------------:|---------:|---------:|---------:|----------:|------------:|-----------------------:|---------------------------:|------------:|----------------:|-------------:|
| feature_ablation:all_allowed               | regularized_logistic |       936 |             468 |      936 | 0.90289  | 0.97787  | 0.103517  |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:all_allowed               | gradient_boosting    |       936 |             468 |      936 | 0.999361 | 0.999812 | 0.0179727 |         173 |                      3 |                  0.017341  |   0.0442064 |        0.965909 |     0.815171 |
| feature_ablation:portable_only             | regularized_logistic |       936 |             468 |      936 | 0.859334 | 0.960141 | 0.116683  |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:portable_only             | gradient_boosting    |       936 |             468 |      936 | 0.996931 | 0.999251 | 0.025953  |         169 |                      3 |                  0.0177515 |   0.0452379 |        0.943182 |     0.819444 |
| feature_ablation:no_confidence             | regularized_logistic |       936 |             468 |      936 | 0.88627  | 0.975499 | 0.105828  |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:no_confidence             | gradient_boosting    |       936 |             468 |      936 | 0.999361 | 0.999812 | 0.0180118 |         173 |                      3 |                  0.017341  |   0.0442064 |        0.965909 |     0.815171 |
| feature_ablation:no_overlap_or_correlation | regularized_logistic |       936 |             468 |      936 | 0.902718 | 0.977852 | 0.103549  |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:no_overlap_or_correlation | gradient_boosting    |       936 |             468 |      936 | 0.999189 | 0.999771 | 0.0179307 |         171 |                      3 |                  0.0175439 |   0.0447162 |        0.954545 |     0.817308 |
| feature_ablation:no_source_path            | regularized_logistic |       936 |             468 |      936 | 0.887175 | 0.973494 | 0.106598  |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:no_source_path            | gradient_boosting    |       936 |             468 |      936 | 0.993619 | 0.998318 | 0.0327242 |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:no_marginal_novelty       | regularized_logistic |       936 |             468 |      936 | 0.882584 | 0.967076 | 0.107736  |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:no_marginal_novelty       | gradient_boosting    |       936 |             468 |      936 | 0.997148 | 0.999203 | 0.0194653 |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:no_missing_mass_counts    | regularized_logistic |       936 |             468 |      936 | 0.765517 | 0.93462  | 0.12866   |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:no_missing_mass_counts    | gradient_boosting    |       936 |             468 |      936 | 0.999193 | 0.999769 | 0.0198402 |         167 |                      3 |                  0.0179641 |   0.045772  |        0.931818 |     0.821581 |
| feature_ablation:confidence_only           | regularized_logistic |       936 |             468 |      936 | 0.641029 | 0.877342 | 0.145623  |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:confidence_only           | gradient_boosting    |       936 |             468 |      936 | 0.649873 | 0.878627 | 0.144909  |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:counts_only               | regularized_logistic |       936 |             468 |      936 | 0.816089 | 0.950349 | 0.120697  |           0 |                      0 |                nan         | nan         |        0        |     1        |
| feature_ablation:counts_only               | gradient_boosting    |       936 |             468 |      936 | 0.992546 | 0.998046 | 0.0353149 |           0 |                      0 |                nan         | nan         |        0        |     1        |

## Leave-One-Repository-Out

| experiment                             | model                |   n_train |   n_calibration |   n_test |   unsafe_rate_test |    auroc |    auprc |     brier |   certified |   false_certifications | false_certification_rate   | fcr_upper   |   safe_coverage |   abstention |
|:---------------------------------------|:---------------------|----------:|----------------:|---------:|-------------------:|---------:|---------:|----------:|------------:|-----------------------:|:---------------------------|:------------|----------------:|-------------:|
| leave_one_repository:click             | regularized_logistic |       624 |             312 |      780 |           0.985897 | 0.550301 | 0.974321 | 0.171145  |           0 |                      0 |                            |             |               0 |            1 |
| leave_one_repository:click             | gradient_boosting    |       624 |             312 |      780 |           0.985897 | 0.590732 | 0.987946 | 0.0656688 |           0 |                      0 |                            |             |               0 |            1 |
| leave_one_repository:local_policy_docs | regularized_logistic |       624 |             312 |      780 |           0.45641  | 0.141589 | 0.305993 | 0.53291   |           0 |                      0 |                            |             |               0 |            1 |
| leave_one_repository:local_policy_docs | gradient_boosting    |       624 |             312 |      780 |           0.45641  | 0.545745 | 0.480378 | 0.494849  |           0 |                      0 |                            |             |               0 |            1 |
| leave_one_repository:requests          | regularized_logistic |       624 |             312 |      780 |           0.994872 | 0.390464 | 0.994626 | 0.170544  |           0 |                      0 |                            |             |               0 |            1 |
| leave_one_repository:requests          | gradient_boosting    |       624 |             312 |      780 |           0.994872 | 0.69491  | 0.99814  | 0.0345326 |           0 |                      0 |                            |             |               0 |            1 |

## Leave-One-Task-Family-Out

| experiment                                        | model                |   n_train |   n_calibration |   n_test |   unsafe_rate_test |    auroc |    auprc |     brier |   certified |   false_certifications | false_certification_rate   | fcr_upper   |   safe_coverage |   abstention |
|:--------------------------------------------------|:---------------------|----------:|----------------:|---------:|-------------------:|---------:|---------:|----------:|------------:|-----------------------:|:---------------------------|:------------|----------------:|-------------:|
| leave_one_task_family:real_repo_click_deprecation | regularized_logistic |       624 |             312 |      780 |           0.985897 | 0.550301 | 0.974321 | 0.171145  |           0 |                      0 |                            |             |               0 |            1 |
| leave_one_task_family:real_repo_click_deprecation | gradient_boosting    |       624 |             312 |      780 |           0.985897 | 0.590732 | 0.987946 | 0.0656688 |           0 |                      0 |                            |             |               0 |            1 |
| leave_one_task_family:real_repo_requests_tls      | regularized_logistic |       624 |             312 |      780 |           0.994872 | 0.390464 | 0.994626 | 0.170544  |           0 |                      0 |                            |             |               0 |            1 |
| leave_one_task_family:real_repo_requests_tls      | gradient_boosting    |       624 |             312 |      780 |           0.994872 | 0.69491  | 0.99814  | 0.0345326 |           0 |                      0 |                            |             |               0 |            1 |
| leave_one_task_family:synthetic_policy_docs       | regularized_logistic |       624 |             312 |      780 |           0.45641  | 0.141589 | 0.305993 | 0.53291   |           0 |                      0 |                            |             |               0 |            1 |
| leave_one_task_family:synthetic_policy_docs       | gradient_boosting    |       624 |             312 |      780 |           0.45641  | 0.545745 | 0.480378 | 0.494849  |           0 |                      0 |                            |             |               0 |            1 |

## Interpretation

- The declared v2 features pass the direct column-level leakage check.
- Repository and task-family are currently one-to-one in the offline diagnostic, so leave-one-repository-out and leave-one-task-family-out are equivalent stress tests in this data.
- Any high in-distribution score should be treated cautiously unless it remains stable under these held-out repository/task-family splits and later online blind validation.
