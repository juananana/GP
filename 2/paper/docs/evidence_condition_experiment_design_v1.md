# Evidence-Condition Geometry 实验重构设计方案

## 0. 文档目的

本实验设计用于指导在现有论文与代码基础上重构实验部分。目标不是简单增加实验数量，而是把实验设计成一条清晰的证据链：先证明“虚假完成 / false completion”在真实 agent 或 completion-audit 场景中确实存在，再证明 source-route evidence condition 能比 source-only 更好地诊断这种风险，最后证明 Evidence-Condition Controller 在安全性、可行动性和成本之间形成更合理的控制闭环。

本方案默认主实验尽量使用公开、真实、可复现的数据集或环境。已有的 generated policy-docset / code-repo 可保留为补充材料中的 controlled sanity checks，不作为主文最核心证据。

---

## 1. 核心实验问题

当前论文要回答的实验问题可以组织为五个层次。

### Q1. 真实任务中是否存在 false completion？

需要验证：现有 agent / workflow 在任务执行过程中是否会出现“已经停止或声明完成，但评价器认为任务未完成”的情况。

形式化定义：

```text
false completion = workflow accepts SAFE / declares DONE / stops
                   while task oracle says incomplete
```

在不同数据集上完成判定不同：

- Web-agent 任务：环境 evaluator 返回 success=false。
- High-recall audit 任务：bounded recall < target threshold，例如 0.90 或 0.95。
- Repository audit 任务：pattern-defined oracle 或 frozen checklist 中仍有未发现 residual items。

### Q2. Source-only support 是否会产生完成错觉？

需要比较：

```text
source-only support
source-route support
source-route Gini
```

重点不是只看成功率，而是看 stop-time diagnostic 能否区分安全停止与虚假完成。若 source-only support 很高但 source-route support 低、Gini 高，并且 task oracle 显示未完成，则说明 source-only coverage 会隐藏 route mismatch。

### Q3. 与现有或常见 stopping / verification 方法相比，我们的方法是否更合理？

需要比较：

- Naive stop
- Source-only controller
- Fixed-budget continuation
- Random repair
- High-potential repair
- Verifier-gate / LLM judge
- Multi-agent voting / self-consistency
- TREC 上的 TAR / Total Recall stopping baselines
- Full Evidence-Condition Controller

重点结论应避免写成“全面优于所有方法”，而应写成：

```text
Naive / Source-only 容易 unsafe SAFE；
Verifier-gate 较安全但 fail-closed；
Full controller 在保持安全性的同时，把 residual-positive unsafe states 转化为 actionable CONTINUE。
```

### Q4. 控制器各模块是否必要？

需要做消融：

- w/o source-route granularity
- w/o Gini
- w/o Eligibility Gate
- w/o Residual Repair
- w/o under-exposure
- w/o runtime-potential
- Random repair
- No ABSTAIN

消融目标是说明每个模块分别服务于 safety、actionability 或 cost-efficiency。

### Q5. 方法的 trade-off 如何体现？

因为本方法是在 agent/workflow 停止之后增加 controller 和 repair，因此必须展示收益与成本：

- 是否减少 unsafe SAFE？
- 是否提高最终 success / recall？
- 是否增加 token、tool calls、steps、wall-clock time？
- CONTINUE 是否真的发现 residual evidence？
- 在不同 repair budget 和 threshold 下，安全性、可行动性、成本如何变化？

建议统一称为 **Pareto frontier / cost frontier**，不要称为傅里叶前沿图。

---

## 2. 数据集与环境选择

### 2.1 主数据集 A：WebArena / BrowserGym

**用途：** 验证真实 web-agent 场景中的 false completion。

**选择理由：** WebArena 是真实交互式网页环境，用 functional correctness 评价任务完成；BrowserGym/AgentLab 提供统一 web-agent benchmark 框架，有利于复现实验、收集 trajectory、比较不同 agent。

**推荐实验规模：**

