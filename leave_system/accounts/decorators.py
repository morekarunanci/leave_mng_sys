from django.shortcuts import redirect
from functools import wraps


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # ✅ Check login
            if not request.user.is_authenticated:
                return redirect("login")

            # ✅ Get role safely
            user_role = getattr(request.user, "role", None)

            # 🔥 DEBUG (optional)
            print("USER:", request.user)
            print("USER ROLE:", user_role)
            print("REQUIRED ROLE:", allowed_roles)

            # ✅ FIX: support both list and single role
            if isinstance(allowed_roles, list):
                if user_role not in allowed_roles:
                    return redirect_based_on_role(user_role)
            else:
                if user_role != allowed_roles:
                    return redirect_based_on_role(user_role)

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


# 🔥 HELPER FUNCTION (clean redirect logic)
def redirect_based_on_role(user_role):
    if user_role == "manager":
        return redirect("manager_dashboard")
    elif user_role == "employee":
        return redirect("employee_dashboard")
    elif user_role == "superuser":
        return redirect("superuser_dashboard")
    else:
        return redirect("login")
