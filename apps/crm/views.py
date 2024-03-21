from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from .models import Student, LessonSchedule, LessonAdjustment, Person
from django.core.serializers import serialize
import json
from django.contrib.auth import authenticate, login, logout
from .forms import UserCreationForm, LoginForm, StudentForm, LessonForm
from .middleware.crm_middleware import login_exempt
from django.contrib.auth.models import User
import datetime
from django.db.models import Q
from calendar import monthrange

MODES = ['view', 'edit']


# login page
@login_exempt
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('/students')
    else:
        form = LoginForm()
    return render(request, 'auth/auth-sign-in.html', {'form': form})


class CRMHomePage(View):
    @staticmethod
    def post(request, *args, **kwargs):
        pass

    @staticmethod
    def get(request, *args, **kwargs):
        context = {}
        return render(request, "backend/index.html", context)


class DynamicHTMLView(View):
    def get(self, request, *args, **kwargs):
        path_arg = self.kwargs.get('path')
        # path_arg = path_arg[:-1]
        print(path_arg)
        path = path_arg
        print(path)
        if not path:
            raise Http404("No path provided")
        context = {}
        return render(request, path_arg, context)


def students(request):
    students_list = Student.objects.all()
    context = {'students': students_list}
    return render(request, "crm/students.html", context)


def calendar(request):
    # Fetch lessons associated with the current teacher
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            print(form)
            lessonDate = datetime.datetime.strptime(str(form.cleaned_data['lessonDate']), "%Y-%m-%d").date()
            lesson = LessonAdjustment.objects.create(lessonSchedule_id=form.cleaned_data['lessonSchedule'],
                                                     startTime=form.cleaned_data['startTime'], endTime=form.cleaned_data['endTime'],
                                                     lessonDate=lessonDate,
                                                     originalLessonDate=lessonDate, status=form.cleaned_data['status'])
            print('lesson created ->', lesson.id)
            return redirect('/calendar')
        else:
            print('ERROR FORM', form.errors)

    lessons = LessonSchedule.objects.filter(teacher=request.user)

    # Fetch lesson adjustments associated with fetched lessons
    lesson_adjustments = LessonAdjustment.objects.filter(lessonSchedule__in=lessons)

    # Construct a dictionary to hold lesson adjustments data
    lesson_adjustments_data = {}
    for l_adjustment in lesson_adjustments:
        print('l_Adjustment ->', l_adjustment.lessonDate)
        lesson_id = l_adjustment.lessonSchedule.id
        if lesson_id not in lesson_adjustments_data:
            lesson_adjustments_data[lesson_id] = []
        lesson_adjustments_data[lesson_id].append({
            'id': l_adjustment.id,
            'lessonDate': str(l_adjustment.lessonDate),
            'originalLessonDate': str(l_adjustment.originalLessonDate),
            'lessonScheduleId': l_adjustment.lessonSchedule.id,
            'startTime': l_adjustment.startTime.strftime('%H:%M'),
            'endTime': l_adjustment.endTime.strftime('%H:%M'),
            'status': l_adjustment.status,
            'student': l_adjustment.lessonSchedule.student.student.get_full_name()
        })
    print(lesson_adjustments_data)
    # Construct a list of dictionaries with lesson data
    lesson_data = []
    for lesson in lessons:
        lesson_adjustments_for_lesson = lesson_adjustments_data.get(lesson.id, [])
        print(lesson_adjustments_for_lesson)
        student_name = f"{lesson.student.student.firstName} {lesson.student.student.lastName}"
        lesson_data.append({
            'id': lesson.id,
            'weekDay': lesson.weekDay,
            'startTime': lesson.startTime.strftime('%H:%M'),
            'endTime': lesson.endTime.strftime('%H:%M'),
            'startDate': str(lesson.startDate),
            'endDate': str(lesson.endDate) if lesson.endDate else None,
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
    today = datetime.datetime.now()

    start_year = lesson_schedule.startDate.year
    end_year = lesson_schedule.endDate.year if lesson_schedule.endDate else datetime.date.today().year
    for target_year in range(start_year, end_year + 1):
        if target_year == int(year):
            start_month = lesson_schedule.startDate.month if target_year == start_year else 1
            end_month = lesson_schedule.endDate.month if target_year == end_year and lesson_schedule.endDate else 12

            for month in range(start_month, end_month + 1):
                num_days = monthrange(target_year, month)[1]
                # months_counter[month] = {}

                for day in range(1, num_days + 1):
                    current_date = datetime.date(target_year, month, day)
                    if lesson_schedule.startDate <= current_date <= (lesson_schedule.endDate or current_date):
                        weekday = current_date.strftime('%A')
                        if lesson_schedule.weekDay == weekday:
                            current_datetime = datetime.datetime.combine(current_date,
                                                                         datetime.time(lesson_schedule.startTime.hour,
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
            current_datetime = datetime.datetime.combine(lesson_adjustment.originalLessonDate,
                                                         datetime.time(lesson_adjustment.lessonSchedule.startTime.hour,
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
                current_datetime = datetime.datetime.combine(lesson_adjustment.lessonDate,
                                                             datetime.time(lesson_adjustment.startTime.hour,
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


def student_page(request, student_id):
    context = {}
    today = datetime.datetime.now()

    student = Student.objects.get(student_id=student_id)
    context['student'] = student
    #
    # Get lessons for the current year
    lessons = LessonSchedule.objects.filter(student_id=student_id, startDate__year=today.year)
    lesson_adjustments = LessonAdjustment.objects.filter(lessonSchedule__in=lessons)
    months_counter = {month: {'Pending': 0, 'Completed': 0, 'Canceled': 0, 'Summary': 0} for month in range(1, 13)}

    for lesson in lessons:
        temp_dict = generate_series(lesson, lesson_adjustments.filter(lessonSchedule=lesson), 2024, 'counter')
        for key in temp_dict:
            if key in months_counter:
                months_counter[key] = {k: months_counter[key][k] + temp_dict[key].get(k, 0) for k in
                                       months_counter[key]}
            else:
                months_counter[key] = temp_dict[key]

    print('final', months_counter)
    context['months_counter'] = months_counter

    return render(request, "crm/student-page.html", context)


def create_student(request):
    context = {}

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            if 'phone' in form.cleaned_data:
                phone = form.cleaned_data['phone']
            else:
                phone = None
            birth_date = form.cleaned_data['birth_date']

            person = Person.objects.create(firstName=first_name, lastName=last_name, email=email, phone=phone,
                                           birthdate=birth_date)
            student = Student.objects.create(student=person)

            return redirect(f"/students/{student.id}")
        else:
            print("student_form error", form.errors)
            context['message'] = form.errors

    return render(request, "crm/student-create.html", context)


def lesson_page(request, student_id, lesson_id):
    mode = request.GET.get('mode')
    if mode not in MODES:
        return redirect(f'/students/{student_id}/{lesson_id}?mode=view')
    context = {}
    context['lesson'] = LessonSchedule.objects.get(id=lesson_id)
    context['students'] = Student.objects.all()
    context['users'] = User.objects.all()
    context['mode'] = mode

    if request.method == 'POST':
        context['mode'] = 'view'
        return render(request, "crm/lesson-page.html", context)

    return render(request, "crm/lesson-page.html", context)
