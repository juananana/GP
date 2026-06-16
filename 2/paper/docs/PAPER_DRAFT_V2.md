# Local Evidence Is Not Completion: Evidence-Condition Geometry for Dynamic Agent Workflows

## Abstract

Dynamic agent workflows often need to decide whether a task is complete before
the remaining workload is known. Common stop signals, including no-new findings,
agent agreement, stable summaries, and self-reported completion, can be useful
local evidence, but they do not specify the conditions under which that evidence
was produced. The key question is not whether a workflow has stopped, but whether
the evidence condition under which it stopped can support the scope of the
completion claim. We study this certificate mismatch and introduce
source-route evidence-condition geometry as a runtime diagnostic. A source-route
stratum records both where the workflow searched and which audit route it
applied. We then define an evidence-condition controller that rejects `SAFE` when
the current condition is too localized, repairs weak plausible strata, and
returns `SAFE`, `CONTINUE`, or `ABSTAIN`. Across four bounded completion-audit
tasks, homogeneous route reuse produces localized evidence conditions and would
lead to false certification if accepted as a global stop. Broader source-route
exposure improves completion eligibility, while an external `urllib3` audit shows
the key boundary: broad exposure is not sufficient for `SAFE` when residual
evidence remains. The paper provides a diagnostic and control principle rather
than a universal completion guarantee.

## 1. Introduction

Dynamic agent workflows are increasingly used for tasks whose true workload is
not known at runtime: searching a repository for all instances of a behavior,
auditing a document set for policy exceptions, checking whether an implementation
covers relevant failure modes, or deciding whether a multi-agent workflow has
exhausted useful evidence. Such workflows must eventually stop. The difficulty
is that the absence of newly found evidence is not the same object as evidence
that the intended workload is complete.

The failure studied in this paper is certificate mismatch. A workflow may produce
a plausible local stop signal: repeated scans return no new findings, agents
agree with each other, subtasks appear closed, or a summary becomes stable. These
signals are conditioned on the parts of the task that were searched and on the
routes by which they were searched. If the workflow repeatedly applies the same
route to the same subset of sources, a no-new signal may certify only local
exhaustion. It does not automatically support a global claim that the task is
complete over its intended scope.

Consider a code-audit workflow. Auditing a file for timeout behavior does not
certify that the same file has been audited for TLS behavior, exception behavior,
retry behavior, or cleanup behavior. The source may be familiar, the agents may
agree, and the workflow may have stopped finding timeout-related evidence; none
of that establishes that other routes over the same source have been exhausted.
The stop evidence is local in its evidence condition, while the completion claim
is global in scope.

We formalize this observation with evidence-condition geometry. The basic unit
is a source-route stratum, consisting of a bounded evidence region and an audit
or search route. At runtime, the workflow accumulates exposure counts over these
strata. The normalized exposure distribution describes the condition under which
completion evidence was produced. When this distribution is localized, stop
evidence is locally conditioned. It may be useful, but it is not a global
completion certificate.

Based on this geometry, we define an evidence-condition controller. At a proposed
stop, the controller computes the source-route exposure condition, checks whether
the condition is broad enough to make the completion claim eligible for
certification, and, when necessary, triggers repair over weak plausible strata.
The controller is intentionally conservative: broad exposure gives completion
eligibility, not automatic safety. A `SAFE` decision additionally requires that
repair or audit reveal no residual evidence. If residual evidence appears, the
controller outputs `CONTINUE`; if budget is exhausted without a defensible
certificate, it outputs `ABSTAIN`.

Our experiments evaluate this controller on four bounded completion-audit task
families: two generated scored tasks and two external real-repository audits with
pattern-defined oracles. These tasks are not presented as a benchmark for the
best item discovery policy. Instead, they test whether source-route exposure
localization diagnoses unsafe stop claims and whether a controller can avoid
accepting locally conditioned evidence as global completion proof.

The contributions are:

1. We formulate false completion as certificate mismatch between the scope of a
   stop claim and the source-route condition under which supporting evidence was
   produced.
2. We introduce source-route exposure geometry as a runtime-computable diagnostic
   for whether completion evidence is locally or broadly conditioned.
3. We provide a short proposition showing why local no-new evidence can support
   local exhaustion but not global completion without assumptions about
   unexposed strata.
4. We define an evidence-condition controller that outputs `SAFE`, `CONTINUE`, or
   `ABSTAIN` by separating eligibility from completion proof.
5. We provide controlled and external validation showing that homogeneous route
   reuse creates false certification risk, while broader source-route evidence
   improves completion eligibility without being sufficient for safety.

