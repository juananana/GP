# T1 Blind Task: AcmePay v1 Migration Scan

You are auditing this repository before migrating away from AcmePay v1.

Find every migration point in `app/` and `scripts/` that still constructs, configures, invokes, queues, or routes traffic through the legacy AcmePay v1 integration.

Report only real migration points in code, config, or scripts. Ignore tests, docs, comments, and explanatory notes.

Target examples include:

- AcmePay v1 endpoint paths or base URLs.
- Legacy AcmePay clients or factories.
- Calls through legacy AcmePay client instances.
- Legacy AcmePay environment variables.
- AcmePay v1 queue topics, webhook routes, or feature flags.

For each item, output:

```json
{
  "file_path": "relative/path",
  "line": 12,
  "evidence": "short exact evidence",
  "reason": "why this is a legacy AcmePay v1 migration point"
}
```

