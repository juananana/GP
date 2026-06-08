# Appendix B: Adapter Resolution Notes

Follow aliases until a concrete processor, queue topic, sandbox, manual
entry, or current non-AcmePay processor is reached.

Adapter acmepay_v1_tenant_nova reaches AcmePay at https://nova.acmepay.local/v1.
Adapter acmepay_v1_tenant_orbit reaches AcmePay at https://orbit.acmepay.local/v1.
Adapter ap_refund_shadow is only an alias; it forwards to region_ap_legacy.
Adapter charge_fallback_topic publishes to topic acmepay.v1.charge.
Adapter current_recheck publishes to topic acmepay.v2.recheck.
Adapter eu_refund_shadow is only an alias; it forwards to region_eu_legacy.
Adapter ledger_replay_eu is only an alias; it forwards to region_eu_legacy.
Adapter manual_review is a manual workflow and has no processor endpoint.
Adapter nova_gateway is only an alias; it forwards to tenant_nova_rollover.
Adapter orbit_bridge is only an alias; it forwards to acmepay_v1_tenant_orbit.
Adapter refund_fallback_topic publishes to topic acmepay.v1.refund.
Adapter region_ap_legacy reaches AcmePay at https://ap.acmepay.local/v1.
Adapter region_eu_legacy reaches AcmePay at https://eu.acmepay.local/v1.
Adapter sandbox_acmepay is a sandbox-only AcmePay endpoint at https://sandbox.acmepay.local/v1.
Adapter stripe_current uses processor stripe at https://pay.example.local/v2.
Adapter tenant_nova_rollover is only an alias; it forwards to acmepay_v1_tenant_nova.