- Smoke test：20 tasks
- Pilot：50 tasks
- Main：100–150 tasks
- 每个 agent 至少 3 seeds
- 优先选择有明确 evaluator 的任务；避免过度依赖开放式文本评价的任务

**Source 定义：**

按任务环境与页面结构定义，例如：

```text
website module / page / tool resource / task sub-area
```

可具体化为：

- product page
- search results page
- cart page
- checkout / confirmation page
- account / profile page
- forum thread
- issue page
- admin/config page

**Route 定义：**

Route 必须在实验前声明，并写入 config。Web-agent 场景建议使用任务无关但可解释的 action/evidence lenses：

```text
navigation
search/query
read/inspect
form/action
state verification
confirmation
```

更细的 domain-specific route 可在 config 中声明。例如购物任务：

```text
product-search
filter-checking
price-checking
cart-state
checkout-confirmation
```

**Completion oracle：** 环境 evaluator 返回 success/failure。

**False completion 定义：**

```text
agent produces final answer / DONE / stop action
AND evaluator_success = false
```

**需要记录：**

```text
task_id
agent_name
seed
trajectory_id
actions
observations
stop_signal_type
final_answer
evaluator_success
tool_calls
llm_calls
tokens
wall_clock_time
visited_sources
visited_source_routes
```

---

### 2.2 主数据集 B：TREC Total Recall

**用途：** 验证 completion-audit / high-recall 场景中的停止判断。

**选择理由：** TREC Total Recall 的目标是开发面向“找全相关信息”的系统，天然适合验证“什么时候可以停止审计 / 检索”。它有 topics 与 relevance judgments，可以计算 recall 与 residual relevant documents。

**推荐实验规模：**

- 选择 20–30 topics 作为 main set
- 每个 topic 跑 3 seeds
- target recall 使用 0.90 和 0.95 两档
- 可先用小集合调试，再冻结 topic list

**Source 定义：**

根据集合结构和检索过程定义：

```text
collection shard
document cluster
retrieval batch
topic-specific evidence pool
```

如果实现上更简单，也可以把 source 定义为 retrieval batch / document group，但必须在运行前固定。

**Route 定义：**

建议把 query / retrieval strategy 作为 route：

```text
keyword-query
entity-query
synonym-expansion
metadata/date-facet
seed-neighbor-expansion
negative/contrastive-query
```

**Completion oracle：**

```text
recall = found_relevant / total_relevant
complete = recall >= target_recall
```

**False completion 定义：**

```text
workflow stops
AND recall < target_recall
```

**需要记录：**

```text
topic_id
route_id
query_text
retrieved_docs
reviewed_docs
found_relevant
recall_at_stop
remaining_relevant
review_cost
stop_signal_type
source_route_exposure
```

---

### 2.3 外部补充数据集 C：SWE-bench Verified / Defects4J（可选）

**用途：** 作为代码任务外部补充，不建议作为第一阶段主实验。

**原因：** 代码修改任务的“完成”混入 patch generation、测试充分性、issue 理解等因素，实验成本更高。但它可以作为论文后期的外部有效性补充。

**推荐定位：**

```text
external sanity check / code-task transfer case
```

**完成判定：**

- SWE-bench Verified：official harness pass/fail
- Defects4J：test suite pass/fail + optional additional tests

**Source 定义：**

```text
changed files
test files
config files
dependency files
issue discussion / docs
```

**Route 定义：**

```text
reproduction
localization
patch-generation
test-verification
regression-checking
dependency/config-checking
```

**风险：** 不要把 test pass 直接写成“真实完成”；要说明测试 oracle 不是开放世界语义正确性的完全保证。

---

### 2.4 已有 requests / urllib3 repository audit

**用途：** 保留为 repository audit case study。

**定位：**

```text
frozen real-repository audit case study
```

**建议：**

- 保留现有 requests / urllib3 结果。
- 加入更清晰的 route inventory 表。
- 确认 oracle 是 pattern-defined，不写成人工语义 gold label。
- 用于展示 source-route geometry、eligibility-not-proof boundary、repair frontier。

