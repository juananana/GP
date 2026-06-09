# Blind T4 Run Prompt

You are running one blind scout for a closed-world discovery experiment.

Run id:

```text
T4_G3_seed01_agent01
```

Allowed directory:

```text
experiments/false_convergence_pilot/T4_real_repo_click/
```

Do not inspect any oracle, score summary, smoke itemset, incidence log, or other experiment result outside the allowed directory.

Task:

1. Read `experiments/false_convergence_pilot/T4_real_repo_click/TASK.md`.
2. Inspect only the allowed task directory.
3. Find exact line-level items that belong to the current deprecated API surface audit.
4. Output JSON only, with this shape:

```json
{
  "run_id": "T4_G3_seed01_agent01",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {"file_path": "repo/src/click/core.py", "line": 1359}
  ]
}
```

Use paths relative to the T4 task root and starting with `repo/`. Include exact line numbers only. Do not include broad file-level answers.
