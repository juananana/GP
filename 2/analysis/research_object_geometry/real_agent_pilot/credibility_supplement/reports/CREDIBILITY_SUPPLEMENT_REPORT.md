# Credibility Supplement Results

## Controller Decision Table

| task_group     | evaluation_set           |    n |   oracle_safe_n |   oracle_unsafe_n |   safe |   continue |   abstain |   false_certification_rate |   false_certification_n |   safe_coverage |   abstention_rate |   mean_repair_gain |   mean_cost |
|:---------------|:-------------------------|-----:|----------------:|------------------:|-------:|-----------:|----------:|---------------------------:|------------------------:|----------------:|------------------:|-------------------:|------------:|
| all tasks      | observed stop states     |    9 |               4 |                 5 |      4 |          5 |         0 |                          0 |                       0 |               1 |       0           |              0     |        0    |
| external repos | observed external states |    5 |               2 |                 3 |      2 |          3 |         0 |                          0 |                       0 |               1 |       0           |              0     |        0    |
| requests       | seeded repairs           | 1200 |               0 |              1200 |      0 |       1199 |         1 |                          0 |                       0 |             nan |       0.000833333 |            122.992 |     2854.58 |
| urllib3        | seeded repairs           | 1000 |               0 |              1000 |      0 |        998 |         2 |                          0 |                       0 |             nan |       0.002       |            204.987 |     4831.82 |
| external repos | seeded repairs           | 2200 |               0 |              2200 |      0 |       2197 |         3 |                          0 |                       0 |             nan |       0.00136364  |            160.262 |     3753.33 |
| requests       | seeded safe states       | 3000 |            3000 |                 0 |   3000 |          0 |         0 |                          0 |                       0 |               1 |       0           |              0     |     3252.53 |
| urllib3        | seeded safe states       | 3000 |            3000 |                 0 |   3000 |          0 |         0 |                          0 |                       0 |               1 |       0           |              0     |     3933.75 |
| external repos | seeded safe states       | 6000 |            6000 |                 0 |   6000 |          0 |         0 |                          0 |                       0 |               1 |       0           |              0     |     3593.14 |

## Source-Only vs Source-Route

| task             |   source_only_support |   source_route_support |   source_route_gini |   base_recall | source_only_would_be_eligible   | source_route_eligible   | false_certification_if_source_only_safe   |
|:-----------------|----------------------:|-----------------------:|--------------------:|--------------:|:--------------------------------|:------------------------|:------------------------------------------|
| policy_docset_v1 |                     1 |               0.25     |            0.770833 |      0.708333 | True                            | False                   | True                                      |
| code_repo_v1     |                     1 |               0.333333 |            0.75     |      0.3      | True                            | False                   | True                                      |
| requests         |                     1 |               0.25     |            0.888514 |      0.104027 | True                            | False                   | True                                      |
| urllib3          |                     1 |               0.2      |            0.91513  |      0.193133 | True                            | False                   | True                                      |

## Threshold Sensitivity Summary

| task     |   max_fcr |   mean_safe |   mean_abstain |
|:---------|----------:|------------:|---------------:|
| requests |         0 |           0 |    0.000833333 |
| urllib3  |         0 |           0 |    0.002       |

## Sensitivity Numeric Summary

| task     | sweep     | safe_rate_range   | continue_rate_range   | abstain_rate_range   |   max_fcr |   mean_repair_cost |
|:---------|:----------|:------------------|:----------------------|:---------------------|----------:|-------------------:|
| requests | threshold | 0.000-0.000       | 0.995-1.000           | 0.000-0.005          |         0 |            2854.58 |
| urllib3  | threshold | 0.000-0.000       | 0.990-1.000           | 0.000-0.010          |         0 |            4831.82 |
| requests | budget    | 0.000-0.000       | 0.635-1.000           | 0.000-0.365          |         0 |            3179.02 |
| urllib3  | budget    | 0.000-0.000       | 0.640-1.000           | 0.000-0.360          |         0 |            4323.46 |

## Budget Sensitivity Summary

| task     |   budget |   max_fcr |   mean_gain |   mean_cost |
|:---------|---------:|----------:|------------:|------------:|
| requests |        1 |         0 |     29.8358 |     729.437 |
| requests |        2 |         0 |     63.8683 |    1570.61  |
| requests |        3 |         0 |    104.837  |    2288.1   |
| requests |        4 |         0 |    122.657  |    2880.96  |
| requests |        5 |         0 |    138.448  |    3534.92  |
| requests |        6 |         0 |    151.572  |    4190.57  |
| requests |        7 |         0 |    159.208  |    4777.28  |
| requests |        8 |         0 |    168.085  |    5460.25  |
| urllib3  |        1 |         0 |     46.38   |     773.691 |
| urllib3  |        2 |         0 |     93.098  |    1768.75  |
| urllib3  |        3 |         0 |    116.293  |    2644.52  |
| urllib3  |        4 |         0 |    164.478  |    3726.71  |
| urllib3  |        5 |         0 |    204.704  |    4813.81  |
| urllib3  |        6 |         0 |    235.692  |    5896.08  |
| urllib3  |        7 |         0 |    275.208  |    6946.86  |
| urllib3  |        8 |         0 |    302.03   |    8017.3   |