We deliberately do not claim that residual-potential is an optimal repair
method. It is one mechanism-aligned repair instance used to test whether weak
source-route regions can expose residual evidence. The main claim is about the
conditions under which completion evidence can support a stop decision.

## 2. Related Work

### Technology-Assisted Review and Total Recall

Technology-assisted review and total-recall work studies how to retrieve nearly
all relevant items under labeling and review budgets. This literature is
adjacent because our scored subclasses report recall where bounded oracle labels
exist. The distinction is the decision object. Total-recall systems ask how to
retrieve or review enough items; our controller asks whether the evidence
condition under which a workflow proposes to stop can support the scope of its
completion claim. The controller does not observe oracle recall, oracle totals,
or missing mass. It observes source-route exposure, weak plausible gaps, and
whether repair reveals residual evidence. Item discovery is therefore an
evaluation subclass, not the definition of the research problem.

### Active Search and Active Learning

Active search chooses actions to find positives efficiently, and active learning
chooses examples to improve a model. Residual-potential resembles active search
because it prioritizes strata that may produce new evidence. Its role here is
narrower. It is a repair instance inside a stop controller, used to test whether
weak but plausible source-route regions still contain residual evidence. The
controller is not optimized only for yield. A completion decision must also ask
whether the evidence supporting a global stop claim was gathered under conditions
broad enough for that claim.

### Missing Mass and Unseen Evidence

Missing-mass and unseen-species methods estimate how much probability mass
remains unseen after sampling. False stopping under unknown workload is related,
but our object is not a scalar hidden-mass estimate. The object is the runtime
evidence condition: where the workflow searched, which routes it applied, and
whether stop evidence is local or broad relative to the intended workload scope.
A workflow can have many observations and still be localized if those
observations come from a small subset of source-route strata.

### Agent False Completion

Agent systems can prematurely report that a task is done, especially in
long-horizon workflows with tools, decomposition, and self-monitoring. This
paper studies one mechanism behind that failure: local stop evidence is promoted
into a global completion certificate. The contribution is not only to observe
that agents can stop too early, but to formalize the mismatch between the scope
of the stop claim and the source-route condition under which supporting evidence
was produced.

### Dynamic Agent Workflows and Deep Research Completeness

Dynamic workflows allocate work across agents, tools, routes, and intermediate
states. Many such systems are designed around decomposition, planning,
verification, and iterative search. Our setting focuses on the stopping decision
inside such workflows. Evidence-condition geometry does not prescribe a planner,
prompt template, or tool-use policy. It provides a runtime diagnostic for whether
the current evidence log can support a completion claim.

Deep research and report-generation agents face a similar completeness problem:
after searching, reading, summarizing, and reconciling sources, the system must
decide whether the answer is complete enough. Stable summaries or no-new search
results can still be local if contradiction search, temporal qualification, or
scope-boundary audit routes remain underexplored. Claim verification is therefore
a natural future validation for this framework.

### Multi-Agent Collapse, Audit Agents, and Verification Agents

Work on multi-agent collapse, correlated failures, and diversity often studies
whether agents converge to similar outputs, traces, or representations. Our
diagnostic records where and how the workflow searched. Agents may agree because
the task is complete, or because they repeatedly examined the same local
source-route region. Source-route exposure makes that distinction observable.

Audit and verification agents add checks after or during generation. The repair
step in our controller is related, but it is not a generic post-hoc auditor. It
is directed by the evidence condition and invoked specifically to decide whether
a stop claim can be certified. The audit target is a weak but runtime-plausible
source-route stratum, not an unrestricted request for another agent to review the
answer.

## 3. Problem Setting

We study workload-unknown dynamic agent workflows. A workflow receives a task,
allocates work across agents or tools, gathers evidence under a finite budget,
and must decide whether the task is complete. Let

```text
W = (T, S, R, A, B),
```

where `T` is the task, `S` is a set of sources, `R` is a set of routes, `A` is
the set of agents or tools, and `B` is a finite budget. A source is a bounded
evidence region, such as a file, module, document, source family, or repository
component. A route is an audit or search lens applied to a source.

At runtime, the workflow produces evidence events

```text
e_t = (agent_t, source_t, route_t, action_t, observation_t, cost_t).
```

Every evidence event is produced under a source-route condition. A source-route
stratum is

```text
s = (source, route),
```

and the intended evidence-condition space is

```text
Omega = S x R.
```

The source-route space does not require the workflow to know all true missing
items in advance. It requires the intended audit scope to be defined: which
sources and routes are relevant to the completion claim.

