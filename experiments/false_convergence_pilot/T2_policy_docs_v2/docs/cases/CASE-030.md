# CASE-030 Payment Operations Note

case_id: CASE-030
service_id: svc-eu-refund
flow: refund
state: production_active
source_section: west

Operator note: shadow refund path.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
