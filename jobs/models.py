import re
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


def cv_upload_path(instance, filename):
    """
    Organise uploaded CVs by job:
    applications/cvs/job_{id}_{slug}/filename
    e.g. applications/cvs/job_12_finance-manager/amaka_okafor_cv.pdf
    """
    # Slugify the job title — remove special chars, replace spaces with hyphens
    job_title = re.sub(r'[^\w\s-]', '', instance.job.title.lower())
    job_title = re.sub(r'[\s_]+', '-', job_title).strip('-')[:50]
    folder = f'applications/cvs/job_{instance.job.id}_{job_title}'
    return f'{folder}/{filename}'


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
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
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    ]
    EXPERIENCE_CHOICES = [
        ('0-1', '0–1 years (Entry Level)'),
        ('2-4', '2–4 years'),
        ('5-8', '5–8 years'),
        ('9+', '9+ years (Senior)'),
    ]

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, default='Kennedia Consulting')
    company_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    location = models.CharField(max_length=200)
    salary = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text='Monthly salary in Naira'
    )
    salary_display = models.CharField(max_length=100, blank=True,
        help_text='Optional: e.g. "₦400k – ₦600k" (overrides auto-format)')
    description = models.TextField()
    requirements = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    experience_required = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    deadline = models.DateField(null=True, blank=True)
    employer_email = models.EmailField(
        blank=True,
        help_text='Employer contact email — receives notification when someone applies'
    )
    views_count = models.PositiveIntegerField(default=0)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='posted_jobs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'

    def __str__(self):
        return f"{self.title} @ {self.company}"

    @property
    def requires_registration(self):
        """True if salary >= ₦500k — triggers the "Register to Apply" flow."""
        if self.salary is None:
            return False
        return self.salary >= settings.REGISTER_APPLY_THRESHOLD

    @property
    def application_count(self):
        return self.applications.count()

    @property
    def formatted_salary(self):
        if self.salary_display:
            return self.salary_display
        if not self.salary:
            return None
        n = int(self.salary)
        if n >= 1_000_000:
            return f'₦{n/1_000_000:.1f}M/month'.replace('.0M', 'M')
        return f'₦{n//1000}k/month'


class SavedJob(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_jobs'
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.email} saved {self.job.title}"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications',
        null=True, blank=True
    )
    # For easy-apply (non-registered users)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    years_of_experience = models.CharField(max_length=20, blank=True)
    cover_letter = models.TextField(blank=True)
    cv_file = models.FileField(upload_to=cv_upload_path)
    linkedin_url = models.URLField(blank=True)
    current_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text='Internal notes — not visible to applicant')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'

    def __str__(self):
        return f"{self.first_name} {self.last_name} → {self.job.title}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
