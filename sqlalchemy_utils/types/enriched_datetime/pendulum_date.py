from ...exceptions import ImproperlyConfigured
from .pendulum_datetime import PendulumDateTime

pendulum = None
try:
    import pendulum
except ImportError:
    pass


class PendulumDate(PendulumDateTime):
    def __init__(self):
        if not pendulum:
            raise ImproperlyConfigured(
                "'pendulum' package is required to use 'PendulumDate'"
            )

    def _coerce(self, impl, value):
        if value and not isinstance(value, pendulum.Date):
            value = super(PendulumDate, self)._coerce(impl, value).date()
        return value

    def process_result_value(self, impl, value, dialect):
        return pendulum.parse(value.isoformat()).date() if value else value

    def process_bind_param(self, impl, value, dialect):
        return self._coerce(impl, value) if value else value
