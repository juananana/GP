# Oracle Second-Review Status

This file records the review state of real-repository closed-world oracles used
in the AAAI false-convergence experiments. It is intentionally conservative:
the current entries do not claim independent human double annotation.

| task | repository | fixed commit | oracle file | current size | construction status | second-review status | additions | removals | disputed |
| --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | ---: |
| T4 Click deprecation audit | `https://github.com/pallets/click` | `8a1b1a33d739be05b7e91251e3c0dde77c5e152f` | `results/T4_real_repo_click_deprecation_oracle.json` | 149 | script-built line oracle from bounded implementation, tests, docs, and changelog files | TODO: independent reviewer has not produced a signed diff | TBD | TBD | TBD |
| T5 Requests TLS audit | `https://github.com/psf/requests` | `1190afd14fca74292946d62c4c8169880a47ff67` | `results/T5_real_repo_requests_tls_oracle.json` | 304 | script-built line oracle from bounded TLS implementation, tests, cert fixtures, docs, and changelog files | TODO: independent reviewer has not produced a signed diff | TBD | TBD | TBD |
| T6 itsdangerous timed signing audit | `https://github.com/pallets/itsdangerous` | `672971d66a2ef9f85151e53283113f33d642dabd` | `results/T6_real_repo_itsdangerous_timed_signing_oracle.json` | 160 | regex/manual-policy constructed line oracle from bounded timed-signing implementation, tests, docs, exports, and changelog files | TODO: independent reviewer has not produced a signed diff | TBD | TBD | TBD |

## Required Review Protocol

1. Freeze each source repository at the commit above.
2. Give the reviewer only the task statement, bounded repository files, and the
   current oracle CSV/JSON, not agent outputs or score summaries.
3. Ask the reviewer to produce three explicit sets:
   `reviewer_2_added`, `reviewer_2_removed`, and `reviewer_2_disputed`.
4. Resolve disputed lines into a final oracle with a written rationale.
5. Update the table above with final counts and save the signed diff next to
   this status file.

## Current Paper Use

Until the review protocol is complete, the paper should describe these oracles
as bounded line-level oracles constructed from fixed repository snapshots and
should list independent second review as a remaining validity limitation rather
than as completed evidence.
