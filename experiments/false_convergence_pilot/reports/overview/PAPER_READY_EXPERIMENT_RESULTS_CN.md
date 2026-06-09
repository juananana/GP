# Paper-Ready Experiment Results

Date: 2026-06-09

This report is generated from offline score summaries and protocol outputs. No oracle is exposed to blind agents or summarizers; oracle labels are used only by the scorer and table builder.

## Main real-repository result

Across two real repository audit families and three blind seeds per family, standard summarization repeatedly reports completion while recall remains far below full coverage. T3 mainly exposes aggregation-stage loss: raw union recovers nearly all oracle items but standard summarization discards many of them. T4 is harder: even raw union remains incomplete, showing search-stage coverage failure in addition to aggregation risk.

| family | method | n | mean recall | min recall | max recall | mean precision | false stops | completed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T3 Click | evidence_preserving_protocol | 3 | 0.877 | 0.805 | 0.993 | 0.840 | 2/3 | 3/3 |
| T3 Click | majority_consensus | 3 | 0.830 | 0.758 | 0.953 | 0.907 | 0/3 | 0/3 |
| T3 Click | raw_union | 3 | 0.998 | 0.993 | 1.000 | 0.675 | 0/3 | 0/3 |
| T3 Click | standard_summarizer_blind | 3 | 0.709 | 0.685 | 0.745 | 0.997 | 3/3 | 3/3 |
| T3 Click | union_preserving_blind | 3 | 0.998 | 0.993 | 1.000 | 0.675 | 0/3 | 3/3 |
| T4 Requests | evidence_preserving_protocol | 3 | 0.776 | 0.750 | 0.799 | 0.712 | 3/3 | 3/3 |
| T4 Requests | majority_consensus | 3 | 0.685 | 0.678 | 0.701 | 0.724 | 2/3 | 2/3 |
| T4 Requests | raw_union | 3 | 0.844 | 0.829 | 0.859 | 0.668 | 2/3 | 2/3 |
| T4 Requests | standard_summarizer_blind | 3 | 0.546 | 0.368 | 0.648 | 0.775 | 3/3 | 3/3 |
| T4 Requests | union_preserving_blind | 3 | 0.659 | 0.303 | 0.845 | 0.678 | 3/3 | 3/3 |

## Completion certificate v0

| family | n | unsafe_to_stop | requires_audit |
| --- | --- | --- | --- |
| T3 Click | 3 | 3 | 0 |
| T4 Requests | 3 | 3 | 0 |

The certificate refuses to certify completion for every real-repository seed. This is the desired behavior for a completion-risk detector: it should not convert high agreement or high-confidence final prose into a closed-world completion claim.

## Source-aware audit v2

| family | n | candidate recall | candidate precision | filter recall | filter precision | sweep recall | sweep precision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T3 Click | 3 | 0.998 | 0.660 | 0.998 | 1.000 | 1.000 | 1.000 |
| T4 Requests | 3 | 0.849 | 0.652 | 0.849 | 1.000 | 1.000 | 1.000 |

The candidate filter is an offline audit-policy prototype over already observed candidates. The source sweep is a bounded upper bound, not a blind LLM run.

## Protocol cost proxy

| case | consensus recall | full recall | full precision | false stop | audit actions | recovered TP | actions/TP |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T4_real_repo_click_seed01_blind | 0.953 | 0.993 | 0.955 | False | 57 | 6 | 9.500 |
| T4_real_repo_click_seed02_blind | 0.758 | 0.805 | 0.805 | True | 99 | 7 | 14.143 |
| T4_real_repo_click_seed03_blind | 0.779 | 0.832 | 0.761 | True | 103 | 8 | 12.875 |
| T5_real_repo_requests_tls_seed01_blind | 0.701 | 0.799 | 0.706 | True | 98 | 30 | 3.267 |
| T5_real_repo_requests_tls_seed02_blind | 0.678 | 0.750 | 0.715 | True | 98 | 22 | 4.455 |
| T5_real_repo_requests_tls_seed03_blind | 0.678 | 0.780 | 0.716 | True | 96 | 31 | 3.097 |

The cost column is a proxy: audit queue size plus one unit for each triggered holdout. It should be reported as proxy cost until token and wall-clock logs are complete.

## Suggested paper wording

Use: `Consensus and high-confidence summarization are not reliable completion certificates for closed-world multi-agent discovery. In two real-repository line-level audit families, standard summarization false-stops in 6/6 blind seeds; a completion-risk certificate refuses to certify completion in all real-repository seeds.`

Avoid: `The protocol solves completion.` The current evidence supports problem existence, failure mechanism separation, and a promising risk-detection/audit direction.
