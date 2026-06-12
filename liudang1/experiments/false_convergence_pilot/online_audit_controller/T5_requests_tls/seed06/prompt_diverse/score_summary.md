# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed06_prompt_diverse_G3_agent01 | G3 | seed06 | 0.780 | 291 | 214 | 77 | 0.704 | 0.735 | true |
| T5_online_seed06_prompt_diverse_G3_agent02 | G3 | seed06 | 0.730 | 260 | 195 | 65 | 0.641 | 0.750 | true |
| T5_online_seed06_prompt_diverse_G3_agent03 | G3 | seed06 | 0.860 | 262 | 191 | 71 | 0.628 | 0.729 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed06 | 0.790 | 0.770 | 0.181 | 0.661 | 0.730 | null | null | null |

## Bucket Recall By Seed

### seed06

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.857 | 0.857 | null |
| client_certificate | 0.875 | 0.875 | null |
| documentation | 0.631 | 0.769 | null |
| error_handling | 0.778 | 0.778 | null |
| implementation | 0.806 | 0.860 | null |
| test_coverage | 0.329 | 0.405 | null |
| test_infrastructure | 0.900 | 0.950 | null |
| verification_mode | 1.000 | 1.000 | null |

