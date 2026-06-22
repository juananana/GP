# Experiment Refactor Audit: Milestone 0

Date: 2026-06-22

This audit follows `2/paper/docs/evidence_condition_experiment_design_v1.md`.  It is deliberately limited to Milestone 0: checkpoint the current state, inspect the existing experiment code/data/controller path, identify what can be reused, identify oracle or post-hoc leakage risks, and propose a staged refactor plan.  No experiment logic has been deleted or rewritten in this milestone.

## 1. Milestone 0 Status

- Git checkpoint completed before this audit: `b7983cb Add experiment refactor design`, pushed to `GP/main`.
- This audit reviews the current implementation under `2/analysis/research_object_geometry/real_agent_pilot/`, the configs under `2/configs/`, and the current schemas under `2/analysis/research_object_geometry/real_agent_pilot/schemas/`.
- Existing unrelated working-tree files are not part of this audit and should remain untouched unless explicitly requested.

## 2. Current Experiment Code Map

The experiment code is currently concentrated in one research folder but not yet one unified framework:

- `experiment_config.py`: shared config loader for seeds, thresholds, task settings, oracle paths, and output paths.
- `external_validation_requests/run_external_requests_validation.py`: bounded external repository audit over a local `requests` package snapshot.
- `external_validation_v2/run_external_validation_v2.py`: bounded external repository audit over a local `urllib3` package snapshot.
- `controller_validation_v1/run_controller_validation_v1.py`: older controller validation script with a known post-hoc decision leakage risk.
- `controller_validation_v1/run_controller_validation_v2.py`: improved controller validation script that requires `runtime_residual_items` for decisions.
- `credibility_supplement/run_credibility_supplement.py`: current aggregate experiment runner/exporter/plot/table generator for decision variants, repair variants, controller counts, localization trend, threshold/budget sensitivity, and safety-cost frontier.
- `scripts/run_blind_policy_task.py` and `scripts/run_blind_code_task.py`: generated policy-docset/code-repo sanity checks with hardcoded sources, routes, conditions, and oracle entries.
- `schemas/action_event.schema.json`: runtime event schema for action logs.
- `schemas/oracle_item.schema.json`: oracle item schema for post-hoc scoring labels.

The current folder is usable as a starting point, but the main experiments are a collection of compatible scripts rather than a single lifecycle: route inventory -> runtime trace -> runtime decision -> repair action -> post-hoc scorer -> metrics -> plots.

## 3. What Can Be Reused

The following parts are reusable with limited refactoring:

- Runtime event fields in `action_event.schema.json`: `task_id`, `run_id`, `condition`, `agent_id`, `source_family`, `search_route`, `source_route_stratum`, `discovered_item_id`, `new_item`, `self_reported_completion`, `stop_reason`, and `token_or_cost` already match the trace direction in the design document.
- Oracle item fields in `oracle_item.schema.json`: `item_id`, `oracle_label`, `oracle_bucket`, `source_family`, and `source_route_stratum` are a reasonable post-hoc scoring base.
- Config loader in `experiment_config.py`: `load_experiment_config`, `thresholds`, `seeds`, `task_config`, `oracle_path`, and `output_path` are reusable.
- Requests/urllib3 snapshot generation and regex scanning: both external scripts already create bounded, reproducible source snapshots and deterministic event logs.
- Runtime-visible repair ranking ideas: `random`, `low_exposure`, `high_potential`, `residual_potential`, and `free_search_continuation` are implemented in a way that can be wrapped behind a unified adapter.
- Unified aggregate exports in `credibility_supplement/run_credibility_supplement.py`: the current CSV/JSON exports are useful downstream artifacts, but they should become products of a unified trace/scoring pipeline rather than the primary source of truth.

## 4. Route Inventory Audit

Current status: route inventory is partially fixed before runtime, but not yet fully externalized.

