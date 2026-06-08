# CASE-058 Payment Operations Note

case_id: CASE-058
service_id: svc-recheck
flow: refund
state: production_active
source_section: queues

Operator note: v2 topic distractor with target-looking flow.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
