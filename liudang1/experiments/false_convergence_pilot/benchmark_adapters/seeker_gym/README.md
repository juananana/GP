# SeekerGym Adapter TODO

This directory is a scaffold for future public-benchmark validation.

Status: not run. No SeekerGym numbers are included in the paper.

## Goal

Convert SeekerGym episodes into the local closed-world discovery format:

- `oracle.json`
- `itemsets.json`
- `run_cost_logs/*.json`

The completion-certificate evaluator can then consume the converted files
without seeing oracle labels during certificate decisions.

## Required Inputs

Place or point to a local SeekerGym checkout or exported dataset snapshot.
Record the exact source:

- upstream URL
- commit hash or release tag
- task split
- model
- prompt
- budget
- seed

## Expected Command

```powershell
python experiments\false_convergence_pilot\benchmark_adapters\seeker_gym\prepare_seekergym.py `
  --seekergym-root path\to\seekergym `
  --split validation `
  --out-dir experiments\false_convergence_pilot\benchmark_runs\seekergym
```

## TODO Before Reporting Results

- Verify SeekerGym license and citation.
- Map SeekerGym success/completeness labels to closed-world item recall.
- Save exact prompts and model IDs.
- Save token, tool-call, wall-clock, and review-cost logs.
- Run scorer and completion certificate.
- Only then add results to the paper.
