# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed08_source_partitioned_G3_agent01 | G3 | seed08 | 0.860 | 175 | 126 | 49 | 0.414 | 0.720 | true |
| T5_online_seed08_source_partitioned_G3_agent02 | G3 | seed08 | 0.780 | 70 | 46 | 24 | 0.151 | 0.657 | true |
| T5_online_seed08_source_partitioned_G3_agent03 | G3 | seed08 | 0.770 | 62 | 51 | 11 | 0.168 | 0.823 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed08 | 0.803 | 0.000 | 1.000 | 0.000 | 0.734 | null | null | null |

## Bucket Recall By Seed

### seed08

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.000 | 0.929 | null |
| client_certificate | 0.000 | 0.938 | null |
| documentation | 0.000 | 0.785 | null |
| error_handling | 0.000 | 0.556 | null |
| implementation | 0.000 | 0.914 | null |
| test_coverage | 0.000 | 0.354 | null |
| test_infrastructure | 0.000 | 0.900 | null |
| verification_mode | 0.000 | 1.000 | null |

