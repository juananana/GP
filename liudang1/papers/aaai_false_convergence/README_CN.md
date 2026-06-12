# AAAI 初稿说明

日期：2026-06-08

## 当前文件

- `main.tex`：AAAI 风格英文论文初稿。
- `references.bib`：当前相关工作引用库。
- `main.pdf`：已能编译生成的 PDF。

## 当前论文定位

这篇论文现在适合定位为：

> 一个关于 multi-agent closed-world discovery 的 completion-signal failure 论文。

核心口号：

> Consensus is not completion.

更具体地说，我们不是泛泛地说“LLM 会漏东西”，而是研究：在需要找全目标集合的封闭世界任务中，multi-agent workflow 什么时候可以相信自己已经完成。

## 问题定义

建议把 False Convergence 定义为：

> 一种 completion-signal failure：系统表现出高一致性、高置信、自报完成，但在 closed-world oracle 下仍漏掉真实项。

论文里区分两种机制：

- `aggregation loss`：少数派 agent 已经找到真项，但 consensus / standard summarizer 把它丢掉。
- `common blind spot`：多个 agent 因为共享搜索盲区而一起漏掉同一类边界项，raw union 也救不回来。

## 已完成实验

| 任务 | 状态 | 可报告结论 |
| --- | --- | --- |
| T1 synthetic code audit | 完成 | aggregation loss + raw union precision-cost control。 |
| T2 natural policy docs | 完成 | aggregation loss + common blind spot 稳定复现。 |
| T4 Click real repo | 完成 3 blind seed | standard summarizer false stop `3/3`；union-preserving 恢复 recall 但 precision 降低。 |
| completion certificate v0 | 完成 | T4 三 seed 均 `unsafe_to_stop`，没有错误认证完成。 |
| source-aware audit v2 | 完成原型 | T4 candidate filter 可把候选池恢复到高 recall / high precision，但属于 audit-policy 原型，不是 blind LLM 结果。 |
| T5 Requests TLS real repo | 完成 3 blind seed | 第二真实仓库任务族；standard summarizer false stop `3/3`，raw union 提升 recall 但仍低于完成阈值。 |

## T4 核心结果

T4 oracle size：`149`。

standard summarizer：

- seed01：recall `0.698`，precision `0.990`，false stop。
- seed02：recall `0.745`，precision `1.000`，false stop。
- seed03：recall `0.685`，precision `1.000`，false stop。

union-preserving summarizer：

- seed01：recall `0.993`，precision `0.744`。
- seed02：recall `1.000`，precision `0.639`。
- seed03：recall `1.000`，precision `0.642`。

论文里可以写：

> On a real Click repository audit, a standard high-precision summarizer self-reports completion in all three seeds while retaining only 68.5--74.5% of oracle items.

## 方法定位

不要把方法写成“union-preserving solves false convergence”。更稳的定位是：

> Evidence-Preserving Completion Protocol + coverage-risk certificate。

也就是：

1. consensus items 进入保守 final set。
2. singleton items 不直接丢，也不直接收，而是进入 audit queue。
3. high confidence + high agreement + boundary-risk task 触发 holdout/audit。
4. completion 不是一个 yes/no vote，而是 coverage-risk assessment。

## Source-Aware Audit v2 怎么写

可以写成一个 stronger audit prototype：

- `candidate filter`：只审计 G3/holdout 已经报过的候选，T4 seed01 达到 `0.993/1.000` recall/precision，seed02/03 达到 `1.000/1.000`。
- `source sweep`：在 bounded target files 上运行任务策略谓词，是 upper bound，不是 blind LLM 结果。

必须诚实写：

> This is an audit-policy upper-bound prototype, not a blind LLM result.

## 当前不能过度主张

不要写：

- We fully solve false convergence.
- T5 fully replicates the T4 mechanism.
- Union-preserving summarization is the solution.
- High confidence is useless.

可以写：

- consensus and high-confidence summarization are insufficient completion certificates。
- aggregation loss and common blind spots are distinct failure mechanisms。
- raw union is diagnostic but not sufficient。
- retained minority evidence plus audit can convert hidden omissions into auditable risk。

## T5 核心结果

T5 oracle size：`304`。

- consensus recall：seed01 `0.701`，seed02 `0.678`，seed03 `0.678`。
- standard summarizer recall：seed01 `0.368`，seed02 `0.622`，seed03 `0.648`，并且 `3/3` false stop。
- raw union recall：seed01 `0.859`，seed02 `0.845`，seed03 `0.829`，比 consensus 更好但仍不完整。
- completion certificate v0：`3/3 unsafe_to_stop`。

论文里应把 T5 写成第二真实仓库上的“更难边界”：它支持 false convergence 的风险不是 Click/deprecation audit 独有，但不要写成 T4 的直接复制。T4 更像 aggregation-stage false stop；T5 更像 search coverage insufficiency + summarization compression + unsafe stop 的混合形态。

## 下一步

1. 完成 `main.tex` 的最终同步和编译检查。
2. 把 source-aware audit v2 替换/扩展为 blind source-partitioned audit，而不是 deterministic upper bound。
3. 补 prompt-diverse / source-partitioned / model-heterogeneous 对照，验证降低 agent 相关性是否减少共同盲点。
