from app.common.clients import build_current_client, build_legacy_client


def reconcile_recent(batch, settings):
    client = build_current_client(settings)
    return [client.charge({"order_id": item.order_id}) for item in batch]


def reconcile_legacy_batch(batch, settings):
    client = build_legacy_client(settings)
    return [client.charge({"order_id": item.order_id}) for item in batch]


def enqueue_legacy_recheck(queue, order_id):
    queue.publish("acmepay.v1.recheck", {"order_id": order_id})


def enqueue_legacy_refund(queue, refund_id):
    topic = "acmepay" + ".v1" + ".refunds"
    queue.publish(topic, {"refund_id": refund_id})


def enqueue_current_recheck(queue, order_id):
    queue.publish("acmepay.v2.recheck", {"order_id": order_id})

