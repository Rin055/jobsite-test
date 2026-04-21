from django.contrib import admin

from .models import Category, Job, Application


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "location", "job_type", "is_remote", "created_at"]
    list_filter = ["job_type", "is_remote", "experience_level", "category"]
    search_fields = ["title", "company", "location", "description"]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["job", "applicant", "status", "applied_at"]
    list_filter = ["status"]
    search_fields = ["job__title", "applicant__username"]
