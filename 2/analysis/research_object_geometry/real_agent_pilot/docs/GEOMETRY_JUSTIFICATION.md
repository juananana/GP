# Geometry Justification

## Why Source-Route Geometry

The workflow does not only choose where to look. It also chooses how to look.

A source-only representation records:

```text
source
```

but the stopping evidence is conditioned on:

```text
source + route
```

For example, scanning `connectionpool.py` for timeout behavior does not certify that TLS, retry, exception, or cleanup behavior has been audited in the same file. The evidence condition is source-route, not source-only.

## Why Source-Only Is Too Coarse

Source-only geometry collapses routes inside a source. This creates false breadth: a workflow may appear to have covered many files while repeatedly applying the same audit lens.

Empirically, source-only granularity often collapses challenger distinctions. In the `requests` validation, source-only behavior allowed high-yield file selection to dominate, while the source-route view exposed that homogeneous stopping evidence lived in only a small subset of route conditions.

Source-only can still be a useful coarse control, but it should not be the paper's main geometry.

## Why Not Source-Route-Action as Main Geometry

Source-route-action adds action type, such as search, extract, summarize, or verify:

```text
(source, route, action)
```

This can be useful for robustness checks, but it is not the default geometry for this paper.

Reasons:

- it is more sensitive to logging conventions;
- it can fragment evidence conditions without improving interpretability;
- current experiments do not show a stable advantage over source-route;
- source-route already captures the main certificate condition: where and under which audit lens the evidence was produced.

Thus the default geometry is:

```text
source-route exposure distribution
```

with source-only as a coarse failure/control view and source-route-action as an over-refined robustness view.

## Geometric Interpretation

The exposure distribution:

```text
p_exp(t, s)
```

lies on a coverage simplex over source-route strata.

Localized exposure means the point lies near a low-dimensional face of the simplex. Broad exposure means the point occupies more of the relevant simplex support.

This is not geometry for decoration. It formalizes the condition under which completion evidence was produced.

## Main Empirical Role

Across current tasks:

- homogeneous route reuse produces low support ratio and high exposure Gini;
- accepting those stops would cause false certification;
- route-partitioning broadens evidence and often enables `SAFE`;
- `urllib3` shows the boundary: broad exposure gives eligibility, but `SAFE` still requires no residual evidence.

Therefore the geometry is a diagnostic for completion-certificate validity, not merely a way to find more items.
