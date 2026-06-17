from django.db import models
from django.conf import settings


STATUS_CHOICES = [
    ('new', 'New'),
    ('pending', 'Pending'),
    ('read', 'Read'),
    ('done', 'Done'),
]


class CVWritingRequest(models.Model):
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level (0–2 years)'),
        ('mid', 'Mid Level (3–6 years)'),
        ('senior', 'Senior Level (7–12 years)'),
        ('executive', 'Executive (13+ years)'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cv_requests'
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    industry = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    role_target = models.CharField(max_length=200, blank=True)
    existing_cv = models.FileField(upload_to='cv_requests/', null=True, blank=True)
    additional_notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'CV Writing Request'

    def __str__(self):
        return f"CV Request — {self.full_name} ({self.industry})"


class JobSearchRegistration(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='job_search_regs'
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    preferred_industry = models.CharField(max_length=100)
    preferred_location = models.CharField(max_length=200, blank=True)
    experience_level = models.CharField(max_length=100, blank=True)
    cv_file = models.FileField(upload_to='job_search_cvs/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Job Search Registration'

    def __str__(self):
        return f"Job Search — {self.full_name}"


class TrainingEnrolment(models.Model):
    PROGRAMME_CHOICES = [
        ('employability', 'Employability Skills (4 weeks)'),
        ('interview_prep', 'Interview Preparation (2 weeks)'),
        ('career_strategy', 'Career Strategy & Planning (3 weeks)'),
        ('personal_branding', 'Personal Branding (2 weeks)'),
        ('leadership', 'Workplace Leadership (6 weeks)'),
        ('digital_fluency', 'Digital & Tech Fluency (4 weeks)'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='training_enrolments'
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    programme = models.CharField(max_length=50, choices=PROGRAMME_CHOICES)
    industry = models.CharField(max_length=100, blank=True)
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Training Enrolment'

    def __str__(self):
        return f"Training — {self.full_name} ({self.get_programme_display()})"


class ContactMessage(models.Model):
    STATUS_CHOICES_CONTACT = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES_CONTACT, default='unread')
    admin_reply = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Contact Message'

    def __str__(self):
        return f"Message from {self.full_name} — {self.subject or '(no subject)'}"


class EmployerJobRequest(models.Model):
    """Submitted by employers requesting Kennedia to post a job for them."""
    INDUSTRY_CHOICES = [
        ('banking_finance', 'Banking & Finance'),
        ('technology', 'Technology'),
        ('fmcg_retail', 'FMCG / Retail'),
        ('oil_gas', 'Oil & Gas'),
        ('healthcare', 'Healthcare'),
        ('hr_consulting', 'Human Resources / Consulting'),
        ('manufacturing', 'Manufacturing'),
        ('other', 'Other'),
    ]
    PACKAGE_CHOICES = [
        ('free', 'Kennedia Free (₦0)'),
        ('basic', 'Kennedia Basic (₦50k/month)'),
        ('standard', 'Kennedia Standard (₦200k/month)'),
        ('pro', 'Kennedia Pro (₦500k/month)'),
    ]

    # Company info
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)

    # Job details
    job_title = models.CharField(max_length=200)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, default='full_time')
    salary_range = models.CharField(max_length=100, blank=True, help_text='e.g. ₦200k–₦350k/month')
    job_description = models.TextField()
    requirements = models.TextField(blank=True)
    notification_email = models.EmailField(
        help_text='Email to receive notifications when candidates apply'
    )

    # Package selected
    package = models.CharField(max_length=20, choices=PACKAGE_CHOICES, default='free')

    # Admin
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Employer Job Request'

    def __str__(self):
        return f"{self.company_name} — {self.job_title} ({self.get_package_display()})"
