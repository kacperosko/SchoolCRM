import uuid

from django.db import models

from apps.authentication.models import User
from functools import wraps
from django.contrib import messages
from django.shortcuts import render


def get_model_object_by_prefix(prefix):
    from apps.crm.models import Person, Student, StudentPerson, Lesson, LessonAdjustment, Location, Note, WatchRecord, \
        Notification, Group, GroupStudent, AttendanceList, Invoice,  LessonDefinition, Event


    prefixes = {
        '0PR': Person,
        '0ST': Student,
        '0SP': StudentPerson,
        '0LS': Lesson,
        '0LA': LessonAdjustment,
        '0LC': Location,
        '0NT': Note,
        '0WR': WatchRecord,
        '0NF': Notification,
        '0US': User,
        '0GR': Group,
        '0GS': GroupStudent,
        '0AS': AttendanceList,
        '0IV': Invoice,
        '0LD': LessonDefinition,
        '0LE': Event,
    }
    return prefixes.get(prefix, None)


def get_model_by_prefix(prefix):
    prefixes = {
        '0PR': 'Person',
        '0ST': 'Student',
        '0SP': 'StudentPerson',
        '0LS': 'Lesson',
        '0LA': 'LessonAdjustment',
        '0LC': 'Location',
        '0NT': 'Note',
        '0WR': 'WatchRecord',
        '0NF': 'Notification',
        '0US': 'User',
        '0GR': 'Group',
        '0GS': 'GroupStudent',
        '0AS': 'AttendanceList',
        '0IV': 'Invoice',
        '0LD': 'LessonDefinition',
        '0LE': 'Event',
    }
    return prefixes.get(prefix, None)


def get_prefix_by_model(model_name):
    prefixes = {
        'Person': '0PR',
        'Student': '0ST',
        'StudentPerson': '0SP',
        'Lesson': '0LS',
        'LessonAdjustment': '0LA',
        'Location': '0LC',
        'Note': '0NT',
        'WatchRecord': '0WR',
        'Notification': '0NF',
        'User': '0US',
        'Group': '0GR',
        'GroupStudent': '0GS',
        'AttendanceList': '0AS',
        'Invoice': '0IV',
        'LessonDefinition': '0LD',
        'Event': '0LE',
    }
    return prefixes.get(model_name, '0EX')


class PrefixedUUIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 39)  # 3 (prefix) + 29 (UUID) = 32
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        self.model = cls
        self.prefix = get_prefix_by_model(cls.__name__)

    def pre_save(self, model_instance, add):
        if add and not getattr(model_instance, self.attname):
            value = f"{self.prefix}{uuid.uuid4()}"
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)


def custom_404(request, exception):
    messages.error(request, exception)
    return render(request, 'auth/404.html', status=404)


def custom_500(request):
    return render(request, 'auth/404.html', status=505)


def check_is_admin(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin:
            return custom_404(request, "Nie masz odpowiednich uprawnień")
        return func(request, *args, **kwargs)
    return wrapper


def check_permission(perm_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_perm(perm_name):
                return custom_404(request, "Nie masz odpowiednich uprawnie\u0144")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
