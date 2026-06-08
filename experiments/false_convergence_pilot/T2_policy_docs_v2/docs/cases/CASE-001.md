# CASE-001 Payment Operations Note

case_id: CASE-001
service_id: svc-orbit-charge
flow: charge
state: production_active
source_section: north

Operator note: tenant is inferred from service catalog.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
