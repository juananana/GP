from app.runtime.gateway_registry import regional_gateway, tenant_gateway, topic_for
from app.runtime.http_gateway import build_gateway


def replay_orbit_charge(order):
    gateway = build_gateway(tenant_gateway("orbit"))
    return gateway.post("/charges/replay", {"order_id": order.id})


def replay_region_refund(refund):
    gateway = build_gateway(regional_gateway(refund.region))
    return gateway.post("/refunds/replay", {"refund_id": refund.id})


def requeue_refund(queue, refund_id):
    return queue.publish(topic_for("refund-fallback"), {"refund_id": refund_id})

