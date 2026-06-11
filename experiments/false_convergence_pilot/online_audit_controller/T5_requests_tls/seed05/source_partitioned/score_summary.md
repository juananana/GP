# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed05_source_partitioned_G3_agent01 | G3 | seed05 | 0.780 | 166 | 123 | 43 | 0.405 | 0.741 | true |
| T5_online_seed05_source_partitioned_G3_agent02 | G3 | seed05 | 0.810 | 69 | 45 | 24 | 0.148 | 0.652 | true |
| T5_online_seed05_source_partitioned_G3_agent03 | G3 | seed05 | 0.930 | 64 | 52 | 12 | 0.171 | 0.812 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed05 | 0.840 | 0.000 | 1.000 | 0.000 | 0.724 | null | null | null |

## Bucket Recall By Seed

### seed05

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.000 | 0.929 | null |
| client_certificate | 0.000 | 0.938 | null |
| documentation | 0.000 | 0.800 | null |
| error_handling | 0.000 | 0.778 | null |
| implementation | 0.000 | 0.860 | null |
| test_coverage | 0.000 | 0.342 | null |
| test_infrastructure | 0.000 | 0.900 | null |
| verification_mode | 0.000 | 1.000 | null |

