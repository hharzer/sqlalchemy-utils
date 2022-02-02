from collections.abc import Iterable
from datetime import datetime

import six

from ...exceptions import ImproperlyConfigured

arrow = None
try:
    import arrow
except ImportError:
    pass


class ArrowDateTime(object):
    def __init__(self):
        if not arrow:
            raise ImproperlyConfigured(
                "'arrow' package is required to use 'ArrowDateTime'"
            )

    def _coerce(self, impl, value):
        if (
            isinstance(value, six.string_types)
            or not isinstance(value, Iterable)
            and isinstance(value, datetime)
        ):
            value = arrow.get(value)
        elif isinstance(value, Iterable):
            value = arrow.get(*value)
        return value

    def process_bind_param(self, impl, value, dialect):
        if value:
            utc_val = self._coerce(impl, value).to('UTC')
            return utc_val.datetime\
                if impl.timezone else utc_val.naive
        return value

    def process_result_value(self, impl, value, dialect):
        return arrow.get(value) if value else value
