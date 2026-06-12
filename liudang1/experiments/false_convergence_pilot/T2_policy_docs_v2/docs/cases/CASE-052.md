# CASE-052 Payment Operations Note

case_id: CASE-052
service_id: svc-ap-refund
flow: charge
state: scheduled_replay
source_section: east

Operator note: boundary: refund-named service with scheduled charge.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
