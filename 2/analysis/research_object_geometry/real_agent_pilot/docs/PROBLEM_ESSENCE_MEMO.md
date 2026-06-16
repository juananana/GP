# Problem Essence Memo

## Research Scope

The research object is not ordinary QA and not only item discovery.

The object is:

```text
workload-unknown dynamic agent workflows
```

These workflows split, route, audit, or continue work dynamically under partial contexts and finite budgets. Examples include repository migration, claim verification, root-cause analysis, triage, deep research, ranking, and high-recall discovery.

Item discovery is only the most measurable experimental subclass because it gives a bounded oracle and recall-based false-stop labels.

## Core Problem

The core problem is not simply:

```text
agents fail to find all items
```

The deeper problem is:

```text
locally conditioned evidence is used as global completion evidence.
```

Runtime signals such as:

- no-new findings;
- agent agreement;
- self-reported completion;
- stable summaries;
- exhausted assigned subtasks;
- local verification success;

are valid only under the source-route conditions that produced them.

They have stopping authority only when those evidence conditions are broad enough to support the claimed task scope.

## Failure Law

```text
No-new stopping under localized source-route exposure certifies local exhaustion,
not global completion.
```

This is a certificate mismatch:

```text
evidence condition: local
completion claim: global
```

## Why Source-Route Exposure Matters

The source-route exposure distribution does not merely show "where agents searched less."

It describes the condition under which completion evidence was produced:

```text
p_exp(t, s) = v_t(s) / sum_s v_t(s)
```

where `s` is a source-route stratum and `v_t(s)` is runtime-visible search exposure.

If `p_exp` is localized, then no-new / agreement / self-completion are narrow evidence. If `p_exp` is broad over relevant strata, those signals have a stronger basis for global completion.

## Geometric Meaning

The coverage simplex is the geometry of completion-evidence conditions.

The point `p_exp(t)` tells us whether the workflow's evidence lives near a few local basins or covers the task space broadly enough to support a completion certificate.

This is why the geometry is natural rather than decorative.

## Method Implication

The method should not be framed as:

```text
find more missing items
```

It should be framed as:

```text
evidence-condition repair / coverage-certificate repair
```

When the workflow wants to stop under localized evidence, it must either:

1. reject the stop;
2. expand support in weak but relevant source-route conditions;
3. abstain if the evidence condition remains too narrow.

The residual-potential challenger is one operational repair rule:

```text
priority(s) = under_exposure(s) x runtime_computable_potential(s)
```

It targets strata where the current completion certificate is weak and runtime-visible signals suggest the stratum may still matter.

## Current Honesty Boundary

The mechanism and method are better aligned under the evidence-condition repair framing, but they are not fully proven to be uniquely aligned.

External validation shows that high-potential-only can tie residual-potential in a real codebase. Therefore:

- the diagnostic core is stronger than the current method claim;
- residual-potential should be presented as a derived repair candidate;
- the paper should not claim the product rule is universally optimal.

