from django import forms
from .models import EmailMessage, User

class EmailForm(forms.ModelForm):
    class Meta:
        model = EmailMessage
        fields = ['receiver', 'subject', 'body']
        
class ProfilePicForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_pic']