A stop claim is

```text
C_t: task T is complete over the intended workload scope.
```

A false certification occurs when the workflow accepts `SAFE` for a stop claim
that is not supported by the evaluation oracle:

```text
SAFE(C_t) = true, but completion(T) = false.
```

In item-discovery subclasses, this is operationalized as accepting `SAFE` while
bounded-oracle recall is below the completion threshold. In broader completion
audits, it means accepting a global completion claim while relevant support,
contradiction, or unresolved evidence remains outside the evidence condition.

## 4. Evidence-Condition Geometry

Let `v_t(s)` be the runtime-visible exposure count for source-route stratum `s`
up to time `t`. Exposure may count visits, scans, route-specific audits, tool
calls, or other logged search actions. Define

```text
p_exp(t, s) = v_t(s) / sum_{s' in Omega} v_t(s').
```

This distribution is a point on the source-route coverage simplex. It describes
where and how completion evidence was produced.

We use two runtime summaries:

```text
support_ratio(t) = |{s : v_t(s) > 0}| / |Omega|
G_exp(t) = Gini({v_t(s) : s in Omega}).
```

These summaries are operational diagnostics, not universal laws. They summarize
whether the evidence condition is localized or broad enough to make a completion
certificate eligible for consideration.

### Proposition 1: Local No-New Evidence Is Not a Global Certificate

Let `U` be a strict subset of the intended source-route space `Omega`. Suppose
all evidence used to support a stop claim `C_t` is produced inside `U`, and
suppose the workflow observes no-new evidence only for actions inside `U`. Then
the no-new evidence can support local exhaustion over `U`, but it cannot by
itself support global completion over `Omega`.

Proof sketch. No-new evidence is conditioned on the source-route actions that
were executed. If no events are produced in `Omega \ U`, the workflow has not
observed the absence of residual evidence in those unexposed strata. A world in
which `U` is exhausted and `Omega \ U` contains residual evidence is
observationally indistinguishable from a globally complete world under the
workflow's local evidence log. Therefore local no-new evidence rules out
additional findings only under the searched condition `U`; without additional
assumptions about unsearched strata, it cannot rule out residual evidence in
`Omega \ U`.

The proposition does not claim that global completion is impossible. It states
that a local evidence condition is insufficient as a certificate. A controller
must inspect whether the evidence condition matches the scope of the stop claim
before accepting `SAFE`.

### Choice of Geometry

Source-only geometry is too coarse: auditing a file for timeout behavior does
not certify that TLS, retry, exception, or cleanup behavior has been audited in
that file. Source-route-action geometry is more detailed, but it is sensitive to
logging conventions and current experiments do not show a stable advantage over
source-route. Source-route is the default because it captures both where and how
evidence was produced while remaining interpretable and runtime-computable.

## 5. Evidence-Condition Controller

At a proposed stop, the controller checks whether the current evidence condition
can support the stop claim.

```text
Algorithm 1 Evidence-Condition Controller

Input:
  E_t       runtime evidence log up to proposed stop time t
  Omega     intended source-route space
  C_t       proposed stop claim
  B_rem     remaining budget
  tau_s     minimum support-ratio threshold for eligibility
  tau_g     maximum exposure-Gini threshold for eligibility
  Repair    runtime-computable repair rule

Output:
  decision in {SAFE, CONTINUE, ABSTAIN}

1.  Compute exposure counts v_t(s) for all s in Omega from E_t.
2.  Compute p_exp(t, s), support_ratio(t), and G_exp(t).
3.  Set eligible =
        support_ratio(t) >= tau_s and G_exp(t) <= tau_g.

4.  If eligible is false:
        If B_rem == 0:
            return ABSTAIN.
        Select weak plausible strata using Repair(E_t, Omega, C_t).
        Run repair/audit within remaining budget.
        If repair reveals residual evidence:
            return CONTINUE.
        Recompute support_ratio and G_exp after repair.
        If eligibility still fails:
            return CONTINUE if budget remains else ABSTAIN.

5.  If eligible is true:
        Audit weak plausible gaps if any remain.
        If repair/audit reveals residual evidence:
            return CONTINUE.
        Else:
            return SAFE.
```

The eligibility check is not a completion proof. It is only a test of whether the
evidence condition is broad enough for a global stop claim to be considered. A
`SAFE` decision additionally requires that repair or audit reveal no residual
evidence.

### Residual-Potential Repair

The repair instance used in the experiments is

```text
priority(s) = under_exposure(s) x runtime_computable_potential(s).
```

