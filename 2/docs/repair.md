我们暂时不要继续实现 DICE-Lite，也不要修改正式论文正文。请新建一个独立的“小型几何诊断实验包”，目标是验证：在 closed-world high-recall discovery 中，multi-agent false completion 是否表现为 source-path/action trajectory 的局部集中与全局覆盖空洞，以及覆盖几何指标能否比简单 overlap 更好地解释或预测错误停止。

请严格区分：这一阶段是 mechanism diagnostic pilot，不是新方法实现，不要提前宣称 phase transition、Grassmann manifold、geometry-aware controller 或 stopping certificate 已经成立。

## 0. 先阅读并更新邻近工作边界

请建立 `docs/coverage_geometry_related_work.md`，至少整理以下工作：

* Representational Collapse in Multi-Agent LLM Committees, arXiv:2604.03809
* Understanding Agent Scaling in LLM-Based Multi-Agent Systems via Diversity, arXiv:2602.03794
* Predictive Maps of Multi-Agent Reasoning, arXiv:2605.11453
* DiLLS, arXiv:2602.05446
* Auditing Multi-Agent LLM Reasoning Trees Outperforms Majority Vote and LLM-as-Judge, arXiv:2602.09341
* Beyond Consensus: Trace-Level Synthesis in Mixture of Agents, arXiv:2605.29116
* Push Your Agent: Measuring and Enforcing Quantitative Goal Persistence in Long-Horizon LLM Agents, arXiv:2605.23574
* SeekerGym, arXiv:2604.17143
* DeepSearchQA, arXiv:2601.20975
* Total Recall QA, arXiv:2603.18516
* Detecting Underspecification in Software Requirements via k-NN Coverage Geometry, arXiv:2603.24248
* Measuring Black-Box Confidence via Reasoning Trajectories: Geometry, Coverage, and Verbalization, arXiv:2605.06308

对每篇论文记录：

```text
研究对象
输入表示
使用的几何或统计指标
预测目标
是否研究 multi-agent
是否研究 closed-world discovery
是否研究未知目标总数下的 stopping
与我们重叠的部分
仍未覆盖的缺口
```

不要将以下内容视为我们的原创点：

```text
embedding cosine similarity
effective rank
heterogeneous agents improve diversity
majority vote may discard evidence
false completion terminology
coverage geometry terminology
```

我们的候选差异仅限于：

> source-path/action-trajectory coverage geometry for false-completion diagnosis in multi-agent closed-world discovery, where the true total item count is hidden from agents but available to the oracle for evaluation.

## 1. 先审查现有日志，不要假设数据已经存在

请检查当前项目中已有 Requests、Click 和其他 runs 的日志字段，输出：

```text
docs/geometry_log_audit.md
```

逐项说明是否已经记录：

```text
task_id
repo_id
run_id
agent_id
round_id
item_id
oracle_label
source_path
source_family
search_route
query_text
tool_name
action_type
timestamp
self_reported_completion
self_reported_confidence
stop_reason
holdout_or_scout_id
scout_discovered_items
cost_or_token_count
latency
```

如果字段缺失，请明确列出：

```text
可直接计算的指标
只能近似计算的指标
完全无法计算的指标
需要补跑实验才能获得的字段
```

不得虚构日志字段，不得使用无法从现有数据获得的代理值而不说明限制。

## 2. 建立三类表示

优先构建离散、可解释的覆盖表示。

### A. Agent × Source-Route Stratum 覆盖矩阵

定义：

```text
C[i, j] = agent i 在 source-route stratum j 中的访问次数、动作次数或发现条目数量
```

至少分别构建：

```text
visit_count matrix
action_count matrix
discovered_item_count matrix
```

矩阵可以行归一化，但必须同时保留原始计数。

### B. Agent × Item Incidence Matrix

定义：

```text
Z[i, k] = 1，当 agent i 发现 item k；否则为 0
```

区分：

```text
all discovered items
oracle true-positive discovered items
```

其中 oracle true-positive 版本只能用于事后诊断，不能作为部署时特征。

### C. Action-Trajectory Embedding，可选

只有当现有日志包含足够的 query/action/tool 序列时，才构建 action trajectory embedding。

embedding 只作为补充分析，不作为第一优先级。至少比较两种 encoder 或说明为什么无法做 encoder robustness 检查。不要仅凭 embedding 结果得出结论。

## 3. 计算指标

### 3.1 简单基线指标

计算：

```text
pairwise item Jaccard overlap
source overlap
route overlap
self-reported completion confidence
number of no-new-item rounds
raw source coverage
raw route coverage
singleton ratio
```

