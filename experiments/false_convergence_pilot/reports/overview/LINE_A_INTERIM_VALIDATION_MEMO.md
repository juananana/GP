# Line A Interim Validation Memo

Date: 2026-06-07

## Executive Decision

Line A should continue, but the current evidence is not yet paper-grade proof.

The strongest current claim is:

> False Convergence appears under consensus-style aggregation in at least one
> code task seed, and a near-positive instance appears in a document-search task.
> In both cases, union aggregation or a holdout scout can recover items that the
> consensus output drops.

The current evidence is enough to justify the paper direction. It is not enough
to claim stable existence across tasks and seeds.

Update after standard summarizer aggregation:

- The strongest paper direction is now aggregation-policy failure, not further
  synthetic task hardening.
- Standard summarizers reproduced the consensus-style loss pattern on both the
  strict-positive code seed and the near-positive document seed.
- This is a more general claim because it changes the aggregation policy over
  the same agent reports, rather than adding task-specific constraints.

## Latest Status Update CN

这份 memo 是中期记录，下面的部分保留了当时的判断。最新状态已经前进一格：

- T1 hard seed01/02/03 已补齐。seed01 是严格 aggregation-loss 阳性；seed02/03 是阴性或 precision-cost 样本，说明 union-preserving 不是无成本策略。
- T2 policy docs seed01/02/03 已补齐。seed01 是 near-positive aggregation-loss 样本；seed02/03 稳定复现 common blind spot：三个 G3 完全一致地漏掉 `CASE-047/048`，holdout 能恢复到 `30/30`。
- T2 仍不是 strict positive，因为 holdout gain 是 `2/30 = 0.067`，低于 `gamma = 0.100`；但它已经是稳定的“高一致不等于完成”证据。
- 当前更稳的论文主张是：completion signal 同时依赖搜索覆盖和聚合策略。Consensus 不是 completion，union-preserving 也不是万能药；关键是显式建模 singleton 是 missing mass 还是 noise。

## Evidence Status

### T1 AcmePay Easy Repo

Status: control / smoke test.

Result:

- G3 union recall: `1.000`
- Mean pairwise Jaccard: `0.961`
- Holdout gain beyond union: `0.000`

Interpretation:

- This task does not demonstrate False Convergence.
- It validates the blind-task pipeline and scoring process.

### T1 Hard Repo

Status: mixed.

Seed01 result:

- Mean confidence: `0.853`
- Mean pairwise Jaccard: `0.752`
- Consensus recall: `0.629`
- Union recall: `1.000`
- Holdout recall: `1.000`
- Holdout gain over consensus: `0.371`
- False Convergence under consensus threshold: `true`

Seed02 result:

- Mean confidence: `0.907`
- Mean pairwise Jaccard: `0.932`
- Consensus recall: `1.000`
- Union recall: `1.000`
- False Convergence: not present

Seed03 partial result:

- G1 found all 35 oracle items.
- One G3 agent found all 35 oracle items plus 5 non-oracle candidates.
- The seed is incomplete and should not be counted as a G3 aggregate.

Interpretation:

- T1-hard gives one strict positive seed and at least one clear negative seed.
- Therefore T1-hard is a useful mechanism probe, not a stable proof task.
- The key mechanism is aggregation-policy dependent: consensus can fail while
  union succeeds.

### T2 Policy Docs v1

Status: near-positive document task.

Result:

- Oracle size: `30`
- G1 recall: `28/30 = 0.933`, confidence `0.880`
- G3 mean confidence: `0.887`
- G3 mean pairwise Jaccard: `0.956`
- G3 consensus recall: `28/30 = 0.933`
- G3 union recall: `30/30 = 1.000`
- Holdout recall: `30/30 = 1.000`
- Holdout gain over consensus: `2/30 = 0.067`
- Threshold gamma: `max(0.05, 3/30) = 0.100`
- False Convergence under preregistered threshold: `false`

Interpretation:

- T2 v1 reproduces the same mechanism as T1 seed01:
  two agents miss boundary items, one agent and holdout recover them.
- It is not a strict positive because the holdout gain is two items, below the
  preregistered minimum of three items.
- The missed items are systematic: `CASE-047` and `CASE-048`, both
  service-name/flow-mismatch cases that still satisfy the formal rule.

### T2 Policy Docs v2

Status: negative G1 difficulty probe.

Result:

- Oracle size: `38`
- G1 found `38/38`, confidence `0.860`

Interpretation:

- Simply adding more boundary items does not reliably increase difficulty.
- Once the agent applies the formal rule systematically, it can solve the task.
- Future tasks need to manipulate exploration structure, source partitioning,
  and aggregation, not just add more cases.

### T3 Partitioned Policy Docs

Status: negative G1 difficulty probe.

Result:

- Case count: `64`
- Oracle size: `45`
- G1 found `45/45`, confidence `0.980`

Interpretation:

- The task has the intended source partitions:
  case notes, service catalog, adapter registry, lane policy, and exception
  overrides.
- However, the documents are still structured enough that a single careful
  agent can solve the full task.
- It should not be expanded to G3/G6 in this version because the G1 probe shows
  no false-stop signal.

### T2 Partitioned v3

Status: negative G1 difficulty probe.

Result:

