from ollo.models import FileField as _FF


class FileField(_FF):

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def validate(self, instance, value):
        try:
            _ = value.filename
            _ = value.file
            _ = value.content_type
        except AttributeError:
            raise ValueError(
                f"Value <{self.storage_name}> must be object with "
                "fields ('filename', 'file', 'content_type')"
            )

        return value
