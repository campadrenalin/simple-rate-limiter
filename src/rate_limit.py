from time import perf_counter
from array import array

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
    arrays, comes from.
    """

    __slots__ = ('buffer', 'window', 'write_pos')

    def __init__(self, budget, window):
        if (budget < 1):
            raise ValueError("Must have budget of at least 1")
        if (window <= 0):
            raise ValueError("Must have a positive float duration for window")

        self.buffer = array('d', (0,)*budget)
        self.window = window
        self.write_pos = 0

    @property
    def next_pos(self):
        return (self.write_pos + 1) % len(self.buffer)

    def record(self, event_time=None):
        event_time = event_time or perf_counter()    
        self.buffer[self.write_pos] = event_time
        self.write_pos = self.next_pos

    def is_exceeded(self, current_time=None):
        current_time = current_time or perf_counter()
        threshold = current_time - self.window
        least_recent_event = self.buffer[self.next_pos]

        return least_recent_event >= threshold
