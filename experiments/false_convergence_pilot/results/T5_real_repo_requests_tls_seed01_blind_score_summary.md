# T5_real_repo_requests_tls_audit Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_G3_seed01_agent01 | G3 | seed01 | 0.930 | 292 | 220 | 72 | 0.724 | 0.753 | true |
| T5_G3_seed01_agent02 | G3 | seed01 | 0.770 | 291 | 203 | 88 | 0.668 | 0.698 | true |
| T5_G3_seed01_agent03 | G3 | seed01 | 0.730 | 310 | 211 | 99 | 0.694 | 0.681 | true |
| T5_G6_holdout_seed01 | G6 | seed01 | 0.890 | 327 | 228 | 99 | 0.750 | 0.697 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed01 | 0.810 | 0.645 | 0.246 | 0.701 | 0.859 | 0.750 | 0.102 | false |

## Bucket Recall By Seed

### seed01

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.857 | 0.929 | 0.857 |
| client_certificate | 0.938 | 0.938 | 0.938 |
| documentation | 0.615 | 0.800 | 0.785 |
| error_handling | 0.556 | 1.000 | 0.556 |
| implementation | 0.828 | 0.914 | 0.796 |
| test_coverage | 0.633 | 0.747 | 0.557 |
| test_infrastructure | 0.300 | 1.000 | 0.950 |
| verification_mode | 1.000 | 1.000 | 1.000 |

