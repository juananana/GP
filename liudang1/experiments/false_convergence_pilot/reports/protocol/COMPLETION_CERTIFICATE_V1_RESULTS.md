# Completion Certificate v1 Results

Generated at: `2026-06-09T08:41:14.938327+00:00`

## Rule

Pre-audit certificate uses exploration-only signals: confidence, output overlap, singleton/doubleton counts, Good-Turing missing mass, Chao unseen mass, source coverage, and effective exploration size. Holdout gain is only logged in post-audit states.

Labels: `SAFE-TO-STOP`, `UNSAFE-TO-STOP`, `REQUIRES-AUDIT`.

## Aggregate Metrics

- Reportable states: `96`
- Safe states by oracle recall threshold: `44`
- Unsafe states by oracle recall threshold: `52`
- Risk-score AUROC for unsafe-state detection: `0.5148601398601399`
- Risk-score AUPRC for unsafe-state detection: `0.58893864022115`
- Mean pre-audit recall: `0.8826239133615215`
- Mean post-audit recall: `0.9539341222182974`

The current v1 rule is intentionally conservative. A low false-certification rate with low safe coverage should be interpreted as a risk detector, not as a solved stopping rule.

## Logged Cost Summary

Token and wall-clock logs are incomplete for older T4 runs; missing fields are counted rather than imputed.

```json
{
  "input_tokens_logged": 3819471,
  "output_tokens_logged": 238538,
  "tool_calls_logged": 0,
  "wall_clock_seconds_logged": 2239.05403820012,
  "states_with_missing_token_logs": 72,
  "states_with_missing_tool_call_logs": 48,
  "post_audit_states": 10,
  "post_audit_actions_logged": 18,
  "post_audit_holdout_items_reviewed": 1512,
  "post_audit_singleton_candidates": 560
}
```

## Stopping Baselines

| method | n | stopped | false certs | false cert rate | safe coverage | abstention rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| always_holdout | 96 | 10 | 3 | 0.300 | 0.159 | 0.896 |
| always_unsafe | 96 | 0 | 0 | 0.000 | 0.000 | 1.000 |
| chao_only | 96 | 26 | 13 | 0.500 | 0.295 | 0.729 |
| confidence_only | 96 | 70 | 35 | 0.500 | 0.795 | 0.271 |
| no_new_item_stopping | 96 | 22 | 10 | 0.455 | 0.273 | 0.771 |
| overlap_only | 96 | 15 | 10 | 0.667 | 0.114 | 0.844 |
| proposed_certificate | 96 | 1 | 0 | 0.000 | 0.023 | 0.990 |
| raw_union | 96 | 86 | 49 | 0.570 | 0.841 | 0.104 |
| self_reported_completion | 96 | 70 | 35 | 0.500 | 0.795 | 0.271 |

## States

