from django.urls import path
from . import views

urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    # Admin routes must come before the slug catch-all
    path('admin/posts/', views.AdminBlogListView.as_view(), name='admin_blog_list'),
    path('admin/posts/<int:pk>/', views.AdminBlogDetailView.as_view(), name='admin_blog_detail'),
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
]
