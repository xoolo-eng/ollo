from .base import BaseSerializer


class Serializer(BaseSerializer):

    class ValidateError(Exception):
        pass

    def __init__(self, *args, **kwargs):
        for obj in Serializer.__subclasses__():
            obj._fields = set()
        for arg in args:
            for key, value in arg.items():
                setattr(self, key, value)
                self._fields.add(key)

    def _check_fields(self):
        fields = set(self._required_fields) & self._fields
        if fields != set(self._required_fields):
            fields = fields ^ set(self._required_fields)
            raise ValueError(f"Fields {list(fields)} not found")

    def __dict__(self):
        self._check_fields()
        return {key: getattr(self, key) for key in self._fields}

    async def is_valid(self):
        self.errors = dict()
        # проверка наличия валидирующих функций для отдельных полей
        validate_funcs = dict()
        for key in self._fields:
            try:
                validate_funcs[key] = (getattr(self, f"validate_{key}"))
            except AttributeError:
                pass
        # выплнение валидирующих функций для отдельных полей
        for key in validate_funcs:
            try:
                validate_funcs[key](getattr(self, key))
            except self.ValidateError as e:
                self.errors[key] = str(e)
        try:
            self.validate(
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
        return dict(self)


class MoselSerializer(Serializer):
    pass
