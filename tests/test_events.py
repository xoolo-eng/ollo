import unittest
import asyncio
from ollo import events


class TestEvent(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def callback(self, *args, **kwargs):
        print("callback(", args, kwargs, ")")

    def test_1(self):
        async def _go():
            events.Event(name=events.E_USER1, callback=self.callback)

        self.loop.run_until_complete(_go())

    def test_2(self):
        async def _go():
            events.Event.occurence(events.E_USER1, "test_2", argument=4)

        self.loop.run_until_complete(_go())

    def test_3(self):
        async def _go():

            @events.Event.origin(events.E_USER1, asynchron=False)
            def test_middle(name, argument=0):
                print("middle")

            @events.Event.origin(events.E_USER1)
            async def test_middle_as(name, argument):
                await asyncio.sleep(2)
                print("async middle")

            test_middle("argument", argument=9)
            await test_middle_as("argument", argument=9)
        self.loop.run_until_complete(_go())


if __name__ == '__main__':
    unittest.main()