---

### 2.5 原有 generated tasks

**用途：** 放入 supplement 作为 controlled sanity checks。

**建议表述：**

```text
controlled synthetic sanity checks
```

不要作为主文最强证据，因为审稿人可能质疑任务与 route 是人为构造的。

---

## 3. Route Inventory 原则

Route 是本论文的核心概念，必须严格定义。实验文档和代码都要遵守以下原则：

### 3.1 Route 的定义

```text
A route is a task-declared audit lens applied to a source.
```

中文解释：

```text
route 是任务预先声明的审计视角，表示同一个 source 是从哪个证据路径、检查维度或审计角度被检查的。
```

### 3.2 Route 不是通用标准标签

必须在论文和补充材料中说明：

- route 不是跨领域通用常数；
- route inventory 是 declared audit scope 的一部分；
- controller 只对声明好的 source-route scope 负责；
- 若 route inventory 漏掉重要审计维度，controller 不能保证未声明范围的完成性。

### 3.3 Route 不能从 oracle 反推

实验前必须冻结：

```text
sources.yaml
routes.yaml
route_mapping_rules.yaml
thresholds.yaml
budgets.yaml
```

禁止使用：

```text
oracle labels
oracle totals
post-hoc recall
undiscovered true-item counts
hidden missing mass
```

来定义 route 或影响 runtime decision。

### 3.4 Route robustness 检查

建议增加 route inventory sensitivity：

- coarse routes
- main routes
- fine-grained routes

观察 support/Gini、FCR、actionability 是否稳定。这个实验不要求方法在所有 route inventory 上完全不变，而是说明结论是否依赖过度精细的人为 route 设计。

---

## 4. 方法与 Baseline

### 4.1 Full Evidence-Condition Controller

完整方法包括四个模块：

1. Source-route exposure estimation
2. Eligibility Gate
3. Residual Repair
4. SAFE / CONTINUE / ABSTAIN Decision Rule

Runtime decision 不得读取 oracle 字段。

### 4.2 Baseline 组

#### B1. Naive stop

agent / workflow 声明 done 就接受 SAFE。

#### B2. Source-only controller

只检查 source coverage，不检查 route coverage。

#### B3. Fixed-budget continuation

agent 声明 done 后固定继续 k 步或固定多审计 k 个目标。用途：排除“只是因为多花预算所以更好”。

#### B4. Random repair

随机选择未覆盖或弱覆盖的 source-route strata 补查。

#### B5. High-potential repair

只根据 runtime-potential 排序，不考虑 under-exposure。用途：验证 under-exposure 是否必要。

#### B6. Low-exposure repair

只根据 under-exposure 排序，不考虑 runtime-potential。用途：验证 runtime-potential 是否必要。

#### B7. Verifier-gate / LLM judge

用独立 verifier 判断是否完成。未通过则 ABSTAIN 或 CONTINUE。需要保证 verifier 不使用 oracle。可以有两种版本：

```text
Verifier-gate-abstain: warning -> ABSTAIN
Verifier-gate-continue: warning -> fixed-budget continuation
```

#### B8. Multi-agent voting / self-consistency

多个 agents 都声明完成才 SAFE。用途：验证 agreement 不能完全解决 false completion，因为 agents 可能共享相似搜索路径。

#### B9. TAR / Total Recall stopping baselines（TREC only）

在 TREC Total Recall 上加入：

- Continuous Active Learning stopping heuristic
- target recall estimator
- Chao / capture-recapture style estimator
- no-new-in-window stopping

这些 baseline 不一定全部实现，至少选择 2–3 个可复现且实现成本可控的方法。

---

## 5. 指标体系

### 5.1 安全性指标

```text
FCR = unsafe states certified SAFE / unsafe states
```

其中 unsafe state 的定义：

- WebArena：agent stop 但 evaluator_success=false
- TREC：stop 但 recall < target
- Repo audit：stop 但 oracle residual exists