## Chao/Singleton Scalar Proxy

| task             |   observed_items |   oracle_total |   recall |   singletons |   doubletons |   singleton_rate |   chao1_estimate | scalar_stop_proxy   | false_if_scalar_stop   | source_route_mismatch   |
|:-----------------|-----------------:|---------------:|---------:|-------------:|-------------:|-----------------:|-----------------:|:--------------------|:-----------------------|:------------------------|
| policy_docset_v1 |               17 |             24 | 0.708333 |           17 |            0 |                1 |              153 | False               | False                  | True                    |
| code_repo_v1     |                6 |             20 | 0.3      |            6 |            0 |                1 |               21 | False               | False                  | True                    |
| requests         |               31 |            298 | 0.104027 |           31 |            0 |                1 |              496 | False               | False                  | True                    |
| urllib3          |              135 |            699 | 0.193133 |          135 |            0 |                1 |             9180 | False               | False                  | True                    |

## Repair Policy CI

| task             | challenger         |   mean_new_true_items |   new_true_ci95_low |   new_true_ci95_high |   mean_novelty_per_cost |   novelty_per_cost_ci95_low |   novelty_per_cost_ci95_high | source               |
|:-----------------|:-------------------|----------------------:|--------------------:|---------------------:|------------------------:|----------------------------:|-----------------------------:|:---------------------|
| code_repo_v1     | high_potential     |                 5     |             5       |               5      |               0.0757576 |                   0.0757576 |                    0.0757576 | method_validation_v1 |
| code_repo_v1     | random             |                 4.315 |             4.09488 |               4.53   |               0.0653489 |                   0.0620114 |                    0.0686117 | method_validation_v1 |
| code_repo_v1     | residual_potential |                 9     |             9       |               9      |               0.136364  |                   0.136364  |                    0.136364  | method_validation_v1 |
| policy_docset_v1 | high_potential     |                 0     |             0       |               0      |               0         |                   0         |                    0         | method_validation_v1 |
| policy_docset_v1 | random             |                 2.025 |             1.825   |               2.235  |               0.0632812 |                   0.0570312 |                    0.0698437 | method_validation_v1 |
| policy_docset_v1 | residual_potential |                 4     |             4       |               4      |               0.125     |                   0.125     |                    0.125     | method_validation_v1 |
| requests         | high_potential     |               177     |           177       |             177      |               0.0542612 |                 nan         |                  nan         | external_requests    |
| requests         | random             |                45.535 |            41.3619  |              49.6404 |               0.0166784 |                 nan         |                  nan         | external_requests    |
| requests         | residual_potential |               177     |           177       |             177      |               0.0542612 |                 nan         |                  nan         | external_requests    |
| urllib3          | high_potential     |               275     |           275       |             275      |               0.0626995 |                   0.0626995 |                    0.0626995 | external_urllib3     |
| urllib3          | random             |                92.525 |            85.8298  |              99.3054 |               0.0218125 |                   0.0202613 |                    0.023292  | external_urllib3     |
| urllib3          | residual_potential |               329     |           329       |             329      |               0.0622046 |                   0.0622046 |                    0.0622046 | external_urllib3     |

## Oracle Appendix Summary

| repo     | snapshot_version   |   oracle_total | item_granularity                            | dedup_logic                                                  |   routes |   source_route_strata_with_items |
|:---------|:-------------------|---------------:|:--------------------------------------------|:-------------------------------------------------------------|---------:|---------------------------------:|
| requests | 2.32.5             |            298 | line-level source-route evidence occurrence | deduplicate by source_family, route, and line number item_id |        4 |                               18 |
| urllib3  | 2.5.0              |            699 | line-level source-route evidence occurrence | deduplicate by source_family, route, and line number item_id |        5 |                               24 |

## Oracle Route Pattern Examples

