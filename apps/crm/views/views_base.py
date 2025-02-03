import time
from django.http import Http404
from django.apps import apps
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from apps.crm.models import Student, Lesson, LessonAdjustment, Person, StudentPerson, Note, Notification, WatchRecord, \
    Location, LessonStatutes, Group, GroupStudent, AttendanceList, AttendanceListStudent, Invoice, InvoiceItem, Event, LessonDefinition
from apps.service_helper import get_model_object_by_prefix, get_model_by_prefix, check_is_admin, check_permission, \
    custom_404, custom_500
from django.core.serializers import serialize
import json
from django.contrib.auth import authenticate, login, logout
from apps.crm.forms import PersonForm, LessonModuleForm, LessonPlanForm, LessonCreateForm, \
    StudentPersonAddForm, LocationForm, StudentForm, get_form_class, StudentpersonForm, GroupstudentForm, \
    AttendancelistForm
from apps.authentication.models import User
from datetime import datetime, timedelta, date, time
from time import sleep
from django.db.models import Q, Count, Sum
from calendar import monthrange
from collections import defaultdict
from django.utils import timezone as dj_timezone
from apps.crm.lesson_handler import count_lessons_for_student_in_year, create_lesson_adjustment, \
    get_lessons_for_teacher_in_year, get_lessons_for_location_in_year, count_lessons_for_group_in_year, \
    count_lessons_for_student_in_month, count_lessons_for_teacher_in_day, get_today_teacher_lessons, get_student_lessons_in_month, get_student_lessons_in_year
from django.contrib import messages
from django.http.response import JsonResponse
from django.contrib.contenttypes.models import ContentType
from babel.dates import format_datetime
from django.utils.timesince import timesince
from django.utils.timezone import now
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from functools import wraps
from django.db import transaction
from django.contrib.admin.models import LogEntry
import os
from apps.crm.templatetags.crm_tags import get_month_name
