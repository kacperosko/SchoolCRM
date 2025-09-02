from django import template
import json
from django.utils.safestring import mark_safe
import calendar
from apps.service_helper import get_model_by_prefix
from ..models import LessonStatutes
import re

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
    initials_formatted = ''.join([name[0].upper() for name in names])
    return initials_formatted


@register.filter(name='get_model_name')
def get_model_name(obj, language):
    if hasattr(obj, 'get_model_name'):
        return obj.get_model_name(language)
    return obj.__class__.__name__


@register.filter(name='yes_no')
def yes_no(value):
    return "Tak" if value else "Nie"


@register.filter(name='get_model_name_by_id')
def get_model_name_by_id(model_id):
    return get_model_by_prefix(model_id[:3])


@register.filter
def get_first_segment(value):
    segments = value.split('/')
    return segments[1] if len(segments) > 1 else ''


@register.filter(name='get_status_color')
def get_status_color(status):
    if status == LessonStatutes.NIEOBECNOSC:
        return 'bg-danger-light text-danger'
    if status == LessonStatutes.ZAPLANOWANA:
        return 'bg-primary-light text-primary'
    if status == LessonStatutes.ODWOLANA_NAUCZYCIEL or status == LessonStatutes.ODWOLANA_24H_PRZED:
        return 'bg-warning-light text-warning'


@register.filter(name="phone_format")
def phone_format(value: str):
    if not value:
        return ""

    cleaned = re.sub(r"[^\d+]", "", str(value))

    if cleaned.startswith("+48") and len(cleaned) == 12:
        return f"+48 {cleaned[3:6]} {cleaned[6:9]} {cleaned[9:]}"

    if cleaned.startswith("48") and len(cleaned) == 11:
        return f"+48 {cleaned[2:5]} {cleaned[5:8]} {cleaned[8:]}"

    if len(cleaned) == 9:
        return f"{cleaned[0:3]} {cleaned[3:6]} {cleaned[6:]}"

    return cleaned