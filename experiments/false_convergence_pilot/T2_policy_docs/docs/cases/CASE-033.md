# CASE-033 Payment Operations Note

case_id: CASE-033
service_id: svc-fallback-refund
flow: fallback_queue
state: hold
source_section: queues

Operator note: held queue should be excluded.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
