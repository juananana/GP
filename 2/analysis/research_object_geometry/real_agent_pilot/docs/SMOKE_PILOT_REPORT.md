# Smoke Pilot Report

**Task**: `T_doc_dynamic_workflow_smoke`  
**Condition**: `route_partitioned_smoke`

## What we ran

We merged three real trajectory reads into a single pilot log:

- `A1`: dynamic-workflow failure modes and workflow patterns from `2/推文.md`
- `A2`: geometric theory framing from `2/思路.md`
- `A3`: false-completion / coverage-geometry scan from `2/ChatGPT-研究准备与虚假收敛.md`

The pilot logged action events and discovered items, then computed exposure/discovery geometry at both agent level and run level.

## What the pilot shows

Agent-level geometry collapsed to one stratum per agent:

- `exposure_gini = 0.0`
- `discovery_gini = 0.0`

That means the per-agent view is too coarse for a geometric test. Each agent stayed inside one route family, so there is no within-agent simplex structure to measure.

Run-level geometry is more informative:

- `run_exposure_gini = 0.08547`
- `run_discovery_gini = 0.09804`
- `n_exposure_strata = 3`
- `n_discovery_strata = 3`

So the pipeline can already measure a nontrivial coverage simplex across agents/routes, but this smoke pilot is still far from a false-stopping validation.

## Best current reading

The stronger research object is still the **coverage/exposure simplex** story:

- false completion as local exhaustion under localized exposure
- geometry on `source-route` strata
- `coverage_gini` / exposure Gini as the simplest control variable
- low-exposure residual challenger as the method

`DICE-Lite` currently looks like a method label, not yet the core theory object.

## What this did not prove

This pilot does **not** yet show:

- that exposure Gini predicts false stopping better than discovery Gini
- that the challenger recovers missed items better than a baseline
- that the geometric variable is stable across tasks

## Next experiment

Need a blinded task with an oracle and at least two conditions:

1. homogeneous search
2. route-partitioned search

Then test whether:

- exposure localization rises before false stopping
- low-exposure challenger recovers the missing oracle items
- the effect survives across at least two tasks

