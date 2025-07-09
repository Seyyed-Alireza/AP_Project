from django import forms
from .models import UserProfile

class PersianFileInput(forms.ClearableFileInput):
    initial_text = 'هیچ فایلی انتخاب نشده'
    input_text = 'انتخاب فایل'
    clear_checkbox_label = 'پاک کردن'
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
            'address': forms.Textarea(attrs={'rows':5}),
            'profile_picture': PersianFileInput(),
        }

    # def save(self, commit=True):
    #     instance = super().save(commit=False)

    #     if not instance.profile_picture ##and not instance.pk (added after)##:
    #         instance.profile_picture = 'profile_pictures/default/default.svg'

    #     if commit:
    #         instance.save()
    #     return instance
