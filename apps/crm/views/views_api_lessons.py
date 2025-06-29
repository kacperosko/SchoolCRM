from .views_base import *
from django.views.decorators.csrf import csrf_exempt
from ..forms import LessonCreateForm, EditLessonForm
from ..lesson_handler import update_lesson
from ..models import Event
from apps.crm.templatetags.crm_tags import get_status_color


def get_student_group_lessons(request, record_id):
    status = False
    selected_year = int(request.GET.get('selected_year',  dj_timezone.localtime(dj_timezone.now()).year))
    lessons_count = None
    if get_model_by_prefix(record_id[:3]) == 'Student':
        # lessons_count = count_lessons_for_student_in_year(record_id, selected_year)
        lessons_count = get_student_lessons_in_year(record_id, selected_year)
    elif get_model_by_prefix(record_id[:3]) == 'Group':
        lessons_count = count_lessons_for_group_in_year(record_id, selected_year)

    lessons_count_serializable = {}
    for key, value in lessons_count.items():
        lessons = {k: v.to_dict() for k, v in value['Lessons'].items()}
        lessons_count_serializable[key] = {
            LessonStatutes.ZAPLANOWANA: value[LessonStatutes.ZAPLANOWANA],
            LessonStatutes.NIEOBECNOSC: value[LessonStatutes.NIEOBECNOSC],
            LessonStatutes.ODWOLANA_NAUCZYCIEL: value[LessonStatutes.ODWOLANA_NAUCZYCIEL],
            LessonStatutes.ODWOLANA_24H_PRZED: value[LessonStatutes.ODWOLANA_24H_PRZED],
            'Lessons': lessons
        }
    status = True

    return JsonResponse({'status': status, 'lessons': lessons_count_serializable})


@csrf_exempt
def create_lesson(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = LessonCreateForm(request.POST)
        if form.is_valid():
            print('VIEW create_lesson')
            print('forms fields -> ' + str(form.fields))
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
    print('start')
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        print('Headers OK')

        event_id = request.POST.get('event_id')

        try:
            event = Event.objects.get(pk=event_id)
            print('event event_date', event.event_date)
            print('event start_time', event.start_time)
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
            print('event event_date', event.event_date)
            print('event start_time', event.start_time)
            update_lesson(event, form, edit_mode, old_dates)
            return JsonResponse({
                'status': 'success',
                'message': 'Lekcja została zaktualizowana pomyślnie.'
            })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    print('zle')
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
        except Lesson.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Event nie znaleziony'})
    return JsonResponse({'status': False, 'message': 'Niepoprawne zawołanie'})
