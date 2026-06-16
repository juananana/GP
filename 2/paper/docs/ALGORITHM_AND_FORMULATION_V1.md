# Algorithm and Formulation v1

This file replaces the memo-style formulation and method description with a
paper-ready problem statement, geometry proposition, and Algorithm 1. It keeps
the core variables fixed: source-route strata, exposure distribution, support
ratio, exposure Gini, and the evidence-condition controller.

## Problem Setting

We study workload-unknown dynamic agent workflows that must decide whether a
task is complete under partial, routed, and budgeted evidence. A workflow is

```text
W = (T, S, R, A, B),
```

where `T` is the task, `S` is a set of sources, `R` is a set of routes, `A` is
the set of agents or tools, and `B` is a finite budget. A source is a bounded
evidence region such as a file, module, document, repository component, or source
family. A route is an audit or search lens applied to a source, such as timeout
audit, TLS audit, exception audit, policy-exception audit, compatibility audit,
or cleanup audit.

At runtime, the workflow emits evidence events

```text
e_t = (agent_t, source_t, route_t, action_t, observation_t, cost_t).
```

The key distinction is that evidence is not unconditioned. Each event is
produced under a source-route condition. A source-route stratum is

```text
s = (source, route),
```

and the intended evidence-condition space is

```text
Omega = S x R.
```

The source-route space does not require the workflow to know all true missing
items in advance. It requires the intended audit scope to be defined: which
sources and routes are relevant to the completion claim. Oracle labels, when
available, are used only for evaluation after trajectories and challenger
choices are fixed.

## Stop Claim and False Certification

A stop claim is a workflow assertion

```text
C_t: task T is complete over the intended workload scope.
```

Signals such as no-new findings, agent agreement, stable summaries, and
self-reported completion are evidence for `C_t` only under the source-route
conditions that produced them.

A false certification occurs when the workflow accepts `SAFE` for a stop claim
that is not supported by the evaluation oracle:

```text
SAFE(C_t) = true, but completion(T) = false.
```

In item-discovery subclasses, this is operationalized as accepting `SAFE` while
bounded-oracle recall is below the completion threshold. In broader completion
audits, it means accepting a global completion claim while relevant support,
contradiction, or unresolved evidence remains outside the evidence condition.

## Evidence-Condition Geometry

Let `v_t(s)` be the runtime-visible exposure count for source-route stratum `s`
up to time `t`. Exposure may count visits, scans, route-specific audits, tool
calls, or other logged search actions. The exposure distribution is

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

These summaries are operational diagnostics, not new core variables and not
universal laws. They summarize whether the evidence condition is localized or
broad enough to make a completion certificate eligible for consideration.

## Proposition 1: Local No-New Evidence Is Not a Global Certificate

**Proposition.** Let `U` be a strict subset of the intended source-route space
`Omega`. Suppose all evidence used to support a stop claim `C_t` is produced
inside `U`, and suppose the workflow observes no-new evidence only for actions
inside `U`. Then the no-new evidence can support local exhaustion over `U`, but
it cannot by itself support global completion over `Omega`.

**Proof sketch.** No-new evidence is conditioned on the source-route actions that
were actually executed. If no events are produced in `Omega \ U`, the workflow
has not observed the absence of residual evidence in those unexposed strata. A
world in which `U` is exhausted and `Omega \ U` contains residual evidence is
observationally indistinguishable from a globally complete world under the
workflow's local evidence log. Therefore local no-new evidence rules out
additional findings only under the searched condition `U`; without additional
assumptions about the unsearched strata, it cannot rule out residual evidence in
`Omega \ U`.

**Implication.** The proposition does not claim that global completion is
impossible. It states that a local evidence condition is insufficient as a
certificate. A controller must inspect whether the evidence condition matches the
scope of the stop claim before accepting `SAFE`.

## Why Source-Route Is the Default Geometry

Source-only geometry is too coarse: auditing a file for timeout behavior does
not certify that TLS, retry, exception, or cleanup behavior has been audited in
that file. Source-route-action geometry is more detailed, but it is sensitive to
logging conventions and current experiments do not show a stable advantage over
source-route. Source-route is the default because it captures both where and how
evidence was produced while remaining interpretable and runtime-computable.

## Algorithm 1: Evidence-Condition Controller

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

## Notes on the Algorithm

The eligibility check is not a completion proof. It is only a test of whether the
evidence condition is broad enough for a global stop claim to be considered. A
`SAFE` decision additionally requires that repair or audit reveal no residual
evidence.

`ABSTAIN` is used when budget is exhausted and the workflow still lacks a
defensible completion certificate. This matters because a controller that only
outputs `CONTINUE` can avoid false certification trivially. The controller must
also distinguish cases where evidence has become broad and stable enough to
accept `SAFE`.

## Residual-Potential Repair Instance

The repair instance used in the experiments is

```text
priority(s) = under_exposure(s) x runtime_computable_potential(s).
```

`under_exposure(s)` prioritizes weak parts of the current completion certificate.
`runtime_computable_potential(s)` uses only visible runtime information, such as
source text, route names, source size, route match counts, or non-oracle ledger
signals.

Forbidden information:

- oracle labels;
- oracle totals;
- oracle missing mass;
- undiscovered true item counts;
- post-hoc recall;
- scorer-visible target distributions.

Residual-potential is a mechanism-aligned repair instance, not an optimal active
search algorithm and not the main theoretical contribution.
