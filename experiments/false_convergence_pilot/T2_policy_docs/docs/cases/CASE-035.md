# CASE-035 Payment Operations Note

case_id: CASE-035
service_id: svc-ledger-replay
flow: audit
state: scheduled_replay
source_section: replay

Operator note: wrong flow.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
