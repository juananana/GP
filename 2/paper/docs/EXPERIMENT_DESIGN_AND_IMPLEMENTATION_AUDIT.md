# Experiment Design and Implementation Audit

本文档用于逐项审查论文实验和方法实现是否自洽。它不是论文正文的宣传性叙述，而是把实验是怎么构造、怎么运行、怎么评分、怎么导出图表，以及哪些地方最容易误读或出问题写清楚。所有路径均相对于仓库中的 `2/` 目录，除非另有说明。

## 0. 当前状态速查

- 实验代码没有全部放在一个单文件里，但主实验代码集中在 `analysis/research_object_geometry/real_agent_pilot/`；配置在 `configs/`；论文图表生成在 `paper/scripts/make_paper_figures.py`。
- 主文现在同时保留图和表：Figure 3 是 diagnostic evidence，Figure 4 是 controller evaluation；Table 1 是 source-only/source-route ablation，Table 2 是单个 `urllib3` boundary case，Table 3 是 seeded unsafe/complete controller counts。
- Figure 4 现在不是“全是 1”的比例图，而是 count dashboard：左图只显示 400 个 seeded unsafe states 中各策略输出 unsafe `SAFE`、actionable `CONTINUE`、fail-closed `ABSTAIN` 的数量；`1200/1200` complete-state `SAFE` coverage 写入图内短注和 caption；右图显示 repair gain-cost tradeoff。
- “Verifier-gate vs Full controller”的主结论不是 Full 在 seeded warning denominator 上更安全，而是 Full 同样避免 unsafe `SAFE`，同时把 productive unsafe states 转成可行动的 `CONTINUE`；Verifier-gate 是 fail-closed `ABSTAIN`，不给 source-route diagnosis 或 repair target。
- 主文已经恢复独立 `Conclusion`；`Related Work` 已改成围绕 stopping、agent/tool workflow、verification/oversight 三条脉络说明本文区别，而不是单纯罗列文献。当前主文 PDF 为 10 页，References 从第 8 页开始，技术内容控制在 7 页内。
- 当前仍应克制的边界：external repository oracle 是 pattern-defined，不是语义金标准；residual-potential 是启发式 repair target，不是 optimal active search；`SAFE` 是配置预算和 runtime-visible signals 下的 bounded certificate，不是 universal completion guarantee。

## 1. 实验要验证什么

论文主张不是“系统可以普遍保证 completion”，而是一个更窄的 bounded completion-audit 命题：

1. Local stop evidence 不能直接当作 global completion certificate。
2. Evidence condition 必须包含 source-route geometry，也就是证据来自哪些 source，以及通过哪些 route 得到。
3. Source-only coverage 可能造成 illusion：文件/来源看起来都覆盖了，但 route 分布过窄。
4. Eligibility 只是考虑 `SAFE` 的前提，不是 proof；如果 repair 找到 residual evidence，就应当 `CONTINUE`。
5. Full controller 的价值是“安全 + 可行动 + 成本权衡”：它不是只 fail closed，而是在带 runtime residual candidates 的 unsafe states 上返回 `CONTINUE` 并给出下一步 audit target。

因此实验主问题是：

- Safety: controller 是否避免在 oracle-unsafe 状态输出 `SAFE`，即降低 false certification rate (FCR)。
- Usefulness/actionability: 和 generic verifier-gate 相比，Full controller 是否把带 runtime residual candidates 的 unsafe states 转成 actionable `CONTINUE`，而不是 opaque `ABSTAIN`。
- Cost: residual repair 是否以显式 audit cost 换来 residual evidence yield，且这个 repair 策略不是被夸张成 optimal active search。
- Diagnostic chain: 从 local stop signals 到 source-only illusion，再到 source-route mismatch、eligibility-not-proof、residual repair closed loop，实验是否每一环都有证据支撑。

## 2. 代码和数据目录

关键目录如下：

- `configs/`: 运行配置。
- `analysis/research_object_geometry/real_agent_pilot/`: real-agent-style 和 external repository validation 的主要代码与日志。
- `analysis/research_object_geometry/real_agent_pilot/credibility_supplement/`: 论文主结果、supplement 表格、统一 CSV/JSON 导出和部分图的 assembler。
- `analysis/research_object_geometry/results/`: controlled/generated geometry 实验的中间结果。
- `paper/scripts/make_paper_figures.py`: 生成论文 Figure 3/4 和部分表格的脚本。
- `paper/generated/`: LaTeX 表格片段。
- `paper/figures/`: 论文图。
- `paper/build/`: 编译后的主文和 supplement PDF。

主要入口：

- `analysis/research_object_geometry/real_agent_pilot/scripts/run_blind_policy_task.py`
- `analysis/research_object_geometry/real_agent_pilot/scripts/run_blind_code_task.py`
- `analysis/research_object_geometry/real_agent_pilot/external_validation_requests/run_external_requests_validation.py`
- `analysis/research_object_geometry/real_agent_pilot/external_validation_v2/run_external_validation_v2.py`
- `analysis/research_object_geometry/real_agent_pilot/controller_validation_v1/run_controller_validation_v1.py`
- `analysis/research_object_geometry/real_agent_pilot/controller_validation_v1/run_controller_validation_v2.py`
- `analysis/research_object_geometry/real_agent_pilot/credibility_supplement/run_credibility_supplement.py`
- `paper/scripts/make_paper_figures.py`

配置读取由 `analysis/research_object_geometry/real_agent_pilot/experiment_config.py` 完成。默认配置是 `configs/full_200seed.yaml`，也可以通过环境变量 `EVIDENCE_CONFIG` 指定。

实验代码不是全部挤在一个单文件里，但主实验代码集中在一个主目录：

- 核心实验目录：`analysis/research_object_geometry/real_agent_pilot/`。这里包含 generated tasks、external requests/urllib3 validation、controller validation、claim-verification sanity check、结果聚合器。
- 配置目录：`configs/`。seeds、thresholds、budgets、routes、condition route lists、oracle paths、output paths 在这里声明。
- 论文图表生成：`paper/scripts/make_paper_figures.py`。它不重新定义实验逻辑，只读取已经导出的结果表并生成 Figure 3/4 与 LaTeX 表。
- 论文输出：`paper/generated/`、`paper/figures/`、`paper/build/`。

如果只想审查“实验如何产生”，优先看 `real_agent_pilot/` 和 `configs/`；如果想审查“论文图表如何从结果写入论文”，再看 `paper/scripts/make_paper_figures.py`。

## 3. 配置文件

当前有三组配置：

- `configs/main_3seed.yaml`: 快速复现配置。`validation/safe_state/challenger` seeds 都是 `[0,1,2]`，safe-state budgets 是 `[1,2,4]`。
- `configs/full_200seed.yaml`: 论文主结果配置。`validation=200`，`challenger=200`，`safe_state=6000`，阈值为 `tau_support=0.75`、`tau_gini=0.70`，post-hoc recall threshold 为 `0.90`。
- `configs/sensitivity.yaml`: 阈值/预算敏感性配置。`tau_support=[0.50,0.60,0.70,0.75,0.80,0.90]`，`tau_gini=[0.50,0.60,0.70,0.80,0.90]`，safe-state budgets 为 `[1,2,4,6,8]`。

配置还声明：

- tasks 和 routes；
- external oracle paths；
- output paths；
- runtime-visible fields；
- posthoc-oracle-only fields。

这是复现和防泄漏检查的核心：所有 seeds、thresholds、budgets、routes、oracle paths、output paths 都应从 config 读出，而不是散落在代码里。需要注意的是，部分 legacy validation script 仍有本地常量定义，例如 route pattern、file list、route list；论文当前主要通过 supplement assembler 和 figure script 做统一读配置与导出。若要进一步工程化，建议把 legacy script 中的常量也完全 config 化。

## 4. Runtime-Visible 与 Post-Hoc-Only 字段

配置中声明 controller 可在运行时使用的字段：

- `task_id`
- `repo_id`
- `run_id`
- `condition`
- `agent_id`
- `round_id`
- `event_id`
- `timestamp`
- `query_text`
- `tool_name`
- `action_type`
- `source_path`
- `source_family`
- `search_route`
- `source_route_stratum`
- `discovered_item_id`
- `new_item`
- `self_reported_completion`
- `self_reported_confidence`
- `stop_reason`
- `token_or_cost`
- `notes`

配置中声明只能用于 post-hoc scoring 的字段：

- `oracle_label`
- `oracle_bucket`
- `oracle_total`
- `recall`
- `bounded_oracle_recall`
- `undiscovered_true_item_count`
- `hidden_missing_mass`

审查重点：

- controller 决策、repair target 排序、threshold/budget sweep 不应读取 oracle labels、oracle totals、post-hoc recall、undiscovered true-item counts。
- oracle labels 只能在 decision 固定之后用于计算 FCR、safe coverage、recall、missed items、repair gain。
- 文本叙述中必须区分“运行时 controller 可见的 signal”和“post-hoc evaluation 用的 oracle score”。

## 5. 任务和状态

实验覆盖四类 bounded audit family：

1. `policy_docset_v1`: generated policy/docset task。主 stop failure 是 homogeneous local route reuse。
2. `code_repo_v1`: generated code/repo task。主 stop failure 同样是 homogeneous local route reuse。
3. `requests`: frozen external repository audit，routes 包括 `tls_route`、`timeout_route`、`exception_route`、`compat_route`。
4. `urllib3`: frozen external repository audit，routes 包括 `timeout_route`、`retry_route`、`tls_route`、`exception_route`、`cleanup_route`。

状态类型：

- `fixed_stop_state`: 从固定 audit trajectory 得到的 stop proposal，例如 homogeneous、route_partitioned、extended_audit。
- `seeded_unsafe_repair`: 对 external repo unsafe states 做 seeded repair validation。
- `seeded_safe_complete`: 对 complete/safe states 做 order/budget perturbation，检查 safe coverage。

重要 denominator 区分：

- `urllib3` boundary case 是单个 eligible-but-residual-positive fixed state。它的 denominator 是 1，说明 eligibility is not proof。
- controller seeded counts 使用 400 unsafe repair states 和 1200 complete safe states。它们验证 decision policy 的 FCR、safe coverage、`CONTINUE`/`ABSTAIN` rate。
- 这两个 denominator 不能混读。一个是 boundary diagnosis，一个是 seeded decision validation。

## 6. Source-Route Geometry 指标

核心 evidence-condition 指标：

- `support_ratio`: 已覆盖 source-route strata / 全部 source-route strata。
- `exposure_gini`: exposure 在 source-route strata 上的集中程度。越高说明越集中，越可能 local/route-mismatched。
- `weak_plausible_gap`: 运行时 potential 大于 0 但 exposure 为 0 的 strata 数。
- `runtime_potential`: 只从运行时可见的 source text 和 route pattern 计算，不读取 oracle label。

主要判定阈值：

- `tau_support = 0.75`
- `tau_gini = 0.70`
- `eval_only_recall_threshold = 0.90`

其中前两个用于 controller eligibility；最后一个只用于 post-hoc false-certification scoring。

## 7. Controller 方法实现

论文里的 controller 可以概括为：

1. 从 ledger 中计算 source-route exposure。
2. 计算 support、Gini、weak plausible gap 等 evidence-condition features。
3. 判断 source-route eligibility：`support >= tau_support` 且 `gini <= tau_gini`。
4. 若 eligibility 不满足，或存在 runtime weak-plausible gap/residual warning，则不直接 `SAFE`。
5. 在有预算时运行 repair policy，选择 target strata。
6. 如果 repair 产生此前未见过的 runtime candidate evidence，返回 `CONTINUE` 并记录 target。
7. 如果 eligibility 满足、weak gap 为 0、且 budgeted repair 没有 runtime residual candidate，返回 `SAFE`。
8. 如果没有证书且 repair 没有 productive runtime target，返回 `ABSTAIN`。

