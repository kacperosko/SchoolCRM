from .views_general import crm_home_page, delete_record, upsert_record, calendar, view_all, get_all_records, \
    view_person, all_persons
from .views_reports import view_reports, view_student_report, view_students_in_group_report
from .views_student import all_students, view_student, StudentPersonCreate, view_invoice
from .views_location import all_locations, view_location
from .views_group import all_groups, view_group, view_attendance_list
from .views_api import upsert_note, delete_note, get_notifications, \
    mark_notification_as_read, watch_record, save_attendance_list_student, create_attendance_list_student
from .views_api_lessons import get_student_group_lessons, create_lesson, edit_lesson, update_status

