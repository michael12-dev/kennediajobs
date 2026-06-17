from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'title', 'category', 'author_name', 'status', 'views_count', 'published_at']
    list_filter = ['status', 'category']
    search_fields = ['title', 'excerpt', 'body']
    readonly_fields = ['slug', 'views_count', 'created_at', 'updated_at', 'published_at']
    list_editable = ['status']
    prepopulated_fields = {}
