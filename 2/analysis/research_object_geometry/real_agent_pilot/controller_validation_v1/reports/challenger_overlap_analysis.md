# Challenger Overlap Analysis

## Summary

At source-route granularity, `high_potential` and `residual_potential` are identical on 1.000 of seeds, with mean Jaccard 1.000.

This means their tie on the external `requests` task is mostly explained by selecting the same strata, not by independent routes to the same outcome.

## Top Runtime Scores

| stratum                   |   base_exposure |   runtime_potential |   under_exposure |   high_potential_rank_key |   residual_potential_score |
|:--------------------------|----------------:|--------------------:|-----------------:|--------------------------:|---------------------------:|
| adapters::tls_route       |               0 |                  64 |                1 |                       -64 |                         64 |
| models::exception_route   |               0 |                  42 |                1 |                       -42 |                         42 |
| adapters::exception_route |               0 |                  38 |                1 |                       -38 |                         38 |
| sessions::tls_route       |               0 |                  33 |                1 |                       -33 |                         33 |
| utils::exception_route    |               0 |                  30 |                1 |                       -30 |                         30 |
| models::compat_route      |               0 |                  20 |                1 |                       -20 |                         20 |
| sessions::exception_route |               0 |                   9 |                1 |                        -9 |                          9 |
| utils::compat_route       |               0 |                   8 |                1 |                        -8 |                          8 |

## Interpretation

The highest-potential strata are also unexposed or weakly exposed in the homogeneous base run. Therefore the `under_exposure` factor does not change the top-k ranking in this task. The method claim should remain downgraded: residual-potential is mechanism-aligned, but this task does not show extra benefit over high-potential-only.
