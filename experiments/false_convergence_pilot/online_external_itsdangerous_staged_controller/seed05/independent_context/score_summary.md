# T6_real_repo_itsdangerous_timed_signing_external Expanded Score Summary

Oracle size: 160

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T6_itsdangerous_seed05_independent_context_G3_agent01 | G3 | seed05 | 0.910 | 162 | 117 | 45 | 0.731 | 0.722 | true |
| T6_itsdangerous_seed05_independent_context_G3_agent02 | G3 | seed05 | 0.850 | 85 | 62 | 23 | 0.388 | 0.729 | true |
| T6_itsdangerous_seed05_independent_context_G3_agent03 | G3 | seed05 | 0.890 | 138 | 95 | 43 | 0.594 | 0.688 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed05 | 0.883 | 0.310 | 0.094 | 0.844 | 0.869 | null | null | null |

## Bucket Recall By Seed

### seed05

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| changelog | 0.700 | 0.800 | null |
| documentation | 0.933 | 0.933 | null |
| exception_types | 0.368 | 0.368 | null |
| implementation | 0.866 | 0.910 | null |
| public_exports | 1.000 | 1.000 | null |
| test_coverage | 1.000 | 1.000 | null |
| url_safe_timed_api | 1.000 | 1.000 | null |