| Component | Current state | Reuse? | Refactor need |
|---|---|---:|---|
| `full_200seed.yaml`, `main_3seed.yaml`, `sensitivity.yaml` | Seeds, thresholds, repair budgets, task route lists, condition route sequences, oracle paths, runtime-visible fields, and posthoc-only fields are config-driven. | Yes | Keep and expand. |
| Requests script | `CONDITIONS` route sequence is read from config, but `FILES` and `ROUTES` regex definitions are hardcoded in the script. | Yes | Move `FILES`, route IDs, regex patterns, and source families into a frozen route/source inventory manifest. |
| urllib3 script | Same pattern as requests: condition route sequence is config-driven; `FILES` and regex `ROUTES` are hardcoded. | Yes | Same inventory manifest refactor. |
| Policy/code sanity tasks | `ORACLE`, `ROUTES`, `CONDITIONS`, and source lists are all hardcoded in each script. | Partial | Keep as controlled sanity checks; migrate only after external benchmarks are clean. |
| Controller/supplement aggregation | Reads generated CSVs and constructs state tables; does not own a frozen route inventory. | Yes | Make it consume unified manifests and traces rather than script-specific outputs. |

Judgment: the existing route choices are fixed at script import/run time and are not tuned inside the runtime decision loop. However, because route patterns and source inventories live inside Python scripts, the paper cannot yet claim a clean config-defined route inventory. The refactor should freeze this as `route_inventory.yaml` or per-task manifests before running new main experiments.

## 5. Runtime vs Post-Hoc Field Audit

The configs already declare a useful separation:

- Runtime-visible fields include event identity, source path/family, search route, source-route stratum, discovered item ID, `new_item`, self-reported completion/confidence, stop reason, and cost.
- Post-hoc-only fields include `oracle_label`, `oracle_bucket`, `oracle_total`, `recall`, `bounded_oracle_recall`, `undiscovered_true_item_count`, and `hidden_missing_mass`.

The implementation mostly respects this in newer paths, but separation is not yet enforced by schema/type boundaries.

### Main Runtime Decision Paths

| File/function | Decision inputs | Leakage assessment |
|---|---|---|
| `credibility_supplement/run_credibility_supplement.py::runtime_controller_decision` | Support, Gini, weak plausible gap, runtime residual warning/count. | Low risk if called only with runtime-derived fields. |
| `credibility_supplement/run_credibility_supplement.py::verifier_gate_decision` | Unresolved/residual warning only. | Low risk for generic verifier-gate baseline. |
| `external_validation_v2/run_external_validation_v2.py::evaluate_conditions` | Uses exposure geometry and `weak_plausible_gap` for `controller_decision`; computes recall in the same function. | Medium audit risk due to co-location of runtime decision and post-hoc scoring, even though the decision branch does not read recall. |
| `external_validation_v2/run_external_validation_v2.py::evaluate_challengers` | Uses `runtime_residual_items`, support, Gini, weak gap for decisions; uses oracle only for `new_true_items` and `cumulative_recall` scoring. | Low-to-medium risk; logic is acceptable, but scoring and runtime actions should be split. |
| `external_validation_requests/run_external_requests_validation.py::select_targets` | Exposure/discovery counters, source text route match potential, seed, and budget. | Low risk; no oracle totals or undiscovered true counts used in target selection. |
| `external_validation_requests/run_external_requests_validation.py::evaluate_challengers` | Uses oracle IDs for `new_true_items` and scoring after targets are selected. | Low-to-medium risk; acceptable post-hoc scorer, but should be separated. |
| `controller_validation_v1/run_controller_validation_v1.py::decision(before, after, new_true_items)` | Directly uses `new_true_items` to return `CONTINUE`. | High risk; should be treated as legacy/non-main evidence and excluded from runtime-controller claims. |
| `controller_validation_v1/run_controller_validation_v2.py::controller_decision` | Requires `runtime_residual_items`; recall is used only to compute false certification after decisions. | Low risk; use this pattern going forward. |
| `scripts/run_blind_policy_task.py`, `scripts/run_blind_code_task.py` | Runtime scanning is nominally blind, but oracle, route definitions, task construction, and scorer live in the same file. | Medium risk for presentation; keep as supplementary sanity checks until migrated. |

## 6. Controller and Repair Call-Chain Audit

The current intended controller story is:

1. Runtime trace logs source-route exposure and discovered item IDs.
2. Stop-time state computes support and Gini over source-route strata.
3. Runtime potential estimates whether unvisited strata still have plausible evidence using source text and route patterns.
4. Full controller returns `SAFE`, `CONTINUE`, or `ABSTAIN`.
5. Repair target selection uses runtime exposure and potential, then post-hoc oracle scoring measures gain/cost.

This story is sound, but the code should enforce the following boundaries:

