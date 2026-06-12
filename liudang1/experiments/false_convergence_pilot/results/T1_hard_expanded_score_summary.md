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
| T1hard_G1_seed02 | G1 | seed02 | 0.900 | 38 | 35 | 3 | 1.000 | 0.921 | false |
| T1hard_G3_seed02_agent01 | G3 | seed02 | 0.900 | 39 | 35 | 4 | 1.000 | 0.897 | false |
| T1hard_G3_seed02_agent02 | G3 | seed02 | 0.880 | 35 | 35 | 0 | 1.000 | 1.000 | false |
| T1hard_G3_seed02_agent03 | G3 | seed02 | 0.940 | 35 | 35 | 0 | 1.000 | 1.000 | false |
| T1hard_G1_seed03 | G1 | seed03 | 0.910 | 35 | 35 | 0 | 1.000 | 1.000 | false |
| T1hard_G3_seed03_agent01 | G3 | seed03 | 0.900 | 40 | 35 | 5 | 1.000 | 0.875 | false |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed01 | 0.853 | 0.752 | 0.371 | 0.629 | 1.000 | 1.000 | 0.371 | true |
| seed02 | 0.907 | 0.932 | 0.103 | 1.000 | 1.000 | null | null | null |

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

### seed02

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| explicit_config | 1.000 | 1.000 | null |
| queue_downstream | 1.000 | 1.000 | null |
| region_downstream | 1.000 | 1.000 | null |
| registry | 1.000 | 1.000 | null |
| route_downstream | 1.000 | 1.000 | null |
| script_downstream | 1.000 | 1.000 | null |
| tenant_downstream | 1.000 | 1.000 | null |

