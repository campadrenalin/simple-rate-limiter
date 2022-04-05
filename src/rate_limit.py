from time import perf_counter
from array import array
import sys

class LimitExceeded(Exception):
    def __init__(self, budget, window):
        super().__init__(f"Exceeded {budget} events in {window} seconds")

class RateLimiter(object):
    """
    This is a bit overengineered for the fun of it. The concept
    is actually pretty straightforward: have a circular buffer
    of event times, the same size as the maximum number of
    events permitted in the time window.

    This means that when you need to check if you've hit the
    limit, you only have to look at one recorded event (the
    least recent) and check if it was in the time window.
    Because either:

      1. It's inside the time window, so your entire buffer
         (event budget) is exhausted by stuff that happened
         in the time window. Or,
      2. It's outside the time window, so there's at least 1
         free slot in the budget.

    The overengineering comes from taking that idea and saying,
    "I wonder how I can reduce the overhead. To comical extremes."
    That's where using perf_counter for times, and preallocated
    arrays, comes from. This would probably be the right amount
    of engineering, more or less, if we knew we were going to use
    a lot of these objects to act on a per-client basis.

    Main use case: as a context manager.

    >>> rl = RateLimiter(200, 15.0) # 200 requests / 15s
    >>> with rl:
    ...     # Do business logic
    """

    __slots__ = ('buffer', 'window', '_n_events')

    def __init__(self, budget, window):
        if (budget < 1):
            raise ValueError("Must have budget of at least 1")
        if (window <= 0):
            raise ValueError("Must have a positive float duration for window")

        self.buffer = array('d', (0,)*budget)
        self.window = window
        self._n_events = 0

    @property
    def budget(self):
        return len(self.buffer)

    @property
    def write_pos(self):
        return self._n_events % self.budget

    @property
    def read_pos(self):
        return (self._n_events + 1) % self.budget

    def record(self, event_time=None):
        event_time = event_time or perf_counter()    
        self.buffer[self.write_pos] = event_time
        self._n_events += 1

    def is_exceeded(self, current_time=None):
        # Never even filled the buffer yet
        if self._n_events < self.budget:
            return False

        current_time = current_time or perf_counter()
        threshold = current_time - self.window
        least_recent_event = self.buffer[self.read_pos]
        return least_recent_event >= threshold

    def check(self, current_time=None):
        "Raise exception if rate is exceeded, otherwise record new event."
        current_time = current_time or perf_counter()
        if self.is_exceeded(current_time):
            raise LimitExceeded(self.budget, self.window)
        self.record(current_time)

    def __enter__(self):
        self.check()

    def __exit__(self, *exc_data):
        pass
