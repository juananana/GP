TENANT_GATEWAYS = {
    "atlas": {"processor": "stripe", "base": "https://pay.example.local/v2"},
    "orbit": {"processor": "acmepay", "base": "https://orbit.acmepay.local/v1"},
    "nova": {"processor": "acmepay", "base": "https://nova.acmepay.local/v1"},
}

REGION_GATEWAYS = {
    "us-east": {"processor": "stripe", "base": "https://pay.example.local/v2"},
    "eu-west": {"processor": "acmepay", "base": "https://eu.acmepay.local/v1"},
    "ap-south": {"processor": "acmepay", "base": "https://ap.acmepay.local/v1"},
}

QUEUE_TOPICS = {
    "charge-fallback": "acmepay.v1.charge",
    "refund-fallback": "acmepay.v1.refund",
    "recheck-current": "acmepay.v2.recheck",
}


def tenant_gateway(tenant):
    return TENANT_GATEWAYS[tenant]


def regional_gateway(region):
    return REGION_GATEWAYS[region]


def topic_for(name):
    return QUEUE_TOPICS[name]

