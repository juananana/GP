# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed08_independent_context_G3_agent01 | G3 | seed08 | 0.760 | 206 | 149 | 57 | 0.490 | 0.723 | true |
| T5_online_seed08_independent_context_G3_agent02 | G3 | seed08 | 0.590 | 134 | 97 | 37 | 0.319 | 0.724 | true |
| T5_online_seed08_independent_context_G3_agent03 | G3 | seed08 | 0.730 | 209 | 161 | 48 | 0.530 | 0.770 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed08 | 0.693 | 0.287 | 0.194 | 0.622 | 0.717 | null | null | null |

## Bucket Recall By Seed

### seed08

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.714 | 0.857 | null |
| client_certificate | 0.938 | 0.938 | null |
| documentation | 0.738 | 0.800 | null |
| error_handling | 0.556 | 0.778 | null |
| implementation | 0.677 | 0.839 | null |
| test_coverage | 0.278 | 0.354 | null |
| test_infrastructure | 0.900 | 0.900 | null |
| verification_mode | 1.000 | 1.000 | null |

