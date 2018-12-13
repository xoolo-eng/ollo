import unittest
import asyncio
from ollo import OLLOConnect
from models import Object1
from data_for_tests import test_data


DATABASES = {
    "default": {
        "NAME": "shop",
        "HOST": "127.0.0.1",
        "PORT": 27017,
    },
    "test": {
        "NAME": "test",
        "HOST": "127.0.0.1",
        "PORT": 27017,
    },
    "statistics": {
        "NAME": "statistics",
        "HOST": "127.0.0.1",
        "PORT": 27017,
    }
}


OLLOConnect.connect(DATABASES)


class TestCreate(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.data = test_data[0]

    def test_init(self):

        async def _go():
            obj = Object1()
            with self.assertRaises(AttributeError):
                obj._id

        self.loop.run_until_complete(_go())

    def test_create(self):

        async def _go():
            obj = Object1(**self.data)
            with self.assertRaises(AttributeError):
                obj._id
            for key, value in self.data.items():
                self.assertEqual(getattr(obj, key), value)
            self.assertEqual(obj.values(), self.data)

        self.loop.run_until_complete(_go())

    def test_save(self):

        async def _go():
            obj1 = Object1()
            obj1(**self.data)
            await obj1.save()
            self.assertTrue(obj1._id)

            obj2 = await Object1.create(**self.data)
            self.assertTrue(obj2._id)

            self.assertNotEqual(obj1._id, obj2._id)

        self.loop.run_until_complete(_go())


class TestQuery(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.data1 = test_data[1]
        self.data2 = test_data[1]
        self._id1 = None
        self._id2 = None

        async def _go():
            obj1 = await Object1.create(**self.data1)
            obj2 = await Object1.create(**self.data2)
            self._id1 = obj1._id
            self._id2 = obj2._id

        self.loop.run_until_complete(_go())

    def test_get(self):

        async def _go():
            obj1 = await Object1.query.get(_id=self._id1)
            obj2 = await Object1.query.get(_id=self._id2)

            self.assertEqual(obj1._id, self._id1)
            self.assertEqual(obj2._id, self._id2)

        self.loop.run_until_complete(_go())

    def test_values(self):

        async def _go():
            obj1 = await Object1.query.get(_id=self._id1)
            obj2 = await Object1.query.get(_id=self._id2)

            self.assertEqual(
                obj1.values("name", "email", "latitude", "range"),
                obj2.values("name", "email", "latitude", "range")
            )

            self.assertNotEqual(obj1.values(), obj2.values())

        self.loop.run_until_complete(_go())


if __name__ == '__main__':
    unittest.main()
