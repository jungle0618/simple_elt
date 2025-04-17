from datetime import datetime,  timedelta
def time_round(dt: datetime) -> datetime.time:
    remainder = dt.minute % 15
    if remainder < 7.5:
        delta = -remainder
    else:
        delta = 15 - remainder
    rounded = dt.replace(second=0, microsecond=0) + timedelta(minutes=delta)
    return rounded.time()