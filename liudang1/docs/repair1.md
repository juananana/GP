## 结论

**P0 在线实验闭环已经完成，但实验部分还没有达到“可以放心投稿 AAAI 主会”的程度。**

现在你们已经不再只是做离线 stress test。Requests TLS 上的在线审查实验已经真实跑完：

* 5 个 seeds；
* 4 种 discovery 配置；
* 60 次 blind discovery calls；
* 45 次 audit calls；
* 审查阶段总计约 `687k` tokens；
* wall-clock 累计 `837.1s`；
* 审查前后 Recall、Precision、恢复 TP、引入 FP 和额外 token 成本都已记录。

主文第 7 页的 Table 6 与 Figure 3 已经构成一组真正的在线 Recall–Cost 结果。 补充材料第 5–6 页也记录了完整 online suite 和 discovery grid。

但这轮实验揭示出的结论是：

> **审查确实能够恢复遗漏证据，但当前控制器还不能证明任务完成，也不能证明 risk-triggered audit 优于更简单的固定策略。**

--
# 二、当前实验最关键的问题

## 1. Risk-triggered audit 被更简单的方法支配了

这是当前最重要的问题。

比较：

| 策略                        | Recall | Precision | Tokens |
| ------------------------- | -----: | --------: | -----: |
| Source-partitioned review | `.733` |    `.730` |  `55k` |
| Risk-triggered audit      | `.733` |    `.713` |  `83k` |

两者 Recall 相同，但 source-partitioned review：

* 成本更低；
* Precision 更高；
* 引入 FP 更少。

所以当前结果不能支持：

> risk-triggered audit 是最优控制器。

更准确的结论是：

> evidence-preserving audit 有效，但现有 risk-triggered policy 仍然存在过度触发或动作组合不合理的问题。

---

## 2. Singleton audit 才是当前最强的成本收益策略

计算每恢复一个 TP 的额外 token 成本：

| 策略                        | Tokens / Recovered TP |
| ------------------------- | --------------------: |
| Singleton audit           |             约 `0.17k` |
| Source-partitioned review |             约 `0.75k` |
| Random holdout            |             约 `0.90k` |
| Risk-triggered audit      |             约 `1.13k` |
| Boundary holdout          |             约 `1.15k` |
| Always holdout            |             约 `2.05k` |

Singleton audit 只花约 `12k` tokens，就将 Recall 从 `.491` 提升到 `.719`。这说明：

> 当前最合理的下一版方法不是继续叠加复杂 risk score，而是设计一个**分级 escalation controller**。

---

## 3. 在线实验仍然只覆盖一个真实仓库任务族

虽然 Click 和 Requests 都用于验证现象，但真正的 online audit-controller 主实验目前只有 Requests TLS。补充材料也明确承认，这不是 benchmark sweep。

所以当前结果还不能证明：

> controller 能够跨仓库稳定工作。

---

## 4. 线上没有真正评估 SAFE-TO-STOP 状态

Requests TLS 的所有策略都低于 `.95` threshold。换句话说，线上实验只验证了：

> 系统确实应该拒绝停止。

但还没有验证：

> 当任务真正达到完成阈值时，系统能否允许停止。

这会导致审稿人追问：

> 这个 controller 是否只是始终保持保守？

---

# 三、下一步方法应该怎么改？

## 将当前方法收束为分级审查控制器

当前实验天然支持以下 staged controller：

[
\text{Evidence Ledger}
\rightarrow
\text{Singleton Audit}
\rightarrow
\text{Source-Partitioned Review}
\rightarrow
\text{Boundary Holdout}
\rightarrow
\text{Continue Search or Abstain}
]

## 推荐规则

### Stage 0：保留少数证据

不要在 aggregation 阶段静默删除 singleton。

### Stage 1：优先执行 singleton audit

因为它是当前成本收益最好的策略。

### Stage 2：仍存在 source-coverage gap 时，升级到 source-partitioned review

用于处理当前 Agent 没有共同覆盖到的区域。

### Stage 3：存在明显 boundary-risk 时，再触发 boundary-focused holdout

不要默认调用昂贵 holdout。

### Stage 4：仍达不到阈值时继续搜索或保持 abstention

不要强行 certify completion。

这个 staged controller 比当前 risk-triggered policy 更容易解释，也更符合现有结果。

---

# 四、下一轮必须补的实验

