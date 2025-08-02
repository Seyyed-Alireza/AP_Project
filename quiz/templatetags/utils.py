from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def range_value(dictionary, key):
    return dictionary.get(key)['value']

@register.filter
def range_checked(dictionary, key):
    return dictionary.get(key)['idk']

@register.filter
def contains(value, arg):
    try:
        return arg in value
    except:
        return False
    
@register.filter
def addstr(value, arg):
    return f"{value}{arg}"