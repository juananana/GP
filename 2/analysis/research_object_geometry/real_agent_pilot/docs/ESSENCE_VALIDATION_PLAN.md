# Essence Validation Plan

## Goal

Validate the deeper mechanism:

```text
false stopping is a certificate mismatch:
the workflow issues a global completion claim using evidence that is only locally conditioned.
```

This is deeper than only testing whether exposure Gini correlates with recall. The research object is workload-unknown dynamic agent workflows; bounded item discovery is used only when we need an oracle-scored subclass.

## Test 1: Conditional Evidence Perturbation

Hold the final discovered set nearly fixed, but vary the exposure condition.

Example:

- Run A finds items through narrow homogeneous routes.
- Run B finds similar number of items through broader source-route coverage.

Prediction:

```text
same discovered count + broader exposure => safer stopping evidence
same discovered count + localized exposure => higher residual risk
```

If this holds, the theory is about evidence conditions, not just recall.

## Test 2: No-New Signal Under Different Exposure Geometry

Create runs with identical no-new rounds but different exposure distributions.

Prediction:

```text
no-new under localized exposure remains unsafe;
no-new under broad source-route exposure is more reliable.
```

This directly tests the claim:

```text
no-new is conditional evidence.
```

## Test 3: Stop / Continue / Abstain Calibration

Instead of only measuring target recovery, evaluate whether the controller makes better completion decisions:

- SAFE when evidence condition is broad enough;
- CONTINUE when residual repair is promising;
- ABSTAIN when budget ends but evidence condition remains narrow.

Metrics:

- false certification rate;
- false-stop reduction;
- abstention rate;
- abstain precision: how often abstention corresponds to an unsupported certificate;
- safe coverage;
- risk-coverage curve.

## Test 4: Method Alignment

Compare intervention families by the evidence condition they repair:

- random: changes evidence condition accidentally;
- high-potential: searches likely-yield regions, but may ignore certificate gaps;
- low-exposure: repairs certificate gaps, but may be low yield;
- residual-potential: attempts to repair certificate gaps where yield is plausible.

Prediction:

```text
residual-potential should be most useful when high-potential regions are not already well covered.
high-potential may tie or beat it when potential dominates and under-exposure adds little information.
```

This explains the `requests` external validation result without hiding it.

Additional repair metrics:

- support expansion: new occupied source-route strata after repair;
- support gap reduction: fewer under-supported but runtime-plausible strata;
- certificate stability: whether no-new / agreement / self-completion remain after repair;
- novelty per cost and cumulative recall only for oracle-scored item-discovery subclasses.

## Test 5: Scope Beyond Item Discovery

Use one task that is not naturally framed as set enumeration:

- claim verification against a codebase;
- root-cause hypothesis audit;
- refactor completion check.

Still use a bounded oracle for evaluation, but define completion as:

```text
whether the workflow has enough evidence to safely certify the task outcome.
```

This checks whether the essence is genuinely about dynamic workflow stopping, not only set discovery.
