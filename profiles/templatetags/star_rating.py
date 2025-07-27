from django import template
register = template.Library()

@register.filter
def fa_star_rating(value):
    try:
        value = float(value)
    except:
        return ''
    
    full_star = '<i class="fa-solid fa-star"></i>'
    half_star = '<i class="fa-solid fa-star-half-stroke"></i>'
    empty_star = '<i class="fa-regular fa-star"></i>'
    
    html = ''
    for i in range(1, 6):
        if value >= i:
            html += full_star
        elif value >= i - 0.5:
            html += half_star
        else:
            html += empty_star
    return html
