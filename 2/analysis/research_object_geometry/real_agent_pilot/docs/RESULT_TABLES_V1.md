# Result Tables v1

## Table 1: Cross-Task Diagnostic

| task | base support | base Gini | base recall | false cert if stop | controller | broad support | broad recall | broad controller |
|---|---:|---:|---:|---|---|---:|---:|---|
| policy_docset_v1 | 0.250 | 0.771 | 0.708 | True | CONTINUE | 0.750 | 1.000 | SAFE |
| code_repo_v1 | 0.333 | 0.750 | 0.300 | True | CONTINUE | 1.000 | 0.950 | SAFE |
| requests | 0.250 | 0.889 | 0.104 | True | CONTINUE | 1.000 | 1.000 | SAFE |
| urllib3 | 0.200 | 0.915 | 0.193 | True | CONTINUE | 0.800 | 0.835 | CONTINUE |

Takeaway:

```text
localized homogeneous evidence consistently creates false certification risk.
```

The `urllib3` row is essential: broad exposure is geometry-eligible but not sufficient for `SAFE`.

## Table 2: Repair Boundary

| task | residual gain | high-potential gain | random gain | residual per cost | high-potential per cost | high/residual overlap |
|---|---:|---:|---:|---:|---:|---:|
| policy_docset_v1 | 4.000 | 0.000 | 2.025 | 0.125 | 0.000 | n/a |
| code_repo_v1 | 9.000 | 5.000 | 4.315 | 0.136 | 0.076 | n/a |
| requests | 177.000 | 177.000 | 45.535 | 0.054 | 0.054 | 1.000 |
| urllib3 | 329.000 | 275.000 | 92.525 | 0.062 | 0.063 | 0.667 |

Takeaway:

```text
residual-potential is useful but not proven optimal.
```

The `requests` result prevents an overclaim because high-potential and residual-potential are identical there. The `urllib3` result is positive but still bounded because high-potential is cost-competitive.

## Table 3: Leakage Checklist

| component | runtime allowed | oracle forbidden |
|---|---|---|
| exposure distribution | visits, scans, source-route actions | oracle missing mass |
| support ratio / Gini | runtime exposure counts | post-hoc recall |
| potential | source text, route names, lexical matches, source length | undiscovered true item counts |
| controller decision | runtime evidence condition and repair outcome | scorer-visible target distribution |

Takeaway:

```text
oracle labels are used only after trajectories and challenger choices are fixed.
```
