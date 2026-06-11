# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed07_prompt_diverse_G3_agent01 | G3 | seed07 | 0.740 | 245 | 194 | 51 | 0.638 | 0.792 | true |
| T5_online_seed07_prompt_diverse_G3_agent02 | G3 | seed07 | 0.830 | 255 | 194 | 61 | 0.638 | 0.761 | true |
| T5_online_seed07_prompt_diverse_G3_agent03 | G3 | seed07 | 0.780 | 262 | 198 | 64 | 0.651 | 0.756 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed07 | 0.783 | 0.797 | 0.164 | 0.638 | 0.707 | null | null | null |

## Bucket Recall By Seed

### seed07

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.786 | 0.929 | null |
| client_certificate | 0.875 | 0.875 | null |
| documentation | 0.692 | 0.738 | null |
| error_handling | 0.778 | 0.778 | null |
| implementation | 0.763 | 0.860 | null |
| test_coverage | 0.266 | 0.316 | null |
| test_infrastructure | 0.850 | 1.000 | null |
| verification_mode | 1.000 | 1.000 | null |

