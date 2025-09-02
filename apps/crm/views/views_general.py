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


def crm_home_page(request):
    today_day = dj_timezone.localtime(dj_timezone.now())
    lessons_today = get_today_teacher_lessons(request.user.id, today_day)

    monthly_income = income_chart(request) if request.user.groups.filter(name='Kierownik').exists() or request.user.is_superuser else []

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
        model_name = get_model_by_prefix(str(selected_record_id)[:3])  # User or Group
        if model_name is None:
            raise Exception(f'Nie znaleziono modelu dla id {selected_record_id}')
    except Exception as e:
        messages.error(request, e)
        return render(request, 'crm/calendar.html', {})

    selected_year = int(request.GET.get("selected_year", datetime.now().year))
    selected_start_date = request.GET.get("selected_start_date", None)

    if not request.GET._mutable:
        request.GET._mutable = True

    teachers = User.objects.filter(is_active=True)
    locations = Location.objects.all()

    if model_name == 'Location':
        selected_record = Location.objects.get(id=selected_record_id)
        lesson_result = get_location_lessons_in_year(selected_record_id, selected_year)
        locations = locations.exclude(id=selected_record_id)
    else:
        selected_record = User.objects.get(id=selected_record_id)
        lesson_result = get_teacher_lessons_in_year(selected_record_id, selected_year)
        teachers = teachers.exclude(id=selected_record_id)

    lesson_data = lesson_result

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


def delete_record(request, record_id):
    context = {}
    redirect_url = None
    model_name = get_model_by_prefix(record_id[:3])
    if model_name is not None:
        model_object = get_model_object_by_prefix(record_id[:3])
        try:
            record = model_object.objects.get(id=record_id)
        except ObjectDoesNotExist:
            return custom_404(request, f'Rekord z podanym id nie istnieje: {record_id}')

        if not request.user.has_perm(f'crm.delete_{model_name.lower()}'):
            messages.error(request, 'Brak uprawnień do usunięcia rekordu')
            if callable(getattr(record, 'redirect_after_edit', None)):
                return redirect(record.redirect_after_edit())
            return redirect(f'/{model_name.lower()}/{record_id}')

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
            messages.success(request, 'Rekord usunięty')
            if redirect_url:
                return redirect(redirect_url)
            else:
                return redirect(f'/{model_name.lower()}')
    else:
        return custom_404(request, "Nie można usunąć wybranego rekordu")


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
    print("upsert_record")
    print("form_name", form_name)

    try:
        form_class = get_form_class(form_name)
    except Exception:
        messages.error(request, "Wystąpił błąd podczas ładowania formularza.")
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
                print(e)
                messages.error(request, f'Wyst\u0105pi\u0142 b\u0142\u0105d podczas zapisywania rekordu: {e}')
        else:
            print(form.errors)
            context['message'] = form.errors

    return render(request, "crm/record-update-create.html", context)


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


# ============ BELOW ALL VIEWS TODO ============

def view_all(request, model_name):
    print("VIEW ALL")
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

