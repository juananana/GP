# Claim Verification Task Plan

## Purpose

Test whether the research object extends beyond item discovery by using a claim verification completion audit.

## Candidate Task

Given a repo-level claim such as:

```text
All network-facing calls either set a timeout or route through a retry/timeout policy.
```

The workflow must decide whether the audit is complete, not merely enumerate matching items.

## Source-Route Strata

Sources are repo files or modules. Routes are claim-specific audit lenses, such as timeout, retry, exception path, configuration default, and test coverage route.

## Oracle Construction

Build offline labels for:

- supporting evidence;
- contradicting evidence;
- unresolved evidence requiring further audit.

The oracle is hidden until trajectories and challenger choices are fixed.

## Limitation

This task needs more careful human or semi-manual oracle design than pattern-defined item discovery. If time is limited, keep it as a planned external validity extension rather than a required result.
