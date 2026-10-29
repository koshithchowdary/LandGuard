"""Notification provider interfaces. Delivery is disabled until real providers are configured."""
from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ChannelStatus:
    channel: str
    configured: bool
    status: str
    required_env: tuple[str, ...]


def channel_status() -> list[dict[str, object]]:
    definitions = [
        ("email", ("LANDGUARD_EMAIL_PROVIDER", "LANDGUARD_EMAIL_API_KEY", "LANDGUARD_EMAIL_FROM")),
        ("sms", ("LANDGUARD_SMS_PROVIDER", "LANDGUARD_SMS_API_KEY", "LANDGUARD_SMS_SENDER_ID")),
        ("whatsapp", ("LANDGUARD_WHATSAPP_PROVIDER", "LANDGUARD_WHATSAPP_API_KEY", "LANDGUARD_WHATSAPP_SENDER_ID")),
    ]
    result = []
    for channel, keys in definitions:
        configured = all(os.getenv(k, "").strip() for k in keys)
        result.append({
            "channel": channel, "configured": configured,
            "status": "configured_not_delivery_tested" if configured else "not_configured",
            "required_env": list(keys),
            "note": "No message is sent by this module; implement provider SDK and consent checks before enabling delivery.",
        })
    return result
