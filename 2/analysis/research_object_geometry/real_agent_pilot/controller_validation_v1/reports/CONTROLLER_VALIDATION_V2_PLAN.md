# Controller Validation v2 Plan

## Scope

Do not change the paper mainline and do not introduce new core variables. This validation only stress-tests the existing evidence-condition controller on the external `requests` task.

## Experiments

1. Challenger overlap: compare source-route strata selected by `high_potential` and `residual_potential`.
2. Threshold sweep: vary support-ratio and exposure-Gini thresholds while keeping the same SAFE / CONTINUE / ABSTAIN semantics.
3. Matched perturbation v2: hold discovered count or recall bands approximately fixed while changing source-route exposure.
4. Second external task preparation: choose a real repo audit or claim-verification completion task with offline oracle construction.

## Decision Rule

The controller avoids false certification only if it does not accept `SAFE` when bounded-oracle recall is below 0.90. Broad exposure is treated as completion eligibility, not sufficient completion proof.
