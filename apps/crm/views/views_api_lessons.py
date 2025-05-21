from .views_base import *
from django.views.decorators.csrf import csrf_exempt
from ..forms import LessonCreateForm

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
