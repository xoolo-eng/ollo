class Event(object):

    instance = None
    callbacks = dict()

    def __new__(cls, **kwargs):
        if cls.callbacks.get(kwargs.get("name")) is None:
            cls.callbacks[kwargs["name"]] = set()
            if kwargs.get("callback"):
                cls.callbacks[kwargs["name"]].add(kwargs["callback"])
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    @classmethod
    def occurence(self, name, *args, **kwargs):
        try:
            for callback in self.callbacks[name]:
                callback(*args, **kwargs)
        except KeyError:
            pass

    @classmethod
    def origin(self, name, post=False, asynchron=True):

        def _wripper(funck):

            def _executor(*args, **kwargs):
                if post:
                    result = funck(*args, **kwargs)
                    self.occurence(name, *args, **kwargs)
                    return result
                else:
                    self.occurence(name, *args, **kwargs)
                    return funck(*args, **kwargs)

            async def _async_executor(*args, **kwargs):
                if post:
                    result = await funck(*args, **kwargs)
                    self.occurence(name, *args, **kwargs)
                    return result
                else:
                    self.occurence(name, *args, **kwargs)
                    return (await funck(*args, **kwargs))

            if asynchron:
                return _async_executor
            else:
                return _executor
        return _wripper

    def register(self, name, callback):
        if self.callbacks.get(name) is None:
            self.callbacks[name] = set()
        self.callbacks[name].add(callback)