`under_exposure(s)` prioritizes weak parts of the current completion certificate.
`runtime_computable_potential(s)` uses only visible runtime information, such as
source text, route names, source size, route match counts, or non-oracle ledger
signals. It does not use oracle labels, oracle totals, oracle missing mass,
undiscovered true item counts, post-hoc recall, or scorer-visible target
distributions. Residual-potential is a mechanism-aligned repair instance, not an
optimal active-search algorithm.

## 6. Experiments

We organize experiments around four research questions.

**RQ1. Does localized source-route evidence create false certification risk?**

**RQ2. Does broad exposure provide completion eligibility rather than completion
proof?**

**RQ3. Does the evidence-condition controller reduce unsafe stop decisions?**

**RQ4. What is the boundary between residual-potential and high-potential
repair?**

### Tasks and Reproducibility Details

`policy_docset_v1` is a generated policy document set with four sources:
`access_control.md`, `data_handling.md`, `release_process.md`, and
`audit_and_exceptions.md`. Routes are `obligation_route`, `exception_route`,
`deadline_route`, and `prohibition_route`. The hidden oracle contains 24 policy
clauses labeled by source and route bucket.

`code_repo_v1` is a generated bounded code repository with four sources:
`auth.py`, `payments.py`, `storage.py`, and `api_client.py`. Routes are
`compat_route`, `security_route`, and `resilience_route`. The hidden oracle
contains 20 code-risk items.

`requests` is an external real-repository audit over six files from a local
installed snapshot of the Python `requests` package: `adapters.py`, `api.py`,
`auth.py`, `models.py`, `sessions.py`, and `utils.py`. Routes are `tls_route`,
`timeout_route`, `exception_route`, and `compat_route`. The oracle is
pattern-defined from the frozen snapshot using route-specific regular
expressions.

`urllib3` is an external real-repository audit over six files from a local
installed snapshot of `urllib3`: `connection.py`, `connectionpool.py`,
`poolmanager.py`, `response.py`, `util/retry.py`, and `util/timeout.py`. Routes
are `timeout_route`, `retry_route`, `tls_route`, `exception_route`, and
`cleanup_route`, giving 30 intended source-route strata. The oracle is
pattern-defined from the frozen snapshot.

The external tasks are stronger than generated tasks because they exercise real
source structure, but weaker than human-annotated completion-audit benchmarks
because their oracles are pattern-defined.

### Workflow Conditions

Homogeneous route reuse assigns multiple agents to the same route across
sources. In `policy_docset_v1`, agents reuse `obligation_route`; in
`code_repo_v1`, agents reuse `compat_route`; in `requests` and `urllib3`, agents
reuse `timeout_route`. Route-partitioned audit assigns agents to different
routes over the same source set. `urllib3` additionally includes an
`extended_audit` condition covering all five routes.

### Seeds, Budgets, Thresholds, and Cost

Generated-task first-pass challengers used a target budget of 4 strata; method
validation reran generated-task challengers for 200 seeds. `requests` challengers
used 200 seeds and a budget of 4 strata. `urllib3` challengers used 200 seeds and
a budget of 5 strata.

The external controller validation uses:

```text
SAFE_SUPPORT_MIN = 0.75
SAFE_GINI_MAX = 0.70
SAFE_RECALL_MIN = 0.90  # evaluation only
```

`SAFE_RECALL_MIN` is not visible to the controller. It is used only to label
false certification under bounded oracle evaluation. Cost is counted as scanned
source lines plus extraction events. Cost-normalized evidence is new scored
evidence divided by measured scan cost.

### Leakage Control

Oracle rows are constructed offline from the frozen task files or repository
snapshot. They are not available to agents, route assignment, stop decisions, or
challenger selection. Runtime decisions may use evidence log events, source and
route identifiers, exposure counts, source text, route-specific lexical match
counts, source length, and non-oracle ledger signals. They may not use oracle
labels, oracle totals, oracle missing mass, undiscovered true item counts,
post-hoc recall, or scorer-visible target distributions.

## 7. Results

### RQ1: Localized Evidence Creates False Certification Risk

Across all four tasks, homogeneous route reuse produces localized evidence
conditions and would cause false certification if accepted as `SAFE`.

| task | base support | base Gini | base recall | false cert if stop | controller |
|---|---:|---:|---:|---|---|
| policy_docset_v1 | 0.250 | 0.771 | 0.708 | True | CONTINUE |
| code_repo_v1 | 0.333 | 0.750 | 0.300 | True | CONTINUE |
| requests | 0.250 | 0.889 | 0.104 | True | CONTINUE |
| urllib3 | 0.200 | 0.915 | 0.193 | True | CONTINUE |

