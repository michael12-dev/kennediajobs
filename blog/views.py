from rest_framework import generics, permissions
from users.permissions import IsAdminOrSuperAdmin
from .models import BlogPost
from .serializers import BlogListSerializer, BlogDetailSerializer, BlogWriteSerializer

class BlogListView(generics.ListAPIView):
    """GET /api/blog/  — public. ?category=career_tips&search="""
    serializer_class = BlogListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = BlogPost.objects.filter(status='published')
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        if category:
            qs = qs.filter(category=category)
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(excerpt__icontains=search)
        return qs


class BlogDetailView(generics.RetrieveAPIView):
    """GET /api/blog/<slug>/  — increments views."""
    serializer_class = BlogDetailSerializer
    permission_classes = [permissions.AllowAny]
    queryset = BlogPost.objects.filter(status='published')
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        return super().retrieve(request, *args, **kwargs)


# ── ADMIN BLOG MANAGEMENT ──

class AdminBlogListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get_serializer_class(self):
        return BlogWriteSerializer if self.request.method == 'POST' else BlogListSerializer

    def get_queryset(self):
        qs = BlogPost.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class AdminBlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrSuperAdmin]
    queryset = BlogPost.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return BlogWriteSerializer
        return BlogDetailSerializer
