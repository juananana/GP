# 顶会版实验扩充计划

日期：2026-06-08

## 总目标

当前 Line A 已经证明了两个机制：`aggregation loss` 和 `common blind spot`。下一步实验不应该继续“临时找阳性”，而要转成更像顶会论文的系统验证：

> 在 closed-world discovery task 中，比较不同 stopping signal / aggregation policy / audit strategy 对完成性风险的影响，并验证 correlation-aware completion certificate 是否比 confidence、overlap、Good-Turing、Chao 等简单基线更能避免 false stop。

通俗说，我们要证明的不是“某个任务模型漏了”，而是：

> 多 agent 看起来一致，不代表真的完成；完成性需要被估计、校准和审计。

## 实验问题

### RQ1：False Convergence 是否稳定存在？

关注 high confidence、high agreement、自报完成时，consensus 是否仍然漏掉 oracle true items。

主要指标：

- `false_stop_rate`：自报完成且 recall < theta 的比例。
- `consensus_recall` 与 `raw_union_recall`。
- `holdout_gain`：holdout 相对 consensus 新恢复的 true item 比例。
- `strict_positive_rate`：满足预注册 strict positive 条件的 seed 比例。

### RQ2：失败来自哪里？

区分两类机制：

- `aggregation_loss`：true item 已经在 G3 union 中，但被 consensus / standard summarizer 丢掉。
- `common_blind_spot`：true item 不在 G3 union 中，只有 holdout 或新探索能发现。

主要指标：

- `minority_true_drop_rate`。
- `singleton_true_rate` 与 `singleton_false_rate`。
- `common_missing_count`。
- bucket-level recall drop。

### RQ3：什么停止信号不可靠？

比较下面这些 stopping/certification 规则：

- confidence stop。
- overlap/Jaccard stop。
- no-new-item stop。
- Good-Turing missing mass。
- Chao unseen estimator。
- evidence-preserving protocol。
- completion certificate v0。

主要指标：

- `false_certification_count`。
- `conservative_block_count`。
- AUROC / AUPRC：如果后续 seed 足够多，用 risk score 预测 `consensus_recall < theta`。

### RQ4：解决方案是否有成本收益？

比较 full protocol / certificate-triggered holdout 与 always-holdout、random holdout、raw union。

主要指标：

- extra token cost。
- extra wall-clock。
- audit queue size。
- holdout trigger rate。
- recovered true positives per 1k tokens。
- avoided false positives per audit action。

## 任务族设计

### T1：合成代码仓库审计

已有状态：可报告结果已覆盖 seed01/02/03 的关键形态。

价值：

- seed01 是强 aggregation-loss 阳性。
- seed02/03 是 precision-cost 对照，说明 raw union 不能直接当最终答案。

下一步：

- 补到 5 seeds。
- 新增 prompt-diverse G3，与 homogeneous G3 对照。
- 记录真实 token / wall-clock。

### T2：合成 policy docs 搜索

已有状态：seed01/02/03 已稳定展示 near-positive 和 common blind spot。

价值：

- seed01 展示 aggregation loss。
- seed02/03 展示 high agreement common blind spot。

下一步：

- 补到 5-10 seeds。
- 增加 source-partitioned / prompt-diverse 设置。
- 不再继续人为调难；重点转向相关性和停止证书。

### T3：自然化/分区文档任务

已有状态：当前只有 G1 阴性或难度探测。

价值：

- 作为阴性/边界任务有用，说明 pipeline 不会无脑报阳性。

下一步：

- 只在资源允许时补 G3/G6。
- 如果继续阴性，也可以作为“任务族差异”证据。

### T4：真实 Click repo deprecation audit

已有状态：

- 真实 repo snapshot 已固定。
- oracle size = 149。
- scorer compatibility smoke test 已通过。
- 尚未有 blind G3/G6，因此不能报告为实验结果。

这是当前最高优先级。

最小可报告设置：

- `T4_G3_seed01_agent01`
- `T4_G3_seed01_agent02`
- `T4_G3_seed01_agent03`
- `T4_G6_holdout_seed01`
- standard summarizer
- union-preserving summarizer

目标：

- 即使 T4 不出现强阳性，也能提供真实任务族外部有效性证据。
- 如果出现 aggregation loss 或 common blind spot，论文说服力会明显增强。

