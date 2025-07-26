from django.urls import path
from .views import routine_generator

urlpatterns = [
    path('generate', routine_generator, name='routine_generator'),
]
