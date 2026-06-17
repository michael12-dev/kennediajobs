from rest_framework import serializers
from .models import Job, JobApplication, SavedJob


class JobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for job listings."""
    requires_registration = serializers.BooleanField(read_only=True)
    formatted_salary = serializers.CharField(read_only=True)
    application_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'company_logo', 'industry', 'job_type',
            'location', 'salary', 'formatted_salary', 'salary_display',
            'description', 'status', 'deadline', 'requires_registration',
            'application_count', 'views_count', 'created_at',
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    requires_registration = serializers.BooleanField(read_only=True)
    formatted_salary = serializers.CharField(read_only=True)
    application_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'company_logo', 'industry', 'job_type',
            'location', 'salary', 'formatted_salary', 'salary_display',
            'description', 'requirements', 'benefits', 'experience_required',
            'status', 'deadline', 'requires_registration',
            'application_count', 'views_count', 'created_at', 'updated_at',
        ]


class JobWriteSerializer(serializers.ModelSerializer):
    """Used by admins to create/update jobs."""
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'company_logo', 'industry', 'job_type',
            'location', 'salary', 'salary_display',
            'description', 'requirements', 'benefits',
            'experience_required', 'status', 'deadline', 'employer_email',
        ]


class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.company', read_only=True)
    requires_registration = serializers.BooleanField(source='job.requires_registration', read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_title', 'job_company', 'requires_registration',
            'first_name', 'last_name', 'email', 'phone',
            'years_of_experience', 'cover_letter', 'cv_file',
            'linkedin_url', 'current_salary',
            'status', 'applied_at', 'updated_at',
        ]
        read_only_fields = ['id', 'job', 'status', 'applied_at', 'updated_at',
                            'job_title', 'job_company', 'requires_registration']

    def validate_cv_file(self, value):
        allowed = ['application/pdf',
                   'application/msword',
                   'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if hasattr(value, 'content_type') and value.content_type not in allowed:
            raise serializers.ValidationError('Only PDF or Word documents are accepted.')
        max_size = 5 * 1024 * 1024  # 5 MB
        if value.size > max_size:
            raise serializers.ValidationError('CV file must be under 5MB.')
        return value


class ApplicationAdminSerializer(serializers.ModelSerializer):
    """Full application details for admin views."""
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.company', read_only=True)

    class Meta:
        model = JobApplication
        fields = '__all__'


class SavedJobSerializer(serializers.ModelSerializer):
    job = JobListSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(), source='job', write_only=True
    )

    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'job_id', 'saved_at']
        read_only_fields = ['id', 'saved_at']
