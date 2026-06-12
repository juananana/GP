# Source-Aware Audit v1 Results

This is an offline audit-policy prototype. It audits candidate line items
against deterministic source predicates derived from the task policy.
Report it as an upper-bound prototype, not as a blind LLM result.

| case | method | found | TP | FP | recall | precision |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| T4_real_repo_click_seed01_blind | majority_consensus | 143 | 142 | 1 | 0.953 | 0.993 |
| T4_real_repo_click_seed01_blind | raw_union | 199 | 148 | 51 | 0.993 | 0.744 |
| T4_real_repo_click_seed01_blind | holdout_union | 149 | 140 | 9 | 0.940 | 0.940 |
| T4_real_repo_click_seed01_blind | source_aware_audited_union | 148 | 148 | 0 | 0.993 | 1.000 |
| T4_real_repo_click_seed01_blind | source_aware_protocol_v1 | 149 | 148 | 1 | 0.993 | 0.993 |
| T4_real_repo_click_seed02_blind | majority_consensus | 135 | 113 | 22 | 0.758 | 0.837 |
| T4_real_repo_click_seed02_blind | raw_union | 233 | 149 | 84 | 1.000 | 0.639 |
| T4_real_repo_click_seed02_blind | holdout_union | 149 | 120 | 29 | 0.805 | 0.805 |
| T4_real_repo_click_seed02_blind | source_aware_audited_union | 149 | 149 | 0 | 1.000 | 1.000 |
| T4_real_repo_click_seed02_blind | source_aware_protocol_v1 | 171 | 149 | 22 | 1.000 | 0.871 |
| T4_real_repo_click_seed03_blind | majority_consensus | 130 | 116 | 14 | 0.779 | 0.892 |
| T4_real_repo_click_seed03_blind | raw_union | 232 | 149 | 83 | 1.000 | 0.642 |
| T4_real_repo_click_seed03_blind | holdout_union | 149 | 113 | 36 | 0.758 | 0.758 |
| T4_real_repo_click_seed03_blind | source_aware_audited_union | 149 | 149 | 0 | 1.000 | 1.000 |
| T4_real_repo_click_seed03_blind | source_aware_protocol_v1 | 163 | 149 | 14 | 1.000 | 0.914 |

## Interpretation

- If audited union improves precision over raw union while keeping high recall, the task policy can support stronger audit.
- If audited protocol still misses items, the missing mass is outside the current candidate pool and requires broader search, not only candidate filtering.
