# CASE-016 Payment Operations Note

case_id: CASE-016
service_id: svc-orbit-charge
flow: charge
state: hold
source_section: north

Operator note: held rollout should be excluded.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
