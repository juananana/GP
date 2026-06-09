# T5_real_repo_requests_tls_audit Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_G3_seed02_agent01 | G3 | seed02 | 0.890 | 292 | 212 | 80 | 0.697 | 0.726 | true |
| T5_G3_seed02_agent02 | G3 | seed02 | 0.860 | 280 | 204 | 76 | 0.671 | 0.729 | true |
| T5_G3_seed02_agent03 | G3 | seed02 | 0.910 | 300 | 203 | 97 | 0.668 | 0.677 | true |
| T5_G6_holdout_seed02 | G6 | seed02 | 0.780 | 287 | 209 | 78 | 0.688 | 0.728 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed02 | 0.887 | 0.652 | 0.252 | 0.678 | 0.845 | 0.688 | 0.072 | false |

## Bucket Recall By Seed

### seed02

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.857 | 0.929 | 0.786 |
| client_certificate | 0.938 | 0.938 | 0.938 |
| documentation | 0.600 | 0.800 | 0.708 |
| error_handling | 0.556 | 1.000 | 0.556 |
| implementation | 0.753 | 0.882 | 0.710 |
| test_coverage | 0.646 | 0.734 | 0.519 |
| test_infrastructure | 0.300 | 1.000 | 0.850 |
| verification_mode | 1.000 | 1.000 | 1.000 |

