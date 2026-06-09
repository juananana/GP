# T1_hard_repo Expanded Score Summary

Oracle size: 35

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T1hard_G3_seed03_agent01 | G3 | seed03 | 0.900 | 40 | 35 | 5 | 1.000 | 0.875 | false |
| T1hard_G3_seed03_agent02 | G3 | seed03 | 0.880 | 35 | 35 | 0 | 1.000 | 1.000 | false |
| T1hard_G3_seed03_agent03 | G3 | seed03 | 0.900 | 22 | 22 | 0 | 0.629 | 1.000 | true |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed03 | 0.893 | 0.685 | 0.125 | 1.000 | 1.000 | null | null | null |

## Bucket Recall By Seed

### seed03

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| explicit_config | 1.000 | 1.000 | null |
| queue_downstream | 1.000 | 1.000 | null |
| region_downstream | 1.000 | 1.000 | null |
| registry | 1.000 | 1.000 | null |
| route_downstream | 1.000 | 1.000 | null |
| script_downstream | 1.000 | 1.000 | null |
| tenant_downstream | 1.000 | 1.000 | null |

