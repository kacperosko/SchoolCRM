from django import template
import json
from django.utils.safestring import mark_safe
import calendar

register = template.Library()
WEEKDAYS_NAMES = ['Poniedzia\u0142ek', 'Wtorek', '\u015Aroda', 'Czwartek', 'Pi\u0105tek', 'Sobota', 'Niedziela']


@register.filter
def weekdays(value):
    return WEEKDAYS_NAMES


@register.filter
def get_weekday(index):
    return WEEKDAYS_NAMES[index]


MONTH_NAMES = [
    "Stycze\u0144", "Luty", "Marzec", "Kwiecie\u0144",
    "Maj", "Czerwiec", "Lipiec", "Sierpie\u0144",
    "Wrzesie\u0144", "Pa\u017Adziernik", "Listopad", "Grudzie\u0144"
]


@register.filter
def get_month_name(month_number):
    return MONTH_NAMES[month_number - 1]


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


@register.filter(name='ifinlist')
def ifinlist(value, temp_list):
    return str(value) in temp_list


@register.filter(name='verbose_name')
def verbose_name(instance):
    return instance._meta.verbose_name


@register.filter(name='initials')
def initials(full_name):
    if not full_name:
        return ""

    names = full_name.split()
    initials = ''.join([name[0].upper() for name in names])
    return initials


@register.filter(name='get_model_name')
def get_model_name(obj, language):
    if hasattr(obj, 'get_model_name'):
        return obj.get_model_name(language)
    return obj.__class__.__name__
