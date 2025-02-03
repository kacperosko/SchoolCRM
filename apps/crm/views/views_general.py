from .views_base import *


WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']




def income_chart(request):
    today = dj_timezone.now().date()
    monthly_income = []

    # Tworzenie listy dochodu dla każdego z ostatnich 4 miesięcy
    for i in range(6):
        # Get the first day of each month and the corresponding month number
        start_of_month = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        month_number = start_of_month.month

        # Calculate the income for the month
        income = Invoice.objects.filter(
            invoice_date__year=start_of_month.year,
            invoice_date__month=month_number,
            is_paid=True
        ).aggregate(total=Sum('invoiceitem__amount'))['total'] or 0

        # Add month number and income to the list
        monthly_income.append({
            'month': get_month_name(month_number),
            'income': income
        })

    return monthly_income[::-1]


def crmHomePage(request):
    today_day = dj_timezone.localtime(dj_timezone.now())
    lessons_today = get_today_teacher_lessons(request.user.id, today_day)

    monthly_income = income_chart(request) if request.user.is_admin else []

    return render(request, "crm/index.html", {'today_lessons': lessons_today, 'today_day': today_day, 'monthly_income': monthly_income})


@check_permission('crm.view_person')
def all_persons(request):
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


@check_permission('crm.view_person')
def view_person(request, person_id):
    context = {}
    tab_name = request.GET.get("tab", "Details")

    request.GET = request.GET.copy()
    request.GET['tab'] = tab_name

    try:
        person = Person.objects.get(id=person_id)
        context['person'] = person
    except ObjectDoesNotExist as e:
        return custom_404(request, "Kontakt z takim id nie istnieje: {id}".format(id=person_id))
    except Exception as e:
        return custom_404(request, e)

    return render(request, 'crm/person-page.html', context)


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
        lesson_result = get_lessons_for_location_in_year(selected_record_id, selected_year)
        locations = locations.exclude(id=selected_record_id)

    else:
        selected_record = User.objects.get(id=selected_record_id)
        lesson_result = get_lessons_for_teacher_in_year(selected_record_id, selected_year)
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
            'endDate': str(lesson.series_end_date) if lesson.series_end_date else 'null',
            'student': lesson.student.get_full_name() if lesson.student else "[G] " + lesson.group.get_full_name(),
            'student_id': lesson.student.id if lesson.student else lesson.group.id,
            'teacher': lesson.teacher.get_full_name(),
            'adjustments': lesson_adjustments_for_lesson,
            'description': lesson.description,
            'is_series': 'true' if lesson.is_series else 'false',
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


@check_permission('crm.view_lesson')
def view_lesson_series(request, record_id):
    model_name = get_model_by_prefix(record_id[:3])
    try:
        if model_name == "Student":
            lessons = Lesson.objects.filter(student_id=record_id).order_by('start_time')
            record = Student.objects.get(id=record_id)
        elif model_name == "Group":
            lessons = Lesson.objects.filter(group_id=record_id).order_by('start_time')
            record = Group.objects.get(id=record_id)
    except ObjectDoesNotExist as e:
        return custom_404(request, "Nie znaleziono lekcji powiązanych z id: {id}".format(id=record_id))
    except Exception as e:
        return custom_404(request, e)

    context = {
        'lessons': lessons,
        'record': record,
        'model_name': model_name
    }

    return render(request, "crm/record-lesson-series.html", context)


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

            exception_model_url = ['lesson', 'studentperson', 'attendancelist', 'invoice']
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
        messages.error(request, "Wyst\u0105pi\u0142 b\u0142\u0105d podczas \u0142adowania formularza.")
        return redirect(f'/{model_name.lower()}/{record_id}' if record_id else f'/{model_name.lower()}')

    context['title'] = form_class.get_name()

    record = None

    if record_id:
        model_instance = get_model_object_by_prefix(record_id[:3])

        if not request.user.has_perm(f'crm.change_{model_name.lower()}'):
            messages.error(request, 'Brak uprawnie\u0144 do edytowania rekordu')
            return redirect(f'/{model_name.lower()}/{record_id}')

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
        form = form_class(request.POST, request.FILES, instance=record)
        context['form'] = form
        if form.is_valid():
            try:
                saved_instance = form.save(commit=True)

                messages.success(request, 'Rekord zapisany pomy\u015Blnie')

                redirect_url = (
                    saved_instance.redirect_after_edit()
                    if saved_instance and callable(getattr(saved_instance, 'redirect_after_edit', None))
                    else f'/{get_model_by_prefix(saved_instance.id[:3]).lower()}/{saved_instance.id}'
                )
                return redirect(redirect_url)
            except Exception as e:
                messages.error(request, f'Wyst\u0105pi\u0142 b\u0142\u0105d podczas zapisywania rekordu: {e}')
        else:

            context['message'] = form.errors

    return render(request, "crm/record-update-create.html", context)


