from .views_base import *
from django.views.decorators.csrf import csrf_exempt
from ..forms import LessonCreateForm, EditLessonForm
from ..lesson_handler import update_lesson
from ..models import Event


def get_student_group_lessons(request, record_id):
    status = False
    selected_year = int(request.GET.get('selected_year',  dj_timezone.localtime(dj_timezone.now()).year))
    lessons_count = None
    attendance_list_by_event = {}
    if get_model_by_prefix(record_id[:3]) == 'Student':
        lessons_count = get_student_lessons_in_year(record_id, selected_year)
    elif get_model_by_prefix(record_id[:3]) == 'Group':
        lessons_count = get_group_lessons_in_year(record_id, selected_year)
        attendance_list = AttendanceList.objects.filter(group_id=record_id ,event__event_date__year=selected_year)
        for attendance in attendance_list:
            attendance_list_by_event[attendance.event_id] = attendance.id

    lessons_count_serializable = {}
    for key, value in lessons_count.items():
        lessons = {k: v for k, v in value['Lessons'].items()}
        lessons_count_serializable[key] = {
            LessonStatutes.ZAPLANOWANA: value[LessonStatutes.ZAPLANOWANA],
            LessonStatutes.ODWOLANA_NAUCZYCIEL: value[LessonStatutes.ODWOLANA_NAUCZYCIEL],
            'Lessons': lessons
        }
        if  get_model_by_prefix(record_id[:3]) == 'Student':
            lessons_count_serializable[key][LessonStatutes.NIEOBECNOSC] = value[LessonStatutes.NIEOBECNOSC],
            lessons_count_serializable[key][LessonStatutes.ODWOLANA_24H_PRZED] = value[LessonStatutes.ODWOLANA_24H_PRZED],
    status = True

    return JsonResponse({'status': status, 'lessons': lessons_count_serializable, 'attendance_lists': attendance_list_by_event})


@csrf_exempt
@check_permission('crm.add_lessondefinition')
def create_lesson(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = LessonCreateForm(request.POST)
        if form.is_valid():
            lesson = form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Lekcja została utworzona pomyślnie.',
                'lesson_id': str(lesson.id),
            })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Nieprawidłowe żądanie.'}, status=400)


@csrf_exempt
def edit_lesson(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        event_id = request.POST.get('event_id')

        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Lekcja nie istnieje'})

        old_dates = {
            'old_date': event.event_date,
            'old_start_time': event.start_time,
            'old_original_datetime': event.original_lesson_datetime
        }

        form = EditLessonForm(request.POST, instance=event)

        if form.is_valid():
            edit_mode = form.cleaned_data['edit_mode']
            update_lesson(event, form, edit_mode, old_dates)
            return JsonResponse({
                'status': 'success',
                'message': 'Lekcja została zaktualizowana pomyślnie.'
            })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Nieprawidłowe żądanie.'}, status=400)


@csrf_exempt
def update_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event_id = data.get('event_id')
        new_status = data.get('new_status')

        try:
            event = Event.objects.get(id=event_id)
            event.status = new_status
            event.save()
            return JsonResponse({
                'status': True,
                'message': 'Status lekcji zaktualizowany pomyślnie.',
                'status_display': event.get_status_display()
            })
        except Event.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Lekcja nie znaleziona'})
    return JsonResponse({'status': False, 'message': 'Niepoprawne zawołanie'})
