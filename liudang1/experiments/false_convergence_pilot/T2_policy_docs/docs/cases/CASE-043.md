# CASE-043 Payment Operations Note

case_id: CASE-043
service_id: svc-atlas-checkout
flow: charge
state: scheduled_replay
source_section: north

Operator note: stripe scheduled retry.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
