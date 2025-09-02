from django.contrib import admin
from .models import Person, Student, StudentPerson, Note, Location, Notification, WatchRecord, Group, GroupStudent, AttendanceList, AttendanceListStudent, Invoice, InvoiceItem, Event, LessonDefinition
from django.contrib.contenttypes.admin import GenericTabularInline


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email', 'phone')


class NoteItemInline(GenericTabularInline):
    model = Note
    extra = 1


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'modified_date')
    search_fields = ('first_name', 'last_name')

    inlines = [
        NoteItemInline,
    ]


@admin.register(StudentPerson)
class StudentPersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'person')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('content', 'content_type', 'created_by')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_full_name')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message')
    exclude = ['id']


@admin.register(WatchRecord)
class WatchRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'content_object')


@admin.register(Group)
class GroupdAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'modified_by')


@admin.register(GroupStudent)
class GroupStudentdAdmin(admin.ModelAdmin):
    list_display = ('group', 'student')


class AttendanceListStudentItemInline(admin.TabularInline):
    model = AttendanceListStudent
    extra = 0
    can_delete = False
    show_change_link = True
    # readonly_fields = ['', ]


@admin.register(AttendanceList)
class AttendanceListAdmin(admin.ModelAdmin):
    list_display = ('group', 'event')


    inlines = [
        AttendanceListStudentItemInline,
    ]


class InvoiceItemStudentItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    can_delete = False
    show_change_link = True
    # readonly_fields = ['', ]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'student')


    inlines = [
        InvoiceItemStudentItemInline,
    ]


class EventItemInline(admin.TabularInline):
    model = Event
    extra = 0
    can_delete = False
    show_change_link = True
    ordering = ('event_date',)


@admin.register(LessonDefinition)
class LessonDefinitionAdmin(admin.ModelAdmin):
    list_display = ('id',)


    inlines = [
        EventItemInline,
    ]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'duration', 'event_date', 'lesson_definition')

