from .base import Validate, BaseDescriptor
from .utils import isunsignedint


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
        if self._null:
            if not isinstance(value, str) or value != None:
                raise ValueError(f"Value <{self.storage_name}> must be str type or None")
        else:
            if not isinstance(value, str):
                raise ValueError(f"Value <{self.storage_name}> must be str type")
        if self._max_length and value !=None:
            if len(value) > self._max_length:
                raise ValueError(
                    f"Length of value <{self.storage_name}> "
                    "mast be in range (0 < value <= max_length)"
                )


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
        if self._null:
            if not isinstance(value, int) or value is not None:
                raise ValueError(f"Value <{self.storage_name}> must be int type or None")
        else:
            if not isinstance(value, int):
                raise ValueError(f"Value <{self.storage_name}> must be int type")
        super().validate(instance, value)


class FooatField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        if self._null:
            if not isinstance(value, float) or value is not None:
                raise ValueError(f"Value <{self.storage_name}> must be float type or None")
        else:
            if not isinstance(value, float):
                raise ValueError(f"Value <{self.storage_name}> must be float type")
        super().validate(instance, value)


class BooleanField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        if self._null:
            if not isinstance(value, bool) or value is not None:
                raise ValueError(f"Value <{self.storage_name}> must be boolean type or None")
        else:
            if not isinstance(value, bool):
                raise ValueError(f"Value <{self.storage_name}> must be boolean type")
        super().validate(instance, value)


class ArrayField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        if self._null:
            if not isinstance(value, list) or value is not None:
                raise ValueError(f"Value <{self.storage_name}> must be list type or None")
        else:
            if not isinstance(value, list):
                raise ValueError(f"Value <{self.storage_name}> must be list type")
        super().validate(instance, value)


class ObjectField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        if self._null:
            if not isinstance(value, dict) or value is not None:
                raise ValueError(f"Value <{self.storage_name}> must be dict type or None")
        else:
            if not isinstance(value, dict):
                raise ValueError(f"Value <{self.storage_name}> must be dict type")
        super().validate(instance, value)


class BinaryDataField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("max_length"):
            if isunsignedint(kwargs.get("max_length")):
                self._max_length = kwargs["max_length"]
            else:
                raise ValueError("<max_length>: expected int value greater than zero")

    def validate(self, instance, value=Null):
        if self._null:
            if not isinstance(value, bytes) or value is not None:
                raise ValueError(f"Value <{self.storage_name}> must be bytes type or None")
        else:
            if not isinstance(value, bytes):
                raise ValueError(f"Value <{self.storage_name}> must be bytes type")
        if self._max_length and value !=None:
            if len(value) > self._max_length:
                raise ValueError(
                    f"Length of value <{self.storage_name}> "
                    "mast be in range (0 < value <= max_length)"
                )
        super().validate(instance, value)


class DateField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value):
        # 
        super().validate(instance, value)


class DataTimeField(BaseDescriptor, Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        # 
        super().validate(instance, value)

# class ObjectIdField(BaseDescriptor, Validate):
#     pass


# class RegularExpressionField(BaseDescriptor, Validate):
#     pass


# class CodeField(BaseDescriptor, Validate):
#     pass
