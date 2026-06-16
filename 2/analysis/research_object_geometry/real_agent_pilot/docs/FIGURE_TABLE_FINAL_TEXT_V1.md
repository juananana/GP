# Figure and Table Final Text v1

This file freezes the main figure and table text for the v1 paper draft. The
visuals should directly support the central claim:

```text
Local evidence cannot automatically support a global completion claim.
```

## Figure 1: Certificate Mismatch in Dynamic Agent Workflows

### Intended Visual Structure

Use a four-panel left-to-right schematic.

Panel A: Workflow evidence collection.

- Show agents or tool calls interacting with multiple sources.
- Each action is labeled by a route, e.g. timeout, TLS, exception, cleanup.
- The visual unit is a source-route stratum, not only a source.

Panel B: Local stop evidence.

- Highlight repeated exposure on a small subset of source-route strata.
- Show local signals such as no-new findings, agreement, and stable summaries
  emerging from that highlighted region.

Panel C: Naive certificate mismatch.

- Show the local stop signal being promoted into a global completion certificate.
- Mark the mismatch between the narrow evidence condition and the broad stop
  claim.

Panel D: Evidence-condition controller.

- Show the controller checking source-route exposure, repairing weak plausible
  strata, and returning one of `SAFE`, `CONTINUE`, or `ABSTAIN`.
- Make clear that broad exposure is an eligibility condition, not automatic
  safety.

### In-Figure Text

Recommended short labels:

```text
Evidence is conditioned by source and route.
Local exhaustion does not certify global completion.
Controller audits the evidence condition before SAFE.
```

Avoid phrasing that implies the controller proves total correctness.

### Caption

**Figure 1: Certificate mismatch in completion decisions.** Dynamic workflows
produce stop evidence under specific source-route conditions. Repeated no-new
findings, agent agreement, or stable summaries can indicate local exhaustion, but
they do not automatically support a global completion claim. The
evidence-condition controller checks whether the exposure condition is broad
enough for the claim, repairs weak plausible strata, and outputs `SAFE`,
`CONTINUE`, or `ABSTAIN`.

### Main-Text Callout

Figure 1 illustrates the failure mode targeted by the paper. The problem is not
only that agents can miss evidence; it is that locally conditioned evidence can
be converted into a global completion certificate without auditing the condition
under which that evidence was produced.

## Figure 2: Source-Route Exposure Geometry

### Intended Visual Structure

Use a coverage-simplex or grid-simplex hybrid. The figure should make the
geometry concrete without implying a new latent variable.

Panel A: Source-route strata.

- Show sources on one axis and routes on the other.
- Each cell is a stratum `s = (source, route)`.

Panel B: Exposure distribution.

- Define the runtime exposure distribution:

```text
p_exp(t, s) = v_t(s) / sum_s v_t(s)
```

- Show three stylized exposure patterns:
  - homogeneous: concentrated on a small face or small set of cells;
  - route-partitioned: broader support across routes and sources;
  - extended audit: broad support with no residual evidence.

Panel C: Decision boundary.

- Annotate:

```text
localized -> not eligible for SAFE
broad + residual evidence -> CONTINUE
broad + no residual evidence -> SAFE
```

If space is limited, collapse Panel C into annotations on Panel B.

### In-Figure Text

Recommended short labels:

```text
s = (source, route)
support_ratio = covered strata / intended strata
G_exp = localization of exposure counts
```

Side note:

```text
Source-only collapses routes; source-route-action is a robustness view.
```

### Caption

**Figure 2: Source-route exposure geometry.** The runtime exposure distribution
over source-route strata records where and how completion evidence was produced.
Homogeneous route reuse concentrates exposure on a small part of the coverage
simplex, so stop evidence is locally conditioned. Broader route-partitioned
exposure makes a stop claim eligible for certification, but `SAFE` additionally
requires that repair or audit reveal no residual evidence.

### Main-Text Callout

Figure 2 defines the operational geometry used by the controller. Source-only
coverage is too coarse because it hides untested routes within a source; more
detailed source-route-action geometry is possible, but source-route is the
default because it is interpretable, runtime-computable, and sufficient for the
main diagnostic in the current evidence.

## Table 1: Cross-Task Diagnostic and Controller Outcomes

### Table

| task | base support | base Gini | base recall | false cert if stop | controller | broad support | broad recall | broad controller |
|---|---:|---:|---:|---|---|---:|---:|---|
| policy_docset_v1 | 0.250 | 0.771 | 0.708 | True | CONTINUE | 0.750 | 1.000 | SAFE |
| code_repo_v1 | 0.333 | 0.750 | 0.300 | True | CONTINUE | 1.000 | 0.950 | SAFE |
| requests | 0.250 | 0.889 | 0.104 | True | CONTINUE | 1.000 | 1.000 | SAFE |
| urllib3 | 0.200 | 0.915 | 0.193 | True | CONTINUE | 0.800 | 0.835 | CONTINUE |

### Caption

**Table 1: Cross-task evidence-condition diagnostic.** Homogeneous route reuse
produces localized exposure and would be a false certification if accepted as a
global stop in all four tasks. Broader source-route exposure improves completion
eligibility. The `urllib3` row is the boundary case: route-partitioned exposure
is broad but still incomplete, so the controller outputs `CONTINUE` rather than
`SAFE`.

### Main-Text Takeaway

The table supports the main claim without overclaiming: local evidence is unsafe
as a global certificate, and broad exposure is necessary for eligibility but not
sufficient for safety.

## Table 2: Repair Boundary

### Table

| task | residual gain | high-potential gain | random gain | residual per cost | high-potential per cost | high/residual overlap |
|---|---:|---:|---:|---:|---:|---:|
| policy_docset_v1 | 4.000 | 0.000 | 2.025 | 0.125 | 0.000 | n/a |
| code_repo_v1 | 9.000 | 5.000 | 4.315 | 0.136 | 0.076 | n/a |
| requests | 177.000 | 177.000 | 45.535 | 0.054 | 0.054 | 1.000 |
| urllib3 | 329.000 | 275.000 | 92.525 | 0.062 | 0.063 | 0.667 |

### Caption

**Table 2: Residual-potential as a bounded repair instance.** Residual-potential
often finds residual evidence in weak source-route regions, but the evidence does
not establish optimality. On `requests`, residual-potential and high-potential
select identical target sets and obtain identical gain. On `urllib3`,
residual-potential has higher total gain, while high-potential is similar in
cost-normalized evidence.

### Main-Text Takeaway

Use this table to prevent an accidental method overclaim. Residual-potential
supports the controller mechanism because it can expose residual evidence after
an unsafe stop, but it should not be described as the best active-search policy.

## Table 3: Leakage Control Checklist

### Table

| component | runtime allowed | oracle forbidden |
|---|---|---|
| exposure distribution | visits, scans, source-route actions | oracle missing mass |
| support ratio / Gini | runtime exposure counts | post-hoc recall |
| potential | source text, route names, lexical matches, source length | undiscovered true item counts |
| controller decision | runtime evidence condition and repair outcome | scorer-visible target distribution |

### Caption

**Table 3: Leakage control for controller and repair decisions.** The controller
and repair rules use only runtime-visible evidence. Oracle labels, oracle totals,
post-hoc recall, and undiscovered true item counts are used only after
trajectories and challenger choices are fixed, for evaluation.

### Main-Text Takeaway

This table should appear near the experimental protocol or in an appendix
referenced from the protocol. It protects the paper's central claim by separating
runtime decision information from scorer-only oracle information.
