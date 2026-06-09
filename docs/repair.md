## 结论

**方向是对的，而且比继续在 GraphRefactor 上叠加模块更值得优先推进。**

但要把判断说得更准确一些：

> 这份稿件已经完成了一个不错的 **phenomenon pilot**：它证明了“多 Agent 看起来达成一致，并不意味着集合发现任务已经完成”。
> 现在还不能把它当作可直接投稿的完整论文。下一步不是继续扩写文字，而是把现象做实，把启发式协议升级为一个可校准的“完成性证书”。

你这次转向是符合师姐建议的。GraphRefactor 更像“如何优化工作流结构”；当前方向追问的是一个更基础的问题：

> **工作流凭什么认为自己已经完成任务？**

这个问题更容易形成一条清楚的科学主线，也更有机会做出理论和实验都比较扎实的论文。

---

# 一、为什么这个方向值得继续？

## 1. 它不是为了造方法而造方法

当前稿件的核心现象非常清楚：

* 多个 Agent 自报完成；
* 输出之间高度重叠；
* 聚合结果看起来干净、可信；
* 但真实集合中仍有遗漏项。

你进一步将问题拆成了两种机制：

| 机制                    | 含义                              |
| --------------------- | ------------------------------- |
| **Aggregation loss**  | 少数 Agent 已经找到真实条目，但共识或摘要阶段把它丢掉了 |
| **Common blind spot** | 所有 Agent 都没有找到某些条目，因此即使取并集也无法恢复 |

这个拆分是成立的，而且比单纯说“多数投票不可靠”更好。因为它区分了**搜索阶段遗漏**和**汇总阶段丢失**，两类问题需要不同的解决方案。当前协议也抓住了这一点：singleton 不应直接删除，也不应直接纳入最终答案，而应进入审查队列；高一致性反而可能触发额外的边界检查。

## 2. 它对应了近期基准真正暴露出的难点

这个问题不是人为构造出来的。

**WideSearch** 专门评估 Agent 是否能够完整收集大规模、可逐条验证的信息。论文报告，多数现有 Agent 系统的整体成功率接近 0%，最佳系统也只有约 5%。这说明“找出全部条目”远比“给出一个看似正确的答案”困难。([arXiv][1])

**DeepSearchQA** 更直接地将停止条件列为关键能力：Agent 必须在没有显式终止信号的情况下，区分“暂时没有找到更多内容”和“确实没有更多内容”。论文也观察到了提前停止导致的 under-retrieval。([arXiv][2])

**Total Recall QA** 则开始系统构造可验证的 total-recall 查询，用于评估深度研究 Agent 是否真正覆盖了全部相关文档。([arXiv][3])

因此，你的切口是有价值的：

> 现有工作已经证明“完整检索很难”，但仍缺少一个可靠的机制，判断多 Agent 工作流何时可以停止、何时只是虚假收敛。

---

# 二、当前稿件已经做对了哪些事情？

这份 `main.pdf` 作为第一轮验证稿，完成度其实不错。

## 1. 标题和问题意识是成立的

> **Consensus Is Not Completion: False Convergence in Multi-Agent Discovery Workflows**

这个标题抓得很准。它没有泛泛讨论多智能体协作，而是直接指出一个容易被忽略的系统假设：**一致性不是完成性的充分条件。**

## 2. 两类失败机制具有解释力

表 1 和表 2 已经展示了三个比较典型的现象：

* `T1 seed01`：共识只保留 22 个条目，原始并集恢复到 35 个，属于 aggregation loss；
* `T2 seed02/03`：三个 Agent 完全一致，但都漏掉同样的 2 个边界项，原始并集也无法解决，属于 common blind spot；
* `T1 seed02/03`：原始并集虽然不漏条目，却引入 4 个和 5 个假阳性，说明 union 也不能直接当作最终策略。

这几组结果共同支持了一个比较好的论点：

> **Consensus 太保守，union 太激进；可靠系统需要显式处理覆盖风险和不确定证据。**

## 3. 你没有过度包装当前结果

稿件的 Limitations 写得比较诚实：需要真实仓库、更多 seeds、标准化 holdout、成本敏感评估、消融实验和更丰富的相关性指标。这个判断是准确的。

