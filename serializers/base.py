from ollo.models.base import Validate


class BaseSerializer(type):

    def __init__(cls, name, bases, attr_dict):
        super().__init__(name, bases, attr_dict)
        cls._required_fields = list()
        for key, attr in attr_dict.items():
            if isinstance(attr, Validate):
                attr.storage_name = key
                cls._required_fields.append(key)
