from django.contrib import admin
from apps.authentication.models import User
from .forms import UserForm

admin.site.site_header = "Warsztat CRM"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserForm

    model = User

    list_display = ('email', 'first_name', 'last_name',)

    fieldsets = (
        ('Details', {
            'fields': ('email', 'first_name', 'last_name', 'phone', 'avatar_color', 'user_avatar')
        }),

        ('Permissions', {
            'fields': ('is_active', 'staff', 'admin', 'is_superuser')
        }),

        ('Group Permissions', {
            'fields': ('groups', 'user_permissions',)
        }),
    )
