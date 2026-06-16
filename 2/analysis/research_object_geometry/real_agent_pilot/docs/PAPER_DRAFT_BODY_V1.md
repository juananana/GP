# Evidence-Condition Geometry for Completion Decisions in Dynamic Agent Workflows

## Abstract

Dynamic agent workflows often need to decide when a task is complete before the
size and structure of the remaining workload are known. Existing stop signals
such as no-new findings, agent agreement, stable summaries, or self-reported
completion can be useful local evidence, but they do not by themselves specify
the conditions under which that evidence was produced. This paper studies the
resulting certificate mismatch: a workflow may use evidence gathered under a
localized source-route condition to support a global completion claim.

We introduce source-route evidence-condition geometry as a runtime diagnostic
for this failure mode. A source-route stratum records both where the workflow
searched and which audit or search route it applied. The exposure distribution
over these strata describes the condition under which stop evidence was
generated. We then define a conservative evidence-condition controller that
rejects `SAFE` when the current evidence condition is too localized, triggers
targeted repair over weak plausible strata, and outputs `SAFE`, `CONTINUE`, or
`ABSTAIN`. Residual-potential is evaluated as one mechanism-aligned repair
instance, not as an optimal search method.

Across four bounded completion-audit tasks, homogeneous route reuse produces
localized evidence conditions and would lead to false certification if accepted
as a global stop. Broader source-route exposure improves completion eligibility,
while the `urllib3` external audit shows the key boundary: broad exposure is not
sufficient for `SAFE` when residual evidence remains. These results support a
restrained claim: local evidence cannot automatically certify global completion;
completion decisions require the evidence condition itself to be audited.

## 1. Introduction

Agent workflows are increasingly used for tasks whose true workload is not known
at runtime: searching a repository for all instances of a behavior, auditing a
document set for policy exceptions, checking whether an implementation has
covered all relevant failure modes, or deciding whether a multi-agent procedure
has exhausted the space of useful evidence. In these settings, the workflow must
eventually decide whether to stop. The difficulty is that the absence of newly
found evidence is not the same object as evidence that the intended workload is
complete.

The central failure studied in this paper is certificate mismatch. A workflow may
produce a plausible local stop signal: repeated scans return no new findings,
agents agree with each other, subtasks appear closed, or a summary becomes stable.
However, these signals are conditioned on the parts of the task that were
actually searched and on the routes by which they were searched. If the workflow
has repeatedly applied the same route to the same subset of sources, then a
no-new signal may certify only local exhaustion. It does not automatically
support a global claim that the task is complete over its intended scope.

This distinction matters because many dynamic workflows operate under hidden
total workload. The system does not know how many relevant items, counterexamples,
or unresolved cases exist. More importantly, it may not know which source-route
conditions are necessary for the stop claim to be meaningful. Auditing a file for
timeouts, for example, does not certify that the same file has been audited for
TLS behavior, exception behavior, retry behavior, or cleanup behavior. The same
source can support different kinds of evidence depending on the route applied to
it.

We formalize this observation with evidence-condition geometry. The basic unit is
a source-route stratum, consisting of a bounded evidence region and an audit or
search route. At runtime, the workflow accumulates exposure counts over these
strata. The normalized exposure distribution describes the condition under which
the workflow's completion evidence was produced. When this distribution is
localized, stop evidence is locally conditioned. It may be useful, but it is not a
global completion certificate.

Based on this geometry, we define an evidence-condition controller. At a proposed
stop, the controller computes the source-route exposure condition, checks whether
the condition is broad enough to make the completion claim eligible for
certification, and, when necessary, triggers repair or audit over weak plausible
strata. The controller is intentionally conservative: broad exposure gives
completion eligibility, not automatic safety. A `SAFE` decision also requires
that repair or audit reveal no residual evidence. If residual evidence appears,
the controller outputs `CONTINUE`; if budget is exhausted without a defensible
certificate, it outputs `ABSTAIN`.

Our experiments evaluate this controller on four bounded completion-audit task
families: two generated scored tasks and two external real-repository audits with
pattern-defined oracles. The experiments are not presented as a benchmark for the
best item discovery policy. Instead, they test whether source-route exposure
localization diagnoses unsafe stop claims and whether a controller can avoid
accepting locally conditioned evidence as global completion proof.

The contributions are:

1. We formulate false completion as certificate mismatch between the scope of a
   stop claim and the source-route condition under which supporting evidence was
   produced.
2. We introduce source-route exposure geometry as a runtime-computable diagnostic
   for whether completion evidence is locally or broadly conditioned.
3. We define an evidence-condition controller that outputs `SAFE`, `CONTINUE`, or
   `ABSTAIN` by combining exposure breadth with residual repair evidence.
4. We provide controlled and external validation showing that homogeneous route
   reuse creates false certification risk, while broader source-route evidence
   improves completion eligibility without being sufficient for safety.

