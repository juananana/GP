# Mechanism-to-Method Alignment v1

## Core Mechanism

False stopping is a certificate mismatch:

```text
the workflow issues a global completion claim
using evidence that is only valid under a local exposure condition.
```

The key question is not:

```text
Did we find more items?
```

The key question is:

```text
Is the evidence condition broad enough to support the claimed completion scope?
```

## Role of the Geometric Object

The source-route exposure distribution is the runtime description of the evidence condition:

```text
p_exp(t, s) = v_t(s) / sum_s v_t(s)
```

It tells us where the no-new, agreement, verification, and self-completion signals are actually conditioned.

If `p_exp` is localized, then the workflow's completion evidence is local.

If the workflow still makes a global completion claim, the claim is under-supported.

## Why This Variable Can Lead To A Solution

The variable does not solve the task by itself. It changes the stopping problem from:

```text
Do agents feel done?
```

to:

```text
Does the observed evidence condition match the scope of the completion claim?
```

This enables three aligned actions:

1. **Reject invalid stopping**

   If exposure is too localized, no-new evidence is not accepted as global completion evidence.

2. **Repair the evidence condition**

   Allocate additional search to source-route regions that are under-supported but runtime-plausible.

3. **Certify or abstain**

   After repair, either accept stopping if residual evidence collapses, or abstain if the evidence condition remains too narrow.

## Method Principle

The method should be framed as:

```text
evidence-condition repair for safe stopping
```

not as:

```text
a heuristic that finds more missing items
```

Residual-potential challenger is the first operational rule:

```text
priority(s) = under_exposure(s) x runtime_potential(s)
```

where:

- `under_exposure(s)` measures whether the current evidence condition neglects stratum `s`;
- `runtime_potential(s)` measures whether stratum `s` is plausibly relevant using only runtime-visible information.

This is aligned with the mechanism because it does not merely chase high-yield areas. It tries to repair the regions where the completion certificate is weakest.

## Complete Paper Logic

### 1. Engineering anomaly

Dynamic multi-agent workflows can stop with high confidence, high agreement, or no-new rounds while the task is still incomplete.

### 2. Mechanism

Progress signals are conditional on the workflow's exposure distribution. False stopping occurs when locally conditioned evidence is used as a global completion certificate.

### 3. Geometry

The exposure condition is naturally represented as a point on the source-route coverage simplex.

### 4. Diagnostic

Exposure localization measures how narrow the evidence condition is. High localization means no-new evidence certifies local exhaustion, not global completion.

### 5. Intervention

When stopping is requested under localized exposure, the workflow does not stop. It repairs the evidence condition using residual-potential search.

### 6. Decision

The workflow outputs:

- `SAFE`: evidence condition is broad enough and residual challenger finds no meaningful novelty;
- `CONTINUE`: challenger finds new evidence or residual risk remains high;
- `ABSTAIN`: budget is exhausted but evidence condition still cannot support global completion.

## Important Boundary

The current method is not claimed to be universally optimal.

External validation shows that in some real-code settings, `high-potential` can tie residual-potential. This means:

```text
potential may dominate when high-yield regions are already the main missing mass.
```

The honest claim is:

```text
exposure geometry provides the certificate diagnostic;
residual-potential is a mechanism-aligned repair rule, not the only possible repair.
```

## Jiaxin-Style Analogy

Jiaxin's structure:

```text
r/d
=> subspace overlap geometry
=> merging safety zones
=> selective projection
```

Our structure:

```text
p_exp over source-route simplex
=> evidence-condition localization
=> unsafe stopping zones
=> evidence-condition repair / abstain
```

The method is not an add-on. It is the action required when the diagnostic says the current completion certificate is invalid.

