# Click Held-Out Staged Controller Results

The staged controller was frozen from Requests TLS before evaluating Click.

## Policy Means

| policy | n | pre R | post R | precision | recovered TP | introduced FP | audit tok | e2e tok | FCR | safe cov | abstain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no-audit | 9 | 0.465 | 0.465 | 0.769 | 0.0 | 0.0 | 0 | 166302 | 0.000 | 0.000 | 1.000 |
| singleton-audit | 9 | 0.465 | 0.722 | 0.630 | 38.2 | 29.6 | 9134 | 175436 | 0.000 | 0.000 | 1.000 |
| source-partitioned-review | 9 | 0.465 | 0.755 | 0.577 | 43.2 | 44.8 | 56567 | 222869 | 0.000 | 0.000 | 1.000 |
| staged-controller | 9 | 0.465 | 0.761 | 0.555 | 44.0 | 54.1 | 56291 | 222594 | 0.000 | 0.000 | 1.000 |
| always-holdout | 9 | 0.465 | 0.768 | 0.492 | 45.1 | 80.3 | 176575 | 342877 | 0.000 | 0.000 | 1.000 |

## Frozen Controller

```json
{
  "name": "staged_singleton_then_source_partitioned_v1",
  "frozen_from": "Requests TLS development online audit results",
  "stage_order": [
    "conservative_consensus",
    "singleton_verifier",
    "source_partitioned_review_if_escalation_condition_holds",
    "abstain_unless_certification_conditions_hold"
  ],
  "escalate_to_source_review_if_any": {
    "singleton_ratio_ge": 0.1,
    "consensus_to_union_le": 0.92,
    "missing_required_source_family": true
  },
  "certify_safe_if_all": {
    "no_source_escalation_triggered": true,
    "declared_oracle_size_visible_in_task": 149,
    "final_item_count_ge_theta_times_declared_oracle_size": 142,
    "all_required_source_families_present": true,
    "mean_confidence_ge": 0.75,
    "all_discovery_agents_report_completion": true,
    "singleton_verifier_executed_when_queue_nonempty": true
  }
}
```
