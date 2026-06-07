# T1-Hard Blind Task: Indirect AcmePay v1 Migration Scan

You are auditing this repository before migrating away from AcmePay v1.

Find every migration point in `app/` and `scripts/` that still constructs, configures, invokes, queues, or routes traffic through the legacy AcmePay v1 integration.

Important: a line can be a migration point even when it does not literally contain `AcmePay`, `legacy`, or `v1`, if it sends traffic through a helper, registry, tenant route, region route, or queue mapping that resolves to AcmePay v1.

Report only real migration points in code, config, or scripts. Ignore tests, docs, comments, and explanatory notes.

For each item, output:

```json
{
  "file_path": "relative/path",
  "line": 12,
  "evidence": "short exact evidence",
  "reason": "why this is a legacy AcmePay v1 migration point"
}
```

