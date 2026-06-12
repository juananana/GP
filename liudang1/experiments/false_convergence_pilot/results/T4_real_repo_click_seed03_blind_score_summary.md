# T4_real_repo_click_deprecation Expanded Score Summary

Oracle size: 149

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_G3_seed03_agent01 | G3 | seed03 | 0.720 | 149 | 100 | 49 | 0.671 | 0.671 | true |
| T4_G3_seed03_agent02 | G3 | seed03 | 0.930 | 149 | 149 | 0 | 1.000 | 1.000 | false |
| T4_G3_seed03_agent03 | G3 | seed03 | 0.740 | 149 | 101 | 48 | 0.678 | 0.678 | true |
| T4_G6_holdout_seed03 | G6 | seed03 | 0.740 | 149 | 113 | 36 | 0.758 | 0.758 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed03 | 0.797 | 0.505 | 0.440 | 0.779 | 1.000 | 0.758 | 0.054 | false |

## Bucket Recall By Seed

### seed03

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| command_behavior | 0.800 | 1.000 | 1.000 |
| documentation | 1.000 | 1.000 | 1.000 |
| implementation | 0.886 | 1.000 | 0.943 |
| message_formatting | 1.000 | 1.000 | 1.000 |
| parameter_behavior | 0.333 | 1.000 | 0.889 |
| test_coverage | 0.672 | 1.000 | 0.522 |
| warning_emission | 1.000 | 1.000 | 0.917 |

