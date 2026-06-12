from app.runtime.gateway_registry import topic_for


def enqueue_charge_fallback(queue, order_id):
    topic = topic_for("charge-fallback")
    return queue.publish(topic, {"order_id": order_id})


def enqueue_refund_fallback(queue, refund_id):
    topic = topic_for("refund-fallback")
    return queue.publish(topic, {"refund_id": refund_id})


def enqueue_current_recheck(queue, order_id):
    topic = topic_for("recheck-current")
    return queue.publish(topic, {"order_id": order_id})

