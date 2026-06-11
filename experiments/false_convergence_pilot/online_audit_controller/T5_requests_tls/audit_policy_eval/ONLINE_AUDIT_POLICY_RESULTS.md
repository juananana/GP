# Online Audit-Policy Results

Policy triggers and queues are computed from frozen blind-discovery logs.
Oracle scoring is applied only after online audit evidence is written.

## Policy Means

| policy | n | pre R | post R | precision | recovered TP | introduced FP | audit tokens | wall-clock s | cost/TP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no-audit | 20 | 0.491 | 0.491 | 0.829 | 0.0 | 0.0 | 0 | 0.0 |  |
| random-holdout | 20 | 0.491 | 0.554 | 0.755 | 18.9 | 11.9 | 16657 | 31.7 | 1529 |
| singleton-audit | 20 | 0.491 | 0.719 | 0.725 | 69.1 | 38.7 | 12453 | 21.5 | 274 |
| boundary-focused-holdout | 20 | 0.491 | 0.694 | 0.755 | 61.7 | 24.6 | 70774 | 40.8 | 4350 |
| source-partitioned-review | 20 | 0.491 | 0.733 | 0.730 | 73.3 | 38.5 | 55267 | 46.7 | 2441 |
| always-holdout | 20 | 0.491 | 0.753 | 0.706 | 79.5 | 51.1 | 162688 | 128.9 | 5037 |
| risk-triggered-audit | 20 | 0.491 | 0.733 | 0.713 | 73.3 | 45.5 | 83226 | 62.3 | 2771 |

## Per-Seed/Condition Rows