### 3.2 覆盖几何指标

基于覆盖矩阵计算：

```text
pairwise cosine similarity
singular value spectrum
entropy effective rank
normalized effective rank = erank(C) / min(num_agents, num_strata)
Gram matrix G = C C^T
logdet volume = log det(G + epsilon I)
marginal logdet gain after adding each agent
source concentration entropy
route concentration entropy
HHI or Gini concentration
```

如果要计算 principal angles，请先说明每个 Agent 的轨迹如何形成非退化子空间。若每个 Agent 只有一个向量，禁止为了使用 principal angles 人为包装成子空间。

### 3.3 Residual Scout 指标

不要预设 Scout 是“正交”的。

首先计算：

```text
scout_new_items
scout_new_true_positives
scout_cost
residual_novelty_per_cost
scout_source_route_similarity_to_main_agents
```

只有当 Scout 路线向量在已有探索空间上的投影较低时，才进一步计算并报告：

```text
residual_projection_ratio
orthogonal_component_ratio
```

并使用中性名称：

```text
residual-direction scout
```

不要提前称为 orthogonal scout。

## 4. 标签与数据泄漏控制

严格区分：

### 部署时可观察特征

```text
source overlap
route overlap
action concentration
effective rank
logdet volume
marginal logdet gain
new-item rate
singleton ratio
scout residual novelty
```

### 仅用于离线评价的 Oracle 标签

```text
oracle recall
oracle missing-item count
per-stratum true missing mass
false completion label
safe completion label
oracle coverage holes
scout new true positives
```

定义：

```text
false_completion = 系统宣布完成，但 oracle recall < theta
```

至少报告：

```text
theta = 0.90
theta = 0.95
theta = 1.00
```

不得将 oracle missing mass、oracle recall 或 oracle coverage hole 混入运行时预测特征。

## 5. 分析问题

请回答：

### RQ1

错误停止是否表现为 source-path/action trajectory 的局部集中，而不是全局充分覆盖？

### RQ2

effective rank、logdet volume 或 marginal volume gain 是否比简单 Jaccard overlap、source coverage、连续无新增轮数和自报置信度更能解释或预测 false completion？

### RQ3

低投影 residual-direction scout 是否比普通 free-search scout、随机 source scout 和低覆盖 source scout 更容易发现 ledger 外的新真阳性？

### RQ4

几何指标在不同仓库、不同任务和不同 Agent 配置下是否稳定？还是仅在特定表示或特定仓库中有效？

## 6. 统计与可视化

如果现有 runs 数量足够，请报告：

```text
Spearman correlation
AUROC
AUPRC
bootstrap 95% confidence intervals
leave-one-task-out 或 leave-one-repo-out 验证
```

如果样本量不足，不要强行训练分类器。改为报告描述性统计、散点图和需要补跑的最小实验集合。

至少输出：

```text
results/coverage_geometry_metrics.csv
results/run_level_summary.csv
figures/false_completion_vs_erank.png
figures/false_completion_vs_logdet_gain.png
figures/recall_vs_source_concentration.png
figures/scout_gain_vs_residual_projection.png
figures/singular_value_spectrum_safe_vs_false.png
docs/coverage_geometry_diagnostic_report.md
```

## 7. Go / No-Go 判断

请在报告最后给出严格判断。

只有满足以下条件，才建议进入几何主线：

1. 至少一个覆盖几何指标能够稳定区分 safe completion 与 false completion；
2. 它明显优于简单 overlap、source coverage 和连续无新增轮数；
3. 规律在至少两个仓库或两个任务类型中复现；
4. residual-direction scout 在相近成本下优于普通追加搜索；
5. 结果不依赖单一 embedding encoder；
6. 指标可以在不访问 oracle 的情况下计算。

如果不满足，请明确建议回退到：

```text
简单 source coverage
+ evidence ledger
+ lightweight audit controller
```

不要为了保留几何叙事增加复杂模块。

## 8. 实现约束

* 不要覆盖或破坏现有实验代码；
* 新建独立目录，例如 `analysis/coverage_geometry_diagnostics/`；
* 不要修改正式论文正文；
* 不要伪造任何实验结果；
* 所有图表必须由真实日志生成；
* 如果现有日志不足，先给出最小补跑方案，不要直接大规模调用模型；
* 保留运行命令、环境说明和输出文件路径；
* 最后给出一段简短结论：当前证据是否足以继续几何主线，以及下一步最小补跑实验是什么。
