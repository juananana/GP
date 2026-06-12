# CASE-048 Payment Operations Note

case_id: CASE-048
service_id: svc-orbit-charge
flow: refund
state: production_active
source_section: north

Operator note: adapter is legacy; flow is refund but service is charge pipeline.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
