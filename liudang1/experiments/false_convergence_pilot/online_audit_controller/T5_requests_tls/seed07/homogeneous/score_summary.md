# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed07_homogeneous_G3_agent01 | G3 | seed07 | 0.710 | 269 | 206 | 63 | 0.678 | 0.766 | true |
| T5_online_seed07_homogeneous_G3_agent02 | G3 | seed07 | 0.830 | 265 | 202 | 63 | 0.664 | 0.762 | true |
| T5_online_seed07_homogeneous_G3_agent03 | G3 | seed07 | 0.790 | 280 | 210 | 70 | 0.691 | 0.750 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed07 | 0.777 | 0.831 | 0.132 | 0.678 | 0.734 | null | null | null |

## Bucket Recall By Seed

### seed07

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.929 | 0.929 | null |
| client_certificate | 0.875 | 0.875 | null |
| documentation | 0.708 | 0.815 | null |
| error_handling | 0.778 | 0.778 | null |
| implementation | 0.839 | 0.892 | null |
| test_coverage | 0.278 | 0.316 | null |
| test_infrastructure | 0.900 | 1.000 | null |
| verification_mode | 1.000 | 1.000 | null |

