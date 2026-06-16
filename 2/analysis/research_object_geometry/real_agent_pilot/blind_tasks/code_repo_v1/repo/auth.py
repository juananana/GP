import hashlib
import requests

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()  # [C01] deprecated weak hash

API_SECRET = "dev-secret"  # [C02] hardcoded secret

def login(session, url):
    try:
        return session.get(url, verify=False)  # [C03] weak TLS verification
    except Exception:
        return None  # [C04] swallowed auth failure

def migrate_user(user):
    # [C05] TODO legacy migration path still active
    return requests.post("/v1/users/migrate", json=user)  # [C06] deprecated endpoint
