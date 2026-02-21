from django import template

register = template.Library()

@register.filter
def short_indian(value):
    try:
        num = float(value)

        if num >= 10000000:
            return f"{num/10000000:.1f}Cr"
        elif num >= 100000:
            return f"{num/100000:.1f}L"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return f"{num:.0f}"
    except:
        return value
