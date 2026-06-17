from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse
import csv

from users.permissions import IsAdminOrSuperAdmin
from .models import CVWritingRequest, JobSearchRegistration, TrainingEnrolment, ContactMessage
from .serializers import (
    CVWritingRequestSerializer, CVWritingRequestAdminSerializer,
    JobSearchRegistrationSerializer, JobSearchRegistrationAdminSerializer,
    TrainingEnrolmentSerializer, TrainingEnrolmentAdminSerializer,
    ContactMessageSerializer, ContactMessageAdminSerializer,
)


def _notify_admin(subject, body):
    """Internal: email admin when a new submission arrives."""
    try:
        send_mail(
            subject=f'[Kennedia Jobs] {subject}',
            message=body,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[django_settings.EMAIL_HOST_USER or 'info@kennediajobs.com'],
            fail_silently=True,
        )
    except Exception:
        pass


# ── CV WRITING REQUESTS ──

class CVWritingRequestView(generics.CreateAPIView):
    """POST /api/submissions/cv-writing/  — public."""
    serializer_class = CVWritingRequestSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        obj = serializer.save(user=user)
        _notify_admin(
            'New CV Writing Request',
            f'Name: {obj.full_name}\nEmail: {obj.email}\nIndustry: {obj.industry}\nExperience: {obj.experience_level}'
        )
        # Auto-reply to submitter
        send_mail(
            subject='CV Writing Request Received — Kennedia Jobs',
            message=(
                f'Hi {obj.full_name.split()[0]},\n\n'
                'Thank you for requesting our CV Writing service. A specialist will reach out within 24 hours.\n\n'
                'Best regards,\nKennedia Jobs Team'
            ),
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[obj.email],
            fail_silently=True,
        )


class CVWritingAdminListView(generics.ListAPIView):
    serializer_class = CVWritingRequestAdminSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        qs = CVWritingRequest.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class CVWritingAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CVWritingRequestAdminSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    queryset = CVWritingRequest.objects.all()


# ── JOB SEARCH REGISTRATIONS ──

class JobSearchRegistrationView(generics.CreateAPIView):
    serializer_class = JobSearchRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        obj = serializer.save(user=user)
        _notify_admin('New Job Search Registration', f'Name: {obj.full_name}\nEmail: {obj.email}\nIndustry: {obj.preferred_industry}')
        send_mail(
            subject='Job Search Registration Confirmed — Kennedia Jobs',
            message=(f'Hi {obj.full_name.split()[0]},\n\nYour job search profile has been registered. Our consultants will reach out within 24 hours with matching opportunities.\n\nBest regards,\nKennedia Jobs Team'),
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[obj.email], fail_silently=True,
        )


class JobSearchAdminListView(generics.ListAPIView):
    serializer_class = JobSearchRegistrationAdminSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        qs = JobSearchRegistration.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class JobSearchAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSearchRegistrationAdminSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    queryset = JobSearchRegistration.objects.all()


# ── TRAINING ENROLMENTS ──

class TrainingEnrolmentView(generics.CreateAPIView):
    serializer_class = TrainingEnrolmentSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        obj = serializer.save(user=user)
        _notify_admin('New Training Enrolment', f'Name: {obj.full_name}\nEmail: {obj.email}\nProgramme: {obj.get_programme_display()}')
        send_mail(
            subject='Training Enrolment Received — Kennedia Jobs',
            message=(f'Hi {obj.full_name.split()[0]},\n\nThank you for enrolling in {obj.get_programme_display()}. Our training team will contact you with schedule and payment details.\n\nBest regards,\nKennedia Jobs Team'),
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[obj.email], fail_silently=True,
        )


class TrainingAdminListView(generics.ListAPIView):
    serializer_class = TrainingEnrolmentAdminSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        qs = TrainingEnrolment.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class TrainingAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TrainingEnrolmentAdminSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    queryset = TrainingEnrolment.objects.all()


# ── CONTACT MESSAGES ──

