# Challenger Overlap Analysis

## Summary

- identical target sets: 0.000
- mean Jaccard: 0.667

Unlike the frozen `requests` case, high-potential and residual-potential are not identical here. Residual-potential replaces one high-potential target with an under-exposed high-residual target.

## First Seeds

|   seed | high_potential_targets                                                                                                              | residual_potential_targets                                                                                                          |   overlap_count |   union_count |   jaccard | identical   |   high_new_true_items |   residual_new_true_items |
|-------:|:------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------|----------------:|--------------:|----------:|:------------|----------------------:|--------------------------:|
|      0 | connection::tls_route;connectionpool::exception_route;response::exception_route;util_retry::retry_route;util_timeout::timeout_route | connection::tls_route;connectionpool::exception_route;connectionpool::retry_route;response::exception_route;util_retry::retry_route |               4 |             6 |  0.666667 | False       |                   275 |                       329 |
|      1 | connection::tls_route;connectionpool::exception_route;response::exception_route;util_retry::retry_route;util_timeout::timeout_route | connection::tls_route;connectionpool::exception_route;connectionpool::retry_route;response::exception_route;util_retry::retry_route |               4 |             6 |  0.666667 | False       |                   275 |                       329 |
|      2 | connection::tls_route;connectionpool::exception_route;response::exception_route;util_retry::retry_route;util_timeout::timeout_route | connection::tls_route;connectionpool::exception_route;connectionpool::retry_route;response::exception_route;util_retry::retry_route |               4 |             6 |  0.666667 | False       |                   275 |                       329 |
|      3 | connection::tls_route;connectionpool::exception_route;response::exception_route;util_retry::retry_route;util_timeout::timeout_route | connection::tls_route;connectionpool::exception_route;connectionpool::retry_route;response::exception_route;util_retry::retry_route |               4 |             6 |  0.666667 | False       |                   275 |                       329 |
|      4 | connection::tls_route;connectionpool::exception_route;response::exception_route;util_retry::retry_route;util_timeout::timeout_route | connection::tls_route;connectionpool::exception_route;connectionpool::retry_route;response::exception_route;util_retry::retry_route |               4 |             6 |  0.666667 | False       |                   275 |                       329 |
|      5 | connection::tls_route;connectionpool::exception_route;response::exception_route;util_retry::retry_route;util_timeout::timeout_route | connection::tls_route;connectionpool::exception_route;connectionpool::retry_route;response::exception_route;util_retry::retry_route |               4 |             6 |  0.666667 | False       |                   275 |                       329 |
|      6 | connection::tls_route;connectionpool::exception_route;response::exception_route;util_retry::retry_route;util_timeout::timeout_route | connection::tls_route;connectionpool::exception_route;connectionpool::retry_route;response::exception_route;util_retry::retry_route |               4 |             6 |  0.666667 | False       |                   275 |                       329 |
|      7 | connection::tls_route;connectionpool::exception_route;response::exception_route;util_retry::retry_route;util_timeout::timeout_route | connection::tls_route;connectionpool::exception_route;connectionpool::retry_route;response::exception_route;util_retry::retry_route |               4 |             6 |  0.666667 | False       |                   275 |                       329 |
|      8 | connection::tls_route;connectionpool::exception_route;response::exception_route;util_retry::retry_route;util_timeout::timeout_route | connection::tls_route;connectionpool::exception_route;connectionpool::retry_route;response::exception_route;util_retry::retry_route |               4 |             6 |  0.666667 | False       |                   275 |                       329 |
|      9 | connection::tls_route;connectionpool::exception_route;response::exception_route;util_retry::retry_route;util_timeout::timeout_route | connection::tls_route;connectionpool::exception_route;connectionpool::retry_route;response::exception_route;util_retry::retry_route |               4 |             6 |  0.666667 | False       |                   275 |                       329 |

## Interpretation

The result is directionally favorable to residual-potential, because it finds more new scored evidence and repairs more support gap. However, the overlap remains high and residual-potential has higher average cost. This supports a cautious method claim only:

```text
residual-potential is a plausible evidence-condition repair rule;
under-exposure contributes in this repo, but optimality is not established.
```
