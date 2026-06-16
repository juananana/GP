# Paper Skeleton v1

## Problem Formulation

The paper studies workload-unknown dynamic agent workflows that must decide whether a task is complete under partial, routed, and budgeted evidence.

The central failure is certificate mismatch:

```text
locally conditioned evidence is accepted as a global completion certificate.
```

Signals such as no-new findings, agreement, self-completion, or stable summaries are valid only under the source-route conditions that produced them.

## Evidence-Condition Geometry

Define source-route strata:

```text
s = (source, route)
```

and runtime exposure:

```text
p_exp(t, s) = v_t(s) / sum_s v_t(s)
```

This distribution describes the condition under which completion evidence was produced.

Source-route is the main geometry because source-only is too coarse and source-route-action is currently over-refined for the main claim.

## Controller Algorithm

At a stop proposal:

1. compute source-route support and exposure localization;
2. reject `SAFE` when evidence is too localized;
3. repair weak but runtime-plausible source-route conditions;
4. return `SAFE`, `CONTINUE`, or `ABSTAIN`.

`SAFE` requires broad evidence and no residual evidence from repair/audit.

## Repair Instance

Residual-potential:

```text
priority(s) = under_exposure(s) x runtime_computable_potential(s)
```

This is a mechanism-aligned repair candidate, not a proven optimal method.

## Experimental Protocol

Tasks:

- `policy_docset_v1`;
- `code_repo_v1`;
- `requests`;
- `urllib3`.

Conditions:

- homogeneous route reuse;
- route-partitioned audit;
- extended or near-complete audit.

Challengers:

- random;
- low-exposure;
- high-potential;
- residual-potential;
- free-search continuation.

Metrics:

- support ratio;
- exposure Gini;
- false certification;
- `SAFE` / `CONTINUE` / `ABSTAIN`;
- repair gain;
- cost-normalized evidence;
- overlap between high-potential and residual-potential.

## Main Results

1. Localized homogeneous evidence causes false certification across all four tasks.
2. Broad exposure improves completion eligibility.
3. `urllib3` shows broad exposure is not sufficient: route-partitioned evidence is geometry-eligible but still `CONTINUE`.
4. Residual-potential has positive repair evidence but no optimality proof.

## Limitations and Future Work

External oracles are pattern-defined rather than fully human annotated. Residual-potential is not proven optimal. A non-item-discovery claim verification audit remains future work unless separately piloted.