We deliberately do not claim that residual-potential is an optimal repair method.
It is one mechanism-aligned repair instance used to test whether weak
source-route regions can expose residual evidence. The main claim is about the
conditions under which completion evidence can support a stop decision.

## 2. Related Work

### Technology-Assisted Review and Total Recall

Technology-assisted review and total-recall methods study how to retrieve nearly
all relevant items under labeling and review budgets. This literature is adjacent
to our scored subclasses because we report recall where a bounded oracle exists.
The target decision in this paper is different. We do not primarily optimize an
item retrieval policy. We ask whether a dynamic workflow has enough conditioned
evidence to certify a completion claim. Item discovery is therefore an evaluation
subclass, not the definition of the problem.

This distinction changes the role of recall. In scored tasks, low recall reveals
that accepting the stop claim would be a false certification. But the controller
does not observe oracle recall at runtime. It observes the evidence condition:
which sources and routes were actually exercised, whether weak plausible gaps
remain, and whether repair finds residual evidence.

### Active Search and Active Learning

Active search selects actions to find positives efficiently, and active learning
selects examples to improve a model. Residual-potential resembles active search
in that it prioritizes strata that may produce new evidence. Its role here is
narrower. It is not the main optimization target and is not evaluated as a
standalone discovery algorithm. It is used inside a stop controller to test
whether a proposed completion certificate has weak source-route regions that
still contain residual evidence.

The controller's objective is therefore not only yield. A high-yield action can
be useful, but the stop decision must also ask whether the evidence supporting the
completion claim was gathered under conditions broad enough for that claim.

### Missing Mass and Unseen Evidence

Missing-mass and unseen-species methods estimate how much probability mass
remains unseen after sampling. The motivation is close to false stopping under
unknown workload, but our object is not a scalar estimate of hidden mass. The
object is the runtime evidence condition. A workflow can have many observations
and still be localized if those observations come from a small subset of
source-route strata. Conversely, broad exposure can make a completion claim
eligible for certification, but it still does not imply safety when repair
continues to reveal residual evidence.

### Multi-Agent Collapse and Diversity

Work on multi-agent collapse, correlated failures, and diversity often studies
whether agents converge to similar outputs or reasoning traces. Our diagnostic is
not based on semantic similarity between agent answers. It records where and how
the workflow searched. This makes the condition of agreement observable: agents
may agree because the task is complete, or because they repeatedly examined the
same local region through the same route. Source-route exposure geometry
separates these cases at the level of runtime behavior.

### Audit and Verification Agents

Audit and verification agents add checks after or during generation. The repair
step in our controller is related, but it is not a generic post-hoc audit. It is
directed by the current evidence condition and is invoked specifically to decide
whether a stop claim can be certified. The repair target is a weak but plausible
source-route stratum, not an unrestricted request for another agent to review the
answer.

## 3. Problem Formulation

We study workload-unknown dynamic agent workflows. A workflow receives a task,
allocates work across agents or tools, gathers evidence under a finite budget,
and must decide whether the task is complete. The workload is unknown because
the workflow does not know in advance how much relevant evidence exists or which
source-route conditions are required to support the completion claim.

Let a workflow be

```text
W = (T, S, R, A, B),
```

where `T` is the task, `S` is a set of sources, `R` is a set of routes, `A` is
the set of agents or tools, and `B` is a finite budget. A source is a bounded
evidence region, such as a file, module, document, source family, or repository
component. A route is an audit or search lens applied to a source, such as a
timeout audit, TLS audit, exception audit, policy-exception audit, compatibility
audit, or cleanup audit.

At runtime, the workflow produces evidence events

```text
e_t = (agent_t, source_t, route_t, action_t, observation_t, cost_t).
```

An event may be a search, scan, extraction, verification, summary, or stop
proposal. The important point is that evidence is conditioned: every evidence
event is produced under a source-route condition.

A source-route stratum is

```text
s = (source, route),
```

and the set of strata is

```text
Omega = S x R.
```

A stop claim is a workflow assertion

```text
C_t: task T is complete over the intended workload scope.
```

Signals such as no-new findings, agent agreement, stable summaries, or exhausted
assigned subtasks are evidence for `C_t` only under the source-route conditions
that produced them.

A false certification occurs when the workflow accepts `SAFE` for a stop claim
that is not supported by the bounded evaluation oracle:

```text
SAFE(C_t) = true, but task completion is false under evaluation.
```

In item-discovery subclasses, we operationalize this as accepting `SAFE` while
recall is below the chosen completion threshold. In broader completion-audit
settings, false certification means accepting a global completion claim while
relevant support, contradiction, or unresolved evidence remains outside the
evidence condition.

The controller outputs one of three decisions:

