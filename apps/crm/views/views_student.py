from .views_base import *


@check_permission('crm.view_student')
def all_students(request):
    students_list = Student.objects.all().order_by("-last_name").order_by("-first_name")
    context = {'students': students_list}
    return render(request, "crm/students.html", context)


@check_permission('crm.view_student')
def view_student(request, student_id):
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
        student = Student.objects.get(id=student_id)

        student_persons = StudentPerson.objects.filter(student_id=student_id)

        model_name = get_model_by_prefix(student.id[:3])
        user_watch_record = WatchRecord.objects.filter(
            user=request.user, content_type__model=model_name.lower(), object_id=student_id
        ).first()
        invoices = Invoice.objects.filter(student_id=student_id).order_by('-invoice_date')[:10]

        notes = student.notes.all().order_by('-created_at')
        history = student.history.all().order_by('-changed_at')[:10]
        context.update({
            'record': student,
            'notes': notes,
            'field_history': history,
            'student_persons': student_persons,
            'watch_record': user_watch_record,
            'users': User.objects.all(),
            'locations': Location.objects.all(),
            'user': request.user,
            'invoices': invoices,
        })
    except Student.DoesNotExist:
        messages.error(request, f'Nie znaleziono Studenta z id {student_id}')
        return redirect('/student')
    except Exception as e:
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


@check_permission('crm.view_invoice')
def view_invoice(request, invoice_id):
    context = {}

    request.GET = request.GET.copy()
    request.GET.update({
        'tab': "Details",
    })

    try:
        invoice = Invoice.objects.get(id=invoice_id)
        invoice.invoiceitem_set.all()

        context.update({
            'record': invoice
        })

    except Invoice.DoesNotExist as e:
        return custom_404(request, f"Nie znaleziono faktury z takim id: {invoice_id}")

    return render(request, "crm/invoice-page.html", context)
