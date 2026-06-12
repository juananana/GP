# T4_click_heldout_staged_controller Expanded Score Summary

Oracle size: 149

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_click_seed06_source_partitioned_G3_agent01 | G3 | seed06 | 0.930 | 75 | 33 | 42 | 0.221 | 0.440 | true |
| T4_click_seed06_source_partitioned_G3_agent02 | G3 | seed06 | 0.950 | 89 | 66 | 23 | 0.443 | 0.742 | true |
| T4_click_seed06_source_partitioned_G3_agent03 | G3 | seed06 | 0.750 | 34 | 13 | 21 | 0.087 | 0.382 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed06 | 0.877 | 0.000 | 1.000 | 0.000 | 0.752 | null | null | null |

## Bucket Recall By Seed

### seed06

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| command_behavior | 0.000 | 0.600 | null |
| documentation | 0.000 | 1.000 | null |
| implementation | 0.000 | 0.457 | null |
| message_formatting | 0.000 | 0.625 | null |
| parameter_behavior | 0.000 | 0.222 | null |
| test_coverage | 0.000 | 0.985 | null |
| warning_emission | 0.000 | 0.583 | null |

