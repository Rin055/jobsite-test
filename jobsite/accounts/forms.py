from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Profile


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=False, max_length=150)
    last_name = forms.CharField(required=False, max_length=150)
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="First name", required=False, max_length=150)
    last_name = forms.CharField(label="Last name", required=False, max_length=150)
    role = forms.ChoiceField(
        label="Account type",
        required=False,
        choices=(("", "Select account type…"), ("jobseeker", "Job Seeker"), ("employer", "Employer")),
    )

    class Meta:
        model = Profile
        fields = ["company_name", "bio"]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        initial_role = "employer" if getattr(self.instance, "is_employer", False) else "jobseeker"
        if not getattr(self.instance, "can_change_role", True):
            self.fields["role"].disabled = True
            self.fields["role"].required = False
            self.fields["role"].initial = initial_role
        elif getattr(self.instance, "role_selected_at", None):
            self.fields["role"].required = False
            self.fields["role"].initial = initial_role
        else:
            self.fields["role"].required = True
            self.fields["role"].initial = ""

        if self.user is None:
            return

        if not self.is_bound:
            self.fields["first_name"].initial = self.user.first_name
            self.fields["last_name"].initial = self.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)

        selected_role = (self.cleaned_data.get("role") or "").strip().lower()
        if selected_role in {"jobseeker", "employer"}:
            profile.is_employer = selected_role == "employer"
            if not getattr(profile, "role_selected_at", None):
                profile.role_selected_at = timezone.now()

        if self.user is not None:
            self.user.first_name = (self.cleaned_data.get("first_name") or "").strip()
            self.user.last_name = (self.cleaned_data.get("last_name") or "").strip()
            if commit:
                self.user.save()

        if commit:
            profile.save()

        return profile
