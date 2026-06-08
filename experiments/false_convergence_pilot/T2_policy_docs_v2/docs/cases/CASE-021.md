# CASE-021 Payment Operations Note

case_id: CASE-021
service_id: svc-ap-refund
flow: refund
state: production_active
source_section: east

Operator note: same service, different source section.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
