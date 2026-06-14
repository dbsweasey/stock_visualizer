import time


def get_bucket(timestamp: float, interval: int):
    return (timestamp // interval) * interval

def get_next_boundry(now, interval):
    bucket = get_bucket(now, interval)
    return bucket + interval

def current():
    return time.time()
