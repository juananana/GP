# CASE-055 Payment Operations Note

case_id: CASE-055
service_id: svc-fallback-refund
flow: charge
state: production_active
source_section: queues

Operator note: boundary: refund fallback adapter with charge flow.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
