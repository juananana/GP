# Related Work v1

This related-work draft positions the paper as an evidence-condition geometry
and controller paper for dynamic agent completion decisions. It avoids presenting
residual-potential as the main contribution.

## Technology-Assisted Review and Total Recall

Technology-assisted review and total-recall work studies how to retrieve nearly
all relevant items under labeling and review budgets. This literature is
adjacent because our scored subclasses report recall where bounded oracle labels
exist. The distinction is the decision object. Total-recall systems ask how to
retrieve or review enough items; our controller asks whether the evidence
condition under which a workflow proposes to stop can support the scope of its
completion claim.

This distinction matters at runtime. The controller does not observe oracle
recall, oracle totals, or missing mass. It observes the source-route exposure
condition, weak plausible gaps, and whether repair reveals residual evidence.
Item discovery is therefore an evaluation subclass, not the definition of the
research problem.

## Active Search and Active Learning

Active search chooses actions to find positives efficiently, and active learning
chooses examples to improve a model. Residual-potential resembles active search
because it prioritizes strata that may produce new evidence. Its role in this
paper is narrower. It is a repair instance inside a stop controller, used to test
whether weak but plausible source-route regions still contain residual evidence.

The controller is not optimized only for yield. A high-yield action can be
useful, but a completion decision must also ask whether the evidence supporting a
global stop claim was gathered under conditions broad enough for that claim.
This is why the paper treats residual-potential as mechanism-aligned repair, not
as a new optimal active-search algorithm.

## Missing Mass and Unseen Evidence

Missing-mass and unseen-species methods estimate how much probability mass
remains unseen after sampling. False stopping under unknown workload is
conceptually related, but our object is not a scalar hidden-mass estimate. The
object is the runtime evidence condition: where the workflow searched, which
routes it applied, and whether the stop evidence is local or broad relative to
the intended workload scope.

A workflow can have many observations and still be localized if those
observations come from a small subset of source-route strata. Conversely, broad
exposure does not prove completion when repair continues to find residual
evidence. This is the eligibility/safety separation used by the controller.

## Agent False Completion

Recent agent systems can prematurely report that a task is done, especially in
long-horizon workflows with tool calls, decomposition, and self-monitoring. This
paper studies one mechanism behind that failure: local stop evidence is promoted
into a global completion certificate. The contribution is not only to observe
that agents can stop too early, but to formalize the mismatch between the scope
of the stop claim and the source-route condition under which supporting evidence
was produced.

Under this view, no-new findings, agreement, and self-reported completion are
not discarded. They are treated as conditioned evidence. The question becomes:
conditioned on what?

## Dynamic Agent Workflows

Dynamic workflows allocate work across agents, tools, routes, and intermediate
states. Many such systems are designed around decomposition, planning,
verification, and iterative search. Our setting focuses on the stopping decision
inside such workflows. The workflow may adaptively gather evidence, but it must
eventually decide whether the evidence supports task completion.

Evidence-condition geometry is complementary to workflow orchestration. It does
not prescribe a planner, prompt template, or tool-use policy. It provides a
runtime diagnostic for whether the current evidence log can support a completion
claim.

## Deep Research Completeness

Deep research and report-generation agents often face an implicit completeness
problem: after searching, reading, summarizing, and reconciling sources, the
system must decide whether the answer is complete enough. Existing systems often
rely on heuristic stop signals such as stable summaries, no-new search results,
or self-evaluated confidence.

The evidence-condition view gives a sharper failure mode. A research agent may
have thoroughly exhausted one source family or query route while leaving another
route underexplored, such as contradiction search, temporal qualification, or
scope-boundary audit. Stable output under one route does not certify completion
over all intended routes. The claim-verification pilot is a natural future
validation for this broader setting.

## Multi-Agent Collapse and Diversity

Work on multi-agent collapse, correlated failures, and diversity often studies
whether agents converge to similar outputs, traces, or representations. Our
diagnostic is different. It records where and how the workflow searched. Agents
may agree because the task is complete, or because they repeatedly examined the
same local source-route region. Source-route exposure makes that distinction
observable.

This paper therefore does not claim to solve multi-agent collapse in general. It
diagnoses one completion-decision failure mode that can arise from correlated or
localized agent work: the agreement signal is global in wording but local in its
evidence condition.

## Audit Agents and Verification Agents

Audit and verification agents add checks after or during generation. They can
detect errors, validate outputs, or improve answer quality. The repair step in
our controller is related, but it is not a generic post-hoc auditor. It is
directed by the evidence condition and invoked specifically to decide whether a
stop claim can be certified.

The audit target is a weak but runtime-plausible source-route stratum, not an
unrestricted request for another agent to review the answer. This makes the
controller's behavior inspectable: it rejects local certificates, repairs weak
regions, and accepts `SAFE` only when exposure is broad and repair finds no
residual evidence.

## Boundary Statement

The paper should be positioned as:

```text
evidence-condition geometry and controller for dynamic agent completion decisions.
```

It should not be positioned as:

```text
a new optimal active-search method;
a total-recall algorithm;
a universal proof of task completion;
a generic multi-agent diversity metric.
```
