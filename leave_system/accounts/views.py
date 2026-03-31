from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from accounts.models import User, Notification, EmailMessage
from django.core.mail import send_mail
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import ProfilePicForm
from leaves.models import LeaveBalance, LeaveRequest

# 🔐 LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','').strip()

        if not username or not password:
            messages.error(request, "Username and password are required")
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)
        
        if user is None:
            messages.error(request, "Invalid username or password")
            return render(request, 'accounts/login.html')
            
         # 🔴 Inactive user
        if not user.is_active:
            messages.error(request, "Your account is inactive")
            return render(request, 'accounts/login.html')
            
        # ✅ Login
        login(request, user)
        print("User:", user.username)
        
         # 🔴 Superuser
        if user.is_superuser:
            return redirect('superuser_dashboard')
        
         # 🔴 Get profile safely
        profile = getattr(user, 'profile', None)

        if profile and profile.role:
            role = profile.role.name.lower()
            print("Role:", role)

            if role == 'manager':
                return redirect('manager_dashboard')

            elif role == 'employee':
                return redirect('employee_dashboard')

        # ✅ FALLBACK (IMPORTANT)
        return redirect('employee_dashboard')   # or dashboard

    return render(request, 'accounts/login.html')

# 🔓 LOGOUT
def user_logout(request):
    logout(request)
    return redirect("login")


# 👑 SUPERUSER DASHBOARD
@login_required
@role_required('superuser')
def superuser_dashboard(request):

    managers = User.objects.filter(role='manager').select_related('department')
    all_leaves = LeaveRequest.objects.exclude(status__iexact='pending').order_by('-id')

    manager_data = []

    for manager in managers:
        team = User.objects.filter(
            role='employee',
            manager=manager,
        )

        manager_data.append({
            'manager': manager,
            'employees': team
        })

    # 🔥 Manager leave requests
    pending_manager_leaves = LeaveRequest.objects.filter(
        employee__role='manager',
        status__iexact='pending'
    ).order_by('-id')

    return render(request, 'dashboard/superuser_dashboard.html', {
        'manager_data': manager_data,
        'pending_manager_leaves': pending_manager_leaves,
        'all_leaves': all_leaves
    })


# 🧑‍💼 MANAGER DASHBOARD
@login_required
@role_required('manager')
def manager_dashboard(request):

    # 👥 Employees under this manager
    employees = User.objects.filter(
    role='employee',
    manager=request.user,
    )

    # 🔥 Pending leaves (for approval)
    pending_leaves = LeaveRequest.objects.filter(
        employee__manager=request.user,
        status__iexact='pending'
    ).order_by('-id')

    # 📋 Leave history (optional - approved/rejected)
    leave_history = LeaveRequest.objects.filter(
        employee__manager=request.user
    ).exclude(status__iexact='pending').order_by('-id')

    # 📊 Manager's own leave balance
    balance, _ = LeaveBalance.objects.get_or_create(user=request.user)

    return render(request, 'dashboard/manager_dashboard.html', {
        'employees': employees,
        'pending_leaves': pending_leaves,   # ✅ IMPORTANT
        'leave_history': leave_history,     # ✅ OPTIONAL
        'leave_balance': balance
    })


# 👨‍💻 EMPLOYEE DASHBOARD
@login_required
@role_required('employee')
def employee_dashboard(request):

    balance, created = LeaveBalance.objects.get_or_create(user=request.user)

    total = (
        balance.casual_total +
        balance.medical_total +
        balance.other_total
    )

    used = (
        balance.casual_used +
        balance.medical_used +
        balance.other_used
    )

    remaining = total - used

    return render(request, 'dashboard/employee_dashboard.html', {
        'total': total,
        'used': used,
        'remaining': remaining,
        'leave_balance': balance
    })


# 🔔 NOTIFICATIONS
@login_required
def notifications(request):
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')

    # ✅ MARK AS READ
    notes.update(is_read=True)

    # ✅ COUNT AFTER READ (WILL BE ZERO)
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return render(request, 'accounts/notifications.html', {
        'notifications': notes,
        'unread_count': unread_count
    })


# 📧 SEND EMAIL (ROLE-BASED)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from accounts.models import User
from .models import EmailMessage


@login_required
def send_email(request):

    current_user = request.user

    # 🔹 ROLE-BASED USER FILTER
    if current_user.role == 'superuser':
        users = User.objects.filter(role__in=['manager', 'employee'])

    elif current_user.role == 'manager':
        users = User.objects.filter(role__in=['superuser', 'employee'])

    elif current_user.role == 'employee':
        users = User.objects.filter(role__in=['superuser', 'manager'])

    else:
        users = User.objects.none()

    # 🔹 GET receiver (for auto-select)
    receiver_id = request.GET.get('receiver')
    selected_receiver = None

    if receiver_id:
        selected_receiver = get_object_or_404(User, id=receiver_id)

        # 🔐 SECURITY CHECK
        if selected_receiver not in users:
            messages.error(request, "Unauthorized access")
            return redirect('dashboard_redirect')

    # 🔹 POST REQUEST
    if request.method == "POST":
        receiver_id = request.POST.get('receiver')
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        # ❌ VALIDATION
        if not receiver_id or not subject or not body:
            messages.error(request, "All fields are required!")
            return redirect(request.path)

        receiver = get_object_or_404(User, id=receiver_id)

        # 🔐 SECURITY CHECK
        if receiver not in users:
            messages.error(request, "Unauthorized action")
            return redirect('dashboard_redirect')

        # 💾 SAVE MESSAGE (THIS POWERS INBOX ✅)
        EmailMessage.objects.create(
            sender=current_user,
            receiver=receiver,
            subject=subject,
            body=body
        )

        # 📧 SEND EMAIL (OPTIONAL BUT GOOD)
        try:
            send_mail(
                subject,
                body,
                current_user.email,
                [receiver.email],
                fail_silently=True,
            )
        except:
            pass  # prevent crash if email fails

        # ✅ SUCCESS MESSAGE
        messages.success(request, "Email sent successfully!")

        # 🔁 ROLE-BASED REDIRECT
        return redirect('dashboard_redirect')

    # 🔹 RENDER PAGE
    return render(request, 'dashboard/send_email.html', {
        'users': users,
        'selected_receiver': selected_receiver
    })

# 📥 INBOX
@login_required
def inbox(request):
    emails = EmailMessage.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'accounts/inbox.html', {'emails': emails})


@login_required
def mark_as_read(request, email_id):
    email = get_object_or_404(EmailMessage, id=email_id, receiver=request.user)
    email.is_read = True
    email.save()
    return redirect('inbox')


@login_required
def delete_email(request, email_id):
    email = get_object_or_404(EmailMessage, id=email_id, receiver=request.user)
    email.delete()
    return redirect('inbox')


# 👤 PROFILE
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


# 🔐 CHANGE PASSWORD
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            # 🔁 ROLE-BASED REDIRECT
            if request.user.role == 'superuser':
                return redirect('superuser_dashboard')
            elif request.user.role == 'manager':
                return redirect('manager_dashboard')
            else:
                return redirect('employee_dashboard')

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})

def dashboard_redirect(request):
    if request.user.role == 'superuser':
        return redirect('superuser_dashboard')
    elif request.user.role == 'manager':
        return redirect('manager_dashboard')
    else:
        return redirect('employee_dashboard')
    
@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = ProfilePicForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # refresh page
    else:
        form = ProfilePicForm(instance=user)

    return render(request, 'accounts/profile.html', {'form': form})


