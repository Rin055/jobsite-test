from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['is_employer', 'company_name', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }