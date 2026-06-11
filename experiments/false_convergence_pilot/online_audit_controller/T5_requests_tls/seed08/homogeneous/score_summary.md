# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed08_homogeneous_G3_agent01 | G3 | seed08 | 0.870 | 275 | 201 | 74 | 0.661 | 0.731 | true |
| T5_online_seed08_homogeneous_G3_agent02 | G3 | seed08 | 0.860 | 254 | 200 | 54 | 0.658 | 0.787 | true |
| T5_online_seed08_homogeneous_G3_agent03 | G3 | seed08 | 0.740 | 272 | 206 | 66 | 0.678 | 0.757 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed08 | 0.823 | 0.792 | 0.144 | 0.681 | 0.734 | null | null | null |

## Bucket Recall By Seed

### seed08

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.929 | 0.929 | null |
| client_certificate | 0.875 | 0.875 | null |
| documentation | 0.723 | 0.785 | null |
| error_handling | 0.778 | 0.778 | null |
| implementation | 0.828 | 0.871 | null |
| test_coverage | 0.278 | 0.367 | null |
| test_infrastructure | 0.950 | 1.000 | null |
| verification_mode | 1.000 | 1.000 | null |

