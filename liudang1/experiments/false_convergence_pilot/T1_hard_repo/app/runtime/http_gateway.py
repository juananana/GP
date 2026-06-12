class HttpGateway:
    def __init__(self, base):
        self.base = base.rstrip("/")

    def post(self, suffix, payload):
        return {"url": self.base + suffix, "payload": payload}


def build_gateway(entry):
    return HttpGateway(entry["base"])

