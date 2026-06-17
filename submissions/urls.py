from django.urls import path
from . import views

urlpatterns = [
    # Public submissions
    path('cv-writing/', views.CVWritingRequestView.as_view(), name='cv_writing'),
    path('job-search/', views.JobSearchRegistrationView.as_view(), name='job_search_reg'),
    path('training/', views.TrainingEnrolmentView.as_view(), name='training_enrolment'),
    path('contact/', views.ContactMessageView.as_view(), name='contact_message'),

    # Employer job request (public)
    path('employer-request/', views.EmployerJobRequestView.as_view(), name='employer_job_request'),

    # Admin views
    path('admin/cv-writing/', views.CVWritingAdminListView.as_view(), name='admin_cv_writing_list'),
    path('admin/cv-writing/<int:pk>/', views.CVWritingAdminDetailView.as_view(), name='admin_cv_writing_detail'),
    path('admin/job-search/', views.JobSearchAdminListView.as_view(), name='admin_job_search_list'),
    path('admin/job-search/<int:pk>/', views.JobSearchAdminDetailView.as_view(), name='admin_job_search_detail'),
    path('admin/training/', views.TrainingAdminListView.as_view(), name='admin_training_list'),
    path('admin/training/<int:pk>/', views.TrainingAdminDetailView.as_view(), name='admin_training_detail'),
    path('admin/contact/', views.ContactAdminListView.as_view(), name='admin_contact_list'),
    path('admin/contact/<int:pk>/', views.ContactAdminDetailView.as_view(), name='admin_contact_detail'),

    # Employer requests (admin)
    path('admin/employer-requests/', views.AdminEmployerRequestListView.as_view(), name='admin_employer_requests'),
    path('admin/employer-requests/<int:pk>/', views.AdminEmployerRequestDetailView.as_view(), name='admin_employer_request_detail'),

    # CSV exports
    path('export/<str:model_name>/', views.export_csv, name='export_csv'),
]