```text
Safe coverage = complete states certified SAFE / complete states
```

表示方法是否变成 never-stop。

### 5.2 可行动性指标

```text
Actionability = CONTINUE on residual-positive unsafe states / residual-positive unsafe states
```

也可报告：

```text
CONTINUE precision = residual-positive CONTINUE / all CONTINUE
```

用于区分“有方向地继续查”和“泛泛地不让停”。

### 5.3 完成质量指标

- WebArena success rate
- TREC recall at stop
- final recall after repair
- completion gap
- residual relevant items found
- repository residual oracle items found

### 5.4 成本指标

建议统一记录：

```text
llm_calls
tool_calls
tokens
action_steps
wall_clock_time
reviewed_docs
repair_cost
```

不同数据集成本不可直接混合时，使用 normalized cost：

```text
normalized_cost = cost / dataset-specific median cost
```

### 5.5 诊断指标

- source-only support
- source-route support
- source-route Gini
- support/Gini AUROC for unsafe stop
- AUPRC for residual-positive states
- residual-positive rate by support/Gini bucket

### 5.6 收益—成本指标

```text
cost-normalized gain = residual items found / repair cost
success lift per 1k tokens
recall gain per reviewed document
```

---

## 6. 实验设计

## Experiment 1：False Completion Existence

### 目的

证明 false completion 在真实 agent / completion-audit 场景中存在。

### 数据集

- WebArena/BrowserGym
- TREC Total Recall
- requests/urllib3 case study

### 方法

对每个 task/topic 运行基础 agent/workflow。记录 stop signal 与 oracle completion。

### 指标

- FCR
- completion gap
- stop signal distribution
- success / recall
- tokens / tool calls / time

### 预期图表

- Figure A：不同 agent/workflow 的 false completion rate
- Table A：stop signal 类型与失败率
- Figure B：completion gap distribution

### 主结论

```text
Stop signals such as no-new findings, agreement, or self-reported completion do not reliably certify completion.
```

---

## Experiment 2：Source-only vs Source-route Diagnostic

### 目的

验证 source-route geometry 是否比 source-only support 更能诊断 unsafe stop。

### 数据集

- WebArena/BrowserGym
- TREC Total Recall
- requests/urllib3

### 方法

在相同 stop states 上同时计算 source-only support 和 source-route support/Gini。

### 指标

- FCR under source-only SAFE
- source-route eligible rate
- AUROC/AUPRC for unsafe stop
- task success / recall
- cost

### 预期图表

- Bar plot：source-only support vs source-route support vs recall
- Scatter：source-route support vs Gini，点颜色表示 safe/unsafe
- Calibration：support/Gini bucket vs residual-positive probability

### 主结论

```text
Source-only coverage can look complete while source-route exposure remains localized.
```

---

## Experiment 3：Baseline Comparison

### 目的

比较 full controller 与常见 stopping / verification / continuation 策略。

### Baselines

- Naive stop
- Source-only
- Fixed-budget continuation
- Random repair
- High-potential
- Low-exposure
- Verifier-gate
- Multi-agent voting
- TAR/Chao stopping on TREC
- Full controller

### 指标

- FCR
- safe coverage
- actionability
- ABSTAIN rate
- CONTINUE precision
- task success / recall
- tokens/tool calls/time
- cost-normalized gain

### 预期图表

- Decision distribution：SAFE / CONTINUE / ABSTAIN
- Safety-actionability table
- Pareto frontier：cost vs success/recall/residual gain

### 主结论

```text
The full controller is not merely conservative; it preserves safety while turning residual-positive states into actionable CONTINUE decisions.
```

---

## Experiment 4：Ablation Study

### 目的

验证各模块必要性。

### Ablations

