from django.contrib.auth.models import AbstractUser
from django.db import models


# 🔹 Custom User Model
class User(AbstractUser):

    ROLE_CHOICES = (
        ("superuser", "Superuser"),
        ("manager", "Manager"),
        ("employee", "Employee"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    profile_pic = models.ImageField(upload_to="profile_pics/", null=True, blank=True)

    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members",
    )

    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)

    def get_full_name(self):  # ✅ ADD THIS
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def __str__(self):
        return self.username


# 🔥 Proxy Model → Managers
class Manager(User):
    class Meta:
        proxy = True
        verbose_name = "Manager"
        verbose_name_plural = "Managers"


# 🔥 Proxy Model → Employees
class Employee(User):
    class Meta:
        proxy = True
        verbose_name = "Employee"
        verbose_name_plural = "Employees"


class Notification(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}"


class EmailMessage(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_emails"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_emails"
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.receiver}"
