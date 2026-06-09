# T4_real_repo_click_deprecation Expanded Score Summary

Oracle size: 149

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_G3_seed02_agent01 | G3 | seed02 | 0.640 | 149 | 79 | 70 | 0.530 | 0.530 | true |
| T4_G3_seed02_agent02 | G3 | seed02 | 0.980 | 149 | 149 | 0 | 1.000 | 1.000 | false |
| T4_G3_seed02_agent03 | G3 | seed02 | 0.660 | 149 | 113 | 36 | 0.758 | 0.758 | true |
| T4_G6_holdout_seed02 | G6 | seed02 | 0.680 | 149 | 120 | 29 | 0.805 | 0.805 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed02 | 0.760 | 0.495 | 0.421 | 0.758 | 1.000 | 0.805 | 0.047 | false |

## Bucket Recall By Seed

### seed02

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| command_behavior | 0.800 | 1.000 | 0.800 |
| documentation | 1.000 | 1.000 | 1.000 |
| implementation | 0.800 | 1.000 | 0.886 |
| message_formatting | 1.000 | 1.000 | 1.000 |
| parameter_behavior | 0.333 | 1.000 | 0.333 |
| test_coverage | 0.687 | 1.000 | 0.746 |
| warning_emission | 0.917 | 1.000 | 0.917 |

