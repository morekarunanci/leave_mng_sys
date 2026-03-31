from django.urls import path
from . import views

urlpatterns = [
    # 🔐 AUTH
    path('', views.login_view, name="login"),  # default route → login
    path('login/', views.login_view, name="login"),
    path('logout/', views.user_logout, name='logout'),
    path('notifications/', views.notifications, name='notifications'),
    path('send-email/', views.send_email, name='send_email'),

    # 📊 DASHBOARDS
    path('superuser-dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('manager-dashboard/', views.manager_dashboard, name="manager_dashboard"),
    path('employee-dashboard/', views.employee_dashboard, name="employee_dashboard"),
    
    path('inbox/', views.inbox, name='inbox'),
    path('email/read/<int:email_id>/', views.mark_as_read, name='mark_as_read'),
    path('email/delete/<int:email_id>/', views.delete_email, name='delete_email'),
    
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    
]