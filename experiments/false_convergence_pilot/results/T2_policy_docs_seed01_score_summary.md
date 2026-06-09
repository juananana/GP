# T2_policy_docs Expanded Score Summary

Oracle size: 30

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T2_G1_seed01 | G1 | seed01 | 0.880 | 28 | 28 | 0 | 0.933 | 1.000 | true |
| T2_G3_seed01_agent01 | G3 | seed01 | 0.920 | 28 | 28 | 0 | 0.933 | 1.000 | true |
| T2_G3_seed01_agent02 | G3 | seed01 | 0.880 | 30 | 30 | 0 | 1.000 | 1.000 | false |
| T2_G3_seed01_agent03 | G3 | seed01 | 0.860 | 28 | 28 | 0 | 0.933 | 1.000 | true |
| T2_G6_holdout_seed01 | G6 | seed01 | 0.910 | 30 | 30 | 0 | 1.000 | 1.000 | false |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed01 | 0.887 | 0.956 | 0.067 | 0.933 | 1.000 | 1.000 | 0.067 | false |

## Bucket Recall By Seed

### seed01

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| alias_resolution | 0.909 | 1.000 | 1.000 |
| queue_resolution | 1.000 | 1.000 | 1.000 |

