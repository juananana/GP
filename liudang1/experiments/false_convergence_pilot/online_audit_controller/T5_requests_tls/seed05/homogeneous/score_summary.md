# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed05_homogeneous_G3_agent01 | G3 | seed05 | 0.780 | 294 | 213 | 81 | 0.701 | 0.724 | true |
| T5_online_seed05_homogeneous_G3_agent02 | G3 | seed05 | 0.840 | 270 | 203 | 67 | 0.668 | 0.752 | true |
| T5_online_seed05_homogeneous_G3_agent03 | G3 | seed05 | 0.790 | 264 | 201 | 63 | 0.661 | 0.761 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed05 | 0.803 | 0.826 | 0.148 | 0.674 | 0.734 | null | null | null |

## Bucket Recall By Seed

### seed05

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.929 | 0.929 | null |
| client_certificate | 0.938 | 0.938 | null |
| documentation | 0.723 | 0.785 | null |
| error_handling | 0.778 | 0.778 | null |
| implementation | 0.806 | 0.892 | null |
| test_coverage | 0.278 | 0.342 | null |
| test_infrastructure | 0.900 | 0.950 | null |
| verification_mode | 1.000 | 1.000 | null |