- Runtime controller must accept a `RuntimeState` object that does not contain oracle fields.
- Post-hoc scorer must accept `RuntimeDecision` plus oracle labels only after the decision is frozen.
- Repair planner must output targets before any `oracle_total`, `recall`, `new_true_items`, or `undiscovered_true_item_count` is available.
- Plotting and paper tables should be generated only from scored artifacts that retain a pointer to the frozen runtime decision record.

The current scripts often compute these in one Python function. That is understandable for a pilot, but it makes the experiment harder to audit and invites accidental leakage.

## 7. Leakage Risk Register

| Severity | Risk | Evidence | Required action |
|---|---|---|---|
| High | Legacy controller decision reads post-hoc repair success. | `controller_validation_v1/run_controller_validation_v1.py::decision(before, after, new_true_items)` uses `new_true_items` directly. | Exclude v1 from main claims; mark as deprecated; add a test that runtime decision functions reject `new_true_items`. |
| Medium | Runtime decision and oracle scoring co-located in the same functions. | `external_validation_v2::evaluate_conditions` computes `recall` in the same function that assigns `controller_decision`; challenger evaluators compute targets, oracle gain, and decisions together. | Split into `runtime_state_builder`, `controller_decider`, `repair_planner`, and `posthoc_scorer`. |
| Medium | Route/source inventory not fully config-frozen. | Requests/urllib3 `FILES` and `ROUTES` are hardcoded; config only controls condition route sequences. | Move source files, route IDs, regex/lens definitions, and route universe to manifests committed before new runs. |
| Medium | Generated policy/code tasks mix oracle construction and runtime scan in one script. | `ORACLE`, `ROUTES`, and `CONDITIONS` are hardcoded in `run_blind_policy_task.py` and `run_blind_code_task.py`. | Keep as supplement sanity checks or migrate to the same adapter/schema before main use. |
| Low | Aggregate exports are not the raw trace source of truth. | `unified_*.csv/json` are generated aggregate tables in `credibility_supplement/results`. | Keep exports, but add raw unified trace and decision artifacts. |
| Low | Config declares posthoc-only fields but code does not enforce it. | YAML has `posthoc_oracle_only_fields`; runtime functions accept generic DataFrames. | Add automated leakage checks and dataclasses/schemas that block posthoc fields in runtime calls. |

## 8. Existing Dataset Migration Notes

### 8.1 Requests

Current experiment: bounded item-discovery audit over six local package files with four regex routes.

Reuse:

- Snapshot creation.
- Regex route scans.
- Action event format.
- Runtime repair planners.
- Post-hoc oracle scoring.

Migration:

- Create `configs/tasks/requests_inventory.yaml` with source files, source families, route IDs, regex patterns, route descriptions, and condition route sequences.
- Replace hardcoded `FILES`/`ROUTES` with manifest loading.
- Emit three artifacts:
  - `runtime_trace.jsonl`: only runtime-visible event records.
  - `runtime_decisions.jsonl`: stop-time state and controller outputs without oracle fields.
  - `posthoc_scores.jsonl`: recall, oracle total, new true items, false certification labels.
- Keep `requests` as a useful external pattern-defined repository audit, but state clearly that the oracle is pattern-defined.

### 8.2 urllib3

Current experiment: bounded item-discovery audit over six local package files with five regex routes and an extended-audit condition.

Reuse:

- Stronger controller path than requests because `evaluate_challengers` already distinguishes `runtime_residual_items` from `new_true_items`.
- The eligible-but-residual-positive boundary case is still valuable if presented with the correct denominator explanation.

Migration:

- Same inventory manifest as requests.
- Split `evaluate_conditions` into runtime and post-hoc phases.
- Preserve the `extended_audit` condition as a controlled state type, but ensure it is not presented as an oracle-selected state unless explicitly generated by a post-hoc validation protocol.

### 8.3 Policy Docset

Current experiment: generated controlled policy-clause discovery task.

Reuse:

- Good sanity check for whether source-route geometry behaves as expected under a known hidden set.
- Existing runtime fields are close to action-event schema.

Migration:

- Do not use as a main external-validity result unless source documents, route inventory, and hidden oracle are frozen in separate files before runtime.
- Move `ORACLE`, `ROUTES`, `CONDITIONS`, and source list into separate manifests.
- Keep as supplementary controlled evidence if main paper space is limited.

### 8.4 Code Repo

Current experiment: generated controlled code-risk discovery task.

Reuse:

