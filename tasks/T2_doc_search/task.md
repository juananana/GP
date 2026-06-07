# T2: Fixed Document Collection Search

目标：验证 Agent 在固定文档集合的多条件检索任务中是否出现 False Convergence。

## 任务描述

让 Agent 在固定文档集合中找出所有满足条件的条目。

示例：

```text
找出所有同时满足条件 A、B、C 的条目，并给出证据片段。
```

第一轮不要使用实时互联网。使用本地 HTML、Markdown、CSV、JSON 或文档快照。

## 推荐构造方式

- 准备 50 到 200 个 source 文档。
- 设计 30 到 80 个真实目标条目。
- 目标分布在多个 source、主题、字段或章节中。
- 至少一个条件需要跨句、跨字段或上下文判断。
- 加入相似但不满足全部条件的干扰条目。

## Ground Truth 条目格式

```json
{
  "item_id": "T2_item_001",
  "source_id": "doc_014",
  "title": "source title",
  "conditions": {
    "condition_a": true,
    "condition_b": true,
    "condition_c": true
  },
  "evidence_span": "原文中可验证的证据片段",
  "source_region": "topic_or_folder",
  "difficulty_tag": "multi_condition"
}
```

## Agent 输出要求

Agent 必须输出：

```json
{
  "source_id": "doc_014",
  "item_name": "target item name",
  "evidence_span": "原文中可验证的证据片段",
  "matched_conditions": ["A", "B", "C"]
}
```

没有 `source_id` 和 `evidence_span` 的条目不计入 true positive。

## 首轮检查点

- `|G*|` 在 30 到 80 之间。
- 目标条目覆盖至少 4 个 source 区域。
- 干扰条目数量不少于目标条目的 20%。
- Ground Truth 可以由脚本或人工复核得到。