| Variant | Change | Expected risk |
|---|---|---|
| Full | no change | reference |
| w/o source-route | source-only exposure | higher FCR |
| w/o Gini | support only | misses concentration |
| w/o Eligibility Gate | direct repair/decision | higher cost or unstable decisions |
| w/o Residual Repair | eligibility-only | eligible-but-residual states may SAFE |
| w/o under-exposure | high-potential only | may revisit easy/high-signal routes |
| w/o runtime-potential | low-exposure only | may inspect low-value gaps |
| Random repair | random target | low repair efficiency |
| No ABSTAIN | forced SAFE/CONTINUE | unsafe certificate pressure |

### 指标

- FCR
- safe coverage
- actionability
- repair gain
- repair cost
- CONTINUE precision

### 预期图表

- Ablation table
- Repair gain-cost plot
- Boundary case table

### 主结论

```text
Source-route exposure diagnoses mismatch, eligibility controls certificate admission, and residual repair provides actionable continuation.
```

---

## Experiment 5：Trade-off and Sensitivity

### 目的

评估 controller 带来的收益是否值得额外成本，并分析阈值与预算的影响。

### Sweeps

#### Threshold sweep

```text
tau_support: 0.50, 0.60, 0.70, 0.75, 0.80, 0.90
tau_gini: 0.50, 0.60, 0.70, 0.80
```

#### Repair budget sweep

```text
budget: 0, 1, 2, 4, 8, 16
```

### 指标

- FCR
- safe coverage
- CONTINUE rate
- ABSTAIN rate
- residual found
- success / recall lift
- cost

### 预期图表

- Cost frontier：cost vs residual found
- Safety-cost curve
- Actionability-abstention curve
- Heatmap：thresholds vs FCR / ABSTAIN / cost

### 主结论

```text
The controller offers a configurable safety-actionability-cost trade-off rather than a free completion guarantee.
```

---

## Experiment 6：Route Inventory Robustness

### 目的

回应 route 是否人为设计、是否过度依赖特定 route inventory 的质疑。

### 方法

对同一数据集定义三种 route inventory：

```text
coarse route inventory
main route inventory
fine-grained route inventory
```

示例：

- WebArena coarse：navigation / evidence / action / verification
- WebArena main：navigation / search / inspect / form-action / confirmation
- WebArena fine：domain-specific routes

### 指标

- FCR
- AUROC
- actionability
- repair gain
- cost

### 预期结论

```text
The exact route inventory changes operational thresholds and cost, but source-route diagnosis remains useful when routes are declared before evaluation.
```

---

## Experiment 7：Oracle Leakage and Reproducibility Audit

### 目的

确保实验可信，避免 controller 隐性读取 post-hoc oracle。

### 检查项

1. Runtime controller 不读取：
   - oracle labels
   - oracle totals
   - recall
   - missing item counts
   - evaluator success before decision

2. Repair ranking 不读取 oracle。

3. Route inventory 在 run 前冻结。

4. 所有 config、seeds、thresholds、budgets、route mappings 输出到 artifacts。

5. 所有 decision logs 包含：
   - runtime-visible fields
   - decision
   - post-hoc label
   - evaluation metrics

### 自动测试

实现 `test_no_oracle_leakage.py`：

- monkeypatch oracle fields 为 unavailable，controller 仍可运行；
- 扫描 controller/repair ranking 输入 schema；
- 若 runtime decision 函数访问 post-hoc 字段则报错。

---

## 7. 统一日志与文件结构

建议 Codex 重构实验代码为如下结构：

```text
configs/
  datasets/
    webarena.yaml
    trec_total_recall.yaml
    repo_audit.yaml
  routes/
    webarena_routes.yaml
    trec_routes.yaml
    repo_routes.yaml
  experiments/
    e1_false_completion.yaml
    e2_geometry_diagnostic.yaml
    e3_baseline_comparison.yaml
    e4_ablation.yaml
    e5_tradeoff.yaml
    e6_route_robustness.yaml

src/
  datasets/
    webarena_adapter.py
    trec_adapter.py
    repo_audit_adapter.py
  routes/
    route_inventory.py
    route_mapper.py
  controller/
    exposure.py
    eligibility.py
    repair.py
    decision.py
  baselines/
    naive.py
    source_only.py
    verifier_gate.py
    fixed_budget.py
    voting.py
    trec_stopping.py
  evaluation/
    metrics.py
    posthoc_labels.py
    leakage_checks.py
  plotting/
    plot_false_completion.py
    plot_support_gini.py
    plot_decision_distribution.py
    plot_repair_frontier.py
    plot_sensitivity.py

outputs/
  traces/
  decisions/
  metrics/
  figures/
  tables/
  reports/
```