- Useful as an additional controlled sanity check for route granularity and repair targeting.

Migration:

- Same as policy docset.
- Avoid overstating it as a real repository benchmark; it is generated and should not carry the main empirical claim.

## 9. Proposed Unified Trace Schema

The existing `action_event.schema.json` and `oracle_item.schema.json` should become part of a larger schema family:

1. `route_inventory.schema.json`
   - `task_id`
   - `source_id`, `source_family`, `source_path` or external locator
   - `route_id`
   - `route_type` such as regex, action lens, query lens, page lens
   - frozen route definition or adapter-specific reference
   - frozen timestamp/hash/version

2. `runtime_trace.schema.json`
   - Existing action event fields.
   - Add `environment_id`, `trajectory_id`, `step_index`, `observation_ref`, `action_ref`, `adapter_name`, and `cost_breakdown` as optional fields for WebArena/BrowserGym/TREC.

3. `runtime_state.schema.json`
   - `task_id`, `trajectory_id`, `stop_state_id`
   - support, Gini, exposure counts or hash/ref
   - weak plausible gap, runtime residual count/warning
   - no oracle labels, no recall, no oracle total, no undiscovered true count.

4. `runtime_decision.schema.json`
   - `controller_version`
   - `policy`
   - `decision`: `SAFE`, `CONTINUE`, `ABSTAIN`
   - `diagnosis`: source-route mismatch, residual-positive, insufficient support, high concentration, verifier warning, etc.
   - `repair_targets`: optional source-route targets or adapter-specific next audit actions.

5. `posthoc_score.schema.json`
   - `oracle_id` or `evaluator_id`
   - `success`, `recall`, `oracle_total`, `found_true_items`, `new_true_items`, `false_certification`, `safe_coverage_label`
   - must reference an immutable `runtime_decision_id`.

This split is the single most important refactor for making the experiments look designed from first principles rather than tuned toward desired outcomes.

## 10. WebArena / BrowserGym Integration Needs

Purpose: validate false completion and actionability in realistic web-agent workflows.

Required adapters:

- `BrowserGymTraceAdapter`: convert environment trajectories into `runtime_trace.jsonl`.
- `WebTaskSourceMapper`: map pages/modules/tools to source families.
- `WebRouteLens`: map actions and observations into fixed route IDs such as `navigation`, `search_query`, `read_inspect`, `form_action`, `state_verification`, and `confirmation`.
- `StopSignalExtractor`: detect final answer, DONE action, stop action, or no-more-work declaration.
- `EvaluatorScorer`: attach environment success/failure only in `posthoc_score`.

Config additions:

- Environment name/version.
- Task IDs and split.
- Agent name/model/prompt version.
- Seeds.
- Route inventory and source mapping.
- Cost fields: tool calls, LLM calls, tokens, wall-clock time, browser actions.
- Output paths for raw trajectories, runtime traces, decisions, post-hoc scores, and figures.

Metrics:

- False completion rate: stopped or declared done while evaluator success is false.
- Safe coverage: fraction of evaluator-success states accepted as `SAFE`.
- Actionable CONTINUE rate: fraction of unsafe stop states where controller returns `CONTINUE` with a concrete next route/source diagnosis.
- ABSTAIN rate and fail-closed rate.
- Repair success gain after following controller targets.
- Cost: browser actions, LLM calls, tokens, wall-clock time.

Plots/tables:

- False completion prevalence by task family/agent.
- Diagnostic evidence plot: source-route support/Gini for successful vs false-complete stops.
- Controller dashboard: FCR, safe coverage, actionable CONTINUE vs ABSTAIN, repair gain-cost.
- Compact table of task counts, states, and costs.

## 11. TREC Total Recall Integration Needs

Purpose: validate completion-audit behavior under a high-recall oracle with known relevance judgments.

Required adapters:

- `TrecTopicAdapter`: load topics, qrels, and collection metadata.
- `RetrievalRunAdapter`: convert retrieval/review runs into source-route traces.
- `QueryRouteMapper`: map query strategies to route IDs such as keyword query, entity query, synonym expansion, metadata/date facet, seed-neighbor expansion, and contrastive query.
- `ReviewBatchSourceMapper`: map collection shards, clusters, retrieval batches, or evidence pools to source families.
- `TrecPosthocScorer`: compute recall and residual relevant documents only after runtime stop/decision.

