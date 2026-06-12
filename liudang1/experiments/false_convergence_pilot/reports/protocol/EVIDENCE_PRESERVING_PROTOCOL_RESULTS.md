# Evidence-Preserving Completion Protocol Results

## Protocol

The protocol keeps consensus items as the conservative final set, sends singleton evidence to an audit queue, and triggers boundary-focused holdout when G3 agreement and confidence are both high.

It never uses the oracle for decisions; the oracle is used only for scoring.

## Case Metrics

| case | mechanism | mean_conf | mean_jaccard | singleton_count | consensus_missing | raw_union_fp |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| T1_hard_seed01 | aggregation_loss | 0.853 | 0.752 | 13 | 13 | 0 |
| T1_hard_seed02 | precision_cost_control | 0.907 | 0.932 | 4 | 0 | 4 |
| T1_hard_seed03 | precision_cost_control | 0.893 | 0.685 | 5 | 0 | 5 |
| T2_policy_docs_seed01 | aggregation_loss | 0.887 | 0.956 | 2 | 2 | 0 |
| T2_policy_docs_seed02 | common_blind_spot | 0.937 | 1.000 | 0 | 2 | 0 |
| T2_policy_docs_seed03 | common_blind_spot | 0.920 | 1.000 | 0 | 2 | 0 |
| T4_real_repo_click_seed01_blind | real_repo_precision_recall_boundary | 0.780 | 0.670 | 56 | 7 | 51 |
| T4_real_repo_click_seed02_blind | real_repo_precision_recall_boundary | 0.760 | 0.495 | 98 | 36 | 84 |
| T4_real_repo_click_seed03_blind | real_repo_precision_recall_boundary | 0.797 | 0.505 | 102 | 33 | 83 |
| T5_real_repo_requests_tls_seed01_blind | second_real_repo_tls_audit | 0.810 | 0.645 | 97 | 91 | 134 |
| T5_real_repo_requests_tls_seed02_blind | second_real_repo_tls_audit | 0.887 | 0.652 | 97 | 98 | 128 |
| T5_real_repo_requests_tls_seed03_blind | second_real_repo_tls_audit | 0.750 | 0.636 | 95 | 98 | 121 |

## Method Comparison

