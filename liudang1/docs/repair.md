## 结论

**实验设计已经基本闭环，但实验结果还没有闭环。**

这轮并不是没有进展。相反，你已经把下一步真正需要跑的在线实验搭成了可复现 harness：补充材料新增了 `Online Audit-Controller Closure Status`，明确规划了 Requests TLS 的 `seed04–seed08`、四种 discovery 配置和七种 audit policy。问题在于，目前这些仍然只是 dry-run manifest，在线 post-audit verifier / holdout agents 还没有真正执行。

所以现在最准确的判断是：

> **论文已经形成了可信的现象诊断稿，也搭好了方法实验框架；但还不能作为完整的 AAAI 方法论文投稿。**

---

# 一、现在已经完善好的部分

## 1. 核心科学问题已经立住

论文已经能够稳定证明：

[
\text{high agreement}
\not\Rightarrow
\text{complete coverage}
]

而且不是只有合成案例。Click 与 Requests 两个真实仓库已经支持这一结论：

* Click 中，标准 summarizer 连续三个 seeds 都自报完成，但 Recall 只有 `0.685–0.745`，Precision 接近 `1.0`；
* Requests 中，raw union 将 Recall 提升到 `0.829–0.859`，但仍未达到 `0.95` 的停止阈值，说明遗漏不仅来自聚合阶段，也来自候选池本身不完整。

这部分可以认为已经完成。

---

## 2. 两类失败机制已经区分清楚

当前论文已经将 false convergence 拆成：

* **Aggregation loss**：少数 Agent 已经找到真实条目，但 consensus 或 summarizer 将其丢弃；
* **Common blind spots**：所有 Agent 都没有发现某些条目，因此 raw union 也无法恢复。

Figure 1 和 Section 3.4–3.5 已经表达得比较清楚。

这个拆分很重要，因为它决定后续审查策略不能只有一种：

| 失败机制               | 对应策略                                                 |
| ------------------ | ---------------------------------------------------- |
| Aggregation loss   | singleton audit                                      |
| Common blind spots | boundary-focused holdout 或 source-partitioned review |

---

## 3. certificate 与 audit policy 已经正确解耦

现在流程已经合理：

[
\text{pre-audit certificate}
\rightarrow
\text{targeted audit}
\rightarrow
\text{post-audit certificate}
]

而且明确规定：

* pre-audit 不使用 oracle；
* pre-audit 不使用 holdout gain；
* holdout gain 只能在审查之后更新 ledger；
* oracle 只用于离线评分。

补充材料的闭环协议和流程清单已经写清楚这一点。

Figure 2 也已经基本合格，可以保留。

---

## 4. v2 的可信性审计已经做对

现在没有继续将 v2 包装成“已经成功的方法”，而是诚实地报告：

| 设置                    |  AUROC | Safe Coverage |
| --------------------- | -----: | ------------: |
| v2 in-distribution    | `.999` |        `.966` |
| metadata-only probe   | `.988` |        `.000` |
| leave-one Click       | `.591` |        `.000` |
| leave-one policy docs | `.546` |        `.000` |
| leave-one Requests    | `.695` |        `.000` |

这说明：

> 当前 v2 能做同分布诊断，但还没有学到可跨仓库迁移的安全停止规律。

这一轮审计已经完成，不需要继续围绕同分布 AUROC 调参。

---

## 5. 论文排版已经基本进入可用状态

当前正文技术内容控制在 7 页内，References 从第 7 页后开始。Figure 2 已改成跨栏框架图，Conclusion 也不再只有一句口号，而是增加了两类机制和未来验证边界。

论文结构暂时不需要大改。

---

# 二、实验还差什么？最关键的缺口只有一个

## 在线 audit-controller 主实验还没有真正运行

补充材料 Section 11 已经明确写出：

> seed04 有 online discovery evidence，但 online post-audit verifier / holdout agents 尚未执行，因此论文不能声称 risk-triggered audit 在线上具有成本效益。

这正是现在距离“实验闭环完成”差的最后一段：

[
\text{在线 discovery}
\rightarrow
\text{certificate 触发 audit}
\rightarrow
\text{audit agent 实际运行}
\rightarrow
\text{恢复 TP}
\rightarrow
\text{计算 Recall-Cost 权衡}
]

当前只跑到了前两步。

---

# 三、下一轮必须优先完成的 P0 实验

## 1. 真正跑完 Requests TLS 在线闭环

你已经准备了 manifest，不需要重新设计实验。直接执行：

```text
Requests TLS:
seed04–seed08
```

每个 seed 跑四类 discovery：

```text
homogeneous
prompt-diverse
source-partitioned
independent-context
```

每种 discovery 配置之后，跑七种 audit policy：

```text
no audit
random holdout
singleton audit
boundary-focused holdout
source-partitioned review
always-holdout
risk-triggered audit
```

注意：`risk-triggered audit` 的判断规则必须在运行前冻结，不能看到结果后再改阈值。

---

## 2. 在线实验必须记录完整成本

当前 seed04 只报告了总 token 数。正式结果至少还需要：