Config additions:

- Topic split and qrels path.
- Target recall thresholds, e.g. 0.90 and 0.95.
- Route definitions/query templates.
- Review budget schedule.
- Retrieval backend and run seeds.
- Output paths for traces, runtime decisions, qrel-based scores, and plots.

Metrics:

- Recall at stop.
- False completion under target recall.
- Residual relevant documents.
- Review cost and query cost.
- Safe coverage for above-threshold states.
- CONTINUE yield: relevant documents found after following target route/source.
- Comparison to TAR/Total Recall stopping baselines if implemented.

Plots/tables:

- Stop-time recall and false completion distribution.
- Source-route concentration vs residual relevant documents.
- Controller vs TAR-style stopping table.
- Repair/review budget frontier.

## 12. No-Oracle-Leakage Test Plan

Before rerunning main experiments, add tests that make leakage mechanically hard:

- Runtime function input test: call controller and repair planner with DataFrames containing forbidden fields (`oracle_label`, `oracle_total`, `recall`, `bounded_oracle_recall`, `undiscovered_true_item_count`, `new_true_items`) and require either field stripping or a hard error.
- Monkeypatch oracle test: randomize oracle labels after runtime decisions are written; runtime decisions must be byte-identical.
- Decision artifact test: hash `runtime_trace.jsonl` and `runtime_decisions.jsonl` before post-hoc scoring; scorer must not rewrite them.
- Route inventory freeze test: manifest hash must be stored in every runtime artifact and must match the committed manifest.
- Repair target freeze test: selected targets must be written before scorer produces `new_true_items`.
- Legacy exclusion test: fail main pipeline if `controller_validation_v1/run_controller_validation_v1.py::decision` or any function with a `new_true_items` decision argument is imported into the main runner.

## 13. Phased Implementation Plan

### Milestone 1: Schema and Guardrails

- Add route inventory, runtime state, runtime decision, and post-hoc score schemas.
- Add a runtime-field sanitizer/validator.
- Add no-oracle-leakage unit tests.
- Mark the v1 controller script as legacy/deprecated in docs or a module-level warning.

### Milestone 2: Requests/urllib3 Manifest Refactor

- Move source files and route definitions into frozen manifests.
- Refactor requests/urllib3 scripts to load manifests.
- Preserve current behavior and rerun smoke tests to verify same or explainably changed outputs.

### Milestone 3: Runtime/Post-Hoc Split

- Split each experiment into:
  - trace builder,
  - runtime state builder,
  - controller decider,
  - repair planner,
  - post-hoc scorer,
  - metric aggregator.
- Ensure runtime decisions are written before post-hoc oracle files are loaded.

### Milestone 4: Reproduce Current Repository Results

- Rerun `main_3seed.yaml`, `full_200seed.yaml`, and `sensitivity.yaml` through the refactored pipeline.
- Regenerate CSV/JSON exports, Figure 3, Figure 4, and supplement tables from the new artifacts.
- Compare old vs new metrics and document any differences.

### Milestone 5: WebArena/BrowserGym Pilot

- Implement trace adapter and route/source mapping.
- Run a smoke test on a small fixed task list.
- Verify false completion definition with official evaluator success.
- Add pilot plots and decide whether it is strong enough for main paper or supplement.

### Milestone 6: TREC Total Recall Pilot

- Implement topic/qrels/retrieval adapter.
- Run a small topic set at target recall 0.90 and 0.95.
- Compare against simple stopping/TAR baselines if available in time.
- Add high-recall audit plots/tables.

### Milestone 7: Paper Update

- Rewrite experiments around the evidence chain:
  - false completion exists,
  - source-only support can mislead,
  - source-route geometry exposes mismatch,
  - eligibility is not proof,
  - full controller is safe and actionable,
  - residual repair has gain-cost tradeoffs.
- Keep generated policy/code tasks as supplement sanity checks unless fully migrated.
- Ensure claims remain bounded: no universal completion guarantee, pattern-defined repo oracle, residual-potential is not optimal active search.

## 14. Immediate Recommendation

Do not delete or rewrite the existing experiment suite yet.  The right next step is to add schema guardrails and refactor requests/urllib3 into manifest-driven runtime/post-hoc-separated pipelines.  That gives a scientifically cleaner basis for rerunning the existing results and for adding WebArena/BrowserGym and TREC without changing the paper's core claim.

