# T4_real_repo_click_deprecation Expanded Score Summary

Oracle size: 149

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_G3_seed01_agent01 | G3 | seed01 | 0.820 | 149 | 148 | 1 | 0.993 | 0.993 | false |
| T4_G3_seed01_agent02 | G3 | seed01 | 0.740 | 149 | 142 | 7 | 0.953 | 0.953 | false |
| T4_G3_seed01_agent03 | G3 | seed01 | 0.780 | 149 | 104 | 45 | 0.698 | 0.698 | true |
| T4_G6_holdout_seed01 | G6 | seed01 | 0.720 | 149 | 140 | 9 | 0.940 | 0.940 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed01 | 0.780 | 0.670 | 0.281 | 0.953 | 0.993 | 0.940 | 0.040 | false |

## Bucket Recall By Seed

### seed01

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| command_behavior | 1.000 | 1.000 | 1.000 |
| documentation | 1.000 | 1.000 | 0.385 |
| implementation | 0.914 | 0.971 | 0.971 |
| message_formatting | 1.000 | 1.000 | 1.000 |
| parameter_behavior | 0.889 | 1.000 | 1.000 |
| test_coverage | 0.970 | 1.000 | 1.000 |
| warning_emission | 0.917 | 1.000 | 1.000 |

