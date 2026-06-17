from django.contrib import admin
from django.utils.html import format_html
from .models import Job, JobApplication, SavedJob


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'industry', 'job_type', 'location',
                    'formatted_salary', 'requires_registration', 'status',
                    'application_count', 'views_count', 'created_at']
    list_filter = ['status', 'industry', 'job_type']
    search_fields = ['title', 'company', 'location', 'description']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    list_editable = ['status']
    ordering = ['-created_at']

    fieldsets = (
        ('Job Info', {'fields': ('title', 'company', 'company_logo', 'industry', 'job_type', 'location')}),
        ('Salary', {'fields': ('salary', 'salary_display')}),
        ('Content', {'fields': ('description', 'requirements', 'benefits', 'experience_required')}),
        ('Settings', {'fields': ('status', 'deadline', 'posted_by')}),
        ('Stats', {'fields': ('views_count', 'created_at', 'updated_at')}),
    )

    def requires_registration(self, obj):
        if obj.requires_registration:
            return format_html('<span style="color:orange;">🔒 Yes</span>')
        return format_html('<span style="color:green;">⚡ No</span>')
    requires_registration.short_description = 'Reg. Required'

    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = 'Applications'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'job', 'status', 'applied_at']
    list_filter = ['status', 'job__industry']
    search_fields = ['first_name', 'last_name', 'email', 'job__title']
    readonly_fields = ['applied_at', 'updated_at']
    list_editable = ['status']
    ordering = ['-applied_at']

    fieldsets = (
        ('Applicant', {'fields': ('first_name', 'last_name', 'email', 'phone', 'user')}),
        ('Application', {'fields': ('job', 'cv_file', 'cover_letter', 'years_of_experience',
                                     'linkedin_url', 'current_salary')}),
        ('Admin', {'fields': ('status', 'admin_notes')}),
        ('Dates', {'fields': ('applied_at', 'updated_at')}),
    )

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Applicant'


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'saved_at']
    readonly_fields = ['saved_at']
