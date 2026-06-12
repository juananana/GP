# CASE-026 Payment Operations Note

case_id: CASE-026
service_id: svc-recheck
flow: replay
state: scheduled_replay
source_section: replay

Operator note: current v2 replay.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
