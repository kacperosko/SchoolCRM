from .views_base import *



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

            notes = group.notes.all()

            context.update({
                'record': group,
                'group_students': group_students,
                'notes': notes,
                'watch_record': user_watch_record,
                'users': User.objects.all(),
                'locations': Location.objects.all(),
                'user': request.user
            })
        except Group.DoesNotExist as e:
            messages.error(request, f'Nie znaleziono Grupy z id {group_id}')
            return redirect('/group')
        except Exception as e:
            messages.error(request, f'view_group exception: {e}')
            return custom_404(request, e)

        return render(request, "crm/group-page.html", context)


@check_permission('crm.view_attendancelist')
def view_attendance_list(request, attendance_list_id):
    context = {}

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