---

## 8. 统一 Trace Schema

每条 trajectory / audit run 输出一个 JSONL record：

```json
{
  "run_id": "...",
  "dataset": "...",
  "task_id": "...",
  "agent": "...",
  "seed": 0,
  "declared_scope": {
    "sources": [],
    "routes": []
  },
  "events": [
    {
      "t": 0,
      "agent": "...",
      "source": "...",
      "route": "...",
      "action": "...",
      "observation_summary": "...",
      "cost": {
        "llm_calls": 1,
        "tool_calls": 1,
        "tokens": 0,
        "wall_time": 0.0
      }
    }
  ],
  "stop": {
    "stopped": true,
    "stop_signal_type": "self_reported_done|no_new|agreement|budget|other",
    "stop_text": "..."
  },
  "runtime_features": {
    "source_only_support": 0.0,
    "source_route_support": 0.0,
    "source_route_gini": 0.0
  },
  "decision": {
    "policy": "full_controller",
    "decision": "SAFE|CONTINUE|ABSTAIN",
    "repair_targets": [],
    "repair_cost": 0.0
  },
  "posthoc": {
    "complete": false,
    "success": false,
    "recall": 0.0,
    "residual_items": 0
  }
}
```

注意：`posthoc` 字段只能在 decision 后写入。

---

## 9. 主文图表建议

### Table 1：Datasets and declared route inventories

列出 dataset、task type、source definition、route inventory、completion oracle、number of tasks/topics、cost unit。

### Figure 3：False completion and diagnostic geometry

建议合并两部分：

- false completion rate across datasets / agents
- source-route support vs Gini scatter

### Figure 4：Baseline comparison

展示不同方法的 SAFE / CONTINUE / ABSTAIN distribution，并标注 FCR、safe coverage、actionability。

### Figure 5：Repair Pareto frontier

横轴 cost，纵轴 residual found / recall gain / success lift。比较 Random、High-potential、Low-exposure、Residual-potential。

### Table 2：Ablation results

列 Full 和各消融版本的 FCR、safe coverage、actionability、repair gain、cost。

### Figure 6：Threshold and budget sensitivity

热力图或曲线展示 threshold/budget 对 FCR、ABSTAIN、cost、gain 的影响。

### Supplement

- route inventory details
- commands and configs
- full per-seed results
- generated sanity checks
- oracle leakage tests
- route robustness results
- additional code-task sanity results

---

## 10. 实施里程碑

### Milestone 0：现有代码审查

目标：

- 找出现有 controller 是否读取 oracle/post-hoc 字段。
- 梳理已有 requests/urllib3、policy/code-repo 实验代码。
- 输出 `EXPERIMENT_REFACTOR_AUDIT.md`。

### Milestone 1：统一 config 和 trace schema

目标：

- 所有实验输出统一 JSONL。
- route inventory 从 config 读取。
- posthoc 字段在 decision 后填充。

### Milestone 2：实现数据集 adapter

优先顺序：

1. TREC Total Recall
2. WebArena/BrowserGym
3. Repo audit case study
4. Optional SWE-bench/Defects4J

### Milestone 3：实现 baselines

先实现：

- Naive
- Source-only
- Fixed-budget
- Random repair
- High-potential
- Low-exposure
- Verifier-gate
- Full

TREC-specific baseline 可稍后实现。

### Milestone 4：跑 smoke test

每个数据集小规模跑通：

