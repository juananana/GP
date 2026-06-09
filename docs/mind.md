## 结论

按师姐的建议，我会暂时**停止继续给 GraphRefactor 叠加模块**，把研究重心从“设计一个更强的动态工作流优化器”转向：([arXiv][1])项目名称：

> **AgentCompletion：面向动态智能体工作流的完成性判断与统计停止规则**

论文标题可以暂定为：

> **When Are We Done? Correlation-Aware Completion Certificates for Dynamic Agentic Workflows**

这个方向比继续做“静态 DAG → 动态 DAG”“局部编辑”“节点画像”“RL 搜索拓扑”更值得优先验证。你上传的对话里已经指出：GraphRefactor 当前形态工程逻辑合理，但如果目标是 AAAI、ICLR 级别投稿，还缺少一个不可替代的科学问题；师姐真正希望你学习的是 **phenomenon-first** 的研究方式，而不是先决定套用几何学。

---

# 一、为什么不建议继续沿着 GraphRefactor 硬卷？

GraphRefactor 原本的思路并没有问题：

> 以已有静态工作流为锚点，在有限编辑邻域内，根据任务上下文调整节点、边和执行路径。

但截至 **2026 年 6 月 7 日**，动态工作流优化已经明显拥挤。近期工作已经覆盖提示词与拓扑联合优化、工作流搜索、查询级工作流生成、执行期动态编排、预算控制和 Agent 自主设计工作流；2026 年 3 月还出现了专门面向 LLM Agent 工作流优化的综述。([arXiv][2])稿人很容易追问：

* 为什么一定要使用 bounded edit neighborhood，而不是直接搜索或生成工作流？
* 为什么使用 constrained offline RL，而不是 beam search、MCTS、启发式规则或在线路由？
* 节点画像到底揭示了什么新规律，还是仅仅帮助降低搜索空间？
* 局部拓扑修改是否只是另一种工程折中？

这些问题不是完全无法回答，但论文会逐渐变成“模块组合是否比另一组模块略好”，理论主线不够锋利。

GraphRefactor 不应删除。它可以保留为实验平台、对照方法和后续控制组件，但不必继续承担整篇新论文的核心创新。

---

# 二、Claude Code 动态工作流暴露了一个真正有价值的问题

Anthropic 官方文档已经将动态工作流描述为：由 Claude 编写脚本，批量编排多个子 Agent，用于代码库审查、大规模迁移和交叉核验式研究。官方博客在 2026 年 5 月 28 日和 6 月 2 日连续发布了动态工作流相关介绍。([Claude Code][3])何生成 JavaScript 工作流”，而是三类真实失败：

* **Agentic laziness**：任务没有完成，却提前宣布完成；
* **Self-preferential bias**：多个相似 Agent 相互印证，但实际上共享同一个盲区；
* **Goal drift**：长链路委派、摘要压缩和多轮循环后，原始目标逐渐丢失。

其中最适合作为第一篇新论文的，是第一类问题：

> 对于代码仓库覆盖检查、广泛资料搜集、文献检索、合规审查和开放式根因调查，Agent 如何知道自己已经“找完了”？

这个问题既真实，又没有被动态拓扑优化完全覆盖。

近期基准已经明确证明它不是伪问题：

* **WideSearch** 要求系统收集大量可逐条核验的原子信息。论文评测了十余种 Agent 系统，多数系统的整体成功率接近 0%，最佳系统也只有约 5%。([arXiv][4])QA** 专门评估穷尽式答案列表生成，将“什么时候停止搜索”列为关键能力，并观察到了提前停止造成的 under-retrieval。([arXiv][1])ll QA** 进一步提出 total-recall 查询：只有检索到全部相关文档，才能正确回答问题。([arXiv][5])arch in the Wild** 分析了 1444 万次真实搜索请求，发现部分搜索会话呈现明显的重复行为，并指出重复感知停止策略、意图自适应预算和跨步状态跟踪值得研究。([arXiv][6])析问题或优化搜索效率，但仍留下一个很好的切口：

> 多 Agent 结果高度一致、连续多轮没有新增结果，是否真的意味着搜索接近完成？
> 还是仅仅意味着多个同质 Agent 同时陷入了共同盲区？

---

# 三、建议研究的核心现象：动态工作流中的“虚假收敛”

可以暂时把现象命名为：

> **False Convergence in Dynamic Agentic Workflows**
> 动态智能体工作流中的虚假收敛