| case | method | status | found | TP | FP | recall | precision | completion | false_stop | notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| T1_hard_seed01 | majority_consensus | complete_by_consensus | 22 | 22 | 0 | 0.629 | 1.000 | true | true | Items reported by at least two G3 agents. |
| T1_hard_seed01 | standard_summarizer_blind | blind_llm_summary | 22 | 22 | 0 | 0.629 | 1.000 | true | true | confidence=0.860 |
| T1_hard_seed01 | raw_union | complete_by_union | 35 | 35 | 0 | 1.000 | 1.000 | true | false | All unique G3-reported items. |
| T1_hard_seed01 | union_preserving_blind | blind_llm_union_summary | 35 | 35 | 0 | 1.000 | 1.000 | true | false | confidence=0.853 |
| T1_hard_seed01 | holdout_scout | independent_audit | 35 | 35 | 0 | 1.000 | 1.000 | true | false | Independent holdout scout output. |
| T1_hard_seed01 | evidence_preserving_protocol | verified_after_holdout | 35 | 35 | 0 | 1.000 | 1.000 | true | false | Consensus final plus audited singleton/common-blindspot recovery. |
| T1_hard_seed02 | majority_consensus | complete_by_consensus | 35 | 35 | 0 | 1.000 | 1.000 | true | false | Items reported by at least two G3 agents. |
| T1_hard_seed02 | standard_summarizer_blind | blind_llm_summary | 35 | 35 | 0 | 1.000 | 1.000 | true | false | confidence=0.930 |
| T1_hard_seed02 | raw_union | complete_by_union | 39 | 35 | 4 | 1.000 | 0.897 | true | false | All unique G3-reported items. |
| T1_hard_seed02 | union_preserving_blind | blind_llm_union_summary | 39 | 35 | 4 | 1.000 | 0.897 | true | false | confidence=0.907 |
| T1_hard_seed02 | holdout_scout | not_run | n/a | n/a | n/a | n/a | n/a | false | false | not run for this seed |
| T1_hard_seed02 | evidence_preserving_protocol | requires_audit | 35 | 35 | 0 | 1.000 | 1.000 | false | false | Consensus final plus audited singleton/common-blindspot recovery. |
| T1_hard_seed03 | majority_consensus | complete_by_consensus | 35 | 35 | 0 | 1.000 | 1.000 | true | false | Items reported by at least two G3 agents. |
| T1_hard_seed03 | standard_summarizer_blind | blind_llm_summary | 35 | 35 | 0 | 1.000 | 1.000 | true | false | confidence=0.920 |
| T1_hard_seed03 | raw_union | complete_by_union | 40 | 35 | 5 | 1.000 | 0.875 | true | false | All unique G3-reported items. |
| T1_hard_seed03 | union_preserving_blind | blind_llm_union_summary | 40 | 35 | 5 | 1.000 | 0.875 | true | false | confidence=0.893 |
| T1_hard_seed03 | holdout_scout | not_run | n/a | n/a | n/a | n/a | n/a | false | false | not run for this seed |
| T1_hard_seed03 | evidence_preserving_protocol | requires_audit | 35 | 35 | 0 | 1.000 | 1.000 | false | false | Consensus final plus audited singleton/common-blindspot recovery. |
| T2_policy_docs_seed01 | majority_consensus | complete_by_consensus | 28 | 28 | 0 | 0.933 | 1.000 | true | true | Items reported by at least two G3 agents. |
| T2_policy_docs_seed01 | standard_summarizer_blind | blind_llm_summary | 28 | 28 | 0 | 0.933 | 1.000 | true | true | confidence=0.900 |
| T2_policy_docs_seed01 | raw_union | complete_by_union | 30 | 30 | 0 | 1.000 | 1.000 | true | false | All unique G3-reported items. |
| T2_policy_docs_seed01 | union_preserving_blind | blind_llm_union_summary | 30 | 30 | 0 | 1.000 | 1.000 | true | false | confidence=0.887 |
| T2_policy_docs_seed01 | holdout_scout | independent_audit | 30 | 30 | 0 | 1.000 | 1.000 | true | false | Independent holdout scout output. |
| T2_policy_docs_seed01 | evidence_preserving_protocol | verified_after_holdout | 30 | 30 | 0 | 1.000 | 1.000 | true | false | Consensus final plus audited singleton/common-blindspot recovery. |
| T2_policy_docs_seed02 | majority_consensus | complete_by_consensus | 28 | 28 | 0 | 0.933 | 1.000 | true | true | Items reported by at least two G3 agents. |
| T2_policy_docs_seed02 | standard_summarizer_blind | not_run | n/a | n/a | n/a | n/a | n/a | false | false | not run for this seed |
| T2_policy_docs_seed02 | raw_union | complete_by_union | 28 | 28 | 0 | 0.933 | 1.000 | true | true | All unique G3-reported items. |
| T2_policy_docs_seed02 | union_preserving_blind | not_run | n/a | n/a | n/a | n/a | n/a | false | false | not run for this seed |
| T2_policy_docs_seed02 | holdout_scout | independent_audit | 30 | 30 | 0 | 1.000 | 1.000 | true | false | Independent holdout scout output. |
| T2_policy_docs_seed02 | evidence_preserving_protocol | verified_after_holdout | 30 | 30 | 0 | 1.000 | 1.000 | true | false | Consensus final plus audited singleton/common-blindspot recovery. |
| T2_policy_docs_seed03 | majority_consensus | complete_by_consensus | 28 | 28 | 0 | 0.933 | 1.000 | true | true | Items reported by at least two G3 agents. |
| T2_policy_docs_seed03 | standard_summarizer_blind | not_run | n/a | n/a | n/a | n/a | n/a | false | false | not run for this seed |
| T2_policy_docs_seed03 | raw_union | complete_by_union | 28 | 28 | 0 | 0.933 | 1.000 | true | true | All unique G3-reported items. |
| T2_policy_docs_seed03 | union_preserving_blind | not_run | n/a | n/a | n/a | n/a | n/a | false | false | not run for this seed |
| T2_policy_docs_seed03 | holdout_scout | independent_audit | 30 | 30 | 0 | 1.000 | 1.000 | true | false | Independent holdout scout output. |
| T2_policy_docs_seed03 | evidence_preserving_protocol | verified_after_holdout | 30 | 30 | 0 | 1.000 | 1.000 | true | false | Consensus final plus audited singleton/common-blindspot recovery. |
| T4_real_repo_click_seed01_blind | majority_consensus | complete_by_consensus | 143 | 142 | 1 | 0.953 | 0.993 | false | false | Items reported by at least two G3 agents. |
| T4_real_repo_click_seed01_blind | standard_summarizer_blind | blind_llm_summary | 105 | 104 | 1 | 0.698 | 0.990 | true | true | confidence=0.930 |
| T4_real_repo_click_seed01_blind | raw_union | complete_by_union | 199 | 148 | 51 | 0.993 | 0.744 | false | false | All unique G3-reported items. |
| T4_real_repo_click_seed01_blind | union_preserving_blind | blind_llm_union_summary | 199 | 148 | 51 | 0.993 | 0.744 | true | false | confidence=0.910 |
| T4_real_repo_click_seed01_blind | holdout_scout | independent_audit | 149 | 140 | 9 | 0.940 | 0.940 | true | true | Independent holdout scout output. |
| T4_real_repo_click_seed01_blind | evidence_preserving_protocol | verified_after_holdout | 155 | 148 | 7 | 0.993 | 0.955 | true | false | Consensus final plus audited singleton/common-blindspot recovery. |
| T4_real_repo_click_seed02_blind | majority_consensus | complete_by_consensus | 135 | 113 | 22 | 0.758 | 0.837 | false | false | Items reported by at least two G3 agents. |
| T4_real_repo_click_seed02_blind | standard_summarizer_blind | blind_llm_summary | 111 | 111 | 0 | 0.745 | 1.000 | true | true | confidence=0.960 |
| T4_real_repo_click_seed02_blind | raw_union | complete_by_union | 233 | 149 | 84 | 1.000 | 0.639 | false | false | All unique G3-reported items. |
| T4_real_repo_click_seed02_blind | union_preserving_blind | blind_llm_union_summary | 233 | 149 | 84 | 1.000 | 0.639 | true | false | confidence=0.950 |
| T4_real_repo_click_seed02_blind | holdout_scout | independent_audit | 149 | 120 | 29 | 0.805 | 0.805 | true | true | Independent holdout scout output. |
| T4_real_repo_click_seed02_blind | evidence_preserving_protocol | verified_after_holdout | 149 | 120 | 29 | 0.805 | 0.805 | true | true | Consensus final plus audited singleton/common-blindspot recovery. |
| T4_real_repo_click_seed03_blind | majority_consensus | complete_by_consensus | 130 | 116 | 14 | 0.779 | 0.892 | false | false | Items reported by at least two G3 agents. |
| T4_real_repo_click_seed03_blind | standard_summarizer_blind | blind_llm_summary | 102 | 102 | 0 | 0.685 | 1.000 | true | true | confidence=0.930 |
| T4_real_repo_click_seed03_blind | raw_union | complete_by_union | 232 | 149 | 83 | 1.000 | 0.642 | false | false | All unique G3-reported items. |
| T4_real_repo_click_seed03_blind | union_preserving_blind | blind_llm_union_summary | 232 | 149 | 83 | 1.000 | 0.642 | true | false | confidence=0.840 |
| T4_real_repo_click_seed03_blind | holdout_scout | independent_audit | 149 | 113 | 36 | 0.758 | 0.758 | true | true | Independent holdout scout output. |
| T4_real_repo_click_seed03_blind | evidence_preserving_protocol | verified_after_holdout | 163 | 124 | 39 | 0.832 | 0.761 | true | true | Consensus final plus audited singleton/common-blindspot recovery. |
| T5_real_repo_requests_tls_seed01_blind | majority_consensus | complete_by_consensus | 298 | 213 | 85 | 0.701 | 0.715 | true | true | Items reported by at least two G3 agents. |
| T5_real_repo_requests_tls_seed01_blind | standard_summarizer_blind | blind_llm_summary | 143 | 112 | 31 | 0.368 | 0.783 | true | true | confidence=0.920 |
| T5_real_repo_requests_tls_seed01_blind | raw_union | complete_by_union | 395 | 261 | 134 | 0.859 | 0.661 | true | true | All unique G3-reported items. |
| T5_real_repo_requests_tls_seed01_blind | union_preserving_blind | blind_llm_union_summary | 133 | 92 | 41 | 0.303 | 0.692 | true | true | confidence=0.920 |
| T5_real_repo_requests_tls_seed01_blind | holdout_scout | independent_audit | 327 | 228 | 99 | 0.750 | 0.697 | true | true | Independent holdout scout output. |
| T5_real_repo_requests_tls_seed01_blind | evidence_preserving_protocol | verified_after_holdout | 344 | 243 | 101 | 0.799 | 0.706 | true | true | Consensus final plus audited singleton/common-blindspot recovery. |
| T5_real_repo_requests_tls_seed02_blind | majority_consensus | complete_by_consensus | 288 | 206 | 82 | 0.678 | 0.715 | true | true | Items reported by at least two G3 agents. |
| T5_real_repo_requests_tls_seed02_blind | standard_summarizer_blind | blind_llm_summary | 248 | 189 | 59 | 0.622 | 0.762 | true | true | confidence=0.940 |
| T5_real_repo_requests_tls_seed02_blind | raw_union | complete_by_union | 385 | 257 | 128 | 0.845 | 0.668 | true | true | All unique G3-reported items. |
| T5_real_repo_requests_tls_seed02_blind | union_preserving_blind | blind_llm_union_summary | 385 | 257 | 128 | 0.845 | 0.668 | true | true | confidence=0.890 |
| T5_real_repo_requests_tls_seed02_blind | holdout_scout | independent_audit | 287 | 209 | 78 | 0.688 | 0.728 | true | true | Independent holdout scout output. |
| T5_real_repo_requests_tls_seed02_blind | evidence_preserving_protocol | verified_after_holdout | 319 | 228 | 91 | 0.750 | 0.715 | true | true | Consensus final plus audited singleton/common-blindspot recovery. |
| T5_real_repo_requests_tls_seed03_blind | majority_consensus | complete_by_consensus | 278 | 206 | 72 | 0.678 | 0.741 | false | false | Items reported by at least two G3 agents. |
| T5_real_repo_requests_tls_seed03_blind | standard_summarizer_blind | blind_llm_summary | 253 | 197 | 56 | 0.648 | 0.779 | true | true | confidence=0.860 |
| T5_real_repo_requests_tls_seed03_blind | raw_union | complete_by_union | 373 | 252 | 121 | 0.829 | 0.676 | false | false | All unique G3-reported items. |
| T5_real_repo_requests_tls_seed03_blind | union_preserving_blind | blind_llm_union_summary | 373 | 252 | 121 | 0.829 | 0.676 | true | true | confidence=0.810 |
| T5_real_repo_requests_tls_seed03_blind | holdout_scout | independent_audit | 326 | 232 | 94 | 0.763 | 0.712 | true | true | Independent holdout scout output. |
| T5_real_repo_requests_tls_seed03_blind | evidence_preserving_protocol | verified_after_holdout | 331 | 237 | 94 | 0.780 | 0.716 | true | true | Consensus final plus audited singleton/common-blindspot recovery. |

