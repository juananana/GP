# T3 Partitioned Policy Docs Blind Task

You are auditing a fixed local document collection before retiring AcmePay v1.

Inspect only this task directory. Do not inspect oracle, result, or itemset files
outside the task directory.

Target: find every case in `docs/cases/` that is an AcmePay v1 migration point.

A case is a migration point only if all conditions hold:

1. The state is `production_active` or `scheduled_replay`.
2. The flow is one of `charge`, `refund`, `fallback_queue`, or `replay`.
3. The service resolves through `docs/catalog/service_catalog.md` and
   `docs/registry/adapter_registry.md` to AcmePay v1.
4. The case satisfies `docs/policies/lane_policy.md`, unless its
   `override_id` is listed as `disposition=migration_required` in
   `docs/policies/exception_overrides.md`.
5. Overrides listed as `disposition=excluded`, sandbox services, v2 topics,
   manual workflows, hold states, and canary states are excluded.

Important: some true cases look like lane mismatches. Some false cases look
almost identical but have excluded overrides. You must verify the override
disposition rather than relying on service or flow names.

For each item, output:

```json
{
  "source_id": "CASE-001",
  "item_id": "CASE-001",
  "evidence_span": "short exact evidence",
  "matched_conditions": ["state", "flow", "service_resolution", "lane_or_override"]
}
```
