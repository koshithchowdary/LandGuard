"""Safe provider registry. No undocumented portal endpoints or browser automation."""
from dataclasses import dataclass
from enum import Enum
from typing import Any


class AccessMode(str, Enum):
    NOT_CONNECTED = "not_connected"
    OWNER_UPLOAD = "owner_provided_document"
    OFFICIAL_API = "official_api"


@dataclass(frozen=True)
class ProviderStatus:
    key: str
    display_name: str
    state: str
    status: str
    access_mode: AccessMode
    portal_url: str
    note: str


PROVIDERS = {
    "ts_bhu_bharati": ProviderStatus(
        key="ts_bhu_bharati", display_name="Telangana Bhu Bharati", state="Telangana",
        status="blocked_government_access", access_mode=AccessMode.NOT_CONNECTED,
        portal_url="https://bhubharati.telangana.gov.in/homePage",
        note="No approved API credentials or change-feed documentation configured."
    ),
    "ap_meebhoomi_webland": ProviderStatus(
        key="ap_meebhoomi_webland", display_name="Andhra Pradesh MeeBhoomi / Webland", state="Andhra Pradesh",
        status="blocked_government_access", access_mode=AccessMode.NOT_CONNECTED,
        portal_url="http://meebhoomi.ap.gov.in/",
        note="No approved API credentials or change-feed documentation configured."
    ),
}


def provider_status() -> list[dict[str, Any]]:
    """Return honest connector status for a UI/admin page."""
    return [
        {
            "key": p.key, "display_name": p.display_name, "state": p.state,
            "status": p.status, "access_mode": p.access_mode.value,
            "portal_url": p.portal_url, "note": p.note,
            "live_monitoring": False,
        }
        for p in PROVIDERS.values()
    ]
