我会比较客观地说：**这版已经从“有想法的研究草稿”变成了“可以认真冲 AAAI 的方法论文雏形”，但还不是高分稳稿。** 现在的主要风险不是“实验没有闭环”，而是：**方法深度、实验外部有效性、理论边界、图表观感和审稿人对 novelty 的判断还不够稳。**

如果按现在版本直接投，我觉得可能是 **borderline / weak accept 区间**；如果再补强一轮，尤其是补一个更像 completion audit 的小型验证、强化理论保证和图表表达，才有机会接近 **solid accept**。

---

## 一、先给整体评分判断

从审稿人视角，我大概会这样打：

| 维度        | 当前判断                                               |
| --------- | -------------------------------------------------- |
| 问题重要性     | 较好，有现实意义                                           |
| 新颖性       | 中等偏上，但容易被认为是 coverage / audit / active search 的再包装 |
| 方法完整性     | 已经成型，但像 rule-based controller，理论深度还可以加强            |
| 实验完整性     | 主闭环已经有，但外部验证仍偏弱                                    |
| 写作清晰度     | 比之前好很多，摘要和主线清楚                                     |
| 图表质量      | 仍有提升空间，Figure 2/4 尤其影响第一印象                         |
| AAAI 高分潜力 | 有，但目前还不是高分稿                                        |

我会给当前版本一个比较现实的判断：

> **当前：5.5–6.5 / 10，偏 borderline 到 weak accept。**
> **改好后：6.5–7.5 / 10，有机会 weak accept / accept。**
> **想成为高分强稿：需要再补一个更强外部验证或更硬的理论结果。**

---

## 二、这篇论文现在最强的地方

### 1. 问题定义已经比较清楚

论文现在抓住了一个很好的核心问题：

> stop signal 本身不等于 completion certificate。关键是 stop signal 是在什么 evidence condition 下产生的。

摘要里已经把这个问题讲得很清楚：no-new、agreement、stable summary 等停止信号可以局部有意义，但未必能作为 scope-wide completion certificate；论文提出用 source-route stratum 记录“在哪里搜索”和“用什么 audit route 搜索”，再构建 evidence-condition controller。

这个问题比普通“多 agent 会犯错”更具体，审稿人容易理解。

### 2. 方法结构已经像一篇方法论文了

现在方法部分已经拆成四个模块：

```text
source-route exposure estimation
eligibility gate
residual-evidence repair
SAFE / CONTINUE / ABSTAIN decision rule
```

论文也明确说，方法不是证明 universal completion，而是在接受 stop claim 之前显式检查 runtime evidence condition。

这个方向是对的。比之前“发现问题 + 修补实验”的感觉强很多。

### 3. 实验闭环已经成立

现在实验不只是证明问题存在，而是有了 baseline / ablation：

* Naive stop；
* Source-only；
* Source-route eligibility-only；
* Full controller；
* Random / High-potential / Residual-potential repair variants。

论文明确写了这些 policy 使用相同 fixed trajectories 和 proposed stop states，差异来自 decision rule 或 repair target selection，而不是不同 discovery trajectories；oracle 只用于 post-hoc scoring。

这个很关键。它说明你们已经不是单纯“现象论文”，而是在评估 controller 的设计选择。

---

## 三、当前最大的审稿风险

### 风险 1：容易被认为是“coverage + audit + heuristic controller”的组合

严格审稿人可能会说：

> 你们的 source-route exposure 不就是 coverage matrix 吗？
> support/Gini 不就是 coverage/concentration 指标吗？
> repair 不就是继续搜索弱区域吗？

这不是致命问题，但必须防御。现在 Related Work 已经和 high-recall review、active search、missing mass、agent verification、agreement/oversight 做了区分，但还可以更硬一点。论文现在强调 controller 不观察 oracle totals、recall 或 hidden missing mass，只观察 stop claim 产生时的 source-route condition，以及 repair 是否揭示 residual evidence。 这个方向很好，但还需要再加一句更强的 novelty framing：

> **我们不是估计还有多少 item 未发现，而是判断一个 stop certificate 的证据条件是否匹配它声称覆盖的 scope。**

建议在 Introduction 或 Related Work 末尾加一个小段 **“Why this is not coverage / total recall / active search”**。不要太长，3–4 句即可。

---

### 风险 2：理论结果偏“显然”，还不够有深度

Proposition 1 的逻辑是：如果所有 evidence 都在 (U \subset \Omega)，那么 no-new over (U) 不能证明 completion over (\Omega)。这是正确的，但审稿人可能觉得：

> 这个命题太直观，像常识形式化，不足以构成理论贡献。

所以我建议补一个更像方法 guarantee 的命题，例如：

