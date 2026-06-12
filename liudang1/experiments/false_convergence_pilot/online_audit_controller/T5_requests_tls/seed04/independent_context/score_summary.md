# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed04_independent_context_G3_agent01 | G3 | seed04 | 0.830 | 216 | 161 | 55 | 0.530 | 0.745 | true |
| T5_online_seed04_independent_context_G3_agent02 | G3 | seed04 | 0.670 | 132 | 96 | 36 | 0.316 | 0.727 | true |
| T5_online_seed04_independent_context_G3_agent03 | G3 | seed04 | 0.820 | 203 | 158 | 45 | 0.520 | 0.778 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed04 | 0.773 | 0.282 | 0.205 | 0.628 | 0.737 | null | null | null |

## Bucket Recall By Seed

### seed04

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.786 | 0.929 | null |
| client_certificate | 0.875 | 0.938 | null |
| documentation | 0.738 | 0.800 | null |
| error_handling | 0.556 | 0.778 | null |
| implementation | 0.677 | 0.860 | null |
| test_coverage | 0.304 | 0.380 | null |
| test_infrastructure | 0.900 | 0.950 | null |
| verification_mode | 1.000 | 1.000 | null |