```text
input_tokens
output_tokens
tool_calls
wall_clock
audit_trigger_reason
audit_queue_size
recovered_tp
introduced_fp
unnecessary_audit
```

否则只能证明“审查可能有用”，不能证明“审查值得用”。

---

## 3. 生成一张真正的主结果表

现在主文中缺少最关键的在线结果表。建议增加：

| Audit Policy              | Pre-R | Post-R | Precision | Recovered TP | Introduced FP | Tokens | Tool Calls | Wall-clock | Cost / TP |
| ------------------------- | ----: | -----: | --------: | -----------: | ------------: | -----: | ---------: | ---------: | --------: |
| No audit                  |       |        |           |              |               |        |            |            |           |
| Random holdout            |       |        |           |              |               |        |            |            |           |
| Always-holdout            |       |        |           |              |               |        |            |            |           |
| Singleton audit           |       |        |           |              |               |        |            |            |           |
| Source-partitioned review |       |        |           |              |               |        |            |            |           |
| Risk-triggered audit      |       |        |           |              |               |        |            |            |           |

论文真正需要证明的是：

[
\text{Recall}*{\text{risk-triggered}}
\approx
\text{Recall}*{\text{always-holdout}}
]

同时：

[
\text{Cost}*{\text{risk-triggered}}
<
\text{Cost}*{\text{always-holdout}}
]

只要这一点在多个 seeds 上成立，audit-controller 路线就基本站住了。

---

## 4. 将 Figure 3 替换为 Recall-Cost Pareto Curve

当前 Figure 3 只有 Requests seed04 的探索性散点：

* homogeneous；
* prompt-diverse；
* source-partitioned；
* consensus 与 union recall；
* token cost。

它可以保留到 appendix，但不适合做最终主图。

正式主文更需要：

### 横轴

[
\text{Token Cost 或 Wall-clock}
]

### 纵轴

[
\text{Post-audit Recall}
]

### 曲线或点

```text
No audit
Random holdout
Always-holdout
Source-partitioned review
Risk-triggered audit
```

用跨 seeds 均值和误差条表示。

---

# 四、完成 P0 后，还需要补哪些论文级实验？

## P1：扩展真实仓库

目前只有 Click 与 Requests 两个真实仓库。对于现象论文勉强够用，对于方法论文仍偏少。

最低建议：

| 项目          |   最低要求 |
| ----------- | -----: |
| 新增仓库        |    2 个 |
| 总真实仓库       | 至少 4 个 |
| 每个新增仓库任务    |  1–2 类 |
| 每个任务 seeds  |   至少 5 |
| 固定 commit   |     必须 |
| oracle 二次复核 |     必须 |
| 完整成本日志      |     必须 |

新增任务不要都变成简单 grep。需要包含：

* 间接引用；
* 配置路径；
* 异常处理；
* 测试；
* 文档；
* 边界文件。

否则审稿人会问：为什么不用静态扫描器？

---

## P1：补充 oracle 独立复核

当前补充材料已经明确承认：

> 尚未进行 independent double annotation。

对于 closed-world Recall 论文，这仍然是一个硬缺口。

建议为真实仓库 oracle 增加：

| 字段                 | 内容           |
| ------------------ | ------------ |
| Initial candidates | 初始候选数        |
| Reviewer 1 kept    | 第一轮保留数       |
| Reviewer 2 added   | 第二轮新增数       |
| Reviewer 2 removed | 第二轮删除数       |
| Ambiguous cases    | 争议项数量        |
| Resolution rule    | 处理规则         |
| Final oracle size  | 最终 oracle 数量 |
| Agreement rate     | 一致率          |

完整过程放 supplementary，主文一句话概括即可。

---

## P1：增加第二模型子集复现

当前在线实验只使用 `gpt-5.3-codex`。

不必全部实验重跑，但至少在一个仓库、部分 seeds 上加入另一个模型或能力档位，验证趋势不是单模型偶然现象。

最低要求：

```text
Requests TLS
2–3 seeds
homogeneous + source-partitioned
risk-triggered + always-holdout
第二模型
```

---

## P2：公开 benchmark 最小子集

SeekerGym 仍然只有 scaffold，没有真实结果。

正式投稿前最好至少跑一个最小子集。目的不是刷榜，而是证明方法不只适用于自建 repository audit。

最低比较：

```text
single agent
consensus
raw union
Chao-only
risk-triggered audit
```

最低指标：

```text
completeness
FCR
Safe Coverage
tokens
```

如果 SeekerGym schema 难以适配，再换 TRQA 或 WideSearch 子集。

---

# 五、论文正文还需要修改什么？

## 1. 最终摘要必须重写

当前摘要仍然像内部进度汇报，包含：

* v1 safe coverage 低；
* v2 offline diagnostic；
* repository holdout 不迁移；
* 一个 online blind seed；
* public benchmark 尚未运行。

这些内容现在诚实且合理，但不适合最终投稿。

在线闭环跑完后，摘要应只保留：

1. false convergence 问题；
2. 两类机制；
3. evidence-preserving audit controller；
4. 多仓库在线实验；
5. Recall-Cost 权衡；
6. 外部 benchmark 结果或明确边界。

