# Formulation and Method v0

## Problem Formulation

We study workload-unknown dynamic agent workflows. A workflow receives a task, decomposes it into routed work, gathers partial evidence under a finite budget, and must decide whether the task is complete.

The object is not ordinary question answering. The difficult decision is not only what answer to produce, but whether the evidence collected so far is sufficient to certify completion.

Let a workflow produce runtime evidence events:

```text
e_1, e_2, ..., e_t
```

Each event is associated with a source and a route. A source is a bounded evidence region, such as a file, module, document, or source family. A route is the way the workflow queried or audited that source, such as timeout audit, TLS audit, exception audit, policy-exception audit, or compatibility audit.

A proposed stop is a claim:

```text
the task is complete over the intended workload scope.
```

The core failure is certificate mismatch:

```text
local evidence condition -> global completion certificate
```

No-new findings, agreement, self-reported completion, and stable summaries are not globally valid by default. They are valid only under the evidence condition that produced them.

## Evidence-Condition Geometry

Define a source-route stratum:

```text
s = (source, route)
```

Let `v_t(s)` be the runtime-visible exposure count in stratum `s` up to time `t`: visits, scans, tool calls, or audit actions. The exposure distribution is:

```text
p_exp(t, s) = v_t(s) / sum_s v_t(s)
```

This is a point on the source-route coverage simplex. It describes where the completion evidence came from.

High localization means the evidence condition is narrow. A narrow evidence condition can certify local exhaustion, but it should not be accepted as a global completion certificate.

The controller uses two simple diagnostics already used in the experiments:

```text
support ratio = |{s : v_t(s) > 0}| / |S|
exposure Gini = Gini({v_t(s) : s in S})
```

These are not new theoretical objects. They are operational summaries of the same exposure distribution.

## Controller Algorithm

At a proposed stop:

1. Compute the source-route exposure distribution.
2. Check whether the evidence condition is broad enough for the claimed completion scope.
3. If the condition is too localized, reject `SAFE`.
4. Run evidence-condition repair on weak but runtime-plausible source-route strata.
5. Decide `SAFE`, `CONTINUE`, or `ABSTAIN`.

Decision semantics:

```text
SAFE:
  evidence condition is broad enough, weak plausible gaps are absent,
  and repair/audit reveals no residual evidence.

CONTINUE:
  evidence condition is too narrow, or repair/audit finds new evidence.

ABSTAIN:
  budget is exhausted while the evidence condition remains insufficient.
```

## Repair Instance

The instantiated repair rule is residual-potential:

```text
priority(s) = under_exposure(s) x runtime_computable_potential(s)
```

`under_exposure(s)` targets weak parts of the current completion certificate. `runtime_computable_potential(s)` prevents spending repair budget on visibly irrelevant strata.

Potential must use only runtime-visible information such as source text, route names, route match counts, source size, or non-oracle ledger signals. It must not use oracle labels, oracle totals, missing mass, undiscovered true items, post-hoc recall, or scorer-visible target distributions.

Residual-potential is not claimed to be optimal. It is a mechanism-aligned instance of evidence-condition repair.

## Experimental Protocol

Tasks:

- `policy_docset_v1`: generated bounded policy document task.
- `code_repo_v1`: generated bounded code repo task.
- `requests`: external real repo with pattern-defined oracle.
- `urllib3`: second external real repo completion audit.

Conditions:

- homogeneous route reuse;
- route-partitioned audit;
- extended or near-complete audit where available.

Challengers:

- random;
- low-exposure;
- high-potential;
- residual-potential;
- free-search continuation.

Primary evaluation:

- false certification;
- controller decision: `SAFE`, `CONTINUE`, `ABSTAIN`;
- support expansion;
- support gap reduction;
- cost-normalized new evidence.

Recall is used for scoring bounded subclasses, but the paper should not define the problem as item discovery.
