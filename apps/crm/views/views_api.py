from .views_base import *


def upsert_note(request):
    status = False
    message = ""
    note_data = None

    try:
        record_id = request.POST.get("record_id")
        content = request.POST.get("content")
        note_id = request.POST.get("note_id")

        if not content:
            message = "Tre\u015B\u0107 nie mo\u017Ce by\u0107 pusta"
            raise ValueError(message)

        if note_id:  # Update existing note
            try:
                note = Note.objects.get(id=note_id)
                note.content = content
                note.created_at = now()
                note.created_by = request.user
                note.save()
            except Note.DoesNotExist:
                message = "Notatka nie istnieje"
                raise
            except Exception as e:
                message = str(e)
                raise
        else:  # Create new note
            try:
                model_name = get_model_by_prefix(record_id[:3])
                if not model_name:
                    message = "Nie wspierany model"
                    raise ValueError(message)

                content_type = ContentType.objects.get(model=model_name.lower(), app_label='crm')

                note = Note.objects.create(
                    content=content,
                    content_type=content_type,
                    object_id=record_id,
                    created_by=request.user
                )
            except ContentType.DoesNotExist:
                message = "Nie znaleziono typu zawarto\u015Bci"
                raise
            except Exception as e:
                message = str(e)
                raise

        formatted_created_at = format_datetime(note.created_at, "d MMMM YYYY HH:mm", locale='pl')
        note_data = {
            'note_id': note.id,
            'content': note.content,
            'created_at': formatted_created_at,
            'created_by': note.created_by.get_full_name(),
        }
        status = True

    except Exception as e:
        if not message:
            message = str(e)

    return JsonResponse({'status': status, 'message': message, 'note': note_data})


def delete_note(request):
    status = False
    message = ""

    try:
        note_id = request.POST.get("note_id")
        if not note_id:
            message = "Nie mo\u017Cna odczyta\u0107 notatki"
            raise ValueError(message)

        try:
            note = Note.objects.get(id=note_id)
            note.delete()
            status = True
            message = "Notatka zosta\u0142a usuni\u0119ta"
        except Note.DoesNotExist:
            message = "Notatka nie istnieje"
        except Exception as e:
            message = str(e)

    except ValueError as ve:
        message = str(ve)
    except Exception as e:
        message = str(e)

    return JsonResponse({'status': status, 'message': message})


def get_notifications(request):
    notifications_query = Notification.objects.filter(user=request.user).select_related('content_type').order_by(
        '-created_at')

    unread_notifications_count = notifications_query.filter(read=False).aggregate(count=Count('id'))['count']
    all_notifications_count = notifications_query.count()

    paginator = Paginator(notifications_query, 10)
    page_number = request.GET.get('notification_page', 1)
    notifications_page = paginator.page(page_number)
    notifications_data = notifications_page.object_list.values(
        'id', 'message', 'read', 'content_type__model', 'object_id', 'created_at'
    )

    notifications_list = []
    for notification in notifications_data:
        notifications_list.append({
            'id': notification['id'],
            'message': notification['message'],
            'read': notification['read'],
            'model_name': notification['content_type__model'],
            'record_id': notification['object_id'],
            'created_at': timesince(notification['created_at'])
        })

    response_data = {
        'notifications': notifications_list,
        'unread_notifications': unread_notifications_count,
        'all_notifications': all_notifications_count,
        'max_pages': paginator.num_pages
    }

    return JsonResponse(response_data)


def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Nie znaleziono powiadomienia'}, status=404)


def watch_record(request, mode, record_id):
    status = False
    message = ''

    model_name = get_model_by_prefix(record_id[:3])
    if not model_name:
        message = 'Ten rekord nie obs\u0142uguje tej funkcji'
        return JsonResponse({'status': status, 'message': message})

    model_name = model_name.lower()
    try:
        content_type = ContentType.objects.get(model=model_name, app_label='crm')

        if mode == 'follow':
            WatchRecord.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=record_id
            )
        elif mode == 'unfollow':
            user_watch_record = WatchRecord.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=record_id
            ).first()
            if user_watch_record:
                user_watch_record.delete()
            else:
                message = 'Rekord obserwacji nie istnieje'
                return JsonResponse({'status': status, 'message': message})
        else:
            message = 'Nieprawid\u0142owy tryb'
            return JsonResponse({'status': status, 'message': message})

        status = True
    except ContentType.DoesNotExist:
        message = 'Nieprawid\u0142owy typ zawarto\u015Bci'
    except Exception as e:
        message = str(e)

    return JsonResponse({'status': status, 'message': message})


def create_attendance_list_student(request):
    status = True
    message = 'Lista obecności utworzona pomyślnie'
    attendance_list_id = ''
    try:
        event_id = request.POST.get('event_id')
        group_id = request.POST.get('group_id')
        print("event_id", event_id)
        print("group_id", group_id)
        attendance_list = AttendanceList.objects.create(group_id=group_id, event_id=event_id)

        group_students = GroupStudent.objects.filter(group_id=group_id)
        attendances = []

        for group_student in group_students:
            attendances.append(
                AttendanceListStudent(attendance_list=attendance_list, student_id=group_student.student.id))

        AttendanceListStudent.objects.bulk_create(attendances)

        attendance_list_id = attendance_list.id
    except Exception as e:
        message = str(e)
        status = False
    return JsonResponse({'status': status, 'message': message, 'attendance_list_id': attendance_list_id})


def save_attendance_list_student(request):
    status = False
    message = ""

    try:
        attendance_list_students = request.POST.get("attendance_list_students")
        attendance_list_id = request.POST.get("attendance_list_id", None)

        if not attendance_list_students:
            message = "Lista nie może być pusta"
            raise ValueError(message)
        elif not attendance_list_id:
            message = "Id Listy obecności nie może być puste"
            raise ValueError(message)
        else:
            attendance_list_students = json.loads(attendance_list_students)

            attendance_list_students_to_update = AttendanceListStudent.objects.filter(attendance_list_id=attendance_list_id)

            records_to_update = []
            for attendance_student in attendance_list_students:
                attendance_student_record = attendance_list_students_to_update.filter(id=attendance_student['attendance_list_student_id']).first()

                if attendance_student_record:
                    attendance_student_record.attendance_status = attendance_student['status']

                    records_to_update.append(attendance_student_record)

            if records_to_update:
                AttendanceListStudent.objects.bulk_update(records_to_update, ['attendance_status'])

        message = "Lista zapisana pomyślnie"
        status = True

    except Exception as e:
        if not message:
            message = str(e)

    return JsonResponse({'status': status, 'message': message})

