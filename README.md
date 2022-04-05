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

## Demo

Try running `python3 example_server.py`, as a very very basic demonstration of how you'd provide a single global rate limit for all consumers. In a real-world scenario, you'd probably have the following differences:

1. You'd probably write a middleware handler for whatever actual framework you're using.
2. You'd have a global rate limit AND authenticate requests for per-user limits.
3. Again, you'd be using a shared cache service for this data. I haven't done this specific thing in Redis, but it looks like you'd be doing a ZREMRANGEBYSCORE followed by a ZCOUNT for `is_exceeded()`, and a ZADD for `record()`. You could also have a subtly more aggressive limiting policy by always recording, _then_ only proceeding if you haven't exceeded the rate limit - this would be a lot more conservative about letting requests through in race condition scenarios. There might be a better way to make the operations atomic, though, and that would be a fun project to explore in its own right.