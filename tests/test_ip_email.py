import unittest
import asyncio
from ollo import OLLOConnect
from models import Object7

DATABASES = {
    "test": {
        "NAME": "test",
        "HOST": "127.0.0.1",
        "PORT": 27017
    }
}

OLLOConnect.connect(DATABASES)


class TestAddressEmail(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.data = {
            "ip_v4": "126.8.62.87",
            "ip_v6": "2001:0db8:11a3:09d7:1f34:8a2e:07a0:765d",
            "email": "amelchenko.dmitriy@outlook.com"
        }
        self.error_data = {
            "ip_v4": "926.5.6.688",
            "ip_v6": "2001:0dbg:11a3:y9d7:1f34:8a2e:07a0:765d",
            "email": "amelchenko.dmitriy#outlook.com"
        }

    def test_valid(self):

        async def _go():
            obj = Object7()
            obj.ip_v4 = self.data.get("ip_v4")
            obj.ip_v6 = self.data.get("ip_v6")
            obj.email = self.data.get("email")
            obj.save()

        self.loop.run_until_complete(_go())


if __name__ == '__main__':
    unittest.main()
