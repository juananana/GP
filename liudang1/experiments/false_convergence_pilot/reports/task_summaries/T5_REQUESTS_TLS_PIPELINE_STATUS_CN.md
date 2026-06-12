# T5 Requests TLS/certificate 真实仓库任务族结果

日期：2026-06-08

## 一句话结论

T5 已完成 `seed01/02/03` 三个真实 blind seeds。它没有简单复刻 T4 的“多数证据已经在 union 里、summarizer 剪掉”的模式，而是展示了第二真实仓库上的更难边界：G3 agents 本身覆盖不足，raw union 也只能达到 `0.829-0.859` recall；standard summarizer 又会进一步压缩结果，并在 `3/3` seeds 中高置信 false stop。

这对论文很有价值：T4 证明 aggregation-stage false stop，T5 证明真实任务中还会出现“搜索覆盖不足 + 汇总压缩 + 停止风险”混合形态。

## 任务定义

- 仓库：`psf/requests`
- commit：`1190afd14fca74292946d62c4c8169880a47ff67`
- 任务：TLS certificate verification / CA bundle / client certificate / SSL error handling / tests / docs line-level audit
- oracle size：`304`

## 三 seed 核心结果

| seed | consensus recall | standard recall | raw union recall | holdout recall | certificate |
| --- | ---: | ---: | ---: | ---: | --- |
| seed01 | 0.701 | 0.368 | 0.859 | 0.750 | unsafe_to_stop |
| seed02 | 0.678 | 0.622 | 0.845 | 0.688 | unsafe_to_stop |
| seed03 | 0.678 | 0.648 | 0.829 | 0.763 | unsafe_to_stop |

均值：

- consensus recall：`0.685`
- standard summarizer recall：`0.546`
- raw union recall：`0.844`
- holdout recall：`0.734`
- certificate unsafe-to-stop：`3/3`

## 机制解释

T5 的关键不是“union 一下就全救回来”，而是：

- standard summarizer 连续 `3/3` self-report completion，但 recall 明显低于完成阈值。
- raw union 比 consensus 明显更好，说明 aggregation loss 仍然存在。
- raw union 仍低于 `0.95`，说明很多真项没有被 G3 覆盖，搜索/覆盖不足也稳定存在。
- completion certificate v0 连续 `3/3` 输出 `unsafe_to_stop`，说明 observable risk signals 能阻止错误停止。

## Source-Aware Audit v2

| seed | candidate filter recall | candidate filter precision | source sweep recall | source sweep precision |
| --- | ---: | ---: | ---: | ---: |
| seed01 | 0.862 | 1.000 | 1.000 | 1.000 |
| seed02 | 0.845 | 1.000 | 1.000 | 1.000 |
| seed03 | 0.839 | 1.000 | 1.000 | 1.000 |

解释：

- candidate filter 能把候选池中的 false positives 去掉，但不能恢复候选池之外的漏项。
- source sweep 是 bounded target files 上的 deterministic upper bound，不是 blind LLM 结果。
- 因此 T5 支持一个更强结论：如果任务很大，光保留 union 还不够，还需要更系统的 source-partitioned / bucket-targeted audit。

## 论文里建议怎么写

推荐写：

> In a second real-repository Requests TLS audit, the failure shifts from mostly aggregation loss to mixed search-coverage and aggregation risk. Across three seeds, raw union improves over consensus but remains below the completion threshold, while the completion certificate marks all seeds unsafe to stop.

不要写：

> T5 fully replicates the T4 mechanism.

T5 更像是第二任务族上的“更难边界证据”，不是 T4 的复制品。
