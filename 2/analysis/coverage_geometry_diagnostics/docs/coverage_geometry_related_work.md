# Coverage Geometry Related Work Boundary

This note is a boundary document for the small diagnostic pilot. The goal is to
avoid claiming as original anything already covered by nearby work.

## Representational Collapse in Multi-Agent LLM Committees

- Object: multi-agent LLM committees.
- Input representation: reasoning traces or outputs embedded into a vector space.
- Geometry/statistics: embedding cosine similarity, effective rank, collapse/diversity measures.
- Prediction target: committee accuracy or reliability under agent collapse.
- Multi-agent: yes.
- Closed-world discovery: no.
- Unknown-total stopping: no.
- Overlap with us: embedding similarity and effective-rank diagnostics for multi-agent diversity.
- Gap left: source-path/action-route coverage for false-completion diagnosis in bounded discovery.

## Understanding Agent Scaling in LLM-Based Multi-Agent Systems via Diversity

- Object: scaling behavior of LLM multi-agent systems.
- Input representation: agent outputs/answers represented through similarity or diversity matrices.
- Geometry/statistics: Gram matrix, entropy effective rank, effective channel count.
- Prediction target: scaling gains and diversity effects.
- Multi-agent: yes.
- Closed-world discovery: no.
- Unknown-total stopping: no.
- Overlap with us: effective rank and diversity as label-free diagnostics.
- Gap left: coverage holes and hidden missing mass in closed-world item discovery.

## Predictive Maps of Multi-Agent Reasoning

- Object: multi-agent reasoning dynamics and communication topology.
- Input representation: graph/topology and state-transition style representations.
- Geometry/statistics: spectral/topological diagnostics and successor-representation style maps.
- Prediction target: reasoning drift, consensus, robustness, or success.
- Multi-agent: yes.
- Closed-world discovery: no.
- Unknown-total stopping: no.
- Overlap with us: structural diagnostics of multi-agent behavior.
- Gap left: source/item ledger coverage and false-completion labels under an offline oracle.

## DiLLS

- Object: diagnosis of LLM-agent systems.
- Input representation: logged agent behavior, summaries, and diagnostic views.
- Geometry/statistics: diagnostic visualization and layered analysis rather than a specific coverage geometry.
- Prediction target: failure localization and debugging support.
- Multi-agent: yes or agent-system oriented.
- Closed-world discovery: not the central setting.
- Unknown-total stopping: no.
- Overlap with us: agent failure diagnosis.
- Gap left: bounded high-recall discovery and missing-mass/stopping-specific analysis.

## Auditing Multi-Agent LLM Reasoning Trees Outperforms Majority Vote and LLM-as-Judge

- Object: multi-agent reasoning trees and majority-vote failures.
- Input representation: reasoning traces/trees.
- Geometry/statistics: audit and selection over trace structures, not source coverage geometry.
- Prediction target: answer correctness and audit improvement over majority vote.
- Multi-agent: yes.
- Closed-world discovery: no.
- Unknown-total stopping: no.
- Overlap with us: majority vote can discard useful minority evidence.
- Gap left: closed-world recall, source coverage holes, and completion-risk diagnosis.

## Beyond Consensus: Trace-Level Synthesis in Mixture of Agents

- Object: mixture-of-agents synthesis beyond simple consensus.
- Input representation: trace-level outputs from agents.
- Geometry/statistics: trace-level aggregation/synthesis signals.
- Prediction target: improved final answer quality.
- Multi-agent: yes.
- Closed-world discovery: not central.
- Unknown-total stopping: no.
- Overlap with us: consensus is not enough; trace-level evidence matters.
- Gap left: source-path coverage and hidden missing items rather than answer synthesis.

## Push Your Agent

- Object: long-horizon agent persistence and goal pursuit.
- Input representation: long-horizon trajectories and quantitative persistence signals.
- Geometry/statistics: persistence metrics and enforcement/measurement of goal continuation.
- Prediction target: whether agents persist toward goals.
- Multi-agent: not necessarily the core focus.
- Closed-world discovery: not central.
- Unknown-total stopping: related but not formulated as hidden-total recall.
- Overlap with us: premature stopping and persistence.
- Gap left: multi-agent correlated exploration and oracle-evaluated missing mass.

## SeekerGym

- Object: agentic search and information-seeking benchmark behavior.
- Input representation: search tasks, traces, and discovered information.
- Geometry/statistics: benchmark metrics for search performance.
- Prediction target: information-seeking success.
- Multi-agent: not necessarily central.
- Closed-world discovery: related.
- Unknown-total stopping: related but not the same as our completion certificate setting.
- Overlap with us: broad search and total-recall pressure.
- Gap left: multi-agent source-path/action-route concentration as a false-completion diagnostic.

## DeepSearchQA

- Object: deep search QA and under-retrieval/premature stopping.
- Input representation: question, search traces, retrieved evidence, final answers.
- Geometry/statistics: search/evidence metrics rather than coverage geometry as the main object.
- Prediction target: answer quality and search sufficiency.
- Multi-agent: not central.
- Closed-world discovery: adjacent, but QA-oriented.
- Unknown-total stopping: adjacent.
- Overlap with us: premature stopping and incomplete evidence gathering.
- Gap left: bounded source collections with oracle item sets and multi-agent correlation.

## Total Recall QA

- Object: total-recall style question answering.
- Input representation: query, evidence, and recall-oriented answer/evidence sets.
- Geometry/statistics: recall/completeness evaluation.
- Prediction target: exhaustive retrieval/answer coverage.
- Multi-agent: not central.
- Closed-world discovery: yes, adjacent.
- Unknown-total stopping: related.
- Overlap with us: total recall and verifiable coverage.
- Gap left: false completion in multi-agent workflows and source-route concentration.

## Detecting Underspecification in Software Requirements via k-NN Coverage Geometry

- Object: underspecification in software requirements.
- Input representation: requirement embeddings/neighborhoods.
- Geometry/statistics: k-NN coverage geometry.
- Prediction target: underspecified or poorly covered requirements.
- Multi-agent: no.
- Closed-world discovery: no.
- Unknown-total stopping: no.
- Overlap with us: coverage geometry terminology and k-NN/coverage-style diagnostics.
- Gap left: multi-agent discovery logs, source paths, and false completion.

## Measuring Black-Box Confidence via Reasoning Trajectories

- Object: black-box confidence estimation from reasoning trajectories.
- Input representation: trajectories and their geometric/coverage features.
- Geometry/statistics: trajectory geometry, coverage, verbalization signals.
- Prediction target: confidence/correctness calibration.
- Multi-agent: not necessarily central.
- Closed-world discovery: no.
- Unknown-total stopping: no.
- Overlap with us: trajectory geometry and coverage as confidence signals.
- Gap left: closed-world high-recall discovery with hidden total item count and multi-agent source coverage.

## Not Original For This Project

- Embedding cosine similarity.
- Effective rank.
- The idea that heterogeneous agents improve diversity.
- The idea that majority vote may discard evidence.
- False-completion terminology in the broad sense.
- Coverage-geometry terminology in the broad sense.

## Narrow Candidate Difference

The remaining candidate difference is:

> source-path/action-trajectory coverage geometry for false-completion diagnosis
> in multi-agent closed-world discovery, where the true total item count is
> hidden from agents but available to the oracle for offline evaluation.

The current pilot can only test the source-path/item-ledger part because
existing online logs do not contain enough query/action/tool events.