## 1. 初步定义

在集合发现、代码仓库扫描、广泛检索和长尾信息收集任务中，动态工作流可能出现：

1. 多个 Agent 给出的结果高度一致；
2. 连续若干轮没有发现新条目；
3. 主 Agent 判断任务已经完成；
4. 但与实验者掌握的 Ground Truth 比较后，真实 Recall 仍然明显不足；
5. 一个使用不同搜索入口、不同策略或不同提示词的独立 Scout，仍能发现大量遗漏项。

最值得研究的不是“Agent 会漏东西”——这已经比较常见——而是：

> **表面一致性为什么会系统性高估真实完成度？**

## 2. 论文要寻找的关键变量

师姐的论文思路值得模仿的地方，是寻找一个简单但有预测力的变量。你的目标也不是先造一个复杂框架，而是先找出：

> 什么因素决定动态工作流何时进入危险的“伪完成”状态？

值得优先记录的变量包括：

| 变量                         | 直观含义                             |
| -------------------------- | -------------------------------- |
| Pairwise overlap           | 不同 Agent 结果之间的重叠比例               |
| Marginal gain              | 新一轮新增条目的数量                       |
| Singleton ratio            | 仅被一个 Agent 发现的条目比例               |
| Source coverage            | 已覆盖的数据源、目录、文件类型或网页域名             |
| Query diversity            | 搜索表达和路径是否真正多样                    |
| Self-reported completion   | Agent 自己报告的完成置信度                 |
| Holdout discovery rate     | 独立 Scout 在主流程停止后还能找到多少新条目        |
| Effective exploration size | 名义上调用了多少 Agent，真正独立探索的 Agent 有多少 |

其中最有潜力的是：

> **有效独立探索规模，而不是 Agent 数量本身。**

派出 10 个使用相同模型、相同提示词、相同检索入口和相似上下文的 Agent，未必比派出 3 个真正独立的 Agent 更可靠。

---

# 四、理论部分怎么做，才能真正贴合问题？

## 1. 不要先套几何学

工作流空间确实可以使用图编辑距离、离散几何和信赖域优化建模。但在这个新方向里，几何不是第一优先级。

师姐建议的研究路径应该是：

[
\text{现实异常}
\rightarrow
\text{稳定现象}
\rightarrow
\text{关键变量}
\rightarrow
\text{理论模型}
\rightarrow
\text{轻量方法}
\rightarrow
\text{跨场景验证}
]

理论工具应由现象决定。

对于虚假收敛，更自然的理论工具不是流形，而是：

* Missing mass estimation；
* Good–Turing estimator；
* Capture–recapture；
* 序贯检验；
* 置信区间；
* 相关样本下的有效样本量；
* 自适应采样；
* 来源分区与 holdout 校准。

## 2. 从 Missing Mass 开始

设 Agent 已经发现条目集合 (S_t)，但真实世界中仍存在未发现条目。我们关心的不是简单地问：

> 这一轮有没有新增结果？

而是估计：

[
M_t
===

\Pr(\text{继续探索仍能发现重要新条目})
]

这可以理解为剩余的 **missing mass**。

经典 Good–Turing 思路中，样本中只出现一次的 singleton 比例，可以用于估计尚未观察到的概率质量。McAllester 和 Schapire 对 Good–Turing 估计的收敛速度与高概率置信界进行了分析；后续研究也进一步讨论了 missing mass 的集中性和保证。([Learning Theory][7])

[
\widehat{M}_t
\approx
\frac{f_1}{n}
]

其中：

* (n)：累计发现记录数；
* (f_1)：只出现过一次的条目数。

直观上，如果仍然不断出现 singleton，说明未知空间可能还很大，不应贸然停止。

## 3. 真正的新意：Agent 搜索并不是独立采样

经典 Good–Turing 常从近似独立采样开始。但多个 LLM Agent 往往具有很强的相关性：

* 使用相同模型；
* 继承相同上下文；
* 使用相同搜索 API；
* 生成相似查询；
* 优先访问相似来源；
* 依赖相同的内部知识；
* 被相同的汇总节点引导。

因此，名义上的 Agent 数量并不能直接视为独立样本量。

你可以研究一个 **correlation-aware effective exploration size**：

[
n_{\mathrm{eff}}
================

\frac{\left(\sum_i w_i\right)^2}
{\sum_{i,j} w_i w_j \rho_{ij}}
]

