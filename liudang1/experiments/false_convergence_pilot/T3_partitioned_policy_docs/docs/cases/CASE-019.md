# CASE-019 Partitioned Operations Case

case_id: CASE-019
service_id: svc-nova-charge
flow: refund
state: production_active
override_id: XOV-101

Audit note: lane mismatch; exception override decides whether it counts.

Resolution requires checking the service catalog, adapter registry, lane policy,
and exception overrides. Do not decide from this case file alone.
