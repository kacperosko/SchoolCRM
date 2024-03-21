from django import template
import json
from django.utils.safestring import mark_safe
import calendar

register = template.Library()


@register.filter
def weekdays(value):
    return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


@register.filter
def get_month_name(month_number):
    return calendar.month_name[month_number]


@register.filter(is_safe=True)
def jsonify(json_object):
    """
    Output the json encoding of its argument.
    This will escape all the HTML/XML special characters with their unicode
    escapes, so it is safe to be output anywhere except for inside a tag
    attribute.
    If the output needs to be put in an attribute, entitize the output of this
    filter.
    """

    json_str = json.dumps(json_object)

    # Escape all the XML/HTML special characters.
    escapes = ["<", ">", "&"]
    for c in escapes:
        json_str = json_str.replace(c, r"\u%04x" % ord(c))

    # now it's safe to use mark_safe
    return mark_safe(json_str)


@register.filter(name='get_dict_value')
def get_dict_value(dictionary, key):
    """
    Custom template filter to retrieve a value from a dictionary based on the input key.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    else:
        return ''
