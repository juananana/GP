# CASE-014 Payment Operations Note

case_id: CASE-014
service_id: svc-recheck
flow: fallback_queue
state: production_active
source_section: queues

Operator note: acmepay v2 recheck is not legacy v1.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
