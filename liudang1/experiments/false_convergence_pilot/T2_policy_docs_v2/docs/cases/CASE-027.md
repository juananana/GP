# CASE-027 Payment Operations Note

case_id: CASE-027
service_id: svc-sandbox-pay
flow: replay
state: scheduled_replay
source_section: sandbox

Operator note: sandbox replay.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
