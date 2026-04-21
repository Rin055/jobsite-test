from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from jobs.models import Job

from .models import Profile


class RegistrationTests(TestCase):
    def test_duplicate_username_shows_error_instead_of_500(self):
        User.objects.create_user(username="dupe", password="pass12345")

        response = self.client.post(
            reverse("register"),
            {
                "first_name": "A",
                "last_name": "B",
                "username": "dupe",
                "email": "dupe@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "role": "jobseeker",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="dupe").count(), 1)
        self.assertIn("form", response.context)
        self.assertIn("username", response.context["form"].errors)

    def test_role_is_saved_at_signup(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Emp",
                "last_name": "Loyer",
                "username": "employer1",
                "email": "employer1@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "role": "employer",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="employer1")
        profile = Profile.objects.get(user=user)
        self.assertTrue(profile.is_employer)
        self.assertIsNotNone(profile.role_selected_at)


class ProfileRoleSelectionTests(TestCase):
    def test_legacy_user_can_select_employer_role_from_profile(self):
        user = User.objects.create_user(username="legacy", password="pass12345")
        profile = Profile.objects.get(user=user)
        self.assertIsNone(profile.role_selected_at)
        self.assertFalse(profile.is_employer)

        self.assertTrue(self.client.login(username="legacy", password="pass12345"))
        response = self.client.post(
            reverse("profile"),
            {
                "first_name": "Legacy",
                "last_name": "Employer",
                "role": "employer",
                "company_name": "Legacy Co",
                "bio": "",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertTrue(profile.is_employer)
        self.assertIsNotNone(profile.role_selected_at)

    def test_role_cannot_be_changed_after_selection(self):
        user = User.objects.create_user(username="locked", password="pass12345")
        profile = Profile.objects.get(user=user)
        profile.is_employer = True
        profile.role_selected_at = profile.role_selected_at or profile.user.date_joined
        profile.save()

        Job.objects.create(
            title="Test Job",
            description="Test description",
            company="Test Co",
            location="Remote",
            posted_by=user,
        )

        self.assertTrue(self.client.login(username="locked", password="pass12345"))
        response = self.client.post(
            reverse("profile"),
            {
                "first_name": "Locked",
                "last_name": "User",
                "role": "jobseeker",  # attempt to change
                "company_name": "Should Stay Employer",
                "bio": "",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertTrue(profile.is_employer)
