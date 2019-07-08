from ollo.models import FileField as _FF
from ollo.models.base import FieldError


class FileField(_FF):

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def validate(self, instance, value):
        try:
            _ = value.filename
            _ = value.file
            _ = value.content_type
        except AttributeError:
            raise FieldError(
                f"Value <{self.storage_name}> must be object with "
                "fields ('filename', 'file', 'content_type')"
            )

        return value
