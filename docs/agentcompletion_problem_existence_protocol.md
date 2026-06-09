# AgentCompletion 第一阶段 Protocol

目标：证明或否定动态多 Agent 工作流中是否稳定存在 **False Convergence**，即“表面已经完成，但真实覆盖不足”的现象。

当前阶段只验证问题是否存在，不提出新算法，不训练模型，不做复杂工作流优化。

## 1. 要证明的不是“Agent 会漏”

普通遗漏不是论文问题。第一阶段要证明的是一个更具体的现象：

> 当多个 Agent 结果高度一致、连续轮次几乎无新增、主流程自报完成时，真实 Recall 仍然明显不足，并且独立 Holdout Scout 还能发现遗漏项。

因此，问题存在需要同时满足四个信号：

1. 表面收敛：多个 Agent 的结果重叠高，或最近若干轮新增极低。
2. 主观完成：Agent 或主流程明确报告任务完成，且置信度较高。
3. 客观不足：与 Ground Truth 对比后，`Recall@stop` 明显低于目标阈值。
4. 可补遗漏：独立 Holdout Scout 在主流程停止后仍能找到有效新条目。

## 2. 形式化定义

设：

- `G*`：任务的真实目标条目集合。
- `S_t`：主流程在第 `t` 轮累计发现的条目集合。
- `S_stop`：主流程停止时的累计发现集合。
- `H`：Holdout Scout 在主流程停止后发现的条目集合。
- `A_i`：第 `i` 个 Agent 发现的条目集合。

核心指标：

```text
Recall@stop = |S_stop ∩ G*| / |G*|
HoldoutGain = |(H \ S_stop) ∩ G*| / |G*|
PairwiseOverlap = mean Jaccard(A_i, A_j)
FalseStop = stop_is_declared_done AND Recall@stop < theta
FalseConvergence = FalseStop AND PairwiseOverlap >= tau AND HoldoutGain >= gamma
```

第一轮建议阈值：

```text
theta = 0.95
tau = 0.70
gamma = max(0.05, 3 / |G*|)
```

解释：

- `Recall@stop < 0.95`：停止时仍有明显遗漏。
- `PairwiseOverlap >= 0.70`：表面结果已经高度一致。
- `HoldoutGain >= 5%` 或至少 3 个有效条目：遗漏不是偶然一两个边角项。

## 3. 最小证明链

第一阶段的证据链要能回答 5 个审稿人可能会问的问题。

| 审稿人质疑 | 对应证据 |
| --- | --- |
| 这只是 Agent 漏东西，不是新现象 | 同时展示高 overlap、低新增、自报完成和低 recall |
| 这只是任务太难 | 用静态 oracle 或人工 ground truth 证明任务可被穷尽 |
| 这只是预算太少 | 加入固定轮数单 Agent，观察继续探索是否仍能涨 recall |
| 这只是多 Agent 没用 | 比较同质多 Agent 和独立 Scout 的增益差异 |
| 这只是人为构造陷阱 | 使用一个控制任务和一个更贴近真实场景的任务 |

核心逻辑：

```text
如果 G3 看起来比 G1 更一致，但 Recall 没有明显提升；
如果 G6 的独立 Scout 在主流程停止后还能补出有效遗漏；
如果 Agent 自报完成度显著高于真实 Recall；
那么问题不是“单次漏检”，而是“收敛信号误导了完成性判断”。
```

## 4. 第一批任务

为提速，先做两个封闭世界任务。封闭世界的好处是可以严格计算 Recall。

### T1: 代码仓库扫描任务

任务例子：

> 找出代码仓库中所有旧 API、旧路径或危险调用点。

Ground Truth 构造方式：

- 使用 `rg` 做关键词召回。
- 使用 AST 或语法规则过滤误报。
- 人工复核最终条目集合。
- 每个条目记录 `file_path`、`line`、`matched_symbol`、`evidence`。

推荐第一轮使用半合成任务：