- Case count: `64`
- Oracle size: `45`
- Evidence surface: natural-language incident notes, changelog, appendix, and
  policy memos.
- Prompt condition: realistic audit budget and self-stop rule.
- G1 found `45/45`, confidence `0.930`

Interpretation:

- Natural-language evidence and budget/self-stop prompting were not sufficient
  to induce a false stop.
- The model still solved the task through targeted search.
- The next task version needs an enforceable access or logging constraint, not
  only a prompt-level budget suggestion.

### Standard Summarizer Aggregation

Status: positive mechanism replication for aggregation-policy failure.

Design:

- Input: final G3 reports only.
- Aggregator: standard high-precision summarizer.
- No task files, oracle files, holdout reports, or score summaries were exposed.
- No new search budget or task-hardness constraint was introduced.

T1 hard seed01 result:

- Oracle size: `35`
- Standard summarizer confidence: `0.860`
- Standard summarizer recall: `22/35 = 0.629`
- Standard summarizer precision: `1.000`
- Standard summarizer false-stop: `true`
- Consensus recall: `0.629`
- Union recall: `1.000`
- Holdout recall: `1.000`
- Dropped true singleton items: `13`

T2 policy docs seed01 result:

- Oracle size: `30`
- Standard summarizer confidence: `0.900`
- Standard summarizer recall: `28/30 = 0.933`
- Standard summarizer precision: `1.000`
- Standard summarizer false-stop: `true`
- Consensus recall: `0.933`
- Union recall: `1.000`
- Holdout recall: `1.000`
- Dropped true singleton items: `2`

Interpretation:

- The standard summarizer behaved like majority consensus rather than a
  union-preserving audit.
- It dropped minority-discovered true positives in both a code task and a
  document task.
- This supports the Line A framing: consensus and summarization are not
  completion evidence.
- The result does not prove universal failure; it proves that a natural
  aggregation policy can convert minority evidence into a false completion
  signal.

## What Current Results Can Support

Current results support these claims:

- The experimental pipeline works across code and document tasks.
- Consensus aggregation can hide minority-discovered true positives.
- Standard summarization can reproduce the same loss pattern without an
  explicit majority-vote rule.
- High confidence and high overlap are insufficient completion evidence.
- Union aggregation is an important counterfactual and can avoid the observed
  failure in these pilots.
- Missing items are not random; they cluster in downstream or boundary-rule
  buckets.

Current results do not support these claims yet:

- False Convergence is stable across seeds.
- False Convergence appears across two task families under the preregistered
  threshold.
- All multi-agent workflows fail.
- Union aggregation fails in these tasks.

## Main Lesson

The paper should not be framed as:

> Multi-agent systems miss things.

It should be framed as:

> Completion signals in correlated agent workflows are aggregation-policy
> dependent. Consensus can convert shared blind spots into a false completion
> signal, while a minority branch or holdout scout may still contain the missing
> mass.

## Next Strict Validation Design

The next validation step should prioritize aggregation-policy comparisons over
new task-specific difficulty constraints.

For each existing and future G3 packet, score these aggregation policies:

- `majority_consensus`: include items reported by at least two of three agents.
- `standard_summarizer`: ask for a concise high-precision final answer.
- `union_preserving_summarizer`: preserve every unique reported item unless it
  is explicitly contradicted or malformed.
- `raw_union`: include every unique reported item.
- `holdout_scout`: compare missing mass recoverable by an independent scout.

Primary effect sizes:

- `aggregation_loss = recall(raw_union) - recall(aggregation_output)`.
- `minority_true_drop_rate`: true singleton items dropped by the aggregator.
- `false_stop`: self-reported completion with recall below `0.95`.
- `precision_cost`: precision drop introduced by union-preserving aggregation.

Minimum next run:

- Run a union-preserving summarizer counterfactual for `T1_hard_seed01` and
  `T2_policy_docs_seed01`.
- Reuse the same G3 packets; do not expose oracle or holdout outputs.
- If union-preserving summarization recovers the dropped items with acceptable
  precision, the causal variable is aggregation policy, not task impossibility.
- Then repeat across new seeds and at least one less synthetic task family.

## Go / No-Go

Decision: `Go for Line A, No-Go for paper-grade proof yet`.

Reason:

- We have one strict positive and one near-positive across two task families.
- We also have negative controls showing the phenomenon is not automatic.
- The next milestone is stable replication, not conceptual expansion.

## Update After T3

The T3 and T2-partitioned probes show that simply adding natural-language
surface variation is not enough. The next version should avoid overfitting the
task to the desired failure and instead treat search constraints as an explicit
experimental factor.

- Do not prioritize more hand-crafted boundary cases unless they are needed for
  a specific ablation.
- Prefer aggregation-policy ablations on the same agent reports.
- If budgets are studied, make them a named condition rather than a hidden
  source of difficulty.
- Add at least one realistic document or repo snapshot where the oracle is
  constructed independently of the model runs.

After `T2_partitioned_v3`, the most important change is to make the budget
enforceable:

- Provide agents with source partitions rather than the whole directory.
- Log every opened file or search query.
- Stop after a fixed number of source reads for G1/G3, then compare with G2
  fixed-extra-budget and G6 holdout.
- Alternatively, use a larger real-world document snapshot where exhaustive
  targeted search is no longer cheap.
