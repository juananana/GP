# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed06_independent_context_G3_agent01 | G3 | seed06 | 0.630 | 217 | 159 | 58 | 0.523 | 0.733 | true |
| T5_online_seed06_independent_context_G3_agent02 | G3 | seed06 | 0.720 | 133 | 99 | 34 | 0.326 | 0.744 | true |
| T5_online_seed06_independent_context_G3_agent03 | G3 | seed06 | 0.730 | 208 | 164 | 44 | 0.539 | 0.788 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed06 | 0.693 | 0.285 | 0.206 | 0.635 | 0.753 | null | null | null |

## Bucket Recall By Seed

### seed06

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.857 | 0.929 | null |
| client_certificate | 0.938 | 0.938 | null |
| documentation | 0.692 | 0.815 | null |
| error_handling | 0.556 | 0.778 | null |
| implementation | 0.742 | 0.892 | null |
| test_coverage | 0.266 | 0.380 | null |
| test_infrastructure | 0.900 | 1.000 | null |
| verification_mode | 1.000 | 1.000 | null |

