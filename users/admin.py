from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'get_full_name', 'role', 'industry', 'phone',
                    'is_profile_complete', 'is_active', 'created_at']
    list_filter = ['role', 'industry', 'is_active', 'is_profile_complete']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_login']

    fieldsets = (
        ('Account', {'fields': ('email', 'username', 'password', 'role')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'city', 'industry')}),
        ('Career Profile', {'fields': ('years_of_experience', 'current_salary', 'linkedin_url',
                                        'profile_summary', 'cv_file', 'profile_photo')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_profile_complete')}),
        ('Dates', {'fields': ('created_at', 'updated_at', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name',
                       'role', 'password1', 'password2'),
        }),
    )
