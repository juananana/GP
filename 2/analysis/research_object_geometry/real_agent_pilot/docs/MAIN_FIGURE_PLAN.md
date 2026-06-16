# Main Figure Plan

## Figure 1: Certificate Mismatch Mechanism

Panel A: workflow gathers evidence through repeated routes.

Panel B: no-new / agreement / self-completion is produced under localized source-route exposure.

Panel C: naive controller accepts global completion and causes false certification.

Panel D: evidence-condition controller rejects `SAFE`, repairs weak source-route conditions, and outputs `SAFE`, `CONTINUE`, or `ABSTAIN`.

Message:

```text
local evidence condition is not global completion proof.
```

## Figure 2: Source-Route Coverage Simplex

Show a simplex or low-dimensional schematic:

- localized homogeneous exposure near a small face;
- route-partitioned exposure spread across source-route support;
- extended audit near broad support.

Annotate:

```text
p_exp(t, s) = v_t(s) / sum_s v_t(s)
```

Message:

```text
source-route exposure describes where completion evidence came from.
```

## Figure 3: Cross-Task Result Table

Use the table from `cross_task_summary.csv`.

Columns:

- task;
- base support ratio;
- base exposure Gini;
- base recall;
- base false certification if stop accepted;
- controller decision;
- broad support ratio;
- broad recall;
- broad controller decision;
- residual repair gain;
- high-potential repair gain;
- cost-normalized evidence.

Highlight:

- all homogeneous stops are unsafe;
- broad exposure improves eligibility;
- `urllib3` route-partitioned remains `CONTINUE`, showing broad exposure is not sufficient.

## Figure 4: Method Boundary

Compare residual-potential and high-potential:

- `requests`: identical targets, identical gain;
- `urllib3`: partial overlap, residual-potential higher total gain, high-potential similar cost-normalized evidence.

Message:

```text
residual-potential is a repair instance, not a proven optimal method.
```

## Optional Figure 5: Future Claim Verification Audit

A schematic only, if included:

- claim;
- source-route audit lenses;
- support / contradiction / unresolved evidence;
- controller decision.

This should be presented as future work unless a real pilot is run.
