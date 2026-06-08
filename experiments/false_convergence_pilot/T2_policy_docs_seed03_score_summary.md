# T2_policy_docs Expanded Score Summary

Oracle size: 30

## Individual Runs

| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T2_G3_seed03_agent01 | G3 | seed03 | 0.940 | 28 | 28 | 0 | 0.933 | 1.000 | true |
| T2_G3_seed03_agent02 | G3 | seed03 | 0.910 | 28 | 28 | 0 | 0.933 | 1.000 | true |
| T2_G3_seed03_agent03 | G3 | seed03 | 0.910 | 28 | 28 | 0 | 0.933 | 1.000 | true |
| T2_G6_holdout_seed03 | G6 | seed03 | 0.940 | 30 | 30 | 0 | 1.000 | 1.000 | false |

## G3 Seed Aggregates

| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed03 | 0.920 | 1.000 | 0.000 | 0.933 | 0.933 | 1.000 | 0.067 | false |

## Bucket Recall By Seed

### seed03

| bucket | consensus | union | holdout |
| --- | ---: | ---: | ---: |
| alias_resolution | 0.909 | 0.909 | 1.000 |
| queue_resolution | 1.000 | 1.000 | 1.000 |

