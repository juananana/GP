# CASE-034 Payment Operations Note

case_id: CASE-034
service_id: svc-fallback-charge
flow: fallback_queue
state: canary
source_section: queues

Operator note: canary queue should be excluded.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
