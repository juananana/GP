# Incidence Log Summary

This file summarizes item-level incidence logs. Oracle labels are included only for offline scoring; blind agents must not access these logs.

| case | task_family | reportable | status | rows | unique_items | singleton_rows | holdout_new_rows | oracle_positive_rows |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| T1_hard_expanded | synthetic_code_audit | true | blind_agent_result | 358 | 40 | 57 | 0 | 346 |
| T1_hard_seed03_completed | synthetic_code_audit | true | blind_agent_result | 97 | 40 | 5 | 0 | 92 |
| T2_partitioned_v3_seed01 | naturalized_policy_docs | true | blind_agent_result | 45 | 45 | 0 | 0 | 45 |
| T2_policy_docs_seed01 | synthetic_policy_docs | true | blind_agent_result | 144 | 30 | 2 | 0 | 144 |
| T2_policy_docs_seed02 | synthetic_policy_docs | true | blind_agent_result | 114 | 30 | 0 | 2 | 114 |
| T2_policy_docs_seed03 | synthetic_policy_docs | true | blind_agent_result | 114 | 30 | 0 | 2 | 114 |
| T3_partitioned_seed01 | partitioned_policy_docs | true | blind_agent_result | 45 | 45 | 0 | 0 | 45 |
| T4_real_repo_click_seed01_blind | real_repo_code_audit | true | blind_agent_result | 596 | 202 | 56 | 3 | 534 |
| T4_real_repo_click_seed01_smoke | real_repo_code_audit | false | oracle_generated_smoke_test | 447 | 149 | 0 | 0 | 447 |
| T4_real_repo_click_seed02_blind | real_repo_code_audit | true | blind_agent_result | 596 | 243 | 98 | 10 | 461 |
| T4_real_repo_click_seed03_blind | real_repo_code_audit | true | blind_agent_result | 596 | 235 | 102 | 3 | 463 |
| T5_real_repo_requests_tls_seed01_blind | real_repo_tls_audit | true | blind_agent_result | 1220 | 409 | 97 | 14 | 862 |
| T5_real_repo_requests_tls_seed01_smoke | real_repo_tls_audit | false | oracle_generated_smoke_test | 912 | 304 | 0 | 0 | 912 |
| T5_real_repo_requests_tls_seed02_blind | real_repo_tls_audit | true | blind_agent_result | 1159 | 389 | 97 | 4 | 828 |
| T5_real_repo_requests_tls_seed03_blind | real_repo_tls_audit | true | blind_agent_result | 1163 | 389 | 95 | 16 | 839 |
