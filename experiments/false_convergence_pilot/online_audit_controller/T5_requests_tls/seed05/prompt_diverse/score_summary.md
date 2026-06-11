# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed05_prompt_diverse_G3_agent01 | G3 | seed05 | 0.750 | 269 | 205 | 64 | 0.674 | 0.762 | true |
| T5_online_seed05_prompt_diverse_G3_agent02 | G3 | seed05 | 0.830 | 234 | 179 | 55 | 0.589 | 0.765 | true |
| T5_online_seed05_prompt_diverse_G3_agent03 | G3 | seed05 | 0.740 | 252 | 197 | 55 | 0.648 | 0.782 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed05 | 0.773 | 0.765 | 0.175 | 0.645 | 0.730 | null | null | null |

## Bucket Recall By Seed

### seed05

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.857 | 0.929 | null |
| client_certificate | 0.875 | 0.875 | null |
| documentation | 0.708 | 0.769 | null |
| error_handling | 0.778 | 0.778 | null |
| implementation | 0.731 | 0.903 | null |
| test_coverage | 0.291 | 0.354 | null |
| test_infrastructure | 0.900 | 0.900 | null |
| verification_mode | 1.000 | 1.000 | null |

