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
                raise ValueError("< max_length >: expected int value greater than zero")

    def validate(self, instance, value=None):
        if not self._null and not value:
            raise ValueError(f"Value < {self.storage_name} > cannot be empty")
        if isinstance(value, str):
            if self._max_length and not 0 < len(value) <= self._max_length:
                raise ValueError(f"Value < {self.storage_name} > must be in range (0, max_length]")
        else:
            raise ValueError(f"Value < {self.storage_name} > must be type of string")
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

    def validate(self,  instance, value=None):
        if not self._null and not value:
            raise ValueError(f"Value < {self.storage_name} > cannot be empty")
        if not isinstance(value, int):
            raise ValueError(f"Value < {self.storage_name} > must be type of string")
        super().validate(instance, value)
