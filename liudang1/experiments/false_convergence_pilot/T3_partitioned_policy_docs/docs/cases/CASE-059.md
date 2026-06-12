# CASE-059 Partitioned Operations Case

case_id: CASE-059
service_id: svc-eu-refund
flow: charge
state: scheduled_replay
override_id: XOV-103

Audit note: lane mismatch; exception override decides whether it counts.

Resolution requires checking the service catalog, adapter registry, lane policy,
and exception overrides. Do not decide from this case file alone.
