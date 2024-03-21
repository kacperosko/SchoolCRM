from django.contrib import admin
from .models import Person, Student, LessonSchedule, LessonAdjustment


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstName', 'lastName', 'email', 'phone', 'birthdate')
    search_fields = ('firstName', 'lastName', 'email', 'phone')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'parent')
    search_fields = ('student__firstName', 'student__lastName', 'parent__firstName', 'parent__lastName')


class LessonAdjustment_ItemInline(admin.TabularInline):
    model = LessonAdjustment
    extra = 0
    can_delete = False
    show_change_link = True
    # readonly_fields = ['', ]


@admin.register(LessonSchedule)
class LessonScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'weekDay', 'startTime', 'endTime', 'startDate', 'endDate', 'student', 'teacher')
    list_filter = ('weekDay', 'startDate', 'endDate')
    search_fields = ('student__firstName', 'student__lastName', 'teacher__username')

    inlines = [
        LessonAdjustment_ItemInline,
    ]


@admin.register(LessonAdjustment)
class LessonAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'lessonDate', 'startTime', 'endTime', 'lessonSchedule', 'status')

# Uncomment the following lines if you decide to use LessonException model
# from .models import LessonException
# admin.site.register(LessonException)
