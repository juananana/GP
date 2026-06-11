# T4_click_heldout_staged_controller Expanded Score Summary

Oracle size: 149

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_click_seed04_independent_context_G3_agent01 | G3 | seed04 | 0.000 | 115 | 84 | 31 | 0.564 | 0.730 | true |
| T4_click_seed04_independent_context_G3_agent02 | G3 | seed04 | 0.860 | 94 | 70 | 24 | 0.470 | 0.745 | true |
| T4_click_seed04_independent_context_G3_agent03 | G3 | seed04 | 0.000 | 105 | 46 | 59 | 0.309 | 0.438 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed04 | 0.287 | 0.252 | 0.365 | 0.638 | 0.705 | null | null | null |

## Bucket Recall By Seed

### seed04

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| command_behavior | 0.400 | 0.600 | null |
| documentation | 1.000 | 1.000 | null |
| implementation | 0.457 | 0.457 | null |
| message_formatting | 0.625 | 0.625 | null |
| parameter_behavior | 0.222 | 0.222 | null |
| test_coverage | 0.836 | 0.881 | null |
| warning_emission | 0.083 | 0.583 | null |

