import os
import zipfile
import tempfile
import threading

from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsAdminOrSuperAdmin
from .models import Job, JobApplication, SavedJob
from .serializers import (
    JobListSerializer, JobDetailSerializer, JobWriteSerializer,
    JobApplicationSerializer, ApplicationAdminSerializer, SavedJobSerializer,
)


def _auto_expire_jobs():
    """Mark any active jobs whose deadline has passed as expired."""
    today = timezone.now().date()
    Job.objects.filter(status='active', deadline__lt=today).update(status='expired')


# ── PUBLIC JOB ENDPOINTS ──

class JobListView(generics.ListAPIView):
    """
    GET /api/jobs/
    Public. Supports filtering: ?industry=&location=&search=&type=&salary_max=
    """
    serializer_class = JobListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'company', 'location']
    ordering_fields = ['created_at', 'salary', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        _auto_expire_jobs()  # mark past-deadline jobs as expired in DB
        # Return active AND expired jobs — frontend shows expired with closed state
        # Only exclude drafts and closed
        qs = Job.objects.exclude(status__in=['draft', 'closed'])
        industry = self.request.query_params.get('industry')
        location = self.request.query_params.get('location')
        job_type = self.request.query_params.get('type')
        salary_filter = self.request.query_params.get('salary')

        if industry:
            qs = qs.filter(industry=industry)
        if location:
            qs = qs.filter(location__icontains=location)
        if job_type:
            qs = qs.filter(job_type=job_type)
        if salary_filter == 'below_500k':
            qs = qs.filter(salary__lt=500000)
        elif salary_filter == 'above_500k':
            qs = qs.filter(salary__gte=500000)
        return qs


class JobDetailView(generics.RetrieveAPIView):
    """GET /api/jobs/<id>/  — increments view counter."""
    serializer_class = JobDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Job.objects.exclude(status__in=['draft', 'closed'])

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ── APPLICATIONS ──

class ApplyToJobView(generics.CreateAPIView):
    """
    POST /api/jobs/<id>/apply/
    Anyone can apply — either as guest (easy apply) or registered user.
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        job = get_object_or_404(Job, pk=self.kwargs['pk'], status='active')
        user = self.request.user if self.request.user.is_authenticated else None
        application = serializer.save(job=job, user=user)
        self._notify_applicant(application)
        self._notify_employer(application)

    def _notify_applicant(self, application):
        """Send confirmation email to the applicant via Brevo."""
        from users.email_service import send_email
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;background:#f9fafb;padding:32px 24px;border-radius:12px;">
          <div style="text-align:center;margin-bottom:24px;">
            <h1 style="font-size:20px;color:#1a3a1f;margin:0;">KennediaJobs</h1>
          </div>
          <div style="background:white;border-radius:10px;padding:28px 32px;border:1px solid #e5e7eb;">
            <h2 style="font-size:17px;color:#111827;margin:0 0 12px;">Application Received!</h2>
            <p style="color:#4b5563;font-size:14px;line-height:1.6;margin:0 0 16px;">
              Hi {application.first_name},<br><br>
              Thank you for applying for <strong>{application.job.title}</strong> at <strong>{application.job.company}</strong>.
              We have received your application and will review it shortly.
            </p>
            <div style="background:#f0fdf4;border-radius:8px;padding:14px 18px;margin-bottom:16px;">
              <p style="margin:0;font-size:13px;color:#15803d;font-weight:600;">What happens next?</p>
              <p style="margin:6px 0 0;font-size:13px;color:#4b5563;">Our team will review your application within 5–7 business days. If shortlisted, we will contact you directly.</p>
            </div>
            <p style="color:#9ca3af;font-size:12px;margin:0;">Best regards,<br>Kennedia Jobs Team</p>
          </div>
        </div>"""
        try:
            send_email(application.email, application.first_name, f'Application Received — {application.job.title}', html)
        except Exception:
            pass

    def _notify_employer(self, application):
        """Send notification email to the employer when someone applies."""
        from users.email_service import send_email
        employer_email = application.job.employer_email
        if not employer_email:
            return

        cv_info = ''
        if application.cv_file:
            cv_info = f'<p style="margin:6px 0 0;font-size:13px;color:#4b5563;">A CV was submitted with this application. Log in to the Kennedia admin panel to download it.</p>'

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;background:#f9fafb;padding:32px 24px;border-radius:12px;">
          <div style="text-align:center;margin-bottom:24px;">
            <h1 style="font-size:20px;color:#1a3a1f;margin:0;">KennediaJobs</h1>
            <p style="color:#6b7280;font-size:13px;margin-top:4px;">New Application Alert</p>
          </div>
          <div style="background:white;border-radius:10px;padding:28px 32px;border:1px solid #e5e7eb;">
            <h2 style="font-size:17px;color:#111827;margin:0 0 16px;">New application for <strong>{application.job.title}</strong></h2>
            <div style="background:#f8fafc;border-radius:8px;padding:16px 20px;margin-bottom:16px;border:1px solid #e2e8f0;">
              <p style="margin:0 0 8px;font-size:13px;"><strong>Applicant:</strong> {application.first_name} {application.last_name}</p>
              <p style="margin:0 0 8px;font-size:13px;"><strong>Email:</strong> <a href="mailto:{application.email}" style="color:#15803d;">{application.email}</a></p>
              <p style="margin:0 0 8px;font-size:13px;"><strong>Phone:</strong> {application.phone or 'Not provided'}</p>
              <p style="margin:0;font-size:13px;"><strong>Experience:</strong> {application.years_of_experience or 'Not specified'}</p>
            </div>
            {cv_info}
            <p style="color:#9ca3af;font-size:12px;margin-top:16px;border-top:1px solid #f3f4f6;padding-top:12px;">
              This notification was sent by Kennedia Jobs on behalf of {application.job.company}.<br>
              To view all applications, contact your Kennedia consultant.
            </p>
          </div>
        </div>"""
        try:
            send_email(
                employer_email,
                application.job.company,
                f'New Application — {application.job.title} | {application.first_name} {application.last_name}',
                html
            )
        except Exception:
            pass


class MyApplicationsView(generics.ListAPIView):
    """GET /api/jobs/my-applications/ — authenticated user's applications."""
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)