> **Under declared source-route scope and oracle-free repair protocol, the controller never returns SAFE unless eligibility holds and residual repair is nonproductive.**

这不是强保证“世界无遗漏”，而是保证 controller 的输出语义与证据条件一致。可以叫：

```text
Proposition 2: Soundness of SAFE under the controller’s declared certificate semantics.
```

证明也不需要很长。目标是让方法看起来不是一组规则，而是一个有明确 certificate semantics 的控制器。

---

### 风险 3：外部实验仍偏弱，pattern-defined oracle 会被质疑

现在实验包括两个 generated audits 和两个 real-repository audits。论文也很诚实地写了，external oracles 是 pattern-defined from frozen snapshots，比 generated toy 强，但弱于 human-annotated completion-audit benchmarks。

这个诚实是好的，但审稿人可能会因此打折：

> 真实仓库实验是否只是 regex/pattern audit？
> 这是否真的代表 agent workflow completion？
> generated tasks 是否过于可控？

如果时间允许，我最建议补一个**小型 claim-verification completion audit**，而不是再加一个 item-discovery repo audit。

比如论文里自己已经提到未来可以做 claim-verification audit，包括 support、contradiction、exception-path、configuration-default、scope-boundary routes。这个方向非常适合作为一个小主实验，而不是 future work。

可以很小：

```text
Claim: all network-facing calls either set timeout or route through retry/timeout policy.
Sources: 4–6 files/modules.
Routes: support, contradiction, exception-path, config-default, scope-boundary.
Compare: Naive / Source-only / Eligibility-only / Ours.
```

这会显著提高论文价值，因为它能证明方法不只适用于“找 item”，也适用于更像 completion claim 的审计。

---

### 风险 4：Figure 2 还是有点像 AI 画的说明图，不够顶会质感

现在 Figure 2 在第 4 页，方法结构是对的：四模块结构、source-route matrix、eligibility gate、residual repair、decision rule 都有。 但问题是：

* 图里的小字还是太多；
* 模块边框较重；
* 底部 example summary 仍然稍微抢戏；
* 图片整体像“AI infographic”，不是特别像手工排版的 AAAI 图。

建议最终版 Figure 2 用矢量工具重画，不要完全依赖生成图。最稳的做法是用 TikZ / Illustrator / Figma 画，保持四模块主流程，底部只留极小 legend，不要大 inset。

---

### 风险 5：Figure 4 很关键，但在版面上有点“挤”

Figure 4 现在做得比上一版合理：左/中是 decision variants 的 FCR 和 safe coverage，右边是 repair target variants 的 gain-cost tradeoff；caption 也明确 FCR 是 oracle-unsafe fixed stops 的 micro-average，safe coverage 是 oracle-safe fixed stops 和 seeded complete states 的 micro-average。

但审稿人看图时可能仍然会有两个问题：

1. **FCR 1.00 / 1.00 / 0.20 / 0 的 denominator 是多少？**
2. **Full controller 的 safe coverage 是不是只在少数 safe states 上成立？**

建议在正文或 supplement 里加一个小表：

```text
variant | #unsafe states | #safe states | #SAFE on unsafe | #SAFE on safe | FCR | safe coverage
```

主文不一定要放，supplement 放就够。但 Figure 4 caption 可以加一句：

```text
Counts are reported in Supplementary Table X.
```

这样审稿人会觉得统计口径更扎实。

---

## 四、现在还需要具体怎么修改

### 必改 1：把 contribution 里的方法深度再抬一点

现在 contribution 是对的，但可以更强调：

```text
certificate semantics
eligibility/proof separation
oracle-free runtime controller
```

建议把第二个贡献改得更硬：

> We define a certificate semantics for bounded audit completion: a SAFE decision is admissible only when the source-route evidence condition is eligible and residual-evidence repair is nonproductive.

这样比“we introduce geometry and controller”更像理论/方法贡献。

---

### 必改 2：补一个 Proposition 2 或 Theorem-like statement

建议放在 Method 5.4 后面，内容大概是：

```text
Proposition 2 (Controller certificate semantics).
For a declared source-route scope Ω and a fixed repair rule using only runtime-visible signals, Algorithm 1 returns SAFE only if (i) the exposure condition satisfies the eligibility gate and (ii) repair/audit reveals no residual evidence within the allocated repair budget. Otherwise it returns CONTINUE if residual evidence is found, or ABSTAIN when eligibility cannot be established under budget.
```

这个命题不需要夸张。它的价值是把 controller 的语义说清楚。

---

### 必改 3：补强 Related Work 边界

建议新增一个短段，放在 Related Work 最后：

```text
Coverage and stopping criteria.
```

