from __future__ import annotations

from ..db import (
    list_notifications_for_recipient,
    mark_notification_read,
)


def list_notifications_service(account: dict) -> list[dict]:
    return list_notifications_for_recipient(account["id"])


def mark_notification_read_service(
    account: dict,
    notification_id: int,
) -> None:
    if not mark_notification_read(notification_id, account["id"]):
        raise LookupError("Notification not found.")
