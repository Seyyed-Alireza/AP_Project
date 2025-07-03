from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('', views.home, name='mainpage')
]