| state | stage | recall | precision | f1 | oracle safe | label | risk | output J | source overlap | eff size | adj Chao |
| --- | --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| T1_hard_seed01_pre_g1_agent1 | pre_audit | 0.629 | 1.000 | 0.772 | False | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.913 |
| T1_hard_seed01_pre_g1_agent2 | pre_audit | 0.629 | 1.000 | 0.772 | False | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.913 |
| T1_hard_seed01_pre_g1_agent3 | pre_audit | 1.000 | 1.000 | 1.000 | True | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.944 |
| T1_hard_seed01_pre_g2_pair1 | pre_audit | 0.629 | 1.000 | 0.772 | False | REQUIRES-AUDIT | 0.270 | 1.000 | 1.000 | 1.000 | 0.000 |
| T1_hard_seed01_pre_g2_pair2 | pre_audit | 1.000 | 1.000 | 1.000 | True | UNSAFE-TO-STOP | 0.818 | 0.629 | 1.000 | 1.228 | 0.161 |
| T1_hard_seed01_pre_g2_pair3 | pre_audit | 1.000 | 1.000 | 1.000 | True | UNSAFE-TO-STOP | 0.818 | 0.629 | 1.000 | 1.228 | 0.161 |
| T1_hard_seed01_pre_g3 | pre_audit | 1.000 | 1.000 | 1.000 | True | UNSAFE-TO-STOP | 0.820 | 0.752 | 1.000 | 1.198 | 1.000 |
| T1_hard_seed01_post_holdout | post_audit | 1.000 | 1.000 | 1.000 | True | SAFE-TO-STOP | 0.150 | 0.752 | 1.000 | 1.228 | 0.000 |
| T1_hard_seed02_pre_g1_agent1 | pre_audit | 1.000 | 0.897 | 0.946 | True | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.950 |
| T1_hard_seed02_pre_g1_agent2 | pre_audit | 1.000 | 1.000 | 1.000 | True | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.944 |
| T1_hard_seed02_pre_g1_agent3 | pre_audit | 1.000 | 1.000 | 1.000 | True | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.944 |
| T1_hard_seed02_pre_g2_pair1 | pre_audit | 1.000 | 0.897 | 0.946 | True | REQUIRES-AUDIT | 0.306 | 0.897 | 1.000 | 1.054 | 0.011 |
| T1_hard_seed02_pre_g2_pair2 | pre_audit | 1.000 | 0.897 | 0.946 | True | REQUIRES-AUDIT | 0.306 | 0.897 | 1.000 | 1.054 | 0.011 |
| T1_hard_seed02_pre_g2_pair3 | pre_audit | 1.000 | 1.000 | 1.000 | True | REQUIRES-AUDIT | 0.270 | 1.000 | 1.000 | 1.000 | 0.000 |
| T1_hard_seed02_pre_g3 | pre_audit | 1.000 | 0.897 | 0.946 | True | UNSAFE-TO-STOP | 0.698 | 0.932 | 1.000 | 1.048 | 0.382 |
| T1_hard_seed03_pre_g1_agent1 | pre_audit | 1.000 | 0.875 | 0.933 | True | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.951 |
| T1_hard_seed03_pre_g3 | pre_audit | 1.000 | 0.875 | 0.933 | True | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.951 |
| T1_hard_seed03_seed03_pre_g1_agent1 | pre_audit | 1.000 | 0.875 | 0.933 | True | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.951 |
| T1_hard_seed03_seed03_pre_g1_agent2 | pre_audit | 1.000 | 1.000 | 1.000 | True | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.944 |
| T1_hard_seed03_seed03_pre_g1_agent3 | pre_audit | 0.629 | 1.000 | 0.772 | False | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.913 |
| T1_hard_seed03_seed03_pre_g2_pair1 | pre_audit | 1.000 | 0.875 | 0.933 | True | REQUIRES-AUDIT | 0.348 | 0.875 | 1.000 | 1.067 | 0.017 |
| T1_hard_seed03_seed03_pre_g2_pair2 | pre_audit | 1.000 | 0.875 | 0.933 | True | UNSAFE-TO-STOP | 0.820 | 0.550 | 1.000 | 1.290 | 0.241 |
| T1_hard_seed03_seed03_pre_g2_pair3 | pre_audit | 1.000 | 1.000 | 1.000 | True | UNSAFE-TO-STOP | 0.818 | 0.629 | 1.000 | 1.228 | 0.161 |
| T1_hard_seed03_seed03_pre_g3 | pre_audit | 1.000 | 0.875 | 0.933 | True | REQUIRES-AUDIT | 0.432 | 0.685 | 1.000 | 1.266 | 0.056 |
| T2_policy_docs_seed01_seed01_pre_g1_agent1 | pre_audit | 0.933 | 1.000 | 0.966 | False | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.931 |
| T2_policy_docs_seed01_seed01_pre_g1_agent2 | pre_audit | 1.000 | 1.000 | 1.000 | True | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.935 |
| T2_policy_docs_seed01_seed01_pre_g1_agent3 | pre_audit | 0.933 | 1.000 | 0.966 | False | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.931 |
| T2_policy_docs_seed01_seed01_pre_g2_pair1 | pre_audit | 1.000 | 1.000 | 1.000 | True | REQUIRES-AUDIT | 0.245 | 0.933 | 0.933 | 1.034 | 0.005 |
| T2_policy_docs_seed01_seed01_pre_g2_pair2 | pre_audit | 0.933 | 1.000 | 0.966 | False | REQUIRES-AUDIT | 0.270 | 1.000 | 1.000 | 1.000 | 0.000 |
| T2_policy_docs_seed01_seed01_pre_g2_pair3 | pre_audit | 1.000 | 1.000 | 1.000 | True | REQUIRES-AUDIT | 0.245 | 0.933 | 0.933 | 1.034 | 0.005 |
| T2_policy_docs_seed01_seed01_pre_g3 | pre_audit | 1.000 | 1.000 | 1.000 | True | REQUIRES-AUDIT | 0.550 | 0.956 | 0.956 | 1.031 | 0.094 |
| T2_policy_docs_seed01_seed01_post_holdout | post_audit | 1.000 | 1.000 | 1.000 | True | REQUIRES-AUDIT | 0.270 | 0.956 | 0.956 | 1.034 | 0.000 |
| T2_policy_docs_seed02_seed02_pre_g1_agent1 | pre_audit | 0.933 | 1.000 | 0.966 | False | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.931 |
| T2_policy_docs_seed02_seed02_pre_g1_agent2 | pre_audit | 0.933 | 1.000 | 0.966 | False | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.931 |
| T2_policy_docs_seed02_seed02_pre_g1_agent3 | pre_audit | 0.933 | 1.000 | 0.966 | False | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.931 |
| T2_policy_docs_seed02_seed02_pre_g2_pair1 | pre_audit | 0.933 | 1.000 | 0.966 | False | REQUIRES-AUDIT | 0.270 | 1.000 | 1.000 | 1.000 | 0.000 |
| T2_policy_docs_seed02_seed02_pre_g2_pair2 | pre_audit | 0.933 | 1.000 | 0.966 | False | REQUIRES-AUDIT | 0.270 | 1.000 | 1.000 | 1.000 | 0.000 |
| T2_policy_docs_seed02_seed02_pre_g2_pair3 | pre_audit | 0.933 | 1.000 | 0.966 | False | REQUIRES-AUDIT | 0.270 | 1.000 | 1.000 | 1.000 | 0.000 |
| T2_policy_docs_seed02_seed02_pre_g3 | pre_audit | 0.933 | 1.000 | 0.966 | False | REQUIRES-AUDIT | 0.270 | 1.000 | 1.000 | 1.000 | 0.000 |
| T2_policy_docs_seed02_seed02_post_holdout | post_audit | 1.000 | 1.000 | 1.000 | True | REQUIRES-AUDIT | 0.592 | 0.967 | 0.967 | 1.026 | 0.126 |
| T2_policy_docs_seed03_seed03_pre_g1_agent1 | pre_audit | 0.933 | 1.000 | 0.966 | False | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.931 |
| T2_policy_docs_seed03_seed03_pre_g1_agent2 | pre_audit | 0.933 | 1.000 | 0.966 | False | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.931 |
| T2_policy_docs_seed03_seed03_pre_g1_agent3 | pre_audit | 0.933 | 1.000 | 0.966 | False | UNSAFE-TO-STOP | 0.820 | n/a | n/a | 1.000 | 0.931 |
| T2_policy_docs_seed03_seed03_pre_g2_pair1 | pre_audit | 0.933 | 1.000 | 0.966 | False | REQUIRES-AUDIT | 0.270 | 1.000 | 1.000 | 1.000 | 0.000 |
| T2_policy_docs_seed03_seed03_pre_g2_pair2 | pre_audit | 0.933 | 1.000 | 0.966 | False | REQUIRES-AUDIT | 0.270 | 1.000 | 1.000 | 1.000 | 0.000 |
| T2_policy_docs_seed03_seed03_pre_g2_pair3 | pre_audit | 0.933 | 1.000 | 0.966 | False | REQUIRES-AUDIT | 0.270 | 1.000 | 1.000 | 1.000 | 0.000 |
| T2_policy_docs_seed03_seed03_pre_g3 | pre_audit | 0.933 | 1.000 | 0.966 | False | REQUIRES-AUDIT | 0.270 | 1.000 | 1.000 | 1.000 | 0.000 |
| T2_policy_docs_seed03_seed03_post_holdout | post_audit | 1.000 | 1.000 | 1.000 | True | REQUIRES-AUDIT | 0.592 | 0.967 | 0.967 | 1.026 | 0.126 |
| T4_real_repo_click_seed01_blind_seed01_pre_g1_agent1 | pre_audit | 0.993 | 0.993 | 0.993 | True | UNSAFE-TO-STOP | 0.782 | n/a | n/a | 1.000 | 0.987 |
| T4_real_repo_click_seed01_blind_seed01_pre_g1_agent2 | pre_audit | 0.953 | 0.953 | 0.953 | True | UNSAFE-TO-STOP | 0.902 | n/a | n/a | 1.000 | 0.987 |
| T4_real_repo_click_seed01_blind_seed01_pre_g1_agent3 | pre_audit | 0.698 | 0.698 | 0.698 | False | UNSAFE-TO-STOP | 0.902 | n/a | n/a | 1.000 | 0.987 |
| T4_real_repo_click_seed01_blind_seed01_pre_g2_pair1 | pre_audit | 0.993 | 0.955 | 0.974 | True | REQUIRES-AUDIT | 0.344 | 0.923 | 1.000 | 1.040 | 0.006 |
| T4_real_repo_click_seed01_blind_seed01_pre_g2_pair2 | pre_audit | 0.993 | 0.767 | 0.865 | True | UNSAFE-TO-STOP | 0.782 | 0.544 | 1.000 | 1.295 | 0.248 |
| T4_real_repo_click_seed01_blind_seed01_pre_g2_pair3 | pre_audit | 0.953 | 0.736 | 0.830 | True | UNSAFE-TO-STOP | 0.902 | 0.544 | 1.000 | 1.295 | 0.248 |
| T4_real_repo_click_seed01_blind_seed01_pre_g3 | pre_audit | 0.993 | 0.744 | 0.851 | True | UNSAFE-TO-STOP | 0.902 | 0.670 | 1.000 | 1.282 | 0.402 |
| T4_real_repo_click_seed01_blind_seed01_post_holdout | post_audit | 0.993 | 0.733 | 0.843 | True | UNSAFE-TO-STOP | 1.000 | 0.710 | 1.000 | 1.278 | 0.979 |
| T4_real_repo_click_seed02_blind_seed02_pre_g1_agent1 | pre_audit | 0.530 | 0.530 | 0.530 | False | UNSAFE-TO-STOP | 0.902 | n/a | n/a | 1.000 | 0.987 |
| T4_real_repo_click_seed02_blind_seed02_pre_g1_agent2 | pre_audit | 1.000 | 1.000 | 1.000 | True | UNSAFE-TO-STOP | 0.782 | n/a | n/a | 1.000 | 0.987 |
| T4_real_repo_click_seed02_blind_seed02_pre_g1_agent3 | pre_audit | 0.758 | 0.758 | 0.758 | False | UNSAFE-TO-STOP | 0.902 | n/a | n/a | 1.000 | 0.987 |
| T4_real_repo_click_seed02_blind_seed02_pre_g2_pair1 | pre_audit | 1.000 | 0.680 | 0.810 | True | UNSAFE-TO-STOP | 0.782 | 0.361 | 1.000 | 1.470 | 0.492 |
| T4_real_repo_click_seed02_blind_seed02_pre_g2_pair2 | pre_audit | 0.758 | 0.574 | 0.653 | False | UNSAFE-TO-STOP | 0.902 | 0.513 | 1.000 | 1.322 | 0.284 |
| T4_real_repo_click_seed02_blind_seed02_pre_g2_pair3 | pre_audit | 1.000 | 0.805 | 0.892 | True | UNSAFE-TO-STOP | 0.782 | 0.611 | 1.000 | 1.242 | 0.178 |
| T4_real_repo_click_seed02_blind_seed02_pre_g3 | pre_audit | 1.000 | 0.639 | 0.780 | True | UNSAFE-TO-STOP | 0.902 | 0.495 | 1.000 | 1.508 | 0.535 |
| T4_real_repo_click_seed02_blind_seed02_post_holdout | post_audit | 1.000 | 0.613 | 0.760 | True | UNSAFE-TO-STOP | 1.000 | 0.564 | 1.000 | 1.486 | 1.000 |
| T4_real_repo_click_seed03_blind_seed03_pre_g1_agent1 | pre_audit | 0.671 | 0.671 | 0.671 | False | UNSAFE-TO-STOP | 0.902 | n/a | n/a | 1.000 | 0.987 |
| T4_real_repo_click_seed03_blind_seed03_pre_g1_agent2 | pre_audit | 1.000 | 1.000 | 1.000 | True | UNSAFE-TO-STOP | 0.782 | n/a | n/a | 1.000 | 0.987 |
| T4_real_repo_click_seed03_blind_seed03_pre_g1_agent3 | pre_audit | 0.678 | 0.678 | 0.678 | False | UNSAFE-TO-STOP | 0.902 | n/a | n/a | 1.000 | 0.987 |
| T4_real_repo_click_seed03_blind_seed03_pre_g2_pair1 | pre_audit | 1.000 | 0.753 | 0.859 | True | UNSAFE-TO-STOP | 0.782 | 0.505 | 1.000 | 1.329 | 0.294 |
| T4_real_repo_click_seed03_blind_seed03_pre_g2_pair2 | pre_audit | 0.779 | 0.583 | 0.667 | False | UNSAFE-TO-STOP | 0.902 | 0.497 | 1.000 | 1.336 | 0.303 |
| T4_real_repo_click_seed03_blind_seed03_pre_g2_pair3 | pre_audit | 1.000 | 0.756 | 0.861 | True | UNSAFE-TO-STOP | 0.782 | 0.513 | 1.000 | 1.322 | 0.284 |
| T4_real_repo_click_seed03_blind_seed03_pre_g3 | pre_audit | 1.000 | 0.642 | 0.782 | True | UNSAFE-TO-STOP | 0.902 | 0.505 | 1.000 | 1.492 | 0.669 |
| T4_real_repo_click_seed03_blind_seed03_post_holdout | post_audit | 1.000 | 0.634 | 0.776 | True | UNSAFE-TO-STOP | 1.000 | 0.567 | 1.000 | 1.480 | 0.497 |
| T5_real_repo_requests_tls_seed01_blind_seed01_pre_g1_agent1 | pre_audit | 0.724 | 0.753 | 0.738 | False | UNSAFE-TO-STOP | 0.760 | n/a | n/a | 1.000 | 0.993 |
| T5_real_repo_requests_tls_seed01_blind_seed01_pre_g1_agent2 | pre_audit | 0.668 | 0.698 | 0.682 | False | UNSAFE-TO-STOP | 0.880 | n/a | n/a | 1.000 | 0.993 |
| T5_real_repo_requests_tls_seed01_blind_seed01_pre_g1_agent3 | pre_audit | 0.694 | 0.681 | 0.687 | False | UNSAFE-TO-STOP | 0.880 | n/a | n/a | 1.000 | 0.994 |
| T5_real_repo_requests_tls_seed01_blind_seed01_pre_g2_pair1 | pre_audit | 0.842 | 0.688 | 0.757 | False | UNSAFE-TO-STOP | 0.730 | 0.567 | 0.429 | 1.276 | 0.222 |
| T5_real_repo_requests_tls_seed01_blind_seed01_pre_g2_pair2 | pre_audit | 0.753 | 0.672 | 0.710 | False | REQUIRES-AUDIT | 0.490 | 0.765 | 0.800 | 1.133 | 0.061 |
| T5_real_repo_requests_tls_seed01_blind_seed01_pre_g2_pair3 | pre_audit | 0.822 | 0.667 | 0.736 | False | UNSAFE-TO-STOP | 0.850 | 0.603 | 0.375 | 1.248 | 0.186 |
| T5_real_repo_requests_tls_seed01_blind_seed01_pre_g3 | pre_audit | 0.859 | 0.661 | 0.747 | False | UNSAFE-TO-STOP | 0.722 | 0.645 | 0.535 | 1.310 | 0.248 |
| T5_real_repo_requests_tls_seed01_blind_seed01_post_holdout | post_audit | 0.862 | 0.641 | 0.735 | False | UNSAFE-TO-STOP | 0.722 | 0.674 | 0.586 | 1.324 | 0.208 |
| T5_real_repo_requests_tls_seed02_blind_seed02_pre_g1_agent1 | pre_audit | 0.697 | 0.726 | 0.711 | False | UNSAFE-TO-STOP | 0.760 | n/a | n/a | 1.000 | 0.993 |
| T5_real_repo_requests_tls_seed02_blind_seed02_pre_g1_agent2 | pre_audit | 0.671 | 0.729 | 0.699 | False | UNSAFE-TO-STOP | 0.760 | n/a | n/a | 1.000 | 0.993 |
| T5_real_repo_requests_tls_seed02_blind_seed02_pre_g1_agent3 | pre_audit | 0.668 | 0.677 | 0.672 | False | UNSAFE-TO-STOP | 0.760 | n/a | n/a | 1.000 | 0.993 |
| T5_real_repo_requests_tls_seed02_blind_seed02_pre_g2_pair1 | pre_audit | 0.829 | 0.698 | 0.758 | False | UNSAFE-TO-STOP | 0.730 | 0.584 | 0.429 | 1.262 | 0.204 |
| T5_real_repo_requests_tls_seed02_blind_seed02_pre_g2_pair2 | pre_audit | 0.737 | 0.675 | 0.704 | False | REQUIRES-AUDIT | 0.466 | 0.783 | 0.800 | 1.122 | 0.052 |
| T5_real_repo_requests_tls_seed02_blind_seed02_pre_g2_pair3 | pre_audit | 0.803 | 0.668 | 0.729 | False | UNSAFE-TO-STOP | 0.730 | 0.589 | 0.375 | 1.259 | 0.199 |
| T5_real_repo_requests_tls_seed02_blind_seed02_pre_g3 | pre_audit | 0.845 | 0.668 | 0.746 | False | UNSAFE-TO-STOP | 0.722 | 0.652 | 0.535 | 1.302 | 0.278 |
| T5_real_repo_requests_tls_seed02_blind_seed02_post_holdout | post_audit | 0.845 | 0.661 | 0.742 | False | UNSAFE-TO-STOP | 0.813 | 0.686 | 0.586 | 1.308 | 0.300 |
| T5_real_repo_requests_tls_seed03_blind_seed03_pre_g1_agent1 | pre_audit | 0.681 | 0.724 | 0.702 | False | UNSAFE-TO-STOP | 0.880 | n/a | n/a | 1.000 | 0.993 |
| T5_real_repo_requests_tls_seed03_blind_seed03_pre_g1_agent2 | pre_audit | 0.622 | 0.735 | 0.674 | False | UNSAFE-TO-STOP | 0.887 | n/a | n/a | 1.000 | 0.992 |
| T5_real_repo_requests_tls_seed03_blind_seed03_pre_g1_agent3 | pre_audit | 0.694 | 0.718 | 0.706 | False | UNSAFE-TO-STOP | 0.760 | n/a | n/a | 1.000 | 0.993 |
| T5_real_repo_requests_tls_seed03_blind_seed03_pre_g2_pair1 | pre_audit | 0.799 | 0.704 | 0.749 | False | UNSAFE-TO-STOP | 0.857 | 0.574 | 0.500 | 1.271 | 0.215 |
| T5_real_repo_requests_tls_seed03_blind_seed03_pre_g2_pair2 | pre_audit | 0.743 | 0.681 | 0.711 | False | UNSAFE-TO-STOP | 0.638 | 0.747 | 0.800 | 1.145 | 0.072 |
| T5_real_repo_requests_tls_seed03_blind_seed03_pre_g2_pair3 | pre_audit | 0.793 | 0.695 | 0.740 | False | UNSAFE-TO-STOP | 0.857 | 0.588 | 0.429 | 1.260 | 0.200 |
| T5_real_repo_requests_tls_seed03_blind_seed03_pre_g3 | pre_audit | 0.829 | 0.676 | 0.744 | False | UNSAFE-TO-STOP | 0.850 | 0.636 | 0.576 | 1.320 | 0.264 |
| T5_real_repo_requests_tls_seed03_blind_seed03_post_holdout | post_audit | 0.839 | 0.656 | 0.736 | False | UNSAFE-TO-STOP | 0.825 | 0.665 | 0.633 | 1.336 | 0.189 |
