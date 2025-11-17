# notifications/utils.py
from firebase_admin import messaging
from django.conf import settings
from datetime import datetime
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

CITY_TOPIC_MAP: Dict[str, str] = {
    # Захардкоженные соответствия городов и FCM топиков
    # Ключи и значения — пример; отредактируйте по нужным названиям ваших топиков
    'nookat': 'all_users',
    'kyzylkya': 'kyzylkya',
    'kadamjai': 'kadamjai',
}

def _topic_for_city(city: Optional[str]) -> str:
    if not city:
        return 'all_users'
    key = city.strip().lower()
    return CITY_TOPIC_MAP.get(key, 'all_users')

def send_notification_to_all(title: str, body: str, data: Optional[Dict[str, Any]] = None, city: Optional[str] = None):
    """
    Отправляет нотификацию на топик, зависящий от города.
    Если город не задан или не найден в карте, отправляет на 'all_users'.
    """
    topic = _topic_for_city(city)
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
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(aps=messaging.Aps(category='POOL'))
        ),
        topic=topic,
        data=data or {}
    )

    try:
        response = messaging.send(message)
        logger.info(f"FCM send response: {response} (topic={topic})")
        return response
    except Exception:
        logger.exception("Failed to send FCM message")
        raise
