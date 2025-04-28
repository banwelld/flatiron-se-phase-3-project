class SessionState:
    def __init__(self, **kwargs):
        self.data = {**kwargs}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def values(self):
        vals = []
        for item in self.data.values():
            vals.append(item)
        return vals

    def set(self, key, value):
        self.data[key] = value

    def reset(self):
        for key in self.data:
            self.data[key] = None