当前实现中，controller 决策已经拆成 runtime-only decision 和 post-hoc scoring。聚合层使用的 `runtime_controller_decision` 是：

```python
geometry_ok = support >= SAFE_SUPPORT_MIN and gini <= SAFE_GINI_MAX
if runtime_residual_items > 0 or weak_plausible_gap > 0:
    return "CONTINUE"
if geometry_ok:
    return "SAFE"
return "ABSTAIN"
```

`recall`、`new_true_items`、`oracle_total`、`posthoc_missed_items` 只用于事后评分和诊断表述。fixed observed states 上，post-hoc recall 可以说明某个状态是否 unsafe，但不能决定 `SAFE/CONTINUE/ABSTAIN`。seeded repair states 上，`runtime_residual_items` 表示 repair 扫描产生的此前未见候选证据数量；`new_true_items` 表示这些候选中事后被 oracle 标成 true 的数量。

## 8. Baselines 和五类消融

### 8.1 Granularity Ablation

比较：

- Source-only
- Source-route

实现位置：

- `source_only_ablation()`
- 结果：`credibility_supplement/results/source_only_vs_source_route.csv`
- 统一导出：`unified_localization_risk_trend.csv/json`

逻辑：

- Source-only 假设 source coverage 已满，因此 homogeneous local evidence 也可能被误判 eligible。
- Source-route 进一步要求 route coverage，使 route-mismatched local evidence 暴露为 support gap 和 high Gini。

### 8.2 Proof-Separation Ablation

比较：

- Eligibility-only
- Full controller

核心目的：

- 证明 eligibility 是 precondition，而不是 proof。
- `urllib3` route_partitioned boundary: support=0.800，Gini=0.647，eligibility-only 会 `SAFE`，但仍有 6 个 runtime weak-plausible strata；Full controller 因 weak-gap signal 返回 `CONTINUE`，post-hoc recall=0.835 和 missed items=115 只用于证明该拒绝认证是必要的。

结果：

- `eligibility_passed_unsafe_boundary.csv`

### 8.3 Decision-Rule Ablation

比较：

- Naive stop
- Source-only
- Eligibility-only
- Verifier-gate
- Full controller

实现位置：

- `paper/scripts/make_paper_figures.py::controller_variant_summary()`
- `credibility_supplement/run_credibility_supplement.py::_decision_variant_metrics()`

定义：

- Naive stop: 所有 stop proposal 都 `SAFE`。
- Source-only: 忽略 route geometry，实质上对这些 seeded states 也会 `SAFE`。
- Eligibility-only: `geometry_ok` 就 `SAFE`，否则 `ABSTAIN`。
- Verifier-gate: 不使用 source-route geometry，只看显式 `unresolved_warning` 或 `residual_warning`；有 warning 就 `ABSTAIN`，否则 `SAFE`。不能用 support/Gini/weak-gap 派生 warning。
- Full controller: 使用 source-route diagnosis 和 residual repair；存在 runtime weak gap 或 runtime residual candidates 时返回 `CONTINUE`。

关键结果：

- Naive 和 Source-only 在 seeded unsafe states 上 FCR=1.0。
- 在 seeded residual-warning unsafe states 上，Verifier-gate 和 Full controller FCR=0。
- 在同一 seeded denominator 上，Verifier-gate unsafe-state `ABSTAIN` rate=1.0。
- Full controller unsafe-state `CONTINUE` rate=1.0。
- Full controller 与 Verifier-gate 的差别不是更安全，而是更 actionable。
- 在 fixed stop states 上，如果没有显式 warning，Verifier-gate 没有 source-route geometry 可用，因此会像普通 stop gate 一样误 `SAFE` localized unsafe stops；这正是 source-route diagnosis 必要性的证据，不应把 verifier-gate 描述成所有 denominator 上都安全。

### 8.4 Repair-Target Ablation

比较：

- Random
- High-potential
- Residual-potential

实现位置：

