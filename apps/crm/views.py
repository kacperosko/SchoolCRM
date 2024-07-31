import time
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from .models import Student, Lesson, LessonAdjustment, Person, StudentPerson, Note, Notification, WatchRecord, Location, \
    Statutes, get_model_by_prefix, get_model_object_by_prefix, Group, GroupStudent
from django.core.serializers import serialize
import json
from django.contrib.auth import authenticate, login, logout
from .forms import PersonForm, LessonModuleForm, LessonPlanForm, LessonCreateForm, \
    StudentPersonAddForm, LocationForm, StudentForm, get_form_class, StudentpersonForm, GroupstudentForm
from apps.authentication.models import User
from datetime import datetime, timedelta, date, time
from time import sleep
from django.db.models import Q, Count
from calendar import monthrange
from collections import defaultdict
from django.utils import timezone as dj_timezone
from .lesson_handler import count_lessons_for_student_in_months, create_lesson_adjustment, \
    get_lessons_for_teacher_in_months, get_lessons_for_location_in_months
from django.contrib import messages
from django.http.response import JsonResponse
from django.contrib.contenttypes.models import ContentType
from babel.dates import format_datetime
from django.utils.timesince import timesince
from django.utils.timezone import now
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from functools import wraps

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def custom_404(request, exception):
    print("custom 404", request.path, exception)
    messages.error(request, exception)
    return render(request, 'auth/404.html', status=404)


def custom_500(request):
    print("custom 505", request.path)
    return render(request, 'auth/404.html', status=505)


