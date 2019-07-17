from ollo import base
import os



class __BaseSettings(base.__BaseSingleton):
    def __call__(cls, *args, **kwargs):
        result = super().__call__(*args, **kwargs)
        for key, value in kwargs.items():
            result._storage[key] = value
        return result


class Settings(metaclass=__BaseSettings):
    __slots__ = ("_storage",)

    def __new__(cls, *args, **kwargs):
        cls._storage = {key: value for key, value in kwargs.items()}
        return super().__new__(cls)

    @property
    def settings(self):
        return self._storage

    def get(self, name, default=None):
        try:
            return self._storage[name]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        if key not in self._storage:
            self._storage[key] = value

    def __getitem__(self, key):
        return self._storage[key]

    def __getattr__(self, name):
        try:
            return self._storage[name.upper()]
        except KeyError:
            raise AttributeError(f"{name}")

    def __str__(self):
        return "\n".join([f"{key} = {value}" for key, value in self._storage.items()])

    def __repr__(self):
        return f"Settings({self.settings})"


__default_settints = {
    "DEBUG": True,
    "HOST": "localhost",
    "PORT": 8008,
    "BASE_DIR": os.environ["PWD"]
}

settings = Settings(**__default_settints)
