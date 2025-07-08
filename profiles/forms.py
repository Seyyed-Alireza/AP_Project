from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'profile_picture']
        labels = {
            'phone_number': 'شماره موبایل',
            'address': 'آدرس',
            'profile_picture': 'تصویر پروفایل'
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows':3}),
        }

    # def save(self, commit=True):
    #     instance = super().save(commit=False)

    #     if not instance.profile_picture:
    #         instance.profile_picture = 'profile_pictures/default/default.svg'

    #     if commit:
    #         instance.save()
    #     return instance
