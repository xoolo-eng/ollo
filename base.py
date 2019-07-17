class __BaseSingleton(type):
    _instances = {}

    def __init__(cls, name, bases, attr_dict):
        super().__init__(name, bases, attr_dict)

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
