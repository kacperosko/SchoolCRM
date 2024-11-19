from .views_base import *



@check_permission('crm.view_group')
def all_groups(request):
    groups = Group.objects.annotate(student_count=Count('group_student_group_relationship'))

    context = {"groups": groups}

    return render(request, "crm/groups.html", context)


class GroupPage(View):

    @staticmethod
    @check_permission('crm.view_group')
    def post(request, *args, **kwargs):
        group_id = kwargs['group_id']
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
                    f'/group/{group_id}?tab={tab_name}&opened_months={opened_months}&selected_year={selected_year}')
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

                    lesson = Lesson.objects.create(group_id=group_id, start_time=start_datetime,
                                                   end_time=end_datetime,
                                                   is_series=is_series, teacher_id=teacher_id,
                                                   description=description, series_end_date=end_series,
                                                   location_id=location_id)
                    lesson_msg = 'Seria lekcji' if is_series else 'Lekcja'
                    messages.success(request, f'{lesson_msg} dodana pomy\u015Blnie!')
                else:
                    messages.error(request, f'B\u0142ad podczas zapisywania: {form.errors}')
                return redirect(
                    f'/group/{group_id}?tab={tab_name}&opened_months={opened_months}&selected_year={selected_year}')
            elif 'attendance_list_create' in request.POST:
                form = AttendancelistForm(request.POST)
                try:
                    attendance_list = AttendanceList.objects.create(group_id=group_id, lesson_date=dj_timezone.now())

                    group_students = GroupStudent.objects.filter(group_id=group_id)
                    attendances = []

                    for group_student in group_students:
                        attendances.append(AttendanceListStudent(attendance_list=attendance_list, student_id=group_student.student.id))

                    AttendanceListStudent.objects.bulk_create(attendances)


                    messages.success(request, 'Utworzono Listę Obecności!')
                except Exception as e:
                    messages.error(request, e)


                return redirect(
                    f'/group/{group_id}?tab={tab_name}&opened_months={opened_months}&selected_year={selected_year}')
            else:
                messages.error(request, f'Nieobs\u0142ugiwany formularz: {request.POST}')
                return render(request, "crm/student-page.html", context)
    @staticmethod
    @check_permission('crm.view_group')
    def get(request, *args, **kwargs):
        context = {}

        group_id = kwargs.get('group_id')
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

            notes = group.notes.all()

            attendance_lists = list(group.attendance_group_relationship.all().order_by('-lesson_date'))
            attendance_lists_students = AttendanceListStudent.objects.filter(attendance_list__in=attendance_lists)
            attendance_students = {}
            for att_student in attendance_lists_students:
                if att_student.student.id not in attendance_students:
                    months = {str(month): 0 for month in range(1, 13)}

                    attendance_students[att_student.student.id] = {
                        "name": att_student.student.get_full_name(),
                        **months
                    }


            today = datetime.now().date()

            today_attendance_list = next((attendance_list for attendance_list in attendance_lists if attendance_list.lesson_date.date() == today), None)

            if today_attendance_list is not None:
                attendance_lists.remove(today_attendance_list)

            context.update({
                'record': group,
                'group_students': group_students,
                'notes': notes,
                'watch_record': user_watch_record,
                'users': User.objects.all(),
                'locations': Location.objects.all(),
                'user': request.user,
                'attendance_lists': attendance_lists,
                'today_attendance_list': today_attendance_list,
            })
        except Group.DoesNotExist as e:
            messages.error(request, f'Nie znaleziono Grupy z id {group_id}')
            return redirect('/group')
        except Exception as e:
            messages.error(request, f'view_group exception: {e}')
            return custom_404(request, e)

        return render(request, "crm/group-page.html", context)
