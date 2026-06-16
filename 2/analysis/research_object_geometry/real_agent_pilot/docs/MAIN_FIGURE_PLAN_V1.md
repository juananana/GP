# Main Figure Plan v1

## Figure 1: Certificate Mismatch

Goal: communicate the mechanism before introducing any algorithm.

Panels:

1. A dynamic workflow gathers evidence through repeated source-route conditions.
2. No-new / agreement / self-completion arises under localized exposure.
3. A naive stop controller converts local evidence into a global completion certificate.
4. The evidence-condition controller rejects `SAFE`, repairs weak strata, and returns `SAFE`, `CONTINUE`, or `ABSTAIN`.

Caption message:

```text
Completion evidence is conditioned on where and how the workflow searched.
```

## Figure 2: Source-Route Exposure Geometry

Goal: make the geometry concrete.

Show three points on a source-route coverage simplex:

- homogeneous: concentrated on a small face;
- route-partitioned: broader support;
- extended audit: broad support with no residual evidence.

Annotate:

```text
p_exp(t, s) = v_t(s) / sum_s v_t(s)
s = (source, route)
```

Add a side note:

```text
source-only collapses routes; source-route-action is a robustness view.
```

## Figure 3: Controller Decision Boundary

Goal: show why broad exposure is not enough.

Use the `urllib3` cases:

- homogeneous: localized, low recall, `CONTINUE`;
- route-partitioned: broad exposure, recall 0.835, `CONTINUE`;
- extended audit: broad exposure, no weak gap, recall 1.0, `SAFE`.

Caption message:

```text
broad exposure gives completion eligibility; SAFE requires no residual evidence.
```

## Figure 4: Cross-Task Diagnostic Table

Use the compact diagnostic table from `RESULT_TABLES_V1.md`.

Highlight:

- all homogeneous stops would be false certifications;
- route-partitioning improves eligibility;
- `urllib3` prevents the overclaim that broad exposure alone proves completion.

## Figure 5: Repair Boundary

Compare residual-potential and high-potential:

- `requests`: identical target sets and identical gain;
- `urllib3`: partial overlap, residual-potential higher total gain, high-potential similar cost-normalized evidence.

Caption message:

```text
residual-potential is a mechanism-aligned repair instance, not a proven optimum.
```
