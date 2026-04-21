from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Case, When, IntegerField

from .models import Job, Application, Category
from .forms import JobForm, ApplicationForm

def job_list(request):
    query = (request.GET.get("q") or "").strip()
    location = (request.GET.get("location") or "").strip()
    category = (request.GET.get("category") or "").strip()
    job_type = (request.GET.get("job_type") or "").strip()
    remote = (request.GET.get("remote") or "").strip()
    experience = (request.GET.get("experience") or "").strip()
    sort = (request.GET.get("sort") or "newest").strip()

    jobs_qs = (
        Job.objects.all()
        .select_related("category", "posted_by")
        .annotate(applications_count=Count("applications", distinct=True))
    )

    if query:
        jobs_qs = jobs_qs.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(company__icontains=query)
        )

    if location:
        jobs_qs = jobs_qs.filter(location__icontains=location)

    if category and category.isdigit():
        jobs_qs = jobs_qs.filter(category_id=int(category))

    valid_job_types = {choice[0] for choice in Job.JOB_TYPE_CHOICES}
    if job_type in valid_job_types:
        jobs_qs = jobs_qs.filter(job_type=job_type)

    valid_experience = {choice[0] for choice in Job.EXPERIENCE_LEVEL_CHOICES}
    if experience in valid_experience:
        jobs_qs = jobs_qs.filter(experience_level=experience)

    if remote == "remote":
        jobs_qs = jobs_qs.filter(is_remote=True)
    elif remote == "onsite":
        jobs_qs = jobs_qs.filter(is_remote=False)

    if sort == "salary":
        jobs_qs = jobs_qs.order_by("-salary_max", "-salary_min", "-created_at")
    elif sort == "relevance" and query:
        jobs_qs = jobs_qs.annotate(
            _relevance=Case(
                When(title__icontains=query, then=3),
                When(company__icontains=query, then=2),
                When(description__icontains=query, then=1),
                default=0,
                output_field=IntegerField(),
            )
        ).order_by("-_relevance", "-created_at")
    else:
        jobs_qs = jobs_qs.order_by("-created_at")

    paginator = Paginator(jobs_qs, 10)
    jobs = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.all().order_by("name")

    params_without_page = request.GET.copy()
    params_without_page.pop("page", None)
    base_querystring = params_without_page.urlencode()

    sort_urls = {}
    for sort_key in ["newest", "salary", "relevance"]:
        sort_params = params_without_page.copy()
        sort_params["sort"] = sort_key
        sort_urls[sort_key] = f"?{sort_params.urlencode()}"

    return render(
        request,
        "jobs/job_list.html",
        {
            "jobs": jobs,
            "query": query,
            "location": location,
            "category": category,
            "job_type": job_type,
            "remote": remote,
            "experience": experience,
            "sort": sort,
            "categories": categories,
            "total_jobs": Job.objects.count(),
            "base_querystring": base_querystring,
            "sort_urls": sort_urls,
        },
    )

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    has_applied = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    return render(
        request,
        "jobs/job_detail.html",
        {"job": job, "has_applied": has_applied, "already_applied": has_applied},
    )

@login_required
def job_create(request):
    if not hasattr(request.user, "profile") or not request.user.profile.is_employer:
        messages.error(request, "Only employers can post jobs.")
        return redirect('job_list')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobForm()
    return render(request, 'jobs/job_form.html', {'form': form})

@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.posted_by != request.user:
        messages.error(request, "You can only edit your own jobs.")
        return redirect('job_list')

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/job_form.html', {'form': form})

@login_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.posted_by != request.user:
        messages.error(request, "You can only delete your own jobs.")
        return redirect('job_list')

    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted successfully!")
        return redirect('job_list')
    return render(request, 'jobs/job_confirm_delete.html', {'job': job})

@login_required
def apply_for_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if hasattr(request.user, "profile") and request.user.profile.is_employer:
        messages.error(request, "Employers cannot apply for jobs.")
        return redirect('job_detail', pk=pk)

    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.error(request, "You have already applied for this job.")
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES, applicant=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('job_detail', pk=pk)
    else:
        form = ApplicationForm(applicant=request.user)
    return render(request, 'jobs/apply.html', {'form': form, 'job': job})

@login_required
def my_applications(request):
    if hasattr(request.user, "profile") and request.user.profile.is_employer:
        messages.error(request, "Employer accounts cannot apply for jobs.")
        return redirect("job_list")

    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    return render(request, 'jobs/my_applications.html', {'applications': applications})

@login_required
def job_applications(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if not hasattr(request.user, "profile") or not request.user.profile.is_employer:
        messages.error(request, "Only employers can manage applications.")
        return redirect("job_list")
    if job.posted_by != request.user:
        messages.error(request, "You can only view applications for your own jobs.")
        return redirect('job_list')

    applications = Application.objects.filter(job=job).order_by('-applied_at')
    return render(request, 'jobs/job_applications.html', {'job': job, 'applications': applications})

@login_required
@login_required
def update_application_status(request, pk):
    if request.method != "POST":
        messages.error(request, "Invalid request.")
        return redirect("job_list")

    application = get_object_or_404(Application, pk=pk)
    if not hasattr(request.user, "profile") or not request.user.profile.is_employer:
        messages.error(request, "Only employers can manage applications.")
        return redirect("job_list")
    if application.job.posted_by != request.user:
        messages.error(request, "You can only update applications for your own jobs.")
        return redirect('job_list')

    status = (request.POST.get("status") or "").strip()
    valid_statuses = {choice[0] for choice in Application.STATUS_CHOICES}

    if status in valid_statuses:
        application.status = status
        application.save(update_fields=["status"])
        messages.success(request, f"Application marked as {status}.")
    else:
        messages.error(request, "Invalid status.")
    return redirect('job_applications', pk=application.job.pk)
