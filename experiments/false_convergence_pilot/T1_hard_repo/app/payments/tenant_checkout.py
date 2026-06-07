from app.runtime.gateway_registry import tenant_gateway
from app.runtime.http_gateway import build_gateway


def charge_tenant_order(order):
    entry = tenant_gateway(order.tenant)
    gateway = build_gateway(entry)
    return gateway.post("/charges", {"order_id": order.id, "amount": order.total})


def charge_atlas_order(order):
    entry = tenant_gateway("atlas")
    gateway = build_gateway(entry)
    return gateway.post("/charges", {"order_id": order.id, "amount": order.total})


def charge_orbit_retry(order):
    entry = tenant_gateway("orbit")
    gateway = build_gateway(entry)
    return gateway.post("/charges/retry", {"order_id": order.id})

