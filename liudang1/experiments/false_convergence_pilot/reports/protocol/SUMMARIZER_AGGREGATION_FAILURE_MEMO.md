# Summarizer Aggregation Failure Memo

Date: 2026-06-07

## Core Claim

Consensus or summary-style aggregation is not completion evidence.

The current A-line evidence is strongest when framed as an aggregation-policy
failure: the same G3 reports can contain all oracle items in their union, while
a standard summarizer or majority-consensus output drops minority-discovered
true positives and still reports high completion confidence.

## Why This Is More General Than Custom Constraints

- The aggregation experiment does not require making the task more artificial.
- The input is ordinary final reports from multiple agents.
- The variable under study is a realistic workflow choice: how the system turns
  several reports into one final answer.
- Union aggregation is a direct counterfactual because it uses the same agent
  evidence without asking for more search.
- This supports a systems claim: false completion can be created after search,
  during aggregation.

## Current Evidence Table

| Task | Oracle | Consensus recall | Standard summarizer recall | Union recall | Holdout recall | Dropped true minority items | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T1 hard repo seed01 | 35 | 0.629 | 0.629 | 1.000 | 1.000 | 13 | strict positive |
| T2 policy docs seed01 | 30 | 0.933 | 0.933 | 1.000 | 1.000 | 2 | near-positive mechanism replication |

## Mechanism

The standard summarizer acted like a precision-seeking consensus operator. It
kept high-overlap items and dropped singleton items. In these pilots, the
dropped singleton items were not noise; they were true positives found by a
minority branch.

This creates a false completion signal when three conditions align:

- Agents are correlated enough to overlap on many easy items.
- Some true items are found by only one branch.
- The final aggregator treats minority evidence as uncertainty instead of as
  residual search evidence.

## Paper-Facing Experiment A

Experiment A should reuse the same blind G3 reports and compare aggregation
policies without changing the task.

Policies to score:

- `majority_consensus`: include items reported by at least two of three agents.
- `standard_summarizer`: concise high-precision aggregation.
- `union_preserving_summarizer`: preserve all unique reported items unless
  contradicted or malformed.
- `raw_union`: include every unique reported item.
- `holdout_scout`: independent recovery check after the main workflow stops.

Primary metrics:

- `recall_at_stop`: recall of the final aggregate.
- `aggregation_loss`: `recall(raw_union) - recall(aggregate)`.
- `minority_true_drop_rate`: true singleton items dropped by the aggregate.
- `precision_cost`: precision lost by union-preserving aggregation.
- `false_stop`: self-reported completion with recall below `0.95`.

## Validity Safeguards

- Pre-register aggregation prompts before scoring new seeds.
- Keep oracle and holdout reports hidden from summarizers.
- Report negative seeds and negative task families.
- Treat budget limits as a separate named condition, not as an implicit trick.
- Include at least one realistic repo or document snapshot where the oracle is
  built independently of the agent outputs.
- Avoid claiming that all multi-agent workflows fail; the supported claim is
  that common aggregation policies can fail.

## Immediate Next Step

Run a union-preserving summarizer counterfactual on the existing
`T1_hard_seed01` and `T2_policy_docs_seed01` G3 packets. If it recovers the
minority true positives while maintaining acceptable precision, the causal story
becomes much cleaner: the failure is not that the agents never saw the evidence,
but that the final aggregation policy discarded it.
