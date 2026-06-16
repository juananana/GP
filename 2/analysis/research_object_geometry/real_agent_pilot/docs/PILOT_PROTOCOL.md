# Real-Agent Pilot Protocol

Purpose: test the frozen hypothesis on real agent trajectories.

## Tasks

Use two bounded workload-unknown dynamic workflow tasks. At least one may be an
oracle-scored item-discovery subclass, but the protocol should evaluate
completion certification rather than only target recovery.

### Task A: Code Repository Completion Audit

Example target:

```text
Certify whether an API compatibility, deprecated-behavior, migration, or
exception-handling audit is complete in a small repository snapshot.
```

### Task B: Document/Policy Completion Audit

Example target:

```text
Certify whether rules, exceptions, obligations, or policy clauses have been
adequately covered in a bounded document set.
```

Agents must not see oracle counts or post-hoc coverage labels.

## Conditions

Run each task under:

| condition | description |
|---|---|
| homogeneous | agents receive similar broad prompts |
| prompt_diverse | agents receive different perspectives |
| route_partitioned | agents receive different source-route assignments |
| extended_audit | enough extra audit budget to create safe/near-safe states |

At a proposed stopping point, optionally run:

| challenger | description |
|---|---|
| random_challenger | samples random strata |
| low_exposure_challenger | repairs weakly exposed strata without potential weighting |
| low_discovery_challenger | targets bottom-k discovery strata |
| high_potential_challenger | targets high runtime-visible potential |
| residual_potential_challenger | repairs weak evidence conditions with runtime-visible potential |

## Logging

Write JSONL action events to:

```text
logs/action_events.jsonl
```

Write oracle labels after blind runs to:

```text
logs/oracle_items.jsonl
```

Never use oracle labels to form runtime features.

## Minimum Run Size

For a smoke pilot:

```text
2 tasks x 4 conditions x 3 seeds x 3 agents
```

For each task, include at least one extended/audited run that is safe or
near-safe. Without a safe comparison state, the geometry question cannot be
tested.

## Decision Rule

Keep the geometry line if:

- exposure Gini predicts false stopping better than no-new rounds and
  self-reported confidence;
- evidence-condition repair reduces unsupported completion certificates;
- support expansion and support gap reduction improve after repair;
- abstain decisions occur when evidence remains too narrow;
- the effect appears in both tasks.

Otherwise, fall back to simple source coverage plus evidence ledger.
