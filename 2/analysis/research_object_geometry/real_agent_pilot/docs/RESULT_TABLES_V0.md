# Result Tables v0

## Table 1: Cross-Task Diagnostic and Controller

Source: `results/cross_task_summary.csv`.

| task | base support | base Gini | base recall | false cert if stop | controller | broad support | broad recall | broad controller |
|---|---:|---:|---:|---|---|---:|---:|---|
| policy_docset_v1 | 0.250 | 0.771 | 0.708 | True | CONTINUE | 0.750 | 1.000 | SAFE |
| code_repo_v1 | 0.333 | 0.750 | 0.300 | True | CONTINUE | 1.000 | 0.950 | SAFE |
| requests | 0.250 | 0.889 | 0.104 | True | CONTINUE | 1.000 | 1.000 | SAFE |
| urllib3 | 0.200 | 0.915 | 0.193 | True | CONTINUE | 0.800 | 0.835 | CONTINUE |

Interpretation:

All localized homogeneous stops would be false certifications. Broad exposure improves completion eligibility, but `urllib3` shows that broad exposure alone is not sufficient for `SAFE`.

## Table 2: Repair Candidate Boundary

| task | residual gain | high-potential gain | random gain | residual cost-normalized | high-potential cost-normalized | overlap |
|---|---:|---:|---:|---:|---:|---:|
| policy_docset_v1 | 4.000 | 0.000 | 2.025 | 0.125 | 0.000 | n/a |
| code_repo_v1 | 9.000 | 5.000 | 4.315 | 0.136 | 0.076 | n/a |
| requests | 177.000 | 177.000 | 45.535 | 0.054 | 0.054 | 1.000 |
| urllib3 | 329.000 | 275.000 | 92.525 | 0.062 | 0.063 | 0.667 |

Interpretation:

Residual-potential has positive repair evidence, but not enough for an optimality claim. The `requests` task shows complete overlap with high-potential. The `urllib3` task shows higher total residual-potential gain but similar cost-normalized evidence.

## Table 3: Leakage Control Checklist

| component | runtime allowed | oracle forbidden |
|---|---|---|
| exposure distribution | visits, scans, route actions | oracle missing mass |
| support ratio / Gini | runtime exposure counts | post-hoc recall |
| potential | source text, route names, lexical matches, source length | undiscovered true item counts |
| controller decision | runtime evidence condition and repair outcome | scorer-visible target distribution |

## Table 4: Geometry Ablation Summary

| geometry | role | current status |
|---|---|---|
| source-only | coarse control | too coarse; can collapse route distinctions |
| source-route | main geometry | best interpretability/effectiveness tradeoff |
| source-route-action | robustness check | more detailed but not yet more informative |
