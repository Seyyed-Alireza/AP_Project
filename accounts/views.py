from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from quiz.models import SkinProfile

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            activation_link = request.build_absolute_uri(
                f'/accounts/activate/{uid}/{token}/'
            )

            send_mail(
                'فعالسازی حساب کاربری',
                f'برای فعالسازی حساب خود روی لینک زیر کلیک کنید:\n{activation_link}',
                'sahseyyedalirezahosseini1384@gmail.com',
                [user.email],
                fail_silently=False,
            )

            return render(request, 'accounts/activation_sent.html')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            product_url = request.POST.get('next') or request.GET.get('next')
            if product_url:
                return redirect(product_url)
            skin_profile, created = SkinProfile.objects.get_or_create(user=request.user)
            if not skin_profile.quiz_skipped and not skin_profile.quiz_completed:
                return redirect('quiz:quiz')
            return redirect('mainpage:mainpage') 
        else:
            return render(request, 'accounts/login.html', {'form': form})
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form, 'next': request.POST.get('next', '')})


from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'accounts/activation_success.html')
    else:
        return render(request, 'accounts/activation_failed.html')
    
from django.shortcuts import render

def home(request):
    return render(request, 'mainpage/mainpage.html')



from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import CurrentUserSerializer

@api_view(['GET'])
def current_user(request):
    user = request.user
    if user.is_authenticated:
        serializer = CurrentUserSerializer(user)
        return Response(serializer.data)
    else:
        return Response(None)
