# T2 Policy Docs Blind Task

You are auditing a fixed local document collection before retiring AcmePay v1.

Inspect only this task directory. Do not inspect oracle, result, or itemset files
outside the task directory.

Target: find every case in `docs/cases/` that is an AcmePay v1 migration point.

A case is a migration point only if all conditions hold:

1. The case state is `production_active` or `scheduled_replay`.
2. The flow is one of `charge`, `refund`, `fallback_queue`, or `replay`.
3. The case service resolves through `docs/registry/service_catalog.md` and
   `docs/registry/adapter_registry.md` to AcmePay v1.
4. Sandbox AcmePay entries, v2 topics, canary states, hold states, manual-only
   workflows, and wrong-flow cases are excluded.

Important: some cases do not mention AcmePay directly. You must follow aliases
in the adapter registry until they resolve.

For each item, output:

```json
{
  "source_id": "CASE-001",
  "item_id": "CASE-001",
  "evidence_span": "short exact evidence",
  "matched_conditions": ["state", "flow", "service_resolution"]
}
```
