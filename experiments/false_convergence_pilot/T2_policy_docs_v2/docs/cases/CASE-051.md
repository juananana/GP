# CASE-051 Payment Operations Note

case_id: CASE-051
service_id: svc-eu-refund
flow: charge
state: production_active
source_section: west

Operator note: boundary: refund-named service with charge flow.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
