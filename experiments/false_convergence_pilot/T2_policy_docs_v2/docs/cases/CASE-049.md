# CASE-049 Payment Operations Note

case_id: CASE-049
service_id: svc-nova-charge
flow: refund
state: production_active
source_section: north

Operator note: boundary: charge-named service with refund flow.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
