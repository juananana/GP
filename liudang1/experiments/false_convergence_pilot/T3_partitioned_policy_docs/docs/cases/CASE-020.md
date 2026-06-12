# CASE-020 Partitioned Operations Case

case_id: CASE-020
service_id: svc-orbit-charge
flow: refund
state: production_active
override_id: XOV-102

Audit note: lane mismatch; exception override decides whether it counts.

Resolution requires checking the service catalog, adapter registry, lane policy,
and exception overrides. Do not decide from this case file alone.
