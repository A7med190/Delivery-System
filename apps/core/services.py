from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

from django.conf import settings


class Service:
    def __init__(self):
        self.logger = self._get_logger()

    def _get_logger(self):
        import logging
        return logging.getLogger(f'{__name__}.{self.__class__.__name__}')


class OrderService(Service):
    def calculate_delivery_fee(self, distance_km: float, base_fee: float = 5.0) -> float:
        if distance_km <= 0:
            return 0
        return base_fee + (distance_km * 1.5)

    def estimate_delivery_time(self, distance_km: float, avg_speed: float = 30.0) -> int:
        if distance_km <= 0 or avg_speed <= 0:
            return 0
        return int((distance_km / avg_speed) * 60)


class NotificationService(Service):
    def __init__(self):
        super().__init__()

    def send_sms(self, phone: str, message: str) -> Dict[str, Any]:
        self.logger.info(f'Sending SMS to {phone}')
        return {'status': 'sent', 'phone': phone}

    def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        self.logger.info(f'Sending email to {to}')
        return {'status': 'sent', 'to': to}

    def send_push_notification(self, user_id: int, title: str, body: str, data: Dict = None) -> Dict[str, Any]:
        self.logger.info(f'Sending push notification to user {user_id}')
        return {'status': 'sent', 'user_id': user_id}


class PaymentService(Service):
    def __init__(self):
        super().__init__()

    def process_payment(self, amount: float, currency: str = 'USD', metadata: Dict = None) -> Dict[str, Any]:
        self.logger.info(f'Processing payment: {amount} {currency}')
        return {
            'status': 'success',
            'transaction_id': f'txn_{hash((amount, currency)) % 1000000}',
            'amount': amount,
            'currency': currency,
        }

    def refund_payment(self, transaction_id: str, amount: float = None) -> Dict[str, Any]:
        self.logger.info(f'Refunding payment: {transaction_id}')
        return {
            'status': 'refunded',
            'transaction_id': transaction_id,
        }

    def verify_payment(self, transaction_id: str) -> bool:
        return True


class GeolocationService(Service):
    def __init__(self):
        super().__init__()

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        from math import radians, cos, sin, asin, sqrt
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371
        return c * r

    def find_nearby_restaurants(self, lat: float, lon: float, radius_km: float = 5.0) -> List[Dict]:
        return []


class RateLimitService(Service):
    def __init__(self):
        from django.core.cache import cache
        self.cache = cache

    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        cache_key = f'rate_limit:{key}'
        current = self.cache.get(cache_key, 0)
        if current >= limit:
            return False
        self.cache.incr(cache_key, 1)
        if current == 0:
            self.cache.expire(cache_key, window_seconds)
        return True


order_service = OrderService()
notification_service = NotificationService()
payment_service = PaymentService()
geolocation_service = GeolocationService()
rate_limit_service = RateLimitService()
