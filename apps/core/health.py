import logging
from typing import Dict, List, Optional

from django.conf import settings

logger = logging.getLogger(__name__)


class HealthCheckResult:
    def __init__(self, name: str, status: bool, message: str = '', details: Dict = None):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}

    @property
    def is_healthy(self) -> bool:
        return self.status

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'status': 'healthy' if self.status else 'unhealthy',
            'message': self.message,
            'details': self.details,
        }


class HealthCheck:
    def __init__(self):
        self.checks: List[HealthCheckResult] = []

    def add_check(self, name: str, status: bool, message: str = '', details: Dict = None):
        self.checks.append(HealthCheckResult(name, status, message, details))

    @property
    def is_healthy(self) -> bool:
        return all(check.is_healthy for check in self.checks)

    def to_dict(self) -> Dict:
        return {
            'status': 'healthy' if self.is_healthy else 'unhealthy',
            'checks': [check.to_dict() for check in self.checks],
        }


class DatabaseHealthCheck:
    name = 'database'

    def check(self) -> HealthCheckResult:
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            return HealthCheckResult(self.name, True, 'Database connection successful')
        except Exception as e:
            return HealthCheckResult(self.name, False, str(e))


class CacheHealthCheck:
    name = 'cache'

    def check(self) -> HealthCheckResult:
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 10)
            value = cache.get('health_check')
            if value == 'ok':
                return HealthCheckResult(self.name, True, 'Cache is working')
            return HealthCheckResult(self.name, False, 'Cache returned unexpected value')
        except Exception as e:
            return HealthCheckResult(self.name, False, str(e))


class RedisHealthCheck:
    name = 'redis'

    def check(self) -> HealthCheckResult:
        try:
            import redis
            from django.conf import settings
            redis_url = settings.CELERY_BROKER_URL
            r = redis.from_url(redis_url)
            r.ping()
            return HealthCheckResult(self.name, True, 'Redis connection successful')
        except Exception as e:
            return HealthCheckResult(self.name, False, str(e))


class CeleryHealthCheck:
    name = 'celery'

    def check(self) -> HealthCheckResult:
        try:
            from config.celery import app
            inspector = app.control.inspect()
            stats = inspector.stats()
            if stats:
                return HealthCheckResult(self.name, True, 'Celery is running', {'workers': len(stats)})
            return HealthCheckResult(self.name, False, 'No active Celery workers')
        except Exception as e:
            return HealthCheckResult(self.name, False, str(e))


class DiskSpaceHealthCheck:
    name = 'disk_space'

    def check(self) -> HealthCheckResult:
        try:
            import shutil
            usage = shutil.disk_usage('/')
            percent_used = (usage.used / usage.total) * 100
            threshold = getattr(settings, 'HEALTH_CHECK', {}).get('DISK_USAGE_MAX', 90)
            if percent_used < threshold:
                return HealthCheckResult(
                    self.name, True, 'Disk space is adequate',
                    {'percent_used': round(percent_used, 2)}
                )
            return HealthCheckResult(
                self.name, False, 'Disk space is low',
                {'percent_used': round(percent_used, 2)}
            )
        except Exception as e:
            return HealthCheckResult(self.name, False, str(e))


def run_health_checks() -> Dict:
    health = HealthCheck()

    checks = [
        DatabaseHealthCheck(),
        CacheHealthCheck(),
        RedisHealthCheck(),
        CeleryHealthCheck(),
        DiskSpaceHealthCheck(),
    ]

    for check in checks:
        try:
            result = check.check()
        except Exception as e:
            result = HealthCheckResult(check.name, False, str(e))
        health.add_check(result.name, result.status, result.message, result.details)

    return health.to_dict()
