# Mechanism To Method Alignment V2

## Mechanism

False stopping is caused by a mismatch between:

```text
the scope of the evidence
```

and

```text
the scope of the completion claim.
```

No-new, agreement, and self-completion are not globally valid by default. They are conditioned on where and how the workflow searched.

## Variable

The source-route exposure distribution is the runtime description of that evidence condition:

```text
p_exp(t, s) = v_t(s) / sum_s v_t(s)
```

It answers:

```text
Under which source-route conditions was the completion evidence produced?
```

It is not merely a "low search count" feature.

## Diagnostic

Exposure localization measures whether the evidence condition is narrow.

```text
localized exposure => local evidence condition
broad source-route exposure => stronger basis for global completion
```

Thus the diagnostic is not:

```text
will another search find more items?
```

but:

```text
does the current evidence condition justify stopping?
```

## Method Principle

The intervention is:

```text
evidence-condition repair / coverage-certificate repair
```

The workflow should not directly stop when no-new evidence is produced under localized exposure.

Instead:

1. measure source-route exposure localization;
2. reject stopping if the evidence condition is too narrow;
3. repair weak evidence conditions with a challenger;
4. decide `SAFE`, `CONTINUE`, or `ABSTAIN`.

## Residual-Potential Challenger

The current repair candidate is:

```text
priority(s) = under_exposure(s) x runtime_computable_potential(s)
```

Interpretation:

- `under_exposure(s)` identifies where the completion certificate is weak;
- `runtime_computable_potential(s)` avoids wasting repair budget on visibly irrelevant regions.

The challenger is therefore not a generic missing-item finder. It is a targeted attempt to broaden or stress-test the completion evidence condition.

## Closed Loop

The paper logic should read as one chain:

```text
workload-unknown dynamic workflow
=> local progress signals
=> evidence condition represented by source-route exposure distribution
=> localization reveals certificate mismatch
=> repair weak evidence conditions or abstain
=> safer stopping decision
```

## Decision Outputs

- `SAFE`: source-route evidence condition is broad enough, and repair produces no meaningful residual signal.
- `CONTINUE`: repair finds new evidence or the evidence condition remains clearly insufficient.
- `ABSTAIN`: budget is exhausted, but the workflow still lacks a defensible completion certificate.

## Remaining Misalignment

There is still a caveat.

Residual-potential is mechanism-aligned, but not proven uniquely necessary. In the external `requests` validation, high-potential-only tied residual-potential at source-route granularity.

This means:

```text
the diagnostic mechanism is stronger than the current method optimality claim.
```

The correct paper stance is:

```text
exposure localization is the core diagnostic;
residual-potential is a plausible coverage-certificate repair rule;
we do not claim it is the only or universally best repair.
```

