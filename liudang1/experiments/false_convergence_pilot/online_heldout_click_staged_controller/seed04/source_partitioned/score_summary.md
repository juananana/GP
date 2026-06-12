# T4_click_heldout_staged_controller Expanded Score Summary

Oracle size: 149

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_click_seed04_source_partitioned_G3_agent01 | G3 | seed04 | 0.740 | 70 | 36 | 34 | 0.242 | 0.514 | true |
| T4_click_seed04_source_partitioned_G3_agent02 | G3 | seed04 | 0.930 | 75 | 65 | 10 | 0.436 | 0.867 | true |
| T4_click_seed04_source_partitioned_G3_agent03 | G3 | seed04 | 0.730 | 44 | 13 | 31 | 0.087 | 0.295 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed04 | 0.800 | 0.000 | 1.000 | 0.000 | 0.765 | null | null | null |

## Bucket Recall By Seed

### seed04

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| command_behavior | 0.000 | 0.600 | null |
| documentation | 0.000 | 1.000 | null |
| implementation | 0.000 | 0.514 | null |
| message_formatting | 0.000 | 0.625 | null |
| parameter_behavior | 0.000 | 0.222 | null |
| test_coverage | 0.000 | 0.970 | null |
| warning_emission | 0.000 | 0.667 | null |

