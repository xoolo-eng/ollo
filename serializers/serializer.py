from .base import BaseSerializer
from copy import deepcopy


class Serializer(metaclass=BaseSerializer):

    class ValidateError(Exception):
        pass

    def __init__(self, *args, **kwargs):
        for cls in Serializer.__subclasses__():
            cls._fields = set()
        for arg in args:
            for key, value in arg.items():
                setattr(self, key, value)
                self._fields.add(key)

    def _check_fields(self):
        fields = self._required_fields & self._fields
        if fields != self._required_fields:
            fields = fields ^ self._required_fields
            raise ValueError(f"Fields {list(fields)} not found")

    def __getitem__(self, key):
        if isinstance(key, int):
            raise TypeError("Object does not support indexing")
        if isinstance(key, str):
            try:
                return getattr(self, key)
            except AttributeError:
                raise KeyError(key)
        raise TypeError(key)

    async def is_valid(self):
        self._check_fields()
        self.errors = dict()
        validate_funcs = dict()
        for key in self._fields:
            try:
                validate_funcs[key] = (getattr(self, f"validate_{key}"))
            except AttributeError:
                pass
        for key in validate_funcs:
            try:
                await validate_funcs[key](getattr(self, key))
            except self.ValidateError as e:
                self.errors[key] = str(e)
        try:
            await self.validate(
                {key: getattr(self, key) for key in self._fields}
            )
        except AttributeError:
            pass
        except self.ValidateError as e:
            self.errors["non_field"] = str(e)
        if len(self.errors):
            return False
        return True

    def add_error(self, field, *messages):
        self.errors[field] = " ".join(messages)

    def data(self):
        return {key: getattr(self, key) for key in self._fields}


class ModelSerializer(Serializer):
    ALL_FIELDS = "__all__"

    def __init__(self, *args, **kwargs):
        for cls in ModelSerializer.__subclasses__():
            if hasattr(cls, "Meta"):
                fields = list()
                if cls.Meta.fields == self.ALL_FIELDS:
                    fields = list(cls.Meta.model.field_names())
                else:
                    fields = list(cls.Meta.fields)
                for field in fields:
                    obj = type(getattr(cls.Meta.model, field))
                    obj.storage_name = field
                    setattr(cls, field, obj())
                    cls._required_fields.add(field)
        super().__init__(*args, **kwargs)
