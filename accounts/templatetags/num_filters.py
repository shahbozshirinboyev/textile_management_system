"""
Custom template filters for number formatting.

Usage in templates:
    {% load num_filters %}
    {{ value|num }}          → 1 234 567       (integer, space-separated thousands)
    {{ value|money }}        → 1 234 567 so'm  (money with suffix)
    {{ value|numf }}         → 1 234 567.89    (decimal, 2 places, space-separated)
"""
from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()


def _format_number(value, decimal_places=0):
    """Core formatter: returns string with space as thousands separator."""
    if value is None or value == '':
        return '—'
    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return str(value)

    if decimal_places == 0:
        # Round to integer
        formatted = f'{int(round(d)):,}'
    else:
        formatted = f'{d:,.{decimal_places}f}'

    # Replace comma thousands separator with space
    return formatted.replace(',', ' ')


@register.filter
def num(value):
    """Integer with space-separated thousands. e.g. 1234567 → 1 234 567"""
    return _format_number(value, decimal_places=0)


@register.filter
def numf(value, decimal_places=2):
    """Decimal with space-separated thousands. e.g. 1234567.89 → 1 234 567.89"""
    try:
        decimal_places = int(decimal_places)
    except (TypeError, ValueError):
        decimal_places = 2
    return _format_number(value, decimal_places=decimal_places)


@register.filter
def money(value):
    """Integer money with 'so'm' suffix. e.g. 1234567 → 1 234 567 so'm"""
    formatted = _format_number(value, decimal_places=0)
    if formatted == '—':
        return formatted
    return f"{formatted} so'm"
