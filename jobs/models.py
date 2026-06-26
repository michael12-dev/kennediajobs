import re
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


def cv_upload_path(instance, filename):
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
        ('hybrid', 'Hybrid'),
    ]
    INDUSTRY_CHOICES = [
        ('accounting_finance_banking', 'Accounting, Finance & Banking'),
        ('agriculture_agribusiness', 'Agriculture & Agribusiness'),
        ('arts_entertainment_media', 'Arts, Entertainment & Media'),
        ('automotive_aviation_transport', 'Automotive, Aviation & Transportation'),
        ('construction_engineering_realestate', 'Construction, Engineering & Real Estate'),
        ('consumer_goods_retail_ecommerce', 'Consumer Goods, Retail & E-commerce'),
        ('consulting_professional_services', 'Consulting & Professional Services'),
        ('education_training', 'Education & Training'),
        ('energy_utilities_mining_oilgas', 'Energy, Utilities, Mining & Oil & Gas'),
        ('event_hospitality_tourism', 'Event Management, Hospitality & Tourism'),
        ('fashion_beauty_lifestyle', 'Fashion, Beauty & Lifestyle'),
        ('food_beverage', 'Food & Beverage'),
        ('government_public_admin', 'Government & Public Administration'),
        ('healthcare_medical_pharma', 'Healthcare, Medical & Pharmaceutical'),
        ('human_resources_recruitment', 'Human Resources & Recruitment'),
        ('information_technology_telecom', 'Information Technology & Telecommunications'),
        ('legal_services', 'Legal Services'),
        ('logistics_supply_chain', 'Logistics, Supply Chain & Warehousing'),
        ('manufacturing_production', 'Manufacturing & Production'),
        ('nonprofit_ngo_social', 'Nonprofit, NGO & Social Services'),
        ('research_science_lab', 'Research, Science & Laboratory Services'),
        ('sales_marketing_pr', 'Sales, Marketing & Public Relations'),
        ('security_defense', 'Security & Defense'),
        ('web_digital_creative', 'Web, Digital Media & Creative Services'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    ]
    EXPERIENCE_CHOICES = [
        ('trainee', 'Trainee – 0 years'),
        ('entry', 'Entry Level – 1–2 years'),
        ('mid', 'Mid-level – 3–6 years'),
        ('senior_mid', 'Senior Mid – 7–10 years'),
        ('senior', 'Senior/Managerial – 12 years+'),
    ]
    QUALIFICATION_CHOICES = [
        ('secondary', 'Secondary School Certificate or Equivalent'),
        ('certificate', 'Certificate / Vocational Qualification'),
        ('diploma', 'Diploma (ND, OND, NCE, HND)'),
        ('bachelors', "Bachelor's Degree"),
        ('postgraduate', 'Postgraduate Qualification (PGD, Master\'s, Doctorate)'),
        ('professional', 'Professional Certification / Fellowship'),
        ('none', 'No Formal Qualification Required'),
    ]

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, default='Kennedia Consulting')
    company_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    industry = models.CharField(max_length=60, choices=INDUSTRY_CHOICES)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    location = models.CharField(max_length=200)
    salary = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text='Monthly salary in Naira'
    )
    salary_display = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    experience_required = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, blank=True)
    qualification_required = models.CharField(max_length=30, choices=QUALIFICATION_CHOICES, blank=True)
    employer_email = models.EmailField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    deadline = models.DateField(null=True, blank=True)
    requires_registration = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def formatted_salary(self):
        if self.salary_display:
            return self.salary_display
        if self.salary:
            n = float(self.salary)
            if n >= 1_000_000:
                return f'₦{n/1_000_000:.1f}M/month'.replace('.0M', 'M')
            if n >= 1_000:
                return f'₦{int(n/1000)}k/month'
            return f'₦{int(n)}/month'
        return None

    @property
    def application_count(self):
        return self.applications.count()


class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_jobs')
    job  = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f'{self.user} saved {self.job}'


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    years_of_experience = models.CharField(max_length=50, blank=True)
    cv_file = models.FileField(upload_to=cv_upload_path, null=True, blank=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ('job', 'email')

    def __str__(self):
        return f'{self.first_name} {self.last_name} → {self.job.title}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def has_cv(self):
        return bool(self.cv_file)
