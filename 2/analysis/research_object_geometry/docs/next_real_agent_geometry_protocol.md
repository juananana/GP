# Next Real-Agent Geometry Diagnostic Protocol

This protocol follows the controlled simulation result. The current candidate
geometry variable is **coverage localization**, measured first by coverage Gini
or normalized coverage entropy over source-route strata.

The goal is not to prove a final method. The goal is to test whether the
simulation signal survives contact with real agent trajectories.

## 1. Hypothesis

Primary hypothesis:

> False stopping occurs when discovered evidence is localized in a small subset
> of source-route strata while observed novelty has already collapsed.

Operational prediction:

```text
higher coverage_gini
+ lower normalized coverage entropy
+ lower source-route coverage ratio
=> higher probability of false completion
```

Competing null:

```text
simple source coverage, no-new-item rounds, or self-reported confidence explain
the failure; geometry adds no useful signal.
```

## 2. Minimum Tasks

Use two bounded discovery tasks with oracle item sets:

1. Code repository discovery task.
   - Example: find all deprecated API / compatibility behavior / security-
     relevant call sites in a small repo snapshot.
2. Document or policy discovery task.
   - Example: find all rules, exceptions, or obligations across a bounded
     document set.

The tasks must have:

- a hidden oracle item set;
- enough source strata to make coverage meaningful;
- no visible total item count for agents;
- post-run oracle scoring only.

## 3. Conditions

Run each task under at least four conditions:

| condition | purpose |
|---|---|
| homogeneous | create correlated exploration baseline |
| prompt_diverse | test whether prompt diversity alone reduces localization |
| route_partitioned | force source-route coverage differences |
| extended_audited | create safe or near-safe comparison states |

Optional fifth condition:

| residual_challenger | test whether low-coverage strata still contain missing mass |

## 4. Required Logs

Write one JSONL event per agent action:

```json
{
  "task_id": "T_real_001",
  "repo_id": "repo_or_docset_name",
  "run_id": "seed01_homogeneous_agent01",
  "condition": "homogeneous",
  "agent_id": "agent01",
  "round_id": 3,
  "event_id": 17,
  "timestamp": "2026-06-12T00:00:00Z",
  "query_text": "search pattern or natural-language subgoal",
  "tool_name": "rg",
  "action_type": "search",
  "source_path": "src/module/file.py",
  "source_family": "src/module",
  "search_route": "api_surface_first",
  "discovered_item_id": "src/module/file.py:42",
  "new_item": true,
  "self_reported_completion": false,
  "self_reported_confidence": 0.6,
  "stop_reason": null,
  "token_or_cost": 120
}
```

Write oracle labels only after blind runs:

```json
{
  "task_id": "T_real_001",
  "discovered_item_id": "src/module/file.py:42",
  "oracle_label": true,
  "oracle_bucket": "api_compatibility",
  "reportable": true
}
```

## 5. Runtime Metrics

Compute without oracle:

- source-route coverage ratio;
- coverage Gini;
- normalized coverage entropy;
- pairwise route Jaccard;
- pairwise route cosine;
- normalized effective rank of `agent x source-route` matrix;
- log-det volume;
- no-new-item rounds;
- self-reported confidence;
- residual challenger novelty per cost.

Oracle-only labels:

- recall at theta 0.90, 0.95, 1.00;
- false completion;
- safe or near-safe completion;
- missing mass by stratum;
- challenger new true positives.

## 6. Analysis

For each task and condition:

1. Build `agent x source-route stratum` matrices from action logs.
2. Build `agent x discovered-item` incidence matrices.
3. Compare safe/near-safe states against false-completion states.
4. Screen geometry metrics against simple baselines:
   - source coverage count;
   - no-new-item rounds;
   - pairwise item Jaccard;
   - confidence.
5. Test within-task and cross-task stability.

Required evidence to keep the geometry line:

- coverage Gini or entropy separates false from safe states in both tasks;
- it beats source coverage and no-new-item rounds;
- residual challenger finds new true positives primarily in low-coverage/high-
  localization regions;
- the metric is computable before oracle scoring.

## 7. Decision Rule

Go:

```text
coverage_localization predicts false stopping across both tasks
and beats simple stopping baselines
```

Narrow Go:

```text
coverage localization works, but only as a source-coverage diagnostic;
do not use advanced geometry language
```

No-Go:

```text
simple source coverage or no-new-item rounds explain the outcome;
drop the geometry framing and write a safe-stopping/evidence-ledger paper
```

## 8. Current Best Research Claim If Confirmed

If the real-agent experiment confirms the simulation:

> False completion in dynamic multi-agent discovery is better explained by
> coverage localization than by agent agreement. A workflow can exhaust novelty
> inside a locally concentrated region while still leaving global source-route
> holes. Coverage localization gives a runtime-computable warning signal for
> unsafe stopping.

This is strong enough for a research object without claiming phase transition
or Grassmann geometry.
