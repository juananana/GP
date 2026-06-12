# CASE-028 Payment Operations Note

case_id: CASE-028
service_id: svc-atlas-checkout
flow: refund
state: production_active
source_section: west

Operator note: stripe refund.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
