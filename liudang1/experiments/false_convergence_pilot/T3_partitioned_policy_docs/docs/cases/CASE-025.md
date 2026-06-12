# CASE-025 Partitioned Operations Case

case_id: CASE-025
service_id: svc-fallback-refund
flow: charge
state: production_active
override_id: XOV-107

Audit note: lane mismatch; exception override decides whether it counts.

Resolution requires checking the service catalog, adapter registry, lane policy,
and exception overrides. Do not decide from this case file alone.