## P0：冻结 staged controller，在 held-out 仓库测试

不要在 Requests 上重新设计方法后，又在 Requests 上报告主结果。

更合理的方式是：

* Requests TLS：development set；
* Click deprecation audit：held-out online test；
* 新增一个仓库：第二 held-out test。

### Click 最低实验配置

```text
3–5 seeds
homogeneous
source-partitioned
independent-context
singleton audit
source-partitioned review
staged controller
always-holdout
```

关键是：

> 在执行 Click 实验之前，冻结 staged controller 的升级条件。

---

## P0：增加线上 safe states

通过控制：

* 搜索预算；
* Agent 数量；
* 审查轮数；
* 任务难度；
* holdout 强度；

构造一部分 Recall ≥ `.95` 的真实线上状态。

然后报告：

| 指标                       | 作用               |
| ------------------------ | ---------------- |
| False Certification Rate | 不完整却被认证完成的比例     |
| Safe Coverage            | 真正完成状态中，被允许停止的比例 |
| Abstention Rate          | 仍然拒绝停止的比例        |
| Risk–Coverage Curve      | 风险控制与自动停止覆盖率     |

否则 certificate 线上部分仍然无法真正评价。

---

## P1：增加统计检验

Figure 3 已有 mean 和 standard deviation error bars，但建议补充：

* 以 seed 为 cluster 的 bootstrap 95% CI；
* paired permutation test 或 Wilcoxon signed-rank test；
* staged controller 相对 singleton、source-partitioned 和 always-holdout 的配对差异；
* 每个 seed / configuration 的详细结果放 supplementary。

不要把 20 个 seed/configuration states 当作完全独立样本；更稳妥的是按 seed 分组 bootstrap。

---

## P1：补充总成本，而不只报告 audit cost

当前 Table 6 的 token 数只统计额外 audit tokens。

建议同时报告：

| 成本                | 说明           |
| ----------------- | ------------ |
| Discovery tokens  | 初始探索成本       |
| Audit tokens      | 增量审查成本       |
| End-to-end tokens | 总成本          |
| Tool calls        | 工具调用次数       |
| Wall-clock        | 实际运行时间       |
| Cost / TP         | 每恢复一个 TP 的成本 |

因为 source-partitioned discovery 本身成本较低，这可能进一步改变整体 Pareto frontier。

---

## P1：补充 Precision 维度

当前 Recall 提升伴随 Precision 下降。

建议增加：

* F1；
* verified-only Precision；
* verifier acceptance rate；
* Recall@fixed Precision；
* introduced FP；
* cost per accepted TP；
* cost per net TP，即 `TP - λ FP`。

否则审稿人可能认为 Recall 提升只是因为接受了更多噪声。

---

## P1：完成 Oracle 独立二次复核

补充材料仍然明确写出：

> 当前没有 independent double annotation。

对于 closed-world Recall 任务，这是正式投稿前必须补的。

至少为 Click 和 Requests 增加：

```text
initial_candidates
reviewer_1_kept
reviewer_2_added
reviewer_2_removed
ambiguous_cases
resolution_rule
agreement_rate
final_oracle_size
```

---

## P2：增加第二模型子集

当前 online suite 使用单一模型。

最低补充：

```text
Requests TLS
2–3 seeds
homogeneous + source-partitioned
singleton audit + staged controller + always-holdout
第二个模型
```

无需全量重跑，但要验证主要趋势不依赖单一模型。

---

## P2：公开 benchmark 最小验证

SeekerGym 仍未运行。

正式投稿前最好至少跑一个小子集。最低比较：

```text
single agent
consensus
raw union
singleton audit
staged controller
```

报告：

```text
completeness
FCR
Safe Coverage
tokens
```

如果 SeekerGym 适配太慢，再切换到 TRQA 或 WideSearch 子集。

---

# 五、主文现在还需要修改什么？

## 1. 方法章节应该降低 certificate 的层级

当前 Section 4 仍然叫：

> `Coverage-Risk Completion Certificate`



但证据已经更支持 audit-controller 路线。

建议最终改成：

```text
4 Evidence-Preserving Staged Audit Controller
4.1 Evidence Ledger
4.2 Lightweight Risk Triage
4.3 Singleton Verification
4.4 Source-Partitioned Escalation
4.5 Boundary-Focused Holdout and Abstention
```

certificate 保留为 controller 的风险分流模块，而不是论文唯一主方法。

