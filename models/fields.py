from .base import Validate, FieldError
from .utils import isunsignedint
import os
import re
import signal
import shutil
import asyncio
from collections import namedtuple
from bson.objectid import ObjectId
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor
from ollo import events


class StringField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._max_length = None
        if kwargs.get("max_length"):
            if isunsignedint(kwargs.get("max_length")):
                self._max_length = kwargs["max_length"]
            else:
                raise ValueError(
                    "<max_length>: expected int value greater than zero"
                )

    def validate(self, instance, value=None):
        self._check_type(value, str)
        if self._max_length and value is not None:
            if len(value) > self._max_length:
                raise FieldError(
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
        self._check_type(value, int)
        return value


class FooatField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, float)
        return value


class BooleanField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, bool)
        return value


class ArrayField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, list)
        return value


class ObjectField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, dict)
        return value


class ObjectIdField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, instance, value=None):
        self._check_type(value, ObjectId)
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
        self._check_type(value, bytes)
        if self._max_length and value is not None:
            if len(value) > self._max_length:
                raise FieldError(
                    f"Length of value <{self.storage_name}> "
                    "mast be in range (0 < value <= max_length)"
                )
        return value


class DateField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._to_date = False
        self._format = "%d-%m-%Y"
        if kwargs.get("to_date"):
            self._to_date = bool(kwargs["to_date"])
        if kwargs.get("format"):
            self._format = kwargs["format"]

    def validate(self, instance, value=None):
        if self._to_date:
            try:
                value = datetime.strptime(value, self._format).date()
            except ValueError as e:
                raise FieldError(e)
        self._check_type(value, date)
        return value


class DateTimeField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._to_date = False
        self._format = "%d-%m-%Y %H:%M:%S"
        if kwargs.get("to_date"):
            self._to_date = bool(kwargs["to_date"])
        if kwargs.get("format"):
            self._format = kwargs["format"]

    def validate(self, instance, value=None):
        if self._to_date:
            try:
                value = datetime.strptime(value, self._format)
            except ValueError as e:
                raise FieldError(e)
        self._check_type(value, datetime)
        return value


class FileField(Validate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._upload_to = kwargs["upload_to"]
        self._filename = kwargs.get("filename")
        self._file = None
        events.Event(name=events.M_SAVE, callback=self._save)

    # def __get__(self, instance, owner):
    #     return super().__get__(instance, owner)

    def _save(self, *args, **kwargs):
        if self._file:
            def save_file(file, path, name):
                result = None
                with open(os.path.join(path, name), "wb") as new_file:
                    result = shutil.copyfileobj(file, new_file, 4096)
                file.close()
                return result

            with ThreadPoolExecutor() as executor:
                executor.submit(
                    save_file,
                    self._file,
                    self._upload_to,
                    self._filename or self._file.name.split("/")[-1]
                )

    def validate(self, instance, value=None):
        if not self._null:
            if isinstance(value, str):
                pass
            else:
                try:
                    filename = value.filename
                    self._file = value.file
                    self._content_type = value.content_type
                except AttributeError:
                    raise FieldError(
                        f"Value <{self.storage_name}> must be object with "
                        "fields ('filename', 'file', 'content_type') or "
                        "string type with full path to file"
                    )
                if not os.path.isdir(self._upload_to):
                    os.makedirs(self._upload_to)
                if self._filename:
                    filename = f"{self._filename}.{filename.split('.')[-1]}"
                value = os.path.join(
                    self._upload_to,
                    filename
                )
        return value


class EmailField(StringField):
    EMAIL = "[-\w.]+@([A-z0-9][-A-z0-9]+\.)?([A-z0-9][-A-z0-9]+\.)+[A-z]{2,6}$"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._max_length = None
        self._pattern = re.compile(self.EMAIL)

    def validate(self, instance, value=None):
        value = super().validate(instance, value)
        if re.match(self._pattern, value):
            return value
        raise FieldError(f"Value <{self.storage_name}> must be ip email address")


class IpAddressField(StringField):
    IPV4 = "(?:(?:^|\.)(?:2(?:5[0-5]|\
[0-4]\d)|1?\d?\d)){4}"
    IPV6 = "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|\
([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|\
([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|\
([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|\
([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|\
([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|\
[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|\
fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}\
((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|\
(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:\
((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|\
(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._version = kwargs.get("version") or "ipv4"
        if self._version not in ["ipv4", "ipv6"]:
            raise ValueError("<version>: must be \"ipv4\" or \"ipv6\"")
        self._max_length = 15 if self._version == "ipv4" else 39
        self._pattern = re.compile(
            kwargs.get("pattern") or self.IPV4 if self._version == "ipv4" else self.IPV6
        )

    def validate(self, instance, value=None):
        value = super().validate(instance, value)
        if re.match(self._pattern, value):
            return value
        raise FieldError(f"Value <{self.storage_name}> must be ip address")