- 在一个小型真实代码仓库或自建仓库中植入 30 到 60 个目标调用点。
- 目标调用点分布在不同目录、文件类型和命名形式中。
- 保留若干近似但非目标项，用来测试 precision。

这样可以快速拿到可靠 Ground Truth，同时不会把任务做成纯玩具。

### T2: 固定文档集合检索任务

任务例子：

> 在固定文档集合中找出所有满足多条件约束的条目。

可选数据形式：

- 本地 HTML 快照。
- Markdown 文档集合。
- JSON/CSV 商品或论文元数据。
- 本地新闻或教程页面集合。

Ground Truth 构造方式：

- 用脚本或人工标注生成 `G*`。
- 条目必须可逐条验证。
- 每个条目记录 `source_id`、`item_id`、`evidence_span`、`condition_match`。

第一轮建议做成多条件任务：

```text
找出所有同时满足 A、B、C 条件的条目。
```

多条件能制造真实的长尾遗漏，但仍然可以严谨验证。

## 5. 实验组

为了先证明问题存在，第一轮不需要完整 6 组，先跑 4 组。

| 组别 | 设置 | 目的 |
| --- | --- | --- |
| G0 | Oracle / 静态穷尽扫描 | 证明 Ground Truth 可得，任务不是不可完成 |
| G1 | 单 Agent，自主停止 | 测量普通自停的 false stop |
| G2 | 单 Agent，固定轮数 | 区分停止错误和能力不足 |
| G3 | 多个同质 Agent | 检验多 Agent 是否只是增加重复 |
| G6 | 主流程 + 独立 Holdout Scout | 检验停止后是否仍有可发现遗漏 |

最小运行规模：

```text
2 tasks × 4 agent groups × 3 seeds = 24 runs
```

说明：

- `G0` 不算 Agent run，但必须保留，用于证明任务可验证。
- 如果时间非常紧，可以先跑 `T1 × G1/G3/G6 × 3 seeds`，当天就能看到初步信号。
- `G2` 很重要，因为它能回答“是不是只是停得太早”的质疑。

## 6. Holdout Scout 独立性要求

Holdout Scout 是第一阶段最关键的设计。

Scout 必须满足：

1. 不读取主流程的完整推理轨迹。
2. 不复用主流程的原始 prompt。
3. 不优先从主流程已经覆盖的 source 开始。
4. 使用不同搜索策略，例如 source-first、directory-first、schema-first。
5. 输出条目必须附 evidence，允许后验验证。

Scout 可以读取：

- 任务目标。
- 主流程最终发现的去重条目列表。
- 已覆盖 source 的摘要。

Scout 不应读取：

- 主 Agent 的中间推理。
- 主 Agent 的失败查询。
- 主 Agent 对“已经完成”的解释。

这样设计是为了减少共享盲区。

## 7. 日志 Schema

每个 Agent 每轮记录一行 JSONL。

```json
{
  "task_id": "T1_api_scan",
  "run_id": "T1_G3_seed01",
  "group_id": "G3",
  "agent_id": "agent_02",
  "round_id": 3,
  "prompt_variant": "homogeneous_v1",
  "model_name": "model_name_here",
  "query_or_action": "searched src/services for old_api",
  "source_id": "src/services",
  "new_items": ["item_012", "item_018"],
  "all_items": ["item_001", "item_012", "item_018"],
  "item_provenance": {
    "item_012": "src/services/a.py:42"
  },
  "self_reported_completion": true,
  "self_reported_confidence": 0.86,
  "stop_reason": "no_new_items_and_agent_declared_done",
  "latency_seconds": 31.2,
  "token_or_cost": 0.0
}
```

每个 run 结束后生成汇总：

