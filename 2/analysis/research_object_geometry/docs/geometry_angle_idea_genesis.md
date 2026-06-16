# Geometry Angle Idea Genesis

This note asks how to find a deep geometry angle for dynamic multi-agent false
stopping, using Jiaxin's paper as a style template rather than copying its
Grassmann machinery.

## 1. What We Should Learn From Jiaxin's Paper

The important pattern is not "use advanced geometry." The pattern is:

1. Start from a real and repeatable collapse phenomenon.
2. Identify the simplest object that naturally carries geometry.
3. Search for a normalized control variable.
4. Show that the variable predicts the onset of failure.
5. Derive the method from the control law, rather than adding a method first.

For LoRA merging, the natural object is a low-rank task subspace. That justifies
principal angles, projectors, Grassmann geometry, and rank ratio `r/d`.

For dynamic multi-agent workflows, the natural object is not yet a subspace. The
first natural object is the **coverage distribution** induced by agent actions:

```text
agent x source-route stratum coverage matrix
```

The geometry should be discovered from this object before we introduce more
advanced tools.

## 2. Boundary From Nearby Work

Nearby work already covers several tempting but unsafe claims:

- Multi-agent output diversity and effective channel count are already studied.
- Representational collapse in multi-agent committees is already measured with
  embedding similarity and effective rank.
- Reasoning-trajectory geometry is already used for black-box confidence.
- Deep research completeness and stopping criteria are already benchmarked.
- Goal persistence and false completion are already discussed for long-horizon
  agents with verifier-backed work units.

Therefore, our angle cannot be:

```text
multi-agent diversity geometry
reasoning trace embedding geometry
generic completeness benchmark
generic false completion
```

The remaining defensible angle is:

> coverage-process geometry for hidden-total, closed-world multi-agent
> discovery, where agents must decide whether to stop without knowing the true
> total item count.

## 3. Candidate Geometry Angles

### Angle A: Coverage Localization

Object:

```text
p_t(s) = fraction of discovered evidence assigned to source-route stratum s
```

Core variable:

```text
Localization(C_t) = Gini(p_t) or 1 - normalized_entropy(p_t)
```

Hypothesis:

> False stopping occurs when novelty is exhausted inside a localized explored
> region, while global source-route coverage remains incomplete.

Why this is promising:

- It emerged strongly in controlled simulation.
- It is simple, runtime-computable, and auditable.
- It explains why agreement can be misleading: agents may agree because they
  repeatedly explore the same region.

Risk:

- It may reduce to simple source coverage.
- It may be too empirical unless we derive a missing-mass bound.

### Angle B: Coverage Rank / Effective Channels

Object:

```text
C_t[i, s] = coverage by agent i over stratum s
```

Core variables:

```text
effective_rank(C_t)
singular_value_spectrum(C_t)
logdet(C_t C_t^T + eps I)
```

Hypothesis:

> The number of effective independent exploration channels, not the number of
> agents, controls residual missing mass.

Why this is promising:

- It connects to existing multi-agent diversity theory.
- It may generalize across agent counts.

Risk:

- Nearby work already owns much of "effective rank for multi-agent diversity."
- Our controlled simulation found it weaker than coverage localization.

Use:

- Secondary diagnostic, not first core theory.

### Angle C: Residual Coverage Direction

Object:

```text
new scout coverage vector v_{t+1}
current explored coverage span U_t
```

Core variables:

```text
residual_ratio = ||(I - P_U) v_{t+1}||^2 / ||v_{t+1}||^2
residual_novelty_per_cost
```

Hypothesis:

> A challenger is useful only when it genuinely covers residual directions not
> already spanned by the main agents' source-route coverage.

Why this is promising:

- It can lead to a method naturally: send challengers to residual coverage
  directions.
- It directly links diagnosis and intervention.

Risk:

- Requires real action-route logs.
- We must not call it "orthogonal" until the vector projection is measured.

### Angle D: Coverage Saturation Curve

Object:

```text
coverage gain over rounds
Delta coverage volume or Delta unique strata/items
```

Core variables:

```text
marginal_coverage_gain
marginal_localization_change
novelty_decay_rate
```

Hypothesis:

> Safe stopping requires global coverage saturation, not merely local novelty
> saturation.

Why this is promising:

