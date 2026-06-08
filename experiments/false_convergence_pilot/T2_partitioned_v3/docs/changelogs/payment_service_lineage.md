# Payment Service Lineage Changelog

This memo is a narrative changelog, not a complete database dump. The
current lineage statements below are the authoritative service-to-adapter
links for the June retirement audit.

The service svc-ap-refund is currently routed through adapter ap_refund_shadow. Operations classify it as a refund lane.
The service svc-atlas-checkout is currently routed through adapter stripe_current. Operations classify it as a charge lane.
The service svc-eu-refund is currently routed through adapter eu_refund_shadow. Operations classify it as a refund lane.
The service svc-fallback-charge is currently routed through adapter charge_fallback_topic. Operations classify it as a queue lane.
The service svc-fallback-refund is currently routed through adapter refund_fallback_topic. Operations classify it as a queue lane.
The service svc-ledger-replay is currently routed through adapter ledger_replay_eu. Operations classify it as a replay lane.
The service svc-manual-adjust is currently routed through adapter manual_review. Operations classify it as a manual lane.
The service svc-nova-charge is currently routed through adapter nova_gateway. Operations classify it as a charge lane.
The service svc-orbit-charge is currently routed through adapter orbit_bridge. Operations classify it as a charge lane.
The service svc-recheck is currently routed through adapter current_recheck. Operations classify it as a queue lane.
The service svc-sandbox-pay is currently routed through adapter sandbox_acmepay. Operations classify it as a charge lane.
