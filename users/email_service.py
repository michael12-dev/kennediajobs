
import requests
from django.conf import settings


BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_email(to_email: str, to_name: str, subject: str, html_content: str) -> bool:
    """
    Send a transactional email via Brevo.
    Returns True on success, False on failure.
    """
    payload = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html_content,
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.BREVO_API_KEY,
    }

    try:
        response = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=10)
        print("BREVO RESPONSE:", response.status_code, response.text)  # ← add this line
        return response.status_code in (200, 201)
    except Exception as e:
        print("BREVO ERROR:", e)  # ← add this too
        return False


# ─── Email templates ──────────────────────────────────────────────────────────

def send_otp_email(to_email: str, to_name: str, otp: str) -> bool:
    subject = "Verify your Kennedia Jobs account"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;background:#f9fafb;padding:32px 24px;border-radius:12px;">
      <div style="text-align:center;margin-bottom:28px;">
        <h1 style="font-size:22px;color:#1a3a1f;margin:0;">KennediaJobs</h1>
        <p style="color:#6b7280;font-size:13px;margin-top:4px;">Job Placement & Career Services</p>
      </div>
      <div style="background:white;border-radius:10px;padding:28px 32px;border:1px solid #e5e7eb;">
        <h2 style="font-size:18px;color:#111827;margin:0 0 8px;">Verify your email address</h2>
        <p style="color:#4b5563;font-size:14px;line-height:1.6;margin:0 0 24px;">
          Hi {to_name},<br><br>
          Thank you for registering on <strong>Kennedia Jobs</strong>. 
          Enter the verification code below to activate your account.
        </p>
        <div style="text-align:center;margin:28px 0;">
          <div style="display:inline-block;background:#f0fdf4;border:2px solid #16a34a;border-radius:12px;padding:18px 40px;">
            <span style="font-size:36px;font-weight:800;letter-spacing:10px;color:#15803d;font-family:monospace;">{otp}</span>
          </div>
          <p style="color:#6b7280;font-size:12px;margin-top:12px;">This code expires in <strong>10 minutes</strong></p>
        </div>
        <p style="color:#9ca3af;font-size:12px;margin:0;border-top:1px solid #f3f4f6;padding-top:16px;">
          If you didn't create an account on Kennedia Jobs, you can safely ignore this email.
        </p>
      </div>
      <p style="text-align:center;color:#9ca3af;font-size:11px;margin-top:20px;">
        © 2026 Kennedia Consulting Limited. All rights reserved.
      </p>
    </div>
    """
    return send_email(to_email, to_name, subject, html)


def send_password_reset_email(to_email: str, to_name: str, otp: str) -> bool:
    subject = "Reset your Kennedia Jobs password"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;background:#f9fafb;padding:32px 24px;border-radius:12px;">
      <div style="text-align:center;margin-bottom:28px;">
        <h1 style="font-size:22px;color:#1a3a1f;margin:0;">KennediaJobs</h1>
        <p style="color:#6b7280;font-size:13px;margin-top:4px;">Job Placement & Career Services</p>
      </div>
      <div style="background:white;border-radius:10px;padding:28px 32px;border:1px solid #e5e7eb;">
        <h2 style="font-size:18px;color:#111827;margin:0 0 8px;">Password Reset Request</h2>
        <p style="color:#4b5563;font-size:14px;line-height:1.6;margin:0 0 24px;">
          Hi {to_name},<br><br>
          We received a request to reset your password. Use the code below to set a new password.
        </p>
        <div style="text-align:center;margin:28px 0;">
          <div style="display:inline-block;background:#fef2f2;border:2px solid #dc2626;border-radius:12px;padding:18px 40px;">
            <span style="font-size:36px;font-weight:800;letter-spacing:10px;color:#b91c1c;font-family:monospace;">{otp}</span>
          </div>
          <p style="color:#6b7280;font-size:12px;margin-top:12px;">This code expires in <strong>10 minutes</strong></p>
        </div>
        <p style="color:#9ca3af;font-size:12px;margin:0;border-top:1px solid #f3f4f6;padding-top:16px;">
          If you didn't request a password reset, please ignore this email. Your password will not change.
        </p>
      </div>
      <p style="text-align:center;color:#9ca3af;font-size:11px;margin-top:20px;">
        © 2026 Kennedia Consulting Limited. All rights reserved.
      </p>
    </div>
    """
    return send_email(to_email, to_name, subject, html)


def send_admin_welcome_email(to_email: str, to_name: str, temp_password: str, role: str) -> bool:
    subject = "Your Kennedia Jobs Admin Account"
    role_display = "Super Admin" if role == "super_admin" else "Admin"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;background:#f9fafb;padding:32px 24px;border-radius:12px;">
      <div style="text-align:center;margin-bottom:28px;">
        <h1 style="font-size:22px;color:#1a3a1f;margin:0;">KennediaJobs</h1>
        <p style="color:#6b7280;font-size:13px;margin-top:4px;">Admin Portal</p>
      </div>
      <div style="background:white;border-radius:10px;padding:28px 32px;border:1px solid #e5e7eb;">
        <h2 style="font-size:18px;color:#111827;margin:0 0 8px;">Welcome to the Admin Panel</h2>
        <p style="color:#4b5563;font-size:14px;line-height:1.6;margin:0 0 20px;">
          Hi {to_name},<br><br>
          A <strong>{role_display}</strong> account has been created for you on Kennedia Jobs.
          Use the credentials below to log in.
        </p>
        <div style="background:#f8fafc;border-radius:8px;padding:16px 20px;margin-bottom:20px;border:1px solid #e2e8f0;">
          <p style="margin:0 0 8px;font-size:13px;"><strong>Email:</strong> {to_email}</p>
          <p style="margin:0;font-size:13px;"><strong>Temporary Password:</strong> 
            <span style="font-family:monospace;background:#f1f5f9;padding:2px 8px;border-radius:4px;">{temp_password}</span>
          </p>
        </div>
        <p style="color:#ef4444;font-size:13px;font-weight:600;">
          ⚠️ Please change your password immediately after logging in.
        </p>
      </div>
      <p style="text-align:center;color:#9ca3af;font-size:11px;margin-top:20px;">
        © 2026 Kennedia Consulting Limited. All rights reserved.
      </p>
    </div>
    """
    return send_email(to_email, to_name, subject, html)
