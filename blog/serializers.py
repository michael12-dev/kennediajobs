from rest_framework import serializers
from .models import BlogPost


class BlogListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'category', 'category_display',
            'author_name', 'excerpt', 'emoji', 'featured_image',
            'read_time', 'views_count', 'published_at', 'created_at',
        ]


class BlogDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'category', 'category_display',
            'author_name', 'excerpt', 'body', 'emoji', 'featured_image',
            'read_time', 'views_count', 'published_at', 'created_at',
        ]


class BlogWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = [
            'title', 'category', 'author_display', 'excerpt', 'body',
            'emoji', 'featured_image', 'status', 'read_time',
        ]
