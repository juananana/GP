# T5_real_repo_requests_tls_online_minimal Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed04_prompt_diverse_G3_agent01 | G3 | seed04 | 0.770 | 255 | 195 | 60 | 0.641 | 0.765 | true |
| T5_online_seed04_prompt_diverse_G3_agent02 | G3 | seed04 | 0.740 | 262 | 199 | 63 | 0.655 | 0.760 | true |
| T5_online_seed04_prompt_diverse_G3_agent03 | G3 | seed04 | 0.770 | 277 | 210 | 67 | 0.691 | 0.758 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed04 | 0.760 | 0.777 | 0.135 | 0.688 | 0.737 | null | null | null |

## Bucket Recall By Seed

### seed04

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.929 | 0.929 | null |
| client_certificate | 0.875 | 0.875 | null |
| documentation | 0.785 | 0.785 | null |
| error_handling | 0.778 | 0.778 | null |
| implementation | 0.828 | 0.871 | null |
| test_coverage | 0.266 | 0.392 | null |
| test_infrastructure | 0.900 | 0.950 | null |
| verification_mode | 1.000 | 1.000 | null |

