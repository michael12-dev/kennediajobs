from django.contrib import admin
from .models import CVWritingRequest, JobSearchRegistration, TrainingEnrolment, ContactMessage


@admin.register(CVWritingRequest)
class CVWritingRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'industry', 'experience_level', 'status', 'submitted_at']
    list_filter = ['status', 'experience_level']
    search_fields = ['full_name', 'email', 'industry']
    list_editable = ['status']
    readonly_fields = ['submitted_at', 'updated_at']


@admin.register(JobSearchRegistration)
class JobSearchRegistrationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'preferred_industry', 'status', 'submitted_at']
    list_filter = ['status', 'preferred_industry']
    search_fields = ['full_name', 'email']
    list_editable = ['status']
    readonly_fields = ['submitted_at', 'updated_at']


@admin.register(TrainingEnrolment)
class TrainingEnrolmentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'programme', 'status', 'submitted_at']
    list_filter = ['status', 'programme']
    search_fields = ['full_name', 'email']
    list_editable = ['status']
    readonly_fields = ['submitted_at', 'updated_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject', 'status', 'submitted_at']
    list_filter = ['status']
    search_fields = ['full_name', 'email', 'subject', 'message']
    list_editable = ['status']
    readonly_fields = ['submitted_at', 'updated_at']