```text
SAFE:
  the evidence condition is broad enough, weak plausible gaps are absent,
  and repair/audit reveals no residual evidence.

CONTINUE:
  the evidence condition is too narrow, or repair/audit reveals new evidence.

ABSTAIN:
  the budget is exhausted and the workflow still lacks a defensible
  completion certificate.
```

The controller does not treat broad exposure alone as sufficient for `SAFE`.
Broad exposure gives completion eligibility; `SAFE` additionally requires no
residual evidence after repair or audit.

## 4. Evidence-Condition Geometry

Let `v_t(s)` be the runtime-visible exposure count for source-route stratum `s`
up to time `t`. Exposure can be visits, scans, tool calls, route-specific audits,
or other logged search actions. Define

```text
p_exp(t, s) = v_t(s) / sum_{s' in Omega} v_t(s').
```

This distribution is a point on the source-route coverage simplex. It describes
the condition under which completion evidence was produced.

When `p_exp(t, s)` is concentrated on a small subset of strata, no-new or
agreement evidence is locally conditioned. It may certify local exhaustion, but
it does not certify global completion. We summarize this exposure distribution
with two operational quantities:

```text
support_ratio(t) = |{s : v_t(s) > 0}| / |Omega|
G_exp(t) = Gini({v_t(s) : s in Omega}).
```

These are summaries of the exposure distribution, not additional core variables.
They are used to decide whether the evidence condition is broad enough for the
stop claim.

The source-route stratum is the default geometry in this paper. Source-only
geometry is too coarse because it collapses routes inside a source. Auditing a
file for timeout behavior does not certify that TLS, retry, exception, or cleanup
behavior has been audited in that file. Source-route-action geometry is more
detailed, but it is sensitive to logging conventions and the current experiments
do not show a stable advantage over source-route. Source-route therefore captures
both where and how evidence was produced while remaining interpretable and
runtime-computable.

## 5. Evidence-Condition Controller

At a proposed stop, the controller checks whether the current evidence condition
can support the stop claim.

```text
Input:
  runtime evidence log E_t
  source-route strata Omega
  proposed stop claim C_t

1. Compute v_t(s) for each s in Omega.
2. Compute p_exp(t), support_ratio(t), and G_exp(t).
3. If the evidence condition is too localized:
     reject SAFE and trigger repair.
4. Select repair strata using a runtime-computable repair rule.
5. Run repair/audit.
6. If repair finds residual evidence:
     output CONTINUE.
   Else if the evidence condition is broad and weak plausible gaps are absent:
     output SAFE.
   Else if budget remains:
     output CONTINUE.
   Else:
     output ABSTAIN.
```

The controller is conservative by design. It does not infer completion merely
from confidence, agreement, or no-new evidence. It asks whether the evidence
condition is strong enough for the scope of the stop claim.

### Residual-Potential as a Repair Instance

The repair instance used in the experiments is

```text
priority(s) = under_exposure(s) x runtime_computable_potential(s).
```

`under_exposure(s)` gives priority to weak parts of the current completion
certificate. `runtime_computable_potential(s)` uses only visible runtime
information, such as source text, route names, source size, route match counts,
or non-oracle ledger signals.

The repair rule is not allowed to use oracle labels, oracle totals, oracle
missing mass, undiscovered true item counts, post-hoc recall, or scorer-visible
target distributions. Oracle labels are used only after trajectories and
challenger choices are fixed.

Residual-potential is a mechanism-aligned repair instance. It is useful for
testing whether weak source-route regions contain residual evidence, but the
paper does not claim that it is optimal or generally superior to all active
search alternatives.

## 6. Experimental Protocol

We evaluate on four task families:

| task | description | oracle type |
|---|---|---|
| `policy_docset_v1` | generated bounded policy document task | generated bounded labels |
| `code_repo_v1` | generated bounded code repository task | generated bounded labels |
| `requests` | external real repository audit | fixed pattern-defined oracle |
| `urllib3` | external real repository audit | fixed pattern-defined oracle |

The generated tasks are controlled scored subclasses. The external tasks provide
stronger runtime evidence because they use real repositories, but their oracles
are still pattern-defined rather than fully human annotated.

We compare three condition families:

```text
homogeneous route reuse:
  repeated local evidence under a narrow route/source condition.

route-partitioned audit:
  broader source-route exposure across the intended audit routes.

extended or near-complete audit:
  broad exposure plus no residual evidence where available.
```

Homogeneous conditions test whether repeated local evidence can produce unsafe
stop claims. Route-partitioned and extended conditions test whether broader
source-route exposure improves completion eligibility and whether the controller
can distinguish eligibility from safety.

We compare repair challengers:

```text
random
low-exposure
high-potential
residual-potential
free-search continuation
```

These challengers are evaluated as evidence-condition repair mechanisms, not as
standalone item-finding algorithms.