- `repair_policy_ci()`
- `controller_variant_summary()`
- `seeded_safe_state_validation()`
- external validation scripts 中的 challenger detail。

目标排序：

- Random: seed-controlled random order。
- High-potential: 按 runtime potential 最高优先。
- Residual-potential: 按 under-exposure 和 runtime potential 的组合打分，优先检查“有潜力但覆盖不足”的 strata。

当前主结论：

- Residual-potential mean gain 高，但 cost 也更高。
- High-potential 在 cost-normalized sense 上有竞争力。
- Residual-potential 是 mechanism-aligned heuristic，不是 optimal active search。

### 8.5 Threshold/Budget Sensitivity

比较：

- 不同 `tau_support`、`tau_gini`
- 不同 repair budget

实现位置：

- `threshold_and_budget_sensitivity()`
- 结果：`threshold_sensitivity.csv`、`budget_sensitivity.csv`、`sensitivity_summary.csv`
- 统一导出：`unified_threshold_budget_sweep.csv/json`、`unified_safety_cost_frontier.csv/json`

目的：

- 证明阈值和预算主要改变 `SAFE`/`CONTINUE`/`ABSTAIN` mixture 与 cost。
- 在当前 external validation sweep 中没有产生 false certification。
- 这支持 practical use：用户可以通过 threshold/budget 调节保守程度。

## 9. Generic Verifier-Gate Baseline

Verifier-gate 是为了排除“本文只是 fail-closed verifier”的解释。

规则：

```python
unresolved = bool(row.get("unresolved_warning", False))
residual = bool(row.get("residual_warning", False))
return "ABSTAIN" if unresolved or residual else "SAFE"
```

它不使用：

- source-route support；
- Gini；
- weak plausible gap；
- repair target diagnosis；
- oracle totals；
- post-hoc recall。

它的作用：

- 在 seeded residual-warning unsafe states 上可以避免 unsafe `SAFE`，因此在 Figure 4 的 seeded denominator 上和 Full controller 一样 FCR=0。
- 但是它不会告诉 audit 应该继续到哪个 source-route stratum。
- 在带 runtime residual candidates 的 unsafe states 上它 fail closed 为 `ABSTAIN`，而 Full controller 返回 `CONTINUE`。
- 在没有显式 warning 的 fixed stop states 上，它不能靠 source-route support/Gini 拒绝 unsafe stop；这部分由 granularity/proof-separation ablation 说明。

论文中应强调：

- Full controller 的优势不是“Verifier-gate 在 residual-warning denominator 上会不安全”。
- Full controller 的优势是 safe + actionable：同样避免 false certification，但把 residual-positive states 变成下一步 audit action。

## 10. Repair 实验

External repair validation 使用固定 base state 和 seeded target ordering。

对 `requests`：

- 输入：`controller_validation_v1/results/controller_validation_v2_detail.csv`
- 主要 seeded unsafe repair denominator：200 seeds per relevant repair policy。
- 默认 repair budget：`external_requests=4`。

对 `urllib3`：

- 输入：`external_validation_v2/results/controller_challenger_detailed.csv`
- 主要 seeded unsafe repair denominator：200 seeds per relevant repair policy。
- 默认 repair budget：`external_urllib3=5`。

聚合成 Figure 4 使用的 denominator：

- unsafe denominator: 400 = requests 200 + urllib3 200, only residual-potential branch for decision-policy comparison。
- safe denominator: 1200 = requests/urllib3 safe complete perturbations under residual-potential branch。

主要数字：

- Residual-potential: mean repair gain 253.0, mean cost 4275.5。
- Random: mean repair gain 69.0, mean cost 3481.1。
- High-potential: mean repair gain 226.0, mean cost 3824.0。

审查重点：

- repair gain 是 post-hoc oracle scoring，不是 controller 运行前知道的东西。
- repair target 排序必须只基于 runtime potential 和 exposure。
- cost 定义应统一：post-stop scanned lines 加 extraction/search event cost，不能混合不可比成本。

## 11. Safe-State Validation

目的：

