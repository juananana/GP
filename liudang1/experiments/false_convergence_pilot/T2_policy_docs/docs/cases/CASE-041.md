# CASE-041 Payment Operations Note

case_id: CASE-041
service_id: svc-fallback-refund
flow: fallback_queue
state: production_active
source_section: queues

Operator note: refund queue batch.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
