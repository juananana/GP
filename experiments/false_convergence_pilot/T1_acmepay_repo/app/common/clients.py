class AcmePayClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def charge(self, payload):
        return {"endpoint": f"{self.base_url}/charges", "payload": payload}

    def refund(self, payload):
        return {"endpoint": f"{self.base_url}/refunds", "payload": payload}


class LegacyAcmePayClient(AcmePayClient):
    pass


def build_current_client(settings):
    return AcmePayClient(settings["ACMEPAY_BASE_URL"], settings["ACMEPAY_TOKEN"])


def build_legacy_client(settings):
    return LegacyAcmePayClient(settings["ACMEPAY_V1_BASE_URL"], settings["ACMEPAY_LEGACY_TOKEN"])


def client_from_region(settings, region):
    if region in settings.get("legacy_regions", []):
        return LegacyAcmePayClient(settings["regional"][region]["base_v1"], settings["regional"][region]["token"])
    return build_current_client(settings)

