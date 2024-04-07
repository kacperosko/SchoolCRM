import time

from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from .models import Student, Lesson, LessonAdjustment, Person, StudentPerson
from django.core.serializers import serialize
import json
from django.contrib.auth import authenticate, login, logout
from .forms import UserCreationForm, LoginForm, StudentForm, LessonForm, LessonPlanForm, LessonCreateForm, StudentPersonForm
from .middleware.crm_middleware import login_exempt
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date, time
from time import sleep
from django.db.models import Q, Count
from calendar import monthrange
from collections import defaultdict
from django.utils import timezone as dj_timezone
from .lesson_handler import count_lessons_for_student_in_months, create_lesson_adjustment
from django.contrib import messages

MODES = ['view', 'edit']
WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def custom_404(request, exception):
    print("custom 404", request.path, exception)
    # return render(request, '404.html', status=404)
    return render(request, 'auth/404.html', status=404)


def custom_500(request):
    print("custom 505", request.path)
    # return render(request, '404.html', status=404)
    return render(request, 'auth/404.html', status=505)


# login page
@login_exempt
def user_login(request):
    message = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                next_url = request.GET.get("next", "/students")
                return redirect(next_url)
            else:
                message = 'Nazwa użytkownika lub hasło są niepoprawne'
                print(message)
                sleep(4)
    else:
        form = LoginForm()
    return render(request, 'auth/auth-sign-in.html', {'form': form, 'message': message})


class CRMHomePage(View):
    @staticmethod
    def post(request, *args, **kwargs):
        pass

    @staticmethod
    def get(request, *args, **kwargs):
        return redirect("/students")


def students(request):
    students_list = Student.objects.all()
    context = {'students': students_list}
    print(request.user.get_session_auth_hash())
    return render(request, "crm/students.html", context)


def calendar(request):
    # Fetch lessons associated with the current teacher
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            print(form)
            lessonDate = datetime.strptime(str(form.cleaned_data['lessonDate']), "%Y-%m-%d").date()
            lesson = LessonAdjustment.objects.create(lessonSchedule_id=form.cleaned_data['lessonSchedule'],
                                                     startTime=form.cleaned_data['startTime'],
                                                     endTime=form.cleaned_data['endTime'],
                                                     lessonDate=lessonDate,
                                                     originalLessonDate=lessonDate, status=form.cleaned_data['status'])
            print('lesson created ->', lesson.id)
            return redirect('/calendar')
        else:
            print('ERROR FORM', form.errors)

    lessons = Lesson.objects.filter(teacher=request.user)

    # Fetch lesson adjustments associated with fetched lessons
    lesson_adjustments = LessonAdjustment.objects.filter(lesson__in=lessons)

    # Construct a dictionary to hold lesson adjustments data
    lesson_adjustments_data = {}
    for l_adjustment in lesson_adjustments:
        print('l_Adjustment ->', l_adjustment.modified_start_time, l_adjustment.modified_end_time)
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
            'student': l_adjustment.lesson.student.student.get_full_name()
        })
    print(lesson_adjustments_data)
    # Construct a list of dictionaries with lesson data
    lesson_data = []
    for lesson in lessons:
        lesson_adjustments_for_lesson = lesson_adjustments_data.get(lesson.id, [])
        print(lesson_adjustments_for_lesson)
        student_name = f"{lesson.student.student.first_name} {lesson.student.student.last_name}"
        lesson_data.append({
            'id': lesson.id,
            'weekDay': WEEKDAYS[lesson.start_time.weekday()],
            'startTime': lesson.start_time.strftime('%H:%M'),
            'endTime': lesson.end_time.strftime('%H:%M'),
            'startDate': str(lesson.start_time.date()),
            'endDate': str(lesson.series_end_date) if lesson.series_end_date else None,
            'student': student_name,
            'adjustments': lesson_adjustments_for_lesson
        })

    # Pass lesson_data to the template context
    context = {
        'lessons': lesson_data,
    }

    return render(request, "crm/calendar.html", context)


def generate_series(lesson_schedule, lesson_adjustments: LessonAdjustment, year, return_type):
    generated_lessons = {}
    months_counter = {month: {'Pending': 0, 'Completed': 0, 'Canceled': 0, 'Summary': 0} for month in range(1, 13)}
    today = datetime.now()

    start_year = lesson_schedule.startDate.year
    end_year = lesson_schedule.endDate.year if lesson_schedule.endDate else date.today().year
    for target_year in range(start_year, end_year + 1):
        if target_year == int(year):
            start_month = lesson_schedule.startDate.month if target_year == start_year else 1
            end_month = lesson_schedule.endDate.month if target_year == end_year and lesson_schedule.endDate else 12

            for month in range(start_month, end_month + 1):
                num_days = monthrange(target_year, month)[1]
                # months_counter[month] = {}

                for day in range(1, num_days + 1):
                    current_date = date(target_year, month, day)
                    if lesson_schedule.startDate <= current_date <= (lesson_schedule.endDate or current_date):
                        weekday = current_date.strftime('%A')
                        if lesson_schedule.weekDay == weekday:
                            current_datetime = datetime.combine(current_date,
                                                                time(lesson_schedule.startTime.hour,
                                                                     lesson_schedule.startTime.minute))
                            if current_datetime <= today:
                                status = 'Completed'
                            else:
                                status = 'Pending'
                            # if month in months_counter:
                            #     if status in months_counter[month]:
                            months_counter[month][status] += 1
                            #     else:
                            #         months_counter[month][status] = 1
                            # else:
                            #     months_counter[month][status] = 1

                            generated_lessons[current_date.strftime('%d-%m-%Y')] = {
                                'startTime': lesson_schedule.startTime,
                                'endTime': lesson_schedule.endTime,
                                'status': status
                            }

    for lesson_adjustment in lesson_adjustments:
        if lesson_adjustment.originalLessonDate.strftime('%d-%m-%Y') in generated_lessons:
            current_datetime = datetime.combine(lesson_adjustment.originalLessonDate,
                                                time(lesson_adjustment.lessonSchedule.startTime.hour,
                                                     lesson_adjustment.lessonSchedule.startTime.minute))
            if current_datetime <= today:
                status = 'Completed'
            else:
                status = 'Pending'
            months_counter[lesson_adjustment.originalLessonDate.month][status] -= 1
            del generated_lessons[lesson_adjustment.originalLessonDate.strftime('%d-%m-%Y')]

        if lesson_adjustment.lessonDate.year == year:
            if lesson_adjustment.status == 'Canceled':
                status = lesson_adjustment.status
            else:
                current_datetime = datetime.combine(lesson_adjustment.lessonDate,
                                                    time(lesson_adjustment.startTime.hour,
                                                         lesson_adjustment.startTime.minute))
                if current_datetime <= today:
                    status = 'Completed'
                else:
                    status = 'Pending'
            # month = lesson_adjustment.lessonDate.month
            # if status in months_counter[month]:
            months_counter[lesson_adjustment.lessonDate.month][status] += 1
            # else:
            #     months_counter[month][status] = 1

            generated_lessons[lesson_adjustment.lessonDate.strftime('%d-%m-%Y')] = {
                'startTime': lesson_adjustment.startTime,
                'endTime': lesson_adjustment.endTime,
                'status': status
            }

    if return_type == 'counter':
        for month, statutes in months_counter.items():
            months_counter[month]['Summary'] = months_counter[month]['Canceled'] + months_counter[month]['Completed'] + \
                                               months_counter[month]['Pending']
        print(months_counter)
        return months_counter
    else:
        return generated_lessons


