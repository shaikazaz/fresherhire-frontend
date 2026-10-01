import json
import os
import urllib.error
import urllib.request

from django.conf import settings

from .models import CrmSyncLog


HUBSPOT_URL = "https://api.hubapi.com/crm/v3/objects/contacts"


def sync_user_to_hubspot(user):
    """Create/update a HubSpot contact and always record the attempt locally.

    If HUBSPOT_ACCESS_TOKEN is not configured, the signup is logged as skipped.
    The signup itself is never blocked by a CRM outage.
    """
    token = os.getenv("HUBSPOT_ACCESS_TOKEN", "").strip()
    if not token:
        return _log(user, "skipped", "", "HUBSPOT_ACCESS_TOKEN is not configured.")

    payload = {
        "properties": {
            "email": user.email,
            "firstname": user.full_name or "",
            "lifecyclestage": "lead",
        }
    }
    request = urllib.request.Request(
        HUBSPOT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body or "{}")
            return _log(user, "success", str(data.get("id", "")), body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return _log(user, "failed", "", body)
    except Exception as exc:
        return _log(user, "failed", "", str(exc))


def _log(user, status, contact_id, response):
    return CrmSyncLog.objects.create(
        user=user,
        status=status,
        crm_contact_id=contact_id,
        response=response[:10000],
    )
