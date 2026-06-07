# CASE-031 Payment Operations Note

case_id: CASE-031
service_id: svc-ap-refund
flow: refund
state: scheduled_replay
source_section: east

Operator note: scheduled regional replay.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
