# CASE-002 Payment Operations Note

case_id: CASE-002
service_id: svc-nova-charge
flow: charge
state: production_active
source_section: north

Operator note: adapter resolves through a rollover alias.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
