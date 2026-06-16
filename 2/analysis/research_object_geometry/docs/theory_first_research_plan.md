# Theory-First Research Plan

Goal: advance the coverage-localization angle without inventing unnecessary
variables.

## 1. Principle

The paper should not start from a method. It should start from a failure law.

Candidate law:

> In hidden-total multi-agent discovery, false stopping is driven by coverage
> localization: search exposure concentrates in a small subset of source-route
> strata, so no-new-item stopping certifies local exhaustion rather than global
> completion.

The central variable should be as small as possible:

```text
G_exp(t) = Gini(p_t^exp)
p_t^exp(s) = v_t(s) / sum_s v_t(s)
v_t(s) = visits / queries / tool calls / scan actions in source-route stratum s

G_disc(t) = Gini(p_t^disc)
p_t^disc(s) = d_t(s) / sum_s d_t(s)
d_t(s) = discovered candidate items in source-route stratum s
```

Do not introduce compound variables unless they clearly improve generalization.

## 2. Why Not More Variables

The controlled V2 simulation tested:

- coverage Gini;
- source-route coverage ratio;
- effective rank;
- compound lambda = Gini * (1 - coverage ratio);
- small feature combinations.

Leave-world-out AUROC:

| feature set | mean AUROC |
|---|---:|
| Gini + coverage | 0.9963 |
| Gini only | 0.9962 |
| Gini + effective rank | 0.9960 |
| all three | 0.9959 |
| effective rank only | 0.9778 |
| coverage ratio only | 0.8194 |
| stopped round | 0.4978 |

Interpretation:

> Coverage Gini alone is nearly sufficient in the controlled setting.

The controlled V3 simulation then separated exposure localization from
discovery localization. In that construction, `exposure_gini` and
`discovery_gini` were almost tied:

| metric | AUROC |
|---|---:|
| discovery_gini | 0.8453 |
| exposure_gini | 0.8452 |

This does not prove exposure Gini is empirically stronger yet. Its value is
conceptual: it measures where the workflow searched even when nothing was
found, which is exactly what a stopping certificate needs.

This is exactly the kind of result we want: a simple variable with strong
predictive power. Extra variables should be auxiliary diagnostics, not core
theory.

## 3. Related Work Boundary

The contribution must avoid claiming ownership of existing ideas:

- High-recall stopping and prevalence estimation already exist in TAR and
  Chao-style estimators.
- Information-seeking benchmarks already study completeness and premature
  stopping.
- Multi-agent diversity, effective channel count, and representational collapse
  already study diversity/effective rank.
- Reasoning-trajectory geometry already studies geometric confidence signals.
- Majority vote and trace-level synthesis papers already study consensus
  failures and lost minority evidence.

Therefore the narrow gap is:

```text
exposure-localized source-route exploration
under correlated multi-agent discovery
with hidden total target count
and runtime safe-stopping decisions
```

## 4. Theoretical Target

A realistic theorem should not claim a phase transition yet.

Suggested theorem form:

Let each stratum `s` contain hidden target mass `m_s`. Agents sample strata from
dependent distributions `q_i(s)`. The workflow observes discoveries and stops
after a no-new-item event. If the exposure distribution `p_t^exp` has high
Gini, then the no-new-item event is dominated by a small subset of strata.
Unless unobserved strata have zero target mass, residual missing mass remains.

Possible statement:

```text
E[residual_missing_mass | stop]
>= f(G_exp(t), low_exposure_strata, dependency)
```

or:

```text
P(false_stop | stop)
is monotone increasing in localization of p_t^exp
under nonzero missing mass outside high-coverage strata.
```

This is enough for theory depth. It connects observed geometry to stopping
risk without pretending to have discovered a universal phase transition.

## 5. Method Derived From Theory

If `G_exp(t)` is high when a workflow wants to stop:

1. Reject immediate stopping.
2. Identify low-exposure strata:

```text
s in argmin v_t(s)
```

3. Launch residual coverage challenger with a small budget.
4. Forbid returning already-ledgered items.
5. If challenger finds new true or plausible items, continue discovery.
6. If challenger finds no novelty and exposure localization falls, allow
   safe-stop or abstain depending on threshold.

This gives a method only after the variable is justified:

```text
Exposure Localization Monitor
+ Low-Exposure Residual Challenger
+ Evidence Ledger
+ Safe-Stopping Decision
```

## 6. Next Experiments

### Experiment A: Real-Agent Trajectory Logging

Need two bounded tasks:

- one code repository discovery task;
- one document/policy discovery task.

Required action logs:

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

### Experiment B: Metric Competition

Compare:

- exposure Gini;
- discovery Gini;
- source coverage ratio;
- effective rank;
- log-det;
- no-new-item rounds;
- self-reported confidence;
- Jaccard overlap.

Keep the theory centered on the smallest variable that wins.

### Experiment C: Challenger Causal Test

At the stopping point:

- random challenger;
- low-exposure challenger;
- low-discovery challenger;
- high-confidence/no-op baseline.

Measure:

- new valid items found;
- novelty per cost;
- false-stop reduction;
- whether new true items come from predicted low-exposure strata.

This is the decisive test: it checks whether the geometry variable not only
predicts failure, but also identifies where residual missing mass lives.

## 7. Paper Shape If Confirmed

Title candidate:

> Coverage Localization Causes False Stopping in Dynamic Multi-Agent Discovery

Core story:

1. Dynamic workflows help scale discovery but can falsely stop.
2. Existing explanations focus on persistence, consensus, diversity, or
   aggregation.
3. We identify a coverage-process failure: search exposure localizes in a small
   region.
4. Exposure Gini is a runtime-computable predictor of unsafe stopping, with
   discovery Gini as a secondary diagnostic.
5. A low-exposure residual challenger follows directly from the theory.

## 8. Kill Criteria

Drop or weaken the geometry angle if real-agent experiments show:

- exposure Gini does not beat no-new-item rounds or source coverage;
- low-exposure challengers do not find residual true positives;
- the effect only appears in one task;
- action routes cannot be logged reliably.

In that case, write a simpler safe-stopping/evidence-ledger paper.