- WebArena：20 tasks
- TREC：5 topics
- Repo：requests/urllib3
- 每个 1 seed

检查：

- trace 是否完整
- route mapping 是否合理
- no oracle leakage test 是否通过
- 指标是否能生成

### Milestone 5：跑 pilot

规模：

- WebArena：50 tasks × 3 seeds
- TREC：10–15 topics × 3 seeds
- repo：现有 full case
- 输出初版图表

目标：

- 检查 false completion 是否足够明显
- 检查 source-route diagnostic 是否有效
- 调整图表设计，不调 oracle-based threshold

### Milestone 6：跑 main experiments

规模：

- WebArena：100–150 tasks × 3 seeds
- TREC：20–30 topics × 3 seeds
- repo：requests/urllib3
- Optional code sanity：SWE-bench Verified 30–50 tasks or Defects4J subset

### Milestone 7：生成论文图表与报告

输出：

```text
MAIN_RESULTS_REPORT.md
ABLATION_REPORT.md
TRADEOFF_REPORT.md
ROUTE_ROBUSTNESS_REPORT.md
REPRODUCIBILITY_REPORT.md
```

---

## 11. 成功标准

实验重构后，主文至少应能支持以下结论：

1. 在公开真实任务中，agent/workflow 的 stop signal 确实可能对应 incomplete outcome。
2. Source-only coverage 会高估完成状态，source-route geometry 能暴露更细的 evidence-condition mismatch。
3. Full controller 相比 Naive / Source-only 能降低 unsafe SAFE；相比 Verifier-gate 不只是 fail-closed，而是能产生 actionable CONTINUE。
4. Residual repair 可以发现更多 residual evidence，但需要额外成本。
5. 消融证明 source-route、Gini、eligibility gate、residual repair 分别对 safety、diagnosis、actionability、cost 有贡献。
6. 方法边界清楚：只在 declared source-route scope 内讨论证书，不保证开放世界绝对完成。

---

## 12. 给 Codex 的执行要求

Codex 修改时必须遵守：

1. 不删除现有有效实验代码，先迁移、再重构。
2. 所有新实验必须 config-driven。
3. route inventory 必须在运行前固定并输出。
4. runtime decision 禁止读取 oracle/post-hoc 字段。
5. 每个实验都必须生成 trace、decision、metrics、figures、report。
6. 每张图都必须可由保存的 CSV/JSON 复现。
7. 所有 denominator 必须写清楚。
8. 不要把 generated tasks 写成主实验，只作为 supplement sanity checks。
9. 不要把 residual-potential 写成最优搜索策略。
10. 不要只报告成功率，必须报告 safety、actionability、cost 三类指标。

---

## 13. 可直接给 Codex 的总任务说明

请按照本文档重构当前 Evidence-Condition Geometry 论文的实验部分。目标是把实验从主要依赖 controlled/generated tasks，升级为以公开真实 benchmark 和可复现 completion oracle 为主的实验体系。优先实现 WebArena/BrowserGym 和 TREC Total Recall 两条主线，并保留 requests/urllib3 作为 repository audit case study。原 policy-docset/code-repo 只作为 supplement controlled sanity checks。

请先审查现有实验代码和数据结构，建立统一 config、route inventory、trace schema、decision schema 和 metric schema。之后依次实现 false completion existence、source-only vs source-route diagnostic、baseline comparison、ablation、trade-off/sensitivity、route robustness、oracle leakage audit 七组实验。所有 controller 和 repair ranking 在 runtime 阶段不得读取 oracle labels、oracle totals、post-hoc recall 或 undiscovered true-item counts。

主指标包括 FCR、safe coverage、actionability、ABSTAIN rate、CONTINUE precision、task success/recall、repair gain、token/tool/time cost、cost-normalized gain。主图包括 false completion rate、support-Gini diagnostic scatter、baseline decision distribution、repair Pareto frontier、ablation table、threshold/budget sensitivity heatmap。每组实验都要输出 CSV/JSON、图表和 markdown report，保证结果可复现。
