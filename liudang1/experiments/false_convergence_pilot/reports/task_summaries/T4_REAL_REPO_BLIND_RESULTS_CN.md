# T4 Click Real-Repo Blind Validation 结果

日期：2026-06-08

## 一句话结论

T4 真实仓库盲评没有形成 strict False Convergence 阳性，但它补上了一个很重要的真实任务族证据：在 real-repo line-level audit 中，`consensus` 可以达到高 precision 且刚过 recall 阈值，`raw union` 能提高 recall 但会带来大量误报，而 evidence-preserving protocol 能在较高 recall 和较高 precision 之间取得更稳的折中。

更通俗地说：

> T4 不是“大家都错得很离谱”的样本，而是“真实任务里最麻烦的权衡样本”：多收一点能找回漏项，但也会混进噪声；直接相信 consensus 又可能漏掉边界项。

## 运行设置

任务：

- 真实仓库：Click
- commit：`8a1b1a33d739be05b7e91251e3c0dde77c5e152f`
- oracle size：`149`
- 目标：deprecated API surface line-level audit

盲评 runs：

- `T4_G3_seed01_agent01`
- `T4_G3_seed01_agent02`
- `T4_G3_seed01_agent03`
- `T4_G6_holdout_seed01`

重要说明：

- 主线程已经看过 oracle，因此没有直接产出 blind itemsets。
- 四个 blind runs 由独立 worker 执行。
- `T4_real_repo_click_seed01_smoke_*` 仍然只作为 scorer compatibility test，不计入实验结果。

## 单个 run 结果

| run | found | TP | FP | recall | precision | confidence | false stop |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T4_G3_seed01_agent01 | 149 | 148 | 1 | 0.993 | 0.993 | 0.820 | false |
| T4_G3_seed01_agent02 | 149 | 142 | 7 | 0.953 | 0.953 | 0.740 | false |
| T4_G3_seed01_agent03 | 149 | 104 | 45 | 0.698 | 0.698 | 0.780 | true |
| T4_G6_holdout_seed01 | 149 | 140 | 9 | 0.940 | 0.940 | 0.720 | true |

这里有两个信号：

- agent01 很强，几乎完整恢复 oracle。
- agent03 和 holdout 都自报完成但 recall 不足，说明真实任务中单个 agent 的 self-stop 仍不可靠。

## G3 聚合结果

| policy | found | TP | FP | recall | precision | 解释 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| majority consensus | 143 | 142 | 1 | 0.953 | 0.993 | 高精度，刚过 recall 阈值，但仍漏 7 个真项 |
| raw union | 199 | 148 | 51 | 0.993 | 0.744 | 召回几乎完整，但误报很多 |
| holdout scout | 149 | 140 | 9 | 0.940 | 0.940 | 独立复查本身也不完整 |
| evidence-preserving protocol | 155 | 148 | 7 | 0.993 | 0.955 | 通过审计 singleton 恢复 6 个 TP，同时避免 44 个 raw union FP |

T4 的核心价值就在这张表：它说明 `raw union` 不是解决方案，但 `consensus` 也不是充分完成证书。好的方法应该把 singleton evidence 变成审计对象，而不是直接丢弃或直接并入最终答案。

## Completion Certificate v0 结果

certificate v0 对 T4 输出：

```text
unsafe_to_stop
```

触发 flags：

- `low_confidence`
- `singleton_missing_mass`
- `chao_unseen_mass`

这个判断是合理的。虽然 consensus recall 已经达到 `0.953`，但 G3 的平均 confidence 只有 `0.780`，平均 Jaccard 只有 `0.670`，singleton ratio 高，raw union precision 也明显下降。这说明当前状态不是一个“可以放心完成”的状态，而是一个“需要审计少数派证据”的状态。

## T4 支持了什么

- 支持真实任务族外部有效性：不是只有合成 T1/T2 才有 completion-risk 问题。
- 支持 precision-recall tradeoff：consensus 高精度但漏项，union 高召回但噪声多。
- 支持 evidence-preserving protocol：T4 中 full protocol 相比 raw union 避免 `44` 个 FP，同时达到 `0.993` recall。
- 支持 completion certificate 的保守性：它没有把 T4 直接认证为完成，而是要求审计。

## T4 没有支持什么

- 不能说 T4 是 strict False Convergence 阳性。因为 G3 consensus recall 是 `0.953`，没有低于 `theta = 0.95`。
- 不能说 high agreement 导致共同盲点。T4 的 mean Jaccard 只有 `0.670`，不是高一致场景。
- 不能说 holdout 一定更强。T4 holdout recall 只有 `0.940`，低于 G3 consensus。
- 不能说 raw union 可直接作为最终答案，因为 raw union precision 只有 `0.744`。

## 对论文的写法建议

T4 应该放在 stronger validation 或 real-world validation 小节中，定位为：

> Real-repo precision-recall boundary case.

可以这样写：

> On a real Click repository audit, the G3 consensus narrowly satisfies the recall threshold but still misses seven oracle items. Raw union recovers most missing items but introduces 51 false positives. The evidence-preserving protocol recovers six additional true positives over consensus while avoiding 44 false positives relative to raw union, suggesting that the practical role of the controller is not merely to increase recall but to convert minority evidence into auditable risk.

中文理解：

> T4 让论文更真实：现实任务不一定总是 strict false convergence，但 completion risk 仍然存在，而且会以 precision-recall 权衡的形式出现。

## 下一步

T4 seed01 已经值得写进论文，但还不够。下一步优先级：

1. 跑 T4 seed02/03，看这个 precision-recall boundary 是否稳定。
2. 对 T4 G3 packet 跑 standard summarizer 与 union-preserving summarizer。
3. 增加 prompt-diverse G3，测试是否能降低 agent03 这类低质量输出造成的 singleton 噪声。
4. 加真实 token / wall-clock 成本，替换当前 proxy cost。
