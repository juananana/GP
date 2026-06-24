# Threshold and Budget Sensitivity

These tables report the complete sweep, not a selected optimum.  The false
certification label is computed only after each runtime decision is fixed.

## Safety-cost frontier summary

| task     | challenger               |   min_fcr |   max_continue_rate |   max_abstain_rate |   max_repair_gain |   min_cost |   max_cost |
|:---------|:-------------------------|----------:|--------------------:|-------------------:|------------------:|-----------:|-----------:|
| requests | free_search_continuation |         0 |                   1 |              0.095 |           207.165 |    861.69  |    6605.19 |
| requests | high_potential           |         0 |                   1 |              0     |           236     |    696     |    6914    |
| requests | low_discovery            |         0 |                   1 |              0     |           116     |    696     |    3187    |
| requests | low_exposure             |         0 |                   1 |              0     |           116     |    696     |    3187    |
| requests | random                   |         0 |                   1 |              0.365 |            89.345 |    730.93  |    5564.3  |
| requests | residual_potential       |         0 |                   1 |              0     |           244     |    696     |    7304    |
| urllib3  | free_search_continuation |         0 |                   1 |              0.275 |           259.325 |    898.11  |    7420.9  |
| urllib3  | high_potential           |         0 |                   1 |              0     |           374     |    533     |    8049    |
| urllib3  | low_exposure             |         0 |                   1 |              0     |           288     |   1093     |    9084    |
| urllib3  | random                   |         0 |                   1 |              0.36  |           152.825 |    811.345 |    6665.61 |
| urllib3  | residual_potential       |         0 |                   1 |              0     |           436     |    533     |    8867    |
