import unittest
import asyncio
from ollo import OLLOConnect
from models import Object2, Object3, Object4, Object5, Object6
from data_for_tests import test_data
import copy
from datetime import datetime
import os
from ollo.models import FieldError


DATABASES = {
    "test": {
        "NAME": "test",
        "HOST": "127.0.0.1",
        "PORT": 27017
    }
}


OLLOConnect.connect(DATABASES)


class TestModel(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.data = test_data[0]
        self.list_fields = ["index", "guid", "isActive", "name", "tags"]

    def test_fields(self):

        async def _go():
            self.assertEqual(set(self.list_fields), set(Object2.field_names()))

        self.loop.run_until_complete(_go())

    def test_required(self):

        async def _go():
            data = copy.deepcopy(self.data)
            del data[self.list_fields[0]]
            obj = Object2()
            obj(**data)
            with self.assertRaises(ValueError):
                await obj.save()

        self.loop.run_until_complete(_go())

    def test_type(self):

        async def _go():
            obj = Object3()
            for field in self.list_fields:
                with self.assertRaises(FieldError):
                    setattr(obj, field, self.data[field])

        self.loop.run_until_complete(_go())

    def test_save(self):

        async def _go():
            obj = Object2(**self.data)
            for key, value in self.data.items():
                self.assertEqual(getattr(obj, key), value)
            await obj.save()

        self.loop.run_until_complete(_go())


class TestDate(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.formats = {
            "no_format": [
                "18-09-2018",
                "18-09-2018 0:05:59",
            ],
            "date": [
                "2018-09-18",
                "2018-18-09",
                "18-09-18",
            ],
            "datetime": [
                "2018-09-18 12:15:33",
                "2018-18-09 19:01:00",
                "18-09-18 5:3:1",
            ]
        }

    def test_date_raise(self):

        async def _go():
            for key in self.formats["date"]:
                obj = Object4()
                with self.assertRaises(FieldError):
                    obj.date1 = key

        self.loop.run_until_complete(_go())

    def test_datetime_raise(self):

        async def _go():
            for key in self.formats["datetime"]:
                obj = Object4()
                with self.assertRaises(FieldError):
                    obj.date2 = key

        self.loop.run_until_complete(_go())

    def test_date(self):

        async def _go():
            obj = Object4()
            obj.date1 = self.formats["no_format"][0]
            obj.date2 = self.formats["no_format"][1]
            self.assertEqual(
                obj.date1,
                datetime.strptime(self.formats["no_format"][0], "%d-%m-%Y").date()
            )
            self.assertEqual(
                obj.date2,
                datetime.strptime(self.formats["no_format"][1], "%d-%m-%Y %H:%M:%S")
            )

        self.loop.run_until_complete(_go())


class Test_F_Data(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.formats = {
            "format": [
                "2018-09-18",
                "2018-09-18 0:05:59",
            ],
            "date": [
                "09-18-2018",
                "2018-18-09",
                "18-09-18",
            ],
            "datetime": [
                "09-18-2018 12:15:33",
                "2018-18-09 19:01:00",
                "18-09-18 5:3:1",
            ]
        }

    def test_date_raise(self):

        async def _go():
            for key in self.formats["date"]:
                obj = Object5()
                with self.assertRaises(FieldError):
                    obj.date1 = key

        self.loop.run_until_complete(_go())

    def test_datetime_raise(self):

        async def _go():
            for key in self.formats["datetime"]:
                obj = Object5()
                with self.assertRaises(FieldError):
                    obj.date2 = key

        self.loop.run_until_complete(_go())

    def test_date(self):

        async def _go():
            obj = Object5()
            obj.date1 = self.formats["format"][0]
            obj.date2 = self.formats["format"][1]
            self.assertEqual(
                obj.date1,
                datetime.strptime(self.formats["format"][0], "%Y-%m-%d").date()
            )
            self.assertEqual(
                obj.date2,
                datetime.strptime(self.formats["format"][1], "%Y-%m-%d %H:%M:%S")
            )

        self.loop.run_until_complete(_go())

    def test_file(self):
        from collections import namedtuple

        async def _go():
            file = namedtuple("file", ["filename", "file", "content_type"])
            open_file = open(os.path.abspath("tests/models.py"), "rb")
            loadfile = file("model.py", open_file, "text")
            obj = Object6()
            obj.file = loadfile
            await obj.save()

        self.loop.run_until_complete(_go())


if __name__ == '__main__':
    unittest.main()
