# Method Validation v1 Conclusion

## Question

Does the frozen method candidate,

```text
residual-potential challenger = under-exposure x runtime-computable potential
```

stably outperform random continuation and simpler challenger rules on the existing blind tasks?

## Short Answer

Partly yes.

Residual-potential is stable and clearly better at the **source-route** and **source-route-action** granularities, but it collapses at **source-only** granularity because all methods effectively inspect all sources under the fixed budget.

So the result supports:

```text
source-route coverage geometry matters
```

It does not support:

```text
any coarse source coverage is enough
```

## Main Results

### Source-route granularity

| task | random mean | low-exposure | high-potential | residual-potential |
|---|---:|---:|---:|---:|
| policy_docset_v1 | 2.025 | 2.000 | 0.000 | 4.000 |
| code_repo_v1 | 4.315 | 6.000 | 5.000 | 9.000 |

### Source-route-action granularity

| task | random mean | low-exposure | high-potential | residual-potential |
|---|---:|---:|---:|---:|
| policy_docset_v1 | 2.025 | 2.000 | 0.000 | 4.000 |
| code_repo_v1 | 4.315 | 6.000 | 5.000 | 9.000 |

### Source-only granularity

All challenger rules tie:

| task | all methods |
|---|---:|
| policy_docset_v1 | 7.000 |
| code_repo_v1 | 13.000 |

This is not a win for residual-potential. It means source-only is too coarse for this validation design.

## Ablation Answer

The gain does not come from potential alone:

- policy: high-potential only gets 0, residual-potential gets 4
- code: high-potential only gets 5, residual-potential gets 9

The gain also does not come from under-exposure alone:

- policy: low-exposure gets 2, residual-potential gets 4
- code: low-exposure gets 6, residual-potential gets 9

So on these tasks, the combination is doing real work.

## Leakage Control

The potential score uses only runtime-visible source text and route match counts. It does not use:

- oracle labels
- oracle missing mass
- undiscovered true item counts
- post-hoc recall
- any scorer-visible target distribution

Oracle labels are used only after challenger selection for evaluation.

## Caveats

- The tasks are still generated bounded tasks, not external repos.
- Deterministic challengers have zero variance; the uncertainty mainly comes from random/free-search baselines.
- Residual-potential improves cumulative recall but does not always cross the 0.90 safe-stop threshold.
- Source-only robustness fails because the granularity is too coarse.

## Decision

Keep residual-potential as a serious **method candidate**, but only under the source-route coverage geometry.

Do not claim it is universally robust across all strata definitions.

The paper mainline should remain:

```text
exposure localization diagnostic first;
residual-potential challenger as a derived, validated intervention candidate second.
```