The primary metrics are false certification, controller decision, support ratio,
exposure Gini, repair gain, cost-normalized evidence, and overlap between
high-potential and residual-potential. Recall is reported for scored subclasses,
but recall is not the definition of the research problem.

## 7. Results

### Localized Evidence Creates False Certification Risk

Across all four tasks, homogeneous route reuse produces localized evidence
conditions and would cause false certification if accepted as `SAFE`. The base
support ratios range from `0.200` to `0.333`, while base exposure Gini values are
high: `0.750` on `code_repo_v1`, `0.771` on `policy_docset_v1`, `0.889` on
`requests`, and `0.915` on `urllib3`. Under the bounded oracles, the corresponding
base recalls are below the completion threshold in all four tasks.

The controller rejects these local stops. This is the main diagnostic result:
the issue is not simply that an agent failed to find items, but that the stop
evidence was produced under a narrow source-route condition and therefore could
not support a global completion claim.

### Broad Exposure Improves Eligibility but Does Not Guarantee SAFE

Route-partitioned evidence improves completion eligibility. In `policy_docset_v1`,
`code_repo_v1`, and `requests`, the broader condition reaches the completion
threshold and the controller outputs `SAFE`. These cases show that the geometry
is not merely a refusal rule; when the evidence condition is broad and repair
does not reveal residual evidence, the controller can accept the stop claim.

The `urllib3` external audit is the critical boundary case. Route-partitioned
evidence has broad support (`0.800`) and lower localization than the homogeneous
condition, but bounded-oracle recall is `0.835`, below the completion threshold.
The controller outputs `CONTINUE`, not `SAFE`. An extended audit reaches support
`1.000`, recall `1.000`, and receives `SAFE`. This supports the intended claim:
broad exposure is completion eligibility, not a sufficient condition for safety.

### Repair Evidence Is Positive but Bounded

Residual-potential finds residual evidence in several tasks and is useful as a
repair instance. On `code_repo_v1`, it recovers more new true items than random
and high-potential in the source-route setting. On `urllib3`, it recovers more
total new evidence than high-potential. However, the method claim must remain
bounded. On `requests`, residual-potential and high-potential select identical
target sets and obtain identical gain. On `urllib3`, high-potential is similar or
slightly better in cost-normalized evidence despite lower total gain.

These results support residual-potential as a mechanism-aligned repair instance,
not as an optimal repair method. The main conclusion does not depend on proving
that this particular product rule is uniquely best.

### Leakage Control

The controller and repair rules use runtime-visible exposure counts, source text,
route names, route match counts, source sizes, and non-oracle ledger signals.
They do not use oracle totals, oracle missing mass, undiscovered true item
counts, post-hoc recall, or scorer-visible target distributions. Oracle labels
are used only after trajectories and challenger choices are fixed to score
whether a stop would have been a false certification.

## 8. Limitations

The external oracles are pattern-defined rather than human annotated. They are
useful because they test the controller on real repository structure, but they do
not replace a manually curated completion-audit benchmark.

The thresholds used for support ratio and exposure Gini are operational test
points, not theory laws. The current evidence supports the qualitative controller
boundary: local evidence cannot certify global completion, and broad evidence
must still be checked for residual evidence. It does not establish universal
numeric thresholds.

The strata are task-designed. Source-route geometry is interpretable and
runtime-computable, but different domains may require different source and route
definitions. The paper does not claim that a fixed stratum design transfers
unchanged across all workflows.

Residual-potential is not proven optimal. Stronger repair rules may exist, and
some results show that high-potential can match or compete with it. The repair
instance should be read as an implementation of the controller's mechanism, not
as the paper's main algorithmic claim.

Finally, the current experiments are completion-audit and item-discovery
subclasses. A broader claim-verification setting, where the target is whether a
natural-language claim is supported by sufficiently broad and contradiction-free
evidence, remains future work.

## 9. Optional Future Validation: Claim Verification Pilot

A natural next validation is a bounded claim-verification pilot. The task would
give a workflow a set of claims over a document collection or repository and ask
it to certify whether each claim is supported, contradicted, or unresolved. The
source-route strata would pair evidence regions with routes such as support
search, contradiction search, exception search, temporal qualification, and
scope-boundary audit.

This pilot should not change the current main claim. Its purpose would be to test
whether the same certificate mismatch appears when the target is not item recall
but claim support. The expected controller behavior is the same: localized
support evidence should not certify a global claim; broad exposure should make
certification eligible; residual contradiction or unresolved evidence should
force `CONTINUE` or `ABSTAIN`.

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
eligibility without being sufficient by itself.

The main contribution is therefore not a claim that a particular repair heuristic
is optimal. It is a diagnostic and control principle for agent workflows:
completion certificates should be judged by the evidence condition that produced
them.
