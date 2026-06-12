# CASE-022 Payment Operations Note

case_id: CASE-022
service_id: svc-orbit-charge
flow: charge
state: production_active
source_section: north

Operator note: same service, another region batch.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
