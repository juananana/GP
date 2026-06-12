# T5_real_repo_requests_tls_online_minimal Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed04_source_partitioned_G3_agent01 | G3 | seed04 | 0.940 | 162 | 119 | 43 | 0.391 | 0.735 | true |
| T5_online_seed04_source_partitioned_G3_agent02 | G3 | seed04 | 0.720 | 74 | 46 | 28 | 0.151 | 0.622 | true |
| T5_online_seed04_source_partitioned_G3_agent03 | G3 | seed04 | 0.880 | 66 | 52 | 14 | 0.171 | 0.788 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed04 | 0.847 | 0.000 | 1.000 | 0.000 | 0.714 | null | null | null |

## Bucket Recall By Seed

### seed04

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.000 | 0.857 | null |
| client_certificate | 0.000 | 0.938 | null |
| documentation | 0.000 | 0.800 | null |
| error_handling | 0.000 | 0.778 | null |
| implementation | 0.000 | 0.828 | null |
| test_coverage | 0.000 | 0.354 | null |
| test_infrastructure | 0.000 | 0.900 | null |
| verification_mode | 0.000 | 1.000 | null |

