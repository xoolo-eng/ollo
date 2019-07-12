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
        res = await self._bases[self.db][self.collection].update_one(
            {"_id": _id}, {"$set": kwargs}
        )
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
        query = dict()
        query = self._parse_query(kwargs)
        res = await self._bases[self.db][self.collection].find_one(query)
        if not res:
            raise self.model.DoesNotExist(
                f"{self.model.__name__} " "matching query does not exist"
            )
        return self.model(**res)

    def all(self, **kwargs):
        return CollectionSet(
            connect=self._bases[self.db][self.collection], query={}, model=self.model
        )

    def filter(self, **kwargs):
        query = dict()
        query = self._parse_query(kwargs)
        return CollectionSet(
            connect=self._bases[self.db][self.collection], query=query, model=self.model
        )

    def _parse_query(self, obj):
        query = dict()
        for key, value in obj.items():
            if self._iscomplex(key):
                key_condition = key.split("__")
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        query[f"{key_condition[0]}.{sub_key}"] = {
                            f"${key_condition[1]}": sub_value
                        }
                else:
                    query[key_condition[0]] = {f"${key_condition[1]}": value}
            else:
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        query[f"{key}.{sub_key}"] = sub_value
                else:
                    query[key] = value
        return query

    def find(self):
        """execute arbitrary query"""
        pass


class CollectionSet:
    def __init__(self, *args, **kwargs):
        self._json = False
        self._bson = True
        self._connect = kwargs.get("connect")
        self._query = kwargs.get("query")
        self._model = kwargs.get("model")
        self._slice = None
        self._sort = ("_id", -1)

    def __aiter__(self):
        if self._slice is None:
            self.cursor = self._connect.find(self._query).sort(*self._sort)
        else:
            self.cursor = (
                self._connect.find(self._query)
                .sort(*self._sort)
                .skip(self._slice.start)
                .limit(self._slice.stop - self._slice.start)
            )
        return self

    async def __anext__(self):
        result = await self.cursor.fetch_next
        if result:
            if not self._json:
                return self._model(**self.cursor.next_object())
            else:
                return self.cursor.next_object()
        else:
            raise StopAsyncIteration

    def __repr__(self):
        return "CollectionSet([<object>, <object>, ...])"

    def __getitem__(self, index):
        if isinstance(index, int):
            loop = asyncio.get_event_loop()

            async def _getitem():
                cursor = self._connect.find(self._query).skip(index).limit(1)
                result = await cursor.fetch_next
                if result:
                    if not self._json:
                        return self._model(**cursor.next_object())
                    else:
                        return cursor.next_object()
                else:
                    return None

            res = loop.run_until_complete(_getitem())
            if res is None:
                raise IndexError(index)
            return res
        self._slice = index
        return self

    async def count(self):
        return await self._connect.count_documents(self._query)

    async def update(self, new_data):
        await self._connect.update_many(self._query, {"$set": new_data})

    async def delete(self):
        await self._connect.delete_many(self._query)

    def sort(self, item):
        if item[0] == "-":
            self._sort = (item[1 : len(item)], -1)
        else:
            self._sort = (item, 1)
        return self

    def json(self):
        self._json = True
        return self
