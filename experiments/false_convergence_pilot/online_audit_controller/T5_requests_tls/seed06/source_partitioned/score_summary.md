# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed06_source_partitioned_G3_agent01 | G3 | seed06 | 0.860 | 172 | 127 | 45 | 0.418 | 0.738 | true |
| T5_online_seed06_source_partitioned_G3_agent02 | G3 | seed06 | 0.780 | 71 | 47 | 24 | 0.155 | 0.662 | true |
| T5_online_seed06_source_partitioned_G3_agent03 | G3 | seed06 | 0.910 | 63 | 50 | 13 | 0.164 | 0.794 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed06 | 0.850 | 0.000 | 1.000 | 0.000 | 0.737 | null | null | null |

## Bucket Recall By Seed

### seed06

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.000 | 0.929 | null |
| client_certificate | 0.000 | 0.875 | null |
| documentation | 0.000 | 0.769 | null |
| error_handling | 0.000 | 0.778 | null |
| implementation | 0.000 | 0.914 | null |
| test_coverage | 0.000 | 0.367 | null |
| test_infrastructure | 0.000 | 0.900 | null |
| verification_mode | 0.000 | 1.000 | null |

