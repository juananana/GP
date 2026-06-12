# CASE-056 Payment Operations Note

case_id: CASE-056
service_id: svc-nova-charge
flow: fallback_queue
state: production_active
source_section: queues

Operator note: boundary: tenant adapter with queue flow.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
