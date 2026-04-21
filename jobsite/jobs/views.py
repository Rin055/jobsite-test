from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Job, Application
from .forms import JobForm, ApplicationForm

def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    has_applied = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    return render(request, 'jobs/job_detail.html', {'job': job, 'has_applied': has_applied})

@login_required
def job_create(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_employer:
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
    if hasattr(request.user, 'profile') and request.user.profile.is_employer:
        messages.error(request, "Employers cannot apply for jobs.")
        return redirect('job_detail', pk=pk)

    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.error(request, "You have already applied for this job.")
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('job_detail', pk=pk)
    else:
        form = ApplicationForm()
    return render(request, 'jobs/apply.html', {'form': form, 'job': job})

@login_required
def my_applications(request):
    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    return render(request, 'jobs/my_applications.html', {'applications': applications})

@login_required
def job_applications(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.posted_by != request.user:
        messages.error(request, "You can only view applications for your own jobs.")
        return redirect('job_list')

    applications = Application.objects.filter(job=job).order_by('-applied_at')
    return render(request, 'jobs/job_applications.html', {'job': job, 'applications': applications})

@login_required
def update_application_status(request, pk, status):
    application = get_object_or_404(Application, pk=pk)
    if application.job.posted_by != request.user:
        messages.error(request, "You can only update applications for your own jobs.")
        return redirect('job_list')

    if status in ['accepted', 'rejected']:
        application.status = status
        application.save()
        messages.success(request, f"Application {status}!")
    return redirect('job_applications', pk=application.job.pk)
