from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Job


class JobListFilteringTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="employer", password="pass12345")
        self.cat_eng, _ = Category.objects.get_or_create(name="Engineering")
        self.cat_design, _ = Category.objects.get_or_create(name="Design")

        Job.objects.create(
            title="Backend Engineer",
            description="Python + Django",
            company="Acme",
            location="New York",
            job_type="full_time",
            category=self.cat_eng,
            experience_level="mid",
            is_remote=False,
            salary_min=90000,
            salary_max=130000,
            posted_by=self.user,
        )
        Job.objects.create(
            title="Product Designer",
            description="Figma",
            company="Globex",
            location="Remote",
            job_type="contract",
            category=self.cat_design,
            experience_level="entry",
            is_remote=True,
            salary_min=60000,
            salary_max=80000,
            posted_by=self.user,
        )

    def test_search_filters_by_query(self):
        response = self.client.get(reverse("job_list"), {"q": "Designer"})
        jobs = list(response.context["jobs"])
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].title, "Product Designer")

    def test_filters_by_location_text(self):
        response = self.client.get(reverse("job_list"), {"location": "New"})
        jobs = list(response.context["jobs"])
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].company, "Acme")

    def test_filters_by_category(self):
        response = self.client.get(reverse("job_list"), {"category": str(self.cat_eng.id)})
        jobs = list(response.context["jobs"])
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].title, "Backend Engineer")

    def test_filters_by_job_type(self):
        response = self.client.get(reverse("job_list"), {"job_type": "contract"})
        jobs = list(response.context["jobs"])
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].title, "Product Designer")

    def test_filters_by_remote(self):
        response = self.client.get(reverse("job_list"), {"remote": "remote"})
        jobs = list(response.context["jobs"])
        self.assertEqual(len(jobs), 1)
        self.assertTrue(jobs[0].is_remote)

    def test_filters_by_experience(self):
        response = self.client.get(reverse("job_list"), {"experience": "mid"})
        jobs = list(response.context["jobs"])
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].title, "Backend Engineer")

    def test_sort_by_salary(self):
        response = self.client.get(reverse("job_list"), {"sort": "salary"})
        jobs = list(response.context["jobs"])
        self.assertGreaterEqual(jobs[0].salary_max or 0, jobs[1].salary_max or 0)


class ApplicationWorkflowTests(TestCase):
    def setUp(self):
        self.employer = User.objects.create_user(username="mgr", password="pass12345")
        self.applicant = User.objects.create_user(username="app", password="pass12345")

        from accounts.models import Profile

        emp_profile, _ = Profile.objects.get_or_create(user=self.employer)
        emp_profile.is_employer = True
        emp_profile.save(update_fields=["is_employer"])

        seeker_profile, _ = Profile.objects.get_or_create(user=self.applicant)
        seeker_profile.is_employer = False
        seeker_profile.save(update_fields=["is_employer"])

        self.job = Job.objects.create(
            title="QA Engineer",
            description="Test things",
            company="Initech",
            location="Remote",
            job_type="full_time",
            is_remote=True,
            posted_by=self.employer,
        )

    def test_applicant_can_apply_and_employer_can_update_status(self):
        self.client.login(username="app", password="pass12345")
        response = self.client.post(
            reverse("apply_for_job", args=[self.job.pk]),
            {"cover_letter": "Hello", "resume": ""},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        application = self.job.applications.get(applicant=self.applicant)
        self.assertEqual(application.status, "pending")

        self.client.logout()
        self.client.login(username="mgr", password="pass12345")
        response = self.client.post(
            reverse("update_application_status", args=[application.pk]),
            {"status": "accepted"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.status, "accepted")

    def test_employer_cannot_apply(self):
        self.client.login(username="mgr", password="pass12345")
        response = self.client.post(
            reverse("apply_for_job", args=[self.job.pk]),
            {"cover_letter": "Hello"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.job.applications.count(), 0)

    def test_jobseeker_cannot_post_job(self):
        self.client.login(username="app", password="pass12345")
        response = self.client.get(reverse("job_create"))
        self.assertEqual(response.status_code, 302)
