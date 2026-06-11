# T4_click_heldout_staged_controller Expanded Score Summary

Oracle size: 149

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_click_seed06_independent_context_G3_agent01 | G3 | seed06 | 0.000 | 147 | 89 | 58 | 0.597 | 0.605 | true |
| T4_click_seed06_independent_context_G3_agent02 | G3 | seed06 | 0.750 | 94 | 68 | 26 | 0.456 | 0.723 | true |
| T4_click_seed06_independent_context_G3_agent03 | G3 | seed06 | 0.860 | 143 | 50 | 93 | 0.336 | 0.350 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed06 | 0.537 | 0.245 | 0.366 | 0.651 | 0.738 | null | null | null |

## Bucket Recall By Seed

### seed06

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| command_behavior | 0.600 | 0.600 | null |
| documentation | 1.000 | 1.000 | null |
| implementation | 0.343 | 0.514 | null |
| message_formatting | 0.625 | 0.625 | null |
| parameter_behavior | 0.222 | 0.222 | null |
| test_coverage | 0.821 | 0.896 | null |
| warning_emission | 0.583 | 0.750 | null |