def check_permission(perm_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_perm(perm_name):
                return custom_404(request, "Nie masz odpowiednich uprawnie\u0144")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def crmHomePage(request):
    return render(request, "crm/index.html", {})
    # return redirect("/student")


@check_permission('crm.view_student')
def all_students(request):
    students_list = Student.objects.all().order_by("-last_name").order_by("-first_name")
    context = {'students': students_list}
    print(request.user.get_session_auth_hash())
    return render(request, "crm/students.html", context)


@check_permission('crm.view_person')
def view_contacts(request):
    persons_list = Person.objects.all()
    related_students = StudentPerson.objects.filter(person__in=persons_list).select_related('student')
    students_by_person = {}

    for student_person in related_students:
        if student_person.person_id not in students_by_person:
            students_by_person[student_person.person_id] = []
        students_by_person[student_person.person_id].append(student_person.student.get_full_name())

    for person in persons_list:
        person.students = ", ".join(students_by_person.get(person.id, []))

    context = {'persons': persons_list}
    return render(request, "crm/persons.html", context)


def calendar(request):
    selected_record_id = request.GET.get("selected_record_id", request.user.id)
    try:
        model_name = get_model_by_prefix(str(selected_record_id)[:3])
        if model_name is None:
            raise Exception(f'Nie znaleziono modelu dla id {selected_record_id}')
    except Exception as e:
        messages.error(request, e)
        return render(request, 'crm/calendar.html', {})

    selected_year = int(request.GET.get("selected_year", datetime.now().year))
    selected_start_date = request.GET.get("selected_start_date", None)

    if not request.GET._mutable:
        request.GET._mutable = True

    teachers = User.objects.all()
    locations = Location.objects.all()

    if model_name == 'Location':
        selected_record = Location.objects.get(id=selected_record_id)
        lesson_result = get_lessons_for_location_in_months(selected_record_id, selected_year)
        locations = locations.exclude(id=selected_record_id)

    else:
        selected_record = User.objects.get(id=selected_record_id)
        lesson_result = get_lessons_for_teacher_in_months(selected_record_id, selected_year)
        teachers = teachers.exclude(id=selected_record_id)

    lessons = lesson_result['lessons']
    lesson_adjustments = lesson_result['adjustments']

    # Construct a dictionary to hold lesson adjustments data
    lesson_adjustments_data = {}
    for l_adjustment in lesson_adjustments:
        lesson_id = l_adjustment.lesson.id
        if lesson_id not in lesson_adjustments_data:
            lesson_adjustments_data[lesson_id] = []
        lesson_adjustments_data[lesson_id].append({
            'id': l_adjustment.id,
            'lessonDate': str(l_adjustment.modified_start_time.date()),
            'originalLessonDate': str(l_adjustment.original_lesson_date.date()),
            'lessonScheduleId': l_adjustment.lesson.id,
            'startTime': l_adjustment.modified_start_time.strftime('%H:%M'),
            'endTime': l_adjustment.modified_end_time.strftime('%H:%M'),
            'status': l_adjustment.status,
            'teacher': l_adjustment.teacher.get_full_name(),
            'description': l_adjustment.lesson.description,
            'location': l_adjustment.location.get_full_name(),
        })
    # Construct a list of dictionaries with lesson data
    lesson_data = []
    for lesson in lessons:
        lesson_adjustments_for_lesson = lesson_adjustments_data.get(lesson.id, [])
        lesson_data.append({
            'id': lesson.id,
            'weekDay': WEEKDAYS[lesson.start_time.weekday()],
            'startTime': lesson.start_time.strftime('%H:%M'),
            'endTime': lesson.end_time.strftime('%H:%M'),
            'startDate': str(lesson.start_time.date()),
            'endDate': str(lesson.series_end_date) if lesson.series_end_date else None,
            'student': lesson.student.get_full_name(),
            'student_id': lesson.student.id,
            'teacher': lesson.teacher.get_full_name(),
            'adjustments': lesson_adjustments_for_lesson,
            'description': lesson.description,
            'is_series': lesson.is_series,
            'location': lesson.location.get_full_name(),
        })

    # Pass lesson_data to the template context
    context = {
        'lessons': lesson_data,
        'selected_record': selected_record,
        'selected_record_id': selected_record_id,
        'teachers': teachers,
        'locations': locations
    }

    request.GET['selected_record_id'] = selected_record_id
    request.GET['selected_year'] = selected_year
    if selected_start_date is not None and selected_start_date != "" and selected_start_date != "null":
        request.GET['selected_start_date'] = selected_start_date

    return render(request, "crm/calendar.html", context)


class StudentPage(View):
    @staticmethod
    @check_permission('crm.view_student')
    def post(request, *args, **kwargs):
        student_id = kwargs['student_id']
        tab_name = request.GET.get("tab", "Details")
        opened_months = request.GET.get("opened_months", "")
        selected_year = request.GET.get("selected_year", datetime.now().year)
        if request.method == 'POST':
            if 'edit_form_submit' in request.POST:
                print('edit_form_submit')
                form = LessonModuleForm(request.POST)
                if form.is_valid():

                    create_lesson_adjustment(form, is_edit=form.cleaned_data['isAdjustment'])

                    lesson_date = dj_timezone.make_aware(
                        datetime.combine(form.cleaned_data['lessonDate'], datetime.min.time()))

                    messages.success(request, 'Zaktualizowano lekcje pomy\u015Blnie!')

                else:
                    messages.error(request, f'B\u0142\u0105d podczas zapisywania: {form.errors}')
                return redirect(
                    f'/student/{student_id}?tab={tab_name}&opened_months={opened_months}&selected_year={selected_year}')
            elif 'create_lesson_form_submit' in request.POST:
                print('create_form_submit')
                form = LessonCreateForm(request.POST)
                if form.is_valid():
                    start_time = form.cleaned_data['startTime']
                    lesson_duration = int(form.cleaned_data['lessonDuration'])
                    lesson_date = form.cleaned_data['lessonDate']
                    repeat = form.cleaned_data['repeat']
                    is_series = repeat != 'never'
                    description = form.cleaned_data['description']
                    teacher_id = form.cleaned_data['teacher']
                    location_id = form.cleaned_data['location']
                    end_series = None
                    if is_series:
                        end_series = form.cleaned_data['end_series']

                    start_datetime = datetime.combine(lesson_date, start_time)
                    end_datetime = start_datetime + timedelta(minutes=lesson_duration)

                    lesson = Lesson.objects.create(student_id=student_id, start_time=start_datetime,
                                                   end_time=end_datetime,
                                                   is_series=is_series, teacher_id=teacher_id,
                                                   description=description, series_end_date=end_series,
                                                   location_id=location_id)
                    lesson_msg = 'Seria lekcji' if is_series else 'Lekcja'
                    messages.success(request, f'{lesson_msg} dodana pomy\u015Blnie!')
                else:
                    messages.error(request, f'B\u0142ad podczas zapisywania: {form.errors}')
                return redirect(
                    f'/student/{student_id}?tab={tab_name}&opened_months={opened_months}&selected_year={selected_year}')
            else:
                messages.error(request, f'Nieobs\u0142ugiwany formularz: {request.POST}')
                return render(request, "crm/student-page.html", context)

    @staticmethod
    @check_permission('crm.view_student')
    def get(request, *args, **kwargs):
        context = {}

        student_id = kwargs.get('student_id')
        tab_name = request.GET.get("tab", "Details")
        opened_months = request.GET.get("opened_months", "")
        selected_year = int(request.GET.get("selected_year", datetime.now().year))

        request.GET = request.GET.copy()
        request.GET.update({
            'tab': tab_name,
            'opened_months': opened_months,
            'selected_year': selected_year,
        })

        try:
            student = Student.objects.get(id=student_id)

            student_persons = StudentPerson.objects.filter(student_id=student_id)

            model_name = get_model_by_prefix(student.id[:3])
            user_watch_record = WatchRecord.objects.filter(
                user=request.user, content_type__model=model_name.lower(), object_id=student_id
            ).first()

            notes = student.notes.all()
            context.update({
                'record': student,
                'notes': notes,
                'student_persons': student_persons,
                'watch_record': user_watch_record,
                'users': User.objects.all(),
                'locations': Location.objects.all(),
                'user': request.user,
            })
        except Student.DoesNotExist as e:
            print('StudentPage exception', e)
            messages.error(request, f'Nie znaleziono Studenta z id {student_id}')
            return redirect('/student')
        except Exception as e:
            print('StudentPage exception', e)
            messages.error(request, f'StudentPage exception: {e}')
            return custom_404(request, e)

        return render(request, "crm/student-page.html", context)


class StudentPersonCreate(View):
    @staticmethod
    def post(request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        context = {}

        form = StudentPersonAddForm(request.POST)
        if form.is_valid():
            person_id = form.cleaned_data['person']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone')
            relationship_type = form.cleaned_data['relationship_type']

            try:
                if person_id == 'new':
                    person = Person.objects.create(first_name=first_name, last_name=last_name, phone=phone, email=email)
                else:
                    person = get_object_or_404(Person, id=person_id)

                student_person = StudentPerson.objects.create(person=person, relationship_type=relationship_type,
                                                              student_id=student_id)
                messages.success(request, f'Relacja z {student_person.person.get_full_name()} utworzona')
            except Exception as e:
                print(e)
                messages.error(request, f'Error podczas tworzenia relacji: {e}')
                return redirect(f'/student/{student_id}')

            return redirect(f'/student/{student_id}')
        else:
            context['form'] = form
            context['message'] = form.errors

        context['student'] = get_object_or_404(Student, id=student_id)
        return render(request, "crm/student-person-create.html", context)

    @staticmethod
    def get(request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        context = {}

        try:
            context['student'] = get_object_or_404(Student, id=student_id)
            context['persons'] = Person.objects.all()
        except Exception as e:
            return custom_404(request, e)

        return render(request, "crm/student-person-create.html", context)


@check_permission('crm.view_lesson')
def view_student_lesson_series(request, student_id):
    context = {
        'lessons': Lesson.objects.filter(student_id=student_id).order_by('start_time'),
        'student': Student.objects.get(id=student_id)
    }

    return render(request, "crm/student-lesson-series.html", context)


@check_permission('crm.view_person')
def view_person(request, person_id):
    context = {}
    tab_name = request.GET.get("tab", "Details")

    request.GET = request.GET.copy()
    request.GET['tab'] = tab_name

    try:
        person = get_object_or_404(Person, id=person_id)
        context['person'] = person
    except Exception as e:
        print(e)
        return HttpResponse(status=404)

    return render(request, 'crm/person-page.html', context)


def upsert_note(request):
    status = False
    message = ""
    note_data = None

    try:
        record_id = request.POST.get("record_id")
        content = request.POST.get("content")
        note_id = request.POST.get("note_id")

        if not content:
            message = "Tre\u015B\u0107 nie mo\u017Ce by\u0107 pusta"
            raise ValueError(message)

        if note_id:  # Update existing note
            try:
                note = Note.objects.get(id=note_id)
                note.content = content
                note.created_at = now()
                note.created_by = request.user
                note.save()
            except Note.DoesNotExist:
                message = "Notatka nie istnieje"
                raise
            except Exception as e:
                message = str(e)
                raise
        else:  # Create new note
            try:
                model_name = get_model_by_prefix(record_id[:3])
                if not model_name:
                    message = "Nie wspierany model"
                    raise ValueError(message)

                content_type = ContentType.objects.get(model=model_name.lower(), app_label='crm')

                note = Note.objects.create(
                    content=content,
                    content_type=content_type,
                    object_id=record_id,
                    created_by=request.user
                )
            except ContentType.DoesNotExist:
                message = "Nie znaleziono typu zawarto\u015Bci"
                raise
            except Exception as e:
                message = str(e)
                raise

        formatted_created_at = format_datetime(note.created_at, "d MMMM YYYY HH:mm", locale='pl')
        note_data = {
            'note_id': note.id,
            'content': note.content,
            'created_at': formatted_created_at,
            'created_by': note.created_by.get_full_name(),
        }
        status = True

    except Exception as e:
        print('Create note error:', e)
        if not message:
            message = str(e)

    return JsonResponse({'status': status, 'message': message, 'note': note_data})


def delete_note(request):
    status = False
    message = ""

    try:
        note_id = request.POST.get("note_id")
        if not note_id:
            message = "Nie mo\u017Cna odczyta\u0107 notatki"
            raise ValueError(message)

        try:
            note = Note.objects.get(id=note_id)
            note.delete()
            status = True
            message = "Notatka zosta\u0142a usuni\u0119ta"
        except Note.DoesNotExist:
            message = "Notatka nie istnieje"
        except Exception as e:
            message = str(e)

    except ValueError as ve:
        message = str(ve)
    except Exception as e:
        message = str(e)

    return JsonResponse({'status': status, 'message': message})


# TODO to delete
def format_timesince(created_at):
    # Calculate the dirrence beetwen now and created day
    timesince_value = timesince(created_at)

    # If the time difference is less than one day return "X minutes ago"
    if timesince_value.startswith("0 minutes") or timesince_value.startswith("0 minut"):
        return "Teraz"
    elif "day" in timesince_value:
        return timesince_value.replace(",", "").split(" ")[0] + " dni temu"
    else:
        return timesince_value + " temu"


def get_notifications(request):
    notifications_query = Notification.objects.filter(user=request.user).select_related('content_type').order_by(
        '-created_at')

    unread_notifications_count = notifications_query.filter(read=False).aggregate(count=Count('id'))['count']
    all_notifications_count = notifications_query.count()

    paginator = Paginator(notifications_query, 10)
    page_number = request.GET.get('notification_page', 1)
    notifications_page = paginator.page(page_number)
    notifications_data = notifications_page.object_list.values(
        'id', 'message', 'read', 'content_type__model', 'object_id', 'created_at'
    )

    notifications_list = []
    for notification in notifications_data:
        notifications_list.append({
            'id': notification['id'],
            'message': notification['message'],
            'read': notification['read'],
            'model_name': notification['content_type__model'],
            'record_id': notification['object_id'],
            'created_at': timesince(notification['created_at'])
        })

    response_data = {
        'notifications': notifications_list,
        'unread_notifications': unread_notifications_count,
        'all_notifications': all_notifications_count,
        'max_pages': paginator.num_pages
    }

    return JsonResponse(response_data)


def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Nie znaleziono powiadomienia'}, status=404)


def watch_record(request, mode, record_id):
    status = False
    message = ''

    model_name = get_model_by_prefix(record_id[:3])
    if not model_name:
        message = 'Ten rekord nie obs\u0142uguje tej funkcji'
        return JsonResponse({'status': status, 'message': message})

    model_name = model_name.lower()
    try:
        content_type = ContentType.objects.get(model=model_name, app_label='crm')

        if mode == 'follow':
            WatchRecord.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=record_id
            )
        elif mode == 'unfollow':
            user_watch_record = WatchRecord.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=record_id
            ).first()
            if user_watch_record:
                user_watch_record.delete()
            else:
                message = 'Rekord obserwacji nie istnieje'
                return JsonResponse({'status': status, 'message': message})
        else:
            message = 'Nieprawid\u0142owy tryb'
            return JsonResponse({'status': status, 'message': message})

        status = True
    except ContentType.DoesNotExist:
        message = 'Nieprawid\u0142owy typ zawarto\u015Bci'
    except Exception as e:
        message = str(e)

    return JsonResponse({'status': status, 'message': message})


@check_permission('crm.view_location')
def all_locations(request):
    locations_records = None
    try:
        locations_records = Location.objects.all()
    except Exception as e:
        custom_404(request, e)

    return render(request, 'crm/locations.html', {'locations': locations_records})


class LocationPage(View):
    @staticmethod
    @check_permission('crm.view_location')
    def post(request, *args, **kwargs):
        pass

    @staticmethod
    @check_permission('crm.view_location')
    def get(request, *args, **kwargs):
        context = {}
        location_id = None
        try:
            location_id = kwargs['location_id']
        except Exception as e:
            return custom_404(request, e)
        tab_name = request.GET.get("tab", "Details")
        if not request.GET._mutable:
            request.GET._mutable = True

        request.GET['tab'] = tab_name
        try:
            location = Location.objects.get(id=location_id)
            try:
                model_name = get_model_by_prefix(location.id[:3])
                user_watch_record = WatchRecord.objects.get(user=request.user, content_type__model=model_name.lower(),
                                                            object_id=location_id)
            except WatchRecord.DoesNotExist:
                user_watch_record = None

            notes = location.notes.all()
            context['notes'] = notes.order_by('-created_at')
            context['watch_record'] = user_watch_record
            context['record'] = location

        except ObjectDoesNotExist:
            messages.error(request, 'Nie znaleziono takiego rekordu')
            return redirect('/location')
        except Exception as e:
            return custom_404(request, e)

        return render(request, 'crm/location-page.html', context)


def get_student_lessons(request, student_id):
    status = False
    selected_year = int(request.GET.get('selected_year', datetime.now().year))

    lessons_count = count_lessons_for_student_in_months(student_id, selected_year)

    lessons_count_serializable = {}
    for key, value in lessons_count.items():
        lessons = {k: v.to_dict() for k, v in value['Lessons'].items()}
        lessons_count_serializable[key] = {
            Statutes.PLANNED: value[Statutes.PLANNED],
            Statutes.NIEOBECNOSC: value[Statutes.NIEOBECNOSC],
            Statutes.ODWOLANA_NAUCZYCIEL: value[Statutes.ODWOLANA_NAUCZYCIEL],
            Statutes.ODWOLANA_24H_PRZED: value[Statutes.ODWOLANA_24H_PRZED],
            'Lessons': lessons
        }
    status = True

    return JsonResponse({'status': status, 'lessons': lessons_count_serializable})


def delete_record(request, record_id):
    context = {}
    redirect_url = None
    model_name = get_model_by_prefix(record_id[:3])
    if model_name is not None:
        if not request.user.has_perm(f'crm.delete_{model_name.lower()}'):
            messages.error(request, 'Brak uprawnie\u0144 do usuni\u0119cia rekordu')
            return redirect(f'/{model_name.lower()}/{record_id}')

        model_object = get_model_object_by_prefix(record_id[:3])
        try:
            record = model_object.objects.get(id=record_id)
        except ObjectDoesNotExist:
            # messages.error(f'Rekord z podanym id nie istnieje: {record_id}')
            return custom_404(request, f'Rekord z podanym id nie istnieje: {record_id}')
        if callable(getattr(record, 'redirect_after_delete', None)):
            redirect_url = record.redirect_after_delete()
        if request.method == 'GET':
            context['model_name'] = model_name.lower()
            context['record'] = record
            context['record_id'] = record_id
            if callable(getattr(record, 'redirect_after_edit', None)):
                context['redirect_url'] = record.redirect_after_edit()
            else:
                context['redirect_url'] = f'/{model_name.lower()}/{record.id}'

            exception_model_url = ['lesson', 'studentperson']
            if model_name.lower() in exception_model_url:
                context['redirect_model_url'] = record.redirect_after_edit()
            else:
                context['redirect_model_url'] = f'/{model_name.lower()}'

            context['record_id'] = record_id
            return render(request, 'crm/record-delete.html', context)

        if request.method == 'POST':
            record.delete()
            messages.success(request, 'Rekord usuni\u0119ty')
            if redirect_url:
                return redirect(redirect_url)
            else:
                return redirect(f'/{model_name.lower()}')
    else:
        return custom_404(request, "Nie mo\u017Cna usun\u0105\u0107 wybranego rekordu")


def upsert_record(request, model_name, record_id=None):
    context = {
        'record_id': record_id,
        'model_name': model_name,
        'title': None,
        'form': None,
        'redirect_url': None,
        'message': None
    }

    form_name = f"{model_name.capitalize()}Form"

    try:
        form_class = get_form_class(form_name)
    except Exception as e:
        print("ERROR:", e)
        messages.error(request, "Wyst\u0105pi\u0142 b\u0142\u0105d podczas \u0142adowania formularza.")
        return redirect(f'/{model_name.lower()}/{record_id}' if record_id else f'/{model_name.lower()}')

    context['title'] = form_class.get_name()

    record = None

    if record_id:
        if not request.user.has_perm(f'crm.change_{model_name.lower()}'):
            messages.error(request, 'Brak uprawnie\u0144 do edytowania rekordu')
            return redirect(f'/{model_name.lower()}/{record_id}')

        model_instance = get_model_object_by_prefix(record_id[:3])
        try:
            record = model_instance.objects.get(id=record_id)
        except model_instance.DoesNotExist:
            messages.error(request, 'Rekord nie istnieje')
            return redirect(f'/{model_name.lower()}')
    else:
        if not request.user.has_perm(f'crm.add_{model_name.lower()}'):
            messages.error(request, 'Brak uprawnie\u0144 do utworzenia rekordu')
            return redirect(f'/{model_name.lower()}')

    if request.method == 'GET':
        form_instance = form_class(instance=record) if record else form_class()
        data = request.GET.dict()
        if form_instance and callable(getattr(form_instance, 'update_form', None)) and len(data) > 0:
            form_instance.update_form(data=data)
        context['form'] = form_instance
        if record and callable(getattr(record, 'redirect_after_edit', None)):
            context['redirect_url'] = record.redirect_after_edit()
    
    if 'discard_url' in request.GET:
        context['redirect_url'] = request.GET.get('discard_url')

    if request.method == 'POST':
        form = form_class(request.POST, instance=record)
        context['form'] = form
        if form.is_valid():
            try:
                saved_instance = form.save()
                messages.success(request, 'Rekord zapisany pomy\u015Blnie')

                redirect_url = (
                    saved_instance.redirect_after_edit()
                    if saved_instance and callable(getattr(saved_instance, 'redirect_after_edit', None))
                    else f'/{get_model_by_prefix(saved_instance.id[:3]).lower()}/{saved_instance.id}'
                )
                return redirect(redirect_url)
            except Exception as e:
                print('exception')
                messages.error(request, f'Wyst\u0105pi\u0142 b\u0142\u0105d podczas zapisywania rekordu: {e}')
        else:
            print('errors')
            print(form.errors)
            context['message'] = form.errors

    return render(request, "crm/record-update-create.html", context)


@check_permission('crm.view_group')
def all_groups(request):
    groups = Group.objects.annotate(student_count=Count('group_student_group_relationship'))

    context = {"groups": groups}

    return render(request, "crm/groups.html", context)


@check_permission('crm.view_group')
def view_group(request, group_id):
    context = {}

    tab_name = request.GET.get("tab", "Details")
    opened_months = request.GET.get("opened_months", "")
    selected_year = int(request.GET.get("selected_year", datetime.now().year))

    request.GET = request.GET.copy()
    request.GET.update({
        'tab': tab_name,
        'opened_months': opened_months,
        'selected_year': selected_year,
    })

    try:
        group = Group.objects.get(id=group_id)

        model_name = get_model_by_prefix(group.id[:3])
        user_watch_record = WatchRecord.objects.filter(
            user=request.user, content_type__model=model_name.lower(), object_id=group.id
        ).first()

        group_students = GroupStudent.objects.filter(group=group)
        print(group_students)

        notes = group.notes.all()
        context.update({
            'record': group,
            'group_students': group_students,
            'notes': notes,
            'watch_record': user_watch_record,
            'users': User.objects.all(),
            'locations': Location.objects.all(),
            'user': request.user,
        })
    except Group.DoesNotExist as e:
        messages.error(request, f'Nie znaleziono Grupy z id {student_id}')
        return redirect('/group')
    except Exception as e:
        messages.error(request, f'view_group exception: {e}')
        return custom_404(request, e)

    return render(request, "crm/group-page.html", context)
