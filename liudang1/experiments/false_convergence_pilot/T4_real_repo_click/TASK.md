# T4 Real Repo Click Deprecation Audit

This is a real-repository closed-world discovery task.

Repository snapshot:

- local path: `repo/`
- upstream: https://github.com/pallets/click
- commit: `8a1b1a33d739be05b7e91251e3c0dde77c5e152f`

## Goal

Find every line-level location in the repository snapshot that belongs to the
current deprecated API surface audit.

An item is in scope if the line is part of one of these categories:

1. implementation of deprecated command, argument, option, parser, or compatibility behavior;
2. warning emission for deprecated public APIs or deprecated parameter usage;
3. formatting of deprecated help labels or warning suffixes;
4. validation guards that reject invalid deprecated configurations;
5. tests that directly assert deprecated help text, warnings, or validation behavior;
6. direct user documentation for marking commands as deprecated;
7. relevant bounded changelog entries near the current deprecation feature notes.

The oracle has 149 line-level items.

## Boundaries

Inspect only this task directory. Do not inspect oracle, score, result, or
itemset files outside this task directory.

Include only concrete `file_path:line` items. The file path must be relative to
this task root and should start with `repo/`, for example:

```json
{"file_path": "repo/src/click/core.py", "line": 1359}
```

Do not include broad file-level answers. Do not include incidental uses of the
word "deprecated" outside the target audit set.

## Suggested audit strategy

1. Inspect source implementation in `repo/src/click/__init__.py`,
   `repo/src/click/core.py`, and `repo/src/click/parser.py`.
2. Inspect tests in `repo/tests/test_arguments.py`,
   `repo/tests/test_options.py`, and `repo/tests/test_commands.py`.
3. Inspect user documentation in `repo/docs/commands-and-groups.md`.
4. Inspect the bounded current changelog region in `repo/CHANGES.md`.
5. Return exact line-level items only.

## Output format

```json
{
  "run_id": "T4_G3_seed01_agentXX",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {"file_path": "repo/src/click/core.py", "line": 1359}
  ]
}
```
