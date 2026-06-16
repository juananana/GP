# Paper Draft Body v0

## 2. Problem Formulation

We study workload-unknown dynamic agent workflows. A workflow is a runtime procedure that receives a task, allocates work across agents or tool calls, gathers evidence under finite budget, and must decide whether the task is complete. The workload is unknown because the workflow does not know in advance how much relevant evidence exists or which source-route conditions are required to support a completion claim.

This setting is broader than item discovery. Item discovery is useful for evaluation because it provides bounded oracle labels, but the target decision is completion certification: whether the workflow has enough evidence to stop.

### Workflow

Let a workflow be:

```text
W = (T, S, R, A, B)
```

where `T` is the task, `S` is a set of sources, `R` is a set of routes, `A` is the set of agents or tools, and `B` is a finite budget. A source is a bounded evidence region, such as a file, module, document, source family, or repository component. A route is an audit or search lens applied to a source, such as timeout audit, TLS audit, exception audit, policy-exception audit, compatibility audit, or cleanup audit.

### Evidence Event

At runtime, the workflow produces evidence events:

```text
e_t = (agent_t, source_t, route_t, action_t, observation_t, cost_t)
```

The event may be a search, scan, extraction, verification, summary, or stop proposal. The key point is that evidence is not unconditioned. Every evidence event is produced under a source-route condition.

### Source-Route Stratum

A source-route stratum is:

```text
s = (source, route)
```

The set of strata is:

```text
Omega = S x R
```

The source-route stratum records where and how evidence was produced. This is the default geometry in the paper.

### Stop Claim

A stop claim is a workflow assertion:

```text
C_t: task T is complete over the intended workload scope.
```

Signals such as no-new findings, agent agreement, self-reported completion, stable summaries, or exhausted assigned subtasks are evidence for `C_t` only under the source-route conditions that produced them.

### False Certification

A false certification occurs when the workflow accepts `SAFE` for a stop claim that is not supported by the bounded evaluation oracle:

```text
SAFE(C_t) = true, but task completion is false under evaluation.
```

In item-discovery subclasses, we operationalize this as accepting `SAFE` while recall is below the chosen completion threshold. In broader completion-audit settings, false certification means accepting a global completion claim while relevant support, contradiction, or unresolved evidence remains outside the evidence condition.

### Decisions

The controller outputs one of three decisions:

```text
SAFE:
  the evidence condition is broad enough, weak plausible gaps are absent,
  and repair/audit reveals no residual evidence.

CONTINUE:
  the evidence condition is too narrow, or repair/audit reveals new evidence.

ABSTAIN:
  the budget is exhausted and the workflow still lacks a defensible completion certificate.
```

The controller does not treat broad exposure alone as sufficient for `SAFE`. Broad exposure gives completion eligibility; `SAFE` additionally requires no residual evidence after repair or audit.

## 3. Evidence-Condition Geometry

### Exposure Distribution

Let `v_t(s)` be the runtime-visible exposure count for source-route stratum `s` up to time `t`. Exposure can be visits, scans, tool calls, route-specific audits, or other logged search actions. Define:

```text
p_exp(t, s) = v_t(s) / sum_{s' in Omega} v_t(s')
```

This distribution is a point on the source-route coverage simplex. It describes the condition under which completion evidence was produced.

### Localization

When `p_exp(t, s)` is concentrated on a small subset of strata, no-new or agreement evidence is locally conditioned. It may certify local exhaustion, but it does not certify global completion.

We summarize this distribution with two operational quantities:

```text
support_ratio(t) = |{s : v_t(s) > 0}| / |Omega|
G_exp(t) = Gini({v_t(s) : s in Omega})
```

These are summaries of the exposure distribution, not new core variables. They are used to decide whether the evidence condition is broad enough for the stop claim.

### Why Source-Route

Source-only geometry is too coarse because it collapses routes inside a source. Auditing a file for timeout behavior does not certify that TLS, retry, exception, or cleanup behavior has been audited in that file.

Source-route-action geometry is more detailed, but it is not the main geometry here. It is sensitive to logging conventions and current experiments do not show a stable advantage over source-route. We use source-route as the default because it captures both where and how evidence was produced while remaining interpretable and runtime-computable.

## 4. Evidence-Condition Controller

At a proposed stop, the controller checks whether the current evidence condition can support the stop claim.

### Algorithm

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

The controller is intentionally conservative. It does not infer completion merely from confidence, agreement, or no-new evidence.

### Repair Instance: Residual-Potential

The repair instance used in the experiments is:

```text
priority(s) = under_exposure(s) x runtime_computable_potential(s)
```

`under_exposure(s)` gives priority to weak parts of the current completion certificate. `runtime_computable_potential(s)` uses only visible runtime information, such as source text, route names, source size, route match counts, or non-oracle ledger signals.

Forbidden information:

- oracle labels;
- oracle totals;
- oracle missing mass;
- undiscovered true item counts;
- post-hoc recall;
- scorer-visible target distributions.

Residual-potential is a mechanism-aligned repair instance. We do not claim it is optimal.

## 5. Experimental Protocol

### Tasks

We evaluate on four task families:

- `policy_docset_v1`: generated bounded policy document task.
- `code_repo_v1`: generated bounded code repository task.
- `requests`: external real repository audit with pattern-defined oracle.
- `urllib3`: second external real repository completion audit.

The generated tasks are controlled scored subclasses. The external tasks are stronger evidence for runtime geometry, but their oracles are still pattern-defined rather than fully human annotated.

### Conditions

We compare:

- homogeneous route reuse;
- route-partitioned audit;
- extended or near-complete audit where available.

Homogeneous conditions test whether repeated local evidence can produce unsafe stop claims. Route-partitioned and extended conditions test whether broader source-route exposure improves completion eligibility.

### Challengers

We compare:

- random;
- low-exposure;
- high-potential;
- residual-potential;
- free-search continuation.

Challengers are evaluated as evidence-condition repair mechanisms, not as standalone item-finding algorithms.

### Metrics

Primary metrics:

- false certification;
- controller decision: `SAFE`, `CONTINUE`, `ABSTAIN`;
- support ratio;
- exposure Gini;
- repair gain;
- cost-normalized evidence;
- overlap between high-potential and residual-potential.

Recall is reported for scored subclasses, but recall is not the definition of the research problem.

## 6. Results Summary

Across all four tasks, homogeneous route reuse produces localized evidence conditions and would cause false certification if accepted as `SAFE`.

Broad exposure improves completion eligibility. In `policy_docset_v1`, `code_repo_v1`, and `requests`, route-partitioned evidence reaches the completion threshold and the controller outputs `SAFE`. In `urllib3`, route-partitioned evidence is geometry-eligible but still incomplete; the controller correctly outputs `CONTINUE`. This is the key boundary result:

```text
broad exposure is completion eligibility, not a sufficient condition for SAFE.
```

Residual-potential has positive repair evidence but remains bounded as a method claim. It ties high-potential exactly on `requests`, where both select identical strata. It has higher total repair gain on `urllib3`, but high-potential has similar cost-normalized evidence. The paper should present residual-potential as a mechanism-aligned repair instance, not as an optimal algorithm.

## 7. Limitations

The external oracles are pattern-defined. A human-annotated completion-audit benchmark would be stronger. The claim-verification setting remains a planned extension. Residual-potential is not proven optimal, and stronger repair rules may exist.
