# CASE-018 Payment Operations Note

case_id: CASE-018
service_id: svc-west-invoice
flow: invoice
state: production_active
source_section: west

Operator note: non-payment flow.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
