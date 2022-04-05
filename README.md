# A simple rate limiter

This is a space-efficient rate limiter. It's pretty short and readable, it's entirely process-local, and you'd probably want to use something backed by your cache subsystem (like Redis) instead of this in any real-world use case. But it does demonstrate the minimum amount of information you need to keep track of, for any non-probabalistic events-per-window rate limiter. And it's meant to be ergonomic to use:

```python
from rate_limit import RateLimiter, LimitExceeded
rl = RateLimiter(200, 15.0) # 200 requests / 15s

# As a context manager
with rl:
    do_business_logic()

# Or just the check(), to keep from overly indendenting
def on_request(...):
    try:
        rl.check()
        do_business_logic()
    except LimitExceeded:
        # Handle failure case
        pass
```