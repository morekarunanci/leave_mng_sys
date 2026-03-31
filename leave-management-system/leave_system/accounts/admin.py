from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Manager, Employee


# ✅ Custom User Admin with password hashing support
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    model = User

    list_display = ('username', 'email', 'role', 'department', 'manager', 'is_staff')
    list_filter = ('role', 'department', 'is_staff')

    # 🔥 Add your custom fields
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'department', 'manager', 'profile_picture')
        }),
    )

    # 🔥 Add fields when creating user
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'department', 'manager', 'profile_picture')
        }),
    )

    search_fields = ('username', 'email')
    ordering = ('username',)


# 🔥 Managers Section (Proxy Model)
@admin.register(Manager)
class ManagerAdmin(BaseUserAdmin):
    model = Manager
    list_display = ('username', 'department', 'is_active')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role='manager')


# 🔥 Employees Section (Proxy Model)
@admin.register(Employee)
class EmployeeAdmin(BaseUserAdmin):
    model = Employee
    list_display = ('username', 'manager', 'department', 'is_active')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role='employee')