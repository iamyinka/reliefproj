from django import template

register = template.Library()


@register.filter
def currency(value):
    """Format a number as Nigerian Naira currency"""
    try:
        # Convert to float and format with commas
        amount = float(value)
        return f"₦{amount:,.0f}"
    except (ValueError, TypeError):
        return value