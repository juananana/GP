# Problem Essence Memo v1

## Purpose

This memo is not a new method proposal. It tries to identify the underlying problem before writing the paper.

The current risk is that we describe the project too narrowly as:

```text
find all matching items in a document/repository
```

That is only our evaluation carrier. The broader problem from dynamic workflows is:

```text
When can a dynamic multi-agent workflow justifiably claim that an unknown-workload task is complete?
```

## What The Dynamic Workflow Setting Really Includes

The motivating article includes many task families:

- flaky-test diagnosis until a hypothesis succeeds;
- mining repeated mistakes from sessions;
- finding repeated incident root causes;
- reviewing a business plan from multiple perspectives;
- ranking many resumes;
- naming and tournament selection;
- repository-wide refactors;
- technical-claim verification against a codebase;
- deep research and source checking;
- triage at scale;
- root-cause investigation.

These are not all "find every item" tasks.

The common structure is broader:

```text
large / unknown workload
+ decomposed or dynamically routed subtasks
+ multiple agents with partial contexts
+ a stopping decision based on observed progress
+ risk that local progress signals are mistaken for global completion
```

So the paper should not claim to solve all dynamic workflows, but the core phenomenon should be stated at this level.

## Candidate Essence A: Multi-Agent Outputs Are Correlated

This is true but not deep enough.

Correlated outputs explain why ensembling saturates, but they do not directly explain why the workflow declares completion. High agreement can be good or bad:

- good: independent agents converge after broad coverage;
- bad: agents repeat the same route and share a blind spot.

Therefore correlation is a symptom. It is not the essence.

## Candidate Essence B: Search Coverage Is Localized

This is closer and currently has empirical support.

Our blind tasks show:

- homogeneous workflows concentrate exposure and falsely stop;
- route-partitioned workflows reduce localization and recover more targets;
- source-only geometry is too coarse;
- source-route geometry is the useful level.

But "coverage localization" is still a descriptive mechanism. It says where the workflow searched. It does not fully explain why the workflow thinks it is done.

## Candidate Essence C: Completion Evidence Is Conditional, But Treated As Unconditional

This is the strongest current candidate for the real essence.

Dynamic workflows observe signals like:

- no new findings;
- high overlap between agents;
- self-reported completion;
- stable summaries;
- successful local verification;
- exhausted assigned subtasks.

These signals are always conditional on the explored region, route, prompt, tool, context, and budget.

The failure occurs when the workflow treats conditional evidence as an unconditional certificate:

```text
"No new findings under this exposure distribution"
is misread as
"No important work remains globally."
```

This explains why exposure localization matters:

```text
the more localized the exposure distribution is,
the narrower the condition under which no-new evidence is valid.
```

So the deeper failure law is not merely:

```text
localized exposure causes false stopping
```

but:

```text
false stopping is a certificate mismatch:
the workflow issues a global completion claim using evidence that is only locally conditioned.
```

## Why This Is More General Than Item Discovery

For item discovery:

```text
conditional no-new evidence => local exhaustion
global completion claim => all target items found
```

For debugging:

```text
conditional no-new evidence => no more failures under tried hypotheses/log slices
global completion claim => root cause found or ruled out
```

For claim verification:

```text
conditional no-new evidence => checked sources support/contradict known claims
global completion claim => all important claims are verified
```

For refactoring:

```text
conditional no-new evidence => no more call sites under searched patterns
global completion claim => migration is complete
```

The same mismatch appears across these tasks.

## Natural Geometry From The Essence

If evidence is conditional on exposure, then the runtime object must describe the condition.

That object is:

```text
p_exp(t) over source-route strata
```

This is not geometry for decoration. It is the shape of the evidence condition.

When `p_exp(t)` is concentrated near a few strata, the completion evidence is narrow. When it spreads across relevant strata, the evidence condition better supports a global claim.

Thus:

```text
coverage simplex geometry = geometry of completion evidence conditions
```

This is a better explanation than:

```text
we use Gini because it measures concentration
```

## Method Implication

If the essence is certificate mismatch, then the method should not be framed as "find more items."

The method should be framed as:

```text
repair the evidence condition before issuing a completion claim.
```

There are three possible actions:

1. **Reject stop**: if exposure evidence is too localized.
2. **Expand evidence**: run a challenger in under-supported but relevant regions.
3. **Abstain**: if budget is exhausted but evidence remains too local.

Residual-potential is one implementation of action 2:

```text
choose regions that are both under-supported and runtime-visible as promising.
```

But it should not be treated as the only possible repair.

## Why Current Method Feels Misaligned

The user's concern is valid.

Current mechanism:

```text
global completion was certified from local evidence
```

Current method:

```text
search low-exposure x high-potential strata
```

These are connected, but not identical.

The method becomes better aligned if we describe it as:

```text
evidence-condition repair
```

rather than:

```text
blind-spot search heuristic
```

Then residual-potential is not the theory itself. It is the current operational repair rule.

## What Would Make The Paper Deep

A deeper paper should show three things:

1. **Evidence condition law**

   Completion signals are only reliable relative to the exposure distribution that produced them.

2. **Geometric diagnostic**

   Source-route exposure localization quantifies how narrow that condition is.

3. **Repair principle**

   Before stopping, the workflow must either broaden the evidence condition, prove that low-exposure regions are low-risk, or abstain.

This is closer to the Jiaxin-style pattern:

```text
engineering anomaly
=> natural object
=> low-dimensional diagnostic
=> predictive law
=> method as consequence
```

## Revised One-Sentence Thesis

```text
Dynamic multi-agent workflows fail to stop safely when they convert locally conditioned progress evidence into a global completion certificate; source-route exposure geometry makes this certificate mismatch observable and gives a principled basis for residual evidence repair.
```

## Immediate Research Consequence

Do not narrow the paper to "find all matching items."

Use bounded high-recall discovery as the measurable experimental setting, but define the research problem as:

```text
safe stopping for hidden-workload dynamic multi-agent workflows
```

Do not overclaim residual-potential.

Say:

```text
residual-potential is our first evidence-condition repair rule.
```

not:

```text
residual-potential is the unique optimal solution.
```

