# Source-only vs Source-route Ablation

This export is diagnostic rather than a new oracle rule.  The source-only
column asks whether all source families were touched; source-route additionally
asks whether evidence was produced under the declared route lenses.  Oracle
recall is used only after the stop state is fixed.

## Stop-state diagnostic

| task             |   source_only_support |   source_route_support |   source_route_gini |   base_recall | source_only_would_be_eligible   | source_route_eligible   | false_certification_if_source_only_safe   |
|:-----------------|----------------------:|-----------------------:|--------------------:|--------------:|:--------------------------------|:------------------------|:------------------------------------------|
| policy_docset_v1 |                     1 |               0.25     |            0.770833 |      0.708333 | True                            | False                   | True                                      |
| code_repo_v1     |                     1 |               0.333333 |            0.75     |      0.3      | True                            | False                   | True                                      |
| requests         |                     1 |               0.25     |            0.888514 |      0.104027 | True                            | False                   | True                                      |
| urllib3          |                     1 |               0.2      |            0.91513  |      0.193133 | True                            | False                   | True                                      |

## Repair-policy granularity summary

| task             | granularity         | repair_policy      |   mean_new_true_items |
|:-----------------|:--------------------|:-------------------|----------------------:|
| code_repo_v1     | source_only         | random             |                13     |
| code_repo_v1     | source_route        | random             |                 4.315 |
| code_repo_v1     | source_route_action | random             |                 4.315 |
| policy_docset_v1 | source_only         | random             |                 7     |
| policy_docset_v1 | source_route        | random             |                 2.025 |
| policy_docset_v1 | source_route_action | random             |                 2.025 |
| code_repo_v1     | source_only         | high_potential     |                13     |
| code_repo_v1     | source_route        | high_potential     |                 5     |
| code_repo_v1     | source_route_action | high_potential     |                 5     |
| policy_docset_v1 | source_only         | high_potential     |                 7     |
| policy_docset_v1 | source_route        | high_potential     |                 0     |
| policy_docset_v1 | source_route_action | high_potential     |                 0     |
| code_repo_v1     | source_only         | residual_potential |                13     |
| code_repo_v1     | source_route        | residual_potential |                 9     |
| code_repo_v1     | source_route_action | residual_potential |                 9     |
| policy_docset_v1 | source_only         | residual_potential |                 7     |
| policy_docset_v1 | source_route        | residual_potential |                 4     |
| policy_docset_v1 | source_route_action | residual_potential |                 4     |
