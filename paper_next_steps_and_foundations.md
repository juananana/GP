# AgentCompletion: 下一步与概念基础

本文档回答两个问题：

1. 论文下一步应该怎么做。
2. 这个方向在机理、概念和相关工作上可以站在哪里。

## 1. 论文核心命题

建议把论文命题收紧为：

> Completion in agentic workflows is not a consensus problem, but an uncertainty estimation problem under correlated exploration.

中文表达：

> 动态 Agent 工作流的完成性判断，不应被视为“多个 Agent 是否达成一致”，而应被视为“在相关探索下，剩余未发现质量是否足够低”的统计估计问题。

这句话比“Agent 会提前停止”更强，因为它直接指出了机理：

- 多 Agent 一致性可能只是共享偏差。
- 连续低新增可能只是容易发现区域被耗尽。
- 自报完成度可能只是模型对自身探索路径的过度校准。
- 真正需要估计的是未探索空间里还剩多少重要条目。

## 2. 下一步工作顺序

现在不要急着写方法。建议并行推进两条线。

### 线 A: 经验现象线

目标：证明 False Convergence 稳定存在。

最小产物：

- 两类封闭世界任务。
- `G1/G2/G3/G6` 四组实验。
- 4 张图。
- 一页 Go / No-Go memo。

关键结论句应当是：

> High agreement and low marginal gain are not reliable completion signals under correlated agent exploration.

第一阶段要回答：

- 多 Agent 高 overlap 时，Recall 是否仍可能低。
- 主流程自报完成时，真实 Recall 是否系统性不足。
- Holdout Scout 是否能在主流程停止后补出有效遗漏。
- 同质 Agent 增加是否主要提高重复，而不是提高覆盖。

### 线 B: 机理建模线

目标：解释为什么会出现 False Convergence。

先提出一个轻量机制模型：

```text
每个 Agent 不是从真实全集均匀采样，而是从自己的探索分布 P_i 中采样。
同质 Agent 的 P_i 高度相似，因此它们共享高概率发现区和低概率盲区。
当高概率发现区被耗尽后，多个 Agent 会同时表现为低新增和高一致。
但低概率盲区中仍可能存在大量目标项。
```

这就是 False Convergence 的核心：

> Agreement is evidence of shared sampling behavior, not necessarily evidence of low missing mass.

## 3. 可操作的机理假设

后续实验不只比较方法，还要操控机理变量。

### H1: Branch Correlation Hypothesis

Agent 分支越相关，表面收敛信号越容易高估真实完成度。

操控方式：

- 相同模型 vs 不同模型。
- 相同 prompt vs prompt 多样化。
- 相同 source 起点 vs source 分区。
- 共享上下文 vs 隔离上下文。
- 相同工具入口 vs 不同搜索策略。

预期：

- 同质分支的 overlap 更高。
- 同质分支的 recall 增益更快饱和。
- 同质分支更容易出现 high-overlap low-recall。

### H2: Easy-Basin Depletion Hypothesis

连续无新增不一定表示任务完成，可能只表示“容易发现区域”已经被耗尽。

操控方式：

- 把 Ground Truth 分成 easy、medium、hard。
- 观察每轮新增主要来自哪个 difficulty bucket。
- 检查 hard bucket 是否在主流程停止后仍被 Scout 找到。

预期：

- 主流程前期主要发现 easy bucket。
- 后期 marginal gain 下降。
- Scout 通过不同 source 或 query 仍能发现 hard bucket。

### H3: Completion Miscalibration Hypothesis

Agent 自报完成度与真实 recall 不校准。

操控方式：

- 记录 `self_reported_confidence`。
- 对比 `Recall@stop`。
- 绘制 calibration curve。

预期：

- Agent 报告 0.8 到 0.95 完成置信度时，真实 recall 可能显著低于该值。
- 同质多 Agent 的相互确认会进一步提高主观完成度，但不一定提高 recall。

### H4: Effective Exploration Hypothesis

有效探索规模 `n_eff` 比名义 Agent 数更能预测遗漏风险。

候选定义：

```text
n_eff = (sum_i w_i)^2 / sum_{i,j} w_i w_j rho_ij
```

其中 `rho_ij` 可以来自：

- 结果集合 Jaccard overlap。
- query embedding similarity。
- source distribution similarity。
- action path similarity。

预期：

- 名义 Agent 数增加不一定提高 `n_eff`。
- `n_eff` 低时，false stop 风险更高。
- source 分区和 prompt 异构化能提高 `n_eff`。

## 4. 概念基础

### 4.1 Total Recall / 高召回检索

这个方向最自然的祖先不是普通 QA，而是 high-recall retrieval。

TREC Total Recall Track 的目标是评估尽可能接近 100% 召回的系统，典型应用包括法律 e-discovery、医学系统综述和测试集构建。它非常适合用来说明：我们的问题不是“答得差一点”，而是“什么时候可以可信地停止找”。参考：

- TREC Total Recall overview: https://pages.nist.gov/trec-browser/trec24/recall/overview/
- TREC Total Recall corpora: https://trec.nist.gov/data/total-recall/

和它的区别：

- TREC 主要关注人机交互式高召回检索。
- 我们关注 LLM Agent 工作流中的动态分支、共享上下文和相关探索。
- 我们的核心变量不是单一 ranking effort，而是 branch correlation、source coverage、holdout discovery。

### 4.2 TAR 停止规则

Technology-Assisted Review 领域已经研究过“为了达到目标 recall，什么时候停止审查”。这可以支撑我们的停止证书视角。

相关方向：

