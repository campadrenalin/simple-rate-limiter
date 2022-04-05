import pytest
import time
from contextlib import contextmanager
from src import rate_limit

@contextmanager
def does_not_raise():
    yield

@pytest.mark.parametrize("budget,window,expectation", [
    (5, 18.0, does_not_raise()),
    (1, 100.333, does_not_raise()),
    (0, 1, pytest.raises(ValueError)),
    (20, -50, pytest.raises(ValueError)),
])
def test_init(budget, window, expectation):
    with expectation:
        rl = rate_limit.RateLimiter(budget, window)
        assert len(rl.buffer) == budget
        assert rl.buffer[0] == 0
        assert rl.window == window
        assert rl.write_pos == 0

def test_record():
    # 3 requests over 15 minutes capacity
    rl = rate_limit.RateLimiter(3, 15*60)
    rl.record(100)
    assert list(rl.buffer) == [100, 0, 0]
    assert rl.write_pos == 1
    
    rl.record(101)
    assert list(rl.buffer) == [100, 101, 0]
    assert rl.write_pos == 2

    rl.record(102)
    assert list(rl.buffer) == [100, 101, 102]
    assert rl.write_pos == 0

    rl.record(103)
    assert list(rl.buffer) == [103, 101, 102]
    assert rl.write_pos == 1

def test_record_default():
    rl = rate_limit.RateLimiter(3, 15*60)
    rl.record()
    assert 0 < time.perf_counter() - rl.buffer[0] < 0.1

@pytest.mark.parametrize("budget,window,events,current_time, exceeded", [
    (1, 10.0, [], 100.0, False),
    (1, 10.0, [100], 100.0, True),
    (1, 10.0, [100], 110.0, True),
    (1, 10.0, [100], 110.1, False),

    (3, 5.0, [], 200.0, False),
    (3, 5.0, [100,101,102], 103.0, True),
    (3, 5.0, [100,101,102,110], 111.0, False),
])
def test_is_exceeded(budget, window, events, current_time, exceeded):
    rl = rate_limit.RateLimiter(budget, window)
    for event in events:
        rl.record(event)
    
    assert rl.is_exceeded(current_time) == exceeded