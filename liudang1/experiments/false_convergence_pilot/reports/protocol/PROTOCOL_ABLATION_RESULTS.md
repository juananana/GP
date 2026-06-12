# Protocol Ablation Results

Ablations are scored with the oracle only after the variant has selected
its output. Oracle labels are not used to make protocol decisions.

| case | mechanism | variant | status | TP | FP | recall | precision | completion | false_stop |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| T1_hard_seed01 | aggregation_loss | consensus_only | complete_by_consensus | 22 | 0 | 0.629 | 1.000 | true | true |
| T1_hard_seed01 | aggregation_loss | no_singleton_audit | complete_no_audit_trigger | 22 | 0 | 0.629 | 1.000 | true | true |
| T1_hard_seed01 | aggregation_loss | no_common_blindspot_trigger | verified_after_holdout | 35 | 0 | 1.000 | 1.000 | true | false |
| T1_hard_seed01 | aggregation_loss | no_holdout | requires_audit_no_holdout | 22 | 0 | 0.629 | 1.000 | false | false |
| T1_hard_seed01 | aggregation_loss | full_protocol | verified_after_holdout | 35 | 0 | 1.000 | 1.000 | true | false |
| T1_hard_seed02 | precision_cost_control | consensus_only | complete_by_consensus | 35 | 0 | 1.000 | 1.000 | true | false |
| T1_hard_seed02 | precision_cost_control | no_singleton_audit | complete_no_audit_trigger | 35 | 0 | 1.000 | 1.000 | true | false |
| T1_hard_seed02 | precision_cost_control | no_common_blindspot_trigger | requires_audit_holdout_missing | 35 | 0 | 1.000 | 1.000 | false | false |
| T1_hard_seed02 | precision_cost_control | no_holdout | requires_audit_no_holdout | 35 | 0 | 1.000 | 1.000 | false | false |
| T1_hard_seed02 | precision_cost_control | full_protocol | requires_audit_holdout_missing | 35 | 0 | 1.000 | 1.000 | false | false |
| T1_hard_seed03 | precision_cost_control | consensus_only | complete_by_consensus | 35 | 0 | 1.000 | 1.000 | true | false |
| T1_hard_seed03 | precision_cost_control | no_singleton_audit | complete_no_audit_trigger | 35 | 0 | 1.000 | 1.000 | true | false |
| T1_hard_seed03 | precision_cost_control | no_common_blindspot_trigger | requires_audit_holdout_missing | 35 | 0 | 1.000 | 1.000 | false | false |
| T1_hard_seed03 | precision_cost_control | no_holdout | requires_audit_no_holdout | 35 | 0 | 1.000 | 1.000 | false | false |
| T1_hard_seed03 | precision_cost_control | full_protocol | requires_audit_holdout_missing | 35 | 0 | 1.000 | 1.000 | false | false |
| T2_policy_docs_seed01 | aggregation_loss | consensus_only | complete_by_consensus | 28 | 0 | 0.933 | 1.000 | true | true |
| T2_policy_docs_seed01 | aggregation_loss | no_singleton_audit | verified_after_holdout | 28 | 0 | 0.933 | 1.000 | true | true |
| T2_policy_docs_seed01 | aggregation_loss | no_common_blindspot_trigger | verified_after_holdout | 30 | 0 | 1.000 | 1.000 | true | false |
| T2_policy_docs_seed01 | aggregation_loss | no_holdout | requires_audit_no_holdout | 28 | 0 | 0.933 | 1.000 | false | false |
| T2_policy_docs_seed01 | aggregation_loss | full_protocol | verified_after_holdout | 30 | 0 | 1.000 | 1.000 | true | false |
| T2_policy_docs_seed02 | common_blind_spot | consensus_only | complete_by_consensus | 28 | 0 | 0.933 | 1.000 | true | true |
| T2_policy_docs_seed02 | common_blind_spot | no_singleton_audit | verified_after_holdout | 30 | 0 | 1.000 | 1.000 | true | false |
| T2_policy_docs_seed02 | common_blind_spot | no_common_blindspot_trigger | complete_no_audit_trigger | 28 | 0 | 0.933 | 1.000 | true | true |
| T2_policy_docs_seed02 | common_blind_spot | no_holdout | requires_audit_no_holdout | 28 | 0 | 0.933 | 1.000 | false | false |
| T2_policy_docs_seed02 | common_blind_spot | full_protocol | verified_after_holdout | 30 | 0 | 1.000 | 1.000 | true | false |
| T2_policy_docs_seed03 | common_blind_spot | consensus_only | complete_by_consensus | 28 | 0 | 0.933 | 1.000 | true | true |
| T2_policy_docs_seed03 | common_blind_spot | no_singleton_audit | verified_after_holdout | 30 | 0 | 1.000 | 1.000 | true | false |
| T2_policy_docs_seed03 | common_blind_spot | no_common_blindspot_trigger | complete_no_audit_trigger | 28 | 0 | 0.933 | 1.000 | true | true |
| T2_policy_docs_seed03 | common_blind_spot | no_holdout | requires_audit_no_holdout | 28 | 0 | 0.933 | 1.000 | false | false |
| T2_policy_docs_seed03 | common_blind_spot | full_protocol | verified_after_holdout | 30 | 0 | 1.000 | 1.000 | true | false |
| T4_real_repo_click_seed01_blind | real_repo_precision_recall_boundary | consensus_only | complete_by_consensus | 142 | 1 | 0.953 | 0.993 | false | false |
| T4_real_repo_click_seed01_blind | real_repo_precision_recall_boundary | no_singleton_audit | complete_no_audit_trigger | 142 | 1 | 0.953 | 0.993 | false | false |
| T4_real_repo_click_seed01_blind | real_repo_precision_recall_boundary | no_common_blindspot_trigger | verified_after_holdout | 148 | 7 | 0.993 | 0.955 | true | false |
| T4_real_repo_click_seed01_blind | real_repo_precision_recall_boundary | no_holdout | requires_audit_no_holdout | 142 | 1 | 0.953 | 0.993 | false | false |
| T4_real_repo_click_seed01_blind | real_repo_precision_recall_boundary | full_protocol | verified_after_holdout | 148 | 7 | 0.993 | 0.955 | true | false |
| T4_real_repo_click_seed02_blind | real_repo_precision_recall_boundary | consensus_only | complete_by_consensus | 113 | 22 | 0.758 | 0.837 | false | false |
| T4_real_repo_click_seed02_blind | real_repo_precision_recall_boundary | no_singleton_audit | complete_no_audit_trigger | 113 | 22 | 0.758 | 0.837 | false | false |
| T4_real_repo_click_seed02_blind | real_repo_precision_recall_boundary | no_common_blindspot_trigger | verified_after_holdout | 120 | 29 | 0.805 | 0.805 | true | true |
| T4_real_repo_click_seed02_blind | real_repo_precision_recall_boundary | no_holdout | requires_audit_no_holdout | 113 | 22 | 0.758 | 0.837 | false | false |
| T4_real_repo_click_seed02_blind | real_repo_precision_recall_boundary | full_protocol | verified_after_holdout | 120 | 29 | 0.805 | 0.805 | true | true |
| T4_real_repo_click_seed03_blind | real_repo_precision_recall_boundary | consensus_only | complete_by_consensus | 116 | 14 | 0.779 | 0.892 | false | false |
| T4_real_repo_click_seed03_blind | real_repo_precision_recall_boundary | no_singleton_audit | complete_no_audit_trigger | 116 | 14 | 0.779 | 0.892 | false | false |
| T4_real_repo_click_seed03_blind | real_repo_precision_recall_boundary | no_common_blindspot_trigger | verified_after_holdout | 124 | 39 | 0.832 | 0.761 | true | true |
| T4_real_repo_click_seed03_blind | real_repo_precision_recall_boundary | no_holdout | requires_audit_no_holdout | 116 | 14 | 0.779 | 0.892 | false | false |
| T4_real_repo_click_seed03_blind | real_repo_precision_recall_boundary | full_protocol | verified_after_holdout | 124 | 39 | 0.832 | 0.761 | true | true |
| T5_real_repo_requests_tls_seed01_blind | second_real_repo_tls_audit | consensus_only | complete_by_consensus | 213 | 85 | 0.701 | 0.715 | true | true |
| T5_real_repo_requests_tls_seed01_blind | second_real_repo_tls_audit | no_singleton_audit | complete_no_audit_trigger | 213 | 85 | 0.701 | 0.715 | true | true |
| T5_real_repo_requests_tls_seed01_blind | second_real_repo_tls_audit | no_common_blindspot_trigger | verified_after_holdout | 243 | 101 | 0.799 | 0.706 | true | true |
| T5_real_repo_requests_tls_seed01_blind | second_real_repo_tls_audit | no_holdout | requires_audit_no_holdout | 213 | 85 | 0.701 | 0.715 | false | false |
| T5_real_repo_requests_tls_seed01_blind | second_real_repo_tls_audit | full_protocol | verified_after_holdout | 243 | 101 | 0.799 | 0.706 | true | true |
| T5_real_repo_requests_tls_seed02_blind | second_real_repo_tls_audit | consensus_only | complete_by_consensus | 206 | 82 | 0.678 | 0.715 | true | true |
| T5_real_repo_requests_tls_seed02_blind | second_real_repo_tls_audit | no_singleton_audit | complete_no_audit_trigger | 206 | 82 | 0.678 | 0.715 | true | true |
| T5_real_repo_requests_tls_seed02_blind | second_real_repo_tls_audit | no_common_blindspot_trigger | verified_after_holdout | 228 | 91 | 0.750 | 0.715 | true | true |
| T5_real_repo_requests_tls_seed02_blind | second_real_repo_tls_audit | no_holdout | requires_audit_no_holdout | 206 | 82 | 0.678 | 0.715 | false | false |
| T5_real_repo_requests_tls_seed02_blind | second_real_repo_tls_audit | full_protocol | verified_after_holdout | 228 | 91 | 0.750 | 0.715 | true | true |
| T5_real_repo_requests_tls_seed03_blind | second_real_repo_tls_audit | consensus_only | complete_by_consensus | 206 | 72 | 0.678 | 0.741 | false | false |
| T5_real_repo_requests_tls_seed03_blind | second_real_repo_tls_audit | no_singleton_audit | complete_no_audit_trigger | 206 | 72 | 0.678 | 0.741 | false | false |
| T5_real_repo_requests_tls_seed03_blind | second_real_repo_tls_audit | no_common_blindspot_trigger | verified_after_holdout | 237 | 94 | 0.780 | 0.716 | true | true |
| T5_real_repo_requests_tls_seed03_blind | second_real_repo_tls_audit | no_holdout | requires_audit_no_holdout | 206 | 72 | 0.678 | 0.741 | false | false |
| T5_real_repo_requests_tls_seed03_blind | second_real_repo_tls_audit | full_protocol | verified_after_holdout | 237 | 94 | 0.780 | 0.716 | true | true |

## Main Takeaways

- Removing singleton audit leaves aggregation-loss singletons unrecovered.
- Removing common-blindspot trigger leaves high-agreement blind spots unrecovered.
- Removing holdout converts hidden risk into `requires_audit`, but cannot recover missing items.
- Full protocol is the only variant that covers both failure mechanisms when holdout evidence is available.
