# T4_click_heldout_staged_controller Expanded Score Summary

Oracle size: 149

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_click_seed05_homogeneous_G3_agent01 | G3 | seed05 | 0.920 | 182 | 109 | 73 | 0.732 | 0.599 | true |
| T4_click_seed05_homogeneous_G3_agent02 | G3 | seed05 | 0.000 | 186 | 113 | 73 | 0.758 | 0.608 | true |
| T4_click_seed05_homogeneous_G3_agent03 | G3 | seed05 | 0.000 | 176 | 102 | 74 | 0.685 | 0.580 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed05 | 0.307 | 0.876 | 0.056 | 0.758 | 0.758 | null | null | null |

## Bucket Recall By Seed

### seed05

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| command_behavior | 0.600 | 0.600 | null |
| documentation | 1.000 | 1.000 | null |
| implementation | 0.514 | 0.514 | null |
| message_formatting | 0.625 | 0.625 | null |
| parameter_behavior | 0.222 | 0.222 | null |
| test_coverage | 0.940 | 0.940 | null |
| warning_emission | 0.750 | 0.750 | null |

