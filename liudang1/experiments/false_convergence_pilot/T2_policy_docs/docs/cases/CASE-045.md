# CASE-045 Payment Operations Note

case_id: CASE-045
service_id: svc-legacy-adjust
flow: replay
state: scheduled_replay
source_section: ops

Operator note: manual replay, no adapter.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
