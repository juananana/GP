# Oracle Appendix Export

The external repository oracle is pattern-defined and line-level.  It is used
only after runtime states, controller decisions, and repair targets have been
fixed.  It should be described as a bounded completion-audit oracle, not as a
human-annotated universal truth set.

## Oracle construction summary

| repo     | snapshot_version   |   oracle_total | item_granularity                            | dedup_logic                                                  |   routes |   source_route_strata_with_items |
|:---------|:-------------------|---------------:|:--------------------------------------------|:-------------------------------------------------------------|---------:|---------------------------------:|
| requests | 2.32.5             |            298 | line-level source-route evidence occurrence | deduplicate by source_family, route, and line number item_id |        4 |                               18 |
| urllib3  | 2.5.0              |            699 | line-level source-route evidence occurrence | deduplicate by source_family, route, and line number item_id |        5 |                               24 |

## Route patterns and examples

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

## Positive-sample sanity check

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
