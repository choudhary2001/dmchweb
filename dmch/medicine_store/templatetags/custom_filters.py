# medicine_store/templatetags/custom_filters.py

from django import template

register = template.Library()

# @register.filter
# def get_item(dictionary, key):
#     return dictionary.get(key, 0)

@register.filter
def subtract(value, arg):
    return value - arg