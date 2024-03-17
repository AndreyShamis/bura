import logging
from django import template

register = template.Library()

@register.filter
def get_percent(total: float, part: float) -> float:
    """
    Calculates the percentage of 'part' in 'total', rounded to 3 digits.
    Returns 0 if 'part' is 0.

    Args:
        total: The total value.
        part: The value to be compared.

    Returns:
        The percentage of 'part' in 'total', rounded to 3 digits, or 0 if 'part' is 0.
    """
    if total == 0:
        return 0
    return round(part / total * 100, 3)
