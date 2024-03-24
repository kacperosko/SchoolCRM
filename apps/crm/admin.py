from django.contrib import admin
from .models import Person, Student, Lesson, LessonAdjustment


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email', 'phone')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'parent')
    search_fields = ('student__first_name', 'student__last_name', 'parent__first_name', 'parent__last_name')


class LessonAdjustment_ItemInline(admin.TabularInline):
    model = LessonAdjustment
    extra = 0
    can_delete = False
    show_change_link = True
    # readonly_fields = ['', ]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'series_end_date', 'student', 'teacher')
    list_filter = ('start_time', 'end_time')
    search_fields = ('student__firstName', 'student__lastName', 'teacher__username')

    inlines = [
        LessonAdjustment_ItemInline,
    ]


@admin.register(LessonAdjustment)
class LessonAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_lesson_date', 'modified_start_time', 'modified_end_time', 'lesson', 'status')

# Uncomment the following lines if you decide to use LessonException model
# from .models import LessonException
# admin.site.register(LessonException)