class AttendanceListPage(View):

    @staticmethod
    @check_permission('crm.change_attendancelist')
    def post(request, *args, **kwargs):
        pass

    @staticmethod
    @check_permission('crm.view_attendancelist')
    def get(request, *args, **kwargs):
        context = {}

        attendance_list_id = kwargs.get('attendance_list_id')

        request.GET = request.GET.copy()
        request.GET.update({
            'tab': "Details",
        })

        try:
            attendance_list = AttendanceList.objects.get(id=attendance_list_id)
            attendance_list_student = attendance_list.attendance_list_student_group_relationship.all()

            context.update({
                'record': attendance_list,
                'attendances': attendance_list_student,
            })

        except AttendanceList.DoesNotExist as e:
            return custom_404(request, f"Nie znaleziono listy obecności z takim id: {attendance_list_id}")


        return render(request, "crm/attendance-list-page.html", context)


IMPORT_FILES = {
    'student': 'student_import_szablon.xlsx'
}


def import_records(request, model_name):
    context = {}
    if model_name not in IMPORT_FILES:
        messages.error(request, f"Nie znaleziono opcji importu dla tego obiektu: {model_name}")
        return redirect(f"/{model_name}")

    template_file = IMPORT_FILES[model_name]
    template_file_path = os.path.join(settings.MEDIA_ROOT, template_file)
    context['template_file'] = template_file

    # Obsługa pobierania pliku szablonu
    if 'download' in request.GET:
        if os.path.exists(template_file_path):
            # Zwracanie pliku jako odpowiedzi FileResponse
            return FileResponse(open(template_file_path, 'rb'), as_attachment=True, filename=template_file)
        else:
            messages.error(request, "Plik szablonu nie został znaleziony.")
            return redirect(f"/{model_name}")

    # Renderowanie strony import-records.html z kontekstem
    return render(request, "crm/import-records.html", context)


def download_template(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'your_template.xlsx')
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='template.xlsx')


VIEW_ALL_MODELS = {
    'student': {
        'fields': {
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'email': 'Email',
            'phone': 'Telefon',
        }
    },
    'group': {
        'fields': {
            'name': 'Nazwa',
        }
    },
    'person': {
        'fields': {
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'email': 'Email',
            'phone': 'Telefon',
        }
    },
    'location': {
        'fields': {
            'name': 'Nazwa',
            'city': 'Miasto',
            'street': 'Ulica',
            'postal_code': 'Kod pocztowy',
        }
    }
}


def view_all(request, model_name):
    if model_name not in VIEW_ALL_MODELS:
        return custom_404(request, "Nie znaleziono takiej strony")
    try:
        model = apps.get_model(app_label='crm', model_name=model_name)
    except LookupError:
        raise custom_404(request, "Nie znaleziono takiego modelu")

    fields_with_labels = VIEW_ALL_MODELS[model_name]['fields']
    fields = list(fields_with_labels.keys())
    labels = list(fields_with_labels.values())

    context = {
        'model_name': model_name,
        'model_label_plural': model._meta.verbose_name_plural,
        'model_label': model._meta.verbose_name,
        'fields': fields_with_labels,
        'order_field': list(fields_with_labels.keys())[0],
    }

    return render(request, 'crm/list-all.html', context)


def get_all_records(request):
    model_name = request.GET.get('model_name')
    if model_name not in VIEW_ALL_MODELS:
        return JsonResponse({'success': False, 'message': f'Nie znaleziono takiego obiektu {model_name}'}, status=404)

    fields_with_labels = VIEW_ALL_MODELS[model_name]['fields']
    fields = list(fields_with_labels.keys())
    labels = list(fields_with_labels.values())

    try:
        model = apps.get_model(app_label='crm', model_name=model_name)
    except LookupError:
        raise custom_404(request, "Nie znaleziono takiego modelu")
    order_field = request.GET.get('order_field', fields[0])
    user_input = request.GET.get('query', '')

    if user_input:
        # Tworzenie dynamicznego zapytania
        query = Q()
        for field in fields:
            query |= Q(**{f"{field}__icontains": user_input})

        records_query = model.objects.filter(query).values(*fields, 'id').order_by(order_field)
    else:
        records_query = model.objects.all().values(*fields, 'id').order_by(order_field)

    # Paginacja wyników
    paginator = Paginator(records_query, 10)
    page_number = request.GET.get('page', 1)
    try:
        records_page = paginator.page(page_number)
    except EmptyPage:
        records_page = paginator.page(paginator.num_pages)

    # Przekazanie danych do szablonu
    context = {
        'records': [record for record in records_page],
        'records_number': records_page.number,
        'has_previous': records_page.has_previous(),
        'has_next': records_page.has_next(),
        'num_pages': records_page.paginator.num_pages,
    }

    return JsonResponse({'success': True, **context}, status=200)