- 不只看 unsafe states，也要验证 complete/safe states 上 Full controller 不会过度 `ABSTAIN` 或 `CONTINUE`。

实现：

- `seeded_safe_state_validation()`
- 对 `requests route_partitioned` 和 `urllib3 extended_audit` 构造 complete/safe base state。
- 在不同 challenger order 和 budgets 下做 perturbation。
- 对每个 perturbation 决策。

当前结果：

- `requests`: 3000 runs, safe coverage=1.0, FCR=0。
- `urllib3`: 3000 runs, safe coverage=1.0, FCR=0。

审查重点：

- safe-state validation 的 `oracle_safe` 来自 post-hoc cumulative recall >= 0.90。
- controller 的 `SAFE` 分支应依赖 eligibility 和 nonproductive repair，而不是 oracle recall。
- safe-state denominator 与 unsafe repair denominator 不同。

## 12. 统一结果导出

统一导出目录：

`analysis/research_object_geometry/real_agent_pilot/credibility_supplement/results/`

Manifest：

- `unified_results_manifest.json`

核心导出：

- `unified_decision_variants.csv/json`
- `unified_repair_variants.csv/json`
- `unified_controller_count_table.csv/json`
- `unified_localization_risk_trend.csv/json`
- `unified_threshold_budget_sweep.csv/json`
- `unified_safety_cost_frontier.csv/json`
- `unified_state_metrics.csv/json`

统一表字段通常包括：

- `table`
- `task`
- `policy`
- `state_type`
- `seed`
- `budget`
- `n`
- `unsafe_n`
- `safe_n`
- `fcr`
- `safe_coverage`
- `continue_rate`
- `abstain_rate`
- `repair_gain`
- `repair_cost`

注意：

- 某些 metric 在某些 state type 上无定义，因此为 `NaN`。例如 safe coverage 对全 unsafe states 没有意义，FCR 对全 safe states 没有意义。
- `seed=mixed` 和 `budget=mixed/fixed` 是聚合行，不是单个 run。
- `unified_state_metrics.csv` 是最细的合并表之一，目前约 14209 行，含 fixed stop、seeded unsafe repair、seeded safe complete。

## 13. Figure 和 Table 生成

Figure 3 / Figure 4 的主要生成脚本：

```powershell
$env:EVIDENCE_CONFIG='configs/full_200seed.yaml'
python paper/scripts/make_paper_figures.py
```

Figure 4 来自：

- `controller_decision_detail.csv`
- `seeded_safe_state_validation.csv`
- `repair_policy_ci.csv`
- `controller_variant_comparison.csv`

当前 Figure 4 是 1x2 dashboard：

- left: decision safety/actionability count dashboard。红/橙/灰显示 400 个 seeded unsafe residual-warning states 中被判成 unsafe `SAFE`、actionable `CONTINUE`、fail-closed `ABSTAIN` 的数量；绿色点显示 1200 个 seeded complete states 中被判成 `SAFE` 的数量。早先 rate 版本很多值天然等于 1，容易被误读成“全是 1”；count 版本直接显示 denominator 和 count。
- right: repair gain-cost tradeoff with error bars。

Supplement 表格生成：

```powershell
$env:EVIDENCE_CONFIG='configs/full_200seed.yaml'
python analysis/research_object_geometry/real_agent_pilot/credibility_supplement/run_credibility_supplement.py
```

论文编译：

```powershell
cd paper
latexmk -pdf -interaction=nonstopmode -outdir=build evidence_condition_geometry_aaai_v2.tex
latexmk -pdf -interaction=nonstopmode -outdir=build supplementary_material.tex
```

## 14. 推荐完整复现实验流程

快速检查：

```powershell
cd 2
$env:EVIDENCE_CONFIG='configs/main_3seed.yaml'
$P='analysis/research_object_geometry/real_agent_pilot'
python "$P/scripts/run_blind_policy_task.py"
python "$P/scripts/run_blind_code_task.py"
python "$P/external_validation_requests/run_external_requests_validation.py"
python "$P/external_validation_v2/run_external_validation_v2.py"
python "$P/credibility_supplement/run_credibility_supplement.py"
python paper/scripts/make_paper_figures.py
```

