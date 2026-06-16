# External Validation Task Plan

## Purpose

The next experiment should test external validity, not invent new variables or new methods.

Question:

```text
Does source-route exposure localization predict certificate mismatch outside generated bounded tasks?
```

Secondary question:

```text
Does residual-potential repair the completion evidence condition better than random, low-exposure, and high-potential-only challengers?
```

## Preferred Task

Use a real open-source repository with a bounded completion-certification target.

Candidate task type:

```text
Certify whether a bounded migration, compatibility audit, exception-handling audit,
or security-relevant review is complete in a small repo snapshot.
```

Why repo task is preferred:

- it differs from the generated policy document task;
- source-route strata are natural;
- oracle can be constructed by offline exhaustive search;
- action logs can be tied to files, routes, and tools.

## Backup Task

Use a real policy/manual/document set.

Candidate task type:

```text
Certify whether obligations, exceptions, deadlines, prohibitions, and escalation
conditions have been adequately covered in a bounded public manual or policy set.
```

This is easier to oracle-score but less distinct from `policy_docset_v1`.

## Required Conditions

Minimum:

- homogeneous
- route_partitioned
- homogeneous + random challenger
- homogeneous + low-exposure challenger
- homogeneous + high-potential challenger
- homogeneous + residual-potential challenger
- homogeneous + free-search continuation

## Default Geometry

Primary:

```text
source-route
```

Controls:

```text
source-only
source-route-action
```

Expected interpretation:

- source-only should be treated as a coarse failure/control geometry;
- source-route is the main geometry;
- source-route-action is an over-refined robustness check.

## Logging Requirements

For every runtime action:

```text
task_id
repo_id
condition
agent_id
round_id
event_id
action_type
tool_name
query_text
source_path
source_family
search_route
source_route_stratum
discovered_item_id
new_item
self_reported_completion
self_reported_confidence
stop_reason
token_or_cost
notes
```

## Oracle Rules

Oracle labels must be created offline and used only after blind trajectories are fixed.

Forbidden during challenger selection:

- oracle labels;
- oracle total count;
- missing true item count;
- missing mass by source or route;
- post-hoc recall.

## Required Metrics

Primary completion-certificate metrics:

- support expansion after repair;
- support gap reduction after repair;
- false-stop reduction;
- false certification rate;
- abstain rate and abstain precision;
- SAFE / CONTINUE / ABSTAIN calibration.

Secondary scored-subclass metrics:

- new true targets;
- novelty per cost;
- cumulative recall;
- residual-potential percentile under the random challenger distribution.

## Go / No-Go

Go:

- homogeneous has higher exposure localization and lower recall than route_partitioned;
- residual-potential improves certificate repair metrics over random and simple challengers under source-route geometry;
- source-only remains less informative or collapses distinctions.

Narrow Go:

- diagnostic replicates but residual-potential does not beat high-potential-only or random.
- Then keep exposure localization as the paper core and downgrade residual-potential to exploratory intervention.

No-Go:

- diagnostic fails on the external task;
- simple source coverage explains all results;
- residual-potential only wins because of oracle leakage or task-specific artifacts.
