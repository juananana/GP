# Next-Stage Experiment Plan

## Goal

Upgrade the AAAI experiment section from Requests/Click-only evidence to a
genuine external-validity check for the staged audit controller, without tuning
on the existing Requests or Click results.

## Frozen Controller

The current staged controller is frozen before any new repository result is
scored.

Rules:

1. Start from the conservative consensus final set: items reported by at least
   two discovery agents.
2. Preserve singleton evidence as an audit queue; do not silently drop it.
3. Run singleton verification when the singleton queue is non-empty.
4. Escalate to source-partitioned review when any pre-audit observable condition
   holds:
   - singleton ratio >= 0.10;
   - consensus-to-union ratio <= 0.92;
   - any required source family is absent from the conservative consensus.
5. Escalate to boundary-focused holdout only when the task manifest declares a
   boundary-sensitive source family and source-partitioned review still leaves a
   non-empty unresolved evidence queue.
6. Certify `safe-to-stop` only if no escalation trigger remains, required source
   families are represented, singleton audit has run when needed, mean
   confidence >= 0.75, and all discovery agents report completion.
7. Otherwise abstain and report `requires-audit` or `unsafe-to-stop`.

Frozen online parameters:

- discovery agents per state: 3;
- held-out seeds: 3 minimum, 5 target;
- search budget: 180 items unless otherwise stated in a safe-state sweep;
- max context: 1200--1600 lines per selected file;
- policies compared: no audit, singleton audit, source-partitioned review,
  staged controller, always-holdout.

The thresholds above must not be changed based on Requests, Click, or the new
repository test results. Any future change must be logged as a new controller
version and evaluated on a later held-out task.

## New External Repository

Primary candidate:

- repository: `pallets/itsdangerous`
- rationale: public repository, not used in method design, compact source tree,
  and a bounded timestamp-signing audit can be defined with implementation,
  tests, and documentation evidence.
- task: line-level audit for timestamped signing, max-age expiration,
  `SignatureExpired`, `TimestampSigner`, `TimedSerializer`, and direct docs/tests
  for these behaviors.
- fixed commit: record the cloned HEAD in the task manifest.

Minimum online grid:

- seeds: seed04--seed06;
- discovery configurations: homogeneous, source-partitioned,
  independent-context;
- audit policies: no audit, singleton audit, source-partitioned review, staged
  controller, always-holdout.

## Required Metrics

For every seed/configuration/policy row:

- recall;
- precision;
- F1;
- recovered TP;
- introduced FP;
- audit tokens;
- end-to-end tokens;
- tool calls;
- wall-clock;
- cost per recovered TP;
- abstention decision;
- false certification.

Aggregate metrics:

- mean and seed-clustered bootstrap 95% CI;
- paired comparison of staged controller against singleton audit,
  source-partitioned review, and always-holdout;
- FCR, safe coverage, abstention rate;
- threshold sensitivity for certification gates.

## Safe-State Sweep

The new repository must include a small safe-state sweep. Increase budget and/or
agent count on a frozen subset to attempt at least one state with recall >=
0.95. If no safe state is reached, report safe coverage as 0 and do not claim
automatic stopping.

## Oracle Review

Required artifacts:

- `initial_candidates`;
- `reviewer_1_kept`;
- `reviewer_2_added`;
- `reviewer_2_removed`;
- `ambiguous_cases`;
- `resolution_rule`;
- `agreement_rate`;
- `final_oracle_size`.

Current limitation: no independent human reviewer is available in this run.
Automated or model-assisted second pass may be logged, but the paper must not
call it independent human double annotation.

## Second Model Subset

Run a small subset if API/model access is available:

- one seed on Requests or new repository;
- homogeneous and source-partitioned;
- singleton audit, staged controller, always-holdout.

If not run, leave a TODO and do not make model-general claims.

## Public Benchmark

Try SeekerGym first. If the local schema/checkout remains unavailable, keep only
the existing TODO manifest and do not claim benchmark validation.

## Paper Updates

1. Section 4 remains `Evidence-Preserving Staged Audit Controller`.
2. Add Algorithm 1 for singleton -> source-partitioned -> boundary holdout ->
   stop/abstain.
3. Replace the parallel-module workflow figure with a staged workflow figure
   when a polished asset is available.
4. Replace Figure 3 with a multi-panel Requests/Click/new-repo Recall-Cost plot
   after the new repository run completes.
5. Move v1/v2 details and full diagnostic tables to supplementary.
6. Rewrite the abstract around the staged controller and external-validity
   result, not v1/v2 iteration history.

