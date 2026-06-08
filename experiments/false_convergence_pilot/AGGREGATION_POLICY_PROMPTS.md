# Aggregation Policy Prompts

Date: 2026-06-07

Use these prompts for Line A aggregation-policy experiments. Aggregators may
only inspect the provided G3 report packet. They must not inspect task files,
oracle files, holdout reports, previous reasoning traces, or score summaries.

## Standard Summarizer

You are aggregating final reports from three blind agents.

Produce one concise final answer containing the items that are sufficiently
supported by the reports. Prefer high precision. If an item is reported by only
one agent and the other reports do not corroborate it, include it only if the
packet itself gives enough evidence to treat it as reliable.

Return JSON with this shape:

```json
{
  "run_id": "<task>_SUM_standard_<seed>",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [],
  "uncertain_or_dropped_singletons": []
}
```

## Union-Preserving Summarizer

You are aggregating final reports from three blind agents.

Your goal is to preserve recall from the reports. Include every unique reported
item unless it is explicitly malformed, duplicated under another spelling, or
contradicted by the packet itself. Do not drop an item merely because only one
agent reported it. Mark singleton items separately so they can be audited later.

Return JSON with this shape:

```json
{
  "run_id": "<task>_SUM_union_preserving_<seed>",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [],
  "singleton_items_preserved": [],
  "malformed_or_contradicted_items_dropped": []
}
```

## Scoring Notes

- Score the returned `items` field against the same oracle as the source task.
- Report recall, precision, false-stop, and bucket recall.
- Compare against majority consensus, raw union, and holdout scout.
- The key effect size is `recall(raw_union) - recall(aggregation_output)`.
