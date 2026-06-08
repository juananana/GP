# CASE-006 Payment Operations Note

case_id: CASE-006
service_id: svc-fallback-refund
flow: fallback_queue
state: production_active
source_section: queues

Operator note: topic is resolved by queue adapter.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
