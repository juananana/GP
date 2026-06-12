# Line A Experiment Dashboard

Date: 2026-06-08

## Current Takeaway

T4 establishes stable real-repository aggregation-stage false stop: standard summarization self-reports completion in 3/3 seeds while omitting many oracle items. T5 adds a second real-repository family where search coverage is harder: consensus and raw union both remain incomplete across 3 seeds, and the certificate consistently refuses to stop.

## Protocol Overview

| case | mean conf | mean jaccard | singletons | consensus recall | standard recall | raw-union recall | certificate target |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T1_hard_seed01 | 0.853 | 0.752 | 13 | 0.629 | 0.629 | 1.000 | stop-risk |
| T1_hard_seed02 | 0.907 | 0.932 | 4 | 1.000 | 1.000 | 1.000 | precision-risk |
| T1_hard_seed03 | 0.893 | 0.685 | 5 | 1.000 | 1.000 | 1.000 | precision-risk |
| T2_policy_docs_seed01 | 0.887 | 0.956 | 2 | 0.933 | 0.933 | 1.000 | stop-risk |
| T2_policy_docs_seed02 | 0.937 | 1.000 | 0 | 0.933 | n/a | 0.933 | stop-risk |
| T2_policy_docs_seed03 | 0.920 | 1.000 | 0 | 0.933 | n/a | 0.933 | stop-risk |
| T4_real_repo_click_seed01_blind | 0.780 | 0.670 | 56 | 0.953 | 0.698 | 0.993 | precision-risk |
| T4_real_repo_click_seed02_blind | 0.760 | 0.495 | 98 | 0.758 | 0.745 | 1.000 | stop-risk |
| T4_real_repo_click_seed03_blind | 0.797 | 0.505 | 102 | 0.779 | 0.685 | 1.000 | stop-risk |
| T5_real_repo_requests_tls_seed01_blind | 0.810 | 0.645 | 97 | 0.701 | 0.368 | 0.859 | stop-risk |
| T5_real_repo_requests_tls_seed02_blind | 0.887 | 0.652 | 97 | 0.678 | 0.622 | 0.845 | stop-risk |
| T5_real_repo_requests_tls_seed03_blind | 0.750 | 0.636 | 95 | 0.678 | 0.648 | 0.829 | stop-risk |

## Completion Certificate v0

| case | seed | reportable | consensus recall | union recall | union precision | label | flags |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| T1_hard_expanded | seed01 | true | 0.629 | 1.000 | 1.000 | unsafe_to_stop | singleton_missing_mass, chao_unseen_mass |
| T1_hard_expanded | seed02 | true | 1.000 | 1.000 | 0.897 | requires_audit | singleton_missing_mass, chao_unseen_mass, low_effective_independence |
| T1_hard_seed03_completed | seed03 | true | 1.000 | 1.000 | 0.875 | requires_audit | singleton_missing_mass |
| T2_policy_docs_seed01 | seed01 | true | 0.933 | 1.000 | 1.000 | unsafe_to_stop | singleton_missing_mass, high_agreement_boundary_blindspot_risk, low_effective_independence |
| T2_policy_docs_seed02 | seed02 | true | 0.933 | 0.933 | 1.000 | unsafe_to_stop | high_agreement_boundary_blindspot_risk, low_effective_independence |
| T2_policy_docs_seed03 | seed03 | true | 0.933 | 0.933 | 1.000 | unsafe_to_stop | high_agreement_boundary_blindspot_risk, low_effective_independence |
| T4_real_repo_click_seed01_blind | seed01 | true | 0.953 | 0.993 | 0.744 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |
| T4_real_repo_click_seed02_blind | seed02 | true | 0.758 | 1.000 | 0.639 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |
| T4_real_repo_click_seed03_blind | seed03 | true | 0.779 | 1.000 | 0.642 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |
| T5_real_repo_requests_tls_seed01_blind | seed01 | true | 0.701 | 0.859 | 0.661 | unsafe_to_stop | singleton_missing_mass, chao_unseen_mass |
| T5_real_repo_requests_tls_seed02_blind | seed02 | true | 0.678 | 0.845 | 0.668 | unsafe_to_stop | singleton_missing_mass, chao_unseen_mass |
| T5_real_repo_requests_tls_seed03_blind | seed03 | true | 0.678 | 0.829 | 0.676 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |

## Source-Aware Audit v2

| case | seed | candidate recall | candidate precision | filter recall | filter precision | sweep recall | sweep precision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T4_real_repo_click_seed01_blind | seed01 | 0.993 | 0.733 | 0.993 | 1.000 | 1.000 | 1.000 |
| T4_real_repo_click_seed02_blind | seed02 | 1.000 | 0.613 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4_real_repo_click_seed03_blind | seed03 | 1.000 | 0.634 | 1.000 | 1.000 | 1.000 | 1.000 |
| T5_real_repo_requests_tls_seed01_blind | seed01 | 0.862 | 0.641 | 0.862 | 1.000 | 1.000 | 1.000 |
| T5_real_repo_requests_tls_seed02_blind | seed02 | 0.845 | 0.661 | 0.845 | 1.000 | 1.000 | 1.000 |
| T5_real_repo_requests_tls_seed03_blind | seed03 | 0.839 | 0.656 | 0.839 | 1.000 | 1.000 | 1.000 |

Candidate filter audits only G3/holdout candidates. Source sweep is a bounded policy upper bound, not a blind LLM result.
