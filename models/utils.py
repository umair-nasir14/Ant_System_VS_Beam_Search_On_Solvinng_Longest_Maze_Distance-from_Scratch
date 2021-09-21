from time import time
from contextlib import contextmanager


@contextmanager
def measure_time(label):
    tb = time()
    yield
    te = time()
    print(f"Time {label}: {te - tb}")
