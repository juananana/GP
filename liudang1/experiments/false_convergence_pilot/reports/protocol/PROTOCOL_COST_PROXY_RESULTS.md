# Protocol Cost Proxy Analysis

Current logs do not contain reliable token or wall-clock accounting, so this
table reports a proxy cost: `audit_queue_size + holdout_run_units`.

| case | variant | audit_queue | holdout_used | audit_actions | recovered_TP | actions_per_recovered_TP | avoided_FP_vs_raw_union |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| T1_hard_seed01 | no_holdout | 13 | false | 13 | 0 | n/a | 0 |
| T1_hard_seed01 | full_protocol | 13 | true | 14 | 13 | 1.077 | 0 |
| T1_hard_seed02 | no_holdout | 4 | false | 4 | 0 | n/a | 4 |
| T1_hard_seed02 | full_protocol | 4 | false | 4 | 0 | n/a | 4 |
| T1_hard_seed03 | no_holdout | 5 | false | 5 | 0 | n/a | 5 |
| T1_hard_seed03 | full_protocol | 5 | false | 5 | 0 | n/a | 5 |
| T2_policy_docs_seed01 | no_holdout | 2 | false | 2 | 0 | n/a | 0 |
| T2_policy_docs_seed01 | full_protocol | 2 | true | 3 | 2 | 1.500 | 0 |
| T2_policy_docs_seed02 | no_holdout | 0 | false | 0 | 0 | n/a | 0 |
| T2_policy_docs_seed02 | full_protocol | 0 | true | 1 | 2 | 0.500 | 0 |
| T2_policy_docs_seed03 | no_holdout | 0 | false | 0 | 0 | n/a | 0 |
| T2_policy_docs_seed03 | full_protocol | 0 | true | 1 | 2 | 0.500 | 0 |
| T4_real_repo_click_seed01_blind | no_holdout | 56 | false | 56 | 0 | n/a | 50 |
| T4_real_repo_click_seed01_blind | full_protocol | 56 | true | 57 | 6 | 9.500 | 44 |
| T4_real_repo_click_seed02_blind | no_holdout | 98 | false | 98 | 0 | n/a | 62 |
| T4_real_repo_click_seed02_blind | full_protocol | 98 | true | 99 | 7 | 14.143 | 55 |
| T4_real_repo_click_seed03_blind | no_holdout | 102 | false | 102 | 0 | n/a | 69 |
| T4_real_repo_click_seed03_blind | full_protocol | 102 | true | 103 | 8 | 12.875 | 44 |
| T5_real_repo_requests_tls_seed01_blind | no_holdout | 97 | false | 97 | 0 | n/a | 49 |
| T5_real_repo_requests_tls_seed01_blind | full_protocol | 97 | true | 98 | 30 | 3.267 | 33 |
| T5_real_repo_requests_tls_seed02_blind | no_holdout | 97 | false | 97 | 0 | n/a | 46 |
| T5_real_repo_requests_tls_seed02_blind | full_protocol | 97 | true | 98 | 22 | 4.455 | 37 |
| T5_real_repo_requests_tls_seed03_blind | no_holdout | 95 | false | 95 | 0 | n/a | 49 |
| T5_real_repo_requests_tls_seed03_blind | full_protocol | 95 | true | 96 | 31 | 3.097 | 27 |

## Interpretation

- The proxy cost is intentionally conservative and transparent.
- Token and wall-clock cost should be added once run logs are collected.
- `requires_audit` cases are not failures of the controller; they are cases where the controller refuses to certify completion without more evidence.
