# Experiments RQ Version

This file rewrites the experimental section around research questions. It also
adds reproducibility details requested by reviewers: sources/routes, oracle
construction, workflow settings, seeds, budgets, thresholds, cost accounting, and
leakage control.

## Research Questions

**RQ1. Does localized source-route evidence create false certification risk?**

This tests the main diagnostic claim: no-new or stop evidence produced under
localized source-route exposure should not be accepted as a global completion
certificate.

**RQ2. Does broad exposure provide completion eligibility rather than completion
proof?**

This tests the boundary between geometry eligibility and `SAFE`. Broad exposure
should make certification plausible, but `SAFE` should still require no residual
evidence.

**RQ3. Does the evidence-condition controller reduce unsafe stop decisions?**

This evaluates whether the controller avoids false certification by returning
`CONTINUE` or `ABSTAIN` when the evidence condition is too narrow or repair finds
new evidence, while still allowing `SAFE` when the evidence condition is broad
and stable.

**RQ4. What is the boundary between residual-potential and high-potential
repair?**

This checks the method boundary. Residual-potential should be treated as a
mechanism-aligned repair instance, not as a proven optimal active-search method.

## Tasks

We evaluate four bounded completion-audit tasks.

### `policy_docset_v1`

Generated policy document set with four sources:

- `access_control.md`
- `data_handling.md`
- `release_process.md`
- `audit_and_exceptions.md`

Routes:

- `obligation_route`
- `exception_route`
- `deadline_route`
- `prohibition_route`

The oracle contains 24 policy clauses (`P01`--`P24`) labeled by bucket and source.
The oracle is written separately and used only for scoring.

### `code_repo_v1`

Generated bounded code repository with four sources:

- `auth.py`
- `payments.py`
- `storage.py`
- `api_client.py`

Routes:

- `compat_route`
- `security_route`
- `resilience_route`

The oracle contains 20 code-risk items (`C01`--`C20`) labeled by bucket and
source. The oracle is hidden from runtime trajectories and used only for scoring.

### `requests`

External real-repository audit over a local installed snapshot of the Python
`requests` package. Sources:

- `adapters.py`
- `api.py`
- `auth.py`
- `models.py`
- `sessions.py`
- `utils.py`

Routes:

- `tls_route`
- `timeout_route`
- `exception_route`
- `compat_route`

The oracle is pattern-defined from the frozen snapshot using route-specific
regular expressions. This is stronger than a generated toy task because it uses
real source structure, but weaker than a human-annotated benchmark.

### `urllib3`

External real-repository audit over a local installed snapshot of `urllib3`.
Sources:

- `connection.py`
- `connectionpool.py`
- `poolmanager.py`
- `response.py`
- `util/retry.py`
- `util/timeout.py`

Routes:

- `timeout_route`
- `retry_route`
- `tls_route`
- `exception_route`
- `cleanup_route`

The source-route simplex contains 30 strata. The oracle is pattern-defined from
the frozen snapshot and used only after base trajectories and challenger choices
are fixed.

## Workflow Conditions

We compare three condition families.

**Homogeneous route reuse.** Multiple agents repeatedly apply the same route
across sources. In `policy_docset_v1`, agents reuse `obligation_route`. In
`code_repo_v1`, agents reuse `compat_route`. In `requests` and `urllib3`, agents
reuse `timeout_route`. These conditions intentionally produce plausible local
stop signals under narrow source-route exposure.

**Route-partitioned audit.** Agents divide the intended audit routes across the
same sources. This broadens source-route support and tests whether broader
exposure improves completion eligibility.

**Extended audit.** Available for `urllib3`, this adds the cleanup route and
covers all five intended routes. It tests the distinction between broad but still
productive evidence and broad stable evidence.

## Controller Settings

The controller uses runtime source-route exposure summaries:

```text
support_ratio(t) = occupied source-route strata / intended source-route strata
G_exp(t) = Gini(exposure counts over intended strata)
```

The operational eligibility thresholds used in the external controller
validation are:

```text
SAFE_SUPPORT_MIN = 0.75
SAFE_GINI_MAX = 0.70
SAFE_RECALL_MIN = 0.90  # evaluation only
```

`SAFE_RECALL_MIN` is not visible to the controller. It is used only to label
false certification under bounded oracle evaluation.

The paper should state clearly that support and Gini thresholds are operational
test points, not universal laws. The invariant is the controller structure:
localized evidence is not eligible for `SAFE`; broad evidence is eligible but
not sufficient; residual evidence forces `CONTINUE`.

## Repair Challengers

Repair challengers are evaluated after homogeneous local stops.

Challengers:

- `random`
- `low_exposure`
- `low_discovery`
- `high_potential`
- `residual_potential`
- `free_search_continuation` where available

Budget:

