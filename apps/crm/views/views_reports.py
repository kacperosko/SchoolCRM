from .views_base import *


@check_is_admin
def view_reports(request):
    return render(request, "crm/reports.html")


@check_is_admin
def view_student_report(request):
    if not request.user.is_admin:
        return custom_404(request, "Nie masz uprawnień do tej strony")
    month = request.GET.get('month')
    year = request.GET.get('year')
    context = {"students": None}
    if year is not None and month is not None:
        request.GET = request.GET.copy()
        request.GET.update({
            'month': month,
            'year': year,
        })

        students = Student.objects.all().order_by('first_name')
        students_report = []

        for student in students:
            counted_lessons = count_lessons_for_student_in_month(student.id, int(year), int(month))

            if counted_lessons:
                students_report.append({
                    "id": student.id,
                    "name": student.get_full_name(),
                    **counted_lessons
                })

        context['students'] = students_report
        context['month'] = month
        context['year'] = year

    return render(request, "crm/report-student-month.html", context)


@check_is_admin
def view_students_in_group_report(request):
    if not request.user.is_admin:
        return custom_404(request, "Nie masz uprawnień do tej strony")
    groups = Group.objects.all().order_by('name')
    month = request.GET.get('month')
    year = request.GET.get('year')
    group_id = request.GET.get('group')
    context = {"attendance": None, "groups": groups}

    if year is not None and month is not None and group_id is not None:
        request.GET = request.GET.copy()
        request.GET.update({
            'month': month,
            'year': year,
        })

        attendance_list_student = AttendanceListStudent.objects.filter(attendance_list__group_id=group_id,
                                                                       attendance_list__lesson_date__month=month,
                                                                       attendance_list__lesson_date__year=year)

        if not len(attendance_list_student) > 0:
            print("ERROR")
            messages.error(request, "Nie znaleziono rekordów dla takich filtrów")
            return render(request, "crm/report-student-group-month.html", context)

        result = {}
        for attendance in attendance_list_student:
            if attendance.student.id not in result:
                result[attendance.student.id] = {"Obecnosc": 0, "Nieobecnosc": 0, "Spoznienie": 0, "student_id": attendance.student.id, "student_name": attendance.student.get_full_name()}
            result[attendance.student.id][attendance.attendance_status] += 1

        context["result"] = result

    return render(request, "crm/report-student-group-month.html", context)
