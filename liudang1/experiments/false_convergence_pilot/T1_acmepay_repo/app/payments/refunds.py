from app.common.clients import LegacyAcmePayClient, client_from_region


def refund_current(refund, settings):
    client = client_from_region(settings, "us-east")
    return client.refund({"refund_id": refund.id})


def refund_legacy_manual(refund, settings):
    client = LegacyAcmePayClient(settings["ACMEPAY_V1_BASE_URL"], settings["ACMEPAY_LEGACY_TOKEN"])
    return client.refund({"refund_id": refund.id})


def refund_by_endpoint(refund, http):
    return http.post("/acmepay/v1/refunds", json={"refund_id": refund.id})


def refund_by_region(refund, settings):
    client = client_from_region(settings, refund.region)
    return client.refund({"refund_id": refund.id, "region": refund.region})


def refund_partner_portal(refund, settings, http):
    base = settings["partner_v1_base"].rstrip("/")
    return http.post(f"{base}/refunds", json={"refund_id": refund.id})

