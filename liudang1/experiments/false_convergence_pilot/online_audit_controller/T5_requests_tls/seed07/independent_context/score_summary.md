# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed07_independent_context_G3_agent01 | G3 | seed07 | 0.830 | 207 | 158 | 49 | 0.520 | 0.763 | true |
| T5_online_seed07_independent_context_G3_agent02 | G3 | seed07 | 0.760 | 137 | 100 | 37 | 0.329 | 0.730 | true |
| T5_online_seed07_independent_context_G3_agent03 | G3 | seed07 | 0.790 | 196 | 153 | 43 | 0.503 | 0.781 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed07 | 0.793 | 0.289 | 0.188 | 0.632 | 0.720 | null | null | null |

## Bucket Recall By Seed

### seed07

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.786 | 0.857 | null |
| client_certificate | 0.812 | 0.875 | null |
| documentation | 0.723 | 0.815 | null |
| error_handling | 0.778 | 0.778 | null |
| implementation | 0.699 | 0.828 | null |
| test_coverage | 0.316 | 0.367 | null |
| test_infrastructure | 0.800 | 0.950 | null |
| verification_mode | 1.000 | 1.000 | null |

