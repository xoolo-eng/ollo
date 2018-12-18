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
        self._check_type(value, str, null=self._null)
        if self._max_length and value is not None:
            if len(value) > self._max_length:
                raise ValueError(
                    f"Length of value <{self.storage_name}> "
                    "mast be in range (0 < value <= max_length)"
                )
        return value


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
        self._check_type(value, int, null=self._null)
        return value


class FooatField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, float, null=self._null)
        return value


class BooleanField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, bool, null=self._null)
        return value


class ArrayField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, list, null=self._null)
        return value


class ObjectField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, dict, null=self._null)
        return value


class BinaryDataField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("max_length"):
            if isunsignedint(kwargs.get("max_length")):
                self._max_length = kwargs["max_length"]
            else:
                raise ValueError("<max_length>: expected int value greater than zero")

    def validate(self, instance, value=None):
        self._check_type(value, bytes, null=self._null)
        if self._max_length and value is not None:
            if len(value) > self._max_length:
                raise ValueError(
                    f"Length of value <{self.storage_name}> "
                    "mast be in range (0 < value <= max_length)"
                )
        return value


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
        self._check_type(value, date, null=self._null)
        return value


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
        self._check_type(value, datetime, null=self._null)
        return value
