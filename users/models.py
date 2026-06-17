from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Extended user model for Kennedia Jobs.
    Roles: job_seeker | admin | super_admin
    """
    ROLE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
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

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='job_seeker')
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True)
    years_of_experience = models.PositiveSmallIntegerField(null=True, blank=True)
    linkedin_url = models.URLField(blank=True)
    profile_summary = models.TextField(blank=True)
    cv_file = models.FileField(upload_to='cvs/', null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    current_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_profile_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def is_admin_user(self):
        return self.role in ('admin', 'super_admin')

    @property
    def is_super_admin(self):
        return self.role == 'super_admin'

    def save(self, *args, **kwargs):
        # Auto-set staff status for admins so they can access Django admin
        if self.role in ('admin', 'super_admin'):
            self.is_staff = True
        if self.role == 'super_admin':
            self.is_superuser = True
        # Check profile completeness
        required = [self.first_name, self.last_name, self.phone, self.city, self.industry]
        self.is_profile_complete = all(required)
        super().save(*args, **kwargs)
