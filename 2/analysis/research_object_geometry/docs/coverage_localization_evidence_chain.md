# Coverage Localization Evidence Chain

This note answers four questions:

1. How was the geometry quantity discovered?
2. What evidence currently supports its existence?
3. What would a proof or theoretical explanation look like?
4. How can it be implemented as a residual coverage challenger?

The answer is deliberately conservative. The current evidence supports
**coverage localization**, not a Grassmann phase-transition theory.

## 1. How The Quantity Was Discovered

The starting failure mode is dynamic multi-agent false stopping:

```text
agents stop because no new items are observed,
but oracle evaluation shows hidden valid items remain.
```

The first hypothesis was broad:

```text
some coverage geometry controls false stopping
```

We tested candidate quantities in a controlled closed-world simulation:

- source-route coverage ratio;
- coverage entropy;
- coverage HHI/Gini;
- effective rank of the agent-by-stratum matrix;
- log-det volume;
- pairwise route overlap;
- scout residual novelty.

The discovery was empirical and comparative, not assumed in advance.

Result from `controlled_geometry_simulation.py`:

| metric | AUROC, best direction |
|---|---:|
| coverage_gini | 0.943 |
| source_coverage_ratio | 0.805 |
| source_logdet_volume | 0.759 |
| pairwise_route_jaccard | 0.727 |
| source_normalized_effective_rank | 0.653 |

Then we tested a more "order-parameter-like" compound quantity:

```text
lambda = coverage_gini * (1 - source_coverage_ratio)
```

Result from `controlled_geometry_simulation_v2.py`:

| metric | AUROC, best direction |
|---|---:|
| coverage_gini | 0.995 |
| source_normalized_effective_rank | 0.897 |
| coverage_risk_lambda | 0.831 |
| source_coverage_ratio | 0.830 |

This is a useful negative result:

> The compound lambda does not beat plain coverage Gini.

Therefore the current geometry quantity should remain:

```text
coverage localization = concentration of discovered evidence over source-route strata
```

rather than a more complicated formula.

## 2. What "Existence" Means Here

We should not say we have proven a universal law. What we can currently say is:

> In a controlled stratified discovery model where agents explore correlated
> easy regions and stop after local novelty exhaustion, coverage localization is
> a stable predictive signal for false stopping.

The existence evidence has three parts.

### 2.1 Label Balance

The controlled simulation creates both false and safe states:

```text
false completion: 2484
safe/non-false: 1116
```

This fixes the key limitation of archived historical logs, which had only false
states at high-recall thresholds.

### 2.2 Predictive Strength

Coverage Gini predicts false stopping better than the other tested quantities.
Effective rank and log-det are informative but weaker.

Interpretation:

```text
advanced subspace geometry is not currently the core.
source-route evidence localization is.
```

### 2.3 Cross-World Stability

Coverage Gini remains predictive across worlds with different numbers of
strata:

| n_strata | coverage_gini AUROC |
|---:|---:|
| 18 | 0.997 |
| 30 | 0.972 |
| 42 | 0.956 |

This is the first hint of a normalized control variable. It is not yet a proof,
but it is the right kind of evidence to motivate real-agent experiments.

## 3. Why It Makes Mechanistic Sense

Dynamic workflows often stop by observing novelty collapse:

```text
if several rounds produce no new items, stop
```

But no-new-item is only evidence about the region actually sampled.

Let:

```text
S = set of source-route strata
Y_s = hidden valid items in stratum s
q_i(s) = sampling distribution of agent i
q_bar(s) = mixture sampling distribution induced by all agents
p_t(s) = observed discovered evidence distribution at time t
```

If agent exploration is correlated, then `q_bar` can concentrate on easy strata.
The workflow may exhaust observable novelty under `q_bar` while leaving strata
with low `q_bar(s)` insufficiently searched.

Coverage localization measures this failure:

```text
high Gini(p_t)
=> discovered evidence is concentrated in a small subset of strata
=> no-new-item events mostly certify local exhaustion
=> global missing mass may remain
```

This gives the theoretical path:

