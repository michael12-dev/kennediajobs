from django.db import models
from django.conf import settings
from django.utils.text import slugify


class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('career_tips', 'Career Tips'),
        ('interview_prep', 'Interview Prep'),
        ('salary_finance', 'Salary & Finance'),
        ('industry_news', 'Industry News'),
        ('cv_resume', 'CV & Resume'),
        ('company_news', 'Company News'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='blog_posts'
    )
    author_display = models.CharField(max_length=100, blank=True,
        help_text='Override author name shown publicly (e.g. "Kennedia Editorial")')
    excerpt = models.TextField(max_length=500, help_text='Short summary shown in listing')
    body = models.TextField(help_text='Full HTML or markdown content')
    emoji = models.CharField(max_length=10, default='📝')
    featured_image = models.ImageField(upload_to='blog/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    read_time = models.CharField(max_length=20, blank=True, help_text='e.g. "5 min"')
    views_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        # Auto-set published_at when first published
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def author_name(self):
        if self.author_display:
            return self.author_display
        if self.author:
            return self.author.get_full_name() or self.author.email
        return 'Kennedia Team'