v1 / v2 的内部迭代过程移到正文或 appendix。

---

## 2. 方法章节建议降低 certificate 的层级

当前 Section 4 是：

```text
Coverage-Risk Completion Certificate
```

但跨仓库 certificate 尚未成立。最终更稳妥的写法是：

```text
4 Evidence-Preserving Audit Controller
4.1 Evidence Ledger
4.2 Lightweight Risk Triage
4.3 Targeted Audit Policies
4.4 Post-Audit Update
```

其中 certificate 作为 `Lightweight Risk Triage`，不再被包装成一个已经具备通用安全保证的方法。

---

## 3. 主文中弱化 v2 细节

当前 Section 6.6 已经压缩到一小段，这是对的。

最终版本可以继续保留：

> 同分布估计器看起来很强，但跨仓库失败，因此没有升为主方法。

完整 feature audit、metadata-only probe 和全部表格留在 supplementary。

这反而会让论文更可信。

---

## 4. Conclusion 可以再多一句方法结论

现在 Conclusion 已经比上一版好：

> Consensus is not completion. We identified aggregation loss and common blind spots ... The current evidence supports an evidence-preserving audit-controller direction ...



在线结果跑出来以后，再补一句真正的方法结论：

> Risk-triggered audits recover a substantial fraction of missing evidence while reducing unnecessary review relative to always-on holdout.

当然，只有数据支持后才能加入。

---

# 六、补充材料还需要修改什么？

## 1. Section 11 最终不能保留为 gap report

现在 Section 11 的作用是诚实记录：

> harness 已搭好，但 post-audit agents 尚未运行。

内部版本可以保留。正式投稿时必须替换成：

```text
11 Online Audit-Controller Evaluation
```

内容包括：

* 运行设置；
* per-seed 结果；
* 均值与标准差；
* 成本统计；
* 失败案例；
* Pareto 曲线；
* trigger 分布。

---

## 2. 补充 prompts 与环境配置

建议新增：

```text
Discovery prompts
Prompt-diverse variants
Source-partitioned instructions
Independent-context setup
Singleton audit prompt
Boundary-focused holdout prompt
Verifier prompt
Model version
Temperature
Budget
Tool access
Execution date
```

---

## 3. Calibration curve 可以保留，但不是重点

Supplementary 第 7 页的 v1 calibration curve 可以留在 appendix。

但正式版本更值得增加：

* source coverage heatmap；
* marginal discovery gain curve；
* audit trigger frequency；
* Recall-Cost Pareto curve。

---

# 七、现在实验完成度如何？

| 模块                          | 当前状态                                  | 判断       |
| --------------------------- | ------------------------------------- | -------- |
| False convergence 现象        | 合成 + Click + Requests                 | **完成**   |
| 两类机制                        | aggregation loss + common blind spot  | **完成**   |
| stopping baselines          | self-report、confidence、overlap、Chao 等 | **基本完成** |
| v1 certificate              | 安全但过度保守                               | **完成基线** |
| v2 可信性审计                    | 已发现不迁移                                | **完成诊断** |
| Evidence ledger             | 流程与图已完成                               | **完成原型** |
| 在线 audit-controller harness | manifest 已搭好                          | **设计完成** |
| 在线 post-audit agents        | 尚未执行                                  | **未完成**  |
| 在线 Recall-Cost 主结果          | 尚未生成                                  | **未完成**  |
| 多仓库在线验证                     | 仍只有两个仓库                               | **未完成**  |
| oracle 独立复核                 | 尚未完成                                  | **未完成**  |
| 第二模型验证                      | 尚未完成                                  | **未完成**  |
| 公开 benchmark                | 尚未运行                                  | **未完成**  |

---

# 八、接下来最合理的执行顺序

## 第一批：必须马上做

```text
[ ] 执行 Requests TLS seed04–seed08
[ ] 跑四种 discovery 配置
[ ] 跑七种 online audit policy
[ ] 补齐 token / tool-call / wall-clock
[ ] 生成在线主表
[ ] 生成 Recall-Cost Pareto Curve
```

## 第二批：提高论文级可信度

```text
[ ] 新增两个真实仓库
[ ] 每个仓库 1–2 个任务
[ ] 每个任务至少 5 seeds
[ ] oracle 独立二次复核
[ ] 第二模型子集复现
```

## 第三批：外部验证和写作收束

```text
[ ] 跑 SeekerGym 最小子集
[ ] 将 Figure 3 替换为 Pareto Curve
[ ] 重写摘要
[ ] 将方法章节调整为 audit-controller 主线
[ ] 将 Section 11 gap report 替换为正式结果
```

---

## 最终判断

**现在还不能说实验部分已经完善好。**

但你已经不再处于“实验方向是否正确”的阶段，而是进入了一个非常明确的收尾阶段：

> **把已经搭好的 online audit-controller harness 真正跑完，并验证 risk-triggered audit 是否以低于 always-holdout 的成本恢复更多遗漏证据。**

这一步一旦跑稳，论文就会从“很诚实、很有价值的现象诊断稿”升级为“具备方法贡献的完整投稿稿”。
