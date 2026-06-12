# v2 Pre-Audit Feature Audit

This table audits the declared v2 offline diagnostic features. It is a design
review of whether each feature is eligible for a future portable certificate,
not evidence that the feature already generalizes.

| Feature | Formula / meaning | Source | Pre-audit? | Uses oracle? | Uses holdout? | Encodes repo/task identity? | Encodes task size? | Portable? | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nominal_agent_count | number of agents in state | run metadata | yes | no | no | no | weakly | partial | isolate |
| mean_confidence | mean self-reported confidence | agent run logs | yes | no | no | no | no | partial | keep as baseline signal |
| output_jaccard | pairwise item-set Jaccard | agent item sets | yes | no | no | no | no | yes | keep |
| source_overlap | pairwise source-set Jaccard | candidate source ids | yes | no | no | path distribution may leak domain | no | partial | keep, audit |
| source_coverage | covered source files / bounded source files | source universe and candidate source ids | yes | no | no | repository structure can leak | yes | partial | normalize/audit |
| query_similarity | pairwise action/query Jaccard | candidate/action logs | yes | no | no | prompt/task wording can leak | no | partial | keep, audit |
| search_path_overlap | pairwise scanned-file Jaccard | candidate/action logs | yes | no | no | directory names can leak | yes | partial | keep, audit |
| marginal_discovery_gain_last | last agent's absolute new candidate count | ordered agent item sets | yes | no | no | no | yes | weak | isolate/remove from portable |
| marginal_discovery_gain_mean | mean absolute new candidate count | ordered agent item sets | yes | no | no | no | yes | weak | isolate/remove from portable |
| novelty_decay | 1 - last gain / first gain | ordered agent item sets | yes | no | no | no | no | yes | keep |
| singletons_f1 | absolute singleton count | support counts | yes | no | no | no | yes | weak | isolate/remove from portable |
| doubletons_f2 | absolute doubleton count | support counts | yes | no | no | no | yes | weak | isolate/remove from portable |
| singleton_ratio | singleton count / unique candidates | support counts | yes | no | no | no | less | yes | keep |
| doubleton_ratio | doubleton count / unique candidates | support counts | yes | no | no | no | less | yes | keep |
| per_source_singleton_density | mean singleton rate per source | support counts and source ids | yes | no | no | source structure can leak | less | partial | keep, audit |
| good_turing_missing_mass | f1 / total incidences | support counts | yes | no | no | no | no | yes | keep |
| chao_missing_ratio | Chao unseen / observed+unseen | support counts | yes | no | no | no | no | yes | keep |
| corr_adjusted_chao_missing_ratio | Chao ratio adjusted by effective exploration size | support counts and overlap | yes | no | no | no | no | yes | keep |
| effective_exploration_size | k / (1 + (k-1)rho) | agent count and output Jaccard | yes | no | no | no | weakly | yes | keep |

## Forbidden From Pre-Audit Model

The following columns are present only for offline scoring or bookkeeping and
must not enter the pre-audit risk model: `state_id`, `task_id`, `repository`,
`task_family`, `seed`, `split`, `run_ids`, `collection_mode`, `found`,
`true_positive`, `false_positive`, `recall`, `precision`, `f1_score`,
`residual_missing_mass`, `unsafe`, `token_input`, `token_output`, `tool_calls`,
`wall_clock`, and any verified singleton or holdout-gain label.

## Current Interpretation

The portable feature family is not yet validated. The current v2 diagnostic has
strong in-distribution performance, but metadata-only shortcuts are also strong
and leave-one-repository/task-family validation cannot certify any held-out
state. The paper should therefore remain on the false-convergence diagnosis
route until new online blind data demonstrates transferable signal.