- Quant / QuantCI 等基于模型估计的停止规则。
- Chao estimator 作为停止准则。
- 系统综述筛选中的统计停止标准。

参考：

- Heuristic Stopping Rules for TAR: https://arxiv.org/abs/2106.09871
- Using Chao's Estimator as a Stopping Criterion for TAR: https://arxiv.org/abs/2404.01176

和它的区别：

- TAR 通常有显式文档池、人工标签和主动学习排序。
- AgentCompletion 中，Agent 的搜索路径、工具调用、source 选择和上下文继承本身会引入相关性。
- 因此不能直接把“已审文档样本”当作独立样本。

### 4.3 Missing Mass / Good-Turing / Unseen Species

Missing mass 给我们一个很自然的理论语言：

> 已发现集合之外，还剩多少概率质量属于未发现但重要的条目？

Good-Turing 的直觉是：样本中 singleton 越多，未观察到的质量可能越大。McAllester 和 Schapire 给出了 Good-Turing missing mass 估计的高概率分析。参考：

- On the Convergence Rate of Good-Turing Estimators: https://www.schapire.net/papers/good-turing.pdf

和它的区别：

- 经典 Good-Turing 通常从独立同分布采样开始。
- 多 Agent 搜索不是独立采样。
- 我们的机会在于把 missing mass 和 branch correlation 结合起来。

### 4.4 Capture-Recapture / Chao Estimator

Capture-recapture 和 Chao estimator 适合估计“还有多少类别没被发现”。这和我们估计遗漏项数量很接近。

可借用的概念：

- singleton：只被一个 Agent 发现的条目。
- doubleton：被两个 Agent 发现的条目。
- unseen population：未发现目标项。
- heterogeneous catchability：不同条目被发现概率不同。

这层非常适合解释 easy/hard bucket：

> 有些目标项天然容易被多个 Agent 捕获，有些目标项捕获概率很低。False Convergence 常发生在 easy items 被耗尽，而 hard items 仍未被覆盖时。

### 4.5 Agentic Search Benchmarks

近年的 agentic search benchmark 已经证明“广泛收集”和“总召回”是现实痛点。

可以引用：

- WideSearch: https://arxiv.org/abs/2508.07999
- DeepSearchQA: https://arxiv.org/abs/2601.20975
- Total Recall QA: https://arxiv.org/abs/2603.18516

定位方式：

- WideSearch 证明 broad information seeking 很难。
- DeepSearchQA 观察到 premature stopping / under-retrieval。
- TRQA 强调 total recall query 和可验证评价。
- 我们进一步问：为什么多 Agent 工作流会相信自己已经完成，以及如何给出相关性感知的完成证书。

### 4.6 Multi-Agent Workflow 可靠性

多 Agent 工作流方向正在快速变拥挤，所以我们不要把论文写成“又一个工作流优化器”。

可作为背景：

- Workflow optimization survey: https://huggingface.co/papers/2603.22386
- Rethinking the Value of Multi-Agent Workflow: https://arxiv.org/abs/2601.12307
- Multi-agent RL workflow tradeoffs: https://arxiv.org/abs/2605.24202

定位方式：

- 现有工作多问：怎么设计、优化、训练或选择工作流。
- 我们问：一个动态工作流什么时候可以相信自己已经完成。
- 这让论文从 optimization paper 变成 reliability / evaluation / statistical control paper。

## 5. 论文可以主打的贡献

建议最终论文贡献写成 4 点。

1. Phenomenon

提出并实证刻画动态 Agent 工作流中的 False Convergence。

2. Mechanism

提出相关探索下的表面收敛机制，解释为什么 overlap、低新增和自报完成会误导 recall。

3. Metrics

提出或系统比较 `singleton_ratio`、`source_coverage`、`holdout_gain`、`n_eff` 等完成性风险指标。

4. Controller

提出轻量的 Correlation-Aware Completion Certificate，包括 Discovery Ledger、Correlation Monitor、Holdout Scout 和 stopping certificate。

## 6. 建议论文结构

```text
1. Introduction
   问题：Agent 如何知道自己找完了？

2. False Convergence
   定义现象，给出例子和形式化指标。

3. Why Consensus Fails
   相关探索、easy-basin depletion、missing mass。

4. Diagnostic Benchmark / Tasks
   封闭世界代码扫描和固定文档集合。

5. Empirical Study
   G1/G2/G3/G4/G5/G6 对比，证明现象。

6. Correlation-Aware Completion Certificate
   轻量控制器和停止规则。

7. Evaluation
   是否降低 false stop，成本是多少，是否保持 precision。

8. Related Work
   Total Recall、TAR stopping、missing mass、多 Agent workflows、agentic search benchmarks。

9. Limitations
   开放世界无法保证绝对完成，只能给统计证书。
```

## 7. 现在最该做的具体下一步

第一优先级：

> 构造 T1 代码扫描任务，并跑出第一批 9 个 run：`T1 × G1/G3/G6 × 3 seeds`。

第二优先级：

> 同时写一页理论 memo，标题为 `Why Consensus is Not Completion`。

这页 memo 只需要讲清楚：

- Agent 分支是相关采样器。
- 高 overlap 可以来自共享发现偏好。
- 低 marginal gain 可以来自 easy-basin depletion。
- Holdout Scout 是对共享盲区的后验检验。
- completion certificate 应估计 missing mass，而不是计数投票一致性。

第三优先级：

> 做相关工作矩阵，不超过 20 篇论文。

矩阵列：

```text
paper
problem
setting
stop/completion signal
handles correlation?
uses ground truth recall?
relation to AgentCompletion
```

这会直接服务 Related Work 和 Introduction。

