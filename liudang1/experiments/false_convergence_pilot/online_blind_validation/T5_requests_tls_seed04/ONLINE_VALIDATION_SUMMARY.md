# Online Blind Validation Minimal Results

Generated from completed online blind runs. Oracle scoring is applied only after agent outputs are written.

| condition | mean conf. | mean Jaccard | singleton ratio | consensus recall | union recall | union precision | input tokens | output tokens | wall-clock s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| homogeneous | 0.763 | 0.814 | 0.120 | 0.684 | 0.720 | 0.709 | 198444 | 13646 | 135.939 |
| prompt_diverse | 0.760 | 0.777 | 0.135 | 0.688 | 0.737 | 0.718 | 198463 | 14211 | 121.180 |
| source_partitioned | 0.847 | 0.000 | 1.000 | 0.000 | 0.714 | 0.719 | 67751 | 6110 | 59.863 |

## Interpretation

- All three online G3 conditions remain below the 0.95 completion threshold on Requests TLS seed04.
- Prompt diversity gives a small union-recall gain over homogeneous agents in this single seed.
- Source partitioning reduces token cost and keeps union recall near the homogeneous run, but majority consensus collapses because partitions have no item overlap; source-partitioned exploration needs a union/audit ledger rather than majority voting.

## Output Paths

- Manifest: `experiments\false_convergence_pilot\online_blind_validation\T5_requests_tls_seed04\MANIFEST.json`
- Summary CSV: `experiments\false_convergence_pilot\online_blind_validation\T5_requests_tls_seed04\ONLINE_VALIDATION_SUMMARY.csv`
- Per-condition directories contain `runs/`, `raw/`, `cost/`, `merged_itemsets.json`, `score_summary.json`, and `score_summary.md`.