| seed | condition | policy | pre R | post R | recovered TP | introduced FP | tokens | trigger |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| seed04 | homogeneous | no-audit | 0.684 | 0.684 | 0 | 0 | 0 |  |
| seed04 | homogeneous | random-holdout | 0.684 | 0.704 | 6 | 14 | 7204 |  |
| seed04 | homogeneous | singleton-audit | 0.684 | 0.717 | 10 | 23 | 4423 |  |
| seed04 | homogeneous | boundary-focused-holdout | 0.684 | 0.704 | 6 | 9 | 70475 |  |
| seed04 | homogeneous | source-partitioned-review | 0.684 | 0.740 | 17 | 24 | 73861 |  |
| seed04 | homogeneous | always-holdout | 0.684 | 0.757 | 22 | 37 | 217355 |  |
| seed04 | homogeneous | risk-triggered-audit | 0.684 | 0.730 | 14 | 29 | 74898 | self_reported_completion_confidence+high_overlap_but_nontrivial_union_gap |
| seed04 | prompt-diverse | no-audit | 0.688 | 0.688 | 0 | 0 | 0 |  |
| seed04 | prompt-diverse | random-holdout | 0.688 | 0.711 | 7 | 13 | 8098 |  |
| seed04 | prompt-diverse | singleton-audit | 0.688 | 0.737 | 15 | 27 | 5194 |  |
| seed04 | prompt-diverse | boundary-focused-holdout | 0.688 | 0.711 | 7 | 11 | 70475 |  |
| seed04 | prompt-diverse | source-partitioned-review | 0.688 | 0.734 | 14 | 29 | 73861 |  |
| seed04 | prompt-diverse | always-holdout | 0.688 | 0.757 | 21 | 42 | 217355 |  |
| seed04 | prompt-diverse | risk-triggered-audit | 0.688 | 0.737 | 15 | 30 | 75669 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+high_overlap_but_nontrivial_union_gap |
| seed04 | source-partitioned | no-audit | 0.000 | 0.000 | 0 | 0 | 0 |  |
| seed04 | source-partitioned | random-holdout | 0.000 | 0.158 | 48 | 15 | 39882 |  |
| seed04 | source-partitioned | singleton-audit | 0.000 | 0.674 | 205 | 81 | 31681 |  |
| seed04 | source-partitioned | boundary-focused-holdout | 0.000 | 0.645 | 196 | 58 | 70475 |  |
| seed04 | source-partitioned | source-partitioned-review | 0.000 | 0.714 | 217 | 85 | 0 |  |
| seed04 | source-partitioned | always-holdout | 0.000 | 0.757 | 230 | 98 | 143494 |  |
| seed04 | source-partitioned | risk-triggered-audit | 0.000 | 0.711 | 216 | 91 | 102156 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+small_consensus_cardinality |
| seed04 | independent-context | no-audit | 0.628 | 0.628 | 0 | 0 | 0 |  |
| seed04 | independent-context | random-holdout | 0.628 | 0.655 | 8 | 8 | 9932 |  |
| seed04 | independent-context | singleton-audit | 0.628 | 0.727 | 30 | 24 | 7110 |  |
| seed04 | independent-context | boundary-focused-holdout | 0.628 | 0.681 | 16 | 14 | 70475 |  |
| seed04 | independent-context | source-partitioned-review | 0.628 | 0.724 | 29 | 32 | 73861 |  |
| seed04 | independent-context | always-holdout | 0.628 | 0.757 | 39 | 45 | 73861 |  |
| seed04 | independent-context | risk-triggered-audit | 0.628 | 0.734 | 32 | 32 | 77585 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct |
| seed05 | homogeneous | no-audit | 0.674 | 0.674 | 0 | 0 | 0 |  |
| seed05 | homogeneous | random-holdout | 0.674 | 0.697 | 7 | 13 | 8563 |  |
| seed05 | homogeneous | singleton-audit | 0.674 | 0.727 | 16 | 26 | 5684 |  |
| seed05 | homogeneous | boundary-focused-holdout | 0.674 | 0.707 | 10 | 13 | 70727 |  |
| seed05 | homogeneous | source-partitioned-review | 0.674 | 0.737 | 19 | 22 | 73798 |  |
| seed05 | homogeneous | always-holdout | 0.674 | 0.747 | 22 | 33 | 216584 |  |
| seed05 | homogeneous | risk-triggered-audit | 0.674 | 0.740 | 20 | 32 | 76411 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+high_overlap_but_nontrivial_union_gap |
| seed05 | prompt-diverse | no-audit | 0.645 | 0.645 | 0 | 0 | 0 |  |
| seed05 | prompt-diverse | random-holdout | 0.645 | 0.671 | 8 | 11 | 9022 |  |
| seed05 | prompt-diverse | singleton-audit | 0.645 | 0.717 | 22 | 24 | 6187 |  |
| seed05 | prompt-diverse | boundary-focused-holdout | 0.645 | 0.701 | 17 | 18 | 70727 |  |
| seed05 | prompt-diverse | source-partitioned-review | 0.645 | 0.734 | 27 | 30 | 73798 |  |
| seed05 | prompt-diverse | always-holdout | 0.645 | 0.747 | 31 | 44 | 216584 |  |
| seed05 | prompt-diverse | risk-triggered-audit | 0.645 | 0.727 | 25 | 31 | 76914 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+high_overlap_but_nontrivial_union_gap |
| seed05 | source-partitioned | no-audit | 0.000 | 0.000 | 0 | 0 | 0 |  |
| seed05 | source-partitioned | random-holdout | 0.000 | 0.171 | 52 | 18 | 41178 |  |
| seed05 | source-partitioned | singleton-audit | 0.000 | 0.717 | 218 | 77 | 32588 |  |
| seed05 | source-partitioned | boundary-focused-holdout | 0.000 | 0.664 | 202 | 67 | 70727 |  |
| seed05 | source-partitioned | source-partitioned-review | 0.000 | 0.724 | 220 | 79 | 0 |  |
| seed05 | source-partitioned | always-holdout | 0.000 | 0.747 | 227 | 95 | 142786 |  |
| seed05 | source-partitioned | risk-triggered-audit | 0.000 | 0.727 | 221 | 91 | 103315 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+small_consensus_cardinality |
| seed05 | independent-context | no-audit | 0.615 | 0.615 | 0 | 0 | 0 |  |
| seed05 | independent-context | random-holdout | 0.615 | 0.651 | 11 | 9 | 10625 |  |
| seed05 | independent-context | singleton-audit | 0.615 | 0.720 | 32 | 28 | 7689 |  |
| seed05 | independent-context | boundary-focused-holdout | 0.615 | 0.691 | 23 | 25 | 70727 |  |
| seed05 | independent-context | source-partitioned-review | 0.615 | 0.730 | 35 | 30 | 73798 |  |
| seed05 | independent-context | always-holdout | 0.615 | 0.747 | 40 | 43 | 73798 |  |
| seed05 | independent-context | risk-triggered-audit | 0.615 | 0.730 | 35 | 38 | 78416 | singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct |
| seed06 | homogeneous | no-audit | 0.671 | 0.671 | 0 | 0 | 0 |  |
| seed06 | homogeneous | random-holdout | 0.671 | 0.707 | 11 | 3 | 8272 |  |
| seed06 | homogeneous | singleton-audit | 0.671 | 0.730 | 18 | 21 | 5629 |  |
| seed06 | homogeneous | boundary-focused-holdout | 0.671 | 0.711 | 12 | 8 | 70511 |  |
| seed06 | homogeneous | source-partitioned-review | 0.671 | 0.743 | 22 | 26 | 73935 |  |
| seed06 | homogeneous | always-holdout | 0.671 | 0.763 | 28 | 34 | 217579 |  |
| seed06 | homogeneous | risk-triggered-audit | 0.671 | 0.730 | 18 | 24 | 76140 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+high_overlap_but_nontrivial_union_gap |
| seed06 | prompt-diverse | no-audit | 0.661 | 0.661 | 0 | 0 | 0 |  |
| seed06 | prompt-diverse | random-holdout | 0.661 | 0.664 | 1 | 16 | 9296 |  |
| seed06 | prompt-diverse | singleton-audit | 0.661 | 0.711 | 15 | 31 | 6611 |  |
| seed06 | prompt-diverse | boundary-focused-holdout | 0.661 | 0.694 | 10 | 5 | 70511 |  |
| seed06 | prompt-diverse | source-partitioned-review | 0.661 | 0.743 | 25 | 27 | 73935 |  |
| seed06 | prompt-diverse | always-holdout | 0.661 | 0.766 | 32 | 36 | 217579 |  |
| seed06 | prompt-diverse | risk-triggered-audit | 0.661 | 0.720 | 18 | 33 | 77122 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+high_overlap_but_nontrivial_union_gap |
| seed06 | source-partitioned | no-audit | 0.000 | 0.000 | 0 | 0 | 0 |  |
| seed06 | source-partitioned | random-holdout | 0.000 | 0.204 | 62 | 11 | 40817 |  |
| seed06 | source-partitioned | singleton-audit | 0.000 | 0.727 | 221 | 79 | 32291 |  |
| seed06 | source-partitioned | boundary-focused-holdout | 0.000 | 0.661 | 201 | 55 | 70511 |  |
| seed06 | source-partitioned | source-partitioned-review | 0.000 | 0.737 | 224 | 82 | 0 |  |
| seed06 | source-partitioned | always-holdout | 0.000 | 0.763 | 232 | 94 | 143644 |  |
| seed06 | source-partitioned | risk-triggered-audit | 0.000 | 0.743 | 226 | 91 | 102802 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+small_consensus_cardinality |
| seed06 | independent-context | no-audit | 0.635 | 0.635 | 0 | 0 | 0 |  |
| seed06 | independent-context | random-holdout | 0.635 | 0.671 | 11 | 8 | 10318 |  |
| seed06 | independent-context | singleton-audit | 0.635 | 0.750 | 35 | 27 | 7398 |  |
| seed06 | independent-context | boundary-focused-holdout | 0.635 | 0.697 | 19 | 15 | 70511 |  |
| seed06 | independent-context | source-partitioned-review | 0.635 | 0.743 | 33 | 30 | 73935 |  |
| seed06 | independent-context | always-holdout | 0.635 | 0.763 | 39 | 40 | 73935 |  |
| seed06 | independent-context | risk-triggered-audit | 0.635 | 0.750 | 35 | 33 | 77909 | singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct |
| seed07 | homogeneous | no-audit | 0.678 | 0.678 | 0 | 0 | 0 |  |
| seed07 | homogeneous | random-holdout | 0.678 | 0.707 | 9 | 9 | 7812 |  |
| seed07 | homogeneous | singleton-audit | 0.678 | 0.734 | 17 | 24 | 5044 |  |
| seed07 | homogeneous | boundary-focused-holdout | 0.678 | 0.714 | 11 | 7 | 71372 |  |
| seed07 | homogeneous | source-partitioned-review | 0.678 | 0.734 | 17 | 10 | 73423 |  |
| seed07 | homogeneous | always-holdout | 0.678 | 0.750 | 22 | 26 | 216142 |  |
| seed07 | homogeneous | risk-triggered-audit | 0.678 | 0.747 | 21 | 25 | 76416 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+high_overlap_but_nontrivial_union_gap |
| seed07 | prompt-diverse | no-audit | 0.638 | 0.638 | 0 | 0 | 0 |  |
| seed07 | prompt-diverse | random-holdout | 0.638 | 0.671 | 10 | 5 | 8726 |  |
| seed07 | prompt-diverse | singleton-audit | 0.638 | 0.707 | 21 | 25 | 5934 |  |
| seed07 | prompt-diverse | boundary-focused-holdout | 0.638 | 0.691 | 16 | 8 | 71372 |  |
| seed07 | prompt-diverse | source-partitioned-review | 0.638 | 0.724 | 26 | 16 | 73423 |  |
| seed07 | prompt-diverse | always-holdout | 0.638 | 0.750 | 34 | 33 | 216142 |  |
| seed07 | prompt-diverse | risk-triggered-audit | 0.638 | 0.730 | 28 | 26 | 77306 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+high_overlap_but_nontrivial_union_gap |
| seed07 | source-partitioned | no-audit | 0.000 | 0.000 | 0 | 0 | 0 |  |
| seed07 | source-partitioned | random-holdout | 0.000 | 0.184 | 56 | 10 | 37802 |  |
| seed07 | source-partitioned | singleton-audit | 0.000 | 0.688 | 209 | 63 | 29812 |  |
| seed07 | source-partitioned | boundary-focused-holdout | 0.000 | 0.671 | 204 | 57 | 71372 |  |
| seed07 | source-partitioned | source-partitioned-review | 0.000 | 0.711 | 216 | 64 | 0 |  |
| seed07 | source-partitioned | always-holdout | 0.000 | 0.750 | 228 | 85 | 142719 |  |
| seed07 | source-partitioned | risk-triggered-audit | 0.000 | 0.727 | 221 | 72 | 101184 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+small_consensus_cardinality |
| seed07 | independent-context | no-audit | 0.632 | 0.632 | 0 | 0 | 0 |  |
| seed07 | independent-context | random-holdout | 0.632 | 0.651 | 6 | 14 | 9271 |  |
| seed07 | independent-context | singleton-audit | 0.632 | 0.714 | 25 | 28 | 6448 |  |
| seed07 | independent-context | boundary-focused-holdout | 0.632 | 0.711 | 24 | 16 | 71372 |  |
| seed07 | independent-context | source-partitioned-review | 0.632 | 0.727 | 29 | 18 | 73423 |  |
| seed07 | independent-context | always-holdout | 0.632 | 0.750 | 36 | 35 | 73423 |  |
| seed07 | independent-context | risk-triggered-audit | 0.632 | 0.734 | 31 | 36 | 77820 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct |
| seed08 | homogeneous | no-audit | 0.681 | 0.681 | 0 | 0 | 0 |  |
| seed08 | homogeneous | random-holdout | 0.681 | 0.691 | 3 | 17 | 8075 |  |
| seed08 | homogeneous | singleton-audit | 0.681 | 0.730 | 15 | 29 | 5325 |  |
| seed08 | homogeneous | boundary-focused-holdout | 0.681 | 0.724 | 13 | 12 | 70783 |  |
| seed08 | homogeneous | source-partitioned-review | 0.681 | 0.743 | 19 | 27 | 73431 |  |
| seed08 | homogeneous | always-holdout | 0.681 | 0.750 | 21 | 37 | 216924 |  |
| seed08 | homogeneous | risk-triggered-audit | 0.681 | 0.737 | 17 | 34 | 76108 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+high_overlap_but_nontrivial_union_gap |
| seed08 | prompt-diverse | no-audit | 0.678 | 0.678 | 0 | 0 | 0 |  |
| seed08 | prompt-diverse | random-holdout | 0.678 | 0.691 | 4 | 11 | 7459 |  |
| seed08 | prompt-diverse | singleton-audit | 0.678 | 0.714 | 11 | 29 | 4838 |  |
| seed08 | prompt-diverse | boundary-focused-holdout | 0.678 | 0.717 | 12 | 12 | 70783 |  |
| seed08 | prompt-diverse | source-partitioned-review | 0.678 | 0.743 | 20 | 24 | 73431 |  |
| seed08 | prompt-diverse | always-holdout | 0.678 | 0.750 | 22 | 33 | 216924 |  |
| seed08 | prompt-diverse | risk-triggered-audit | 0.678 | 0.734 | 17 | 35 | 75621 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+high_overlap_but_nontrivial_union_gap |
| seed08 | source-partitioned | no-audit | 0.000 | 0.000 | 0 | 0 | 0 |  |
| seed08 | source-partitioned | random-holdout | 0.000 | 0.161 | 49 | 23 | 41377 |  |
| seed08 | source-partitioned | singleton-audit | 0.000 | 0.724 | 220 | 81 | 32465 |  |
| seed08 | source-partitioned | boundary-focused-holdout | 0.000 | 0.691 | 210 | 62 | 70783 |  |
| seed08 | source-partitioned | source-partitioned-review | 0.000 | 0.734 | 223 | 84 | 0 |  |
| seed08 | source-partitioned | always-holdout | 0.000 | 0.747 | 227 | 94 | 143493 |  |
| seed08 | source-partitioned | risk-triggered-audit | 0.000 | 0.747 | 227 | 90 | 103248 | self_reported_completion_confidence+singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct+small_consensus_cardinality |
| seed08 | independent-context | no-audit | 0.622 | 0.622 | 0 | 0 | 0 |  |
| seed08 | independent-context | random-holdout | 0.622 | 0.651 | 9 | 10 | 9406 |  |
| seed08 | independent-context | singleton-audit | 0.622 | 0.711 | 27 | 27 | 6706 |  |
| seed08 | independent-context | boundary-focused-holdout | 0.622 | 0.704 | 25 | 19 | 70783 |  |
| seed08 | independent-context | source-partitioned-review | 0.622 | 0.734 | 34 | 31 | 73431 |  |
| seed08 | independent-context | always-holdout | 0.622 | 0.747 | 38 | 38 | 73431 |  |
| seed08 | independent-context | risk-triggered-audit | 0.622 | 0.720 | 30 | 37 | 77489 | singleton_ratio_ge_0.12+consensus_union_gap_ge_12pct |
