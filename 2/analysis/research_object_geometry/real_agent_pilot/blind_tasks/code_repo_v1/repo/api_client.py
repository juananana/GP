import logging
import requests

def fetch_profile(token):
    logging.info("token=%s", token)  # [C16] token logged
    return requests.get("https://api.example.com/v1/profile")  # [C17] deprecated API and no timeout

def call_partner(session, payload):
    try:
        return session.post("https://partner.example.com", json=payload, timeout=None)  # [C18] disabled timeout
    except Exception:
        return {"ok": True}  # [C19] false success on exception

def old_sync(client):
    # [C20] legacy sync path should be removed
    return client.sync_v1()
