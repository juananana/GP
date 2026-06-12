# CASE-042 Payment Operations Note

case_id: CASE-042
service_id: svc-recheck
flow: fallback_queue
state: production_active
source_section: queues

Operator note: v2 topic distractor.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