其中：

* (w_i)：第 (i) 个 Agent 或搜索分支的权重；
* (\rho_{ij})：两个分支结果、查询路径或来源分布之间的相关性；
* (n_{\mathrm{eff}})：真正有效的独立探索规模。

这只是一个初始建模方向，不应在 pilot 前直接宣称它成立。真正值得验证的是：

> (n_{\mathrm{eff}}) 是否比名义 Agent 数量、更比“连续无新增轮数”，更能预测 False Stop？

如果能稳定预测，这就可能成为论文里类似 (r/d) 的关键变量。

## 4. 两类完成性必须明确区分

### 封闭世界完成性

例如：

* 代码仓库内所有旧 API 调用点；
* 固定 HTML 快照中所有满足条件的网页；
* 固定文档库中的全部目标实体；
* 数据库中所有符合条件的记录。

实验者掌握 Ground Truth，因此可以计算：

[
\operatorname{Recall}_t
=======================

\frac{|S_t\cap G^\star|}
{|G^\star|}
]

甚至验证是否达到 100% Recall。

### 开放世界完成性

例如：

* 整个互联网中全部相关论文；
* 所有可能的商业竞品；
* 所有潜在事故根因；
* 所有相关市场信息。

这里不能声称：

> 一个条目都没有遗漏。

更严谨的目标是给出统计证书：

[
\Pr(M_t\leq \varepsilon)
\geq
1-\delta
]

含义是：

> 以至少 (1-\delta) 的置信度，继续探索仍能发现重要新内容的剩余概率质量不超过 (\varepsilon)。

论文里不要把开放世界任务包装成绝对完成性证明。你要研究的是 **可信停止条件**，而不是不可能实现的全知保证。

---

# 五、第一阶段不要急着造新算法：先验证现象

这是最符合师姐建议的一步。

## Pilot 目标

先回答：

> 动态多 Agent 工作流是否稳定存在“高一致性、低 Recall、过早停止”的虚假收敛现象？

不要先加入强化学习，不要先训练分类器，也不要先开发大型 Benchmark。

## 1. 第一批任务：只选两类

### A. 代码仓库扫描任务

例如：

* 将旧 API 重命名为新 API；
* 找出全部不安全函数调用；
* 找出全部配置项；
* 统计全部受影响调用点；
* 检查所有未迁移的旧路径引用。

Ground Truth 可以使用：

* `ripgrep`；
* AST 静态扫描；
* 人工复核；
* 单元测试；
* 预先构造的代码仓库。

代码任务非常适合第一轮实验，因为 Ground Truth 容易获得，也贴近 Claude Code 动态工作流的真实使用场景。

### B. 固定文档库或网页快照任务

例如：

* 在本地 HTML 集合中找出满足多个条件的全部条目；
* 在固定论文元数据中找出某一主题、年份和机构组合下的全部论文；
* 在本地商品目录中找出满足复杂约束的全部商品；
* 在固定新闻快照中收集全部相关事件。

这里不要直接使用实时互联网作为第一阶段唯一数据源，因为真实 Recall 无法严格计算。

## 2. 第一轮实验组

第一周只跑 6 组就够了：

| 组别 | 设置                     | 目的                        |
| -- | ---------------------- | ------------------------- |
| G1 | 单 Agent，自行决定停止         | 基准                        |
| G2 | 单 Agent，固定轮数           | 区分停止错误与检索能力不足             |
| G3 | 多个同质 Agent             | 判断增加 Agent 数是否只是增加重复      |
| G4 | Prompt 多样化 Agent       | 检验提示词差异是否改善覆盖             |
| G5 | 来源分区 Agent             | 强制不同 Agent 搜索不同目录、来源或文件类型 |
| G6 | 主流程 + 独立 Holdout Scout | 检测主流程停止后是否仍存在大量遗漏         |

最关键的是 **G6**。Holdout Scout 不应读取主 Agent 的完整轨迹，也不应完全复用相同的提示词与检索入口，否则它并不独立。

## 3. 第一轮日志

每轮都要保存：

```text
task_id
agent_id
round_id
prompt_variant
model_name
query_or_action
source_id
new_items
all_items
item_provenance
self_reported_completion
self_reported_confidence
latency
token_or_cost
stop_reason
```

并额外计算：

