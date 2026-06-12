# Online Audit-Controller Status Report

This report is intentionally conservative. It separates the completed
Requests P0 online audit-controller loop from broader paper-level claims
that still require more repositories, independent oracle review, and public
benchmark validation.

## Current Claim Status

- Claim status: `requests_p0_method_effect_loop_completed_but_not_completion_certifying`.
- Requests P0 method-effect loop: completed when policy results are present.
- Completion certification: not achieved; all online policies remain below the 0.95 recall threshold.
- Paper-level general online audit-controller claim: not yet supported.

## Discovery Grid Status

| seed | homogeneous | prompt-diverse | source-partitioned | independent-context |
| --- | --- | --- | --- | --- |
| seed04 | completed_minimal_seed04 | completed_minimal_seed04 | completed_minimal_seed04 | completed |
| seed05 | completed | completed | completed | completed |
| seed06 | completed | completed | completed | completed |
| seed07 | completed | completed | completed | completed |
| seed08 | completed | completed | completed | completed |

## Online Audit Policy Status

Policy results: `E:\learn3\B\new\experiments\false_convergence_pilot\online_audit_controller\T5_requests_tls\audit_policy_eval\ONLINE_AUDIT_POLICY_RESULTS.csv`.

| policy | n | pre R | post R | precision | recovered TP | introduced FP | audit tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_audit | 20 | 0.491 | 0.491 | 0.829 | 0.0 | 0.0 | 0 |
| random_holdout | 20 | 0.491 | 0.554 | 0.755 | 18.9 | 11.9 | 16657 |
| singleton_audit | 20 | 0.491 | 0.719 | 0.725 | 69.1 | 38.7 | 12453 |
| boundary_focused_holdout | 20 | 0.491 | 0.694 | 0.755 | 61.7 | 24.6 | 70774 |
| source_partitioned_review | 20 | 0.491 | 0.733 | 0.730 | 73.3 | 38.5 | 55267 |
| always_holdout | 20 | 0.491 | 0.753 | 0.706 | 79.5 | 51.1 | 162688 |
| risk_triggered_audit | 20 | 0.491 | 0.733 | 0.713 | 73.3 | 45.5 | 83226 |

## Remaining Work Before Broader Paper-Level Claim

- Add independent oracle second-pass review before submission.
- Run at least one public benchmark subset or keep external benchmark claims out of the main paper.
- Add more real repositories before claiming repository-general audit-controller performance.
- Run second-model or cross-provider validation before claiming model-general behavior.
