import time
from contextlib import contextmanager


# Context manager that prints time taken in milliseconds, using nano time
@contextmanager
def timed():
    start = time.time_ns()
    yield
    end = time.time_ns()
    print(f"Time taken: {(end-start)/1000000}ms")