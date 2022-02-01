from django import template

register = template.Library()

# check https://docs.djangoproject.com/en/4.0/howto/custom-template-tags/
# how to write custom tags

@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    return price * quantity
