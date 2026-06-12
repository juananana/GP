# Source-Aware Audit v2 Results

This report separates candidate-pool filtering from source-sweep audit.
`source_aware_candidate_filter_v2` audits items already discovered by G3/holdout.
`source_sweep_v2_upper_bound` is an audit-policy upper bound, not a blind LLM result.

| case | reportable | method | found | TP | FP | recall | precision |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| T4_real_repo_click_seed01_blind | true | majority_consensus | 143 | 142 | 1 | 0.953 | 0.993 |
| T4_real_repo_click_seed01_blind | true | raw_union | 199 | 148 | 51 | 0.993 | 0.744 |
| T4_real_repo_click_seed01_blind | true | holdout_union | 149 | 140 | 9 | 0.940 | 0.940 |
| T4_real_repo_click_seed01_blind | true | candidate_pool | 202 | 148 | 54 | 0.993 | 0.733 |
| T4_real_repo_click_seed01_blind | true | source_aware_candidate_filter_v2 | 148 | 148 | 0 | 0.993 | 1.000 |
| T4_real_repo_click_seed01_blind | true | source_sweep_v2_upper_bound | 149 | 149 | 0 | 1.000 | 1.000 |
| T4_real_repo_click_seed02_blind | true | majority_consensus | 135 | 113 | 22 | 0.758 | 0.837 |
| T4_real_repo_click_seed02_blind | true | raw_union | 233 | 149 | 84 | 1.000 | 0.639 |
| T4_real_repo_click_seed02_blind | true | holdout_union | 149 | 120 | 29 | 0.805 | 0.805 |
| T4_real_repo_click_seed02_blind | true | candidate_pool | 243 | 149 | 94 | 1.000 | 0.613 |
| T4_real_repo_click_seed02_blind | true | source_aware_candidate_filter_v2 | 149 | 149 | 0 | 1.000 | 1.000 |
| T4_real_repo_click_seed02_blind | true | source_sweep_v2_upper_bound | 149 | 149 | 0 | 1.000 | 1.000 |
| T4_real_repo_click_seed03_blind | true | majority_consensus | 130 | 116 | 14 | 0.779 | 0.892 |
| T4_real_repo_click_seed03_blind | true | raw_union | 232 | 149 | 83 | 1.000 | 0.642 |
| T4_real_repo_click_seed03_blind | true | holdout_union | 149 | 113 | 36 | 0.758 | 0.758 |
| T4_real_repo_click_seed03_blind | true | candidate_pool | 235 | 149 | 86 | 1.000 | 0.634 |
| T4_real_repo_click_seed03_blind | true | source_aware_candidate_filter_v2 | 149 | 149 | 0 | 1.000 | 1.000 |
| T4_real_repo_click_seed03_blind | true | source_sweep_v2_upper_bound | 149 | 149 | 0 | 1.000 | 1.000 |
| T5_real_repo_requests_tls_seed01_smoke | false | majority_consensus | 304 | 304 | 0 | 1.000 | 1.000 |
| T5_real_repo_requests_tls_seed01_smoke | false | raw_union | 304 | 304 | 0 | 1.000 | 1.000 |
| T5_real_repo_requests_tls_seed01_smoke | false | holdout_union | 0 | 0 | 0 | 0.000 | 1.000 |
| T5_real_repo_requests_tls_seed01_smoke | false | candidate_pool | 304 | 304 | 0 | 1.000 | 1.000 |
| T5_real_repo_requests_tls_seed01_smoke | false | source_aware_candidate_filter_v2 | 304 | 304 | 0 | 1.000 | 1.000 |
| T5_real_repo_requests_tls_seed01_smoke | false | source_sweep_v2_upper_bound | 304 | 304 | 0 | 1.000 | 1.000 |
| T5_real_repo_requests_tls_seed01_blind | true | majority_consensus | 298 | 213 | 85 | 0.701 | 0.715 |
| T5_real_repo_requests_tls_seed01_blind | true | raw_union | 395 | 261 | 134 | 0.859 | 0.661 |
| T5_real_repo_requests_tls_seed01_blind | true | holdout_union | 327 | 228 | 99 | 0.750 | 0.697 |
| T5_real_repo_requests_tls_seed01_blind | true | candidate_pool | 409 | 262 | 147 | 0.862 | 0.641 |
| T5_real_repo_requests_tls_seed01_blind | true | source_aware_candidate_filter_v2 | 262 | 262 | 0 | 0.862 | 1.000 |
| T5_real_repo_requests_tls_seed01_blind | true | source_sweep_v2_upper_bound | 304 | 304 | 0 | 1.000 | 1.000 |
| T5_real_repo_requests_tls_seed02_blind | true | majority_consensus | 288 | 206 | 82 | 0.678 | 0.715 |
| T5_real_repo_requests_tls_seed02_blind | true | raw_union | 385 | 257 | 128 | 0.845 | 0.668 |
| T5_real_repo_requests_tls_seed02_blind | true | holdout_union | 287 | 209 | 78 | 0.688 | 0.728 |
| T5_real_repo_requests_tls_seed02_blind | true | candidate_pool | 389 | 257 | 132 | 0.845 | 0.661 |
| T5_real_repo_requests_tls_seed02_blind | true | source_aware_candidate_filter_v2 | 257 | 257 | 0 | 0.845 | 1.000 |
| T5_real_repo_requests_tls_seed02_blind | true | source_sweep_v2_upper_bound | 304 | 304 | 0 | 1.000 | 1.000 |
| T5_real_repo_requests_tls_seed03_blind | true | majority_consensus | 278 | 206 | 72 | 0.678 | 0.741 |
| T5_real_repo_requests_tls_seed03_blind | true | raw_union | 373 | 252 | 121 | 0.829 | 0.676 |
| T5_real_repo_requests_tls_seed03_blind | true | holdout_union | 326 | 232 | 94 | 0.763 | 0.712 |
| T5_real_repo_requests_tls_seed03_blind | true | candidate_pool | 389 | 255 | 134 | 0.839 | 0.656 |
| T5_real_repo_requests_tls_seed03_blind | true | source_aware_candidate_filter_v2 | 255 | 255 | 0 | 0.839 | 1.000 |
| T5_real_repo_requests_tls_seed03_blind | true | source_sweep_v2_upper_bound | 304 | 304 | 0 | 1.000 | 1.000 |

## Notes

- Candidate filtering is the cleaner reportable direction when blind agents already surfaced the item.
- Source sweep shows whether a stronger audit policy can recover items missing from all current candidates.
- T5 smoke rows are scorer/pipeline checks only; T5 blind rows are reportable evidence.
