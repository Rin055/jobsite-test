from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from jobs.models import Job, Application
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Populate database with realistic sample data'

    def handle(self, *args, **options):
        self.stdout.write("Creating sample users and jobs...")

        # Create Employer Users
        employers_data = [
            ('tech_recruiter', 'tech@company.com', 'Tech Company', 'Top tech company hiring engineers'),
            ('startup_hr', 'hr@startup.io', 'Startup Inc', 'Fast-growing startup looking for talent'),
            ('finance_jobs', 'jobs@financeplus.com', 'FinancePlus', 'Leading financial services firm'),
            ('design_studio', 'hire@creativestudio.com', 'Creative Studio', 'Award-winning design agency'),
            ('remote_work', 'jobs@remotefirst.io', 'RemoteFirst', 'Global remote-first company'),
        ]

        employers = []
        for username, email, company, bio in employers_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': company.split()[0],
                    'last_name': 'HR' if len(company.split()) > 1 else 'Team',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                profile = user.profile
                profile.is_employer = True
                profile.company_name = company
                profile.bio = bio
                profile.save()
                self.stdout.write(f"✓ Created employer: {username}")
            employers.append(user)

        # Create Job Seeker Users
        seekers_data = [
            ('john_dev', 'john@example.com', 'Passionate full-stack developer with 5+ years experience'),
            ('sarah_designer', 'sarah@example.com', 'UI/UX Designer specializing in web and mobile'),
            ('mike_analyst', 'mike@example.com', 'Data analyst with strong SQL and Python skills'),
            ('emma_manager', 'emma@example.com', 'Project manager with agile and scrum experience'),
            ('alex_frontend', 'alex@example.com', 'Frontend developer proficient in React and Vue'),
            ('jessica_backend', 'jessica@example.com', 'Backend engineer specializing in Python and Node.js'),
        ]

        seekers = []
        for username, email, bio in seekers_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': username.split('_')[0].capitalize(),
                    'last_name': 'Job Seeker',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                profile = user.profile
                profile.is_employer = False
                profile.bio = bio
                profile.save()
                self.stdout.write(f"✓ Created job seeker: {username}")
            seekers.append(user)

        # Create Jobs
        jobs_data = [
            (employers[0], 'Senior Full Stack Developer', 'We are looking for experienced full stack developers to join our growing team...', 120000, 'New York, NY'),
            (employers[0], 'Python Backend Engineer', 'Help us build scalable APIs and microservices...', 110000, 'Remote'),
            (employers[1], 'React Developer', 'Build amazing UIs for our SaaS platform...', 100000, 'San Francisco, CA'),
            (employers[1], 'DevOps Engineer', 'Infrastructure, CI/CD, and cloud architecture...', 115000, 'Remote'),
            (employers[2], 'Data Analyst', 'Analyze financial data and create insights...', 95000, 'Chicago, IL'),
            (employers[2], 'SQL Developer', 'Database design and optimization...', 90000, 'Remote'),
            (employers[3], 'UI/UX Designer', 'Design beautiful interfaces for web and mobile...', 85000, 'Los Angeles, CA'),
            (employers[3], 'Graphic Designer', 'Create stunning visual assets and branding...', 80000, 'Remote'),
            (employers[4], 'JavaScript Developer', 'Full-stack JS development with Node.js and React...', 105000, 'Remote'),
            (employers[4], 'QA Engineer', 'Test automation and quality assurance...', 75000, 'Remote'),
        ]

        jobs = []
        for employer, title, description, salary, location in jobs_data:
            job, created = Job.objects.get_or_create(
                title=title,
                posted_by=employer,
                defaults={
                    'description': description,
                    'company': employer.profile.company_name,
                    'location': location,
                    'salary': salary,
                }
            )
            if created:
                self.stdout.write(f"✓ Created job: {title}")
            jobs.append(job)

        # Create Applications
        for i, job in enumerate(jobs):
            num_applicants = (i % 3) + 1
            for j in range(num_applicants):
                seeker = seekers[j % len(seekers)]
                application, created = Application.objects.get_or_create(
                    job=job,
                    applicant=seeker,
                    defaults={
                        'cover_letter': f"I am very interested in this position at {job.company}. "
                                      f"My experience includes working with similar technologies and delivering quality work. "
                                      f"I would love to discuss how I can contribute to your team.",
                        'status': 'pending' if i % 3 != 0 else ('accepted' if i % 5 == 0 else 'rejected'),
                    }
                )
                if created:
                    self.stdout.write(f"  ✓ {seeker.username} applied for {job.title}")

        self.stdout.write(self.style.SUCCESS('\n✅ Database populated successfully!'))
        self.stdout.write('\nSample Login Credentials:')
        self.stdout.write('Employers: tech_recruiter, startup_hr, finance_jobs (password: password123)')
        self.stdout.write('Job Seekers: john_dev, sarah_designer, mike_analyst (password: password123)')
