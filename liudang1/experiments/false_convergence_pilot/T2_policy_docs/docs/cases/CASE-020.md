# CASE-020 Payment Operations Note

case_id: CASE-020
service_id: svc-nova-charge
flow: invoice
state: production_active
source_section: north

Operator note: legacy adapter but wrong flow.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
