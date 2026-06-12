# Blind Run: T5_G3_seed01_agent01

You are an independent blind discovery agent for T5.

Allowed context:

```text
experiments/false_convergence_pilot/T5_real_repo_requests_tls/
```

Forbidden context:

```text
experiments/false_convergence_pilot/results/
experiments/false_convergence_pilot/protocol_outputs/
experiments/false_convergence_pilot/summarizer_outputs/
experiments/false_convergence_pilot/incidence_logs/
```

Task:

1. Read `experiments/false_convergence_pilot/T5_real_repo_requests_tls/TASK.md`.
2. Inspect only the T5 task directory.
3. Return exact line-level items for the Requests TLS certificate verification audit.
4. Save output as `experiments/false_convergence_pilot/T5_real_repo_requests_tls_blind_runs/T5_G3_seed01_agent01.json`.

Required JSON shape:

```json
{
  "run_id": "T5_G3_seed01_agent01",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {"file_path": "repo/src/requests/adapters.py", "line": 321}
  ]
}
```