The result supports the diagnostic claim. The false stop is not merely an
item-recovery failure; it is a certificate mismatch between local evidence and a
global completion claim.

### RQ2: Broad Exposure Is Eligibility, Not Proof

Route-partitioned evidence improves completion eligibility in all tasks, but it
does not always justify `SAFE`.

| task | broad support | broad recall | broad controller |
|---|---:|---:|---|
| policy_docset_v1 | 0.750 | 1.000 | SAFE |
| code_repo_v1 | 1.000 | 0.950 | SAFE |
| requests | 1.000 | 1.000 | SAFE |
| urllib3 | 0.800 | 0.835 | CONTINUE |

The `urllib3` row is the boundary case. Route-partitioned exposure is broad
enough to be geometry-eligible, but bounded-oracle recall is below threshold and
repair/audit remains productive. The controller returns `CONTINUE`, not `SAFE`.
The extended `urllib3` audit reaches support `1.000`, recall `1.000`, and
`SAFE`.

### RQ3: Controller Reduction of Unsafe Stops

A naive controller that accepts local stop signals would falsely certify all four
homogeneous conditions. The evidence-condition controller rejects these stops
because the evidence condition is localized. It also avoids the trivial
"never stop" solution: it returns `SAFE` for `policy_docset_v1`, `code_repo_v1`,
and `requests` under broad complete conditions, and reserves `SAFE` for the
extended `urllib3` audit rather than the broad-but-incomplete route-partitioned
condition.

This supports the intended controller role: distinguish local stop evidence,
broad-but-productive evidence, and broad-stable evidence.

### RQ4: Residual-Potential Boundary

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
cost-normalized evidence. The correct conclusion is that residual-potential is a
mechanism-aligned repair instance that can expose residual evidence, not an
optimal active-search method.

## 8. Figure Plan

The final paper should use two main figures.

**Figure 1: Local Evidence Is Not Completion.** This should be a simple
conceptual figure showing localized source-route exposure, a no-new stop signal,
a global completion claim, and a mismatch. The controller appears as the
corrective branch. The figure should use minimal in-figure text and rely on the
caption for explanation.

**Figure 2: Evidence-Condition Controller.** This should be the formal method
figure. It maps evidence log `E_t` to exposure distribution over `Omega`, then to
eligibility check, repair, and `SAFE` / `CONTINUE` / `ABSTAIN`. The figure should
show three states: localized -> not eligible; broad + residual evidence ->
`CONTINUE`; broad + no residual evidence -> `SAFE`.

## 9. Limitations and Additional Validation

The current evidence supports a diagnostic and controller in bounded
completion-audit subclasses. It does not establish a universal completion
certificate for arbitrary agent workflows.

First, the external oracles are pattern-defined rather than human annotated.
They test whether the mechanism survives real repository structure, but they do
not replace a manually curated completion-audit benchmark. Second, support and
Gini thresholds are operational test points, not theory laws. Third,
source-route strata are task-designed; different domains may require different
source and route definitions. Fourth, residual-potential is not proven optimal,
and high-potential can match or compete with it in some settings.

The most useful optional validation is a small claim-verification completion
audit rather than another item-discovery repo audit. A candidate claim is:

```text
All network-facing calls either set a timeout or route through a retry/timeout policy.
```

Sources would be files or modules. Routes would include support search,
contradiction search, exception-path audit, configuration-default audit, and
scope-boundary audit. The oracle should label supporting, contradicting, and
unresolved evidence. If not run before submission, this should remain future
validation rather than part of the main result.

## 10. Conclusion

This paper studies completion decisions in dynamic agent workflows under unknown
workload. The central observation is simple but consequential: local evidence
does not automatically support a global completion claim. Stop signals such as
no-new findings, agreement, or stable summaries are conditioned on where and how
the workflow searched.

Source-route evidence-condition geometry makes this conditioning explicit. The
evidence-condition controller uses that geometry to reject unsafe local stops,
repair weak plausible strata, and reserve `SAFE` for cases where the evidence
condition is broad and no residual evidence appears. Across generated and
external bounded audits, homogeneous route reuse consistently creates false
certification risk, while broader source-route exposure improves completion
eligibility without being sufficient by itself. The main contribution is
therefore not a claim that a particular repair heuristic is optimal. It is a
diagnostic and control principle: completion certificates should be judged by the
evidence condition that produced them.