论文主结果：

```powershell
cd 2
$env:EVIDENCE_CONFIG='configs/full_200seed.yaml'
$P='analysis/research_object_geometry/real_agent_pilot'
python "$P/scripts/run_blind_policy_task.py"
python "$P/scripts/run_blind_code_task.py"
python "$P/external_validation_requests/run_external_requests_validation.py"
python "$P/controller_validation_v1/run_controller_validation_v1.py"
python "$P/controller_validation_v1/run_controller_validation_v2.py"
python "$P/external_validation_v2/run_external_validation_v2.py"
python "$P/credibility_supplement/run_credibility_supplement.py"
python paper/scripts/make_paper_figures.py
```

敏感性：

```powershell
cd 2
$env:EVIDENCE_CONFIG='configs/sensitivity.yaml'
python analysis/research_object_geometry/real_agent_pilot/credibility_supplement/run_credibility_supplement.py
python paper/scripts/make_paper_figures.py
```

编译：

```powershell
cd 2/paper
latexmk -pdf -interaction=nonstopmode -outdir=build evidence_condition_geometry_aaai_v2.tex
latexmk -pdf -interaction=nonstopmode -outdir=build supplementary_material.tex
```

## 15. 当前主结果

主要结果可以简写为：

1. Homogeneous local stops 产生 source-only illusion。source-only support 可以看起来是 1.0，但 source-route support 和 Gini 暴露 route mismatch。
2. `urllib3` boundary 证明 eligibility is not proof：support=0.800、Gini=0.647 已通过 eligibility，但仍有 6 个 runtime weak-plausible strata；post-hoc recall=0.835 且 missed items=115。
3. Decision ablation 证明 Full controller 与 Verifier-gate 的区别是 actionability：二者 FCR=0，但 Verifier-gate 对 seeded unsafe repair states 全部 `ABSTAIN`，Full controller 对 400 个带 runtime residual candidates 的 seeded unsafe states 全部 `CONTINUE`。
4. Repair ablation 证明 residual-potential high-yield but higher-cost，不是免费 certificate。
5. Threshold/budget sweep 说明 conservatism 可调，在当前 external validation sweep 中未产生 false certification。

## 16. 最值得仔细检查的问题

### 16.1 Post-hoc recall 是否混入 runtime decision

这是最重要的审计点，目前已做过一次修复：旧的 `state_decision(recall, productive)` 已删除，聚合/绘图层改为 `runtime_controller_decision(support, gini, weak_plausible_gap, runtime_residual_items)`。`recall` 仍保留在结果表中，但只用于 oracle-safe/unsafe denominator、FCR、safe coverage、missed item 等 post-hoc scoring。

建议检查：

- 主文是否没有说 controller 运行时用 recall。
- Figure/Table caption 是否清楚说明 post-hoc recall 是 evaluation-only。
- 新增字段 `runtime_residual_items` 是否完整传递到 controller detail、unified exports、Figure 4 生成脚本。

### 16.2 Verifier-gate 的 warning 定义是否公平

Verifier-gate 使用显式 `unresolved_warning` 和 `residual_warning`。当前 residual warning 来自 runtime residual candidates，不来自 oracle-positive `repair_gain`；fixed-state weak-gap 是 Full controller 的 source-route diagnosis signal，不再喂给 Verifier-gate。

建议检查：

- warning 是否太强，是否等价于“已经知道 residual positive”。
- 如果 verifier-gate 在实际运行中也需要 repair 才知道 residual warning，那么它的 cost 是否应计入。
- 论文中是否清楚说明 Verifier-gate 是 generic fail-closed baseline，不给 source-route target。
- 论文中是否清楚说明 Verifier-gate 只在 seeded residual-warning denominator 上 FCR=0，不代表它能解决 un-warned fixed stop localization。

### 16.3 Fixed stop states 与 seeded states 的 denominator

建议逐表检查：

