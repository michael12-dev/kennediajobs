"""
Kennedia Jobs — users/urls.py
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # ── Core Auth ──────────────────────────────────────────────────────────────
    path('login/',          views.KennediaTokenObtainPairView.as_view(), name='login'),
    path('logout/',         views.LogoutView.as_view(),                  name='logout'),
    path('token/refresh/',  TokenRefreshView.as_view(),                  name='token_refresh'),

    # ── Registration — 3-step flow ─────────────────────────────────────────────
    # Step 1: Check email is free + send OTP
    path('check-email/',              views.CheckEmailView.as_view(),              name='check_email'),
    # Step 2: Verify OTP
    path('verify-registration-otp/',  views.VerifyRegistrationOTPView.as_view(),   name='verify_registration_otp'),
    # Step 3: Create account (email already verified)
    path('register/',                 views.RegisterView.as_view(),                name='register'),

    # ── Backward-compat OTP verify (for existing inactive accounts) ────────────
    path('verify-email/',   views.VerifyEmailView.as_view(),             name='verify_email'),
    path('resend-otp/',     views.ResendOTPView.as_view(),               name='resend_otp'),

    # ── Forgot / Reset Password ────────────────────────────────────────────────
    path('forgot-password/',      views.ForgotPasswordView.as_view(),      name='forgot_password'),
    path('verify-reset-otp/',     views.VerifyResetOTPView.as_view(),       name='verify_reset_otp'),
    path('reset-password/',       views.ResetPasswordView.as_view(),        name='reset_password'),

    # ── Profile ────────────────────────────────────────────────────────────────
    path('profile/',         views.ProfileView.as_view(),                name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(),         name='change_password'),
    path('dashboard/stats/', views.dashboard_stats,                      name='dashboard_stats'),

    # ── Admin Management (super_admin only) ────────────────────────────────────
    path('admin/users/',           views.AdminUserListView.as_view(),    name='admin_user_list'),
    path('admin/users/<int:pk>/',  views.AdminUserDetailView.as_view(),  name='admin_user_detail'),
    path('admin/create/',          views.CreateAdminView.as_view(),      name='create_admin'),
]
