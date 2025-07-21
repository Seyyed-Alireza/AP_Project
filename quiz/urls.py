from django.urls import path
from .views import skin_quiz_view, skip_quiz, from_prof

urlpatterns = [
    path('', skin_quiz_view, name='quiz'),
    path('q_f_prof', from_prof, name='quiz_from_prof'),
    path('skip', skip_quiz, name='skip_quiz')
]