class StudentPage(View):
    @staticmethod
    def post(request, *args, **kwargs):
        student_id = kwargs['student_id']
        tab_name = request.GET.get("tab", "Details")
        opened_months = request.GET.get("opened_months", "")
        mode = request.GET.get("mode", "view")
        selected_year = request.GET.get("selected_year", datetime.now().year)
        if request.method == 'POST':
            if 'cancel_form_submit' in request.POST:
                print('cancel_form_submit')
                form = LessonForm(request.POST)
                print(form)
                if form.is_valid():
                    if form.cleaned_data['isAdjustment']:
                        print('isAdjustment')
                        leson_adjustment = LessonAdjustment.objects.get(id=form.cleaned_data['lessonId'])
                        leson_adjustment.status = form.cleaned_data['status']

                        leson_adjustment.save()
                        print('lesson adjustment canceled')
                    else:
                        print('NOT isAdjustment ')
                        create_lesson_adjustment(form)

                    messages.success(request, 'Odwołano lekcje pomyślnie!')
                else:
                    messages.error(request, f'Bład podczas zapisywania: {form.errors}')
                return redirect(
                    f'/students/{student_id}?tab={tab_name}&opened_months={opened_months}&mode={mode}&selected_year={selected_year}')
            elif 'edit_form_submit' in request.POST:
                print('edit_form_submit')
                form = LessonForm(request.POST)
                if form.is_valid():
                    if form.cleaned_data['isAdjustment']:
                        create_lesson_adjustment(form, is_edit=True)
                    else:
                        create_lesson_adjustment(form)

                    lesson_date = dj_timezone.make_aware(
                        datetime.combine(form.cleaned_data['lessonDate'], datetime.min.time()))

                    opened_months_list = [int(month) for month in opened_months.split(',') if month]

                    if lesson_date.month not in opened_months_list:
                        opened_months_list.append(lesson_date.month)
                        opened_months = ','.join(map(str, opened_months_list))

                    messages.success(request, 'Zaktualizowano lekcje pomyślnie!')

                else:
                    messages.error(request, f'Bład podczas zapisywania: {form.errors}')
                return redirect(
                    f'/students/{student_id}?tab={tab_name}&opened_months={opened_months}&mode={mode}&selected_year={selected_year}')
            elif 'create_form_submit' in request.POST:
                print('create_form_submit')
                form = LessonCreateForm(request.POST)
                if form.is_valid():
                    start_time = form.cleaned_data['startTime']
                    end_time = form.cleaned_data['endTime']
                    lesson_date = form.cleaned_data['lessonDate']
                    repeat = form.cleaned_data['repeat']
                    is_series = repeat != 'never'
                    description = form.cleaned_data['description']
                    end_series = None
                    if is_series:
                        end_series = form.cleaned_data['end_series']

                    start_datetime = datetime.combine(lesson_date, start_time)
                    end_datetime = datetime.combine(lesson_date, end_time)

                    lesson = Lesson.objects.create(student_id=student_id, start_time=start_datetime,
                                                   end_time=end_datetime,
                                                   is_series=is_series, teacher_id=request.user.id,
                                                   description=description, series_end_date=end_series)
                    lesson_msg = 'Seria lekcji' if is_series else 'Lekcja'
                    messages.success(request, f'{lesson_msg} dodana pomyślnie!')
                else:
                    messages.error(request, f'Bład podczas zapisywania: {form.errors}')
                return redirect(
                    f'/students/{student_id}?tab={tab_name}&opened_months={opened_months}&mode={mode}&selected_year={selected_year}')
            else:
                print('else form')
                form = LessonPlanForm(request.POST)
                if form.is_valid():
                    leson_adjustment = LessonAdjustment.objects.get(id=form.cleaned_data['lessonId'])
                    leson_adjustment.status = form.cleaned_data['status']

                    leson_adjustment.save()
                    print('lesson adjustment updated')
                    messages.success(request, 'Zaplanowano lekcje pomyślnie!')
                else:
                    messages.error(request, f'Bład podczas zapisywania: {form.errors}')
                return redirect(
                    f'/students/{student_id}?tab={tab_name}&opened_months={opened_months}&mode={mode}&selected_year={selected_year}')

    @staticmethod
    def get(request, *args, **kwargs):
        student_id = kwargs['student_id']
        context = {}
        tab_name = request.GET.get("tab", "Details")
        opened_months = request.GET.get("opened_months", "")
        mode = request.GET.get("mode", "view")
        selected_year = int(request.GET.get("selected_year", datetime.now().year))

        if not request.GET._mutable:
            request.GET._mutable = True

        request.GET['tab'] = tab_name
        request.GET['opened_months'] = opened_months
        request.GET['mode'] = mode
        request.GET['selected_year'] = selected_year

        try:
            student = Student.objects.get(id=student_id)

            student_persons = StudentPerson.objects.filter(student_id=student_id)
            context['student'] = student
            context['student_persons'] = student_persons
        except Exception as e:
            print('StudentPage exception', e)
            return HttpResponse(status=404, msg=e)

        lessons_count = count_lessons_for_student_in_months(student_id, selected_year)

        context['months_counter'] = lessons_count

        return render(request, "crm/student-page.html", context)


