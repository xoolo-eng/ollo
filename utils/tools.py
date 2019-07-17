from aiofile import AIOFile
import hashlib
import pickle


def sha512(*args):
    data = bytes()
    for arg in args:
        data += pickle(args)
    return hashlib.sha512(data).hexdigest()


def __random(length):
    from random import random

    value = random()
    return sha512(value)[:length]


async def random(length):
    """512 characters maximum."""
    if length > 512:
        length = 512
    try:
        async with AIOFile("/dev/urandom", "rb") as fd:
            return (await fd.read(length // 2 + 1)).hex()[:length]
    except Exception:
        return __random(length)
