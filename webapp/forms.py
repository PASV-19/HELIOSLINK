from django import forms
from django.contrib.auth.models import User

class UserUpdateForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password or confirm:
            if password != confirm:
                raise forms.ValidationError("Passwords do not match")

            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters")

        return cleaned_data
