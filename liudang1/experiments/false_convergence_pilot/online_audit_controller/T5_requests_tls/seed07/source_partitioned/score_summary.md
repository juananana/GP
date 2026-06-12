# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed07_source_partitioned_G3_agent01 | G3 | seed07 | 0.870 | 154 | 120 | 34 | 0.395 | 0.779 | true |
| T5_online_seed07_source_partitioned_G3_agent02 | G3 | seed07 | 0.830 | 65 | 45 | 20 | 0.148 | 0.692 | true |
| T5_online_seed07_source_partitioned_G3_agent03 | G3 | seed07 | 0.900 | 61 | 51 | 10 | 0.168 | 0.836 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed07 | 0.867 | 0.000 | 1.000 | 0.000 | 0.711 | null | null | null |

## Bucket Recall By Seed

### seed07

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.000 | 0.929 | null |
| client_certificate | 0.000 | 0.875 | null |
| documentation | 0.000 | 0.785 | null |
| error_handling | 0.000 | 0.778 | null |
| implementation | 0.000 | 0.839 | null |
| test_coverage | 0.000 | 0.342 | null |
| test_infrastructure | 0.000 | 0.900 | null |
| verification_mode | 0.000 | 1.000 | null |

