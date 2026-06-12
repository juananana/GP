# T5_real_repo_requests_tls_audit Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_G3_seed03_agent01 | G3 | seed03 | 0.660 | 286 | 207 | 79 | 0.681 | 0.724 | true |
| T5_G3_seed03_agent02 | G3 | seed03 | 0.730 | 257 | 189 | 68 | 0.622 | 0.735 | true |
| T5_G3_seed03_agent03 | G3 | seed03 | 0.860 | 294 | 211 | 83 | 0.694 | 0.718 | true |
| T5_G6_holdout_seed03 | G6 | seed03 | 0.790 | 326 | 232 | 94 | 0.763 | 0.712 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed03 | 0.750 | 0.636 | 0.255 | 0.678 | 0.829 | 0.763 | 0.112 | false |

## Bucket Recall By Seed

### seed03

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.857 | 0.929 | 0.857 |
| client_certificate | 0.938 | 0.938 | 0.938 |
| documentation | 0.600 | 0.831 | 0.769 |
| error_handling | 0.556 | 1.000 | 0.556 |
| implementation | 0.828 | 0.892 | 0.860 |
| test_coverage | 0.570 | 0.658 | 0.557 |
| test_infrastructure | 0.250 | 0.900 | 0.900 |
| verification_mode | 1.000 | 1.000 | 1.000 |

