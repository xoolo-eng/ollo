from .base import Validate
from .utils import isunsignedint
from datetime import datetime, date


class StringField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._max_length = None
        if kwargs.get("max_length"):
            if isunsignedint(kwargs.get("max_length")):
                self._max_length = kwargs["max_length"]
            else:
                raise ValueError("<max_length>: expected int value greater than zero")

    def validate(self, instance, value=None):
        self._check_type(value, str)
        if self._max_length and value is not None:
            if len(value) > self._max_length:
                raise ValueError(
                    f"Length of value <{self.storage_name}> "
                    "mast be in range (0 < value <= max_length)"
                )
        # return value
        return self._check_default(value, str)


class SymbolField(StringField):
    """
    For symbol type.
    Not implementation.
    Full copy StringField.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IntegerField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, int)
        # return value
        return self._check_default(value, int)


class FooatField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, float)
        # return value
        return self._check_default(value, float)


class BooleanField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, bool)
        # return value
        return self._check_default(value, bool)


class ArrayField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, list)
        # return value
        return self._check_default(value, list)


class ObjectField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, dict)
        # return value
        return self._check_default(value, dict)


class BinaryDataField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("max_length"):
            if isunsignedint(kwargs.get("max_length")):
                self._max_length = kwargs["max_length"]
            else:
                raise ValueError("<max_length>: expected int value greater than zero")

    def validate(self, instance, value=None):
        self._check_type(value, bytes)
        if self._max_length and value is not None:
            if len(value) > self._max_length:
                raise ValueError(
                    f"Length of value <{self.storage_name}> "
                    "mast be in range (0 < value <= max_length)"
                )
        # return value
        return self._check_default(value, bytes)


class DateField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._to_date = True
        self._format = "%d-%m-%Y"
        if kwargs.get("to_date"):
            self._to_date = bool(kwargs["to_date"])
        if kwargs.get("format"):
            self._format = kwargs["format"]

    def validate(self, instance, value):
        if self._to_date:
            value = datetime.strptime(value, self._format).date()
        self._check_type(value, date)
        # return value
        return self._check_default(value, date)


class DataTimeField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._to_date = True
        self._format = "%d-%m-%Y %H:%M:%S"
        if kwargs.get("to_date"):
            self._to_date = bool(kwargs["to_date"])
        if kwargs.get("format"):
            self._format = kwargs["format"]

    def validate(self, instance, value):
        if self._to_date:
            value = datetime.strptime(value, self._format)
        self._check_type(value, datetime)
        # return value
        return self._check_default(value, datetime)
