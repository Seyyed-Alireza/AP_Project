from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows':3}),
        }
