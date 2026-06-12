# T6 Real Repo itsdangerous Timestamp Signing Audit

This is a real-repository closed-world discovery task.

Repository snapshot:

- local path: `repo/`
- upstream: https://github.com/pallets/itsdangerous
- commit: `672971d66a2ef9f85151e53283113f33d642dabd`

## Goal

Find every line-level location in the repository snapshot that belongs to the
timestamped signing and expiration audit.

An item is in scope if the line is part of one of these categories:

1. implementation of `TimestampSigner`, `TimedSerializer`, or
   `URLSafeTimedSerializer` timestamp signing behavior;
2. timestamp encoding, decoding, conversion to datetime, or current timestamp
   lookup;
3. `max_age`, expiration, future timestamp, `return_timestamp`, or
   `date_signed` behavior;
4. `SignatureExpired` or `BadTimeSignature` exception behavior directly tied to
   timestamped signatures;
5. tests that directly assert timestamp signing, expiration, malformed
   timestamp, returned timestamp, or URL-safe timed serializer behavior;
6. direct user documentation or bounded changelog notes about timestamped
   signing and expiration.

The oracle has 160 line-level items.

## Boundaries

Inspect only this task directory. Do not inspect oracle, score, result, or
itemset files outside this task directory.

Include only concrete `file_path:line` items. The file path must be relative to
this task root and should start with `repo/`, for example:

```json
{"file_path": "repo/src/itsdangerous/timed.py", "line": 141}
```

Do not include broad file-level answers. Do not include generic signing,
serializer, or URL-safe behavior unless the line directly concerns timestamped
signing or expiration.

## Suggested audit strategy

1. Inspect `repo/src/itsdangerous/timed.py`.
2. Inspect timestamp-related exceptions in `repo/src/itsdangerous/exc.py`.
3. Inspect timed URL-safe API and public exports.
4. Inspect `test_timed.py` and URL-safe timed tests.
5. Inspect `docs/timed.rst`, `docs/exceptions.rst`, `docs/url_safe.rst`,
   README, and bounded changelog notes.

## Output format

```json
{
  "run_id": "T6_G3_seed04_agent01",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {"file_path": "repo/src/itsdangerous/timed.py", "line": 141}
  ]
}
```
