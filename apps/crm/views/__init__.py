from .views_general import crmHomePage, delete_record, upsert_record, calendar, view_all, get_all_records, \
    view_lesson_series, view_person, all_persons, AttendanceListPage, import_records
from .views_reports import view_reports, view_student_report, view_students_in_group_report
from .views_student import all_students, StudentPage, StudentPersonCreate
from .views_location import all_locations, LocationPage
from .views_group import all_groups, GroupPage
from .views_api import get_student_group_lessons, upsert_note, delete_note, get_notifications, \
    mark_notification_as_read, watch_record, save_attendance_list_student

