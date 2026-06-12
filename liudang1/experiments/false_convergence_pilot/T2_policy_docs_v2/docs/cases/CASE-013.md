# CASE-013 Payment Operations Note

case_id: CASE-013
service_id: svc-atlas-checkout
flow: charge
state: production_active
source_section: north

Operator note: current stripe path.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
