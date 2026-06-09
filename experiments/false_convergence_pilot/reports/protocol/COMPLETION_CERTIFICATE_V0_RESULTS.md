# Completion Certificate v0 Results

The certificate uses only observable run signals for decisions. Oracle labels are used only afterward to evaluate whether a stop decision would have been safe.

## Seed-Level Certificates

| case | seed | reportable | consensus_recall | union_precision | mean_conf | mean_jaccard | f1 | GT mass | Chao miss | risk | label | flags |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| T1_hard_expanded | seed01 | true | 0.629 | 1.000 | 0.853 | 0.752 | 13 | 0.165 | 0.690 | 0.600 | unsafe_to_stop | singleton_missing_mass, chao_unseen_mass |
| T1_hard_expanded | seed02 | true | 1.000 | 0.897 | 0.907 | 0.932 | 4 | 0.037 | 0.133 | 0.589 | requires_audit | singleton_missing_mass, chao_unseen_mass, low_effective_independence |
| T1_hard_seed03_completed | seed03 | true | 1.000 | 0.875 | 0.893 | 0.685 | 5 | 0.052 | 0.023 | 0.350 | requires_audit | singleton_missing_mass |
| T2_policy_docs_seed01 | seed01 | true | 0.933 | 1.000 | 0.887 | 0.956 | 2 | 0.023 | 0.032 | 0.586 | unsafe_to_stop | singleton_missing_mass, high_agreement_boundary_blindspot_risk, low_effective_independence |
| T2_policy_docs_seed02 | seed02 | true | 0.933 | 1.000 | 0.937 | 1.000 | 0 | 0.000 | 0.000 | 0.350 | unsafe_to_stop | high_agreement_boundary_blindspot_risk, low_effective_independence |
| T2_policy_docs_seed03 | seed03 | true | 0.933 | 1.000 | 0.920 | 1.000 | 0 | 0.000 | 0.000 | 0.350 | unsafe_to_stop | high_agreement_boundary_blindspot_risk, low_effective_independence |
| T4_real_repo_click_seed01_smoke | seed01 | false | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0.000 | 0.000 | 0.350 | unsafe_to_stop | high_agreement_boundary_blindspot_risk, low_effective_independence |
| T4_real_repo_click_seed01_blind | seed01 | true | 0.953 | 0.744 | 0.780 | 0.670 | 56 | 0.125 | 0.172 | 0.800 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |
| T4_real_repo_click_seed02_blind | seed02 | true | 0.758 | 0.639 | 0.760 | 0.495 | 98 | 0.219 | 0.269 | 0.800 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |
| T4_real_repo_click_seed03_blind | seed03 | true | 0.779 | 0.642 | 0.797 | 0.505 | 102 | 0.228 | 0.333 | 0.800 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |
| T5_real_repo_requests_tls_seed01_smoke | seed01 | false | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0.000 | 0.000 | 0.350 | unsafe_to_stop | high_agreement_boundary_blindspot_risk, low_effective_independence |
| T5_real_repo_requests_tls_seed01_blind | seed01 | true | 0.701 | 0.661 | 0.810 | 0.645 | 97 | 0.109 | 0.108 | 0.600 | unsafe_to_stop | singleton_missing_mass, chao_unseen_mass |
| T5_real_repo_requests_tls_seed02_blind | seed02 | true | 0.678 | 0.668 | 0.887 | 0.652 | 97 | 0.111 | 0.121 | 0.600 | unsafe_to_stop | singleton_missing_mass, chao_unseen_mass |
| T5_real_repo_requests_tls_seed03_blind | seed03 | true | 0.678 | 0.676 | 0.750 | 0.636 | 95 | 0.114 | 0.116 | 0.800 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |

## Baseline Stop Safety

| method | n | stopped/certified | false certifications | conservative blocks |
| --- | ---: | ---: | ---: | ---: |
| certificate_v0_stop | 12 | 0 | 0 | 3 |
| chao_stop | 12 | 4 | 3 | 2 |
| confidence_stop | 12 | 8 | 6 | 1 |
| good_turing_stop | 12 | 4 | 3 | 2 |
| overlap_stop | 12 | 3 | 3 | 3 |
