# CASE-054 Payment Operations Note

case_id: CASE-054
service_id: svc-fallback-charge
flow: refund
state: production_active
source_section: queues

Operator note: boundary: charge fallback adapter with refund flow.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
