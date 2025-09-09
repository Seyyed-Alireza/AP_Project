from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('', RedirectView.as_view(url='/', permanent=False)),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('', views.home, name='return_home')
]
