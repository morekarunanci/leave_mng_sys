from django.contrib import admin
from .models import LeaveType, LeaveRequest


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color_code")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "applied_at",
        "reviewed_by",
        "reviewed_on",
    )

    list_filter = ("status", "leave_type")
    search_fields = ("employee__username",)