内容包括：

* 软件测试 / audit coverage 关注覆盖多少程序结构或测试路径；
* active search / total recall 关注如何更快找全 positives；
* 本文关注的是 stop certificate 的条件匹配；
* source-route coverage 不是目标本身，而是 certificate eligibility 的诊断条件。

这个能防止“这不就是 coverage 吗”的攻击。

---

### 必改 4：Figure 2 用人工矢量重画

我建议不要再继续纯 AI 生成。直接用现在这个结构做人工版：

```text
[Exposure Estimation] → [Eligibility Gate] → [Residual Repair] → [Decision Rule]
```

底部只放：

```text
observed / exposed / residual gap
local→ABSTAIN; broad+residual→CONTINUE; broad+clean→SAFE
```

不要大热图，不要复杂内部图标，不要粗边框。Figure 2 的目标是**方法架构清楚**，不是好看复杂。

---

### 必改 5：补充一个 small claim-verification audit，或者至少把它写成强 future validation

如果能跑实验，强烈建议补。它可能是从 borderline 拉到 weak accept/accept 的关键。

如果实在跑不了，就不要在主文里写太多 future claim-verification，而是在 Limitations 里保守一句即可。因为现在主文提 future work 会提醒审稿人：

> 你们自己也知道缺一个非 item-discovery audit。

最理想是把 future work 变成一小节 supplement validation。

---

## 五、次要但会影响观感的问题

### 1. 章节太碎

现在有 8 Discussion and Validity、9 Limitations and Supplement、10 Conclusion，而且每节都很短。

建议合并成：

```text
8 Discussion, Limitations, and Conclusion
```

这样节奏更自然，也省空间。

---

### 2. Table 1 可以移到 supplement

Table 1 的信息有用，但主文已经非常紧。它现在占了第 6 页顶部不少空间。

如果要腾空间给 claim-verification audit 或 Proposition 2，可以把 Table 1 移到 supplement，正文保留一句：

> We evaluate two generated audits, two external repository audits, 200-seed controller validations, and controlled simulation sweeps; details are in Supplementary Table X.

---

### 3. Abstract 现在不错，但略密

摘要已经比之前好很多，尤其是最后一句“bounded diagnostic and control principle”很稳。 但可以稍微减少罗列，让读者更快抓到“certificate mismatch + controller”。

---

### 4. references 仍需格式统一

有些 arXiv 文献格式已经比之前好，但最后还要统一检查大小写，例如 “ai safety” 应该按标题格式或 BibTeX 保留规范大小写。这个是小问题，但 AAAI 审稿里会影响正式感。

---

## 六、这篇论文的高分潜力在哪里？

它有潜力，但高分的前提是你把它包装成：

> **一种 bounded audit completion 的 certificate framework。**

而不是：

> **我们发现 LLM agents 会局部搜索，然后用 coverage/Gini 修一下。**

高分点在这里：

1. **问题切得准**：不是泛泛说 agent 不可靠，而是说 stop evidence 的条件与 completion claim 的范围错配。
2. **方法边界克制**：不声称 universal completion，不声称 optimal repair。
3. **实验设计能服务方法设计点**：source-only 消融、eligibility-only 边界、full controller 非 never-stop、repair policy 对比都已经有。
4. **容易引起 agent workflow / audit / safety 审稿人的兴趣**。

但是高分阻碍也很明显：

1. **方法容易被看成 heuristic controller**；
2. **理论命题目前偏直观**；
3. **真实实验是 pattern-defined oracle，不是人工 completion benchmark**；
4. **图表还有 AI 感和压缩感**；
5. **应用范围被 bounded audit 限制，可能被认为较窄。**

所以我的客观判断是：

> **这篇论文有“好想法 + 可投潜力”，但目前不是那种一看就 strong accept 的稿子。**
> 它更像一篇需要靠清晰定位、克制主张、扎实消融和漂亮图表来赢审稿人的方法论文。

---

## 七、最终修改优先级

最值得做的 5 件事：

```text
1. 补 Proposition 2，把 controller 的 certificate semantics 形式化。
2. Related Work 加一小段 coverage / stopping criteria 边界，防止被说成 coverage 换名。
3. Figure 2 用人工矢量重画，保留四模块架构，删掉视觉噪声。
4. Figure 4 在 supplement 补 denominator/count table，主文 caption 指向它。
5. 能跑的话，补一个小型 claim-verification audit；不能跑就弱化 future-work 暗示。
```

我会把现在的论文定位为：

> **已经具备 AAAI 投稿基础，但还需要一次“审稿人防御型重构”。**
> 不是大改主线，而是把 novelty、guarantee、validity 和 figure polish 补到位。
