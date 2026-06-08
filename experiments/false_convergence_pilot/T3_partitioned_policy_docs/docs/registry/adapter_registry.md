# Adapter Registry

- adapter_id: acmepay_v1_tenant_nova; processor=acmepay, base=https://nova.acmepay.local/v1
- adapter_id: acmepay_v1_tenant_orbit; processor=acmepay, base=https://orbit.acmepay.local/v1
- adapter_id: ap_refund_shadow; processor=alias, alias_for=region_ap_legacy
- adapter_id: charge_fallback_topic; processor=queue, topic=acmepay.v1.charge
- adapter_id: current_recheck; processor=queue, topic=acmepay.v2.recheck
- adapter_id: eu_refund_shadow; processor=alias, alias_for=region_eu_legacy
- adapter_id: ledger_replay_eu; processor=alias, alias_for=region_eu_legacy
- adapter_id: manual_review; processor=manual, base=n/a
- adapter_id: nova_gateway; processor=alias, alias_for=tenant_nova_rollover
- adapter_id: orbit_bridge; processor=alias, alias_for=acmepay_v1_tenant_orbit
- adapter_id: refund_fallback_topic; processor=queue, topic=acmepay.v1.refund
- adapter_id: region_ap_legacy; processor=acmepay, base=https://ap.acmepay.local/v1
- adapter_id: region_eu_legacy; processor=acmepay, base=https://eu.acmepay.local/v1
- adapter_id: sandbox_acmepay; processor=sandbox, base=https://sandbox.acmepay.local/v1
- adapter_id: stripe_current; processor=stripe, base=https://pay.example.local/v2
- adapter_id: tenant_nova_rollover; processor=alias, alias_for=acmepay_v1_tenant_nova
