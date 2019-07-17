import os
import importlib
from collections import namedtuple
from ollo import base


route = namedtuple("route", ["name", "handler", "path"])

_x = property()


class ControllerError(Exception):
    pass


class Controller(metaclass=base.__BaseSingleton):
    __slots__ = ("_urlpatterns", "_sub_path")

    def __new__(cls, *args, **kwargs):
        cls._urlpatterns = []
        cls._sub_path = []
        return super().__new__(cls, *args, **kwargs)

    @property
    def urlpatterns(self):
        for router in self._urlpatterns:
            yield router

    @_x.setter
    def entry_point(self, path):
        importlib.import_module(path)

    @classmethod
    def add(cls, path, **kwargs):
        try:
            cls._urlpatterns.append(
                route(
                    kwargs["name"], kwargs["handler"], "".join(cls._sub_path + [path])
                )
            )
        except KeyError as e:
            print(e)
            raise ControllerError("ERROR")

    @classmethod
    def include(cls, path, lib):
        cls._sub_path.append(path)
        importlib.import_module(lib)
        cls._sub_path.remove(path)

    def __repr__(self):
        return f"Controller({[url for url in self.urlpatterns]})"

    def __str__(self):
        return f"{[url for url in self.urlpatterns]}"
