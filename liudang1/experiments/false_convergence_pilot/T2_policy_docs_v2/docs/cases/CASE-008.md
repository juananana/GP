# CASE-008 Payment Operations Note

case_id: CASE-008
service_id: svc-orbit-charge
flow: charge
state: scheduled_replay
source_section: replay

Operator note: late retry path.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
