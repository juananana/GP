# Completion Certificate v0 中文结果

日期：2026-06-08

## 一句话结论

v0 证书没有把当前这些高风险 run 轻易判成“已经完成”。它会把少数派证据、missing-mass 信号和高一致共同盲点转成 `requires_audit` 或 `unsafe_to_stop`，比单看 confidence / overlap 更适合作为论文里的停止条件方向。

## 当前结果怎么读

- 可报告 G3 seed 数：`12`。
- 其中 consensus recall 低于 `0.95` 的 seed 数：`9`。
- certificate v0 输出非 certified 的 seed 数：`12`。
- certificate v0 的 false certification 数：`0`。

注意：这不是说 v0 已经是最终方法。它现在更像一个保守的“别急着停”证书，价值在于把 false convergence 从隐藏错误变成显式审计信号。

## 逐 seed 结果

| case | seed | consensus recall | union precision | mean jaccard | f1 singleton | GT mass | Chao missing | certificate | flags |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| T1_hard_expanded | seed01 | 0.629 | 1.000 | 0.752 | 13 | 0.165 | 0.690 | unsafe_to_stop | singleton_missing_mass, chao_unseen_mass |
| T1_hard_expanded | seed02 | 1.000 | 0.897 | 0.932 | 4 | 0.037 | 0.133 | requires_audit | singleton_missing_mass, chao_unseen_mass, low_effective_independence |
| T1_hard_seed03_completed | seed03 | 1.000 | 0.875 | 0.685 | 5 | 0.052 | 0.023 | requires_audit | singleton_missing_mass |
| T2_policy_docs_seed01 | seed01 | 0.933 | 1.000 | 0.956 | 2 | 0.023 | 0.032 | unsafe_to_stop | singleton_missing_mass, high_agreement_boundary_blindspot_risk, low_effective_independence |
| T2_policy_docs_seed02 | seed02 | 0.933 | 1.000 | 1.000 | 0 | 0.000 | 0.000 | unsafe_to_stop | high_agreement_boundary_blindspot_risk, low_effective_independence |
| T2_policy_docs_seed03 | seed03 | 0.933 | 1.000 | 1.000 | 0 | 0.000 | 0.000 | unsafe_to_stop | high_agreement_boundary_blindspot_risk, low_effective_independence |
| T4_real_repo_click_seed01_blind | seed01 | 0.953 | 0.744 | 0.670 | 56 | 0.125 | 0.172 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |
| T4_real_repo_click_seed02_blind | seed02 | 0.758 | 0.639 | 0.495 | 98 | 0.219 | 0.269 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |
| T4_real_repo_click_seed03_blind | seed03 | 0.779 | 0.642 | 0.505 | 102 | 0.228 | 0.333 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |
| T5_real_repo_requests_tls_seed01_blind | seed01 | 0.701 | 0.661 | 0.645 | 97 | 0.109 | 0.108 | unsafe_to_stop | singleton_missing_mass, chao_unseen_mass |
| T5_real_repo_requests_tls_seed02_blind | seed02 | 0.678 | 0.668 | 0.652 | 97 | 0.111 | 0.121 | unsafe_to_stop | singleton_missing_mass, chao_unseen_mass |
| T5_real_repo_requests_tls_seed03_blind | seed03 | 0.678 | 0.676 | 0.636 | 95 | 0.114 | 0.116 | unsafe_to_stop | low_confidence, singleton_missing_mass, chao_unseen_mass |

## 和简单停止基线相比

| stopping rule | stopped/certified | false certifications | conservative blocks |
| --- | ---: | ---: | ---: |
| certificate_v0_stop | 0 | 0 | 3 |
| chao_stop | 4 | 3 | 2 |
| confidence_stop | 8 | 6 | 1 |
| good_turing_stop | 4 | 3 | 2 |
| overlap_stop | 3 | 3 | 3 |

## 对论文实验的意义

这一步把方法主线从“加一个 holdout agent”升级为“完成性风险估计”。真实仓库 T4 seed01/02/03 中，certificate v0 都没有给出 certified，因此它能稳定避免把高风险状态误报为完成。

T4 smoke 行没有进入可报告统计，因为它是 oracle-generated scorer compatibility test，不能当作 blind-agent result。