* True Recall；
* Precision；
* False Stop Rate；
* 每轮新增率；
* Pairwise Jaccard overlap；
* Singleton ratio；
* 来源覆盖率；
* Agent 自报置信度与真实 Recall 的 calibration error；
* Holdout Scout 的新增发现数量；
* 成本、时延和 Agent 调用次数。

## 4. 第一批图表

第一阶段只需要生成 5 张图：

1. **Recall–Round Curve**：轮数增加时 Recall 如何变化；
2. **Reported Completion vs. True Recall**：Agent 自报完成度是否高估真实完成度；
3. **Overlap vs. Remaining Missing Items**：高一致性是否真的意味着剩余遗漏更少；
4. **Nominal Agent Count vs. Effective Exploration Size**：调用更多 Agent 是否获得真实独立探索；
5. **Cost–Recall Frontier**：独立 Scout、来源分区和 Prompt 多样化分别带来多少覆盖增益。

---

# 六、什么结果出现后，值得继续写论文？

建议设置清晰的 Go / No-Go 条件。

## 值得继续的信号

至少在两类任务、两个模型或两种检索设置中观察到：

* 多个 Agent 高度一致，但真实 Recall 仍明显不足；
* Agent 自报完成置信度与真实 Recall 存在稳定偏差；
* 同质 Agent 数量增加后，结果重叠显著增加，但 Recall 增益迅速饱和；
* 独立 Holdout Scout 在主流程停止后仍能发现遗漏项；
* Singleton ratio、来源覆盖率或 (n_{\mathrm{eff}}) 能较稳定地预测 False Stop；
* 来源分区或真正独立的探索策略比简单增加 Agent 数更有效。

## 应降低优先级的信号

出现以下情况，就不要强行包装：

* 常规模型在合理预算下几乎总能达到接近 100% Recall；
* False Stop 只存在于刻意构造的极端任务；
* 独立 Scout 几乎无法补充新条目；
* Prompt 多样化、来源分区和 Agent 异构化均无明显效果；
* 相关性指标无法预测遗漏；
* 简单静态扫描器已经完全解决目标场景，而且没有必要引入 Agent。

师姐希望你学会的正是这一点：先允许假设被否定，而不是为了保住选题不断增加复杂模块。

---

# 七、如果现象成立，第二阶段再设计轻量方法

当你已经证明虚假收敛存在后，再提出：

> **Correlation-Aware Completion Controller**
> 相关性感知完成性控制器

它不需要一开始就训练复杂模型。可以包含四个部分：

## 1. Discovery Ledger

记录每个条目的：

* 来源；
* 首次发现 Agent；
* 出现次数；
* 发现轮次；
* 检索路径；
* 证据；
* 去重映射。

## 2. Correlation Monitor

监控：

* Agent 结果重叠；
* 搜索查询相似性；
* 来源分布相似性；
* 新增条目趋势；
* singleton 数量；
* 有效独立探索规模。

## 3. Holdout Scout

当控制器认为主流程接近停止，但不确定性仍较高时，派出独立 Scout：

* 使用不同提示词；
* 访问不同来源；
* 使用不同检索策略；
* 不继承过多主流程偏见；
* 优先覆盖尚未探索的区域。

## 4. Completion Certificate

只有满足以下条件才停止：

* 最近若干轮新增率足够低；
* 估计 missing mass 的上界低于阈值；
* 来源覆盖满足要求；
* Holdout Scout 未发现显著遗漏；
* 自报完成度与外部统计信号一致。

在开放世界任务中，输出的不应是：

> 已经找完。

而应是：

> 在当前来源范围、预算和置信水平下，继续搜索发现重要新增条目的估计概率已经低于阈值。

---

# 八、GraphRefactor 怎么处理？

我赞成你上传对话中的处理方式：**新建同级项目，不要直接塞进原仓库。** 

建议目录：

```text
E:\learn3\B\
├── GR\                    # 原 GraphRefactor，保持稳定
└── AgentCompletion\       # 新方向 pilot
```

GraphRefactor 保留三种价值：

| 用法     | 如何保留                                |
| ------ | ----------------------------------- |
| 实验基础设施 | 复用 Agent 接口、执行器、日志、Verifier、成本与时延统计 |
| 对照方法   | 作为局部拓扑编辑基线，验证“只优化结构还不够”             |
| 后续组件   | 在高遗漏风险下插入 Scout、Verifier 或来源分区分支    |

第一阶段不要复用 RL、节点画像和复杂 DAG 重构器。新实验的代码越干净，结论越可信。

---

