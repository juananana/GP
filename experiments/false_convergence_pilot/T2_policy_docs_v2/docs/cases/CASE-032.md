# CASE-032 Payment Operations Note

case_id: CASE-032
service_id: svc-orbit-charge
flow: charge
state: production_active
source_section: north

Operator note: tenant checkout charge.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