> Under dependent stratified sampling, the residual missing mass after a
> no-new-item stopping event is lower bounded by unvisited or weakly visited
> strata; coverage localization is a runtime-observable proxy for that risk.

A modest theorem could show:

```text
P(false stop) increases with localization of q_bar or p_t
and decreases with global stratum coverage.
```

This would be enough. We do not need a phase-transition claim yet.

## 4. How This Relates To Existing Work

The angle is partly constrained by nearby literature:

- High-recall review and Chao-style estimators already study stopping under
  incomplete discovery.
- Adaptive/submodular coverage already gives formal language for coverage and
  marginal gains.
- Multi-agent diversity and effective rank already study how many independent
  information channels agents provide.
- Reasoning-trajectory geometry already studies geometry of model reasoning.

Therefore our distinction should be:

```text
source-route coverage localization under correlated multi-agent discovery,
for hidden-total safe stopping
```

not generic diversity, generic confidence, or generic completion.

## 5. How To Implement The Residual Coverage Challenger

The challenger should be derived from the geometry quantity.

Runtime state:

```text
C_t[i, s] = number of discoveries or visits by agent i in source-route stratum s
e_t(s) = sum_i C_t[i, s]
p_t(s) = e_t(s) / sum_s e_t(s)
G_t = Gini(p_t)
R_t = fraction of strata with e_t(s) > 0
```

Trigger:

```text
if no_new_rounds >= patience and G_t is high:
    do not stop
    launch residual coverage challenger
```

First version challenger policy:

```text
target strata with lowest e_t(s)
prioritize strata adjacent to known valid evidence buckets
forbid returning already-ledgered items
budget = small fixed audit budget
```

Why not use the compound lambda policy first?

The V2 simulation found:

```text
coverage_gini AUROC: 0.995
lambda AUROC:        0.831
```

and the challenger ablation showed:

| condition | strategy | false rate | mean recall | scout new items |
|---|---|---:|---:|---:|
| homogeneous | none | 1.000 | 0.750 | 0.0 |
| prompt_diverse | none | 1.000 | 0.750 | 0.0 |
| route_partitioned | low_coverage | 0.637 | 0.849 | 22.1 |
| extended_audit | risk_weighted | 0.546 | 0.870 | 7.2 |

The simpler low-coverage challenger is stronger in this simulation. Therefore
the first real implementation should be:

```text
coverage-localization monitor
+ low-coverage stratum challenger
```

not an over-designed risk-weighted controller.

## 6. What A Real-Agent Experiment Must Show

To move from simulation to paper-quality evidence, we need real trajectory logs:

```text
agent_id
round_id
query_text
tool_name
action_type
source_path
source_family
search_route
discovered_item_id
new_item
stop_reason
```

The empirical test:

1. Build `agent x source-route` matrices.
2. Compute coverage Gini before stopping.
3. Compare against:
   - source coverage ratio;
   - no-new-item rounds;
   - self-reported confidence;
   - pairwise Jaccard;
   - effective rank;
   - log-det.
4. Launch low-coverage challengers when localization is high.
5. Check whether they find oracle-true new items.

The geometry angle survives only if:

- coverage Gini predicts unsafe stopping in real runs;
- low-coverage challengers find residual true positives;
- the signal repeats across at least two tasks or repositories;
- it beats simple baselines or at least explains when they fail.

## 7. Current Claim We Can Safely Make

Safe claim:

> Controlled evidence suggests false stopping can be generated by coverage
> localization: agents exhaust novelty in a small subset of source-route strata
> while hidden valid items remain elsewhere. Coverage Gini is currently the
> strongest candidate runtime signal.

Unsafe claim:

> We have discovered a universal phase transition or Grassmann geometry of
> multi-agent workflows.

## 8. Next Step

Implement the real-agent diagnostic, not a final method:

```text
bounded discovery task
+ action-level logs
+ coverage-localization monitor
+ low-coverage challenger
+ oracle scoring after the run
```

If this confirms the simulation, the method can naturally become:

```text
Coverage Localization Monitor
+ Residual Coverage Challenger
+ Evidence Ledger
+ Safe-Stopping Decision
```

That would give the paper a real conceptual spine.

