# Paper Skeleton v0

## Problem Formulation

Study workload-unknown dynamic agent workflows that must decide whether a task is complete under partial, routed, and budgeted evidence. Item discovery is a scored subclass, not the full problem.

The failure mode is certificate mismatch: local progress evidence is used as a global completion certificate.

## Evidence-Condition Geometry

Define source-route strata `s` and runtime exposure distribution:

```text
p_exp(t, s) = v_t(s) / sum_s v_t(s)
```

This distribution describes the condition under which no-new, agreement, and self-completion evidence was produced.

## Controller Algorithm

1. Log source-route exposure during the workflow.
2. When a stop is proposed, compute support ratio and exposure localization.
3. If the evidence condition is too narrow, reject `SAFE`.
4. Run evidence-condition repair over weak but runtime-plausible strata.
5. Output `SAFE`, `CONTINUE`, or `ABSTAIN`.

`SAFE` requires broad evidence and no residual evidence from repair/audit.

## Experimental Protocol

Tasks:

- generated policy document set;
- generated code repo;
- external `requests` repo audit;
- external `urllib3` repo audit.

Controls:

- homogeneous route reuse;
- route-partitioned audit;
- extended or near-complete audit;
- random, low-exposure, high-potential, residual-potential, free-search continuation.

Leakage control: oracle labels are used only after trajectories and challenger choices are fixed.

## Result Table Skeleton

Columns:

- task;
- base support ratio;
- base exposure Gini;
- base recall;
- base false certification;
- controller decision;
- broad support ratio;
- broad recall;
- residual repair gain;
- high-potential repair gain;
- cost-normalized evidence;
- overlap between high-potential and residual-potential.

## Limitations

Current external oracles are pattern-defined, not human annotated. Residual-potential is not proven optimal. More non-item-discovery completion audits are needed.