---

## 2. Table 6 要解释 Pre R 与 Union Recall 的区别

当前 Table 6 的 `Pre R = .491`，但补充材料 Table 5 中 union recall 大约是 `.724–.732`。

读者很容易困惑。

必须明确说明：

* `Pre R` 是否指 conservative consensus final set；
* union candidate pool 是否仅作为 evidence queue；
* 为什么 audit 从 `.491` 开始，而不是 `.72x`；
* verifier 是否只将审查通过的候选加入最终答案。

建议直接在 Table 6 caption 中加一句解释。

---

## 3. Figure 3 可以强化 Pareto 结论

当前 Figure 3 已经合格，但可以再优化：

* 标出 Pareto frontier；
* 将 dominated 策略淡化；
* 突出 `Singleton → Source-partitioned → Always holdout`；
* risk-triggered 暂时作为 baseline，不要作为视觉中心；
* 增加 end-to-end cost 版本放 supplementary。

---

## 4. Abstract 还需要最终重写

当前摘要仍然包含：

* v1；
* v2；
* 不迁移；
* public benchmark 未运行。



内部版本这样写很诚实，但最终投稿摘要不应像实验进度报告。

等 staged controller 与 held-out test 做完后，摘要只保留：

1. 问题；
2. 两类机制；
3. staged audit controller；
4. 多仓库在线结果；
5. Recall–Cost 权衡；
6. abstention 边界。

---

## 5. 补充材料中的长路径排版要修

补充材料中路径造成 overfull warning。建议：

* 使用 `\path{...}`；
* 或 `\url{...}`；
* 或定义简短根目录别名，例如 `\expdir`；
* 路径只保留相对目录；
* 允许换行。

这不是内容问题，但正式提交前应清掉。

---

# 六、当前完成度判断

| 模块                              | 当前状态                                 | 判断       |
| ------------------------------- | ------------------------------------ | -------- |
| False convergence 现象            | 合成 + Click + Requests                | **完成**   |
| 两类机制                            | aggregation loss + common blind spot | **完成**   |
| Stopping baselines              | 已完成                                  | **基本完成** |
| v1 certificate                  | 安全但保守                                | **完成基线** |
| v2 transferability audit        | 已完成，结果不迁移                            | **完成诊断** |
| Requests 在线闭环                   | 5 seeds × 4 configs                  | **完成**   |
| 在线审查真实成本                        | 已记录                                  | **完成**   |
| 当前 risk-triggered policy        | 被简单策略支配                              | **需要重构** |
| Staged controller               | 尚未实现                                 | **未完成**  |
| Held-out online repository test | 尚未完成                                 | **未完成**  |
| 线上 SAFE 状态评价                    | 尚未完成                                 | **未完成**  |
| Oracle 二次复核                     | 尚未完成                                 | **未完成**  |
| 第二模型验证                          | 尚未完成                                 | **未完成**  |
| Public benchmark                | 尚未完成                                 | **未完成**  |

---

# 七、下一轮最合理的优先级

## 第一优先级

```text
[ ] 将 Requests 作为 development set
[ ] 设计并冻结 staged controller
[ ] 在 Click 上运行 held-out online test
[ ] 增加 safe-state budget sweep
[ ] 报告 FCR / Safe Coverage / Abstention
```

## 第二优先级

```text
[ ] 增加 end-to-end cost
[ ] 增加 F1 / Recall@Precision / net TP
[ ] 加入 cluster bootstrap CI 和 paired test
[ ] 完成 Click 与 Requests oracle 二次复核
```

## 第三优先级

```text
[ ] 增加一个新仓库
[ ] 第二模型子集复现
[ ] 跑公开 benchmark 最小子集
[ ] 重写 Abstract 和 Section 4
```

---

## 最终判断

**P0 在线实验已经完善，但整篇论文的实验部分还没有最终完成。**

下一轮不要继续优化已经被支配的 risk-triggered policy，也不要继续堆离线 AUROC。最值得做的是：

> **将 singleton audit 与 source-partitioned review 组织成一个冻结的分级控制器，并在未参与设计的 held-out 仓库上验证其 Recall–Cost 优势和 abstention 可靠性。**

只要 held-out online test 能成立，这篇论文就会从“扎实的 false-convergence 分析稿”进一步升级为“具备明确方法贡献的 AAAI 投稿稿”。
