"""
Kennedia Jobs — users/views.py
"""
import random
import string

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer, UserProfileSerializer,
    AdminUserSerializer, ChangePasswordSerializer,
    KennediaTokenObtainPairSerializer,
)
from .permissions import IsAdminOrSuperAdmin, IsSuperAdmin
from .email_service import (
    send_otp_email,
    send_password_reset_email,
    send_admin_welcome_email,
)

User = get_user_model()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def generate_otp(length=6) -> str:
    return ''.join(random.choices(string.digits, k=length))

def otp_cache_key(purpose: str, email: str) -> str:
    return f"otp:{purpose}:{email.lower()}"

def email_verified_key(email: str) -> str:
    """Marks that this email passed OTP — valid for 15 min to complete registration."""
    return f"email_verified:{email.lower()}"

OTP_TTL = 600       # 10 minutes
VERIFIED_TTL = 900  # 15 minutes — window to complete registration after OTP


# ─── Auth ─────────────────────────────────────────────────────────────────────

class KennediaTokenObtainPairView(TokenObtainPairView):
    """Login endpoint — returns JWT + user info."""
    serializer_class = KennediaTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            try:
                from django.utils import timezone
                email = request.data.get('email', '').lower()
                User.objects.filter(email__iexact=email).update(last_login=timezone.now())
            except Exception:
                pass
        return response


