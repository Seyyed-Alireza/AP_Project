from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='ایمیل')

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            'username': 'نام کاربری',
            'password1': 'رمز عبور',
            'password2': 'تکرار رمز عبور',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # تغییر متن پیام‌های خطا (errors)
        self.fields['username'].error_messages = {
            'required': 'وارد کردن نام کاربری الزامی است.',
            'unique': 'این نام کاربری قبلاً استفاده شده است.'
        }
        self.fields['email'].error_messages = {
            'required': 'ایمیل الزامی است.',
            'invalid': 'فرمت ایمیل معتبر نیست.'
        }
        self.fields['password1'].error_messages = {
            'required': 'رمز عبور را وارد کنید.',
            'password_too_short': 'رمز عبور باید حداقل ۸ کاراکتر باشد.',
        }
        self.fields['password2'].error_messages = {
            'required': 'تکرار رمز عبور الزامی است.',
            'password_mismatch': 'رمزهای عبور یکسان نیستند.',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='نام کاربری',
        widget=forms.TextInput(attrs={'autofocus': True}),
        error_messages={
            'required': 'وارد کردن نام کاربری الزامی است.',
        }
    )
    password = forms.CharField(
        label='رمز عبور',
        strip=False,
        widget=forms.PasswordInput,
        error_messages={
            'required': 'وارد کردن رمز عبور الزامی است.',
        }
    )
    
    error_messages = {
        'invalid_login': "نام کاربری یا رمز عبور اشتباه است.",
        'inactive': "حساب کاربری غیرفعال است.",
    }