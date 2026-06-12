# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed06_homogeneous_G3_agent01 | G3 | seed06 | 0.660 | 270 | 207 | 63 | 0.681 | 0.767 | true |
| T5_online_seed06_homogeneous_G3_agent02 | G3 | seed06 | 0.780 | 285 | 203 | 82 | 0.668 | 0.712 | true |
| T5_online_seed06_homogeneous_G3_agent03 | G3 | seed06 | 0.860 | 255 | 204 | 51 | 0.671 | 0.800 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed06 | 0.767 | 0.798 | 0.158 | 0.671 | 0.740 | null | null | null |

## Bucket Recall By Seed

### seed06

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.929 | 0.929 | null |
| client_certificate | 0.938 | 0.938 | null |
| documentation | 0.692 | 0.754 | null |
| error_handling | 0.556 | 0.778 | null |
| implementation | 0.839 | 0.892 | null |
| test_coverage | 0.278 | 0.392 | null |
| test_infrastructure | 0.900 | 0.950 | null |
| verification_mode | 1.000 | 1.000 | null |

