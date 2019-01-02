import unittest
import asyncio
from serializers import TestSerializer


class TestModelSerializer(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def test_create(self):

        async def _go():
            serializer = TestSerializer({
                "index": "index",
                "guid": 8,
                "isActive": True,
                "name": ["one", "twoo"],
                "tags": {
                            "first": "Charles",
                            "last": "Hardin"
                        },
                "uuid": 88999
            })
            if await serializer.is_valid():
                print(serializer.data())
            else:
                print(serializer.errors)

        self.loop.run_until_complete(_go())


if __name__ == '__main__':
    unittest.main()
