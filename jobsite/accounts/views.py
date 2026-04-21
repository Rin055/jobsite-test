from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import IntegrityError, transaction
from .models import Profile
from .forms import ProfileForm, RegistrationForm
from jobs.models import Application, Job
from django.db.models import Count

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    role = (request.POST.get("role") or "jobseeker").strip().lower()
                    profile, _ = Profile.objects.get_or_create(user=user)
                    profile.is_employer = role == "employer"
                    if profile.role_selected_at is None:
                        profile.role_selected_at = timezone.now()
                    profile.save(update_fields=["is_employer", "role_selected_at"])
            except IntegrityError:
                attempted_username = (
                    getattr(form, "cleaned_data", {}).get("username")
                    or request.POST.get("username")
                    or ""
                )
                if attempted_username:
                    form.add_error("username", "This username is already taken.")
                else:
                    form.add_error(None, "Could not create account. Please try again.")
            else:
                login(request, user)
                return redirect('job_list')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)

    seeker_applications = Application.objects.none()
    employer_jobs = Job.objects.none()

    if hasattr(request.user, "profile") and request.user.profile.is_employer:
        employer_jobs = (
            Job.objects.filter(posted_by=request.user)
            .annotate(applications_count=Count("applications", distinct=True))
            .order_by("-created_at")
        )
    else:
        seeker_applications = (
            Application.objects.filter(applicant=request.user)
            .select_related("job")
            .order_by("-applied_at")
        )

    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "seeker_applications": seeker_applications,
            "employer_jobs": employer_jobs,
        },
    )