## Agent 配置矩阵

### 第一阶段：最低可投稿版

| task | seeds | agents | holdout | summarizers | cost logs |
| --- | ---: | ---: | --- | --- | --- |
| T1 | 5 | homogeneous G3 | triggered + selected | standard + union-preserving | yes |
| T2 | 5 | homogeneous G3 | triggered + selected | standard + union-preserving | yes |
| T4 | 3 | homogeneous G3 | all seeds | standard + union-preserving | yes |

### 第二阶段：更强顶会版

| factor | levels | 目的 |
| --- | --- | --- |
| agent count | G1 / G3 / G5 | 测 nominal agents 增加是否真的提高有效覆盖。 |
| prompt diversity | homogeneous / prompt-diverse | 测多样化是否减少共同盲点。 |
| source partition | unrestricted / source-partitioned | 测源覆盖是否降低相关错误。 |
| aggregation policy | consensus / standard / raw union / union-preserving / protocol | 测最后汇总环节的 precision-recall tradeoff。 |
| stopping rule | confidence / overlap / Good-Turing / Chao / certificate | 测 completion signal 是否可校准。 |

## 预注册判定

### Strict False Convergence

一个 seed 满足：

```text
consensus_recall < theta
mean_confidence >= 0.80
mean_pairwise_jaccard >= 0.70
holdout_gain >= max(0.05, 3 / oracle_size)
```

### Aggregation Loss

一个 seed 满足：

```text
exists y:
  y in oracle
  y in raw_union(G3)
  y not in consensus_or_standard_summary
```

### Common Blind Spot

一个 seed 满足：

```text
exists y:
  y in oracle
  y not in raw_union(G3)
  y in holdout
```

### Safe Certification

一个 stopping rule/certificate 的输出满足：

```text
certified_or_stop == true
consensus_recall >= theta
precision >= target_precision
```

当前建议 `target_precision = 0.95`，后续可按任务族调整。

## 必备输出表

论文实验章至少需要 5 张表/图：

- 表 1：任务族与 oracle 规模。
- 表 2：主结果，按 task/seed/aggregation policy 展示 recall、precision、false stop。
- 表 3：机制分解，aggregation loss vs common blind spot。
- 表 4：stopping/certificate 对比，false certification 与 conservative block。
- 表 5：成本收益，tokens、wall-clock、audit actions、recovered TP。

推荐图：

- confidence vs true recall。
- pairwise overlap vs missing true items。
- singleton ratio / Chao missing ratio vs false stop。
- audit cost vs recovered recall。

## 当前缺口

- T4 还没有 blind-agent 结果。
- T1/T2 seed 数仍少，适合机制证明，但不足以做强统计结论。
- 成本仍是 proxy，没有真实 token / wall-clock。
- certificate v0 目前很保守，false certification 为 0，但 conservative block 偏多；需要更多数据校准阈值。
- 还没有 prompt-diverse / source-partitioned / model-heterogeneous 对照。

## 最近一周执行顺序

1. 跑 T4 blind G3 seed01 和 G6 holdout。
2. 对 T4 G3 packet 跑 standard summarizer 与 union-preserving summarizer。
3. 用统一 scorer、incidence log、certificate v0 生成 T4 表。
4. 给 T1/T2 各补 seed04/05，记录真实 token / wall-clock。
5. 开始 prompt-diverse G3 小规模对照，每个任务族先 1 个 seed。

## Go / No-Go 标准

Go 条件：

- 至少两个任务族出现 false stop 或 near-positive。
- 至少一个真实任务族 T4 提供非平凡证据：阳性、near-positive、或明确阴性/边界结论。
- certificate/protocol 相比 confidence/overlap 至少显著减少 false certification。
- 成本分析能说明 triggered audit 比 always-holdout 更划算或更可控。

No-Go 或降级条件：

- T4 和扩展 seeds 全部阴性，且 certificate 只是保守拒停，没有额外解释力。
- singleton audit 只能恢复少数手工构造项，真实任务中没有价值。
- 成本过高，且无法通过 trigger policy 控制。

如果出现 No-Go，不代表方向废掉，但论文定位要降级为 mechanism/workshop paper，而不是强方法论文。
