# T5_real_repo_requests_tls_online_minimal Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed04_homogeneous_G3_agent01 | G3 | seed04 | 0.830 | 260 | 202 | 58 | 0.664 | 0.777 | true |
| T5_online_seed04_homogeneous_G3_agent02 | G3 | seed04 | 0.710 | 273 | 211 | 62 | 0.694 | 0.773 | true |
| T5_online_seed04_homogeneous_G3_agent03 | G3 | seed04 | 0.750 | 274 | 198 | 76 | 0.651 | 0.723 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed04 | 0.763 | 0.814 | 0.120 | 0.684 | 0.720 | null | null | null |

## Bucket Recall By Seed

### seed04

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.929 | 0.929 | null |
| client_certificate | 0.875 | 0.938 | null |
| documentation | 0.708 | 0.785 | null |
| error_handling | 0.778 | 0.778 | null |
| implementation | 0.860 | 0.892 | null |
| test_coverage | 0.278 | 0.291 | null |
| test_infrastructure | 0.900 | 0.950 | null |
| verification_mode | 1.000 | 1.000 | null |

