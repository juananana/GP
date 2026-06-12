from app.common.clients import LegacyAcmePayClient, build_legacy_client


def audit_legacy_charges(settings, orders):
    client = build_legacy_client(settings)
    return [client.charge({"order_id": order.id}) for order in orders]


def replay_legacy_refunds(settings, refunds):
    client = LegacyAcmePayClient(settings["ACMEPAY_V1_BASE_URL"], settings["ACMEPAY_LEGACY_TOKEN"])
    return [client.refund({"refund_id": refund.id}) for refund in refunds]


def ping_legacy_health(http, settings):
    return http.get(settings["ACMEPAY_V1_BASE_URL"] + "/health")

