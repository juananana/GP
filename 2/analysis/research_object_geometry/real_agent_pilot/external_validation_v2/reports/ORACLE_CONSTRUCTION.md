# Oracle Construction Note

## Task

Second external validation uses a real local snapshot of `urllib3` and evaluates a bounded completion audit over timeout, retry, TLS, exception, and resource-cleanup routes.

## Source-Route Strata

Sources:

- `connection.py`
- `connectionpool.py`
- `poolmanager.py`
- `response.py`
- `util/retry.py`
- `util/timeout.py`

Routes:

- `timeout_route`
- `retry_route`
- `tls_route`
- `exception_route`
- `cleanup_route`

The source-route simplex contains `30` strata.

## Leakage Control

Oracle rows are built offline from the frozen snapshot and are used only after base trajectories and challenger targets are fixed. Runtime potential uses only source text, route names, source length, and lexical route hits. It does not use oracle totals, missing mass, undiscovered true item counts, post-hoc recall, or scorer-visible target distributions.

This oracle is pattern-defined rather than human-annotated, so it is stronger than a generated toy task but weaker than a manual benchmark.
