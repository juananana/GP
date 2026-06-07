from app.common.clients import LegacyAcmePayClient, build_current_client, build_legacy_client


def charge_checkout(order, settings):
    client = build_current_client(settings)
    return client.charge({"order_id": order.id, "amount": order.total})


def charge_legacy_checkout(order, settings):
    client = build_legacy_client(settings)
    return client.charge({"order_id": order.id, "amount": order.total})


def charge_partner_checkout(order, settings):
    partner = LegacyAcmePayClient(settings["partner_v1_base"], settings["partner_token"])
    return partner.charge({"order_id": order.id, "amount": order.total})


def charge_split_checkout(order, http):
    version = "v1"
    path = "/acmepay/" + version + "/charges"
    return http.post(path, json={"order_id": order.id, "amount": order.total})


def charge_feature_flagged(order, settings, http):
    if settings.get("use_legacy_acmepay"):
        return http.post(settings["ACMEPAY_V1_BASE_URL"] + "/charges", json={"order_id": order.id})
    return http.post(settings["ACMEPAY_BASE_URL"] + "/charges", json={"order_id": order.id})

