# T1_hard_repo Expanded Score Summary

Oracle size: 35

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T1hard_G1_seed01 | G1 | seed01 | 0.900 | 22 | 22 | 0 | 0.629 | 1.000 | true |
| T1hard_G3_seed01_agent01 | G3 | seed01 | 0.840 | 22 | 22 | 0 | 0.629 | 1.000 | true |
| T1hard_G3_seed01_agent02 | G3 | seed01 | 0.880 | 22 | 22 | 0 | 0.629 | 1.000 | true |
| T1hard_G3_seed01_agent03 | G3 | seed01 | 0.840 | 35 | 35 | 0 | 1.000 | 1.000 | false |
| T1hard_G6_holdout_seed01 | G6 | seed01 | 0.880 | 35 | 35 | 0 | 1.000 | 1.000 | false |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed01 | 0.853 | 0.752 | 0.371 | 0.629 | 1.000 | 1.000 | 0.371 | true |

## Bucket Recall By Seed

### seed01

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| explicit_config | 1.000 | 1.000 | 1.000 |
| queue_downstream | 0.500 | 1.000 | 1.000 |
| region_downstream | 0.333 | 1.000 | 1.000 |
| registry | 1.000 | 1.000 | 1.000 |
| route_downstream | 0.500 | 1.000 | 1.000 |
| script_downstream | 0.600 | 1.000 | 1.000 |
| tenant_downstream | 0.333 | 1.000 | 1.000 |

