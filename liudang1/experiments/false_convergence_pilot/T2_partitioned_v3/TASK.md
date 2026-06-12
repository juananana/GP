# T2 Partitioned v3 Blind Task

You are auditing a fixed local document collection before retiring AcmePay v1.

Inspect only this task directory. Do not inspect oracle, result, or itemset files
outside the task directory.

Target: find every incident case that is an AcmePay v1 migration point.

Use the incident notes, payment service lineage changelog, adapter appendix,
lane policy memo, and late-cycle exception memo. The incident notes are written
as natural-language field notes, not as a neat table.

A case counts only if all conditions hold:

1. Its state is production-active or scheduled for replay.
2. Its traffic is charge, refund, fallback queue, or replay traffic.
3. Its service resolves through the changelog and adapter appendix to AcmePay v1
   or an AcmePay v1 queue topic.
4. The traffic fits the service lane, unless a cited override is marked
   migration_required in the exception memo.
5. Sandbox endpoints, v2 topics, manual workflows, hold/canary cases, and
   excluded overrides do not count.

Realistic audit budget:

- Prefer search and selective reading over exhaustive parsing.
- Do not write a full parser or scraper for every document.
- Stop when two consecutive search passes add no new valid cases and you can
  state a confidence estimate.
- If uncertain, report the uncertainty rather than silently expanding the task.

For each item, output:

```json
{
  "source_id": "CASE-001",
  "item_id": "CASE-001",
  "evidence_span": "short exact evidence",
  "matched_conditions": ["state", "flow", "service_resolution", "lane_or_override"]
}
```
