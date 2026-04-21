from django import forms
from .models import Job, Application, Category

class JobForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), required=False, empty_label="Select a category"
    )

    class Meta:
        model = Job
        fields = [
            "title",
            "company",
            "location",
            "job_type",
            "category",
            "experience_level",
            "is_remote",
            "salary_min",
            "salary_max",
            "deadline",
            "description",
            "requirements",
            "benefits",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "requirements": forms.Textarea(attrs={"rows": 4}),
            "benefits": forms.Textarea(attrs={"rows": 4}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, applicant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.applicant = applicant

    def clean(self):
        cleaned_data = super().clean()
        if self.applicant is not None:
            try:
                is_employer = bool(self.applicant.profile.is_employer)
            except Exception:
                is_employer = False
            if is_employer:
                raise forms.ValidationError("Employer accounts cannot apply for jobs.")
        return cleaned_data
