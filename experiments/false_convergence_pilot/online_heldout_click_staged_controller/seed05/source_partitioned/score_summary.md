# T4_click_heldout_staged_controller Expanded Score Summary

Oracle size: 149

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_click_seed05_source_partitioned_G3_agent01 | G3 | seed05 | 0.880 | 77 | 34 | 43 | 0.228 | 0.442 | true |
| T4_click_seed05_source_partitioned_G3_agent02 | G3 | seed05 | 0.860 | 67 | 60 | 7 | 0.403 | 0.896 | true |
| T4_click_seed05_source_partitioned_G3_agent03 | G3 | seed05 | 0.830 | 30 | 13 | 17 | 0.087 | 0.433 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed05 | 0.857 | 0.000 | 1.000 | 0.000 | 0.718 | null | null | null |

## Bucket Recall By Seed

### seed05

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| command_behavior | 0.000 | 0.600 | null |
| documentation | 0.000 | 1.000 | null |
| implementation | 0.000 | 0.429 | null |
| message_formatting | 0.000 | 0.625 | null |
| parameter_behavior | 0.000 | 0.222 | null |
| test_coverage | 0.000 | 0.896 | null |
| warning_emission | 0.000 | 0.750 | null |

