class RingBuffer:

    def __init__(self, size):

        self.size = size

        self.buffer = [None] * size

        self.head = 0

        self.tail = 0

        self.count = 0

    # =========================
    # Push
    # =========================

    def push(self, item):

        if self.count == self.size:
            return False

        self.buffer[self.tail] = item

        self.tail = (
            self.tail + 1
        ) % self.size

        self.count += 1

        return True

    # =========================
    # Pop
    # =========================

    def pop(self):

        if self.count == 0:
            return None

        item = self.buffer[self.head]

        self.buffer[self.head] = None

        self.head = (
            self.head + 1
        ) % self.size

        self.count -= 1

        return item

    # =========================
    # Empty Check
    # =========================

    def is_empty(self):

        return self.count == 0