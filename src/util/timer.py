import time
from contextlib import contextmanager
from typing import Optional


# Context manager that prints time taken in milliseconds, using nano time
@contextmanager
def timed(name: Optional[str] = None):
    start = time.time_ns()
    yield
    end = time.time_ns()
    suffix = f" by ({name})" if name else ""
    print(f"Time taken{suffix}: {(end-start)/1000000}ms")