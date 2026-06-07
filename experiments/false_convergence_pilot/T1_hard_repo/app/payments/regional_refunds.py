from app.runtime.gateway_registry import regional_gateway
from app.runtime.http_gateway import build_gateway


def refund_by_region(refund):
    entry = regional_gateway(refund.region)
    gateway = build_gateway(entry)
    return gateway.post("/refunds", {"refund_id": refund.id})


def refund_us_east(refund):
    entry = regional_gateway("us-east")
    gateway = build_gateway(entry)
    return gateway.post("/refunds", {"refund_id": refund.id})


def refund_eu_manual(refund):
    entry = regional_gateway("eu-west")
    gateway = build_gateway(entry)
    return gateway.post("/refunds/manual", {"refund_id": refund.id})