class MyApplicationDetailView(generics.RetrieveAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)


# ── SAVED JOBS ──

class SavedJobView(generics.ListCreateAPIView):
    """GET: list saved jobs. POST: save a job."""
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related('job')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UnsaveJobView(generics.DestroyAPIView):
    """DELETE /api/jobs/<id>/unsave/"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)

    def get_object(self):
        return generics.get_object_or_404(
            SavedJob, user=self.request.user, job_id=self.kwargs['pk']
        )


# ── ADMIN JOB MANAGEMENT ──

class AdminJobListView(generics.ListCreateAPIView):
    """GET: all jobs (any status). POST: create job."""
    permission_classes = [IsAdminOrSuperAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobWriteSerializer
        return JobListSerializer

    def get_queryset(self):
        qs = Job.objects.all().order_by('-created_at')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class AdminJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE a single job — admin only."""
    permission_classes = [IsAdminOrSuperAdmin]
    queryset = Job.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return JobWriteSerializer
        return JobDetailSerializer


class AdminApplicationListView(generics.ListAPIView):
    """GET all applications — admin only. ?job=&status=&search="""
    serializer_class = ApplicationAdminSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        qs = JobApplication.objects.select_related('job', 'user').order_by('-applied_at')
        job_id = self.request.query_params.get('job')
        status_filter = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        if job_id:
            qs = qs.filter(job_id=job_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) | Q(last_name__icontains=search) |
                Q(email__icontains=search) | Q(job__title__icontains=search)
            )
        return qs


class AdminApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: update application status, add notes, delete."""
    serializer_class = ApplicationAdminSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    queryset = JobApplication.objects.all()

    def perform_update(self, serializer):
        old_status = self.get_object().status
        application = serializer.save()
        # Email applicant when status changes
        if application.status != old_status:
            self._notify_status_change(application)

    def _notify_status_change(self, application):
        messages = {
            'reviewed': 'Your application has been reviewed by our team.',
            'shortlisted': 'Great news! You have been shortlisted for the next stage.',
            'rejected': 'Thank you for your interest. Unfortunately your application was not successful at this time.',
            'hired': 'Congratulations! You have been selected for this role. Our team will be in touch shortly.',
        }
        msg = messages.get(application.status)
        if not msg:
            return
        try:
            send_mail(
                subject=f'Application Update — {application.job.title}',
                message=f'Hi {application.first_name},\n\n{msg}\n\nBest regards,\nKennedia Jobs Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[application.email],
                fail_silently=True,
            )
        except Exception:
            pass


@api_view(['GET'])
@permission_classes([IsAdminOrSuperAdmin])
def admin_jobs_stats(request):
    """Dashboard stats for admin."""
    from submissions.models import CVWritingRequest, JobSearchRegistration, TrainingEnrolment, ContactMessage
    return Response({
        'total_jobs': Job.objects.filter(status='active').count(),
        'draft_jobs': Job.objects.filter(status='draft').count(),
        'total_applications': JobApplication.objects.count(),
        'pending_applications': JobApplication.objects.filter(status='pending').count(),
        'shortlisted': JobApplication.objects.filter(status='shortlisted').count(),
        'cv_requests': CVWritingRequest.objects.filter(status='new').count(),
        'job_search_regs': JobSearchRegistration.objects.filter(status='new').count(),
        'training_enrolments': TrainingEnrolment.objects.filter(status='new').count(),
        'contact_messages': ContactMessage.objects.filter(status='unread').count(),
    })


# ── CV Download Views (admin only) ────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAdminOrSuperAdmin])
def job_applications_list(request, pk):
    """
    GET /api/jobs/admin/jobs/<pk>/applications/
    All applications for a job with individual CV download links.
    """
    job = get_object_or_404(Job, pk=pk)
    applications = JobApplication.objects.filter(job=job).order_by('-applied_at')

    data = []
    for app in applications:
        cv_url = None
        if app.cv_file:
            cv_url = request.build_absolute_uri(
                f'/api/jobs/admin/applications/{app.id}/download-cv/'
            )
        data.append({
            'id': app.id,
            'full_name': f'{app.first_name} {app.last_name}',
            'email': app.email,
            'phone': app.phone or '—',
            'years_of_experience': app.years_of_experience or '—',
            'status': app.status,
            'applied_at': app.applied_at,
            'cv_download_url': cv_url,
            'has_cv': bool(app.cv_file),
        })

    return Response({
        'job_id': job.id,
        'job_title': job.title,
        'total_applications': len(data),
        'applications': data,
    })


@api_view(['GET'])
@permission_classes([IsAdminOrSuperAdmin])
def download_cv(request, pk):
    """
    GET /api/jobs/admin/applications/<pk>/download-cv/
    Download a single applicant's CV.
    """
    application = get_object_or_404(JobApplication, pk=pk)

    if not application.cv_file:
        return Response({'error': 'No CV file for this application.'}, status=404)

    cv_path = application.cv_file.path

    if not os.path.exists(cv_path):
        return Response({'error': 'CV file not found on server.'}, status=404)

    ext = os.path.splitext(cv_path)[1]
    safe_name = f"{application.first_name}_{application.last_name}_{application.job.title}".replace(' ', '_')
    safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    filename = f'{safe_name}_CV{ext}'

    return FileResponse(open(cv_path, 'rb'), as_attachment=True, filename=filename)


@api_view(['GET'])
@permission_classes([IsAdminOrSuperAdmin])
def download_all_cvs(request, pk):
    """
    GET /api/jobs/admin/jobs/<pk>/download-all-cvs/
    Download all CVs for a job as a single ZIP file.
    """
    job = get_object_or_404(Job, pk=pk)
    applications = JobApplication.objects.filter(job=job).exclude(cv_file='')

    if not applications.exists():
        return Response({'error': 'No CVs found for this job.'}, status=404)

    safe_title = ''.join(
        c for c in job.title if c.isalnum() or c in (' ', '-', '_')
    ).replace(' ', '_')
    zip_filename = f'{safe_title}_All_CVs.zip'

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    tmp.close()

    added = 0
    used_names = []

    with zipfile.ZipFile(tmp.name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for app in applications:
            if not app.cv_file:
                continue
            cv_path = app.cv_file.path
            if not os.path.exists(cv_path):
                continue
            ext = os.path.splitext(cv_path)[1]
            arc_name = f"{app.first_name}_{app.last_name}{ext}".replace(' ', '_')
            if arc_name in used_names:
                arc_name = f"{app.first_name}_{app.last_name}_{app.id}{ext}".replace(' ', '_')
            used_names.append(arc_name)
            zf.write(cv_path, arc_name)
            added += 1

    if added == 0:
        os.unlink(tmp.name)
        return Response({'error': 'No CV files found on disk.'}, status=404)

    response = FileResponse(
        open(tmp.name, 'rb'),
        as_attachment=True,
        filename=zip_filename,
        content_type='application/zip',
    )

    def cleanup():
        import time; time.sleep(60)
        try: os.unlink(tmp.name)
        except: pass
    threading.Thread(target=cleanup, daemon=True).start()

    return response
