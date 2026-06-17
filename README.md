# Kennedia Jobs — Django Backend

Full REST API backend for the Kennedia Jobs platform, built with **Django 4.2** and **Django REST Framework**.

---

## 🗂 Project Structure

```
kennedia_backend/
├── core/               # Project config (settings, root URLs)
├── users/              # Custom user model, auth, roles, dashboard
├── jobs/               # Job listings, applications, saved jobs
├── blog/               # Blog posts CRUD
├── submissions/        # CV writing, job search, training, contact forms
├── manage.py
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

### 1. Clone / copy the project
```bash
cd kennedia_backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Seed initial data (jobs + blog posts from the frontend)
```bash
python manage.py seed_data
```

### 7. Create a super admin account
```bash
python manage.py createsuperuser
# Then update their role in admin: set role = super_admin
```

### 8. Start the development server
```bash
python manage.py runserver
```

API is live at: **http://127.0.0.1:8000/api/**
Django Admin: **http://127.0.0.1:8000/admin/**

---

## 🔐 Authentication

All auth uses **JWT (Bearer tokens)**.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register new job seeker |
| `/api/auth/login/` | POST | Login → returns access + refresh tokens |
| `/api/auth/logout/` | POST | Blacklist refresh token |
| `/api/auth/token/refresh/` | POST | Refresh access token |
| `/api/auth/profile/` | GET/PATCH | View/update own profile |
| `/api/auth/change-password/` | POST | Change password |
| `/api/auth/dashboard/stats/` | GET | User dashboard stats |

**Login request body:**
```json
{ "email": "user@example.com", "password": "yourpassword" }
```

**Using tokens:**
```
Authorization: Bearer <access_token>
```

---

## 💼 Jobs API

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/jobs/` | GET | Public | List active jobs. Filters: `?industry=&location=&search=&salary=below_500k\|above_500k` |
| `/api/jobs/<id>/` | GET | Public | Job detail (increments views) |
| `/api/jobs/<id>/apply/` | POST | Public | Submit application + CV upload |
| `/api/jobs/my-applications/` | GET | User | My applications |
| `/api/jobs/saved/` | GET/POST | User | List / save a job |
| `/api/jobs/<id>/unsave/` | DELETE | User | Remove from saved |
| `/api/jobs/admin/jobs/` | GET/POST | Admin | All jobs / create job |
| `/api/jobs/admin/jobs/<id>/` | GET/PATCH/DELETE | Admin | Manage job |
| `/api/jobs/admin/applications/` | GET | Admin | All applications. Filters: `?job=&status=&search=` |
| `/api/jobs/admin/applications/<id>/` | GET/PATCH/DELETE | Admin | Update status, add notes |
| `/api/jobs/admin/stats/` | GET | Admin | Dashboard stats |

**Apply (easy apply, multipart/form-data):**
```
POST /api/jobs/3/apply/
first_name, last_name, email, phone, years_of_experience, cover_letter, cv_file (file)
```

**Application statuses:** `pending` → `reviewed` → `shortlisted` → `hired` / `rejected`
Applicants receive **automatic email notifications** on status change.

---

## 📝 Blog API

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/blog/` | GET | Public | List published posts. `?category=&search=` |
| `/api/blog/<slug>/` | GET | Public | Post detail (increments views) |
| `/api/blog/admin/posts/` | GET/POST | Admin | List all / create post |
| `/api/blog/admin/posts/<id>/` | GET/PATCH/DELETE | Admin | Manage post |

**Categories:** `career_tips`, `interview_prep`, `salary_finance`, `industry_news`, `cv_resume`, `company_news`

---

## 📋 Submissions API

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/submissions/cv-writing/` | POST | Public | CV writing request |
| `/api/submissions/job-search/` | POST | Public | Job search registration |
| `/api/submissions/training/` | POST | Public | Training enrolment |
| `/api/submissions/contact/` | POST | Public | Contact message |
| `/api/submissions/admin/cv-writing/` | GET | Admin | All CV requests |
| `/api/submissions/admin/cv-writing/<id>/` | GET/PATCH/DELETE | Admin | Manage request |
| `/api/submissions/admin/job-search/` | GET | Admin | All registrations |
| `/api/submissions/admin/training/` | GET | Admin | All enrolments |
| `/api/submissions/admin/contact/` | GET | Admin | All messages |
| `/api/submissions/export/<model>/` | GET | Admin | CSV export |

**CSV Export models:** `cv_writing`, `job_search`, `training`, `contact`, `applications`

---

## 👥 User Roles & Permissions

| Role | Can Do |
|------|--------|
| `job_seeker` | Register, apply to jobs, save jobs, manage own profile |
| `admin` | All of the above + manage jobs, blog, view all submissions, export CSV |
| `super_admin` | All of the above + create/manage other admin accounts, manage all users |

---

## 💰 Salary Threshold Logic

Jobs with salary **≥ ₦500,000/month** have `requires_registration: true` in the API response. The frontend uses this to show:
- ⚡ **Easy Apply** for jobs below the threshold
- 🔒 **Register to Apply** for high-pay senior roles

The threshold is configurable in `settings.py`:
```python
REGISTER_APPLY_THRESHOLD = 500_000
```

---

## 📧 Email Notifications

Automatic emails are sent for:
- ✅ New job application (confirmation to applicant)
- 🔄 Application status change (reviewed / shortlisted / hired / rejected)
- 📄 CV writing request received
- 🔍 Job search registration confirmed
- 🎓 Training enrolment received

Set `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` in `.env` for real emails.

---

## 🗄 Switching to PostgreSQL

1. Uncomment the PostgreSQL block in `settings.py`
2. Add DB credentials to `.env`
3. Install the driver: `pip install psycopg2-binary`
4. Run: `python manage.py migrate`

---

## 🌐 Deployment Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Set a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Configure `CORS_ALLOWED_ORIGINS` with your frontend URL
- [ ] Switch to PostgreSQL
- [ ] Set up real SMTP email
- [ ] Install `gunicorn` and `whitenoise`
- [ ] Run `python manage.py collectstatic`
- [ ] Set up SSL (HTTPS)

---

## 🔗 Connecting the Frontend

In your HTML frontend, replace the static JS data arrays with `fetch()` calls:

```javascript
// Example: load jobs from API
async function loadJobs() {
  const res = await fetch('http://127.0.0.1:8000/api/jobs/');
  const data = await res.json();
  // data.results = array of job objects
  renderJobs(data.results);
}

// Example: submit application
async function submitApplication(jobId, formData) {
  const res = await fetch(`http://127.0.0.1:8000/api/jobs/${jobId}/apply/`, {
    method: 'POST',
    body: formData  // FormData object (handles file upload)
  });
  return res.json();
}

// Example: admin login
async function adminLogin(email, password) {
  const res = await fetch('http://127.0.0.1:8000/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json();
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  return data.user; // { id, email, full_name, role }
}
```
