# notifications/utils.py
from firebase_admin import messaging
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def send_notification_to_all(title: str, body: str, data: dict | None = None):
    """
    Отправляет нотификацию на топик 'all_users'
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                click_action='FLUTTER_NOTIFICATION_CLICK'
            ),
        ),
        apns=messaging.APNSConfig(  # iOS (на будущее)
            payload=messaging.APNSPayload(aps=messaging.Aps(category='POOL'))
        ),
        topic='all_users',
        data=data or {}
    )

    try:
        response = messaging.send(message)
        logger.info(f"FCM send response: {response}")
        return response
    except Exception as e:
        logger.exception("Failed to send FCM message")
        raise
