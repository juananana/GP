# CASE-033 Partitioned Operations Case

case_id: CASE-033
service_id: svc-fallback-refund
flow: charge
state: production_active
override_id: XOV-207

Audit note: lane mismatch; similar to required overrides but explicitly excluded.

Resolution requires checking the service catalog, adapter registry, lane policy,
and exception overrides. Do not decide from this case file alone.
