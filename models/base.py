from abc import ABC, abstractmethod
from motor import motor_asyncio as ma


class FieldError(Exception):
    pass


class ConnectMeta(type):
    """Metaclass for connection."""
    def __init__(cls, name, bases, attr_dict):
        super().__init__(name, bases, attr_dict)


class QueryBase(metaclass=ConnectMeta):
    _connections = dict()
    _bases = dict()

    @classmethod
    def connect(cls, databases):
        for db in databases.keys():
            cls._connections[db] = ma.AsyncIOMotorClient(
                databases[db]["HOST"],
                databases[db]["PORT"]
            )
            cls._bases[db] = cls._connections[db][databases[db]["NAME"]]


from .query import _SetQuery, GetQuery


class BaseModel(type):

    def __init__(cls, name, bases, attr_dict):
        super().__init__(name, bases, attr_dict)
        cls._required_fields = set()
        cls._default_fields = set()
        cls._fields = set()
        for key, attr in attr_dict.items():
            if isinstance(attr, Validate):
                attr.storage_name = key
                cls._required_fields.add(key)
                if hasattr(attr, "_default") and attr._default is not None:
                    cls._default_fields.add(key)
        cls._meta = {
            "db": "default",
            "collection": None,
            "abstract": False
        }
        try:
            cls._meta["db"] = cls.Meta.db
        except AttributeError:
            pass
        try:
            cls._meta["abstract"] = cls.Meta.abstract
        except AttributeError:
            pass
        try:
            cls._meta["collection"] = cls.Meta.collection
        except AttributeError:
            cls._meta["collection"] = f"{name}__collection"
        if not cls._meta["abstract"]:
            cls.query = GetQuery(
                cls._meta["db"],
                cls._meta["collection"],
                cls
            )
            cls._changes = _SetQuery(
                cls._meta["db"],
                cls._meta["collection"]
            )


class Base:
    
    def __init__(self, *args, **kwargs):
        self._null = False
        self._changes = False
        try:
            kwargs["null"]
        except KeyError:
            pass
        else:
            if isinstance(kwargs.get("null"), bool):
                self._null = kwargs.get("null")
            else:
                raise ValueError("[null]: expected bool value")
        try:
            self._default = kwargs["default"]
        except KeyError:
            pass
        try:
            kwargs["choices"]
        except KeyError:
            pass
        else:
            if isinstance(kwargs["choices"], list) or \
                    isinstance(kwargs["choices"], tuple):
                self._changes = kwargs["choices"]
        self.storage_name = None

    def __get__(self, instance, owner):
        if not instance:
            return self
        else:
            try:
                return instance.__dict__[self.storage_name]
            except KeyError:
                return self._default

    def __set__(self, instance, value):
        instance.__dict__[self.storage_name] = value

    def _check_type(self, value, data_type):
        if self._null:
            if value is not None:
                if not isinstance(value, data_type):
                    raise FieldError(
                        f"Value <{self.storage_name}> must be "
                        f"{data_type} type or None"
                    )
                if self._changes and value not in self._changes:
                    raise FieldError(
                        f"Value <{self.storage_name}> must be in {self._changes}"
                    )
        else:
            if not isinstance(value, data_type):
                raise FieldError(
                    f"Value <{self.storage_name}> must be {data_type} type"
                )
            if self._changes and value not in self._changes:
                raise FieldError(
                    f"Value <{self.storage_name}> must be in {self._changes}"
                )

    # def _check_default(self, value, data_type):
    #     if self._default is not None and \
    #             not isinstance(self._default, data_type):
    #         raise TypeError("Value for default not valid.")
    #     elif self._default is not None and value is None:
    #         return self._default
    #     return value


class Validate(ABC, Base):

    def __set__(self, instance, value):
        value = self.validate(instance, value)
        super().__set__(instance, value)

    @abstractmethod
    def validate(self, instance, value):
        """base validate method"""
