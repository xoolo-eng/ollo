from abc import ABC, abstractmethod
from motor import motor_asyncio as ma


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
        # cls._fields = set()
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
        try:
            kwargs["null"]
        except KeyError:
            pass
        else:
            if isinstance(kwargs.get("null"), bool):
                self._null = kwargs.get("null")
            else:
                raise ValueError("[null]: expected bool value")
        self.storage_name = None

    def __get__(self, instance, owner):
        if not instance:
            return self
        else:
            return instance.__dict__[self.storage_name]

    def __set__(self, instance, value):
        instance.__dict__[self.storage_name] = value

    def _check_type(self, value, data_type, null=False):
        if null:
            if not isinstance(value, data_type) or value is not None:
                raise TypeError(f"Value <{self.storage_name}> must be {data_type} type or None")
        else:
            if not isinstance(value, data_type):
                raise TypeError(f"Value <{self.storage_name}> must be {data_type} type")


class Validate(ABC, Base):

    def __set__(self, instance, value):
        value = self.validate(instance, value)
        super().__set__(instance, value)

    @abstractmethod
    def validate(self, instance, value):
        """base validate method"""
