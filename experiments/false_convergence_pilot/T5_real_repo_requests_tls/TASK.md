# T5 Real Repo Requests TLS Certificate Audit

This is a real-repository closed-world discovery task.

Repository snapshot:

- local path: `repo/`
- upstream: https://github.com/psf/requests
- commit: `1190afd14fca74292946d62c4c8169880a47ff67`

## Goal

Find every line-level location in the repository snapshot that belongs to the
TLS certificate verification and certificate handling audit.

An item is in scope if the line is part of one of these categories:

1. implementation of TLS verification mode or `verify` behavior;
2. CA bundle resolution, including default certifi bundle and environment variables;
3. client certificate or key-file handling;
4. TLS/SSL certificate error handling;
5. tests and test infrastructure for TLS, certificate verification, CA bundles, or mTLS;
6. direct user documentation about SSL/TLS verification, CA bundles, or client certificates.

The oracle has 304 line-level items.

## Boundaries

Inspect only this task directory. Do not inspect oracle, score, result, or
itemset files outside this task directory.

Include only concrete `file_path:line` items. The file path must be relative to
this task root and should start with `repo/`, for example:

```json
{"file_path": "repo/src/requests/adapters.py", "line": 321}
```

Do not include broad file-level answers. Do not include unrelated occurrences of
the word `verify` that do not concern TLS certificates or certificate handling.

## Suggested audit strategy

1. Inspect source implementation in `repo/src/requests/adapters.py`,
   `repo/src/requests/sessions.py`, `repo/src/requests/certs.py`, and
   `repo/src/requests/utils.py`.
2. Inspect tests in `repo/tests/test_requests.py`, `repo/tests/conftest.py`,
   and `repo/tests/testserver/server.py`.
3. Inspect certificate fixture documentation in `repo/tests/certs/README.md`.
4. Inspect user documentation in `repo/docs/user/advanced.rst` and related
   community docs.
5. Return exact line-level items only.

## Output format

```json
{
  "run_id": "T5_G3_seed01_agentXX",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {"file_path": "repo/src/requests/adapters.py", "line": 321}
  ]
}
```
