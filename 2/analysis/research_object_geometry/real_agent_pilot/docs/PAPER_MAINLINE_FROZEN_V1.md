# Paper Mainline Frozen v1

## Status

This document freezes the current research mainline. Do not introduce new core variables or new method families before completing the next external validation task.

## Core Claim

In workload-unknown dynamic agent workflows, false stopping is not only an aggregation failure. A workflow can stop because locally conditioned progress evidence is treated as a global completion certificate.

Item discovery is a measurable experimental subclass, not the full research object.

## Failure Law

```text
No-new stopping under source-route exposure localization certifies local exhaustion, not global completion.
```

Meaning:

- If agents repeatedly operate under the same source-route conditions, then no-new / agreement / self-completion evidence is only locally conditioned.
- It does not certify that the claimed workload has been globally completed.
- High confidence, agreement, or no-new rounds are unsafe when the evidence condition remains localized.

## Geometric Object

The runtime object is the exposure distribution on the source-route coverage simplex:

```text
p_exp(t, s) = v_t(s) / sum_s v_t(s)
```

where:

- `s` is a source-route stratum;
- `v_t(s)` is the number of runtime-visible visits, scans, tool calls, or search actions in stratum `s`.

This is the natural geometry because it records the source-route conditions under which completion evidence was produced.

## Diagnostic

The diagnostic is:

```text
exposure localization on the source-route coverage simplex
```

In current experiments this is operationalized with exposure Gini and source-route coverage ratio.

The diagnostic role is:

```text
high localization => unsafe stopping risk
lower localization => stronger evidence condition for a global completion claim
```

## Intervention Candidate

The frozen method candidate is:

```text
residual-potential challenger = under-exposure x runtime-computable potential
```

The intervention is triggered only when the workflow wants to stop under high exposure localization.

It is a coverage-certificate repair rule. It targets strata where:

- the current completion evidence is thin at runtime;
- runtime-visible signals still make the stratum worth stress-testing.

The method is not framed as finding more targets. It is framed as repairing the evidence condition before accepting or rejecting a completion claim.

## Potential Definition and Leakage Control

Potential must use only runtime-visible information, such as:

- route match counts;
- source length or file/document size;
- route-source relevance visible before oracle scoring;
- discovered-neighbor rates that do not depend on oracle labels.

Potential must not use:

- oracle labels;
- oracle missing mass;
- undiscovered true item counts;
- post-hoc recall;
- any scorer-visible target distribution.

Oracle information is allowed only after challenger selection, for evaluation.

## Boundary Condition

Current validation supports the method under:

```text
source-route geometry
source-route-action geometry
```

Current validation does not support the method under:

```text
source-only geometry
```

Interpretation:

- `source-only` is too coarse and collapses the geometry.
- `source-route-action` works but does not yet show clear extra benefit over source-route in the current tasks.
- `source-route` is the current default because it balances interpretability, runtime computability, and empirical effectiveness.

## Current Evidence

Two bounded blind tasks support the diagnostic pattern:

| task | homogeneous exposure Gini | route-partitioned exposure Gini | homogeneous recall | route-partitioned recall |
|---|---:|---:|---:|---:|
| policy_docset_v1 | 0.7708 | 0.3854 | 0.7083 | 1.0000 |
| code_repo_v1 | 0.7500 | 0.1995 | 0.3000 | 0.9500 |

Method Validation v1 supports residual-potential at source-route granularity:

| task | random mean | low-exposure | high-potential | residual-potential |
|---|---:|---:|---:|---:|
| policy_docset_v1 | 2.025 | 2.000 | 0.000 | 4.000 |
| code_repo_v1 | 4.315 | 6.000 | 5.000 | 9.000 |

The source-only granularity is a failure control: all challenger rules tie there.

External validation on a real `requests` repository snapshot supports the diagnostic but weakens the method optimality claim: source-route exposure localization separates unsafe from safer stopping, while high-potential-only ties residual-potential in that setting.

## Why Source-Route Geometry

The paper should explicitly answer this question.

Source-only is too coarse:

- it cannot distinguish how a source was searched;
- it lets all challenger rules collapse into the same behavior;
- it does not expose local route exhaustion.

Source-route-action may be useful:

- it is more detailed;
- but current tasks do not show consistent extra benefit over source-route.

Source-route is the default:

- it captures both where agents searched and how they searched;
- it is cheap to log at runtime;
- it describes the condition under which completion evidence was produced;
- it is the current best tradeoff between interpretability and empirical signal.

## Evaluation Metrics

The experiment should not be scored only by added true items. The primary evaluation is whether the workflow makes better completion decisions.

Required metrics:

- support expansion: increase in occupied source-route support after repair;
- support gap reduction: reduction of weakly supported but runtime-plausible strata;
- false-stop reduction: fewer unsafe stop decisions under bounded oracle evaluation;
- abstain decision quality: whether the system refuses certification when evidence remains too narrow;
- novelty per cost and cumulative recall for item-discovery subclasses only.

## What Not To Claim Yet

Do not claim:

- a phase transition has been proven;
- residual-potential is universally optimal;
- the method works under arbitrary coverage granularity;
- source-only coverage is enough;
- item discovery is the full problem class;
- current generated blind tasks are sufficient for final paper evidence.

## Next Required Step

Run one more external validation task:

```text
real open-source repo bounded discovery
or
real policy/manual document set bounded discovery
```

Purpose:

```text
test whether the evidence-condition law and residual-potential repair survive outside generated tasks
```

This is not for metric chasing. It is for external validity.

## Current Decision

The project can move from:

```text
exploratory direction
```

to:

```text
paper core prototype
```

but only with this ordering:

```text
1. exposure localization diagnostic
2. source-route geometry boundary
3. residual-potential challenger as derived intervention
4. external validation before stronger claims
```
