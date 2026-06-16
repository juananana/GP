# Oracle Appendix Data

## requests

- snapshot version: `2.32.5`

- oracle item granularity: line-level source-route evidence occurrence

- deduplication: item id combines source family, route, and line number

- positive sampling note: pattern positives are deterministic; manual validation should sample positives and nearby nonmatching lines before submission


### Route Counts


| oracle_bucket   |   oracle_items |
|:----------------|---------------:|
| compat_route    |             44 |
| exception_route |            121 |
| timeout_route   |             31 |
| tls_route       |            102 |


### Pattern Rules


| route           | pattern                                                                                    |
|:----------------|:-------------------------------------------------------------------------------------------|
| tls_route       | \b(verify|cert|ssl|SSL|TLS|cert_verify|ca_bundle|DEFAULT_CA_BUNDLE_PATH)\b                 |
| timeout_route   | \b(timeout|Timeout|connect timeout|read timeout)\b                                         |
| exception_route | \b(except|raise|RetryError|SSLError|ConnectionError|Timeout|TooManyRedirects)\b            |
| compat_route    | \b(deprecated|compat|super_len|basestring|builtin_str|to_native_string|unicode_is_ascii)\b |


### Examples


| oracle_bucket   | item_id                      | source_family   | line                                                                            |
|:----------------|:-----------------------------|:----------------|:--------------------------------------------------------------------------------|
| compat_route    | adapters:compat_route:32     | adapters        | from .compat import basestring, urlparse                                        |
| compat_route    | adapters:compat_route:320    | adapters        | if not isinstance(cert, basestring):                                            |
| exception_route | adapters:exception_route:136 | adapters        | raise NotImplementedError                                                       |
| exception_route | adapters:exception_route:140 | adapters        | raise NotImplementedError                                                       |
| timeout_route   | adapters:timeout_route:120   | adapters        | self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None |
| timeout_route   | adapters:timeout_route:126   | adapters        | :param timeout: (optional) How long to wait for the server to send              |
| tls_route       | adapters:tls_route:103       | adapters        | # cert path                                                                     |
| tls_route       | adapters:tls_route:120       | adapters        | self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None |



## urllib3

- snapshot version: `2.5.0`

- oracle item granularity: line-level source-route evidence occurrence

- deduplication: item id combines source family, route, and line number

- positive sampling note: pattern positives are deterministic; manual validation should sample positives and nearby nonmatching lines before submission


### Route Counts


| oracle_bucket   |   oracle_items |
|:----------------|---------------:|
| cleanup_route   |            115 |
| exception_route |            170 |
| retry_route     |            168 |
| timeout_route   |            135 |
| tls_route       |            111 |


### Pattern Rules


| route           | pattern                                                                           |
|:----------------|:----------------------------------------------------------------------------------|
| timeout_route   | \b(timeout|Timeout|connect_timeout|read_timeout|_connect_timeout|_read_timeout)\b |
| retry_route     | \b(retry|Retry|retries|increment|backoff|status_forcelist)\b                      |
| tls_route       | \b(ssl|SSL|TLS|cert|certificate|verify|assert_hostname|ca_certs|cert_reqs)\b      |
| exception_route | \b(except|raise|Error|TimeoutError|SSLError|ProxyError|HTTPError|MaxRetryError)\b |
| cleanup_route   | \b(close|release_conn|drain_conn|shutdown|finally|with\s+|__exit__)\b             |


### Examples


| oracle_bucket   | item_id                         | source_family   |   line_no | line                                                                           |
|:----------------|:--------------------------------|:----------------|----------:|:-------------------------------------------------------------------------------|
| cleanup_route   | connection:cleanup_route:1016   | connection      |      1016 | ssl_sock.close()                                                               |
| cleanup_route   | connection:cleanup_route:173    | connection      |       173 | However, the hostname with trailing dot is critical to DNS resolution; doing a |
| exception_route | connection:exception_route:1015 | connection      |      1015 | except BaseException:                                                          |
| exception_route | connection:exception_route:1017 | connection      |      1017 | raise                                                                          |
| retry_route     | connectionpool:retry_route:1011 | connectionpool  |      1011 | retries,                                                                       |
| retry_route     | connectionpool:retry_route:156  | connectionpool  |       156 | :param retries:                                                                |
| timeout_route   | connection:timeout_route:137    | connection      |       137 | timeout: _TYPE_TIMEOUT = _DEFAULT_TIMEOUT,                                     |
| timeout_route   | connection:timeout_route:149    | connection      |       149 | timeout=Timeout.resolve_default_timeout(timeout),                              |
| tls_route       | connection:tls_route:1005       | connection      |      1005 | cert,                                                                          |
| tls_route       | connection:tls_route:1006       | connection      |      1006 | assert_hostname or server_hostname,  # type: ignore[arg-type]                  |


