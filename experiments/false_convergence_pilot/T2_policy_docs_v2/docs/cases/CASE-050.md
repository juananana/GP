# CASE-050 Payment Operations Note

case_id: CASE-050
service_id: svc-orbit-charge
flow: refund
state: scheduled_replay
source_section: north

Operator note: boundary: charge-named service with scheduled refund.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
