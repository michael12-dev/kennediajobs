from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.JobListView.as_view(), name='job_list'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('<int:pk>/apply/', views.ApplyToJobView.as_view(), name='apply_to_job'),

    # Authenticated user
    path('my-applications/', views.MyApplicationsView.as_view(), name='my_applications'),
    path('my-applications/<int:pk>/', views.MyApplicationDetailView.as_view(), name='my_application_detail'),
    path('saved/', views.SavedJobView.as_view(), name='saved_jobs'),
    path('<int:pk>/unsave/', views.UnsaveJobView.as_view(), name='unsave_job'),

    # Admin — jobs
    path('admin/jobs/', views.AdminJobListView.as_view(), name='admin_job_list'),
    path('admin/jobs/<int:pk>/', views.AdminJobDetailView.as_view(), name='admin_job_detail'),
    path('admin/jobs/<int:pk>/applications/', views.job_applications_list, name='job_applications_list'),
    path('admin/jobs/<int:pk>/download-all-cvs/', views.download_all_cvs, name='download_all_cvs'),

    # Admin — applications
    path('admin/applications/', views.AdminApplicationListView.as_view(), name='admin_applications'),
    path('admin/applications/<int:pk>/', views.AdminApplicationDetailView.as_view(), name='admin_application_detail'),
    path('admin/applications/<int:pk>/download-cv/', views.download_cv, name='download_cv'),

    # Admin — stats
    path('admin/stats/', views.admin_jobs_stats, name='admin_jobs_stats'),
]
