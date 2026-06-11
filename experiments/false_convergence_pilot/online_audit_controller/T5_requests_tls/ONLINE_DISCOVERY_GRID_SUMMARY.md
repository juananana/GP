# Online Discovery Grid Summary

This file summarizes completed online discovery runs only. It is not a
post-audit controller result: online verifier/holdout audit policies remain
unrun.

## Per-Condition Means

| condition | n | union R | union R sd | consensus R | consensus R sd | precision | tokens | wall-clock s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| homogeneous | 5 | 0.732 | 0.006 | 0.678 | 0.005 | 0.710 | 212677 | 187.033 |
| prompt-diverse | 5 | 0.724 | 0.011 | 0.662 | 0.019 | 0.709 | 212699 | 136.966 |
| source-partitioned | 5 | 0.724 | 0.010 | 0.000 | 0.000 | 0.737 | 73690 | 62.239 |
| independent-context | 5 | 0.732 | 0.013 | 0.626 | 0.007 | 0.729 | 143227 | 109.608 |

## Per-Seed Rows

| seed | condition | Jaccard | consensus R | union R | precision | tokens | wall-clock s | source |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| seed04 | homogeneous | 0.814 | 0.684 | 0.720 | 0.709 | 212090 | 135.939 | online_blind_validation_seed04 |
| seed04 | independent-context | 0.282 | 0.628 | 0.737 | 0.730 | 143494 | 93.782 | online_audit_controller_discovery |
| seed04 | prompt-diverse | 0.777 | 0.688 | 0.737 | 0.718 | 212674 | 121.180 | online_blind_validation_seed04 |
| seed04 | source-partitioned | 0.000 | 0.000 | 0.714 | 0.719 | 73861 | 59.863 | online_blind_validation_seed04 |
| seed05 | homogeneous | 0.826 | 0.674 | 0.734 | 0.701 | 212478 | 137.971 | online_audit_controller_discovery |
| seed05 | independent-context | 0.280 | 0.615 | 0.734 | 0.729 | 142786 | 92.517 | online_audit_controller_discovery |
| seed05 | prompt-diverse | 0.765 | 0.645 | 0.730 | 0.733 | 212060 | 139.284 | online_audit_controller_discovery |
| seed05 | source-partitioned | 0.000 | 0.000 | 0.724 | 0.736 | 73798 | 56.266 | online_audit_controller_discovery |
| seed06 | homogeneous | 0.798 | 0.671 | 0.740 | 0.710 | 212173 | 132.113 | online_audit_controller_discovery |
| seed06 | independent-context | 0.285 | 0.635 | 0.753 | 0.736 | 143644 | 94.115 | online_audit_controller_discovery |
| seed06 | prompt-diverse | 0.770 | 0.661 | 0.730 | 0.681 | 213851 | 146.129 | online_audit_controller_discovery |
| seed06 | source-partitioned | 0.000 | 0.000 | 0.737 | 0.732 | 73935 | 54.328 | online_audit_controller_discovery |
| seed07 | homogeneous | 0.831 | 0.678 | 0.734 | 0.719 | 213870 | 398.752 | online_audit_controller_discovery |
| seed07 | independent-context | 0.289 | 0.632 | 0.720 | 0.735 | 142719 | 178.091 | online_audit_controller_discovery |
| seed07 | prompt-diverse | 0.797 | 0.638 | 0.707 | 0.719 | 212892 | 138.271 | online_audit_controller_discovery |
| seed07 | source-partitioned | 0.000 | 0.000 | 0.711 | 0.771 | 73423 | 72.315 | online_audit_controller_discovery |
| seed08 | homogeneous | 0.792 | 0.681 | 0.734 | 0.712 | 212775 | 130.390 | online_audit_controller_discovery |
| seed08 | independent-context | 0.287 | 0.622 | 0.717 | 0.717 | 143493 | 89.536 | online_audit_controller_discovery |
| seed08 | prompt-diverse | 0.783 | 0.678 | 0.717 | 0.694 | 212016 | 139.966 | online_audit_controller_discovery |
| seed08 | source-partitioned | 0.000 | 0.000 | 0.734 | 0.726 | 73431 | 68.421 | online_audit_controller_discovery |
