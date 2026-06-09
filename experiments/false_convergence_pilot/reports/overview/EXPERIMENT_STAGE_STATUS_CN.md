# 当前实验阶段判断

日期：2026-06-08

## 一句话判断

当前已经不只是“验证问题是否存在”。Line A 已经完成了问题机制验证，正在进入：

> 方法评估 + 真实任务族验证 + 扩量稳定性测试阶段。

也就是说，我们现在不是在训练模型，而是在做系统性测试、对照实验和论文证据扩充。

## 已完成到哪里

### 1. 问题存在与机制验证：已基本完成

已有证据：

- T1 seed01：strict aggregation-loss 阳性。
- T2 seed01：near-positive aggregation loss。
- T2 seed02/03：common blind spot 稳定复现。
- standard summarizer / consensus 会丢少数派真阳性。
- union-preserving 能恢复部分漏项，但在 T1 seed02/03 和 T4 中会带来 precision cost。

这足以支撑论文里的问题定义：

> Consensus is not completion.

### 2. 方法初步验证：已完成第一版

已有方法：

- evidence-preserving protocol。
- completion certificate v0。
- singleton audit。
- high-agreement blindspot trigger。
- holdout scout。

已有 ablation：

- 去掉 singleton audit，aggregation loss 恢复不了。
- 去掉 common-blindspot trigger，T2 seed02/03 恢复不了。
- 去掉 holdout，只能输出 requires_audit，不能恢复漏项。

### 3. 真实任务族验证：已开始并有结果

T4 Click real-repo blind validation 已完成 seed01：

- consensus：recall `0.953`，precision `0.993`。
- raw union：recall `0.993`，precision `0.744`。
- protocol：recall `0.993`，precision `0.955`。
- AutoDL standard summarizer：confidence `0.930`，recall `0.698`，precision `0.990`，构成真实仓库上的 aggregation-stage false stop。
- AutoDL union-preserving summarizer：recall `0.993`，precision `0.744`，说明保留少数派证据能恢复 recall，但需要审计控制 precision cost。

T4 的 consensus 不是 strict false convergence 阳性，但 AutoDL standard summarizer 给出了强聚合阶段阳性；因此 T4 现在不只是边界样本，也是现实 aggregation policy 失败样本。

## 现在还缺什么

如果目标是顶会论文，现在最缺的是：

- 更多 seed：T1/T2/T4 至少补到 5 seeds。
- T4 seed02/03：看真实仓库结论是否稳定。
- prompt-diverse G3：验证降低相关错误是否有效。
- 真正的 LLM summarizer 对照：standard vs union-preserving，而不是只有确定性基线。
- 真实 token / wall-clock 成本：替代 proxy cost。
- completion certificate 校准：v0 目前保守，false certification 为 0，但 conservative block 偏多。

## 加速推进路线

### 最快可产出论文增量

1. 跑 T4 seed02/03 的 G3 + G6。
2. 扩展 AutoDL summarizer 到 T4 seed02/03。
3. 加真实成本日志到所有新增 G3/G6/summarizer runs。
4. 更新 main.tex 的实验表。

### 最有研究价值的增量

1. prompt-diverse G3 vs homogeneous G3。
2. source-partitioned G3 vs unrestricted G3。
3. certificate v0 阈值校准。
4. Good-Turing / Chao / confidence / overlap / certificate 的统一 ROC/AUPRC 对比。

### 暂时不建议优先做

- 继续构造更难的合成任务。
- 继续手工调 T2 文档格式。
- 现在就声称“问题已普遍证明”。
- 现在就把 protocol 写成最终解决方案。

## 当前论文定位

比较稳的定位是：

> 我们识别并形式化了 multi-agent discovery workflow 中的 false convergence 风险，展示了 aggregation loss 和 common blind spot 两类机制，并提出 coverage-risk-aware completion certificate / evidence-preserving audit controller，用于把隐藏漏项风险转成显式审计决策。

不要写成：

> 我们已经解决了 multi-agent discovery 的完成性问题。

更好的写法是：

> 我们证明 consensus/confidence 不是可靠完成证书，并展示 correlation-aware audit controller 可以在多个任务族中降低 false stop 或 precision-recall 风险。