# 九、其他值得研究的方向

虚假收敛是我最推荐优先验证的方向，但还有三个可保留的备选。

## 备选 1：约束漂移与工作流承载能力

核心问题：

> 委派深度、摘要压缩、循环次数和 fan-in 增加后，Agent 对原始约束的保持率如何衰减？

例如要求：

* 只能修改 `src/`；
* 禁止修改测试文件；
* 必须检查全部调用点；
* 不可信文本不得触发写操作；
* 每项修改必须运行对应测试。

然后控制工作流深度、分支数量、摘要方式和模型规模，记录约束保持率。

理论工具更接近：

* 信息论；
* 信道收缩；
* 路径累积误差；
* 状态压缩；
* 外部结构化记忆。

这个方向很有价值，但构造实验和定义约束难度稍高，建议作为第二优先级。

## 备选 2：错误级联临界点

核心问题：

> 一个错误中间结论在什么结构下会被修正，在什么结构下会快速扩散？

可以人工注入错误，研究：

* 分支数量；
* 验证器位置；
* 信息汇总方式；
* Agent 同质性；
* 错误源距离；
* 工作流深度；
* 是否存在级联阈值。

理论工具包括传播动力学、分枝过程和谱分析。

方向很漂亮，但已经开始出现运行时审计、错误定位和故障恢复相关研究，不建议作为第一选择。

## 备选 3：工作流模式相图

核心问题：

> 什么任务适合单 Agent、fan-out、对抗验证、tournament 或 loop-until-done？

可以尝试建立：

[
\text{task decomposability}
\times
\text{verification difficulty}
\times
\text{budget}
\times
\text{branch correlation}
\rightarrow
\text{best workflow motif}
]

这可能形成“工作流模式相图”。但它对数据量和实验覆盖要求比较高，容易再次滑向动态路由红海。

---

# 十、最合适的研究顺序

按师姐的建议，不要立刻定论文标题，也不要马上开发大系统。先走下面这条路线：

| 阶段     | 目标                    | 产物                                                    |
| ------ | --------------------- | ----------------------------------------------------- |
| 第 1 阶段 | 验证虚假收敛是否稳定存在          | 两类任务、6 组实验、5 张图                                       |
| 第 2 阶段 | 找到最具预测力的变量            | overlap、singleton、来源覆盖、(n_{\mathrm{eff}}) 对比          |
| 第 3 阶段 | 建立统计模型                | missing mass 上界、相关性感知停止规则                             |
| 第 4 阶段 | 设计轻量控制器               | Discovery Ledger、Holdout Scout、Completion Certificate |
| 第 5 阶段 | 外部验证                  | WideSearch、DeepSearchQA、TRQA 和真实代码仓库任务                |
| 第 6 阶段 | 再决定是否加入 GraphRefactor | 按风险动态插入 Scout、Verifier 或重构分支                          |

现阶段最值得投入的不是几何感知拓扑优化，而是一个更尖锐的问题：

> **多个 Agent 看起来已经达成一致时，它们是真的完成了任务，还是只是共同停止了探索？**

这个问题有真实工业背景，有可测量的现象，有自然的统计理论工具，也能在不浪费既有 GraphRefactor 代码的前提下，形成一条更有辨识度的新主线。

[1]: https://arxiv.org/abs/2601.20975?utm_source=chatgpt.com "DeepSearchQA: Bridging the Comprehensiveness Gap for Deep Research Agents"
[2]: https://arxiv.org/html/2603.22386v1?utm_source=chatgpt.com "A Survey of Workflow Optimization for LLM Agents"
[3]: https://code.claude.com/docs/en/workflows?utm_source=chatgpt.com "Orchestrate subagents at scale with dynamic workflows"
[4]: https://arxiv.org/abs/2508.07999?utm_source=chatgpt.com "WideSearch: Benchmarking Agentic Broad Info-Seeking"
[5]: https://arxiv.org/abs/2603.18516?utm_source=chatgpt.com "Total Recall QA: A Verifiable Evaluation Suite for Deep Research Agents"
[6]: https://arxiv.org/abs/2601.17617?utm_source=chatgpt.com "Agentic Search in the Wild: Intents and Trajectory Dynamics from 14M+ Real Search Requests"
[7]: https://www.learningtheory.org/colt2000/papers/McAllesterSchapire.pdf?utm_source=chatgpt.com "On the Convergence Rate of Good-Turing Estimators"