---

# 三、为什么这份稿件还不能直接作为正式投稿？

方向没有问题，但当前证据只能支撑：

> **这种失败机制确实存在。**

还不能支撑：

> **我们已经提出了一套普遍有效的完成性判断方法。**

## 1. 当前样本量太小

现在只有：

* 两类任务；
* 六个 case slices；
* 每个 seed 三个主 Agent；
* 可选的一个 holdout scout；
* 一个合成代码仓库；
* 一个自然化但仍偏构造的文档搜索任务。

更关键的是，按照稿件自己预注册的严格判定标准，表 1 中只有 `T1 hard seed01` 被标记为 strict positive。`T2 seed02/03` 虽然展示了非常有价值的共同盲区，但由于 holdout gain 为 (2/30)，低于设定阈值，因此仍不满足严格正例条件。

这不意味着结果无效，但意味着现阶段应该称为：

> **机制级证据和概念验证。**

不要急着写成已经得到普遍结论。

## 2. 当前协议仍然比较像人工规则

现在的 Evidence-Preserving Completion Protocol 很合理，但审稿人可能会说：

> 发现 singleton 就人工复核；高度一致时再派一个 Agent 查边界项。这是一个实用 checklist，但学术创新在哪里？

尤其是这条触发条件：

> `if confidence and overlap are high and the task has boundary-resolution risk`

“任务具有边界解析风险”目前需要人工判断。如果只在已知会漏项的场景中手工触发 holdout，容易被质疑为针对数据集定制。

正式论文需要把它升级为：

* 可计算的风险分数；
* 可校准的停止条件；
* 固定预算下的审查策略；
* 能够在新任务中自动决定是否继续搜索。

## 3. 相关工作必须补齐 2025—2026 年的邻近研究

当前稿件主要引用了 self-consistency、debate、reflection 和 long-context 等较早工作。

但近期已经出现几项与你非常接近的研究：

* **AgentAuditor** 指出多 Agent 会出现 correlated errors 和 confabulation consensus，并主张保留推理分歧，在关键分叉处审查，而不是简单多数投票。([arXiv][4])
* **When Agents Disagree** 提出 selection bottleneck：生成器多样性是否有用，取决于聚合器是否能够正确选择。([arXiv][5])
* **MATU** 从完整交互轨迹出发，对多 Agent 系统的不确定性进行建模。([arXiv][6])
* **WideSeek** 已经研究面向 Wide Research 的动态层级多 Agent 架构和端到端强化学习。([arXiv][7])

因此，你不能把主要创新写成：

> 多数投票会出错，所以我们保留少数意见并增加审查 Agent。

这个表述已经太接近现有邻域。

---

# 四、论文真正应该聚焦在哪里？

## 不建议把主线写成

> 我们提出一种 Evidence-Preserving Completion Protocol，通过保留 singleton 并增加 holdout scout，提升发现任务的召回率。

这更像工程方案。

## 更建议把主线写成

> **在具有相关探索偏差的多 Agent 集合发现任务中，如何估计残余覆盖风险，并生成可信的完成性证书？**

也就是从“设计一个协议”，升级为：

> **完成性风险估计问题。**

可以将目标形式化为：

[
\Pr\left(
\operatorname{Recall}(F_t)\geq 1-\varepsilon
\mid
\mathcal{L}_t
\right)
\geq
1-\delta
]

其中：

* (F_t)：当前最终结果集合；
* (\mathcal{L}_t)：截至第 (t) 轮的发现日志，包括每个 Agent 找到的条目、来源、查询路径、重复次数和置信度；
* (\varepsilon)：允许的遗漏比例；
* (\delta)：风险容忍度。

系统输出的不再只是：

> 已完成。

而是：

> 在当前探索记录和审查预算下，以至少 (1-\delta) 的置信度，剩余遗漏比例不超过 (\varepsilon)。

这个版本会明显更有研究味道。

---

# 五、理论工具也应该换方向

你之前想过从几何学角度做 GraphRefactor。对于当前问题，**不要为了保留几何学而硬套几何学。**

这个方向最自然的理论工具是：

* Missing mass estimation；
* Capture–recapture；
* Good–Turing estimator；
* Chao estimator；
* 相关采样下的有效样本量；
* 序贯检验；
* Calibration；
* 风险受限停止策略。

