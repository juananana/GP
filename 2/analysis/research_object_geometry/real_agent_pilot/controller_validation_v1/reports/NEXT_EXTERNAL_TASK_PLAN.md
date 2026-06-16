# Next External Task Plan

## Preferred Task

Use a second real Python repo with a completion-audit objective, not a generated item-discovery task.

Recommended target: a small installed package or vendored repo with natural audit routes such as:

- exception-handling audit;
- timeout / retry / resource cleanup audit;
- compatibility or deprecation audit;
- security-relevant argument validation audit.

## Why This Task

It keeps natural source-route strata while moving beyond the current `requests` snapshot. The goal is to test whether evidence-condition control avoids false certification across a different codebase.

## Oracle Construction

1. Freeze a local repo snapshot.
2. Define route patterns before running trajectories.
3. Build an offline exhaustive oracle by scanning all files and routes.
4. Hide oracle labels, oracle totals, and missing mass from challenger selection.
5. Score only after trajectories and challenger targets are fixed.

## Claim-Verification Variant

If feasible, add a claim verification completion audit:

```text
Given a repo-level claim such as "all network calls use timeouts" or
"all public parsing paths handle malformed input", certify whether the audit is complete.
```

Oracle construction then labels claim-supporting and claim-violating evidence sites offline. This would help show that the research object is workload-unknown completion certification, not only item discovery.

## Go / No-Go

Go if the controller reduces false certification under localized evidence and still uses `ABSTAIN` or `CONTINUE` when broad evidence remains productive.

Downgrade method claims if high-potential-only again explains most challenger gains.
