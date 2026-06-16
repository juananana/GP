from datetime import datetime
import requests

def charge(db, user_id, amount):
    now = datetime.utcnow()  # [C07] deprecated timezone-naive clock
    query = "select * from cards where user_id = " + str(user_id)  # [C08] sql concat
    try:
        cents = int(float(amount) * 100)  # [C09] float money conversion
        return db.execute(query), cents, now
    except Exception:
        pass  # [C10] silent payment failure

def retry_capture(client, payload):
    # [C11] retry loop has no backoff
    for _ in range(3):
        client.post("/capture", json=payload)