- `eligibility_passed_unsafe_boundary.csv`: denominator=1。
- `controller_variant_comparison.csv`: unsafe denominator=400, safe denominator=1200。
- `unified_controller_count_table.csv`: 各行 denominator 不同，例如 observed stop states、seeded repairs、seeded safe states。

论文中不能把 boundary case 的比例和 seeded counts 的比例直接相加或并列成同一统计总体。

### 16.4 Oracle 是 pattern-defined，不是 semantic gold

External repository oracle 是 frozen pattern-defined oracle。它适合验证 controller logic 和 source-route mismatch，但不能声称代表人类专家的 complete semantic audit。

建议检查：

- 论文是否避免说 universal completion guarantee。
- Discussion 是否承认 pattern-defined oracle 的边界。
- claim-verification pilot 是否只作为 small sanity check。

### 16.5 Repair target 策略不是 optimal active search

Residual-potential 是 under-exposure * potential 的 heuristic。它在当前状态高 yield，但不应声称 optimal。

建议检查：

- 是否把 high-potential 的竞争性讲清楚。
- 是否报告 cost，而不是只报告 gain。
- Figure 4 是否能体现 cost tradeoff。

### 16.6 Seeds 和 budgets 的聚合方式

`full_200seed.yaml` 中 `safe_state=6000`，实现中会按 task/challenger/budget cells 分摊 seed 数，最终当前 safe-state validation 是每个 external task 3000 runs。

建议检查：

- 论文里写的是 runs 数还是 seed 数，避免把 6000 seed budget 误写成每个 cell 6000。
- `seed=mixed` 的聚合表不要被误解为单 seed。

### 16.7 成本定义是否完全一致

Repair cost 在不同任务/脚本中可能由 candidate lines、scan cost、extraction events 聚合而来。

建议检查：

- `requests` 与 `urllib3` 的 cost 是否同量纲。
- generated tasks 的 novelty-per-cost 与 external repo repair cost 是否只在同任务内比较。
- Figure 4 的 cost comparison 是否只基于同一 external validation setting。

## 17. 建议的审查清单

逐项勾选：

- [ ] 所有论文主结果均能从 `full_200seed.yaml` 复现。
- [ ] `main_3seed.yaml` 能完成轻量 run。
- [ ] `sensitivity.yaml` 能生成 threshold/budget sweep。
- [ ] controller 决策代码未读取 oracle labels、oracle totals、post-hoc recall。
- [ ] repair target ranking 未读取 oracle labels。
- [ ] FCR denominator 是 oracle-unsafe states。
- [ ] safe coverage denominator 是 oracle-safe complete states。
- [ ] `CONTINUE` rate 和 `ABSTAIN` rate 在 unsafe states 上解释清楚。
- [ ] Table 2 boundary denominator 与 supplement controller count denominator 分开解释。
- [ ] Verifier-gate 不被 strawman 化：它安全，但不可行动。
- [ ] Residual-potential 不被说成 optimal。
- [ ] claim-verification pilot 不被当成主实验。
- [ ] Figure 3 支撑 diagnostic chain。
- [ ] Figure 4 支撑 safe + actionable + cost。
- [ ] Supplement 中有 runtime-visible vs post-hoc-only fields。
- [ ] Unified CSV/JSON export 包含 task、policy、state_type、seed、budget 和核心 metrics。

## 18. 如果要进一步加固

最值得做的三项加固：

1. 为 Verifier-gate 增加 cost accounting：如果 residual warning 需要 repair 才能产生，就给 verifier-gate 明确同等 repair cost 或说明它是 warning-only admission baseline。
2. 写一个 automated leakage test：扫描 controller/repair ranking 函数调用链，断言不可访问 `oracle_label`、`oracle_total`、`recall`、`undiscovered_true_item_count`。
3. 把 legacy script 中仍写死的 file/pattern 常量进一步迁入 config，降低配置外设定的空间；routes 和 condition route lists 当前已在 config 中声明。

这三项不会改变论文主线，但会显著提高实验逻辑的可审计性。
