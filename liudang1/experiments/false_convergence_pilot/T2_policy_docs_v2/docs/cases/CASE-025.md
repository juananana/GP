# CASE-025 Payment Operations Note

case_id: CASE-025
service_id: svc-ledger-replay
flow: replay
state: scheduled_replay
source_section: replay

Operator note: ledger batch replay.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
