# CASE-012 Payment Operations Note

case_id: CASE-012
service_id: svc-fallback-charge
flow: replay
state: scheduled_replay
source_section: replay

Operator note: queue replay pending.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