```json
{
  "task_id": "T1_api_scan",
  "run_id": "T1_G3_seed01",
  "group_id": "G3",
  "ground_truth_size": 47,
  "found_size": 36,
  "true_positive_size": 34,
  "false_positive_size": 2,
  "recall_at_stop": 0.723,
  "precision_at_stop": 0.944,
  "pairwise_overlap": 0.78,
  "singleton_ratio": 0.11,
  "source_coverage": 0.58,
  "holdout_gain": null,
  "false_stop": true,
  "false_convergence": null
}
```

## 8. 需要出的图

第一批只出 4 张图，够做方向判断。

1. `Recall vs Round`

看主流程是否在低 recall 时停止。

2. `Reported Completion vs True Recall`

看 Agent 自报完成度是否系统性高估。

3. `Pairwise Overlap vs Missing Items`

看高一致性是否掩盖剩余遗漏。

4. `Main Workflow vs Holdout Scout`

看主流程停止后 Scout 是否还能补出新条目。

## 9. Go / No-Go 标准

### Go

满足以下任意两个：

- 至少一个任务中，`G3` 的 `PairwiseOverlap >= 0.70` 且 `Recall@stop < 0.95`。
- 至少一个任务中，`G6` 的 `HoldoutGain >= 0.05` 或补出至少 3 个有效条目。
- Agent 平均自报完成置信度高于 0.80，但真实 recall 低于 0.90。
- `G3` 相比 `G1` 的 recall 增益小于 10%，但 overlap 明显升高。

### Strong Go

满足以下任意两个：

- 两类任务都出现 False Convergence。
- Holdout Scout 在两个任务中都能稳定补出有效遗漏。
- 同质多 Agent 的结果重叠升高，但 recall 增益饱和。
- `source_coverage` 或 `singleton_ratio` 能比 `no new items` 更好预测遗漏。

### No-Go

满足以下任意两个：

- 多数 run 在合理预算下达到 `Recall@stop >= 0.95`。
- Holdout Scout 基本补不出有效新条目。
- 高 overlap 与高 recall 强相关，且没有明显反例。
- 固定轮数继续探索也几乎没有新增。

No-Go 不代表失败，只说明第一篇论文不该押在 False Convergence 上。

## 10. 72 小时执行顺序

### Day 1: 定任务和 Ground Truth

产物：

- `tasks/T1_api_scan/ground_truth.json`
- `tasks/T2_doc_search/ground_truth.json`
- 每个任务一页说明。

检查点：

- `|G*|` 最好在 30 到 80 之间。
- 目标条目分布在至少 4 个 source 区域。
- 有一部分目标项不容易被单一关键词覆盖。

### Day 2: 跑最小实验

优先顺序：

1. `T1 × G1 × 3 seeds`
2. `T1 × G3 × 3 seeds`
3. `T1 × G6 × 3 seeds`
4. 如果 T1 有明显信号，再跑 T2。

当天必须看：

- 主流程是否自报完成。
- 停止时 recall 是否低于 0.95。
- 多 Agent 是否高 overlap。
- Scout 是否能补出有效遗漏。

### Day 3: 汇总和判断

产物：

- 4 张图。
- 一页 memo。
- Go / No-Go 判断。

Memo 结构：

```text
Observation:
  我们是否观察到高一致、低 recall、自报完成？

Counter-explanation:
  是否可能只是任务太难、预算太少或 ground truth 有问题？

Evidence:
  哪些 run 支持 False Convergence？

Decision:
  Go / Strong Go / No-Go
```

## 11. 第一阶段结论应该怎么写

如果现象成立，不要写成：

> Agent 没有找全。

应该写成：

> 在封闭世界集合发现任务中，动态多 Agent 工作流可能产生误导性的完成信号：Agent 间高一致性和连续低新增并不可靠地对应高 recall。独立 Scout 的后验发现表明，主流程的停止判断可能反映的是共享探索盲区，而非真实完成。

如果现象不成立，也要保留结论：

> 在当前任务和预算下，False Convergence 没有稳定出现。下一步应转向更困难的长尾任务、约束漂移，或错误级联方向。