## Protocol Audit Details

| case | protocol_status | risk_flags | audit_queue | verified_singletons | unverified_singletons | holdout_new_items |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| T1_hard_seed01 | verified_after_holdout | singleton_evidence_requires_audit | 13 | 13 | 0 | 0 |
| T1_hard_seed02 | requires_audit | singleton_evidence_requires_audit | 4 | 0 | 4 | 0 |
| T1_hard_seed03 | requires_audit | singleton_evidence_requires_audit | 5 | 0 | 5 | 0 |
| T2_policy_docs_seed01 | verified_after_holdout | singleton_evidence_requires_audit, high_agreement_boundary_blindspot_risk | 2 | 2 | 0 | 0 |
| T2_policy_docs_seed02 | verified_after_holdout | high_agreement_boundary_blindspot_risk | 0 | 0 | 0 | 2 |
| T2_policy_docs_seed03 | verified_after_holdout | high_agreement_boundary_blindspot_risk | 0 | 0 | 0 | 2 |
| T4_real_repo_click_seed01_blind | verified_after_holdout | singleton_evidence_requires_audit | 56 | 12 | 44 | 0 |
| T4_real_repo_click_seed02_blind | verified_after_holdout | singleton_evidence_requires_audit | 98 | 14 | 84 | 0 |
| T4_real_repo_click_seed03_blind | verified_after_holdout | singleton_evidence_requires_audit | 102 | 33 | 69 | 0 |
| T5_real_repo_requests_tls_seed01_blind | verified_after_holdout | singleton_evidence_requires_audit | 97 | 46 | 51 | 0 |
| T5_real_repo_requests_tls_seed02_blind | verified_after_holdout | singleton_evidence_requires_audit | 97 | 31 | 66 | 0 |
| T5_real_repo_requests_tls_seed03_blind | verified_after_holdout | singleton_evidence_requires_audit | 95 | 53 | 42 | 0 |
