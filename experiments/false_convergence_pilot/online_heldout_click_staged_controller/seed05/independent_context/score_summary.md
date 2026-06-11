# T4_click_heldout_staged_controller Expanded Score Summary

Oracle size: 149

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_click_seed05_independent_context_G3_agent01 | G3 | seed05 | 0.910 | 144 | 92 | 52 | 0.617 | 0.639 | true |
| T4_click_seed05_independent_context_G3_agent02 | G3 | seed05 | 0.640 | 103 | 72 | 31 | 0.483 | 0.699 | true |
| T4_click_seed05_independent_context_G3_agent03 | G3 | seed05 | 0.860 | 110 | 51 | 59 | 0.342 | 0.464 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed05 | 0.803 | 0.264 | 0.292 | 0.698 | 0.745 | null | null | null |

## Bucket Recall By Seed

### seed05

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| command_behavior | 0.600 | 0.600 | null |
| documentation | 1.000 | 1.000 | null |
| implementation | 0.457 | 0.543 | null |
| message_formatting | 0.625 | 0.625 | null |
| parameter_behavior | 0.222 | 0.222 | null |
| test_coverage | 0.881 | 0.896 | null |
| warning_emission | 0.500 | 0.750 | null |

