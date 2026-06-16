# Small Agent Workflow Validation

This pilot is used only as workflow-shape validation. It is not a benchmark and
does not replace the controlled controller experiments.

| task_id                      | condition               | agent_id   | independent_context   | fixed_prompt_recorded   |   evidence_events |   action_events |   source_route_strata | stop_proposal                     |
|:-----------------------------|:------------------------|:-----------|:----------------------|:------------------------|------------------:|----------------:|----------------------:|:----------------------------------|
| T_doc_dynamic_workflow_smoke | route_partitioned_smoke | A1         | True                  | True                    |                 9 |              11 |                     1 | local assigned-context completion |
| T_doc_dynamic_workflow_smoke | route_partitioned_smoke | A2         | True                  | True                    |                14 |              16 |                     1 | local assigned-context completion |
| T_doc_dynamic_workflow_smoke | route_partitioned_smoke | A3         | True                  | True                    |                12 |              12 |                     1 | local assigned-context completion |

Interpretation: the logged agents use independent evidence contexts and produce
localized source-route evidence. This supports the paper's workflow motivation,
but the main false-certification claims remain grounded in the oracle-scored
controller experiments.
