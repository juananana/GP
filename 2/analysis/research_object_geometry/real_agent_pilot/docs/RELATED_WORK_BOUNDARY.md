# Related Work Boundary

This is not a full related work section. It records the boundary that the eventual paper should maintain.

## TAR / Total Recall

Technology-assisted review and total-recall work studies how to retrieve nearly all relevant items under labeling and review budgets. This is adjacent because our scored subclasses use recall-like evaluation.

Boundary:

```text
We do not primarily study item retrieval policy. We study whether a dynamic workflow may certify completion from locally conditioned evidence.
```

Item discovery is an evaluation subclass, not the definition of the problem.

## Missing Mass and Unseen Species

Missing-mass estimation asks how much probability mass remains unseen after sampling. This is conceptually adjacent to false stopping under incomplete coverage.

Boundary:

```text
We do not estimate a scalar hidden mass from samples. We diagnose whether completion evidence was produced under source-route conditions broad enough to support a stop claim.
```

The object is the evidence condition, represented by source-route exposure geometry.

## Active Search and Active Learning

Active search chooses where to sample next to find positives efficiently. Active learning chooses examples to label in order to improve a model.

Boundary:

```text
Our controller is not optimized only for yield. It decides whether completion evidence is certifiable, whether to continue, or whether to abstain.
```

Residual-potential may resemble active search, but its role here is evidence-condition repair.

## Multi-Agent Collapse and Diversity

Work on multi-agent collapse, correlated failures, or lack of diversity studies how agents converge to similar outputs or shared blind spots.

Boundary:

```text
We give a runtime geometric diagnostic for when correlated work produces only local completion evidence.
```

The source-route exposure distribution makes the condition of agreement observable.

## Agent False Completion

Agent false completion covers cases where agents prematurely report that a task is done. This is the closest practical failure mode.

Boundary:

```text
We formalize false completion as certificate mismatch: the evidence condition is local while the completion claim is global.
```

This shifts the question from "did the agent miss something?" to "under what conditions was the stop evidence produced?"

## Audit Agents and Verification Agents

Audit-agent work uses additional agents or tools to check outputs, detect errors, or improve reliability.

Boundary:

```text
Our repair step is not a generic auditor. It is directed by the source-route evidence condition and targets weak but runtime-plausible strata.
```

The audit is part of a stop controller, not merely a post-hoc quality check.

## Positioning

The paper should be positioned as:

```text
evidence-condition geometry and controller for dynamic agent completion decisions.
```

Residual-potential is a repair instance within this controller. It should not be presented as the main theoretical contribution or as an optimal active-search algorithm.