例如，Technology-Assisted Review 领域已经使用 Chao 的总体规模估计器判断文档筛查何时可以停止。([arXiv][8])

但不能直接套用经典方法，因为 LLM Agent 并不是独立同分布采样器：

* 多个 Agent 可能使用相同模型；
* 查询表达高度相似；
* 优先访问相同来源；
* 继承相同上下文；
* 共享相同的推理盲区。

这恰恰可能成为你的理论切口：

> **经典 coverage estimator 在相关 Agent 探索下为什么失效？如何构造 correlation-aware completion certificate？**

可以将每个 Agent 对每个条目的发现情况写成矩阵：

[
Z_{ij}
======

\mathbf{1}
[
\text{Agent } i \text{ discovers item } j
]
]

然后研究：

* singleton 数量；
* doubleton 数量；
* Agent 之间的发现重叠；
* 来源覆盖率；
* 查询路径相似度；
* Agent 异质性；
* 剩余遗漏数量；
* 真实 Recall。

初始阶段不必急着证明一个很复杂的定理。先比较：

1. 简单连续无新增停止；
2. overlap 阈值；
3. confidence 阈值；
4. Good–Turing；
5. Chao estimator；
6. 相关性感知修正版；
7. 学习式 calibration 模型。

只要你能证明：

> 相同 Agent 数量下，相关性越强，传统停止信号越容易高估完成性；而 correlation-aware estimator 能更准确识别 false stop。

论文的核心就立住了。

---

# 六、你与邻近工作的区别必须写得非常清楚

后续论文中，建议明确强调下面的区分。

| 邻近方向                 | 主要问题                    | 你的问题                           |
| -------------------- | ----------------------- | ------------------------------ |
| 多数投票、自一致性            | 哪个答案更可能正确？              | 是否还有真实条目没有被找到？                 |
| AgentAuditor         | 多 Agent 对单个问题达成错误共识怎么办？ | 集合发现任务中，如何判断覆盖是否足够完整？          |
| Selection Bottleneck | 多样化输出如何正确聚合？            | 如何估计未观察到的 missing mass？        |
| WideSeek             | 如何扩展多 Agent 并行搜索能力？     | 工作流什么时候应该停止扩展？                 |
| MATU                 | 多 Agent 推理轨迹的不确定性如何量化？  | 如何将覆盖不确定性转化为可执行的停止证书？          |
| TAR stopping         | 文档筛查何时停止？               | 如何适配具有复杂相关性和动态搜索策略的 LLM Agent？ |

真正有辨识度的一句话是：

> **现有工作主要优化“如何找到更多内容”或“如何聚合已有答案”；本文研究“在相关探索条件下，如何判断尚未找到的内容是否仍然足以影响完成性”。**

---

# 七、下一轮实验应该怎么做？

现在不要急着继续写论文正文。先把当前版本冻结为 `v0.1 mechanism pilot`，然后完成一轮更严格的验证。

## 1. 扩充任务

至少加入三类：

| 任务类型    | 推荐设置                                   | 价值                  |
| ------- | -------------------------------------- | ------------------- |
| 代码仓库审查  | 一个真实开源仓库 + AST 或静态扫描 oracle            | 最贴近 Claude Code 工作流 |
| 固定文档库搜索 | 固定快照、人工复核 oracle                       | 验证文档领域可迁移性          |
| 宽搜索基准子集 | WideSearch、TRQA 或 DeepSearchQA 中可控制的子集 | 与近期公开基准接轨           |

## 2. 增加探索配置

不要只跑 G3。至少比较：

* 单 Agent；
* 同质 G3；
* 同质 G5；
* Prompt 多样化 G3；
* 模型异构 G3；
* 来源分区 G3；
* 固定预算 holdout；
* 风险触发 holdout。

## 3. 记录完整 incidence 日志

每个条目必须记录：

```text
task_id
round_id
agent_id
item_id
source_id
query_path
first_seen_round
support_count
is_singleton
confidence
aggregation_status
audit_status
oracle_label
```

这样后续才能真正建模相关性，而不是只看一个输出 Jaccard。

## 4. 增加强基线

至少加入：

