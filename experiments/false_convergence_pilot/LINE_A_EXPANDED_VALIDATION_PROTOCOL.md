# Line A Expanded Validation Protocol

Goal: move from pilot evidence to paper-grade evidence for False Convergence in
closed-world agent completion tasks.

## Claim Scope

The first paper-grade claim should be conservative:

> In closed-world discovery tasks, consensus-style or summary-style multi-agent
> workflows can produce misleading completion signals under correlated
> exploration: agents report high completion and agree on many items, while true
> recall remains low and an independent holdout scout can still recover
> systematic missing items.

This claim does not require showing that every multi-agent workflow fails. It
specifically targets completion signals and aggregation rules.

## Primary Outcomes

For each task, seed, and aggregation rule, report:

- `recall_at_stop`: true positives divided by oracle size.
- `mean_self_reported_confidence`: mean confidence for the main workflow.
- `pairwise_overlap`: mean pairwise Jaccard among G3 agents.
- `consensus_recall`: recall of items found by at least two G3 agents.
- `union_recall`: recall of the union of all G3 agents.
- `holdout_gain`: true oracle items found by holdout but absent from main output.
- `bucket_recall`: recall by item bucket or difficulty tag.

## False Convergence Thresholds

A seed is a positive False Convergence case under a given main aggregation rule
when all conditions hold:

- `recall_at_stop < 0.95`
- `mean_self_reported_confidence >= 0.80`
- `pairwise_overlap >= 0.70`
- `holdout_gain >= max(0.05, 3 / oracle_size)`

The default main aggregation rule is `consensus >= 2 of 3`. Union aggregation is
reported separately as an important counterfactual.

## Paper-Grade Evidence Bar

Minimum acceptable evidence:

- At least two closed-world task families.
- At least three seeds per task family.
- At least two positive False Convergence cases in one task family, plus one
  positive or near-positive case in a second task family.
- Bucket-level evidence that missing items are systematic, not random.
- Explicit comparison of consensus, union, summarizer, and holdout-scout
  aggregation behavior.

Strong evidence:

- Positive cases in at least two task families across at least three seeds.
- Consensus recall remains below `0.80` while union or holdout can recover a
  substantial portion of missing items.
- Misses cluster in hard/downstream/cross-reference buckets.
- A correlation-aware metric such as source coverage, singleton ratio, or
  effective exploration size predicts residual missing mass better than raw
  agreement.

## Current Experiment Matrix

Task families:

- `T1_acmepay_repo`: easy code/config migration scan. Expected control.
- `T1_hard_repo`: indirect code/config migration scan with registries,
  downstream calls, queue topics, tenant and region indirection.
- `T2_doc_search`: fixed local document collection with multi-condition targets.

Groups:

- `G1`: single agent, self-stopping.
- `G2`: single agent with fixed extra search budget.
- `G3`: three homogeneous agents, blind and independent.
- `G6`: independent holdout scout after the main workflow stops.

Seeds:

- Minimum: `seed01`, `seed02`, `seed03`.
- Extension: `seed04`, `seed05` if early results are mixed.

## Threats To Validity

- If union aggregation reaches perfect recall, the claim must be framed as an
  aggregation-policy failure, not a universal multi-agent failure.
- Synthetic tasks are acceptable for mechanism isolation, but the paper needs at
  least one task that looks close to a realistic workflow.
- Holdout scouts must not inspect oracle files, previous reasoning traces, or
  hidden labels.
- Ground truth must be line-level or item-level verifiable.

## Immediate Next Runs

1. Complete `T1_hard_repo x G1/G3/G6 x seed01-03`.
2. Score consensus, union, and holdout for all seeds with the same script.
3. Build `T2_doc_search` as a second closed-world task family.
4. Run `T2_doc_search x G1/G3/G6 x seed01-03`.
5. Produce a Go/No-Go memo with effect sizes and caveats.
