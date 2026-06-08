# CASE-039 Payment Operations Note

case_id: CASE-039
service_id: svc-orbit-charge
flow: charge
state: scheduled_replay
source_section: north

Operator note: scheduled charge retry.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
