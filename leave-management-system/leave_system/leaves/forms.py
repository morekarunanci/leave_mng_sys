from django import forms
from .models import LeaveRequest


class LeaveForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]

        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "leave_type": forms.Select(attrs={"class": "form-select"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    # 🔥 Clean validation (updated)
    def clean(self):
        cleaned_data = super().clean()
        leave_type = cleaned_data.get("leave_type")
        reason = cleaned_data.get("reason")

        # 👉 If "Other" selected → reason is mandatory
        if leave_type and leave_type.name.lower() == "other":
            if not reason:
                raise forms.ValidationError(
                    "Please provide a reason for 'Other' leave type."
                )

        return cleaned_data
