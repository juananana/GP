# Service Catalog

- service_id: svc-ap-refund; adapter_id: ap_refund_shadow; lane: refund
- service_id: svc-atlas-checkout; adapter_id: stripe_current; lane: charge
- service_id: svc-eu-refund; adapter_id: eu_refund_shadow; lane: refund
- service_id: svc-fallback-charge; adapter_id: charge_fallback_topic; lane: queue
- service_id: svc-fallback-refund; adapter_id: refund_fallback_topic; lane: queue
- service_id: svc-ledger-replay; adapter_id: ledger_replay_eu; lane: replay
- service_id: svc-manual-adjust; adapter_id: manual_review; lane: manual
- service_id: svc-nova-charge; adapter_id: nova_gateway; lane: charge
- service_id: svc-orbit-charge; adapter_id: orbit_bridge; lane: charge
- service_id: svc-recheck; adapter_id: current_recheck; lane: queue
- service_id: svc-sandbox-pay; adapter_id: sandbox_acmepay; lane: charge
