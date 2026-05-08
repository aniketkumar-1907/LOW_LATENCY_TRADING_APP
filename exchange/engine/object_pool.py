from collections import deque


class ObjectPool:

    def __init__(self, cls, size):

        self.pool = deque(
            cls() for _ in range(size)
        )

        self.cls = cls

    # =========================
    # Acquire
    # =========================

    def acquire(self):

        if self.pool:
            return self.pool.popleft()

        return self.cls()

    # =========================
    # Release
    # =========================

    def release(self, obj):

        self.pool.append(obj)