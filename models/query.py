import re
from .base import QueryBase
import asyncio
from bson.objectid import ObjectId


class _SetQuery(QueryBase):

    def __init__(self, db, collection):
        super().__init__()
        self.db = db
        self.collection = collection


    async def _save_obj(self, **kwargs):
        if kwargs.get("_id"):
            _id = kwargs["_id"]
            del kwargs["_id"]
            self._bases[self.db][self.collection].replace_one({"_id": _id}, kwargs)
            return _id
        else:
            res = await self._bases[self.db][self.collection].insert_one(kwargs)
            return res.inserted_id

    async def _update_obj(self, _id, **kwargs):
        res = await self._bases[self.db][self.collection].update_one({"_id": _id}, {"$set": kwargs})
        return res.modified_count

    async def _delete_obj(self, _id):
        res = await self._bases[self.db][self.collection].delete_one({"_id": _id})
        return res.deleted_count


class GetQuery(QueryBase):

    def _iscomplex(self, key):
        for pattern in self.patterns:
            if re.match(pattern, key):
                return True
        return False

    def __init__(self, db, collection, model):
        super().__init__()
        self.query = {}
        self.db = db
        self.collection = collection
        self.patterns = [
            re.compile("[a-zA-Z0-9]+__lt"),
            re.compile("[a-zA-Z0-9]+__lte"),
            re.compile("[a-zA-Z0-9]+__gt"),
            re.compile("[a-zA-Z0-9]+__gte"),
            re.compile("[a-zA-Z0-9]+__ne"),
        ]
        self.model = model

    def __call__(self):
        return self

    async def get(self, **kwargs):
        if kwargs.get("_id") and isinstance(kwargs["_id"], str):
            kwargs["_id"] = ObjectId(kwargs["_id"])
        res = await self._bases[self.db][self.collection].find_one(kwargs)
        if not res:
            raise self.model.DoesNotExist(f"{self.model.__name__} "
                "matching query does not exist")
        return self.model(**res)

    def all(self, *args):
        return CollectionSet(
            connect=self._bases[self.db][self.collection],
            query=self.query,
            model=self.model
        )

    def filter(self, **kwargs):
        for key, value in kwargs.items():
            if self._iscomplex(key):
                key_condition = key.split("__")
                self.query[key_condition[0]] = {f"${key_condition[1]}": value}
            else:
                self.query[key] = value
        return CollectionSet(
            connect=self._bases[self.db][self.collection],
            query=self.query,
            model=self.model
        )

    def find(self):
        """execute arbitrary query"""
        pass


class CollectionSet():

    def __init__(self, *args, **kwargs):
        self._json = False
        self._bson = True
        self.connect = kwargs.get("connect")
        self.query = kwargs.get("query")
        self.model = kwargs.get("model")
        self.counter = 0
        self.slice = None

    def __aiter__(self):
        if not self.slice:
            self.cursor = self.connect.find(self.query)
        else:
            self.cursor = self.connect.find(
                self.query).skip(
                self.slice.start).limit(
                self.slice.stop)
        return self

    async def __anext__(self):
        result = await self.cursor.fetch_next
        if result:
            if not self._json:
                return self.model(**self.cursor.next_object())
            else:
                return self.cursor.next_object()
        else:
            raise StopAsyncIteration

    def __repr__(self):
        return "CollectionSet([<object>, <object>, ...])"

    async def __getitem__(self, index):
        if isinstance(index, int):
            cursor = self.connect.find(self.query).skip(index).limit(1)
            result = await cursor.fetch_next
            if result:
                if not self._json:
                    return self.model(**cursor.next_object())
                else:
                    return cursor.next_object()
            else:
                raise IndexError
        self.slice = index
        return self

    async def count(self):
        return await self.connect.count_documents(self.query)

    async def update(self, new_data):
        await self.connect.update_many(self.query, {"$set": new_data})

    async def delete(self):
        await self.connect.delete_many(self.query, {"$set": new_data})

    def json(self):
        self._json = True
        return self