| repo     | route           |   oracle_items | pattern                                                                                    | pattern_category                   | examples                                                                                                    | dedup             |
|:---------|:----------------|---------------:|:-------------------------------------------------------------------------------------------|:-----------------------------------|:------------------------------------------------------------------------------------------------------------|:------------------|
| requests | tls_route       |            102 | \b(verify|cert|ssl|SSL|TLS|cert_verify|ca_bundle|DEFAULT_CA_BUNDLE_PATH)\b                 | TLS/certificate/verification terms | adapters:tls_route:103: # cert path                                                                         | source+route+line |
| requests | timeout_route   |             31 | \b(timeout|Timeout|connect timeout|read timeout)\b                                         | timeout/connect/read-timeout terms | adapters:timeout_route:120: self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None | source+route+line |
| requests | exception_route |            121 | \b(except|raise|RetryError|SSLError|ConnectionError|Timeout|TooManyRedirects)\b            | exception/raise/error terms        | adapters:exception_route:136: raise NotImplementedError                                                     | source+route+line |
| requests | compat_route    |             44 | \b(deprecated|compat|super_len|basestring|builtin_str|to_native_string|unicode_is_ascii)\b | compatibility/deprecation terms    | adapters:compat_route:32: from .compat import basestring, urlparse                                          | source+route+line |
| urllib3  | timeout_route   |            135 | \b(timeout|Timeout|connect_timeout|read_timeout|_connect_timeout|_read_timeout)\b          | timeout/connect/read-timeout terms | connection:timeout_route:137: timeout: _TYPE_TIMEOUT = _DEFAULT_TIMEOUT,                                    | source+route+line |
| urllib3  | retry_route     |            168 | \b(retry|Retry|retries|increment|backoff|status_forcelist)\b                               | retry/backoff/status terms         | connectionpool:retry_route:1011: retries,                                                                   | source+route+line |
| urllib3  | tls_route       |            111 | \b(ssl|SSL|TLS|cert|certificate|verify|assert_hostname|ca_certs|cert_reqs)\b               | TLS/certificate/verification terms | connection:tls_route:1005: cert,                                                                            | source+route+line |
| urllib3  | exception_route |            170 | \b(except|raise|Error|TimeoutError|SSLError|ProxyError|HTTPError|MaxRetryError)\b          | exception/raise/error terms        | connection:exception_route:1015: except BaseException:                                                      | source+route+line |
| urllib3  | cleanup_route   |            115 | \b(close|release_conn|drain_conn|shutdown|finally|with\s+|__exit__)\b                      | close/release/finally terms        | connection:cleanup_route:1016: ssl_sock.close()                                                             | source+route+line |

## Small Agent Workflow Validation

| task_id                      | condition               | agent_id   | independent_context   | fixed_prompt_recorded   |   evidence_events |   action_events |   source_route_strata | stop_proposal                     |
|:-----------------------------|:------------------------|:-----------|:----------------------|:------------------------|------------------:|----------------:|----------------------:|:----------------------------------|
| T_doc_dynamic_workflow_smoke | route_partitioned_smoke | A1         | True                  | True                    |                 9 |              11 |                     1 | local assigned-context completion |
| T_doc_dynamic_workflow_smoke | route_partitioned_smoke | A2         | True                  | True                    |                14 |              16 |                     1 | local assigned-context completion |
| T_doc_dynamic_workflow_smoke | route_partitioned_smoke | A3         | True                  | True                    |                12 |              12 |                     1 | local assigned-context completion |

## Workflow Pilot Summary

| task                         | model                     |   agents |   independent_contexts |   action_events |   evidence_events |   stop_proposals | controller_decision                   |
|:-----------------------------|:--------------------------|---------:|-----------------------:|----------------:|------------------:|-----------------:|:--------------------------------------|
| T_doc_dynamic_workflow_smoke | logged LLM-agent workflow |        3 |                      3 |              39 |                35 |                3 | not scored; workflow-shape validation |

## Seeded Safe-State Validation

| task     | condition         | order_budget_sweep    |   runs |   safe |   continue |   abstain |   false_certification_rate |   safe_coverage |   repair_gain |   mean_cost | cost_range   |
|:---------|:------------------|:----------------------|-------:|-------:|-----------:|----------:|---------------------------:|----------------:|--------------:|------------:|:-------------|
| requests | route_partitioned | 5 orders; budgets 1-8 |   3000 |   3000 |          0 |         0 |                          0 |               1 |             0 |     3252.53 | 157-7647     |
| urllib3  | extended_audit    | 5 orders; budgets 1-8 |   3000 |   3000 |          0 |         0 |                          0 |               1 |             0 |     3933.75 | 275-9072     |

## Oracle Sanity Check

| repo     | route           |   sample_n |   positive_n |   ambiguous_n |   sample_precision | notes                             |
|:---------|:----------------|-----------:|-------------:|--------------:|-------------------:|:----------------------------------|
| requests | compat_route    |          8 |            8 |             0 |              1     | line-level oracle-positive sample |
| requests | exception_route |          8 |            8 |             0 |              1     | line-level oracle-positive sample |
| requests | timeout_route   |          8 |            8 |             0 |              1     | line-level oracle-positive sample |
| requests | tls_route       |          8 |            8 |             0 |              1     | line-level oracle-positive sample |
| urllib3  | cleanup_route   |          8 |            7 |             1 |              0.875 | line-level oracle-positive sample |
| urllib3  | exception_route |          8 |            8 |             0 |              1     | line-level oracle-positive sample |
| urllib3  | retry_route     |          8 |            8 |             0 |              1     | line-level oracle-positive sample |
| urllib3  | timeout_route   |          8 |            8 |             0 |              1     | line-level oracle-positive sample |
| urllib3  | tls_route       |          8 |            8 |             0 |              1     | line-level oracle-positive sample |
