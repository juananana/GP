# Research Object Memo: Coverage Geometry for Dynamic Multi-Agent Workflows

This note is for defining the research object. It does not continue the archived
`liudang1/` direction, does not introduce a finished method, and does not claim
that a geometry theory or phase transition has been established.

## 1. Starting Point

The practical trigger is the dynamic workflow setting described in
`2/推文.md`: large tasks can be split across multiple sub-agents, with patterns
such as fan-out-and-synthesize, adversarial verification, generate-and-filter,
tournament, and loop-until-done.

The important failure modes are:

- Agentic laziness: an agent declares completion after only partially covering
  the task.
- Self-preferential bias: agents or aggregators over-trust their own findings.
- Goal drift: long workflows gradually lose boundary conditions and edge cases.
- Unknown workload stopping: workflows stop when there are no obvious new items,
  even though the true remaining workload is unknown.

The research object should therefore not be "dynamic workflows are useful" or
"multi-agent systems improve coverage." Those are already part of the product
and systems story. The sharper object is:

> In bounded high-recall discovery tasks, why can a dynamic multi-agent workflow
> confidently stop while still missing valid in-scope items?

## 2. Candidate Phenomenon

The phenomenon we want to study is false completion under correlated
exploration.

In these tasks, there exists a hidden target set `Y*`. Agents do not know the
total size of `Y*` at runtime, but an oracle can evaluate coverage offline.
Each agent observes part of the source space and emits discovered items. The
workflow then decides whether to continue, audit, or stop.

The suspected failure is not merely wrong aggregation. It is:

> Multiple agents explore locally similar source-path/action regions, produce
> mutually reinforcing evidence, and make the workflow believe coverage is
> sufficient while the global source space still contains coverage holes.

This distinguishes two channels:

- Aggregation-induced omission: an item was found by at least one agent but lost
  during summarization, voting, filtering, or conservative aggregation.
- Correlated-exploration omission: no agent found the item because their search
  trajectories overlapped in the same easy basin.

These names should be treated as operational labels, not necessarily as new
terminology claims.

## 3. Why Geometry Might Be Relevant

Jiaxin's ICLR2027 draft is useful as a research style template, not as a formula
template. The lesson is:

1. Start from a real collapse phenomenon.
2. Find a normalized control variable.
3. Measure whether that variable predicts the onset of failure.
4. Only then derive or design a method from the observed law.

For LoRA merging, the natural object is a task subspace, so principal angles and
Grassmann geometry are justified. For multi-agent workflows, that is not yet
true. We must first find the right geometric object.

A conservative first object is a coverage matrix:

```text
C[i, j] = how much agent i covered stratum j
```

where a stratum may be:

- source family;
- source path bucket;
- search route;
- action/tool route;
- source-route pair.

The first geometry should be discrete and auditable:

- coverage entropy;
- HHI/Gini concentration;
- pairwise source-route overlap;
- effective rank of the coverage matrix;
- singular value spectrum;
- marginal log-det gain;
- residual novelty from a scout or challenger.

Grassmann manifolds, principal angles, coverage hulls, and phase-transition
language should remain suspended until the data show that trajectories form a
stable low-dimensional structure that simple coverage statistics cannot explain.

## 4. Current Research Question

The clean research question is:

> Does false completion in dynamic multi-agent discovery arise from measurable
> source-path/action-trajectory coverage concentration, and can a normalized
> coverage-geometry variable predict when a workflow is unsafe to stop?

More concrete subquestions:

1. Do false-completion runs show higher local concentration than safe runs?
2. Do geometry variables explain false completion beyond simple overlap, source
   coverage, no-new-item rounds, and self-reported confidence?
3. Does a challenger aimed at low-coverage or residual directions find more
   valid new items than a generic extra search at similar cost?
4. Is any discovered law stable across repositories, tasks, agent prompts, and
   models?

## 5. What We Should Not Claim Yet

Do not claim:

- DICE-Lite is already the method.
- A phase transition exists.
- Grassmann geometry is the right theory.
- Orthogonal scout gain exists before route vectors are measured.
- Effective rank or log-det is already the controlling variable.
- Existing archived logs are sufficient to prove the geometry hypothesis.

The earlier archived experiments can be used as historical observations only.
They should not define the new research object.

## 6. Minimum Evidence Needed

A credible geometry pilot needs both failure and non-failure states. Historical
logs that contain only false-completion states cannot test whether geometry
distinguishes safe stopping from unsafe stopping.

Minimum new run design:

```text
tasks:
  - one code-repository discovery task from a familiar repo
  - one held-out repository or document-discovery task

conditions:
  - homogeneous multi-agent exploration
  - source-partitioned or route-partitioned exploration
  - extended/audited high-recall run to create safe or near-safe comparison
  - challenger/scout targeted at weak or residual coverage

logs:
  - task_id
  - repo_id
  - run_id
  - agent_id
  - round_id
  - query_text
  - tool_name
  - action_type
  - source_path
  - source_family
  - search_route
  - timestamp
  - discovered_item_id
  - self_reported_completion
  - self_reported_confidence
  - stop_reason
  - token/cost
  - oracle_label only after the blind run
```

Primary outputs should be diagnostic, not method claims:

- source-route coverage matrices;
- item incidence matrices;
- safe vs false completion comparison;
- metric screening against simple baselines;
- scout residual novelty per cost;
- Go/No-Go decision for whether geometry is worth continuing.

## 7. Candidate Paper Positioning

A defensible early positioning is:

> We study safe stopping in dynamic multi-agent discovery workflows. While
> dynamic workflows use parallel agents to improve coverage and verification,
> we show that correlated exploration can produce false completion: agents agree
> and stop despite hidden coverage holes. We investigate whether source-path and
> action-trajectory coverage geometry provides a measurable control signal for
> this failure.

This is deliberately weaker than a method claim, but stronger than a product
observation. If a stable variable emerges, the method can later be derived from
it.

## 8. Go/No-Go Logic

Continue the geometry line only if:

- at least one geometry variable separates safe and false completion;
- it beats simple source coverage and overlap baselines;
- it generalizes across at least two tasks or repositories;
- it is computable without oracle information at runtime;
- challenger residual novelty confirms that low-coverage regions still contain
  missing mass.

If not, fall back to a simpler paper:

```text
safe stopping for multi-agent discovery
+ evidence ledger
+ source coverage
+ lightweight audit controller
```

That fallback is still publishable if the problem is clean and the evaluation is
strong. Geometry should earn its place by prediction, not by vocabulary.
