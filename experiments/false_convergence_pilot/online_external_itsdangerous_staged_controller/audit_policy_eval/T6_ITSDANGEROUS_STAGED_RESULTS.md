# T6 itsdangerous External Staged Controller Results

The staged controller was frozen before evaluating this new repository.

| policy | n | pre R | post R | precision | F1 | recovered TP | introduced FP | audit tok | e2e tok | FCR | safe cov | abstain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no-audit | 9 | 0.569 | 0.569 | 0.841 | 0.679 | 0.0 | 0.0 | 0 | 31168 | 0.000 | 0.000 | 1.000 |
| singleton-audit | 9 | 0.569 | 0.867 | 0.719 | 0.786 | 47.8 | 26.1 | 8909 | 40077 | 0.000 | 0.000 | 1.000 |
| source-partitioned-review | 9 | 0.569 | 0.871 | 0.733 | 0.796 | 48.3 | 22.1 | 11495 | 42663 | 0.000 | 0.000 | 1.000 |
| staged-controller | 9 | 0.569 | 0.879 | 0.709 | 0.785 | 49.7 | 29.6 | 18507 | 49675 | 1.000 | 0.000 | 0.889 |
| always-holdout | 9 | 0.569 | 0.890 | 0.675 | 0.768 | 51.4 | 39.9 | 41218 | 72386 | 0.000 | 0.000 | 1.000 |
