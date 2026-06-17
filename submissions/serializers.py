from rest_framework import serializers
from .models import CVWritingRequest, JobSearchRegistration, TrainingEnrolment, ContactMessage


class CVWritingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVWritingRequest
        fields = ['id', 'full_name', 'email', 'phone', 'industry',
                  'experience_level', 'role_target', 'existing_cv',
                  'additional_notes', 'status', 'submitted_at']
        read_only_fields = ['id', 'status', 'submitted_at']


class CVWritingRequestAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVWritingRequest
        fields = '__all__'


class JobSearchRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSearchRegistration
        fields = ['id', 'full_name', 'email', 'phone', 'preferred_industry',
                  'preferred_location', 'experience_level', 'cv_file',
                  'status', 'submitted_at']
        read_only_fields = ['id', 'status', 'submitted_at']


class JobSearchRegistrationAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSearchRegistration
        fields = '__all__'


class TrainingEnrolmentSerializer(serializers.ModelSerializer):
    programme_display = serializers.CharField(source='get_programme_display', read_only=True)

    class Meta:
        model = TrainingEnrolment
        fields = ['id', 'full_name', 'email', 'phone', 'programme',
                  'programme_display', 'industry', 'special_requests',
                  'status', 'submitted_at']
        read_only_fields = ['id', 'status', 'submitted_at']


class TrainingEnrolmentAdminSerializer(serializers.ModelSerializer):
    programme_display = serializers.CharField(source='get_programme_display', read_only=True)

    class Meta:
        model = TrainingEnrolment
        fields = '__all__'


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'full_name', 'email', 'phone', 'subject',
                  'message', 'status', 'submitted_at']
        read_only_fields = ['id', 'status', 'submitted_at']


class ContactMessageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
