from django import template

register = template.Library()

EN_TO_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

@register.filter(name='persian_numbers')
def persian_numbers(value):
    if not isinstance(value, str):
        value = str(value)
    return value.translate(EN_TO_FA)