- Generated task first-pass challengers used a target budget of 4 strata.
- Method validation reran generated-task challengers for 200 seeds.
- `requests` challengers used 200 seeds and a target budget of 4 strata.
- `urllib3` challengers used 200 seeds and a target budget of 5 strata.

Cost:

- Cost is counted as scanned source lines plus extraction events.
- Cost-normalized evidence is new scored evidence divided by the measured scan
  cost.

Runtime potential:

- Generated tasks use route match counts over source text.
- External tasks use source text, route names, source length, and lexical route
  hits.
- Potential does not use oracle totals, oracle missing mass, undiscovered true
  item counts, post-hoc recall, or scorer-visible target distributions.

## Leakage Control

Oracle rows are constructed offline from the frozen task files or repository
snapshot. They are not available to agents, route assignment, stop decisions, or
challenger selection. The runtime controller may use:

- evidence log events;
- source and route identifiers;
- exposure counts;
- source text;
- route-specific lexical match counts;
- source length;
- non-oracle discovery ledger signals.

The runtime controller may not use:

- oracle labels;
- oracle totals;
- oracle missing mass;
- undiscovered true item counts;
- post-hoc recall;
- scorer-visible target distributions.

## RQ1: Localized Evidence and False Certification

Across all four tasks, homogeneous route reuse produces localized evidence
conditions and would cause false certification if accepted as `SAFE`.

| task | base support | base Gini | base recall | false cert if stop | controller |
|---|---:|---:|---:|---|---|
| policy_docset_v1 | 0.250 | 0.771 | 0.708 | True | CONTINUE |
| code_repo_v1 | 0.333 | 0.750 | 0.300 | True | CONTINUE |
| requests | 0.250 | 0.889 | 0.104 | True | CONTINUE |
| urllib3 | 0.200 | 0.915 | 0.193 | True | CONTINUE |

Interpretation: the false stop is not merely an item-recovery failure. It is a
certificate mismatch: the stop evidence was produced under a narrow source-route
condition and cannot support a global completion claim.

## RQ2: Broad Exposure as Eligibility, Not Proof

Route-partitioned evidence improves completion eligibility in all tasks, but it
does not always justify `SAFE`.

| task | broad support | broad recall | broad controller |
|---|---:|---:|---|
| policy_docset_v1 | 0.750 | 1.000 | SAFE |
| code_repo_v1 | 1.000 | 0.950 | SAFE |
| requests | 1.000 | 1.000 | SAFE |
| urllib3 | 0.800 | 0.835 | CONTINUE |

The `urllib3` row is essential. Route-partitioned exposure is broad enough to be
geometry-eligible, but repair/audit remains productive and bounded-oracle recall
is below threshold. The controller returns `CONTINUE`, not `SAFE`. The extended
`urllib3` audit reaches support `1.000`, recall `1.000`, and `SAFE`.

## RQ3: Controller Reduction of Unsafe Stops

A naive controller that accepts local stop signals would falsely certify all four
homogeneous conditions. The evidence-condition controller rejects these stops
because the evidence condition is localized. It also avoids the opposite trivial
failure mode: it does not always refuse stopping. It returns `SAFE` for
`policy_docset_v1`, `code_repo_v1`, and `requests` under broad complete
conditions, and reserves `SAFE` for the extended `urllib3` audit rather than the
route-partitioned but incomplete `urllib3` condition.

This supports the intended controller role: distinguish local stop evidence,
broad-but-productive evidence, and broad-stable evidence.

## RQ4: Residual-Potential Boundary

Residual-potential provides positive repair evidence but is not proven optimal.

| task | residual gain | high-potential gain | random gain | residual per cost | high-potential per cost | overlap |
|---|---:|---:|---:|---:|---:|---:|
| policy_docset_v1 | 4.000 | 0.000 | 2.025 | 0.125 | 0.000 | n/a |
| code_repo_v1 | 9.000 | 5.000 | 4.315 | 0.136 | 0.076 | n/a |
| requests | 177.000 | 177.000 | 45.535 | 0.054 | 0.054 | 1.000 |
| urllib3 | 329.000 | 275.000 | 92.525 | 0.062 | 0.063 | 0.667 |

On `requests`, residual-potential and high-potential are identical at
source-route granularity. On `urllib3`, residual-potential recovers more total
new evidence, but high-potential is similar or slightly better in
cost-normalized evidence. Therefore the correct claim is:

```text
Residual-potential is a mechanism-aligned repair instance that can expose
residual evidence; it is not an optimal active-search method.
```

## Optional Additional Validation

The most useful optional validation is a small claim-verification completion
audit rather than another item-discovery repo audit. Candidate claim:

```text
All network-facing calls either set a timeout or route through a retry/timeout policy.
```

Sources would be files or modules. Routes would include support search,
contradiction search, exception-path audit, configuration-default audit, and
scope-boundary audit. The oracle should label supporting, contradicting, and
unresolved evidence. If not run before submission, this should remain future
validation rather than part of the main result.
