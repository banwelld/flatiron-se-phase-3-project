class SessionState:
    def __init__(self):
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def clear(self):
        self.data.clear()

    def remove(self, key):
        if key in self.data:
            del self.data[key]