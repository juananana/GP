# T4_click_heldout_staged_controller Expanded Score Summary

Oracle size: 149

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_click_seed04_homogeneous_G3_agent01 | G3 | seed04 | 0.000 | 179 | 103 | 76 | 0.691 | 0.575 | true |
| T4_click_seed04_homogeneous_G3_agent02 | G3 | seed04 | 0.000 | 205 | 113 | 92 | 0.758 | 0.551 | true |
| T4_click_seed04_homogeneous_G3_agent03 | G3 | seed04 | 0.820 | 171 | 101 | 70 | 0.678 | 0.591 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed04 | 0.273 | 0.837 | 0.146 | 0.691 | 0.765 | null | null | null |

## Bucket Recall By Seed

### seed04

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| command_behavior | 0.600 | 0.600 | null |
| documentation | 1.000 | 1.000 | null |
| implementation | 0.514 | 0.514 | null |
| message_formatting | 0.625 | 0.625 | null |
| parameter_behavior | 0.222 | 0.222 | null |
| test_coverage | 0.896 | 0.955 | null |
| warning_emission | 0.167 | 0.750 | null |

