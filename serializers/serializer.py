from .base import BaseSerializer
from copy import deepcopy


class Serializer(metaclass=BaseSerializer):

    class ValidateError(Exception):
        pass

    # def __setattr__(self, name, value):
    #     self._fields.add(name)
    #     super().__setattr__(name, value)

    def __init__(self, *args, **kwargs):
        # for cls in Serializer.__subclasses__():
            # cls._fields = set()
        self._fields = set()
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
        if not isinstance(key, str):
            raise TypeError("Object does not support indexing")
        elif key in self._fields:
            try:
                return getattr(self, key)
            except AttributeError:
                pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
        self._fields.add(key)

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
            if str(e):
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
        if hasattr(self, "Meta"):
            fields = list(self.Meta.model.field_names())
            if hasattr(self.Meta, "fields"):
                if self.Meta.fields == self.ALL_FIELDS:
                    fields = list(self.Meta.model.field_names())
                else:
                    fields = list(self.Meta.fields)
            if hasattr(self.Meta, "exclude"):
                exclude = list(self.Meta.exclude)
                for element in exclude:
                    fields.remove(element)
            for field in fields:
                obj = type(getattr(self.Meta.model, field))
                obj.storage_name = field
                self.__dict__["field"] = obj()
                self._required_fields.add(field)
        super().__init__(*args, **kwargs)

    async def save(self):
        return await self.Meta.model.create(**self.data())