class CheckEmailView(APIView):
    """
    POST /api/auth/check-email/
    Body: { "email": "user@example.com" }

    Step 1 of registration:
    - Checks the email is not already registered
    - Sends a 6-digit OTP to the email
    - Returns success so frontend can show OTP screen
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()

        if not email:
            return Response(
                {'error': 'Email address is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if email is already registered and active
        if User.objects.filter(email__iexact=email, is_active=True).exists():
            return Response(
                {'error': 'This email address is already registered. Please log in instead.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clean up any stale inactive account with this email (e.g. previous failed registration)
        User.objects.filter(email__iexact=email, is_active=False).delete()

        # Generate OTP and cache it
        otp = generate_otp()
        cache.set(otp_cache_key('register', email), otp, OTP_TTL)

        # Send OTP email
        sent = send_otp_email(email, email.split('@')[0], otp)

        if not sent:
            return Response(
                {'error': 'Could not send verification email. Please check the address and try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'message': 'Verification code sent. Please check your email.',
            'email': email,
        })


class VerifyRegistrationOTPView(APIView):
    """
    POST /api/auth/verify-registration-otp/
    Body: { "email": "...", "otp": "123456" }

    Step 2 of registration:
    - Verifies the OTP
    - Marks the email as verified in cache so registration can proceed
    - Does NOT create the account yet
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp_input = request.data.get('otp', '').strip()

        if not email or not otp_input:
            return Response(
                {'error': 'Email and verification code are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cached_otp = cache.get(otp_cache_key('register', email))

        if not cached_otp:
            return Response(
                {'error': 'Verification code has expired. Please start again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_input != cached_otp:
            return Response(
                {'error': 'Incorrect verification code. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark email as verified — frontend can now show registration form
        cache.delete(otp_cache_key('register', email))
        cache.set(email_verified_key(email), True, VERIFIED_TTL)

        return Response({
            'message': 'Email verified. Please complete your registration.',
            'email': email,
            'verified': True,
        })


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Body: { email, username, first_name, last_name, password, password2 }

    Step 3 of registration:
    - Requires email to have been verified via /check-email/ + /verify-registration-otp/
    - Creates the account as active immediately (OTP already verified)
    - Returns JWT tokens so user is logged in right away
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email', '').strip().lower()

        # Confirm OTP was verified for this email
        if not cache.get(email_verified_key(email)):
            return Response(
                {'error': 'Email not verified. Please complete the verification step first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create user as active (email already verified)
        user = serializer.save()
        user.is_active = True
        user.save(update_fields=['is_active'])

        # Clear the verified flag
        cache.delete(email_verified_key(email))

        # Update last_login since this is effectively a first login
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        # Issue tokens — user is logged in immediately
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Account created successfully. Welcome to Kennedia Jobs!',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': user.role,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    """
    POST /api/auth/verify-email/
    Kept for backward compatibility — verifies OTP and activates account.
    (Used when account was created inactive and needs post-registration verification.)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp_input = request.data.get('otp', '').strip()

        if not email or not otp_input:
            return Response({'error': 'Email and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        cached_otp = cache.get(otp_cache_key('register', email))

        if not cached_otp:
            return Response({'error': 'Verification code has expired. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_input != cached_otp:
            return Response({'error': 'Invalid verification code. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.save(update_fields=['is_active'])
        cache.delete(otp_cache_key('register', email))

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Email verified successfully. Welcome to Kennedia Jobs!',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': user.role,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class ResendOTPView(APIView):
    """
    POST /api/auth/resend-otp/
    Body: { "email": "...", "purpose": "register" | "password_reset" }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        purpose = request.data.get('purpose', 'register')

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp()
        cache.set(otp_cache_key(purpose, email), otp, OTP_TTL)

        if purpose == 'password_reset':
            try:
                user = User.objects.get(email__iexact=email)
                send_password_reset_email(email, user.get_full_name() or email, otp)
            except User.DoesNotExist:
                pass
        else:
            send_otp_email(email, email.split('@')[0], otp)

        return Response({'message': 'A new verification code has been sent to your email.'})


# ─── Forgot Password ──────────────────────────────────────────────────────────

class VerifyResetOTPView(APIView):
    """
    POST /api/auth/verify-reset-otp/
    Body: { "email": "...", "otp": "123456" }
    Validates the reset OTP. If correct, marks it as verified in cache
    so the reset-password endpoint knows it was legitimately verified.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp_input = request.data.get('otp', '').strip()

        if not email or not otp_input:
            return Response(
                {'error': 'Email and code are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cached_otp = cache.get(otp_cache_key('password_reset', email))

        if not cached_otp:
            return Response(
                {'error': 'Reset code has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_input != cached_otp:
            return Response(
                {'error': 'Incorrect reset code. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # OTP is correct — mark as verified so reset-password can proceed
        # We keep the OTP in cache so reset-password can do a final check
        cache.set(otp_cache_key('password_reset_verified', email), True, VERIFIED_TTL)

        return Response({
            'message': 'Code verified. You can now set a new password.',
            'verified': True,
        })


class ForgotPasswordView(APIView):
    """
    POST /api/auth/forgot-password/
    Body: { "email": "..." }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'message': 'If that email is registered, a reset code has been sent.'})

        otp = generate_otp()
        cache.set(otp_cache_key('password_reset', email), otp, OTP_TTL)
        send_password_reset_email(email, user.get_full_name() or email, otp)

        return Response({
            'message': 'A 6-digit reset code has been sent to your email.',
            'email': email,
        })


class ResetPasswordView(APIView):
    """
    POST /api/auth/reset-password/
    Body: { "email", "otp", "new_password", "confirm_password" }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp_input = request.data.get('otp', '').strip()
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')

        if not all([email, otp_input, new_password, confirm_password]):
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)

        cached_otp = cache.get(otp_cache_key('password_reset', email))

        if not cached_otp:
            return Response({'error': 'Reset code has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_input != cached_otp:
            return Response({'error': 'Invalid reset code. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

        # Also require that verify-reset-otp was called first
        if not cache.get(otp_cache_key('password_reset_verified', email)):
            return Response({'error': 'Please verify your reset code first.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.is_active = True
        user.save()
        cache.delete(otp_cache_key('password_reset', email))
        cache.delete(otp_cache_key('password_reset_verified', email))

        return Response({'message': 'Password reset successfully. You can now log in.'})


# ─── Logout ───────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


# ─── Profile ──────────────────────────────────────────────────────────────────

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Password updated successfully.'})


# ─── Admin User Management ────────────────────────────────────────────────────

class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        qs = User.objects.all().order_by('-created_at')
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(email__icontains=search) | qs.filter(first_name__icontains=search)
        return qs


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsSuperAdmin]
    queryset = User.objects.all()


class CreateAdminView(generics.CreateAPIView):
    permission_classes = [IsSuperAdmin]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email', '').strip()
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        role = request.data.get('role', 'admin')
        password = request.data.get('password', '')
        username = request.data.get('username', email.split('@')[0])

        if not email or not first_name or not password:
            return Response({'error': 'Email, first name and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if role not in ('admin', 'super_admin'):
            return Response({'error': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email__iexact=email).exists():
            return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username, email=email,
            first_name=first_name, last_name=last_name,
            password=password, role=role, is_active=True,
        )

        full_name = f"{first_name} {last_name}".strip()
        send_admin_welcome_email(email, full_name, password, role)

        return Response(AdminUserSerializer(user).data, status=status.HTTP_201_CREATED)


# ─── Dashboard stats ──────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    user = request.user
    apps = user.applications.all()
    return Response({
        'total_applications': apps.count(),
        'pending': apps.filter(status='pending').count(),
        'reviewed': apps.filter(status='reviewed').count(),
        'shortlisted': apps.filter(status='shortlisted').count(),
        'rejected': apps.filter(status='rejected').count(),
        'saved_jobs': user.saved_jobs.count(),
        'profile_complete': user.is_profile_complete,
        'under_review': apps.filter(status__in=['reviewed', 'shortlisted']).count(),
    })