class ContactMessageView(generics.CreateAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        obj = serializer.save()
        _notify_admin(f'New Contact Message: {obj.subject}', f'From: {obj.full_name} ({obj.email})\n\n{obj.message}')


class ContactAdminListView(generics.ListAPIView):
    serializer_class = ContactMessageAdminSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        qs = ContactMessage.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class ContactAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactMessageAdminSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    queryset = ContactMessage.objects.all()


# ── CSV EXPORT ──

@api_view(['GET'])
@permission_classes([IsAdminOrSuperAdmin])
def export_csv(request, model_name):
    """
    GET /api/submissions/export/<model_name>/
    model_name: cv_writing | job_search | training | contact | applications
    """
    model_map = {
        'cv_writing': (CVWritingRequest, ['full_name', 'email', 'phone', 'industry', 'experience_level', 'status', 'submitted_at']),
        'job_search': (JobSearchRegistration, ['full_name', 'email', 'phone', 'preferred_industry', 'preferred_location', 'status', 'submitted_at']),
        'training': (TrainingEnrolment, ['full_name', 'email', 'phone', 'programme', 'industry', 'status', 'submitted_at']),
        'contact': (ContactMessage, ['full_name', 'email', 'phone', 'subject', 'message', 'status', 'submitted_at']),
    }
    if model_name == 'applications':
        from jobs.models import JobApplication
        model_cls = JobApplication
        fields = ['first_name', 'last_name', 'email', 'phone', 'years_of_experience', 'status', 'applied_at']
        qs = model_cls.objects.select_related('job').all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="kennedia_{model_name}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Job Title'] + fields)
        for obj in qs:
            writer.writerow([obj.job.title] + [getattr(obj, f, '') for f in fields])
        return response

    if model_name not in model_map:
        return Response({'error': 'Unknown model.'}, status=400)

    model_cls, fields = model_map[model_name]
    qs = model_cls.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="kennedia_{model_name}.csv"'
    writer = csv.writer(response)
    writer.writerow(fields)
    for obj in qs:
        writer.writerow([getattr(obj, f, '') for f in fields])
    return response


# ── Employer Job Request ──────────────────────────────────────────────────────

class EmployerJobRequestView(generics.CreateAPIView):
    """
    POST /api/submissions/employer-request/
    Public endpoint — employers submit job posting requests.
    """
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        from .models import EmployerJobRequest
        data = request.data

        required = ['company_name', 'contact_person', 'email', 'phone',
                    'job_title', 'industry', 'location', 'job_description', 'notification_email']
        missing = [f for f in required if not data.get(f, '').strip()]
        if missing:
            return Response(
                {'error': f"Missing required fields: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        req = EmployerJobRequest.objects.create(
            company_name=data['company_name'],
            contact_person=data['contact_person'],
            email=data['email'],
            phone=data['phone'],
            website=data.get('website', ''),
            job_title=data['job_title'],
            industry=data['industry'],
            location=data['location'],
            job_type=data.get('job_type', 'full_time'),
            salary_range=data.get('salary_range', ''),
            job_description=data['job_description'],
            requirements=data.get('requirements', ''),
            notification_email=data['notification_email'],
            package=data.get('package', 'free'),
        )

        # Send confirmation email to employer
        from users.email_service import send_email
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;background:#f9fafb;padding:32px 24px;border-radius:12px;">
          <div style="text-align:center;margin-bottom:24px;">
            <h1 style="font-size:20px;color:#1a3a1f;margin:0;">KennediaJobs</h1>
          </div>
          <div style="background:white;border-radius:10px;padding:28px 32px;border:1px solid #e5e7eb;">
            <h2 style="font-size:17px;color:#111827;margin:0 0 12px;">Job Posting Request Received</h2>
            <p style="color:#4b5563;font-size:14px;line-height:1.6;margin:0 0 16px;">
              Hi {req.contact_person},<br><br>
              Thank you for submitting your job posting request for <strong>{req.job_title}</strong> at <strong>{req.company_name}</strong>.
            </p>
            <div style="background:#f0fdf4;border-radius:8px;padding:14px 18px;margin-bottom:16px;">
              <p style="margin:0;font-size:13px;color:#15803d;font-weight:600;">What happens next?</p>
              <p style="margin:6px 0 0;font-size:13px;color:#4b5563;">
                Our team will review your request and post the job listing within 24 hours.
                You will receive application notifications at <strong>{req.notification_email}</strong>.
              </p>
            </div>
            <p style="color:#9ca3af;font-size:12px;margin:0;">Best regards,<br>Kennedia Jobs Team</p>
          </div>
        </div>"""
        try:
            send_email(req.email, req.contact_person,
                      f'Job Posting Request Received — {req.job_title}', html)
        except Exception:
            pass

        return Response({
            'message': 'Your job posting request has been received. We will post it within 24 hours.',
            'reference': req.id,
        }, status=status.HTTP_201_CREATED)


class AdminEmployerRequestListView(generics.ListAPIView):
    """
    GET /api/submissions/admin/employer-requests/
    Admin view of all employer job requests.
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, *args, **kwargs):
        from .models import EmployerJobRequest
        reqs = EmployerJobRequest.objects.all()
        data = [{
            'id': r.id,
            'company_name': r.company_name,
            'contact_person': r.contact_person,
            'email': r.email,
            'phone': r.phone,
            'job_title': r.job_title,
            'industry': r.industry,
            'location': r.location,
            'salary_range': r.salary_range,
            'job_description': r.job_description,
            'requirements': r.requirements,
            'notification_email': r.notification_email,
            'package': r.package,
            'status': r.status,
            'submitted_at': r.submitted_at,
        } for r in reqs]
        return Response(data)

    def patch(self, request, *args, **kwargs):
        from .models import EmployerJobRequest
        req_id = kwargs.get('pk')
        try:
            req = EmployerJobRequest.objects.get(pk=req_id)
            req.status = request.data.get('status', req.status)
            req.admin_notes = request.data.get('admin_notes', req.admin_notes)
            req.save()
            return Response({'message': 'Updated.'})
        except EmployerJobRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)


class AdminEmployerRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/submissions/admin/employer-requests/<pk>/
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        from .models import EmployerJobRequest
        return EmployerJobRequest.objects.all()

    def get(self, request, *args, **kwargs):
        from .models import EmployerJobRequest
        req = get_object_or_404(EmployerJobRequest, pk=kwargs['pk'])
        return Response({
            'id': req.id, 'company_name': req.company_name,
            'contact_person': req.contact_person, 'email': req.email,
            'phone': req.phone, 'job_title': req.job_title,
            'industry': req.industry, 'location': req.location,
            'job_description': req.job_description, 'requirements': req.requirements,
            'notification_email': req.notification_email, 'package': req.package,
            'salary_range': req.salary_range, 'status': req.status,
            'submitted_at': req.submitted_at,
        })

    def patch(self, request, *args, **kwargs):
        from .models import EmployerJobRequest
        req = get_object_or_404(EmployerJobRequest, pk=kwargs['pk'])
        req.status = request.data.get('status', req.status)
        req.admin_notes = request.data.get('admin_notes', req.admin_notes)
        req.save()
        return Response({'message': 'Updated.'})

    def delete(self, request, *args, **kwargs):
        from .models import EmployerJobRequest
        req = get_object_or_404(EmployerJobRequest, pk=kwargs['pk'])
        req.delete()
        return Response(status=204)
