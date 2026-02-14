"""
Day boundary logic — extends "today" past midnight when enabled.
"""
from datetime import datetime, timedelta


def get_effective_date(timestamp=None, day_extension=False, cutoff_hour=3):
    """
    Return the effective date, respecting day-extension setting.

    If day_extension is enabled and current time is before cutoff_hour (e.g. 3AM),
    the effective date is still "yesterday" — the user hasn't gone to bed yet.

    Args:
        timestamp: datetime object (defaults to now)
        day_extension: bool, whether day extension is active
        cutoff_hour: int, hour threshold (0-6)

    Returns:
        str: 'YYYY-MM-DD' effective date
    """
    if timestamp is None:
        timestamp = datetime.now()

    if day_extension and timestamp.hour < cutoff_hour:
        effective = timestamp - timedelta(days=1)
    else:
        effective = timestamp

    return effective.strftime("%Y-%m-%d")


def get_effective_today(settings_dict):
    """
    Get today's effective date using the current settings.

    Args:
        settings_dict: dict with 'day_extension' and 'day_extension_hour' keys

    Returns:
        str: 'YYYY-MM-DD' effective date
    """
    day_ext = settings_dict.get("day_extension", "false") == "true"
    cutoff = int(settings_dict.get("day_extension_hour", "3"))
    return get_effective_date(day_extension=day_ext, cutoff_hour=cutoff)
