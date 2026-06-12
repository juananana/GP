from app.common.clients import LegacyAcmePayClient


def register_routes(router, settings):
    router.post("/webhooks/acmepay/v2/events", handle_current_event)
    router.post("/webhooks/acmepay/v1/events", handle_legacy_event)
    router.post(settings["legacy_webhook_path"], handle_legacy_event)


def handle_current_event(request):
    return {"ok": True, "version": "v2"}


def handle_legacy_event(request):
    return {"ok": True, "version": "v1"}


def replay_legacy_event(event, settings):
    client = LegacyAcmePayClient(settings["ACMEPAY_V1_BASE_URL"], settings["ACMEPAY_LEGACY_TOKEN"])
    return client.charge({"event_id": event.id})

