import pytz

from datetime import datetime


def to_timestamp(dt):
    """ Take a datetime object and return a UTC timestamp.
    """
    epoch = datetime.fromtimestamp(0, pytz.utc)
    return int((dt - epoch).total_seconds())
