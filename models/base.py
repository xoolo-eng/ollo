from abc import ABC, abstractmethod
from motor import motor_asyncio as ma


class ConnectMeta(type):
    """Metaclass for connection."""
    def __init__(cls, name, bases, attr_dict):
        super().__init__(name, bases, attr_dict)


class QueryBase(metaclass=ConnectMeta):
    __connections = dict()
    __bases = dict()

    @classmethod
    def connect(cls, databases):
        for db in databases.keys():
            cls.__connections[db] = ma.AsyncIOMotorClient(
                databases[db]["HOST"],
                databases[db]["PORT"]
            )
            cls.__bases[db] = cls.__connections[db][databases[db]["NAME"]]

from .query import _SetQuery, GetQuery


class BaseModel(type):

    def __init__(cls, name, bases, attr_dict):
        super().__init__(name, bases, attr_dict)
        cls._required_fields = list()
        for key, attr in attr_dict.items():
            if isinstance(attr, Validate):
                attr.storage_name = key
                cls._required_fields.append(key)
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
        cls._fields = set()
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


class BaseDescriptor:

    def __init__(self, *args, **kwargs):
        self._null = False
        try:
            kwargs["blank"]
        except KeyError:
            pass
        else:
            if isinstance(kwargs.get("null"), bool):
                self._null = kwargs.get("null")
            else:
                raise ValueError("[blank]: expected bool value")


class Base:

    def __init__(self):
        self.storage_name = None

    def __get__(self, instance, owner):
        if not instance:
            return self
        else:
            return instance.__dict__[self.storage_name]

    def __set__(self, instance, value):
        instance.__dict__[self.storage_name] = value


class Validate(ABC, Base):

    def __set__(self, instance, value):
        value = self.validate(instance, value)
        super().__set__(instance, value)

    @abstractmethod
    def validate(self, instance, value):
        """base validate method"""

