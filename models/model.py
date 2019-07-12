from .base import BaseModel
import os
from ollo import events


class Model(metaclass=BaseModel):
    def __setattr__(self, name, value):
        if name in self._required_fields:
            self._fields.add(name)
        super().__setattr__(name, value)

    def __init__(self, *args, **kwargs):
        # for obj in Model.__subclasses__():
        # obj._fields = set()
        self._fields = set()
        if len(kwargs) > 0:
            self.__call__(*args, **kwargs)
            self._check_fields()

    def __call__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
            # self._fields.add(key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
        self._fields.add(key)

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError("Object does not support indexing")
        elif key in self._fields:
            try:
                return getattr(self, key)
            except AttributeError:
                pass
        raise KeyError(key)

    def __str__(self):
        element = dict()
        for key in self._fields:
            try:
                element[key] = getattr(self, key, None)
            except KeyError:
                raise AttributeError("Object not found, maybe it was deleted.")
        return f"ModelObject({element})"

    @classmethod
    def field_names(cls):
        for name in cls._required_fields:
            yield name

    def _check_fields(self):
        fields = (self._required_fields ^ self._default_fields) & self._fields
        if fields != (self._required_fields ^ self._default_fields):
            fields = fields ^ self._required_fields
            raise ValueError(f"Fields {list(fields)} not found")

    @events.Event.origin(events.M_SAVE)
    async def save(self):
        self._check_fields()
        result = await self._changes._save_obj(
            **{key: getattr(self, key) for key in (self._fields | self._default_fields)}
        )
        setattr(self, "_id", result)
        return result

    @classmethod
    async def create(cls, **kwargs):
        result = cls()
        result(**kwargs)
        await result.save()
        return result

    async def update(self, **kwargs):
        try:
            await self._changes._update_obj(self._id, **kwargs)
        except AttributeError:
            raise AttributeError("Model cannot be updated without saving.")
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def delete(self):
        try:
            await self._changes._delete_obj(self._id)
        except AttributeError:
            raise ArithmeticError("Model cannot be delete without saving.")
        for name in self._fields:
            delattr(self, name)
        del self

    def values(self, *args, include=True):
        if len(args) > 0:
            if include:
                return {key: getattr(self, key) for key in self._fields if key in args}
            else:
                return {
                    key: getattr(self, key) for key in self._fields if key not in args
                }
        return {key: getattr(self, key) for key in self._fields}

    class Meta:
        abstract = True

    class DoesNotExist(Exception):
        pass