def create_student(request):
    context = {}

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = None
            print(form.cleaned_data)
            if 'phone_number' in form.cleaned_data and form.cleaned_data['phone_number']:
                phone = form.cleaned_data['phone_number']
            student = None
            try:
                student = Student.objects.create(first_name=first_name, last_name=last_name, email=email, phone=phone)
            except Exception as e:
                print(e)
            messages.success(request, f'Dodano studenta {student.get_full_name()} pomyslnie!')

            return redirect(f"/students/{student.id}")
        else:
            print("student_form error", form.errors)
            context['message'] = form.errors
            context['form'] = form

    return render(request, "crm/student-create.html", context)


class StudentPersonDelete(View):
    @staticmethod
    def post(request, *args, **kwargs):
        context = {}
        if request.method == "POST" and 'delete_student_person' in request.POST:
            student_id = kwargs['student_id']
            student_person_id = kwargs['student_person_id']
            try:
                student_person = StudentPerson.objects.get(id=student_person_id, student_id=student_id)
                student_person.delete()
                messages.success(request, 'Relacja usunięta pomyślnie')
            except Exception as e:
                print(e)
                return HttpResponse(status=404, msg=e)

            return redirect(f"/students/{student_id}")
        else:
            context['message'] = "Nieprawidłowe żądanie"

        return render(request, "crm/student-person-delete.html", context)

    @staticmethod
    def get(request, *args, **kwargs):
        context = {}
        student_id = kwargs['student_id']
        student_person_id = kwargs['student_person_id']
        try:
            student_person = StudentPerson.objects.get(id=student_person_id, student_id=student_id)
        except Exception as e:
            return HttpResponse(status=404, msg=e)

        context['student_person'] = student_person

        return render(request, "crm/student-person-delete.html", context)

class StudentPersonCreate(View):
    @staticmethod
    def post(request, *args, **kwargs):
        context = {}
        student_id = kwargs['student_id']
        if request.method == "POST":
            form = StudentPersonForm(request.POST)
            if form.is_valid():
                print(form.cleaned_data)
                person_id = form.cleaned_data['person']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                phone = None
                if 'phone' in form.cleaned_data:
                    phone = form.cleaned_data['phone']
                print('test create')
                relationship_type = form.cleaned_data['relationship_type']
                person = None
                student_person = None
                if person_id == 'new':
                    try:
                        person = Person.objects.create(first_name=first_name, last_name=last_name, phone=phone, email=email)
                    except Exception as e:
                        print(e)
                else:
                    person = Person.objects.get(id=person_id)
                try:
                    print(person.first_name, person.last_name, person)
                    student_person = StudentPerson.objects.create(person=person, relationship_type=relationship_type, student_id=student_id)
                except Exception as e:
                    print(e)
                messages.success(request, f'Relacja z {student_person.person.get_full_name()} utworzona')
                return redirect(f'/students/{student_id}')
            else:
                context['message'] = form.errors
                context['form'] = form
                student = Student.objects.get(id=student_id)
                context['student'] = student

        #     student_id = kwargs['student_id']
        #     student_person_id = kwargs['student_person_id']
        #     try:
        #         student_person = StudentPerson.objects.get(id=student_person_id, student_id=student_id)
        #         student_person.delete()
        #         messages.success(request, 'Relacja usunięta pomyślnie')
        #     except Exception as e:
        #         print(e)
        #         return HttpResponse(status=404, msg=e)
        #
        #     return redirect(f"/students/{student_id}")
        # else:
        #     context['message'] = "Nieprawidłowe żądanie"

        return render(request, "crm/student-person-create.html", context)

    @staticmethod
    def get(request, *args, **kwargs):
        context = {}
        student_id = kwargs['student_id']

        try:
            student = Student.objects.get(id=student_id)
            persons = Person.objects.all()
            context['student'] = student
            context['persons'] = persons
        except Exception as e:
            return HttpResponse(status=404, msg=e)


        return render(request, "crm/student-person-create.html", context)


def lesson_page(request, student_id, lesson_id):
    mode = request.GET.get('mode')
    if mode not in MODES:
        return redirect(f'/students/{student_id}/{lesson_id}?mode=view')
    context = {}
    context['lesson'] = Lesson.objects.get(id=lesson_id)
    context['students'] = Student.objects.all()
    context['users'] = User.objects.all()
    context['mode'] = mode

    if request.method == 'POST':
        context['mode'] = 'view'
        return render(request, "crm/lesson-page.html", context)

    return render(request, "crm/lesson-page.html", context)
