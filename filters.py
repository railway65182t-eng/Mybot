from __future__ import annotations
import time
from collections import defaultdict, deque

class FloodGuard:
    def __init__(self, window_sec: int, max_msgs: int):
        self.window_sec = window_sec
        self.max_msgs = max_msgs
        self._messages: dict[tuple[int, int], deque[float]] = defaultdict(deque)

    def push(self, chat_id: int, user_id: int) -> bool:
        now = time.time()
        key = (chat_id, user_id)
        q = self._messages[key]
        q.append(now)
        while q and now - q[0] > self.window_sec:
            q.popleft()
        return len(q) > self.max_msgs
