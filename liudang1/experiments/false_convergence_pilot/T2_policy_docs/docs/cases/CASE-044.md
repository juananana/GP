# CASE-044 Payment Operations Note

case_id: CASE-044
service_id: svc-sandbox-pay
flow: charge
state: hold
source_section: sandbox

Operator note: sandbox and held.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