- It directly attacks loop-until-done stopping.
- It can explain why "no new items" is not enough.

Risk:

- Needs round-level logs.
- Might collapse to standard stopping/Chao estimators unless we model
  correlated exploration.

### Angle E: Coverage Phase Diagram

Object:

```text
(coverage localization, source-route coverage ratio, residual novelty)
```

Possible regions:

| region | geometry | behavior |
|---|---|---|
| local trap | high localization, low global coverage | high false stopping risk |
| diffuse noise | low localization, low validated support | high audit cost |
| safe saturation | low residual novelty, high global coverage | safe to stop |
| transition | marginal coverage gain decays while holes remain | requires challenger |

Hypothesis:

> There may be a reproducible phase diagram, but we should not call it a phase
> transition until thresholds replicate across tasks.

Why this is promising:

- It is closest to Jiaxin's "safe/transition/danger" style.
- It can organize theory and method.

Risk:

- Easy to overclaim.
- Needs cross-task normalized variables.

## 4. Current Best Direction

The strongest current candidate is:

> **Coverage localization controls false stopping.**

The first theoretical object should be the distribution of discovered evidence
over source-route strata, not embedded answer traces.

A possible normalized order parameter:

```text
lambda_t = Gini(p_t) * (1 - R_t)
```

where:

```text
p_t(s) = discovered evidence distribution over strata
R_t = source-route coverage ratio
```

Interpretation:

- high `Gini(p_t)` means evidence is localized;
- low `R_t` means global source-route coverage is incomplete;
- their product flags local saturation with global holes.

This is not yet a theorem. It is a candidate order parameter to test.

## 5. What A Theoretical Result Could Look Like

A modest but publishable theorem target:

> Under a stratified discovery model with unknown target count and dependent
> agent exploration, the probability of false stopping is lower bounded by a
> function increasing in coverage localization and decreasing in global
> stratum coverage.

Sketch:

1. Let each stratum `s` contain hidden valid items with rate `mu_s`.
2. Agents sample strata from dependent distributions `q_i(s)`.
3. The observed no-new-item event estimates only local exhaustion under the
   induced mixture `q_bar(s)`.
4. If `q_bar` has high localization while unvisited strata have nonzero
   missing mass, then no-new-item stopping underestimates residual mass.
5. Coverage localization gives a runtime-computable upper-risk proxy.

The theory should explain:

- why homogeneous agents fail;
- why route partitioning helps;
- why residual challengers help;
- when simple source coverage is enough;
- when effective rank/logdet add value.

## 6. Experiments Needed To Find The Angle

### Experiment 1: Controlled Simulation

Already done.

Result:

- coverage Gini is strong in the constructed mechanism;
- effective rank/logdet are weaker;
- residual targeting helps.

Conclusion:

> Continue toward real-agent diagnostic, but keep the geometry simple.

### Experiment 2: Real-Agent Bounded Discovery

Need new logs:

```text
round_id
agent_id
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

Compare:

- homogeneous;
- prompt diverse;
- route partitioned;
- extended audited;
- residual challenger.

Primary test:

```text
Does coverage localization predict false stopping better than:
- source coverage count
- no-new-item rounds
- confidence
- pairwise Jaccard
```

### Experiment 3: Cross-Task Normalization

Normalize by:

```text
number of strata
agent count
budget
oracle-free observed coverage
```

Goal:

> Find whether a stable danger zone exists, not necessarily a hard phase
> transition.

## 7. If This Works, The Paper Shape

Potential title:

> Coverage Localization in Dynamic Multi-Agent Discovery Workflows

Core claim:

> False stopping is not merely a failure of persistence or aggregation. It is a
> coverage-process failure: agents can exhaust novelty in a local region while
> hidden target mass remains in weakly covered strata.

Method, if needed:

```text
Coverage-localization monitor
+ residual challenger
+ evidence ledger
+ safe stopping decision
```

The method should be derived only after the geometry result holds.

## 8. Kill Criteria

Drop the geometry framing if:

- simple source coverage explains false stopping as well as coverage Gini;
- localization does not replicate across tasks;
- action-route logs do not show stable structure;
- residual challengers do not find missing mass in predicted regions.

If this happens, the fallback paper is still:

> safe stopping for multi-agent discovery with evidence ledger and lightweight
> audit control.

