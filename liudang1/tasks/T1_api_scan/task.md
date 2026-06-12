# T1: Code Repository Scan

目标：验证 Agent 在代码仓库覆盖扫描任务中是否出现 False Convergence。

## 任务描述

让 Agent 找出仓库中所有满足条件的目标调用点，例如：

```text
找出所有旧 API、旧路径、危险函数或未迁移调用点。
```

第一轮建议选一个具体目标，不要同时混合多类目标。

## 推荐构造方式

为了快速获得 Ground Truth，第一轮使用半合成任务：

- 选择一个小型真实仓库或自建仓库。
- 植入 30 到 60 个目标调用点。
- 目标分布在至少 4 个目录或文件类型中。
- 使用不同命名形式、包装函数、别名导入和配置引用。
- 加入少量相似但非目标项，用于测试 precision。

## Ground Truth 条目格式

```json
{
  "item_id": "T1_item_001",
  "file_path": "src/services/payment.py",
  "line": 42,
  "target_type": "old_api_call",
  "matched_symbol": "legacy_charge",
  "evidence": "legacy_charge(user_id, amount)",
  "source_region": "src/services",
  "difficulty_tag": "alias_or_wrapper"
}
```

## Agent 输出要求

Agent 必须输出可验证条目：

```json
{
  "file_path": "src/services/payment.py",
  "line": 42,
  "evidence": "legacy_charge(user_id, amount)",
  "reason": "旧 API 调用点"
}
```

没有 `file_path` 和 `evidence` 的条目不计入 true positive。

## 首轮检查点

- `|G*|` 在 30 到 60 之间。
- 至少 20% 目标项不容易被单一关键词覆盖。
- 至少 10% 非目标项看起来相似。
- 静态扫描或人工复核能得到完整 Ground Truth。

