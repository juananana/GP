# CASE-053 Payment Operations Note

case_id: CASE-053
service_id: svc-ledger-replay
flow: refund
state: production_active
source_section: replay

Operator note: boundary: replay service with refund flow.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
