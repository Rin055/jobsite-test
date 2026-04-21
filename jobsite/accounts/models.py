from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.apps import apps

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_employer = models.BooleanField(default=False)
    role_selected_at = models.DateTimeField(null=True, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    @property
    def can_change_role(self) -> bool:
        """
        Allow changing account type until the user takes role-specific actions.

        This supports legacy/admin-created users (or accounts affected by earlier
        role backfills) to correct their role before they post jobs or apply.
        """
        if not self.user_id:
            return True

        Job = apps.get_model("jobs", "Job")
        Application = apps.get_model("jobs", "Application")

        has_jobs = Job.objects.filter(posted_by_id=self.user_id).exists()
        has_applications = Application.objects.filter(applicant_id=self.user_id).exists()
        return not (has_jobs or has_applications)

    def clean(self):
        super().clean()
        if not self.pk:
            return

        previous = Profile.objects.filter(pk=self.pk).only("is_employer", "role_selected_at").first()
        if not previous:
            return

        if previous.is_employer != self.is_employer and not self.can_change_role:
            raise ValidationError({"is_employer": "Account type cannot be changed after you start using the platform."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {'Employer' if self.is_employer else 'Job Seeker'}"
