from .views_base import *


@check_permission('crm.view_student')
def all_students(request):
    students_list = Student.objects.all().order_by("-last_name").order_by("-first_name")
    context = {'students': students_list}
    return render(request, "crm/students.html", context)


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

                    start_datetime = dj_timezone.make_aware(datetime.combine(lesson_date, start_time), dj_timezone.get_current_timezone())
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

            invoices = Invoice.objects.filter(student_id=student_id).order_by('-invoice_date')[:10]

            notes = student.notes.all().order_by('-created_at')
            context.update({
                'record': student,
                'notes': notes,
                'student_persons': student_persons,
                'watch_record': user_watch_record,
                'users': User.objects.all(),
                'locations': Location.objects.all(),
                'user': request.user,
                'invoices': invoices,
            })
        except Student.DoesNotExist as e:
            messages.error(request, f'Nie znaleziono Studenta z id {student_id}')
            return redirect('/student')
        except Exception as e:
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
