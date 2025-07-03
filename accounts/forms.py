from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

import re

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='ایمیل')
    error_messages = {
        'password_mismatch': 'رمزهای عبور با هم مطابقت ندارند.',
    }
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

        self.fields['username'].widget.attrs.update({
            'placeholder': 'نام کاربری را وارد کنید (انگلیسی)',
            'pattern': '[A-Za-z0-9_]{1,150}',
            'title': 'فقط حروف و اعداد انگلیسی و زیرخط (_) مجاز است.'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'ایمیل را وارد کنید',
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'رمز عبور را وارد کنید',
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'رمز عبور را تکرار کنید',
        })

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
            'password_mismatch': 'رمزهای عبور با هم مطابقت ندارند.',
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            raise forms.ValidationError("نام کاربری فقط می‌تواند شامل حروف، اعداد انگلیسی و زیرخط (_) باشد.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if self.errors.get('password2'):
            errors = self.errors['password2'].as_data()
            for error in errors:
                if error.message == "The two password fields didn't match.":
                    self.errors['password2'] = self.error_class(["رمزهای عبور با هم مطابقت ندارند."])

        if password1 and password2:
            if password1 != password2:
                self.add_error("password2", "رمزهای عبور با هم مطابقت ندارند.")
            else:
                try:
                    validate_password(password1)
                except ValidationError as e:
                    translated_errors = []
                    for err in e.messages:
                        if "too short" in err:
                            translated_errors.append("رمز عبور باید حداقل ۸ کاراکتر باشد.")
                        elif "too common" in err:
                            translated_errors.append("رمز عبور خیلی ساده است.")
                        elif "entirely numeric" in err:
                            translated_errors.append("رمز عبور نباید فقط شامل اعداد باشد.")
                        else:
                            translated_errors.append("رمز عبور معتبر نیست.")

                    self.add_error("password1", translated_errors)
                    self.add_error("password2", translated_errors)  # اضافه کردن خطا به هر دو فیلد

    

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            'placeholder': 'نام کاربری را وارد کنید (انگلیسی)',
            'pattern': '[A-Za-z0-9_]{1,150}',
            'title': 'فقط حروف و اعداد انگلیسی و زیرخط (_) مجاز است.'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'رمز عبور را وارد کنید',
        })

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

