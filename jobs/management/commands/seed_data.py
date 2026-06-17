"""
Management command to seed the database with initial jobs and blog posts
from the original HTML frontend data.

Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from jobs.models import Job
from blog.models import BlogPost

User = get_user_model()

JOBS = [
    {'title': 'Partnership Manager, Public Sector', 'company': 'Kennedia Consulting', 'industry': 'banking_finance', 'job_type': 'full_time', 'location': 'FCT, Lagos, Rivers', 'salary': 750000, 'description': 'Responsible for developing, managing, and strengthening strategic relationships with government institutions and public sector entities.', 'requirements': 'Bachelor\'s degree in Business, Finance or related field.\n5+ years in partnership management or business development.\nStrong knowledge of public sector procurement and governance.\nExcellent relationship management and communication skills.', 'status': 'active'},
    {'title': 'Project Manager', 'company': 'Kennedia Consulting', 'industry': 'banking_finance', 'job_type': 'full_time', 'location': 'Lagos, Nationwide', 'salary': 600000, 'description': 'Responsible for planning, coordinating, executing, monitoring, and delivering strategic and operational projects across the organisation.', 'requirements': 'PMP certification preferred.\n4+ years project management experience.\nProficiency in project management tools.\nStrong stakeholder management skills.', 'status': 'active'},
    {'title': 'Partnership Manager, Private Banking', 'company': 'Kennedia Consulting', 'industry': 'banking_finance', 'job_type': 'full_time', 'location': 'FCT, Lagos', 'salary': 850000, 'description': 'Driving implementation of the Bank\'s Personal and Private Banking strategy through customer acquisition and portfolio management.', 'requirements': 'Minimum 6 years in private banking or wealth management.\nProven track record in HNI client acquisition.\nStrong financial product knowledge.', 'status': 'active'},
    {'title': 'Deputy Treasurer', 'company': 'Kennedia Consulting', 'industry': 'banking_finance', 'job_type': 'full_time', 'location': 'Lagos', 'salary': 1200000, 'description': 'Supporting the Treasurer in the management of the Bank\'s liquidity, funding, investments, and balance sheet strategy.', 'requirements': 'ACA/CFA qualified.\n8+ years treasury experience in a commercial bank.\nDeep knowledge of money markets and FX operations.', 'status': 'active'},
    {'title': 'Business Development Manager', 'company': 'Kennedia Consulting', 'industry': 'hr_consulting', 'job_type': 'full_time', 'location': 'Lagos, Abuja', 'salary': 480000, 'description': 'Drive new business opportunities and manage key client relationships to grow revenue across multiple sectors.', 'requirements': 'Bachelor\'s degree in Business or Marketing.\n4+ years B2B sales experience.\nExcellent negotiation and presentation skills.', 'status': 'active'},
    {'title': 'Direct Sales Agent (DSA)', 'company': 'Kennedia Consulting', 'industry': 'banking_finance', 'job_type': 'full_time', 'location': 'Lagos, Nationwide', 'salary': 120000, 'description': 'Responsible for customer acquisition, account opening, and product sales in assigned territory.', 'requirements': 'SSCE/OND minimum.\nStrong communication and persuasion skills.\nAbility to meet monthly sales targets.', 'status': 'active'},
    {'title': 'Relationship Manager', 'company': 'Kennedia Consulting', 'industry': 'banking_finance', 'job_type': 'full_time', 'location': 'Lagos, Rivers', 'salary': 380000, 'description': 'Build and maintain strong relationships with clients in the retail and commercial banking space.', 'requirements': 'BSc in any discipline.\n2–5 years relationship management experience.\nCustomer-focused with strong commercial acumen.', 'status': 'active'},
    {'title': 'HR Manager', 'company': 'Kennedia Consulting', 'industry': 'hr_consulting', 'job_type': 'full_time', 'location': 'Lagos', 'salary': 550000, 'description': 'Oversee HR operations, talent acquisition, employee relations, and organisational development activities.', 'requirements': 'BSc in Human Resources or related field.\nCIPM/SHRM certification preferred.\n5+ years progressive HR experience.', 'status': 'active'},
    {'title': 'Digital Marketer', 'company': 'Kennedia Consulting', 'industry': 'technology', 'job_type': 'full_time', 'location': 'Lagos', 'salary': 250000, 'description': 'Plan and execute digital marketing campaigns across social media, email, and search channels to drive brand awareness.', 'requirements': 'BSc in Marketing, Communications or related field.\n2+ years digital marketing experience.\nProficiency in Google Ads, Meta Ads, and analytics tools.', 'status': 'active'},
    {'title': 'Finance Manager', 'company': 'Kennedia Consulting', 'industry': 'banking_finance', 'job_type': 'full_time', 'location': 'Abuja, Lagos', 'salary': 650000, 'description': 'Manage financial planning, budgeting, reporting, and controls to support business decision-making.', 'requirements': 'ACA/ACCA qualified.\n6+ years in financial management.\nStrong financial modelling and reporting skills.', 'status': 'active'},
]

BLOG_POSTS = [
    {'title': '10 Things Nigerian Employers Look for in a Top Candidate', 'category': 'career_tips', 'emoji': '💡', 'author_display': 'Kennedia Editorial', 'read_time': '6 min', 'excerpt': 'From communication skills to cultural fit, discover the exact traits that make candidates stand out to HR managers at Nigeria\'s leading firms.', 'body': '<h3>Why First Impressions Still Matter</h3><p>In Nigeria\'s competitive job market, your CV gets an average of 7 seconds of attention before a recruiter moves on. That means your first impression must be immediate and compelling.</p><h3>Top Qualities Nigerian Employers Seek</h3><p>1. <strong>Strong communication skills</strong> — both written and verbal. Employers rate this as the #1 differentiator between equally qualified candidates.</p><p>2. <strong>Cultural adaptability</strong> — Nigeria\'s corporate culture blends global professional standards with local relationship-based values.</p><p>3. <strong>Digital literacy</strong> — post-pandemic, virtually every employer requires comfort with productivity tools and data interpretation.</p>', 'status': 'published'},
    {'title': 'How to Answer "Tell Me About Yourself" Like a Pro', 'category': 'interview_prep', 'emoji': '🎯', 'author_display': 'Tunde Adeyemi', 'read_time': '4 min', 'excerpt': 'Most candidates stumble on this simple question. Here\'s a proven framework to craft a compelling answer that sets the tone for your entire interview.', 'body': '<h3>Why This Question Is Actually a Gift</h3><p>"Tell me about yourself" is your invitation to control the narrative. Most candidates waste it by rambling or reciting their CV.</p><h3>The P-E-S Framework</h3><p><strong>P (Professional background):</strong> Start with your current role and key responsibilities. Keep it to 2 sentences.</p><p><strong>E (Experience highlights):</strong> Name 1–2 significant achievements relevant to the role.</p><p><strong>S (Skills & why you\'re here):</strong> Briefly tie your background to why this specific role excites you.</p>', 'status': 'published'},
    {'title': 'Nigeria Salary Benchmarks 2026: What Are You Worth?', 'category': 'salary_finance', 'emoji': '💰', 'author_display': 'Chioma Obi', 'read_time': '8 min', 'excerpt': 'Comprehensive salary data across banking, finance, tech, FMCG, and consulting sectors in Nigeria. Know your market value before your next negotiation.', 'body': '<h3>Banking & Finance</h3><p>Entry-level analysts: ₦150,000–₦280,000/month. Senior relationship managers: ₦500,000–₦900,000. Deputy treasurers and CFO-level roles: ₦1.2M–₦3M+ depending on institution size.</p><h3>Technology</h3><p>Junior developers: ₦180,000–₦350,000. Mid-level full-stack engineers: ₦400,000–₦750,000. Senior engineers at fintech firms: ₦900,000–₦2M+.</p>', 'status': 'published'},
    {'title': 'Nigeria\'s Job Market in 2026: Sectors Hiring the Most', 'category': 'industry_news', 'emoji': '📰', 'author_display': 'Kennedia Editorial', 'read_time': '5 min', 'excerpt': 'Which sectors are seeing the biggest hiring surge? Banking, fintech, and renewable energy top the list.', 'body': '<h3>Banking & Fintech Lead the Way</h3><p>Nigeria\'s banking sector continues its aggressive talent acquisition drive in 2026, particularly following the CBN\'s recapitalisation directive.</p><h3>Renewable Energy Emerges</h3><p>The energy transition is creating thousands of new roles in solar installation, project management, and environmental compliance.</p>', 'status': 'published'},
    {'title': '7 LinkedIn Habits That Get Nigerian Professionals Noticed', 'category': 'career_tips', 'emoji': '🚀', 'author_display': 'Tunde Adeyemi', 'read_time': '5 min', 'excerpt': 'Most Nigerian professionals have a LinkedIn profile but very few use it strategically. These 7 habits will transform yours into a recruiter magnet.', 'body': '<h3>Your Profile is Your 24/7 Salesperson</h3><p>Recruiters at top Nigerian firms use LinkedIn daily to headhunt candidates. If your profile isn\'t optimised, you\'re invisible to opportunities you never knew were available.</p>', 'status': 'published'},
    {'title': 'Competency-Based Interviews: The STAR Method Explained', 'category': 'interview_prep', 'emoji': '🧠', 'author_display': 'Chioma Obi', 'read_time': '6 min', 'excerpt': 'Most Nigerian banks and multinationals now use competency-based interviews. Master the STAR method and watch your success rate soar.', 'body': '<h3>What is a Competency-Based Interview?</h3><p>Instead of asking "Are you a team player?", employers ask "Tell me about a time when you had to work through a difficult team conflict."</p><h3>The STAR Method</h3><p><strong>S — Situation:</strong> Set the scene. <strong>T — Task:</strong> Your specific responsibility. <strong>A — Action:</strong> What YOU did. <strong>R — Result:</strong> Quantify the outcome.</p>', 'status': 'published'},
]


class Command(BaseCommand):
    help = 'Seed database with initial jobs and blog posts from the Kennedia frontend'

    def handle(self, *args, **options):
        self.stdout.write('Seeding jobs...')
        for job_data in JOBS:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=job_data['company'],
                defaults=job_data
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {job.title}')

        self.stdout.write('\nSeeding blog posts...')
        for post_data in BLOG_POSTS:
            post, created = BlogPost.objects.get_or_create(
                title=post_data['title'],
                defaults=post_data
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {post.title}')

        self.stdout.write(self.style.SUCCESS('\n✅ Seed complete!'))
