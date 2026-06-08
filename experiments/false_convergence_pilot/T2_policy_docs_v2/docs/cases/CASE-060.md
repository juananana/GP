# CASE-060 Payment Operations Note

case_id: CASE-060
service_id: svc-legacy-adjust
flow: charge
state: production_active
source_section: ops

Operator note: manual workflow distractor with target-looking flow.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
