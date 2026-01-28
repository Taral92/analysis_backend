"""
Helper utility functions.
"""
from datetime import datetime, timedelta
from typing import List, Tuple
import pytz


def get_date_range(days: int = 30) -> Tuple[datetime, datetime]:
    """
    Get date range for last N days.
    Returns (start_date, end_date)
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def get_hour_ranges() -> List[int]:
    """Get list of hours (0-23)."""
    return list(range(24))


def get_day_of_week_name(day_number: int) -> str:
    """Convert day number to name (0=Monday, 6=Sunday)."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[day_number]


def calculate_growth_rate(current: float, previous: float) -> float:
    """
    Calculate growth rate percentage.
    Returns: ((current - previous) / previous) * 100
    """
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / previous) * 100


def calculate_percentage(part: float, whole: float) -> float:
    """Calculate percentage safely."""
    if whole == 0:
        return 0.0
    return (part / whole) * 100


def round_currency(amount: float) -> float:
    """Round currency to 2 decimal places."""
    return round(amount, 2)


def extract_hour(dt: datetime) -> int:
    """Extract hour from datetime object."""
    return dt.hour


def extract_day_of_week(dt: datetime) -> int:
    """Extract day of week (0=Monday, 6=Sunday)."""
    return dt.weekday()


def format_date(dt: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str)


def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> datetime:
    """Parse string to datetime."""
    return datetime.strptime(date_str, format_str)


def is_weekend(dt: datetime) -> bool:
    """Check if date is weekend (Saturday=5, Sunday=6)."""
    return dt.weekday() >= 5


def moving_average(values: List[float], window: int = 7) -> List[float]:
    """Calculate moving average."""
    if len(values) < window:
        return values
    
    result = []
    for i in range(len(values)):
        if i < window - 1:
            result.append(values[i])
        else:
            window_values = values[i - window + 1:i + 1]
            result.append(sum(window_values) / window)
    
    return result


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is 0."""
    if denominator == 0:
        return default
    return numerator / denominator
