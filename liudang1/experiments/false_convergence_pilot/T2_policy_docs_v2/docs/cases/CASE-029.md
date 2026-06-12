# CASE-029 Payment Operations Note

case_id: CASE-029
service_id: svc-nova-charge
flow: charge
state: production_active
source_section: north

Operator note: rollover alias in catalog.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
