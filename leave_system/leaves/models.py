from django.db import models
from django.conf import settings


# 📌 Leave Types (Medical, Casual, Other)
class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    color_code = models.CharField(max_length=20)

    def __str__(self):
        return self.name


# 📌 Main Leave Request Model (USE THIS ONLY)
class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leaves",
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_leaves",
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    other_description = models.TextField(blank=True, null=True)

    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    applied_at = models.DateTimeField(auto_now_add=True)

    # 🔥 Approval Tracking
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leaves",
    )

    reviewed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.status})"


class LeaveBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    casual_total = models.IntegerField(default=15)
    medical_total = models.IntegerField(default=20)
    other_total = models.IntegerField(default=5)

    casual_used = models.IntegerField(default=0)
    medical_used = models.IntegerField(default=0)
    other_used = models.IntegerField(default=0)

    def casual_remaining(self):
        return self.casual_total - self.casual_used

    def medical_remaining(self):
        return self.medical_total - self.medical_used

    def other_remaining(self):
        return self.other_total - self.other_used
