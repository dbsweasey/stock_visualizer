def get_bucket(timestamp: float, interval: int):
    return (timestamp // interval) * interval
