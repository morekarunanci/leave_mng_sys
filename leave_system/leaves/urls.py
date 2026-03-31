from django.urls import path
from . import views

app_name = 'leaves'

urlpatterns = [
    # 🔹 Leave Actions
    path('apply-leave/', views.apply_leave, name="apply_leave"),
    path('history/', views.leave_history, name="leave_history"),
    path('pending/', views.pending_leaves, name='pending_leaves'),

    # 🔹 Approval Actions
    path('approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),

    # 🔹 Summary
    path('leave-summary/<int:user_id>/', views.leave_summary, name='leave_summary'),

    # 🔥🔥 IMPORTANT (THIS FIXES YOUR ERROR)
    path('leave-events/', views.leave_events, name='leave_events'),
    
]