# T2 policy docs 稳定性补充结果

日期：2026-06-07

## 一句话结论

T2 policy docs 已经补齐 seed01/02/03。它没有达到 strict false convergence 阈值，但稳定证明了一个很重要的现象：多个 agent 可以高信心、高一致地停在同一个不完整答案上；独立复查能恢复漏掉的边界项。

## 三 seed 对照

| seed | G3 形态 | Consensus recall | Raw union recall | Holdout recall | Precision | Strict positive | 解释 |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| seed01 | 一个 G3 找到边界项，两个漏掉 | 0.933 | 1.000 | 1.000 | 1.000 | false | aggregation loss：少数派真项被 consensus / standard summarizer 丢掉 |
| seed02 | 三个 G3 完全一致地漏掉边界项 | 0.933 | 0.933 | 1.000 | 1.000 | false | common blind spot：union 也救不回来，因为 G3 reports 中没有漏项 |
| seed03 | 三个 G3 再次完全一致地漏掉边界项 | 0.933 | 0.933 | 1.000 | 1.000 | false | common blind spot 跨 seed 复现 |

三个 seed 都漏的是同两个边界案例：`CASE-047` 和 `CASE-048`。这两个 case 的 service 名称像 charge，但 flow 是 refund；真正判断需要跟随 service catalog / adapter registry 解析到 AcmePay v1。

## 这一步证明了什么

- `consensus` 不等于完成：T2 三个 seed 的 consensus 都只有 `28/30`，但 agent 仍自报完成。
- `high overlap` 不等于完成：seed02/03 的 G3 pairwise Jaccard 都是 `1.000`，但仍漏掉同两个真项。
- `raw union` 只能恢复“已经被某个 agent 找到”的项：seed01 可以恢复，seed02/03 不能恢复。
- `holdout scout` 能证明任务不是不可解：seed01/02/03 的 holdout 都达到 `30/30` 且 precision 为 `1.000`。

## 这一步还不能证明什么

- 不能说 T2 已经是 strict positive，因为 holdout gain 是 `2/30 = 0.067`，低于预注册阈值 `gamma = 0.100`。
- 不能说 union-preserving 总能解决问题。seed02/03 中漏项没有进入 G3 reports，union-preserving 也没有材料可保留。
- 不能说所有 multi-agent workflow 都会失败。更稳的说法是：completion signal 需要同时检查搜索覆盖和聚合策略。

## 对论文主张的意义

T2 把 A 线从单一 aggregation-loss 机制扩展为双机制：

1. `aggregation loss`：少数派 agent 找到了真项，但最终汇总丢掉它。
2. `common blind spot`：多个 agent 使用相似搜索路径，彼此高度一致地漏掉同一类边界项。

因此当前最稳的论文表达是：

> Consensus is not completion. High agreement can either mean the task is solved, or that agents share the same blind spot.

下一步如果要继续增强论文级证据，优先补一个更真实的第二任务族，或扩大 T2 风格任务的 oracle 规模，让小数量边界漏项也能被更稳定地统计出来。