* Majority consensus；
* Standard summary；
* Raw union；
* No-new-item stopping；
* Confidence stopping；
* Always-holdout；
* Random holdout；
* Good–Turing；
* Chao estimator；
* 你的 correlation-aware certificate。

## 5. 重点画四张图

1. **Agent 自报完成度 vs. 真实 Recall**
2. **输出重叠率 vs. 剩余遗漏数量**
3. **名义 Agent 数量 vs. 有效独立探索规模**
4. **额外审查成本 vs. 召回率提升**

---

# 八、什么结果出现后，可以确认这是一篇值得写的论文？

我会设四个 Go / No-Go 门槛。

| 门槛     | 值得继续的结果                                         |
| ------ | ----------------------------------------------- |
| 现象稳定性  | 在真实仓库和文档任务中，false stop 不是偶发个例                   |
| 相关性价值  | 同质 Agent 数量增加时，重复率上升明显，但 Recall 收益快速饱和          |
| 风险估计能力 | 你的 estimator 比 overlap、confidence、无新增轮数更准确地预测遗漏 |
| 成本收益   | 相比 always-holdout，风险触发审查以更低开销恢复相近 Recall        |

只要前 3 项成立，这个方向就值得作为主线推进。

如果最后只能证明：

> singleton 应该人工复核。

那它适合写成经验分析或 workshop 论文，但不足以承担一篇强投稿。

---

# 九、GraphRefactor 不需要丢掉

GraphRefactor 已经完成的 QA、Math、Code 验证没有浪费。

更合适的处理方式是：

* 暂停将它继续扩写为主论文；
* 保留现有执行器、日志和成本统计；
* 将它作为动态工作流实验平台；
* 后续让 Completion Controller 决定何时插入 Scout、Verifier 或新的搜索分支。

两条路线的关系可以写成：

| GraphRefactor | AgentCompletion   |
| ------------- | ----------------- |
| 如何修改工作流结构？    | 什么时候必须继续修改或扩展工作流？ |
| 优化质量、成本和时延    | 控制遗漏风险和停止决策       |
| 结构适配器         | 完成性控制器            |

AgentCompletion 更适合作为当前论文主线；GraphRefactor 可以成为后续整合模块。

---

## 最终判断

**这条路可以继续，而且值得认真做。**

但不要把当前 PDF 当成已经定型的方法论文。它目前最有价值的地方，是准确抓住了一个真实、可验证、具有理论延展空间的现象：

> **Consensus is not completion.**

下一步最重要的不是再加一个 Agent，也不是继续润色摘要，而是将这个现象升级为：

> **correlation-aware coverage-risk estimation and completion certificates for multi-agent discovery workflows。**

做到这一步，这个方向会比原本的 GraphRefactor 更锋利，也更符合师姐希望你走的研究路线。

[1]: https://arxiv.org/abs/2508.07999?utm_source=chatgpt.com "WideSearch: Benchmarking Agentic Broad Info-Seeking"
[2]: https://arxiv.org/html/2601.20975v1?utm_source=chatgpt.com "DeepSearchQA: Bridging the Comprehensiveness Gap for ..."
[3]: https://arxiv.org/abs/2603.18516?utm_source=chatgpt.com "Total Recall QA: A Verifiable Evaluation Suite for Deep Research Agents"
[4]: https://arxiv.org/abs/2602.09341?utm_source=chatgpt.com "Auditing Multi-Agent LLM Reasoning Trees Outperforms Majority Vote and LLM-as-Judge"
[5]: https://arxiv.org/abs/2603.20324?utm_source=chatgpt.com "When Agents Disagree: The Selection Bottleneck in Multi-Agent LLM Pipelines"
[6]: https://arxiv.org/abs/2604.08708?utm_source=chatgpt.com "Every Response Counts: Quantifying Uncertainty of LLM-based Multi-Agent Systems through Tensor Decomposition"
[7]: https://arxiv.org/abs/2602.02636?utm_source=chatgpt.com "WideSeek: Advancing Wide Research via Multi-Agent Scaling"
[8]: https://arxiv.org/abs/2404.01176?utm_source=chatgpt.com "Using Chao's Estimator as a Stopping Criterion for Technology-Assisted Review"
