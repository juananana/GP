# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed08_prompt_diverse_G3_agent01 | G3 | seed08 | 0.730 | 282 | 204 | 78 | 0.671 | 0.723 | true |
| T5_online_seed08_prompt_diverse_G3_agent02 | G3 | seed08 | 0.840 | 256 | 192 | 64 | 0.632 | 0.750 | true |
| T5_online_seed08_prompt_diverse_G3_agent03 | G3 | seed08 | 0.690 | 264 | 199 | 65 | 0.655 | 0.754 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed08 | 0.753 | 0.783 | 0.134 | 0.678 | 0.717 | null | null | null |

## Bucket Recall By Seed

### seed08

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.857 | 0.857 | null |
| client_certificate | 0.875 | 0.938 | null |
| documentation | 0.692 | 0.785 | null |
| error_handling | 0.778 | 0.778 | null |
| implementation | 0.806 | 0.849 | null |
| test_coverage | 0.342 | 0.342 | null |
| test_infrastructure | 0.900 | 0.950 | null |
| verification_mode | 1.000 | 1.000 | null |

