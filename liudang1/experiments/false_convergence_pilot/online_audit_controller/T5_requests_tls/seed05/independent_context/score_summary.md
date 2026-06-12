# T5_real_repo_requests_tls_online_audit_controller Expanded Score Summary

Oracle size: 304

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T5_online_seed05_independent_context_G3_agent01 | G3 | seed05 | 0.680 | 219 | 162 | 57 | 0.533 | 0.740 | true |
| T5_online_seed05_independent_context_G3_agent02 | G3 | seed05 | 0.770 | 128 | 96 | 32 | 0.316 | 0.750 | true |
| T5_online_seed05_independent_context_G3_agent03 | G3 | seed05 | 0.670 | 198 | 152 | 46 | 0.500 | 0.768 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed05 | 0.707 | 0.280 | 0.219 | 0.615 | 0.734 | null | null | null |

## Bucket Recall By Seed

### seed05

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| ca_bundle_resolution | 0.857 | 0.929 | null |
| client_certificate | 0.875 | 0.875 | null |
| documentation | 0.615 | 0.800 | null |
| error_handling | 0.556 | 0.778 | null |
| implementation | 0.731 | 0.882 | null |
| test_coverage | 0.291 | 0.354 | null |
| test_infrastructure | 0.850 | 0.950 | null |
| verification_mode | 1.000 | 1.000 | null |

