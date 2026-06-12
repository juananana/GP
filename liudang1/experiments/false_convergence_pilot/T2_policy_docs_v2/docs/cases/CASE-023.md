# CASE-023 Payment Operations Note

case_id: CASE-023
service_id: svc-fallback-charge
flow: fallback_queue
state: production_active
source_section: queues

Operator note: retry topic through fallback adapter.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
