# Frozen Hypothesis for Real-Agent Pilot

This pilot freezes the theory before running real-agent experiments.

## Hypothesis

False stopping in workload-unknown dynamic agent workflows is caused by
**localized evidence conditions**:

> no-new / agreement / self-completion under high source-route exposure
> localization certifies local exhaustion, not global completion.

Bounded item discovery is used as an oracle-scored experimental subclass, not as
the full research object.

## Minimal Geometry

Use only two core localization diagnostics:

```text
G_exp(t) = Gini(p_exp(t))
p_exp(t, s) = v_t(s) / sum_s v_t(s)
v_t(s) = visits / queries / tool calls / scan actions in source-route stratum s

G_disc(t) = Gini(p_disc(t))
p_disc(t, s) = d_t(s) / sum_s d_t(s)
d_t(s) = discovered candidate items in source-route stratum s
```

Primary variable:

```text
G_exp(t)
```

Secondary diagnostic:

```text
G_disc(t)
```

Do not add compound variables unless real trajectories show that they improve
cross-task prediction.

## Baselines

Compare against:

- no-new-item rounds;
- self-reported completion/confidence;
- source-route coverage ratio;
- pairwise item Jaccard;
- effective rank;
- log-det volume.

## Intervention

If the workflow wants to stop while exposure localization is high:

```text
launch evidence-condition repair
```

The current repair candidate is residual-potential:

```text
priority(s) = under_exposure(s) x runtime_computable_potential(s)
```

It targets source-route strata where the current completion certificate is thin
and runtime-visible signals still justify further stress-testing.

## Success Criteria

Continue this research direction only if real-agent traces show:

1. `G_exp(t)` predicts false stopping better than no-new rounds and confidence.
2. `G_exp(t)` is competitive with or stronger than `G_disc(t)`.
3. Evidence-condition repair reduces unsupported completion certificates more
   than random or free-search continuation.
4. The pattern appears in at least two bounded tasks or repositories.

## Kill Criteria

Weaken or drop the geometry framing if:

- simple source-route coverage ratio explains the outcome equally well;
- exposure Gini fails outside one task;
- residual-potential does not improve certificate repair over simpler challengers;
- action logs are too noisy to define source-route strata reliably.
