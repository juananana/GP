# Staged Controller Bootstrap and Paired Tests

Inputs: Requests, Click, itsdangerous.
Bootstrap: 5000 resamples over dataset/seed clusters.

Requests rows are included in policy summaries but excluded from staged paired tests because that development run did not contain a frozen staged-controller arm.

## Policy Means with Seed-Clustered 95% CI

| dataset | policy | n | recall mean [95% CI] | precision mean [95% CI] | F1 mean [95% CI] | audit tokens | recovered TP | introduced FP | FCR among certified | safe coverage | abstention |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Requests | no_audit | 20 | 0.491 [0.487, 0.496] | 0.829 [0.826, 0.832] | 0.531 [0.529, 0.534] | 0 | 0.0 | 0.0 | NA | 0.000 | NA |
| Requests | singleton_audit | 20 | 0.719 [0.713, 0.725] | 0.725 [0.719, 0.732] | 0.722 [0.719, 0.725] | 12453 | 69.1 | 38.7 | NA | 0.000 | NA |
| Requests | source_partitioned_review | 20 | 0.733 [0.727, 0.738] | 0.730 [0.720, 0.746] | 0.731 [0.726, 0.737] | 55267 | 73.3 | 38.5 | NA | 0.000 | NA |
| Requests | always_holdout | 20 | 0.753 [0.748, 0.759] | 0.706 [0.700, 0.715] | 0.729 [0.724, 0.733] | 162688 | 79.5 | 51.1 | NA | 0.000 | NA |
| Click | no_audit | 9 | 0.465 [0.443, 0.485] | 0.769 [0.753, 0.783] | 0.447 [0.441, 0.458] | 0 | 0.0 | 0.0 | NA | 0.000 | 1.000 |
| Click | singleton_audit | 9 | 0.722 [0.694, 0.747] | 0.630 [0.577, 0.668] | 0.665 [0.650, 0.679] | 9134 | 38.2 | 29.6 | NA | 0.000 | 1.000 |
| Click | source_partitioned_review | 9 | 0.755 [0.738, 0.767] | 0.577 [0.548, 0.600] | 0.653 [0.636, 0.663] | 56567 | 43.2 | 44.8 | NA | 0.000 | 1.000 |
| Click | staged_controller | 9 | 0.761 [0.740, 0.772] | 0.555 [0.513, 0.583] | 0.640 [0.614, 0.655] | 56291 | 44.0 | 54.1 | NA | 0.000 | 1.000 |
| Click | always_holdout | 9 | 0.768 [0.752, 0.779] | 0.492 [0.458, 0.511] | 0.600 [0.577, 0.615] | 176575 | 45.1 | 80.3 | NA | 0.000 | 1.000 |
| itsdangerous | no_audit | 9 | 0.569 [0.565, 0.573] | 0.841 [0.825, 0.857] | 0.536 [0.529, 0.542] | 0 | 0.0 | 0.0 | NA | 0.000 | 1.000 |
| itsdangerous | singleton_audit | 9 | 0.867 [0.867, 0.869] | 0.719 [0.710, 0.726] | 0.785 [0.779, 0.789] | 8909 | 47.8 | 26.1 | NA | 0.000 | 1.000 |
| itsdangerous | source_partitioned_review | 9 | 0.871 [0.860, 0.881] | 0.733 [0.725, 0.737] | 0.796 [0.794, 0.799] | 11495 | 48.3 | 22.1 | NA | 0.000 | 1.000 |
| itsdangerous | staged_controller | 9 | 0.879 [0.869, 0.888] | 0.709 [0.700, 0.718] | 0.784 [0.782, 0.785] | 18507 | 49.7 | 29.6 | 1.000 | 0.000 | 0.889 |
| itsdangerous | always_holdout | 9 | 0.890 [0.887, 0.894] | 0.675 [0.665, 0.684] | 0.768 [0.760, 0.773] | 41218 | 51.4 | 39.9 | NA | 0.000 | 1.000 |

## Paired Staged-Controller Comparisons

| comparator | pairs | datasets | recall diff [95% CI] | precision diff [95% CI] | F1 diff [95% CI] | audit-token diff [95% CI] | sign-flip p, recall |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| singleton_audit | 18 | Click,itsdangerous | 0.025 [0.012, 0.039] | -0.042 [-0.067, -0.019] | -0.013 [-0.025, -0.002] | 28378 [12375, 47147] | 0.000 |
| source_partitioned_review | 18 | Click,itsdangerous | 0.007 [0.005, 0.009] | -0.023 [-0.029, -0.017] | -0.012 [-0.017, -0.009] | 3368 [-6422, 9405] | 0.002 |
| always_holdout | 18 | Click,itsdangerous | -0.009 [-0.013, -0.005] | 0.048 [0.034, 0.063] | 0.029 [0.018, 0.039] | -71497 [-110745, -36567] | 0.004 |

Interpretation: the paired tests are descriptive at this size. They test whether the frozen staged controller improves recall over the corresponding baseline under seed-clustered resampling; they do not justify retuning the controller on these data.
