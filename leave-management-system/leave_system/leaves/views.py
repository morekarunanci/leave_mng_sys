from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from accounts.decorators import role_required
from accounts.models import Notification, User
from .forms import LeaveForm
from .models import LeaveRequest, LeaveBalance


# 📌 APPLY LEAVE (Employee / Manager)
@login_required
@role_required(["employee", "manager"])
def apply_leave(request):
    if request.method == "POST":
        form = LeaveForm(request.POST)

        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.manager = request.user.manager
            leave.status = "pending"
            leave.save()

            # 🔥 EMPLOYEE APPLY
            if request.user.role == "employee":

                if request.user.manager:
                    Notification.objects.create(
                        user=request.user.manager,
                        message=f"{request.user.username} applied for leave from"
                        f"{leave.start_date} to {leave.end_date}.",
                    )

                messages.success(request, "Leave applied successfully!")
                return redirect("employee_dashboard")

            # 🔥 MANAGER APPLY
            elif request.user.role == "manager":

                leave.manager = None
                leave.employee = request.user
                leave.status = "pending"
                leave.save()

                superusers = User.objects.filter(role="superuser")
                for su in superusers:
                    Notification.objects.create(
                        user=su,
                        message=f"Manager {request.user.username} applied for leave from"
                        f"{leave.start_date} to {leave.end_date}.",
                    )

                messages.success(request, "Leave applied successfully!")
                return redirect("manager_dashboard")

    else:
        form = LeaveForm()

    return render(request, "leaves/apply_leave.html", {"form": form})


# 📌 LEAVE HISTORY
@login_required
@role_required(["employee", "manager"])
def leave_history(request):

    if request.user.role == "manager":
        leaves = (
            LeaveRequest.objects.filter(employee__manager=request.user)
            .exclude(status__iexact="pending")
            .order_by("-id")
        )
    else:
        leaves = LeaveRequest.objects.filter(employee=request.user).order_by("-id")

    return render(request, "leaves/leave_history.html", {"leaves": leaves})


# 📌 PENDING LEAVES
@login_required
@role_required(["employee", "manager"])
def pending_leaves(request):

    if request.user.role == "manager":
        leaves = LeaveRequest.objects.filter(
            employee__manager=request.user, status__iexact="pending"
        ).order_by("-id")
    else:
        leaves = LeaveRequest.objects.filter(
            employee=request.user, status__iexact="pending"
        ).order_by("-id")

    return render(request, "leaves/pending_leaves.html", {"leaves": leaves})


# 📌 APPROVE LEAVE
@login_required
def approve_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id)

    if request.user.role == "manager":
        if leave.employee.manager != request.user:
            messages.error(request, "Not authorized!")
            return redirect("manager_dashboard")

    elif request.user.role == "superuser":
        if leave.employee.role != "manager":
            messages.error(request, "Invalid request!")
            return redirect("superuser_dashboard")

    leave.status = "Approved"
    leave.reviewed_by = request.user
    leave.save()
    print("APPROVED BY:", request.user.username, request.user.role)

    Notification.objects.create(
        user=leave.employee,
        message=f"Your leave has been approved by {request.user.username}",
    )

    superusers = User.objects.filter(role="superuser").exclude(id=request.user.id)
    for su in superusers:
        Notification.objects.create(
            user=su,
            message=f"{leave.employee.username}'s leave approved by {request.user.username}",
        )

    messages.success(request, "Leave approved successfully!")

    return redirect(
        "manager_dashboard" if request.user.role == "manager" else "superuser_dashboard"
    )


# 📌 REJECT LEAVE
@login_required
def reject_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = "Rejected"
    leave.reviewed_by = request.user
    leave.save()
    print("REJECTED BY:", request.user.username, request.user.role)

    Notification.objects.create(
        user=leave.employee,
        message=f"Your leave has been rejected by {request.user.username}",
    )

    superusers = User.objects.filter(role="superuser").exclude(id=request.user.id)
    for su in superusers:
        Notification.objects.create(
            user=su,
            message=f"{leave.employee.username}'s leave rejected by {request.user.username}",
        )

    messages.error(request, "Leave rejected.")

    return redirect(
        "manager_dashboard" if request.user.role == "manager" else "superuser_dashboard"
    )


# 📌 LEAVE SUMMARY
@login_required
def leave_summary(request, user_id):
    user = get_object_or_404(User, id=user_id)
    leaves = LeaveRequest.objects.filter(employee=user)
    total_leaves = leaves.count()
    approved = leaves.filter(status="Approved").count()
    rejected = leaves.filter(status="Rejected").count()
    pending = leaves.filter(status__iexact="pending").count()
    balance, _ = LeaveBalance.objects.get_or_create(user=user)

    total_allowed = balance.casual_total + balance.medical_total + balance.other_total
    used = balance.casual_used + balance.medical_used + balance.other_used
    remaining = total_allowed - used

    return render(
        request,
        "leaves/leave_summary.html",
        {
            "user": user,
            "total_leaves": total_leaves,
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
            "total_allowed": total_allowed,
            "used": used,
            "remaining": remaining,
            "leaves": leaves,
        },
    )


# =========================================================
# 🔥 CALENDAR EVENTS API
# =========================================================
@login_required
def leave_events(request):

    if request.user.role != "manager":
        return JsonResponse([], safe=False)

    leaves = LeaveRequest.objects.filter(employee__manager=request.user)

    events = []

    for leave in leaves:
        events.append(
            {
                "title": leave.employee.get_full_name(),
                "start": leave.start_date.strftime("%Y-%m-%d"),
                "end": leave.end_date.strftime("%Y-%m-%d"),
                "color": (
                    "green"
                    if leave.status == "Approved"
                    else "red" if leave.status == "Rejected" else "orange"
                ),
                "status": leave.status,
            }
        )

    return JsonResponse(events, safe=False)
