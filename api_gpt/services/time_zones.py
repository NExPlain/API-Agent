import datetime
from dateutil import tz


def get_current_iso_datetime():
    """
    Get the current datetime in ISO format with local timezone.

    Returns:
        str: ISO formatted datetime string.
    """
    # Get the current datetime with local timezone
    local_timezone = tz.tzlocal()
    current_datetime = datetime.datetime.now(local_timezone)

    # Convert to ISO format with timezone and UTC offset
    iso_datetime = current_datetime.isoformat()

    return iso_datetime
