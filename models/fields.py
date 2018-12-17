from .base import Validate, BaseDescriptor
from .utils import isunsignedint
from datetime import datetime


def _check_type(value, data_type, null=False):
    if null:
        if not isinstance(value, data_type) or value is not None:
            raise ValueError(f"Value <{self.storage_name}> must be {data_type} type or None")
    else:
        if not isinstance(value, data_type):
            raise ValueError(f"Value <{self.storage_name}> must be {data_type} type")


class StringField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._max_length = None
        if kwargs.get("max_length"):
            if isunsignedint(kwargs.get("max_length")):
                self._max_length = kwargs["max_length"]
            else:
                raise ValueError("<max_length>: expected int value greater than zero")

    def validate(self, instance, value=None):
        _check_type(value, str, null=self._null)
        if self._max_length and value is not None:
            if len(value) > self._max_length:
                raise ValueError(
                    f"Length of value <{self.storage_name}> "
                    "mast be in range (0 < value <= max_length)"
                )
        super().validate(instance, value)


class SymbolField(StringField):
    """
    For symbol type.
    Not implementation.
    Full copy StringField.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IntegerField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        _check_type(value, int, null=self._null)
        super().validate(instance, value)


class FooatField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        _check_type(value, float, null=self._null)
        super().validate(instance, value)


class BooleanField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        _check_type(value, bool, null=self._null)
        super().validate(instance, value)


class ArrayField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        _check_type(value, list, null=self._null)
        super().validate(instance, value)


class ObjectField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        _check_type(value, dict, null=self._null)
        super().validate(instance, value)


class BinaryDataField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("max_length"):
            if isunsignedint(kwargs.get("max_length")):
                self._max_length = kwargs["max_length"]
            else:
                raise ValueError("<max_length>: expected int value greater than zero")

    def validate(self, instance, value=None):
        _check_type(value, bytes, null=self._null)
        if self._max_length and value is not None:
            if len(value) > self._max_length:
                raise ValueError(
                    f"Length of value <{self.storage_name}> "
                    "mast be in range (0 < value <= max_length)"
                )
        super().validate(instance, value)


class DateField(BaseDescriptor, Validate):

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
            value = datetime.datetime(value, self._format).date()
        _check_type(value, datetime.date, null=self._null)
        super().validate(instance, value)


class DataTimeField(DateField):

    def validate(self, instance, value):
        if self._to_date:
            value = datetime.datetime(value, self._format)
        _check_type(value, datetime.datetime, null=self._null)
        super(DateField).validate(instance, value)
