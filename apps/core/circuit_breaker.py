import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CircuitBreakerOpen(Exception):
    pass


class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = 'closed'

    @property
    def _cache_key(self) -> str:
        return f'circuit_breaker:{self.name}'

    def _load_state(self) -> None:
        state = cache.get(self._cache_key)
        if state:
            self.failure_count = state.get('failure_count', 0)
            self.last_failure_time = state.get('last_failure_time')
            self.state = state.get('state', 'closed')

    def _save_state(self) -> None:
        cache.set(
            self._cache_key,
            {
                'failure_count': self.failure_count,
                'last_failure_time': self.last_failure_time,
                'state': self.state,
            },
            timeout=self.recovery_timeout * 2,
        )

    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == 'open':
            import time
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed < self.recovery_timeout:
                    raise CircuitBreakerOpen(f'Circuit breaker {self.name} is OPEN')
                self.state = 'half-open'
                self._save_state()

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _on_success(self) -> None:
        if self.state == 'half-open':
            self.state = 'closed'
            self.failure_count = 0
            self._save_state()
            logger.info(f'Circuit breaker {self.name} reset to CLOSED')

    def _on_failure(self) -> None:
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
            logger.warning(f'Circuit breaker {self.name} opened after {self.failure_count} failures')
        else:
            self.state = 'half-open' if self.state == 'half-open' else 'closed'

        self._save_state()

    def reset(self) -> None:
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'
        cache.delete(self._cache_key)


_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str,
    failure_threshold: Optional[int] = None,
    recovery_timeout: Optional[int] = None,
    expected_exception: Type[Exception] = Exception,
) -> CircuitBreaker:
    if name not in _circuit_breakers:
        config = getattr(settings, 'CIRCUIT_BREAKER', {})
        _circuit_breakers[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold or config.get('FAILURE_THRESHOLD', 5),
            recovery_timeout=recovery_timeout or config.get('RECOVERY_TIMEOUT', 60),
            expected_exception=expected_exception,
        )
    return _circuit_breakers[name]


def circuit_breaker(
    name: str,
    failure_threshold: Optional[int] = None,
    recovery_timeout: Optional[int] = None,
    expected_exception: Type[Exception] = Exception,
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            breaker = get_circuit_breaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                expected_exception=expected_exception,
            )
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator
